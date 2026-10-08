"""Regression cases discovered by independent signed-harness review."""

from copy import deepcopy

import pytest

from agent_bazaar.crypto import Signer, content_ref, digest, unsigned_digest
from agent_bazaar.errors import ProtocolError
from agent_bazaar.fixtures import Environment, U
from agent_bazaar.harness import FEATURES, P
from agent_bazaar.records import ref_key


@pytest.fixture
def env(tmp_path):
    environment = Environment(tmp_path)
    yield environment
    environment.close()


def new_candidate(env, source, identifier, **body_changes):
    record = deepcopy(source)
    record["id"] = record["body"]["candidate_id"] = identifier
    record["body"].update(body_changes)
    return env.sign("requester", record)


def resign(env, actor, record):
    """Produce a genuine proof-only variant with an additionally enrolled key."""
    original = env.signers[actor]
    alternate = Signer(original.agent_id, original.principal_id)
    certificate = env.ledger.get("transport_identity", original.agent_id)
    env.registry.register(
        alternate,
        features=FEATURES,
        roles=("principal-control",)
        if actor.endswith("_control")
        else ("agent", "notice"),
        certificate_digests=[certificate],
    )
    env.signers[actor] = alternate
    variant = env.sign(actor, record)
    assert unsigned_digest(variant) == unsigned_digest(record)
    assert content_ref(variant) != content_ref(record)
    env.registry.verify(variant, env.store.resolve, env.clock.now_ms)
    return variant


def test_candidate_cannot_substitute_trusted_zero_resource_constraints(env):
    agreement = env.bilateral(finalize=False)
    free = env.document("zero-resource-selection", {"resources": {}})
    env.domain.selection[ref_key(free)] = {"resources": {}}
    malicious = new_candidate(
        env,
        agreement["candidate"],
        "candidate:free-resource",
        selection_constraints_refs=[free],
    )
    receipt = env.invoke("requester", "requester", "submit_record", malicious)
    assert receipt["body"]["outcome"] in ("blocked", "conflict")
    assert env.harnesses["requester"].store.is_admitted(content_ref(malicious)) is False
    assert env.ledger.items("formations") == []


def test_withdrawn_standalone_promise_cannot_supply_candidate_provenance(env):
    agreement = env.bilateral(finalize=False)
    promise = agreement["candidate"]["body"]["own_promises"][0]
    standalone = env.emit(
        "researcher",
        "promise",
        {
            "publication_contract_ref": content_ref(env.publications["researcher"]),
            "own_promise": promise,
        },
        identifier="promise-record:standalone",
    )
    env.require_applied(
        env.invoke("researcher", "requester", "submit_record", standalone)
    )
    withdrawal = env.emit(
        "researcher",
        "withdrawal_event",
        {
            "target_kind": "promise",
            "target_ref": content_ref(standalone),
            "authority_refs": [env.principal_policies["researcher"]],
            "status_ref": "https://fixture.invalid/withdrawn-standalone",
        },
    )
    env.require_applied(
        env.invoke("researcher", "requester", "submit_record", withdrawal)
    )
    malicious = new_candidate(
        env,
        agreement["candidate"],
        "candidate:withdrawn-source",
        promise_bindings=[
            {
                "promise_id": promise["promise_id"],
                "promiser_agent_id": "agent:researcher",
                "basis": "previously_issued",
                "source_ref": content_ref(standalone),
                "source_promise_id": promise["promise_id"],
            }
        ],
    )
    receipt = env.invoke("requester", "requester", "submit_record", malicious)
    assert receipt["body"]["outcome"] == "blocked"
    assert env.harnesses["requester"].store.is_admitted(content_ref(malicious)) is False


def test_finalization_rechecks_every_adopters_current_policy(env):
    agreement = env.bilateral(finalize=False)
    assert len(agreement["adoptions"]) == 2
    for grant in env.policy.grants:
        if grant["agent_id"] == "agent:researcher":
            grant["revoked"] = True
    receipt = env.invoke(
        "requester", "requester", "finalize_candidate", agreement["candidate"]
    )
    assert receipt["body"]["outcome"] == "blocked"
    assert env.ledger.items("formations") == []
    assert env.ledger.get("resource_used", "research-slots:researcher", 0) == 0


def test_registering_route_name_does_not_interpret_arbitrary_arrangement(env):
    agreement = env.bilateral(finalize=False)
    route_type = U + "uninterpreted-route"
    env.domain.understood_uris.add(route_type)
    offer = deepcopy(agreement["offers"][0])
    offer["id"] = "offer:uninterpreted-route"
    offer["body"]["option_id"] = "option:uninterpreted-route"
    offer["body"]["route_selections"] = [
        {
            "route_id": "route:arbitrary",
            "profile_uri": route_type,
            "selection": {
                "destination": "unapproved-place",
                "authorization": "invented",
            },
            "policy_refs": [env.commercial_ref],
        }
    ]
    signed = env.sign("researcher", offer)
    receipt = env.invoke("researcher", "requester", "submit_record", signed)
    assert receipt["body"]["outcome"] == "blocked"
    assert receipt["body"]["reason_code"] == "unsupported_semantics"
    assert env.harnesses["requester"].store.is_admitted(content_ref(signed)) is False


def test_proof_only_adoption_variant_preserves_original_adoption_and_pins(env):
    agreement = env.bilateral(finalize=False)
    original = agreement["adoptions"][1]
    adoptions_before = env.ledger.items("adoptions")
    pins_before = env.ledger.items("pins")
    variant = resign(env, "researcher", original)
    receipt = env.invoke("researcher", "requester", "submit_record", variant)
    assert receipt["body"]["outcome"] == "applied"
    assert env.ledger.items("adoptions") == adoptions_before
    assert env.ledger.items("pins") == pins_before


def test_proof_only_refusal_variant_does_not_create_a_second_refusal_effect(env):
    accepted = env.bilateral()["accepted"]
    original_receipt = env.refuse(accepted)
    original = env.require_applied(original_receipt)
    first = env.status(accepted)
    assert first["body"]["refusal_event_refs"] == [content_ref(original)]
    variant = resign(env, "researcher_control", original)
    receipt = env.invoke("researcher_control", "requester", "submit_record", variant)
    assert receipt["body"]["outcome"] == "applied"
    current = env.status(accepted)
    assert current["body"]["status"] == "refused"
    assert current["body"]["refusal_event_refs"] == first["body"]["refusal_event_refs"]


def test_control_recovery_rate_limit_preserves_reserved_first_refusal(env):
    accepted = env.bilateral()["accepted"]
    for number in range(32):
        receipt = env.invoke(
            "researcher_control",
            "requester",
            "query_status",
            accepted,
            operation_id=f"control-status:{number}",
        )
        assert receipt["body"]["outcome"] == "applied"
    excess = env.invoke(
        "researcher_control",
        "requester",
        "query_status",
        accepted,
        operation_id="control-status:excess",
    )
    assert excess["body"]["outcome"] == "blocked"
    assert excess["body"]["reason_code"] == "quota_exhausted"
    # The separately reserved first refusal survives this identity's exhausted
    # recovery allowance; proposal traffic has not supplied or spent the right.
    assert env.refuse(accepted)["body"]["outcome"] == "applied"
    assert env.status(accepted)["body"]["status"] == "refused"


def test_slow_refusal_policy_cannot_move_authoritative_admission_past_deadline(env):
    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    env.advance_healthy(accepted, 100)
    ingress_time = env.clock.now_ms
    original_evaluate = env.policy.evaluate
    delayed = False

    def slow_policy(request, now_ms):
        nonlocal delayed
        result = original_evaluate(request, now_ms)
        if (
            not delayed
            and request["actor"]["agent_id"] == "agent:researcher_control"
            and request["subject"].get("kind") == "refusal_event"
        ):
            delayed = True
            env.clock.advance(10)
        return result

    env.policy.evaluate = slow_policy
    assert env.refuse(accepted)["body"]["outcome"] == "applied"
    assert delayed and env.clock.now_ms > ingress_time
    retained = env.ledger.get("recovery.objects", accepted["id"])
    admissions = list(retained["admissions"].values())
    assert len(admissions) == 1
    assert admissions[0]["admitted_lower_ms"] == ingress_time
    assert admissions[0]["admitted_upper_ms"] == ingress_time
    env.advance_healthy(accepted, 0)
    assert env.status(accepted)["body"]["status"] == "refused"


def test_signed_health_cannot_invent_unresolvable_service_or_clock_evidence(env):
    accepted = env.bilateral()["accepted"]
    env.notify(accepted)
    start = env.clock.now_ms
    env.clock.advance(101)
    fake = {"id": "does-not-exist", "digest": digest({"invented": True})}
    for descriptor in accepted["body"]["principal_refusal_windows"]:
        evidence = env.emit_profile(
            "requester",
            P + "#rp1-principal-inbox/health-interval",
            {
                "principal_id": descriptor["principal_id"],
                "accepted_offer_ref": content_ref(accepted),
                "interval_start_ms": start,
                "interval_end_ms": env.clock.now_ms,
                "state": "usable",
                "service_evidence_refs": [fake],
                "monotonic_elapsed_ms": 101,
                "continuity_evidence_ref": fake,
            },
        )
        with pytest.raises(ProtocolError):
            env.harnesses["requester"].health(evidence)
    assert env.status(accepted)["body"]["status"] == "unresolved"


def test_authenticated_offer_fork_survives_restart_and_blocks_original_candidate(env):
    agreement = env.bilateral("offer-fork", finalize=False)
    original = agreement["offers"][0]
    fork = deepcopy(original)
    fork["id"] = "offer:same-option-conflicting-revision"
    fork["body"]["own_promises"][0]["action"]["parameters"]["scope"] = (
        "A different authenticated scope"
    )
    fork = env.sign("researcher", fork)
    assert fork["body"]["option_id"] == original["body"]["option_id"]
    assert fork["body"]["revision"] == original["body"]["revision"]
    receipt = env.invoke("researcher", "requester", "submit_record", fork)
    assert receipt["body"]["outcome"] == "conflict"
    assert receipt["body"]["reason_code"] == "lineage_conflict"
    saved = env.ledger.items("lineage_conflicts")
    assert len(saved) == 1
    assert saved[0][1] == {
        "original_ref": content_ref(original),
        "conflicting_ref": content_ref(fork),
    }
    env.restart()
    assert env.ledger.items("lineage_conflicts") == saved
    finalization = env.invoke(
        "requester", "requester", "finalize_candidate", agreement["candidate"]
    )
    assert finalization["body"]["outcome"] == "conflict"
    assert finalization["body"]["reason_code"] == "lineage_conflict"
    assert env.ledger.items("formations") == []
    assert env.ledger.get("resource_used", "research-slots:researcher", 0) == 0


def test_same_envelope_plan_fork_fences_original_plan_across_restart(env):
    intent = env.intent("same-id-plan-fork")
    plan = env.emit(
        "requester",
        "transaction_plan",
        {
            "transaction_id": "transaction:same-id-plan-fork",
            "revision": 1,
            "previous_digest": None,
            "orchestrator_agent_id": "agent:requester",
            "origin_ref": content_ref(intent),
            "components": [
                {
                    "component_id": "sources",
                    "required_agents": [
                        {
                            "agent_id": "agent:requester",
                            "principal_id": "principal:requester",
                        },
                        {
                            "agent_id": "agent:researcher",
                            "principal_id": "principal:researcher",
                        },
                    ],
                    "role": "contribution",
                    "requirement": {
                        "type_uri": U + "component",
                        "parameters": {"report_id": "plan-component"},
                    },
                }
            ],
            "dependencies": [],
            "privacy_policy_ref": env.privacy_ref,
            "validity": env.validity("requester"),
        },
        identifier="plan:same-envelope-identity",
    )
    env.require_applied(env.invoke("requester", "requester", "submit_record", plan))
    agreement = env.bilateral(
        "plan-component",
        composition={"plan_ref": content_ref(plan), "component_id": "sources"},
        origin=intent,
        finalize=False,
    )
    fork = deepcopy(plan)
    fork["body"]["components"][0]["requirement"]["parameters"]["report_id"] = (
        "changed-plan-requirement"
    )
    fork = env.sign("requester", fork)
    assert fork["id"] == plan["id"]
    assert fork["body"]["revision"] == plan["body"]["revision"]
    receipt = env.invoke("requester", "requester", "submit_record", fork)
    assert receipt["body"]["outcome"] in ("blocked", "conflict")
    retained = env.ledger.items("composition_revisions")
    assert len(retained) == 1
    assert retained[0][1]["conflicted"] is True
    assert content_ref(fork) in retained[0][1]["conflict_refs"]
    env.restart()
    assert env.ledger.items("composition_revisions") == retained
    with pytest.raises(ProtocolError, match="composition_fork"):
        env.harnesses["requester"].composition.validate_candidate(
            agreement["candidate"]
        )
    finalization = env.invoke(
        "requester", "requester", "finalize_candidate", agreement["candidate"]
    )
    assert finalization["body"]["outcome"] in ("blocked", "conflict")
    assert env.ledger.items("formations") == []
