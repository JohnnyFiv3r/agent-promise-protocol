"""Portable evidence and custody checks, not distributed formation conformance.

These cases use separately owned keys, public-only peer enrollment, separate
SQLite files and explicit A2A wire bytes. They establish preservation of signed
authorship and exact content references. They do not demonstrate remote semantic
admission, independent conflict authorities, principal recovery or federation.
The repository examples supply record shapes; their application facts remain
illustrative even after these tests replace their illustrative proofs.
"""

from contextlib import ExitStack
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path

import pytest

from agent_bazaar.crypto import (
    PROFILE,
    Registry,
    Signer,
    canonical,
    content_ref,
    strict_loads,
)
from agent_bazaar.errors import ProtocolError
from agent_bazaar.fixtures import Environment
from agent_bazaar.records import RecordStore
from agent_bazaar.schema import validate
from agent_bazaar.storage import Ledger
from agent_bazaar.transport import decode_request, encode_request


@dataclass
class Custodian:
    signer: Signer
    ledger: Ledger
    store: RecordStore
    registry: Registry


@pytest.fixture
def custodians(tmp_path):
    with ExitStack() as cleanup:
        peers = {}
        for role, agent in (
            ("buyer", "requester"),
            ("seller", "researcher"),
            ("relay", "custodian"),
        ):
            ledger = Ledger(tmp_path / f"{role}.sqlite")
            cleanup.callback(ledger.close)
            peers[role] = Custodian(
                Signer(f"agent:{agent}", f"principal:{agent}"),
                ledger,
                RecordStore(ledger),
                Registry(),
            )
        # Explicit administrative enrollment is separate from transported records.
        # Receivers see only serialized public claims, never a peer's Signer/key.
        declarations = [
            strict_loads(
                canonical(
                    {
                        "agent_id": p.signer.agent_id,
                        "principal_id": p.signer.principal_id,
                        "public_jwk": p.signer.public_jwk(),
                    }
                )
            )
            for p in peers.values()
        ]
        for peer in peers.values():
            for declaration in declarations:
                peer.registry.enroll(**declaration)
            assert all("d" not in key.jwk for key in peer.registry.keys.values())
        assert len({p.signer.kid for p in peers.values()}) == 3
        yield peers


def signed_example(peer, name, *, origin_ref=None):
    path = Path(__file__).resolve().parents[2] / "examples" / name
    record = json.loads(path.read_text())
    record.pop("proofs")
    if origin_ref is not None:
        record["body"]["origin"]["record_ref"] = origin_ref
    signed, proof = peer.signer.sign(record)
    validate(signed)
    peer.store.put(proof)
    peer.store.put(signed)
    return signed, proof


def signed_offer(peers):
    intent, intent_proof = signed_example(peers["buyer"], "requester-intent.json")
    offer, offer_proof = signed_example(
        peers["seller"],
        "researcher-standard-offer.json",
        origin_ref=content_ref(intent),
    )
    return intent, intent_proof, offer, offer_proof


def packet(sender, recipient_agent_id, subject, records):
    # This schema-valid operation is carried and verified only, never invoked.
    # Its admission-basis reference conveys no actual grant in these tests.
    raw_request = {
        "profile": PROFILE,
        "kind": "interaction_request",
        "id": f"interaction:{sender.signer.agent_id}:{subject['id']}",
        "issuer_agent_id": sender.signer.agent_id,
        "issuer_principal_id": sender.signer.principal_id,
        "created_at": "2026-10-08T18:01:00Z",
        "required_extensions": [],
        "required_features": ["bilateral"],
        "body": {
            "operation_id": f"operation:{sender.signer.agent_id}:{subject['id']}",
            "recipient_agent_id": recipient_agent_id,
            "recipient_scope_id": f"scope:{recipient_agent_id}",
            "purpose": "submit_record",
            "subject_ref": content_ref(subject),
            "admission_basis_ref": content_ref(
                {"id": "fixture:unadmitted-publication", "test_only": True}
            ),
        },
    }
    request, proof = sender.signer.sign(raw_request)
    sender.store.put(request)
    sender.store.put(proof)
    return encode_request(
        request,
        list(records) + [proof],
        message_id=f"message:{request['id']}",
    )


def materialize(store, headers, wire):
    """The receiver has only wire bytes and its own store, no sender resolver."""
    decoded = decode_request(wire, headers)
    for record in [decoded["request"], *decoded["records"]]:
        store.put(record)
    return decoded


def test_separate_stores_verify_portable_evidence_without_semantic_admission(
    custodians,
):
    buyer, seller = custodians["buyer"], custodians["seller"]
    intent, intent_proof, offer, offer_proof = signed_offer(custodians)
    reference = content_ref(offer)
    with pytest.raises(ProtocolError, match="evidence_unavailable"):
        buyer.store.resolve(reference)
    headers, wire = packet(
        seller, buyer.signer.agent_id, offer, [intent, intent_proof, offer, offer_proof]
    )
    seller.ledger.close()  # Subsequent verification cannot read the sender's store.
    decoded = materialize(buyer.store, headers, wire)
    buyer.registry.verify(decoded["request"], buyer.store.resolve, 100)
    received = buyer.store.resolve(decoded["request"]["body"]["subject_ref"])
    identity = buyer.registry.verify(received, buyer.store.resolve, 100)
    assert identity["agent_id"] == "agent:researcher"
    assert identity["principal_id"] == "principal:researcher"
    assert content_ref(received) == reference
    assert canonical(received) == canonical(offer)
    assert not buyer.store.is_admitted(reference)
    assert buyer.ledger.items("formations") == []


def test_relay_custody_preserves_original_issuer_principal_and_coordinator(custodians):
    buyer, seller, relay = (custodians[x] for x in ("buyer", "seller", "relay"))
    intent, intent_proof, offer, offer_proof = signed_offer(custodians)
    headers, wire = packet(
        seller, buyer.signer.agent_id, offer, [intent, intent_proof, offer, offer_proof]
    )
    first = materialize(relay.store, headers, wire)
    relay.registry.verify(first["request"], relay.store.resolve, 100)
    # A custody hop forwards the original signed logical operation unchanged.
    # It does not pretend that relay possession authorizes semantic submission.
    headers, wire = encode_request(
        first["request"], first["records"], message_id="message:custody-forward"
    )
    second = materialize(buyer.store, headers, wire)
    received = buyer.store.resolve(second["request"]["body"]["subject_ref"])
    buyer.registry.verify(received, buyer.store.resolve, 100)
    source = buyer.store.resolve(received["body"]["origin"]["record_ref"])
    buyer.registry.verify(source, buyer.store.resolve, 100)
    assert content_ref(received) == content_ref(offer)
    assert received["issuer_agent_id"] == "agent:researcher"
    assert received["issuer_principal_id"] == "principal:researcher"
    assert (
        received["body"]["own_promises"][0]["promiser_agent_id"] == "agent:researcher"
    )
    assert (
        received["body"]["origin"]["coordinator_agent_id"] == source["issuer_agent_id"]
    )
    assert source["issuer_agent_id"] == "agent:requester"
    assert not relay.store.is_admitted(content_ref(received))
    assert not buyer.store.is_admitted(content_ref(received))


def test_custodian_signature_cannot_substitute_for_seller_authorship(custodians):
    buyer, relay = custodians["buyer"], custodians["relay"]
    _, _, offer, _ = signed_offer(custodians)
    with pytest.raises(ProtocolError, match="identity_mismatch"):
        relay.signer.sign(offer)
    # Even a hostile host that signs a relabeled payload cannot splice that
    # signature into the original seller record, despite being a trusted peer.
    relabeled = deepcopy(offer)
    relabeled["issuer_agent_id"] = relay.signer.agent_id
    relabeled["issuer_principal_id"] = relay.signer.principal_id
    host_record, host_proof = relay.signer.sign(relabeled)
    forged = deepcopy(offer)
    forged["proofs"] = host_record["proofs"]
    headers, wire = packet(relay, buyer.signer.agent_id, forged, [forged, host_proof])
    decoded = materialize(buyer.store, headers, wire)
    buyer.registry.verify(decoded["request"], buyer.store.resolve, 100)
    forged = buyer.store.resolve(decoded["request"]["body"]["subject_ref"])
    with pytest.raises(ProtocolError):
        buyer.registry.verify(forged, buyer.store.resolve, 100)
    assert not buyer.store.is_admitted(content_ref(forged))


def test_missing_remote_proof_blocks_verification_without_sender_fallback(custodians):
    buyer, seller = custodians["buyer"], custodians["seller"]
    _, _, offer, proof = signed_offer(custodians)
    headers, wire = packet(seller, buyer.signer.agent_id, offer, [offer])
    decoded = materialize(buyer.store, headers, wire)
    buyer.registry.verify(decoded["request"], buyer.store.resolve, 100)
    received = buyer.store.resolve(decoded["request"]["body"]["subject_ref"])
    assert seller.store.resolve(content_ref(proof)) == proof
    with pytest.raises(ProtocolError, match="evidence_unavailable"):
        buyer.registry.verify(received, buyer.store.resolve, 100)
    assert not buyer.store.is_admitted(content_ref(received))


def test_current_harness_rejects_valid_peer_from_incompatible_authority(tmp_path):
    env = Environment(tmp_path / "common-authority-limit")
    try:
        record = env.publications["researcher"]
        receiver = env.harnesses["requester"]
        # Signature remains valid; local configuration rejects incompatible
        # authority scope rather than silently claiming federated support.
        receiver.registry.verify(record, receiver.resolve, receiver.now())
        env.enrollments["agent:researcher"].authority_scope_id = "authority:independent"
        with pytest.raises(ProtocolError, match="incompatible authority domain"):
            receiver.verify(record)
        assert env.ledger.items("formations") == []
    finally:
        env.close()
