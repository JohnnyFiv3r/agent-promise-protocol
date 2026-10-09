"""Adversarial regressions for durable, timely principal-refusal ingress.

The fully signed realm, policy, clock, and service evidence are controlled
fixtures. No principal inbox, external OPA endpoint, or native service is used.
"""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Event

import pytest

from agent_promise_protocol.crypto import content_ref, digest
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.fixtures import Environment
from agent_promise_protocol.storage import Ledger


class SimulatedCrash(BaseException):
    """A process loss must leave durable pending protection intact."""


@pytest.fixture
def realm(tmp_path):
    environment = Environment(tmp_path / "realm")
    try:
        yield environment
    finally:
        environment.close()


def ready_at_deadline(realm, name):
    accepted = realm.bilateral(name)["accepted"]
    realm.notify(accepted)
    realm.advance_healthy(accepted, 100)
    return accepted


def refusal_request(realm, accepted):
    refusal = realm.emit(
        "researcher_control",
        "refusal_event",
        {
            "accepted_offer_ref": content_ref(accepted),
            "refusing_principal_id": "principal:researcher",
            "authority_ref": realm.principal_policies["researcher"],
            "status_authority_agent_id": "agent:requester",
            "clock_evidence_ref": realm.clock_ref,
            "reason": "Exercise the protected principal right at its exact deadline.",
        },
        features=accepted["required_features"],
    )
    return realm.make_request(
        "researcher_control", "requester", "submit_record", refusal
    )


def admissions(ledger, accepted):
    return list(ledger.get("recovery.objects", accepted["id"])["admissions"].values())


@pytest.mark.parametrize(
    "failure_code",
    [
        "evidence_unavailable",
        "evidence_stale",
        "internal_unresolved",
        "policy_denied",
        "authority_absent",
    ],
)
def test_unknown_policy_verification_preserves_timely_refusal_and_can_resume(
    realm, failure_code
):
    accepted = ready_at_deadline(realm, "unknown-policy:" + failure_code)
    request = refusal_request(realm, accepted)
    original_policy = realm.policy.evaluate
    arrival_ms = realm.clock.now_ms

    def unavailable_policy(policy_input, now_ms):
        if (
            policy_input["act"] == "submit_record"
            and policy_input["subject"]["kind"] == "refusal_event"
        ):
            # There is deliberately no validated policy_result: this is an
            # inability to decide, rather than a signed/attributed negative act.
            raise ProtocolError(
                failure_code, "Controlled verifier is temporarily unable to decide"
            )
        return original_policy(policy_input, now_ms)

    realm.policy.evaluate = unavailable_policy
    with pytest.raises(ProtocolError) as failure:
        realm.deliver(request)
    assert failure.value.code == failure_code
    pending = admissions(realm.ledger, accepted)
    assert len(pending) == 1
    assert pending[0]["state"] == "pending"
    assert pending[0]["admitted_lower_ms"] == arrival_ms

    realm.policy.evaluate = original_policy
    realm.advance_healthy(accepted, 2)
    assert realm.status(accepted)["body"]["status"] == "unresolved"

    resumed = realm.deliver(request)
    assert resumed["body"]["outcome"] == "applied"
    completed = admissions(realm.ledger, accepted)
    assert len(completed) == 1
    assert completed[0]["admitted_lower_ms"] == arrival_ms
    assert completed[0]["outcome"] == "refused"
    assert realm.status(accepted)["body"]["status"] == "refused"


def test_invalid_proof_variant_cannot_poison_crashed_valid_refusal(realm, monkeypatch):
    accepted = ready_at_deadline(realm, "invalid-retry-proof")
    request = refusal_request(realm, accepted)
    harness = realm.harnesses["requester"]
    original_invoke = harness._invoke
    arrival_ms = realm.clock.now_ms

    def crash_before_semantic_verification(*args, **kwargs):
        raise SimulatedCrash()

    monkeypatch.setattr(harness, "_invoke", crash_before_semantic_verification)
    with pytest.raises(SimulatedCrash):
        realm.deliver(request)
    monkeypatch.setattr(harness, "_invoke", original_invoke)
    assert admissions(realm.ledger, accepted)[0]["state"] == "pending"

    invalid_variant = deepcopy(request)
    invalid_variant["proofs"][0]["signed_payload_digest"] = digest(
        "invalid proof-only copy"
    )
    with pytest.raises(ProtocolError, match="identity_mismatch"):
        realm.deliver(invalid_variant)
    assert admissions(realm.ledger, accepted)[0]["state"] == "pending"
    assert admissions(realm.ledger, accepted)[0]["admitted_lower_ms"] == arrival_ms

    realm.advance_healthy(accepted, 2)
    assert realm.status(accepted)["body"]["status"] == "unresolved"
    assert realm.deliver(request)["body"]["outcome"] == "applied"
    assert realm.status(accepted)["body"]["status"] == "refused"


def test_pending_refusal_is_committed_before_policy_callback_finishes(realm):
    accepted = ready_at_deadline(realm, "observable-before-policy")
    request = refusal_request(realm, accepted)
    arrival_ms = realm.clock.now_ms
    # Open this connection before the worker takes a write lock. Reads through
    # WAL must see the committed ingress while its later policy transaction waits.
    observer = Ledger(realm.path)
    entered, release = Event(), Event()
    original_policy = realm.policy.evaluate
    paused = False

    def delayed_policy(policy_input, now_ms):
        nonlocal paused
        if (
            not paused
            and policy_input["act"] == "submit_record"
            and policy_input["subject"]["kind"] == "refusal_event"
        ):
            paused = True
            entered.set()
            assert release.wait(5), "test did not release the policy callback"
        return original_policy(policy_input, now_ms)

    realm.policy.evaluate = delayed_policy
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            submission = executor.submit(realm.deliver, request)
            try:
                assert entered.wait(5), "refusal never reached policy evaluation"
                durable = admissions(observer, accepted)
                assert len(durable) == 1
                assert durable[0]["state"] == "pending"
                assert durable[0]["admitted_lower_ms"] == arrival_ms
                assert durable[0]["operation_key"] == [
                    realm.scope("requester"),
                    "agent:researcher_control",
                    request["body"]["operation_id"],
                ]
            finally:
                release.set()
            assert submission.result()["body"]["outcome"] == "applied"
    finally:
        realm.policy.evaluate = original_policy
        observer.close()
    assert realm.status(accepted)["body"]["status"] == "refused"
