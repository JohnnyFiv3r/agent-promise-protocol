"""Current participant delegation is required for clearance and native reliance.

All identities, policies, notice services and native effects are controlled
fixtures. The regression uses real signed agreements and the ordinary harness
boundary; it does not treat a pinned delegation reference as a live grant.
"""

import pytest

from agent_promise_protocol.crypto import content_ref
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.fixtures import Environment


@pytest.fixture
def env(tmp_path):
    environment = Environment(tmp_path)
    yield environment
    environment.close()


def grant_for(env, actor):
    return next(g for g in env.policy.grants if g["agent_id"] == "agent:" + actor)


def lose_authority(env, actor, change, monkeypatch):
    grant = grant_for(env, actor)
    if change == "revoked":
        grant["revoked"] = True
    elif change == "expired":
        grant["valid_until_ms"] = env.clock.now_ms
    else:
        evaluate = env.policy.evaluate

        def unavailable(request, now_ms):
            if (
                request["actor"]["agent_id"] == "agent:" + actor
                and request["act"] == "authority_commit"
            ):
                raise ProtocolError("policy_unavailable", "controlled owner outage")
            return evaluate(request, now_ms)

        monkeypatch.setattr(env.policy, "evaluate", unavailable)


@pytest.mark.parametrize("change", ["revoked", "expired", "unavailable"])
def test_nonexecutor_authority_loss_blocks_prepared_bilateral_dispatch(
    env, monkeypatch, change
):
    agreement = env.bilateral()
    accepted = agreement["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted)
    assert env.status(accepted)["body"]["status"] == "refusal_windows_closed"
    request = env.handoff_request(accepted)
    assert env.handoff_phase(request, "prepare")["body"]["outcome"] == "prepared"

    # Researcher remains fully authorized to dispatch. The other participant's
    # current authority must still be evaluated despite its unchanged enrollment.
    lose_authority(env, "requester", change, monkeypatch)
    assert env.enrollments["agent:requester"].active
    observed = env.harnesses["requester"]._status_for_composition(accepted)
    assert observed["status"] == "unresolved"
    assert observed["authority_evidence_refs"] == []
    assert env.handoff_phase(request, "dispatch")["body"]["outcome"] == "blocked"
    assert env.adapter.dispatch_calls == 0
    assert (
        env.harnesses["requester"].agreement_for_candidate(
            content_ref(agreement["candidate"])
        )
        == accepted
    )


@pytest.mark.parametrize("change", ["revoked", "expired", "unavailable"])
def test_dependency_authority_loss_blocks_otherwise_cleared_component(
    env, monkeypatch, change
):
    chain = env.compose()
    source = chain["components"]["sources"]["accepted"]
    review = chain["components"]["review"]["accepted"]
    for accepted in (source, review):
        env.notify(accepted)
    env.advance_healthy([source, review])
    assert env.status(source)["body"]["status"] == "refusal_windows_closed"
    request = env.handoff_request(review)
    assert env.handoff_phase(request, "prepare")["body"]["outcome"] == "prepared"

    # The reviewer and requester still have permission. Researcher's expired
    # source-component authority cannot be hidden behind a historical agreement.
    lose_authority(env, "researcher", change, monkeypatch)
    assert env.status(review)["body"]["status"] == "refusal_windows_closed"
    assert env.status(source)["body"]["status"] == "unresolved"
    assert env.handoff_phase(request, "dispatch")["body"]["outcome"] == "blocked"
    assert env.adapter.dispatch_calls == 0


def test_status_read_permission_does_not_substitute_for_participant_authority(env):
    agreement = env.bilateral()
    accepted = agreement["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted)
    old = env.status(accepted)
    assert old["body"]["status"] == "refusal_windows_closed"
    grant = grant_for(env, "requester")
    grant["acts"].remove("authority_commit")

    # The caller can read status, but cannot currently authorize this commitment.
    status = env.status(accepted)
    assert status["body"]["status"] == "unresolved"
    evidence_ref = status["body"]["current_policy_authority_checks"][0][
        "authority_status_ref"
    ]
    observation = env.store.resolve(evidence_ref)["body"]
    checks = {c["agent_id"]: c for c in observation["participant_authority_checks"]}
    denied = env.store.resolve(checks["agent:requester"]["decision_ref"])
    assert denied["body"]["result"]["allow"] is False
    assert denied["body"]["input"]["act"] == "authority_commit"
    assert denied["body"]["input"]["subject_ref"] == content_ref(agreement["candidate"])
    assert checks["agent:researcher"]["state"] == "allowed"
    assert observation["authority_evidence_refs"] == []
    assert env.store.resolve(content_ref(old)) == old

    grant["acts"].append("authority_commit")
    recovered = env.status(accepted)
    assert recovered["body"]["status"] == "refusal_windows_closed"
    assert recovered["body"]["revision"] > status["body"]["revision"]


def test_known_refusal_survives_unavailable_participant_policy(env, monkeypatch):
    accepted = env.bilateral()["accepted"]
    env.require_applied(env.refuse(accepted))
    lose_authority(env, "researcher", "unavailable", monkeypatch)
    assert env.status(accepted)["body"]["status"] == "refused"


@pytest.mark.parametrize("change", ["participant_grant", "capacity_policy"])
def test_participant_decisions_must_share_one_stable_local_boundary(
    env, monkeypatch, change
):
    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted)
    harness = env.harnesses["requester"]
    authorize = harness.authorize
    changed = False

    def change_after_first_participant(actor, act, subject, **kwargs):
        nonlocal changed
        decision = authorize(actor, act, subject, **kwargs)
        if not changed and actor == "agent:requester" and act == "authority_commit":
            changed = True
            if change == "participant_grant":
                grant_for(env, "requester")["revoked"] = True
            else:
                capacity = env.ledger.get(
                    "resource_limits", "research-slots:researcher"
                )
                capacity["limit"] = 0
                env.ledger.put("resource_limits", "research-slots:researcher", capacity)
        return decision

    monkeypatch.setattr(harness, "authorize", change_after_first_participant)
    observed = harness._status_for_composition(accepted)
    assert changed
    assert observed["status"] == "unresolved"
    assert observed["authority_evidence_refs"] == []
    assert {c["state"] for c in observed["participant_authority_checks"]} == {"stale"}
    # Both individual decisions were allowed. They cannot be combined because
    # their recorded local authority boundaries differ.
    decisions = [
        env.store.resolve(c["decision_ref"])["body"]
        for c in observed["participant_authority_checks"]
    ]
    assert all(d["result"]["allow"] for d in decisions)
    assert len({d["input"]["boundary_state_digest"] for d in decisions}) == 2


def test_final_executor_check_cannot_hide_revocation_of_other_participant(
    env, monkeypatch
):
    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted)
    request = env.handoff_request(accepted)
    env.handoff_phase(request, "prepare")
    harness = env.harnesses["requester"]
    authorize = harness.authorize
    changed = False

    def revoke_before_executor_decision(actor, act, subject, **kwargs):
        nonlocal changed
        if act == "dispatch_handoff":
            changed = True
            grant_for(env, "requester")["revoked"] = True
        return authorize(actor, act, subject, **kwargs)

    monkeypatch.setattr(harness, "authorize", revoke_before_executor_decision)
    result = env.handoff_phase(request, "dispatch")
    assert changed
    assert result["body"]["outcome"] == "blocked"
    assert env.adapter.dispatch_calls == 0


def test_later_dependency_checks_cannot_hide_changed_component_authority(
    env, monkeypatch
):
    chain = env.compose()
    source = chain["components"]["sources"]["accepted"]
    review = chain["components"]["review"]["accepted"]
    for accepted in (source, review):
        env.notify(accepted)
    env.advance_healthy([source, review])
    request = env.handoff_request(review)
    env.handoff_phase(request, "prepare")
    harness = env.harnesses["requester"]
    observe = harness._status_for_composition
    changed = False

    def revoke_review_commitment_before_dependency(accepted):
        nonlocal changed
        ref = content_ref(accepted) if "body" in accepted else accepted
        if ref == content_ref(source) and not changed:
            changed = True
            grant_for(env, "reviewer")["acts"].remove("authority_commit")
        return observe(accepted)

    monkeypatch.setattr(
        harness, "_status_for_composition", revoke_review_commitment_before_dependency
    )
    result = env.handoff_phase(request, "dispatch")
    assert changed
    assert "dispatch_handoff" in grant_for(env, "reviewer")["acts"]
    assert result["body"]["outcome"] == "blocked"
    assert env.adapter.dispatch_calls == 0


@pytest.mark.parametrize("change", ["revoked", "expired"])
def test_formation_rechecks_joint_authority_before_consuming_capacity(
    env, monkeypatch, change
):
    draft = env.bilateral(finalize=False)
    candidate = draft["candidate"]
    harness = env.harnesses["requester"]
    authorize = harness.authorize
    requester_grant = grant_for(env, "requester")
    changed = False
    if change == "expired":
        requester_grant["valid_until_ms"] = env.clock.now_ms + 1

    def change_after_requester_decision(actor, act, subject, **kwargs):
        nonlocal changed
        decision = authorize(actor, act, subject, **kwargs)
        if not changed and actor == "agent:requester" and act == "authority_commit":
            changed = True
            if change == "revoked":
                requester_grant["revoked"] = True
            else:
                env.clock.advance(2)
        return decision

    monkeypatch.setattr(harness, "authorize", change_after_requester_decision)
    before = env.ledger.get("resource_used", "research-slots:researcher")
    receipt = env.invoke("researcher", "requester", "finalize_candidate", candidate)
    assert changed
    assert receipt["body"]["outcome"] == "blocked"
    assert env.ledger.get("resource_used", "research-slots:researcher") == before
    assert harness.agreement_for_candidate(content_ref(candidate)) is None

    # The failed attempt did not form or consume anything. A fresh authorized
    # attempt can use the already adopted exact terms without rewriting them.
    requester_grant.pop("revoked", None)
    requester_grant.pop("valid_until_ms", None)
    accepted = env.require_applied(
        env.invoke("researcher", "requester", "finalize_candidate", candidate)
    )
    assert accepted["body"]["candidate_ref"] == content_ref(candidate)
    assert env.ledger.get("resource_used", "research-slots:researcher") == 1


def test_earlier_participant_decision_must_survive_later_evaluations(env, monkeypatch):
    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted)
    grant_for(env, "requester")["valid_until_ms"] = env.clock.now_ms + 1
    evaluate = env.policy.evaluate

    def delayed_provider(request, now_ms):
        result = evaluate(request, now_ms)
        if (
            request["actor"]["agent_id"] == "agent:researcher"
            and request["act"] == "authority_commit"
        ):
            env.clock.advance(2)
        return result

    monkeypatch.setattr(env.policy, "evaluate", delayed_provider)
    observation = env.harnesses["requester"]._status_for_composition(accepted)
    assert observation["status"] == "unresolved"
    assert observation["authority_evidence_refs"] == []
    checks = {c["agent_id"]: c for c in observation["participant_authority_checks"]}
    assert checks["agent:requester"]["state"] == "expired"


@pytest.mark.parametrize("scope", ["own_agreement", "dependency"])
def test_earliest_participant_deadline_bounds_the_native_dispatch_gate(env, scope):
    if scope == "own_agreement":
        accepted = env.bilateral()["accepted"]
        agreements = [accepted]
        expiring_actor = "requester"
    else:
        chain = env.compose()
        accepted = chain["components"]["review"]["accepted"]
        agreements = [c["accepted"] for c in chain["components"].values()]
        expiring_actor = "researcher"
    for agreement in agreements:
        env.notify(agreement)
    env.advance_healthy(agreements)
    request = env.handoff_request(accepted)
    env.handoff_phase(request, "prepare")
    deadline = env.clock.now_ms + 1
    grant_for(env, expiring_actor)["valid_until_ms"] = deadline

    def after_marker(name):
        if name == "after_dispatch_marker":
            env.clock.advance(2)

    env.harnesses["requester"].handoff.failpoint = after_marker
    result = env.handoff_phase(request, "dispatch")
    assert result["body"]["outcome"] == "not_dispatched"
    assert env.adapter.dispatch_calls == 0
    slots = env.ledger.items("handoff_slots")
    assert len(slots) == 1
    assert slots[0][1]["gate"]["valid_until_ms"] == deadline
