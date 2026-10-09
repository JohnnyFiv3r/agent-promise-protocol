"""Durable boundary-proven no-call disposition, with controlled native effects."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Event

import pytest

from agent_promise_protocol.crypto import content_ref
from agent_promise_protocol.fixtures import Environment
from agent_promise_protocol.storage import Ledger
from test_handoff import Crash, World


def replacement_agreement(env, prior):
    """Fresh signed candidate/adoptions with explicit fixture-owner disposition."""
    draft = env.bilateral("replacement", finalize=False)
    candidate = deepcopy(draft["candidate"])
    candidate["id"] = candidate["body"]["candidate_id"] = "candidate:replacement-final"
    candidate["body"]["replacement"] = {
        "accepted_offer_ref": content_ref(prior),
        "disposition_ref": env.document(
            "replacement-disposition",
            {"accepted_offer_ref": content_ref(prior), "owner_authorized": True},
        ),
    }
    candidate = env.sign("requester", candidate)
    env.require_applied(
        env.invoke("requester", "requester", "submit_record", candidate)
    )
    for original in draft["adoptions"]:
        actor = original["issuer_agent_id"].removeprefix("agent:")
        body = deepcopy(original["body"])
        body["candidate_ref"] = content_ref(candidate)
        adoption = env.emit(actor, "terms_adoption", body)
        env.require_applied(env.invoke(actor, "requester", "submit_record", adoption))
    return env.require_applied(
        env.invoke("researcher", "requester", "finalize_candidate", candidate)
    )


def cleared_handoff(env):
    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted)
    request = env.handoff_request(accepted)
    env.handoff_phase(request, "prepare")
    return accepted, request


def test_local_no_call_survives_restart_reconcile_and_allows_authorized_replacement(
    tmp_path,
):
    env = Environment(tmp_path)
    try:
        accepted, request = cleared_handoff(env)

        def expire_after_marker(name):
            if name == "after_dispatch_marker":
                env.clock.advance(1001)

        env.harnesses["requester"].handoff.failpoint = expire_after_marker
        disposition = env.handoff_phase(request, "dispatch")
        assert disposition["body"]["outcome"] == "not_dispatched"
        assert (
            disposition["body"]["reason_code"] == "authority_expired_before_native_call"
        )
        assert disposition["body"]["native_evidence_refs"] == []
        key = disposition["body"]["handoff_key"]
        slot = env.ledger.get("handoff_slots", key)
        assert slot["dispatch_attempt_started"] is True
        assert slot["native_observation"]["outcome"] == "not_dispatched"
        assert slot["native_observation"]["local_disposition_ref"] == content_ref(
            disposition
        )
        assert env.adapter.dispatch_calls == 0

        env.restart()
        for _ in range(2):
            reconciled = env.handoff_phase(request, "reconcile")
            assert reconciled["body"]["outcome"] == "not_dispatched"
            assert reconciled["body"]["native_evidence_refs"] == []
            assert env.handoff_phase(request, "dispatch") == disposition
        assert env.adapter.reconcile_calls == 0
        assert env.adapter.dispatch_calls == 0
        assert env.adapter.operations == {}

        replacement = replacement_agreement(env, accepted)
        next_request = env.handoff_request(replacement)
        prepared = env.handoff_phase(next_request, "prepare")
        assert prepared["body"]["outcome"] == "prepared"
        assert prepared["body"]["handoff_key"] != key
        assert env.adapter.dispatch_calls == 0
        assert env.adapter.operations == {}
    finally:
        env.close()


@pytest.mark.parametrize("failure", ["marker_only_crash", "lost_native_reply"])
def test_uncertain_dispatch_still_blocks_replacement(tmp_path, failure):
    env = Environment(tmp_path)
    try:
        accepted, request = cleared_handoff(env)
        if failure == "marker_only_crash":

            def crash(name):
                if name == "after_dispatch_marker":
                    raise Crash()

            env.harnesses["requester"].handoff.failpoint = crash
            with pytest.raises(Crash):
                env.handoff_phase(request, "dispatch")
            assert env.adapter.dispatch_calls == 0
        else:
            env.adapter.lose_reply = True
            assert (
                env.handoff_phase(request, "dispatch")["body"]["outcome"] == "in_doubt"
            )
            assert env.adapter.dispatch_calls == 1
        env.restart()
        replacement = replacement_agreement(env, accepted)
        next_request = env.handoff_request(replacement)
        blocked = env.invoke("researcher", "requester", "prepare_handoff", next_request)
        assert blocked["body"]["outcome"] == "blocked"
        assert blocked["body"]["reason_code"] == "evidence_unavailable"
        if failure == "marker_only_crash":
            assert (
                env.handoff_phase(request, "reconcile")["body"]["outcome"] == "in_doubt"
            )
            assert env.adapter.dispatch_calls == 0
        else:
            assert env.adapter.dispatch_calls == 1
    finally:
        env.close()


@pytest.mark.parametrize("native_outcome", ["in_doubt", "dispatched", "resolved"])
def test_in_flight_lookup_preserves_local_no_call_or_conflicting_native_evidence(
    tmp_path, native_outcome
):
    world = World(tmp_path)
    independent = Ledger(world.path)
    marked, lookup_started, return_lookup = Event(), Event(), Event()
    try:
        world.handoff.prepare(world.request)
        other = world.make_handoff(independent)
        native_ref = world.save({"id": "observed-native-effect", "test_only": True})
        native_refs = [] if native_outcome == "in_doubt" else [native_ref]

        def pause_after_marker(name):
            if name == "after_dispatch_marker":
                marked.set()
                assert lookup_started.wait(5), "reconcile did not start"
                world.now += 1001

        def slow_lookup(native_key):
            lookup_started.set()
            assert return_lookup.wait(5), "lookup was not released"
            return {"outcome": native_outcome, "native_evidence_refs": native_refs}

        world.handoff.failpoint = pause_after_marker
        world.adapter.reconcile = slow_lookup
        with ThreadPoolExecutor(max_workers=2) as executor:
            dispatch = executor.submit(world.handoff.dispatch, world.request)
            try:
                assert marked.wait(5), "dispatch marker did not commit"
                lookup = executor.submit(other.reconcile, world.request)
                disposition = dispatch.result(timeout=5)
                assert disposition["body"]["outcome"] == "not_dispatched"
            finally:
                return_lookup.set()
            expected = "not_dispatched" if native_outcome == "in_doubt" else "in_doubt"
            assert lookup.result(timeout=5)["body"]["outcome"] == expected
        slot = world.ledger.get("handoff_slots", world.key())
        assert slot["native_observation"]["outcome"] == expected
        assert slot["native_observation"]["native_evidence_refs"] == native_refs
        assert slot["native_observation"]["local_disposition_ref"] == content_ref(
            disposition
        )
        world.restart()
        assert world.handoff.reconcile(world.request)["body"]["outcome"] == expected
        assert world.handoff.dispatch(world.request)["body"]["outcome"] == expected
        # A late, inconclusive or final-absence native report cannot erase the
        # evidenced contradiction. Model results from earlier in-flight lookups.
        for later in (
            {"outcome": "in_doubt", "native_evidence_refs": []},
            {
                "outcome": "not_dispatched", "final_absence": True,
                "native_evidence_refs": [world.contract],
            },
        ):
            with world.ledger.transaction():
                retained = world.ledger.get("handoff_slots", world.key())
                result = world.handoff._observe(retained, "reconcile", later)
            assert result["body"]["outcome"] == expected
            assert result["body"]["native_evidence_refs"] == native_refs
        assert world.handoff.resolve(content_ref(disposition)) == disposition
        assert world.adapter.dispatch_calls == 0
    finally:
        return_lookup.set()
        independent.close()
        world.ledger.close()


@pytest.mark.parametrize("native_outcome", ["dispatched", "resolved"])
def test_native_effect_observed_before_no_call_stays_in_doubt_and_blocks_replacement(
    tmp_path, native_outcome
):
    env = Environment(tmp_path)
    try:
        accepted, request = cleared_handoff(env)
        native_ref = env.document(
            "controlled-native-positive", {"native_fact": "operation exists"}
        )
        env.adapter.reconcile = lambda key: {
            "outcome": native_outcome, "native_evidence_refs": [native_ref]
        }
        observed = []

        def observe_then_expire(name):
            if name == "after_dispatch_marker":
                observed.append(env.handoff_phase(request, "reconcile"))
                env.clock.advance(1001)

        env.harnesses["requester"].handoff.failpoint = observe_then_expire
        conflict = env.handoff_phase(request, "dispatch")
        assert observed[0]["body"]["outcome"] == native_outcome
        assert conflict["body"]["outcome"] == "in_doubt"
        assert conflict["body"]["native_evidence_refs"] == [native_ref]
        key = conflict["body"]["handoff_key"]
        slot = env.ledger.get("handoff_slots", key)
        local_ref = slot["local_no_call_ref"]
        local = env.harnesses["requester"].handoff.resolve(local_ref)
        assert local["body"]["outcome"] == "not_dispatched"
        assert local["body"]["reason_code"] == "authority_expired_before_native_call"
        assert slot["native_observation"]["outcome"] == "in_doubt"
        assert slot["local_no_call_conflicts"] == [
            {"outcome": native_outcome, "native_evidence_refs": [native_ref]}
        ]
        env.restart()
        env.adapter.reconcile = lambda key: {
            "outcome": "in_doubt", "native_evidence_refs": []
        }
        for _ in range(2):
            assert (
                env.handoff_phase(request, "reconcile")["body"]["outcome"] == "in_doubt"
            )
            assert (
                env.handoff_phase(request, "dispatch")["body"]["outcome"] == "in_doubt"
            )
        replacement = replacement_agreement(env, accepted)
        next_request = env.handoff_request(replacement)
        blocked = env.invoke("researcher", "requester", "prepare_handoff", next_request)
        assert blocked["body"]["outcome"] == "blocked"
        assert blocked["body"]["reason_code"] == "evidence_unavailable"
        assert env.adapter.dispatch_calls == 0
    finally:
        env.close()


def test_existing_local_no_call_receipt_recovers_missing_disposition_index(tmp_path):
    world = World(tmp_path)
    try:
        world.handoff.prepare(world.request)

        def expire_after_marker(name):
            if name == "after_dispatch_marker":
                world.now += 1001

        world.handoff.failpoint = expire_after_marker
        disposition = world.handoff.dispatch(world.request)
        # Earlier runtime versions retained the signed local no-call receipt but
        # omitted the disposition field consulted by the replacement guard.
        slot = world.ledger.get("handoff_slots", world.key())
        del slot["native_observation"]
        world.ledger.put("handoff_slots", world.key(), slot)
        world.restart()
        assert (
            world.handoff.reconcile(world.request)["body"]["outcome"]
            == "not_dispatched"
        )
        slot = world.ledger.get("handoff_slots", world.key())
        assert slot["native_observation"]["local_disposition_ref"] == content_ref(
            disposition
        )
        assert world.adapter.dispatch_calls == world.adapter.reconcile_calls == 0
    finally:
        world.ledger.close()
