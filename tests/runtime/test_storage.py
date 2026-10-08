import concurrent.futures
import os
from pathlib import Path
import subprocess
import sys

import pytest

from agent_bazaar.errors import ProtocolError
from agent_bazaar.storage import Ledger


def test_json_copy_revision_and_nested_savepoint_rollback(tmp_path):
    ledger = Ledger(tmp_path / "authority.db")
    source = {"nested": [1]}
    assert ledger.revision == 0
    with ledger.transaction():
        assert ledger.in_transaction
        ledger.put("records", "a", source)
        source["nested"].append(2)
        with pytest.raises(RuntimeError):
            with ledger.transaction():
                ledger.put("records", "a", {"wrong": True})
                ledger.put("records", "rolled-back", {})
                raise RuntimeError("rollback only this savepoint")
        assert ledger.get("records", "a") == {"nested": [1]}
        assert ledger.get("records", "rolled-back") is None
        ledger.put("records", "b", [2])
        assert ledger.revision == 0
    assert not ledger.in_transaction
    assert ledger.revision == 1
    result = ledger.get("records", "a")
    result["nested"].append(9)
    assert ledger.get("records", "a") == {"nested": [1]}
    default = {"a": []}
    ledger.get("records", "missing", default)["a"].append(1)
    assert default == {"a": []}
    with ledger.transaction():
        ledger.get("records", "a")
    assert ledger.revision == 1
    with pytest.raises(RuntimeError):
        with ledger.transaction():
            ledger.delete("records", "a")
            raise RuntimeError("outer rollback")
    assert ledger.revision == 1
    assert ledger.get("records", "a") == {"nested": [1]}
    ledger.close()


def test_conflicting_writers_serialize_check_and_update(tmp_path):
    path = tmp_path / "authority.db"
    ledgers = [Ledger(path), Ledger(path)]
    ledgers[0].put("capacity", "one", {"available": 1, "winner": None})

    def claim(index):
        with ledgers[index].transaction():
            state = ledgers[index].get("capacity", "one")
            if state["available"] == 0:
                return False
            state.update(available=0, winner=index)
            ledgers[index].put("capacity", "one", state)
            return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(claim, (0, 1))) == [False, True]
    assert ledgers[0].revision == ledgers[1].revision == 2
    assert ledgers[0].get("capacity", "one")["available"] == 0
    for ledger in ledgers:
        ledger.close()


def test_process_crash_keeps_committed_tombstones_and_discards_open_write(tmp_path):
    path = tmp_path / "authority.db"
    program = """
import os, sys
from agent_bazaar.storage import Ledger
ledger = Ledger(sys.argv[1])
ledger.put('operation.tombstones', 'op-1', {'outcome': 'declined'})
with ledger.transaction():
    ledger.put('operation.tombstones', 'op-2', {'outcome': 'applied'})
    os._exit(17)
"""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
    proc = subprocess.run([sys.executable, "-c", program, str(path)], env=env)
    assert proc.returncode == 17
    recovered = Ledger(path)
    assert recovered.get("operation.tombstones", "op-1") == {"outcome": "declined"}
    assert recovered.get("operation.tombstones", "op-2") is None
    assert recovered.revision == 1
    assert recovered._connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert recovered._connection.execute("PRAGMA synchronous").fetchone()[0] == 2
    recovered.close()


@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), {1: "not-json"}, {"set": {1}}]
)
def test_rejects_non_json_values(value):
    ledger = Ledger(":memory:")
    with pytest.raises(ProtocolError):
        ledger.put("data", "invalid", value)
    assert ledger.revision == 0
    ledger.close()


def test_no_revision_for_rolled_back_inner_writes():
    ledger = Ledger(":memory:")
    with ledger.transaction():
        with pytest.raises(RuntimeError):
            with ledger.transaction():
                ledger.put("x", "y", 1)
                raise RuntimeError()
    assert ledger.revision == 0
    assert ledger.items("x") == []
    ledger.close()
