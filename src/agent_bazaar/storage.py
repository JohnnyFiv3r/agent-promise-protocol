"""Small durable authority ledger with serialized, nestable write boundaries.

No cache or expiry is involved: replay and formation tombstones written by the
harness survive until the owning authority explicitly removes its state.
"""

from __future__ import annotations

from contextlib import contextmanager
import json
import math
from pathlib import Path
import sqlite3
import threading

from .errors import ProtocolError


MAX_INTEGER = 9_007_199_254_740_991


def _json(value):
    def check(item):
        if item is None or type(item) in (str, bool, int):
            return
        if type(item) is float and math.isfinite(item):
            return
        if type(item) is list:
            for entry in item:
                check(entry)
            return
        if type(item) is dict and all(type(key) is str for key in item):
            for entry in item.values():
                check(entry)
            return
        raise ProtocolError("invalid_record", "ledger values must be finite JSON")

    check(value)
    return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"))


class Ledger:
    """A local SQLite writer, fenced by SQLite's transactional file locking.

    Each outer boundary starts with BEGIN IMMEDIATE, so check-and-update code
    cannot race another connection's writer. Nested boundaries are savepoints.
    The revision advances exactly once when an outer transaction commits writes.
    This does not provide fencing against a separate copy of the database.
    """

    def __init__(self, path: str | Path):
        self.path = str(path)
        self._lock = threading.RLock()
        self._dirty: list[bool] = []
        self._savepoint = 0
        self._closed = False
        self._connection = sqlite3.connect(
            self.path, timeout=30.0, isolation_level=None, check_same_thread=False
        )
        self._connection.execute("PRAGMA busy_timeout = 30000")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA synchronous = FULL")
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.executescript(
            "CREATE TABLE IF NOT EXISTS ledger_values ("
            "namespace TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL,"
            "PRIMARY KEY(namespace, key));"
            "CREATE TABLE IF NOT EXISTS ledger_metadata ("
            "id INTEGER PRIMARY KEY CHECK(id = 1), revision INTEGER NOT NULL);"
            "INSERT OR IGNORE INTO ledger_metadata(id, revision) VALUES(1, 0);"
        )

    def _ensure_open(self):
        if self._closed:
            raise ProtocolError("internal_unresolved", "ledger is closed")

    @staticmethod
    def _key(namespace, key=None):
        if type(namespace) is not str or (key is not None and type(key) is not str):
            raise ProtocolError(
                "invalid_record", "ledger namespace and key must be strings"
            )

    @contextmanager
    def transaction(self):
        with self._lock:
            self._ensure_open()
            outer = not self._dirty
            name = None
            if outer:
                self._connection.execute("BEGIN IMMEDIATE")
            else:
                self._savepoint += 1
                name = f"ledger_sp_{self._savepoint}"
                self._connection.execute(f"SAVEPOINT {name}")
            self._dirty.append(False)
            try:
                yield self
                dirty = self._dirty[-1]
                if outer:
                    if dirty:
                        revision = self.revision
                        if revision >= MAX_INTEGER:
                            raise ProtocolError(
                                "internal_unresolved", "ledger revision exhausted"
                            )
                        self._connection.execute(
                            "UPDATE ledger_metadata SET revision = revision + 1 WHERE id = 1"
                        )
                    self._connection.execute("COMMIT")
                else:
                    self._connection.execute(f"RELEASE SAVEPOINT {name}")
                self._dirty.pop()
                if dirty and self._dirty:
                    self._dirty[-1] = True
            except BaseException:
                if outer:
                    if self._connection.in_transaction:
                        self._connection.execute("ROLLBACK")
                else:
                    self._connection.execute(f"ROLLBACK TO SAVEPOINT {name}")
                    self._connection.execute(f"RELEASE SAVEPOINT {name}")
                self._dirty.pop()
                raise

    @property
    def in_transaction(self) -> bool:
        with self._lock:
            self._ensure_open()
            return bool(self._dirty)

    @property
    def revision(self) -> int:
        with self._lock:
            self._ensure_open()
            return self._connection.execute(
                "SELECT revision FROM ledger_metadata WHERE id = 1"
            ).fetchone()[0]

    def get(self, namespace: str, key: str, default=None):
        self._key(namespace, key)
        if type(key) is not str:
            raise ProtocolError("invalid_record", "ledger key must be a string")
        with self._lock:
            self._ensure_open()
            row = self._connection.execute(
                "SELECT value FROM ledger_values WHERE namespace = ? AND key = ?",
                (namespace, key),
            ).fetchone()
            return json.loads(row[0]) if row else json.loads(_json(default))

    def put(self, namespace: str, key: str, value):
        self._key(namespace, key)
        if type(key) is not str:
            raise ProtocolError("invalid_record", "ledger key must be a string")
        encoded = _json(value)
        with self.transaction():
            self._connection.execute(
                "INSERT INTO ledger_values(namespace, key, value) VALUES(?, ?, ?) "
                "ON CONFLICT(namespace, key) DO UPDATE SET value = excluded.value",
                (namespace, key, encoded),
            )
            self._dirty[-1] = True

    def delete(self, namespace: str, key: str):
        self._key(namespace, key)
        if type(key) is not str:
            raise ProtocolError("invalid_record", "ledger key must be a string")
        with self.transaction():
            result = self._connection.execute(
                "DELETE FROM ledger_values WHERE namespace = ? AND key = ?",
                (namespace, key),
            )
            if result.rowcount:
                self._dirty[-1] = True

    def items(self, namespace: str) -> list[tuple[str, object]]:
        self._key(namespace)
        with self._lock:
            self._ensure_open()
            return [
                (key, json.loads(value))
                for key, value in self._connection.execute(
                    "SELECT key, value FROM ledger_values WHERE namespace = ? ORDER BY key",
                    (namespace,),
                ).fetchall()
            ]

    def snapshot(self):
        """Copy the committed/current transaction state for policy binding."""
        with self._lock:
            self._ensure_open()
            return [
                [namespace, key, json.loads(value)]
                for namespace, key, value in self._connection.execute(
                    "SELECT namespace,key,value FROM ledger_values ORDER BY namespace,key"
                )
                if namespace not in ("objects", "handoff_objects")
            ]

    def close(self):
        with self._lock:
            if self._dirty:
                raise ProtocolError(
                    "internal_unresolved", "cannot close an active transaction"
                )
            if not self._closed:
                self._connection.close()
                self._closed = True
