"""Live-option allowance belongs to the addressed recipient and selected pool.

These recipients share one trusted authority database; the checks exercise
accounting isolation, not a multi-tenant storage access-control boundary.
"""

from copy import deepcopy

import pytest

from agent_bazaar.crypto import content_ref
from agent_bazaar.fixtures import Environment, U


@pytest.fixture
def env(tmp_path):
    environment = Environment(tmp_path)
    yield environment
    environment.close()


def configure_pools(env, recipient, limits):
    enrollment = env.enrollments["agent:" + recipient]
    policy = deepcopy(env.store.resolve(enrollment.admission_policy_ref))
    policy["id"] += ":scoped"
    negotiation = next(
        p for p in policy["pools"] if p["traffic_class"] == "negotiation"
    )
    policy["pools"] = [
        p for p in policy["pools"] if p["traffic_class"] != "negotiation"
    ]
    for allowance, limit in limits.items():
        pool = deepcopy(negotiation)
        pool.update(allowance_id=allowance, max_live_options=limit)
        policy["pools"].append(pool)
    policy = env.sign(recipient, policy)
    enrollment.admission_policy_ref = content_ref(policy)
    previous = env.publications[recipient]
    body = deepcopy(previous["body"])
    body.update(revision=2, previous_digest=content_ref(previous)["digest"])
    body["contact"]["admission_policy_ref"] = content_ref(policy)
    publication = env.emit(recipient, "publication_contract", body)
    # Administrative fixture enrollment updates policy and its publication together.
    env.harnesses[recipient].submit(publication)
    env.publications[recipient] = publication


def offer(env, name, *, actor="researcher", recipient="requester"):
    identifier = "offer:scope:" + name
    return env.emit(
        actor,
        "offer",
        {
            "semantics": "issued_qualified_promises",
            "origin": {
                "self_origin": True,
                "record_kind": "offer",
                "record_id": identifier,
                "originator_agent_id": "agent:" + actor,
                "originator_principal_id": "principal:" + actor,
                "coordinator_agent_id": "agent:" + actor,
            },
            "negotiation_id": "negotiation:" + name,
            "option_id": "option:" + name,
            "revision": 1,
            "previous_option_digest": None,
            "publication_contract_refs": [
                content_ref(env.publications[a]) for a in (actor, recipient)
            ],
            "selection_constraints_ref": env.selections[actor],
            "validity": env.validity(actor),
            "own_promises": [env.promise(actor, recipient, name, "produce_report")],
            "requested_counterpromises": [],
            "agreement_terms": {
                "profile_uri": U + "no-consideration",
                "terms": {"consideration": "none", "report_id": name},
                "policy_refs": [env.principal_policies[a] for a in (actor, recipient)],
            },
            "route_selections": [],
            "privacy_policy_ref": env.privacy_ref,
        },
        identifier=identifier,
    )


def revise(env, original):
    changed = deepcopy(original)
    changed["id"] += ":revised"
    body = changed["body"]
    body.update(revision=2, previous_option_digest=content_ref(original)["digest"])
    body["origin"] = {
        "record_kind": "offer",
        "record_ref": content_ref(original),
        "originator_agent_id": original["issuer_agent_id"],
        "originator_principal_id": original["issuer_principal_id"],
        "coordinator_agent_id": original["issuer_agent_id"],
    }
    body["own_promises"][0]["action"]["parameters"]["scope"] = "Revised report scope"
    return env.sign(original["issuer_agent_id"].removeprefix("agent:"), changed)


def grant(env, recipient, actor, allowance):
    record = env.emit(
        recipient,
        "admission_grant",
        {
            "recipient_agent_id": "agent:" + recipient,
            "grantee_agent_id": "agent:" + actor,
            "grantee_principal_id": "principal:" + actor,
            "recipient_scope_id": env.scope(recipient),
            "publication_contract_ref": content_ref(env.publications[recipient]),
            "admission_policy_ref": env.enrollments[
                "agent:" + recipient
            ].admission_policy_ref,
            "allowance_ids": [allowance],
            "allowed_record_kinds": ["offer"],
            "validity": env.validity(recipient),
            "operation_purposes": ["submit_record"],
        },
    )
    env.require_applied(env.invoke(recipient, recipient, "submit_record", record))
    return record


def submit_with_grant(env, subject, permission):
    actor = subject["issuer_agent_id"].removeprefix("agent:")
    recipient = permission["body"]["recipient_agent_id"].removeprefix("agent:")
    request = env.make_request(actor, recipient, "submit_record", subject)
    request["body"]["admission_basis_ref"] = content_ref(permission)
    return env.deliver(env.sign(actor, request))


def test_unrelated_recipient_offers_do_not_consume_live_option_capacity(env):
    # Deliberately reuse the allowance name: the recipient scope still isolates it.
    for recipient in ("requester", "reviewer"):
        configure_pools(env, recipient, {"shared-name": 1})
        record = offer(env, recipient, recipient=recipient)
        env.require_applied(
            env.invoke("researcher", recipient, "submit_record", record)
        )
    extra = offer(env, "requester-extra")
    blocked = env.invoke("researcher", "requester", "submit_record", extra)
    assert blocked["body"]["reason_code"] == "quota_exhausted"
    assert len(env.ledger.items("admitted_options")) == 2


def test_allowance_pools_are_independent_and_revision_cannot_move_pools(env):
    configure_pools(env, "requester", {"pool-a": 1, "pool-b": 1})
    a = grant(env, "requester", "researcher", "pool-a")
    b = grant(env, "requester", "researcher", "pool-b")
    first = offer(env, "first")
    env.require_applied(submit_with_grant(env, first, a))
    env.require_applied(submit_with_grant(env, offer(env, "second"), b))
    changed = revise(env, first)
    blocked = submit_with_grant(env, changed, b)
    assert blocked["body"]["reason_code"] == "quota_exhausted"
    assert not env.store.is_admitted(content_ref(changed))
    env.require_applied(submit_with_grant(env, changed, a))
    assert len(env.ledger.items("admitted_options")) == 2


def test_invalid_offer_does_not_occupy_live_slot(env):
    configure_pools(env, "requester", {"bounded": 1})
    invalid = offer(env, "invalid")
    invalid["body"]["own_promises"][0]["authority_refs"] = [
        env.principal_policies["reviewer"]
    ]
    invalid = env.sign("researcher", invalid)
    blocked = env.invoke("researcher", "requester", "submit_record", invalid)
    assert blocked["body"]["reason_code"] == "authority_absent"
    assert env.ledger.items("admitted_options") == []
    assert not env.store.is_admitted(content_ref(invalid))
    env.require_applied(
        env.invoke("researcher", "requester", "submit_record", offer(env, "valid"))
    )
    quota = env.ledger.get("quota", env.scope("requester") + ":bounded")
    assert quota["messages"] == 2  # Incurred admission work is still accounted for.


def test_revisions_proof_variants_replays_and_other_senders_share_one_pool(env):
    configure_pools(env, "requester", {"bounded": 1})
    first = offer(env, "one")
    receipt = env.invoke("researcher", "requester", "submit_record", first)
    env.require_applied(receipt)
    request = env.last_request
    quota_before = env.ledger.items("quota")
    assert env.deliver(request) == receipt
    assert env.ledger.items("quota") == quota_before
    variant = deepcopy(first)
    proof = deepcopy(env.store.resolve(variant["proofs"][0]["native_proof_ref"]))
    proof["id"] += ":alternate-wrapper"
    env.save(proof)
    variant["proofs"][0]["native_proof_ref"] = content_ref(proof)
    env.save(variant)
    env.require_applied(env.invoke("researcher", "requester", "submit_record", variant))
    env.require_applied(
        env.invoke("researcher", "requester", "submit_record", revise(env, first))
    )
    assert len(env.ledger.items("admitted_options")) == 1
    # A different authenticated sender and option name do not replenish this pool.
    other = offer(env, "other", actor="reviewer")
    blocked = env.invoke("reviewer", "requester", "submit_record", other)
    assert blocked["body"]["reason_code"] == "quota_exhausted"
    env.restart()
    assert env.deliver(request) == receipt
    assert len(env.ledger.items("admitted_options")) == 1


def test_pending_operations_recheck_live_capacity_at_application(env):
    class Crash(BaseException):
        pass

    configure_pools(env, "requester", {"bounded": 1})

    def fail(name):
        if name == "after_operation_admission":
            raise Crash()

    env.harnesses["requester"].failpoint = fail
    first, second = offer(env, "pending-one"), offer(env, "pending-two")
    requests = []
    for record in (first, second):
        with pytest.raises(Crash):
            env.invoke("researcher", "requester", "submit_record", record)
        requests.append(env.last_request)
    assert env.ledger.items("admitted_options") == []
    env.restart()
    env.require_applied(env.deliver(requests[0]))
    blocked = env.deliver(requests[1])
    assert blocked["body"]["reason_code"] == "quota_exhausted"
    assert not env.store.is_admitted(content_ref(second))
    assert len(env.ledger.items("admitted_options")) == 1
    assert env.deliver(requests[1]) == blocked


def test_withdrawal_releases_only_the_applied_option_slot(env):
    configure_pools(env, "requester", {"bounded": 1})
    first = offer(env, "withdrawn")
    env.require_applied(env.invoke("researcher", "requester", "submit_record", first))
    withdrawal = env.emit(
        "researcher",
        "withdrawal_event",
        {
            "target_ref": content_ref(first),
            "target_kind": "offer",
            "authority_refs": [env.principal_policies["researcher"]],
            "status_ref": "https://fixture.invalid/withdrawal/withdrawn",
            "reason": "Owner withdrew this unselected option",
        },
    )
    env.require_applied(
        env.invoke("researcher", "requester", "submit_record", withdrawal)
    )
    env.require_applied(
        env.invoke(
            "researcher", "requester", "submit_record", offer(env, "replacement")
        )
    )
    assert (
        len(env.ledger.items("admitted_options")) == 2
    )  # Retained membership tombstones.


def test_legacy_applied_offer_without_membership_does_not_create_fresh_allowance(env):
    configure_pools(env, "requester", {"bounded": 1})
    first = offer(env, "legacy")
    receipt = env.invoke("researcher", "requester", "submit_record", first)
    env.require_applied(receipt)
    original_request = env.last_request
    # Old runtime ledgers retained outcomes but had no scoped option index.
    for key, _ in env.ledger.items("admitted_options"):
        env.ledger.delete("admitted_options", key)
    env.restart()
    extra = offer(env, "not-extra-allowance")
    blocked = env.invoke("researcher", "requester", "submit_record", extra)
    assert blocked["body"]["reason_code"] == "internal_unresolved"
    assert not env.store.is_admitted(content_ref(extra))
    assert env.ledger.items("admitted_options") == []
    # Existing outcome recovery does not become a fresh admission or lose history.
    assert env.deliver(original_request) == receipt


def test_legacy_pending_offer_without_saved_limit_blocks_safely_after_restart(env):
    class Crash(BaseException):
        pass

    configure_pools(env, "requester", {"bounded": 1})

    def fail(name):
        if name == "after_operation_admission":
            raise Crash()

    env.harnesses["requester"].failpoint = fail
    pending_offer = offer(env, "legacy-pending")
    with pytest.raises(Crash):
        env.invoke("researcher", "requester", "submit_record", pending_offer)
    request = env.last_request
    for key, saved in env.ledger.items("operations"):
        if saved["request_ref"] == content_ref(request):
            assert not saved["terminal"]
            saved["admission"].pop("max_live_options")
            env.ledger.put("operations", key, saved)
            break
    else:
        pytest.fail("expected retained pending offer operation")
    env.restart()
    blocked = env.deliver(request)
    assert blocked["body"]["outcome"] == "blocked"
    assert blocked["body"]["reason_code"] == "internal_unresolved"
    assert not env.store.is_admitted(content_ref(pending_offer))
    assert env.ledger.items("admitted_options") == []
    assert env.deliver(request) == blocked
