"""C8 uses a deterministic TEST-ONLY adapter; no native service is contacted."""

from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from agent_promise_protocol.crypto import content_ref, digest
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.handoff import (
    FakeAdapter,
    Handoff,
    decode_native_wrapper,
    handoff_key,
    native_wrapper,
)
from agent_promise_protocol.storage import Ledger


class Crash(BaseException):
    """Bypass ordinary adapter error handling to simulate process death."""


def record(kind, record_id, body, issuer="alice"):
    return {
        "id": record_id,
        "kind": kind,
        "issuer_agent_id": issuer,
        "body": body,
        "proofs": [{"test_proof": "one"}],
    }


class World:
    def __init__(self, tmp_path):
        self.path = tmp_path / "handoff.sqlite"
        self.ledger = Ledger(self.path)
        self.records = {}
        self.now = 1000
        self.serial = 0
        self.clear = True
        self.gate_calls = 0
        self.contract = self.save({"id": "test-adapter-contract", "test_only": True})
        self.adapter = FakeAdapter(contract_ref=self.contract)
        self.candidate = record(
            "candidate_terms",
            "candidate",
            {
                "own_promises": [
                    {"promiser_agent_id": "alice", "promise_id": "do-one-thing"}
                ],
                "handoff_rules": {
                    "preclearance": "no_effects",
                    "policy_ref": self.contract,
                },
            },
        )
        candidate_ref = self.save(self.candidate)
        self.adoption = record(
            "terms_adoption",
            "alice-adopts",
            {
                "candidate_ref": candidate_ref,
                "adopted_own_promise_ids": ["do-one-thing"],
            },
        )
        self.accepted = record(
            "accepted_offer",
            "accepted",
            {
                "candidate_ref": candidate_ref,
                "adoption_refs": [self.save(self.adoption)],
            },
        )
        payload = {
            "id": "native-input",
            "target": "test-only-target",
            "message": "test-only-action",
        }
        self.request = record(
            "handoff_request",
            "handoff",
            {
                "handoff_id": "h1",
                "agreement_ref": self.save(self.accepted),
                "action_ref": {
                    "promiser_agent_id": "alice",
                    "promise_id": "do-one-thing",
                },
                "action_instance": {
                    "type_uri": "urn:test:one-time",
                    "parameters": {"occurrence": "only"},
                },
                "adapter_agent_id": "test-adapter",
                "adapter_profile_uri": "urn:test:adapter:v1",
                "request_payload_ref": self.save(payload),
                "dependency_evidence_refs": [],
                "clearance_refs": [],
                "authority_refs": [self.contract],
                "effect_class": "externally_effective",
            },
        )
        self.save(self.request)
        self.handoff = self.make_handoff()

    def save(self, rec):
        self.records[content_ref(rec)["digest"]] = deepcopy(rec)
        return content_ref(rec)

    def resolve(self, ref):
        return deepcopy(self.records.get(ref["digest"]))

    def emit(self, kind, body):
        self.serial += 1
        result = record(
            kind, kind + ":" + str(self.serial), body, issuer="boundary-authority"
        )
        self.save(result)
        return result

    @staticmethod
    def action_check(request, accepted, candidate):
        return request["body"]["action_instance"] == {
            "type_uri": "urn:test:one-time",
            "parameters": {"occurrence": "only"},
        }

    def gate(self, request, prepared, native_auth, now_ms):
        self.gate_calls += 1
        return {
            "allow": self.clear,
            "valid_until_ms": now_ms + 1000,
            "authorization_decision_ref": self.contract,
            "gate_evidence_refs": [self.contract],
        }

    def make_handoff(self, ledger=None, adapter=None):
        boundary = Handoff(
            ledger or self.ledger,
            self.resolve,
            emit=self.emit,
            action_check=self.action_check,
            gate_check=self.gate,
            clock=lambda: self.now,
        )
        boundary.register(
            "test-adapter",
            "urn:test:adapter:v1",
            adapter or self.adapter,
            self.contract,
        )
        return boundary

    def key(self):
        return handoff_key(
            self.accepted,
            self.request["body"]["action_ref"],
            self.request["body"]["action_instance"],
        )

    def restart(self):
        self.ledger.close()
        self.ledger = Ledger(self.path)
        self.handoff = self.make_handoff()


def test_preparation_is_effect_free_frozen_and_does_not_imply_clearance(tmp_path):
    world = World(tmp_path)
    world.clear = False
    exact_bytes = b'{ "native_signature": "preserve spaces", "target" : "/test" }\n'
    world.adapter.native_bytes = exact_bytes
    result = world.handoff.prepare(world.request)
    assert result["receipt"]["body"]["outcome"] == "prepared"
    assert world.adapter.dispatch_calls == 0
    assert world.adapter.operations == {}
    assert world.gate_calls == 0
    prepared = result["prepared"]["body"]
    assert prepared["native_operation_key"] == "app-rp1-" + world.key()[7:]
    wrapper = world.handoff.resolve(prepared["native_request_ref"])
    assert decode_native_wrapper(wrapper, prepared["native_request_ref"]) == exact_bytes
    assert world.handoff.prepare(world.request) == result
    assert world.adapter.prepare_calls == 1
    assert world.handoff.dispatch(world.request)["body"]["outcome"] == "blocked"
    assert world.adapter.dispatch_calls == 0


def test_native_authority_is_separate_fresh_and_checked_again_at_dispatch(tmp_path):
    world = World(tmp_path)
    world.handoff.prepare(world.request)
    world.adapter.authorized = False
    assert world.handoff.dispatch(world.request)["body"]["outcome"] == "blocked"
    assert world.adapter.dispatch_calls == 0
    assert world.gate_calls == 0
    world.adapter.authorized = True
    world.handoff.gate_check = lambda *args: {
        "allow": True,
        "valid_until_ms": world.now + 5001,
        "authorization_decision_ref": world.contract,
        "gate_evidence_refs": [world.contract],
    }
    receipt = world.handoff.dispatch(world.request)
    assert receipt["body"]["outcome"] == "blocked"
    assert receipt["body"]["reason_code"] == "authority_stale"
    assert world.adapter.dispatch_calls == 0
    world.handoff.gate_check = world.gate
    assert world.handoff.dispatch(world.request)["body"]["outcome"] == "dispatched"
    assert world.adapter.dispatch_calls == 1


def test_marker_commits_before_native_call_and_outer_transactions_are_rejected(
    tmp_path,
):
    world = World(tmp_path)
    world.handoff.prepare(world.request)
    with world.ledger.transaction():
        with pytest.raises(ProtocolError, match="dispatch_transaction"):
            world.handoff.dispatch(world.request)
    assert world.adapter.dispatch_calls == 0

    def assert_marker(name):
        if name == "after_dispatch_marker":
            independent = Ledger(world.path)
            persisted = independent.get("handoff_slots", world.key())
            assert persisted["dispatch_attempt_started"] is True
            assert persisted["receipts"]["dispatch"]["body"]["outcome"] == "in_doubt"
            assert world.adapter.dispatch_calls == 0
            independent.close()

    world.handoff.failpoint = assert_marker
    result = world.handoff.dispatch(world.request)
    assert result["body"]["outcome"] == "dispatched"
    world.handoff.dispatch(world.request)
    assert world.adapter.dispatch_calls == 1


def test_crash_after_marker_stays_in_doubt_across_restart_without_send(tmp_path):
    world = World(tmp_path)
    world.handoff.prepare(world.request)

    def crash(name):
        if name == "after_dispatch_marker":
            raise Crash()

    world.handoff.failpoint = crash
    with pytest.raises(Crash):
        world.handoff.dispatch(world.request)
    assert world.adapter.dispatch_calls == 0
    world.restart()
    assert world.handoff.dispatch(world.request)["body"]["outcome"] == "in_doubt"
    assert world.handoff.reconcile(world.request)["body"]["outcome"] == "in_doubt"
    assert world.adapter.dispatch_calls == 0
    assert world.adapter.reconcile_calls == 1


@pytest.mark.parametrize("failure", ["lost_reply", "crash_after_effect"])
def test_possible_effect_never_retries_after_reply_loss_or_restart(tmp_path, failure):
    world = World(tmp_path)
    world.handoff.prepare(world.request)
    if failure == "lost_reply":
        world.adapter.lose_reply = True
        assert world.handoff.dispatch(world.request)["body"]["outcome"] == "in_doubt"
    else:

        def crash(name):
            if name == "after_native_dispatch":
                raise Crash()

        world.handoff.failpoint = crash
        with pytest.raises(Crash):
            world.handoff.dispatch(world.request)
    assert world.adapter.dispatch_calls == 1
    assert len(world.adapter.operations) == 1
    world.restart()
    world.clear = False  # Later refusal/authority loss must not erase the past attempt.
    assert world.handoff.dispatch(world.request)["body"]["outcome"] == "in_doubt"
    assert world.handoff.reconcile(world.request)["body"]["outcome"] == "dispatched"
    assert world.adapter.dispatch_calls == 1


def test_alternate_adapter_and_proof_variants_cannot_create_another_effect(tmp_path):
    world = World(tmp_path)
    world.handoff.prepare(world.request)
    world.handoff.dispatch(world.request)
    alternate = FakeAdapter(contract_ref=world.contract)
    world.handoff.register(
        "another-adapter", "urn:test:adapter:v1", alternate, world.contract
    )
    routed = deepcopy(world.request)
    routed["id"] = "new-transport-request"
    routed["body"]["handoff_id"] = "new-operation-id"
    routed["body"]["adapter_agent_id"] = "another-adapter"
    with pytest.raises(ProtocolError, match="handoff_conflict"):
        world.handoff.prepare(routed)
    with pytest.raises(ProtocolError, match="handoff_conflict"):
        world.handoff.dispatch(routed)
    resigned = deepcopy(world.accepted)
    resigned["proofs"] = [{"test_proof": "second"}]
    world.save(resigned)
    assert (
        handoff_key(
            resigned,
            world.request["body"]["action_ref"],
            world.request["body"]["action_instance"],
        )
        == world.key()
    )
    proof_request = deepcopy(world.request)
    proof_request["body"]["agreement_ref"] = content_ref(resigned)
    with pytest.raises(ProtocolError, match="handoff_conflict"):
        world.handoff.prepare(proof_request)
    assert world.adapter.dispatch_calls == 1
    assert alternate.dispatch_calls == 0
    assert len(world.ledger.items("handoff_slots")) == 1


def test_new_request_id_recovers_same_frozen_disposition(tmp_path):
    world = World(tmp_path)
    original = world.handoff.prepare(world.request)
    duplicate = deepcopy(world.request)
    duplicate["id"] = "new-request-id"
    duplicate["body"]["handoff_id"] = "new-handoff-id"
    assert world.handoff.prepare(duplicate) == original
    first = world.handoff.dispatch(duplicate)
    assert world.handoff.dispatch(world.request) == first
    assert first["body"]["handoff_ref"] == content_ref(world.request)
    assert world.adapter.dispatch_calls == 1


def test_invented_occurrence_and_other_authors_adoption_are_not_permission(tmp_path):
    world = World(tmp_path)
    invented = deepcopy(world.request)
    invented["body"]["action_instance"]["parameters"]["occurrence"] = "a-new-random-id"
    with pytest.raises(ProtocolError, match="action_authority_absent"):
        world.handoff.prepare(invented)
    wrong_adoption = deepcopy(world.adoption)
    wrong_adoption["issuer_agent_id"] = "bob"
    accepted = deepcopy(world.accepted)
    accepted["body"]["adoption_refs"] = [world.save(wrong_adoption)]
    wrong = deepcopy(world.request)
    wrong["body"]["agreement_ref"] = world.save(accepted)
    with pytest.raises(ProtocolError, match="action_mismatch"):
        world.handoff.prepare(wrong)
    assert world.adapter.prepare_calls == 0


def test_absent_native_record_and_unavailable_reconcile_do_not_prove_no_effect(
    tmp_path,
):
    world = World(tmp_path)
    world.handoff.prepare(world.request)
    world.handoff.dispatch(world.request)
    world.adapter.reconcile = lambda key: {
        "outcome": "not_dispatched",
        "native_evidence_refs": [],
    }
    result = world.handoff.reconcile(world.request)
    assert result["body"]["outcome"] == "in_doubt"
    world.handoff.dispatch(world.request)
    assert world.adapter.dispatch_calls == 1
    retained = world.ledger.get("handoff_slots", world.key())
    assert retained["native_observation_history"][0]["outcome"] == "dispatched"


def test_authority_expiring_after_commit_cannot_be_queued_for_later_send(tmp_path):
    world = World(tmp_path)
    world.handoff.prepare(world.request)

    def time_passes(name):
        if name == "after_dispatch_marker":
            world.now += 1001

    world.handoff.failpoint = time_passes
    result = world.handoff.dispatch(world.request)
    assert result["body"]["outcome"] == "not_dispatched"
    assert world.adapter.dispatch_calls == 0
    world.handoff.dispatch(world.request)
    assert world.adapter.dispatch_calls == 0


def test_receipt_chains_are_per_key_and_phase_and_reconcile_is_read_only(tmp_path):
    world = World(tmp_path)
    world.handoff.prepare(world.request)
    before = world.handoff.reconcile(world.request)
    assert before["body"]["outcome"] == "not_dispatched"
    assert world.adapter.reconcile_calls == 0
    dispatched = world.handoff.dispatch(world.request)
    reconciled = world.handoff.reconcile(world.request)
    assert (
        dispatched["body"]["revision"] == 2
    )  # durable intent then observed submission
    assert reconciled["body"]["revision"] == 2
    assert (
        reconciled["body"]["previous_receipt_digest"] == content_ref(before)["digest"]
    )
    assert world.adapter.dispatch_calls == 1
    assert world.adapter.reconcile_calls == 1


def test_native_wrapper_checks_both_full_reference_and_exact_payload_digest():
    wrapper = native_wrapper(
        "native", "application/octet-stream", b"\x00\xff\n{ untouched }"
    )
    assert (
        decode_native_wrapper(wrapper, content_ref(wrapper))
        == b"\x00\xff\n{ untouched }"
    )
    altered = deepcopy(wrapper)
    altered["payload_digest"] = digest("wrong native bytes")
    with pytest.raises(ProtocolError, match="native_request_invalid"):
        decode_native_wrapper(altered, content_ref(altered))
    with pytest.raises(ProtocolError, match="native_request_invalid"):
        decode_native_wrapper(
            wrapper, {"id": "different", "digest": content_ref(wrapper)["digest"]}
        )
    noncanonical = deepcopy(wrapper)
    noncanonical["payload"] += "="
    with pytest.raises(ProtocolError, match="native_request_invalid"):
        decode_native_wrapper(noncanonical, content_ref(noncanonical))


def test_adapter_cannot_self_declare_unsupported_final_absence(tmp_path):
    world = World(tmp_path)
    world.handoff.prepare(world.request)

    def crash(name):
        if name == "after_dispatch_marker":
            raise Crash()

    world.handoff.failpoint = crash
    with pytest.raises(Crash):
        world.handoff.dispatch(world.request)
    world.adapter.reconcile = lambda key: {
        "outcome": "not_dispatched",
        "final_absence": True,
        "native_evidence_refs": [world.contract],
    }
    assert world.handoff.reconcile(world.request)["body"]["outcome"] == "in_doubt"
    assert world.adapter.dispatch_calls == 0


def test_second_enforcer_observes_committed_attempt_while_first_is_in_flight(tmp_path):
    world = World(tmp_path)
    world.handoff.prepare(world.request)
    independent_ledger = Ledger(world.path)
    independent_adapter = FakeAdapter(
        contract_ref=world.contract, operations=world.adapter.operations
    )
    independent_handoff = world.make_handoff(independent_ledger, independent_adapter)
    marked, release = Event(), Event()

    def pause(name):
        if name == "after_dispatch_marker":
            marked.set()
            assert release.wait(5), "test failed to release the original dispatch"

    world.handoff.failpoint = pause
    with ThreadPoolExecutor(max_workers=1) as executor:
        attempt = executor.submit(world.handoff.dispatch, world.request)
        try:
            assert marked.wait(5), "original dispatch never committed its marker"
            duplicate = independent_handoff.dispatch(world.request)
            assert duplicate["body"]["outcome"] == "in_doubt"
            assert independent_adapter.dispatch_calls == 0
        finally:
            release.set()
        assert attempt.result()["body"]["outcome"] == "dispatched"
    independent_ledger.close()
    assert world.adapter.dispatch_calls == 1
    assert len(world.adapter.operations) == 1
