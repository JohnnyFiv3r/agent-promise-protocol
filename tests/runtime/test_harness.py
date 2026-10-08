"""Real signed end-to-end records through the C3 harness boundary.

The enrolled domain, time, policies, principal inbox and native services are
explicit controlled fixtures. No fake signature metadata or live integrations.
"""

from copy import deepcopy
import json
import subprocess
import sys

import pytest

from agent_bazaar.crypto import content_ref, PROOF_PROFILE
from agent_bazaar.errors import ProtocolError
from agent_bazaar.fixtures import Environment
from agent_bazaar.schema import validate


@pytest.fixture
def env(tmp_path):
    environment = Environment(tmp_path)
    yield environment
    environment.close()


def test_signed_bilateral_is_real_agent_agreement_without_invented_counterpromise(env):
    agreement = env.bilateral()
    candidate = agreement["candidate"]
    accepted = agreement["accepted"]
    assert len(candidate["body"]["participants"]) == 2
    assert len(candidate["body"]["own_promises"]) == 1
    assert agreement["adoptions"][0]["body"]["adopted_own_promise_ids"] == []
    assert accepted["body"]["candidate_ref"] == content_ref(candidate)
    assert env.status(accepted)["body"]["status"] == "pending_refusal_windows"
    for record in env.records.values():
        if "kind" in record or "type_uri" in record:
            validate(record)
            env.registry.verify(record, env.store.resolve, env.clock.now_ms)
            assert record["proofs"][0]["suite_uri"] == PROOF_PROFILE
    used = env.ledger.get("resource_used", "research-slots:researcher")
    env.restart()
    recovered = env.require_applied(
        env.invoke("researcher", "requester", "finalize_candidate", candidate)
    )
    assert recovered == accepted
    assert env.ledger.get("resource_used", "research-slots:researcher") == used == 1


def test_replay_is_same_receipt_and_altered_operation_does_not_replace_original(env):
    bilateral = env.bilateral()
    candidate = bilateral["candidate"]
    receipt = env.invoke(
        "researcher", "requester", "finalize_candidate", candidate, "finalize:repeat"
    )
    original = env.last_request
    quota_before = env.ledger.items("quota")
    env.clock.advance(5)
    assert env.deliver(original) == receipt
    assert env.ledger.items("quota") == quota_before
    changed = deepcopy(original)
    changed["body"]["purpose"] = "query_status"
    changed["body"]["subject_ref"] = content_ref(bilateral["accepted"])
    altered = env.sign("researcher", changed)
    conflict = env.deliver(altered)
    assert conflict["body"]["outcome"] == "conflict"
    assert conflict["body"]["reason_code"] == "operation_conflict"
    assert conflict["body"]["revision"] == 1
    assert env.deliver(altered) == conflict
    assert env.deliver(original) == receipt


def test_signed_candidate_cannot_splice_a_different_actor_promise(env):
    agreement = env.bilateral(finalize=False)
    changed = deepcopy(agreement["candidate"])
    changed["id"] = changed["body"]["candidate_id"] = "candidate:spliced"
    changed["body"]["own_promises"][0]["action"]["parameters"]["scope"] = (
        "A different unissued obligation"
    )
    signed = env.sign("requester", changed)
    receipt = env.invoke("requester", "requester", "submit_record", signed)
    assert receipt["body"]["outcome"] == "blocked"
    assert receipt["body"]["reason_code"] == "invalid_record"
    assert env.harnesses["requester"].store.is_admitted(content_ref(signed)) is False
    assert env.ledger.items("formations") == []


def test_signature_tampering_cannot_enter_semantic_state(env):
    agreement = env.bilateral()
    request = env.make_request(
        "researcher", "requester", "finalize_candidate", agreement["candidate"]
    )
    request["body"]["operation_id"] = "tampered"
    before = env.ledger.items("operations")
    with pytest.raises(ProtocolError):
        env.deliver(request)
    assert env.ledger.items("operations") == before


def test_refusal_at_deadline_is_absorbing_after_restart_and_cannot_dispatch(env):
    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted, 100)
    assert env.status(accepted)["body"]["status"] == "pending_refusal_windows"
    receipt = env.refuse(accepted)
    request = env.last_request
    assert receipt["body"]["outcome"] == "applied"
    assert env.status(accepted)["body"]["status"] == "refused"
    env.restart()
    env.clock.advance(10_000)
    assert env.deliver(request) == receipt
    assert env.status(accepted)["body"]["status"] == "refused"
    handoff = env.handoff_request(accepted)
    assert env.handoff_phase(handoff, "prepare")["body"]["outcome"] == "prepared"
    assert env.handoff_phase(handoff, "dispatch")["body"]["outcome"] == "blocked"
    assert env.adapter.dispatch_calls == 0


def test_principal_refusal_uses_reserved_admission_after_negotiation_exhaustion(env):
    accepted = env.bilateral()["accepted"]
    # The declaration is finite and the negotiation pool has no remaining work.
    pool = env.scope("requester") + ":requester:negotiation"
    env.ledger.put(
        "quota",
        pool,
        {"messages": 256, "bytes": 16 * 1024 * 1024, "work": 256, "in_flight": 0},
    )
    receipt = env.refuse(accepted)
    assert receipt["body"]["outcome"] == "applied"
    assert env.status(accepted)["body"]["status"] == "refused"
    assert env.ledger.get("quota", pool)["messages"] == 256


def test_ordinary_negotiation_authority_does_not_grant_principal_refusal(env):
    accepted = env.bilateral()["accepted"]
    unauthorized = env.emit(
        "researcher",
        "refusal_event",
        {
            "accepted_offer_ref": content_ref(accepted),
            "refusing_principal_id": "principal:researcher",
            "authority_ref": env.principal_policies["researcher"],
            "status_authority_agent_id": "agent:requester",
            "clock_evidence_ref": env.clock_ref,
        },
    )
    receipt = env.invoke("researcher", "requester", "submit_record", unauthorized)
    assert receipt["body"]["outcome"] == "blocked"
    assert receipt["body"]["reason_code"] == "authority_absent"
    assert env.status(accepted)["body"]["status"] == "pending_refusal_windows"


def test_admitted_refusal_pending_verification_survives_restart(env):
    class Crash(BaseException):
        pass

    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted, 100)

    def fail(name):
        if name == "after_operation_admission":
            raise Crash()

    env.harnesses["requester"].failpoint = fail
    with pytest.raises(Crash):
        env.refuse(accepted)
    original = env.last_request
    env.restart()
    env.advance_healthy(accepted, 100)
    assert env.status(accepted)["body"]["status"] == "unresolved"
    assert env.deliver(original)["body"]["outcome"] == "applied"
    assert env.status(accepted)["body"]["status"] == "refused"


def test_notice_and_clock_alone_cannot_replace_continuous_health(env):
    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.clock.advance(200)
    assert env.status(accepted)["body"]["status"] == "unresolved"
    assert env.adapter.dispatch_calls == 0


def test_handoff_preparation_rechecks_clearance_then_dispatches_at_most_once(env):
    accepted = env.bilateral()["accepted"]
    request = env.handoff_request(accepted)
    assert env.handoff_phase(request, "prepare")["body"]["outcome"] == "prepared"
    assert env.adapter.dispatch_calls == 0
    assert env.handoff_phase(request, "dispatch")["body"]["outcome"] == "blocked"
    env.notify(accepted)
    env.advance_healthy(accepted)
    dispatched = env.handoff_phase(request, "dispatch")
    assert dispatched["body"]["outcome"] == "dispatched"
    assert env.adapter.dispatch_calls == 1
    env.restart()
    assert env.handoff_phase(request, "dispatch") == dispatched
    assert env.adapter.dispatch_calls == 1
    assert env.handoff_phase(request, "reconcile")["body"]["outcome"] == "dispatched"
    assert env.adapter.dispatch_calls == 1


def test_three_agent_composition_blocks_current_uncleared_dependency(env):
    chain = env.compose()
    assert len(chain["components"]) == 2
    source = chain["components"]["sources"]["accepted"]
    review = chain["components"]["review"]["accepted"]
    env.notify(review)
    env.advance_healthy(review)
    assert env.status(review)["body"]["status"] == "refusal_windows_closed"
    request = env.handoff_request(review)
    env.handoff_phase(request, "prepare")
    assert env.handoff_phase(request, "dispatch")["body"]["outcome"] == "blocked"
    assert env.adapter.dispatch_calls == 0
    env.notify(source)
    env.advance_healthy([source, review])
    assert env.handoff_phase(request, "dispatch")["body"]["outcome"] == "dispatched"
    assert env.adapter.dispatch_calls == 1


def test_refused_component_blocks_dependent_handoff_without_undoing_agreement(env):
    chain = env.compose()
    source = chain["components"]["sources"]["accepted"]
    review = chain["components"]["review"]["accepted"]
    env.require_applied(env.refuse(source))
    env.notify(review)
    env.advance_healthy(review)
    request = env.handoff_request(review)
    env.handoff_phase(request, "prepare")
    assert env.handoff_phase(request, "dispatch")["body"]["outcome"] == "blocked"
    assert env.adapter.dispatch_calls == 0
    assert (
        env.harnesses["requester"].agreement_for_candidate(
            review["body"]["candidate_ref"]
        )
        == review
    )
    assert env.status(source)["body"]["status"] == "refused"


def test_shared_capacity_cannot_be_recreated_by_a_new_negotiation(env):
    env.ledger.put(
        "resource_limits",
        "research-slots:researcher",
        {"scope": env.harnesses["requester"].authority_scope, "limit": 1},
    )
    env.bilateral("first")
    second = env.bilateral("second", finalize=False)
    receipt = env.invoke(
        "researcher", "requester", "finalize_candidate", second["candidate"]
    )
    assert receipt["body"]["outcome"] == "conflict"
    assert receipt["body"]["reason_code"] == "selection_conflict"
    assert len(env.ledger.items("formations")) == 1
    assert env.ledger.get("resource_used", "research-slots:researcher") == 1


def test_harness_crash_after_dispatch_marker_recovers_in_doubt_without_sending(env):
    class Crash(BaseException):
        pass

    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted)
    request = env.handoff_request(accepted)
    env.handoff_phase(request, "prepare")

    def fail(name):
        if name == "after_dispatch_marker":
            raise Crash()

    env.harnesses["requester"].handoff.failpoint = fail
    with pytest.raises(Crash):
        env.handoff_phase(request, "dispatch")
    original = env.last_request
    assert env.adapter.dispatch_calls == 0
    env.restart()
    recovered = env.require_applied(env.deliver(original))
    assert recovered["body"]["outcome"] == "in_doubt"
    assert env.handoff_phase(request, "dispatch")["body"]["outcome"] == "in_doubt"
    assert env.handoff_phase(request, "reconcile")["body"]["outcome"] == "in_doubt"
    assert env.adapter.dispatch_calls == 0


def test_demo_cli_reports_measured_simulation_results(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "agent_bazaar.demo",
            "demo",
            "--directory",
            str(tmp_path / "demo"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    output = json.loads(completed.stdout)
    assert output["mode"] == "controlled simulation"
    assert (
        output["evidence_scope"]["real_orders_payments_or_research_performance"]
        is False
    )
    assert output["scenarios"]["bilateral"]["simulated_native_calls_after_replay"] == 1
    assert (
        output["scenarios"]["refusal_at_deadline"]["status_after_restart"] == "refused"
    )
    assert output["scenarios"]["refusal_at_deadline"]["simulated_native_calls"] == 0
    assert (
        output["scenarios"]["three_agent_composition"]["review_before_source_clearance"]
        == "blocked"
    )
    assert output["scenarios"]["three_agent_composition"]["simulated_native_calls"] == 2
