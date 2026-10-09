"""Content-addressed storage; retrieval is separate from semantic admission."""

from copy import deepcopy
from .crypto import content_ref, digest, unsigned_digest
from .errors import ProtocolError


def same_ref(a, b):
    return (
        isinstance(a, dict)
        and isinstance(b, dict)
        and a.get("id") == b.get("id")
        and a.get("digest") == b.get("digest")
    )


def ref_key(ref):
    if (
        not isinstance(ref, dict)
        or not isinstance(ref.get("id"), str)
        or not isinstance(ref.get("digest"), str)
    ):
        raise ProtocolError("invalid_record", "invalid content reference")
    return ref["id"] + "\x00" + ref["digest"]


class RecordStore:
    def __init__(self, ledger):
        self.ledger = ledger

    def put(self, record):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise ProtocolError("invalid_record", "content requires an id")
        ref = content_ref(record)
        self.ledger.put("objects", ref_key(ref), record)
        return ref

    def resolve(self, ref):
        value = self.ledger.get("objects", ref_key(ref))
        if value is None or digest(value) != ref["digest"]:
            raise ProtocolError("evidence_unavailable", ref["id"])
        return deepcopy(value)

    def admit_identity(self, record):
        key = record["issuer_agent_id"] + "\x00" + record["id"]
        value = unsigned_digest(record)
        old = self.ledger.get("semantic_identity", key)
        if old is not None and old != value:
            raise ProtocolError("lineage_conflict", "immutable identity reused")
        if old is None:
            self.ledger.put("semantic_refs", key, content_ref(record))
        self.ledger.put("semantic_identity", key, value)
        self.ledger.put("admitted", ref_key(content_ref(record)), True)

    def is_admitted(self, ref):
        return self.ledger.get("admitted", ref_key(ref), False)
