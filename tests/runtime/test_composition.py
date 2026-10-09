"""C7 authority and dependency tests use already-authenticated internal records."""

from copy import deepcopy

import pytest

from agent_promise_protocol.composition import Composition
from agent_promise_protocol.crypto import content_ref, digest
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.storage import Ledger


def record(kind, record_id, body, issuer="orchestrator"):
    return {
        "id": record_id,
        "kind": kind,
        "issuer_agent_id": issuer,
        "body": body,
        "proofs": [{"test_proof": "one"}],
    }


PARTICIPANTS = [
    {"agent_id": "alice", "principal_id": "alice-owner"},
    {"agent_id": "bob", "principal_id": "bob-owner"},
]


def plan_record(*, revision=1, previous=None, dependencies=None):
    return record(
        "transaction_plan",
        "plan:" + str(revision),
        {
            "transaction_id": "transaction:one",
            "revision": revision,
            "previous_digest": previous,
            "orchestrator_agent_id": "orchestrator",
            "origin_ref": {"id": "origin", "digest": digest("origin")},
            "components": [
                {
                    "component_id": name,
                    "required_agents": deepcopy(PARTICIPANTS),
                    "role": "contribution",
                    "requirement": {
                        "type_uri": "urn:test:purpose",
                        "parameters": {"purpose": name},
                    },
                }
                for name in ("a", "b", "c")
            ],
            "dependencies": dependencies or [],
            "validity": {"mode": "until_withdrawn"},
        },
    )


def dependency(
    subject="a", source="b", stage="formation", condition="agent_agreement", **extra
):
    return {
        "dependency_id": subject + ":" + source + ":" + stage,
        "subject_component_id": subject,
        "stage": stage,
        "requires": [{"component_id": source, "condition": condition, **extra}],
        "on_unavailable": "hold",
        "on_refused": "block",
        "on_failed": "block",
    }


class World:
    def __init__(self, tmp_path):
        self.ledger = Ledger(tmp_path / "composition.sqlite")
        self.records = {}
        self.valid = True
        self.composition = Composition(
            self.ledger,
            self.resolve,
            now_ms=lambda: 1000,
            validity_check=lambda p, now: self.valid,
            requirement_check=self.requirement,
        )

    @staticmethod
    def requirement(requirement, candidate, plan):
        return (
            requirement["type_uri"] == "urn:test:purpose"
            and candidate["body"].get("purpose") == requirement["parameters"]["purpose"]
        )

    def save(self, rec):
        self.records[content_ref(rec)["digest"]] = deepcopy(rec)
        return content_ref(rec)

    def resolve(self, ref):
        return deepcopy(self.records.get(ref["digest"]))

    def submit(self, plan):
        self.save(plan)
        return self.composition.submit_plan(plan)

    def candidate(self, plan, component="a", suffix=""):
        candidate = record(
            "candidate_terms",
            "candidate:" + component + suffix,
            {
                "participants": deepcopy(PARTICIPANTS),
                "purpose": component,
                "composition": {
                    "plan_ref": content_ref(plan),
                    "component_id": component,
                },
            },
        )
        self.save(candidate)
        return candidate

    def bind(self, plan, candidate):
        binding = record(
            "composition_binding",
            "binding:" + candidate["id"],
            {
                "plan_ref": content_ref(plan),
                "component_id": candidate["body"]["composition"]["component_id"],
                "candidate_ref": content_ref(candidate),
            },
        )
        self.save(binding)
        return self.composition.bind(binding)


def test_bilateral_needs_no_composition_and_callback_knowledge_is_required(tmp_path):
    world = World(tmp_path)
    plain = record("candidate_terms", "bilateral", {})
    assert world.composition.validate_candidate(plain) is None
    assert world.composition.check(plain, "formation", None, None, None) is True
    plan = plan_record()
    world.submit(plan)
    candidate = world.candidate(plan)
    world.composition.requirement_check = None
    with pytest.raises(ProtocolError, match="unsupported_semantics"):
        world.bind(plan, candidate)
    assert world.ledger.items("composition_slots") == []


def test_full_plan_dag_checks_all_components_and_both_stages(tmp_path):
    world = World(tmp_path)
    plan = plan_record(
        dependencies=[dependency("b", "c"), dependency("c", "b", "handoff")]
    )
    with pytest.raises(ProtocolError, match="composition_cycle"):
        world.submit(plan)
    assert world.ledger.items("composition_revisions") == []
    invalid = plan_record(dependencies=[dependency("a", "missing")])
    with pytest.raises(ProtocolError, match="composition_invalid"):
        world.submit(invalid)


def test_plan_authority_lineage_and_fork_survive_restart(tmp_path):
    world = World(tmp_path)
    plan = plan_record()
    invalid = deepcopy(plan)
    invalid["issuer_agent_id"] = "alice"
    with pytest.raises(ProtocolError, match="authority_denied"):
        world.submit(invalid)
    with pytest.raises(ProtocolError, match="composition_lineage"):
        world.submit(plan_record(revision=2, previous=digest("missing")))
    world.submit(plan)
    successor = plan_record(revision=2, previous=content_ref(plan)["digest"])
    world.submit(successor)
    candidate = world.candidate(successor)
    world.bind(successor, candidate)
    fork = deepcopy(plan)
    fork["id"] = "different-envelope-id"
    with pytest.raises(ProtocolError, match="composition_fork"):
        world.submit(fork)
    world.ledger.close()
    world.ledger = Ledger(tmp_path / "composition.sqlite")
    world.composition.ledger = world.ledger
    with pytest.raises(ProtocolError, match="composition_fork"):
        world.composition.validate_candidate(candidate)


def test_proof_variants_share_semantic_slot_but_cannot_replace_pinned_refs(tmp_path):
    world = World(tmp_path)
    plan = plan_record()
    world.submit(plan)
    candidate = world.candidate(plan)
    original = world.bind(plan, candidate)
    proof_variant = deepcopy(plan)
    proof_variant["proofs"] = [{"test_proof": "two"}]
    world.submit(proof_variant)
    assert len(world.ledger.items("composition_revisions")) == 1
    alternate = world.candidate(proof_variant, suffix="variant")
    with pytest.raises(ProtocolError, match="composition_conflict"):
        world.bind(proof_variant, alternate)
    slots = world.ledger.items("composition_slots")
    assert len(slots) == 1
    assert slots[0][1]["candidate_ref"] == original["candidate_ref"]
    assert slots[0][1]["plan_ref"] == content_ref(plan)
    assert slots[0][1]["conflicted"] is True


def test_binding_checks_exact_candidate_principals_and_typed_requirement(tmp_path):
    world = World(tmp_path)
    plan = plan_record()
    world.submit(plan)
    wrong_principal = world.candidate(plan)
    wrong_principal["body"]["participants"][0]["principal_id"] = "other-principal"
    world.save(wrong_principal)
    with pytest.raises(ProtocolError, match="composition_mismatch"):
        world.bind(plan, wrong_principal)
    wrong_requirement = world.candidate(plan)
    wrong_requirement["body"]["purpose"] = "not-the-required-work"
    world.save(wrong_requirement)
    with pytest.raises(ProtocolError, match="unsupported_semantics"):
        world.bind(plan, wrong_requirement)
    assert world.ledger.items("composition_slots") == []
    candidate = world.candidate(plan)
    world.bind(plan, candidate)
    variant = deepcopy(candidate)
    variant["proofs"] = [{"test_proof": "resigned"}]
    with pytest.raises(ProtocolError, match="composition_mismatch"):
        world.composition.validate_candidate(variant)


def test_stages_current_refusal_and_exact_accepted_source(tmp_path):
    world = World(tmp_path)
    plan = plan_record(
        dependencies=[dependency(stage="handoff", condition="principal_clearance")]
    )
    world.submit(plan)
    subject, source = world.candidate(plan), world.candidate(plan, "b")
    world.bind(plan, subject)
    world.bind(plan, source)
    accepted = record(
        "accepted_offer", "accepted:b", {"candidate_ref": content_ref(source)}
    )
    status = {"status": "pending_refusal_windows"}
    agreements = lambda ref: accepted
    statuses = lambda ref: status
    assert (
        world.composition.check(subject, "formation", agreements, statuses, None)
        is True
    )
    with pytest.raises(ProtocolError, match="dependency_unmet"):
        world.composition.check(subject, "handoff", agreements, statuses, None)
    status["status"] = "refusal_windows_closed"
    assert (
        world.composition.check(subject, "handoff", agreements, statuses, None) is True
    )
    status["status"] = "refused"
    with pytest.raises(ProtocolError, match="dependency_refused"):
        world.composition.check(subject, "handoff", agreements, statuses, None)
    status["status"] = "refusal_windows_closed"
    accepted["body"]["candidate_ref"] = {
        "id": "different-candidate",
        "digest": digest("different"),
    }
    with pytest.raises(ProtocolError, match="dependency_mismatch"):
        world.composition.check(subject, "handoff", agreements, statuses, None)


@pytest.mark.parametrize(
    "observation",
    [None, {"status": "unknown"}, {"status": "unresolved"}, {"status": "stale"}],
)
def test_historical_agreement_never_overrides_current_unknown(tmp_path, observation):
    world = World(tmp_path)
    plan = plan_record(dependencies=[dependency()])
    world.submit(plan)
    subject, source = world.candidate(plan), world.candidate(plan, "b")
    world.bind(plan, subject)
    world.bind(plan, source)
    accepted = record(
        "accepted_offer", "accepted:b", {"candidate_ref": content_ref(source)}
    )
    with pytest.raises(ProtocolError, match="dependency_unavailable"):
        world.composition.check(
            subject, "formation", lambda r: accepted, lambda r: observation, None
        )


def test_evidence_requires_full_predicate_provenance_and_retains_stage(tmp_path):
    world = World(tmp_path)
    policy_ref = {"id": "evidence-policy", "digest": digest("policy")}
    plan = plan_record(
        dependencies=[
            dependency(
                condition="evidence",
                evidence_type_uri="urn:test:evidence",
                evidence_requirement_ref=policy_ref,
            )
        ]
    )
    world.submit(plan)
    subject, source = world.candidate(plan), world.candidate(plan, "b")
    world.bind(plan, subject)
    world.bind(plan, source)
    accepted = record(
        "accepted_offer", "accepted:b", {"candidate_ref": content_ref(source)}
    )
    agreements, statuses = (
        lambda r: accepted,
        lambda r: {"status": "refusal_windows_closed"},
    )
    for observation in (True, {"state": "established"}, {"state": "unknown"}):
        with pytest.raises(ProtocolError, match="dependency_unavailable"):
            world.composition.check(
                subject, "formation", agreements, statuses, lambda *args: observation
            )
    with pytest.raises(ProtocolError, match="dependency_failed"):
        world.composition.check(
            subject,
            "formation",
            agreements,
            statuses,
            lambda *args: {"state": "failed"},
        )
    calls = []

    def evidence(requirement, candidate, agreement, stage):
        calls.append((candidate["id"], agreement["id"], stage))
        return {
            "state": "established",
            "evidence_refs": [policy_ref],
            "evaluator": "authorized-assessor",
            "policy_ref": policy_ref,
        }

    assert (
        world.composition.check(subject, "formation", agreements, statuses, evidence)
        is True
    )
    assert calls == [(source["id"], accepted["id"], "formation")]
    retained = world.ledger.items("composition_observations")[-1][1][0]
    assert retained["agreement_ref"] == content_ref(accepted)
    assert retained["evidence"]["evaluator"] == "authorized-assessor"


def test_current_plan_validity_is_required_at_every_transition(tmp_path):
    world = World(tmp_path)
    plan = plan_record()
    world.submit(plan)
    candidate = world.candidate(plan)
    world.bind(plan, candidate)
    world.valid = False
    with pytest.raises(ProtocolError, match="composition_unavailable"):
        world.composition.validate_candidate(candidate)


def test_candidate_can_be_admitted_before_binding_but_transition_cannot(tmp_path):
    world = World(tmp_path)
    plan = plan_record()
    world.submit(plan)
    candidate = world.candidate(plan)
    assert (
        world.composition.validate_candidate(candidate, require_binding=False)[
            "binding"
        ]
        is None
    )
    with pytest.raises(ProtocolError, match="composition_unbound"):
        world.composition.check(candidate, "formation", None, None, None)
    world.bind(plan, candidate)
    assert world.composition.validate_candidate(candidate)["binding"] is not None
    assert world.composition.check(candidate, "formation", None, None, None) is True


def test_dependency_clearance_closure_is_transitive_and_stage_specific(tmp_path):
    world = World(tmp_path)
    plan = plan_record(
        dependencies=[dependency("a", "b", "handoff"), dependency("b", "c", "handoff")]
    )
    world.submit(plan)
    candidates = {
        component: world.candidate(plan, component) for component in ("a", "b", "c")
    }
    for candidate in candidates.values():
        world.bind(plan, candidate)
    accepted = {
        content_ref(c)["digest"]: record(
            "accepted_offer", "accepted:" + component, {"candidate_ref": content_ref(c)}
        )
        for component, c in candidates.items()
    }
    agreements = lambda ref: accepted.get(ref["digest"])
    assert (
        world.composition.dependency_agreements(
            candidates["a"], "formation", agreements
        )
        == []
    )
    closure = world.composition.dependency_agreements(
        candidates["a"], "handoff", agreements
    )
    assert [value["id"] for value in closure] == ["accepted:b", "accepted:c"]
    assert (
        world.composition.dependency_agreements(candidates["c"], "handoff", agreements)
        == []
    )
    del accepted[content_ref(candidates["c"])["digest"]]
    with pytest.raises(ProtocolError, match="dependency_unavailable"):
        world.composition.dependency_agreements(candidates["a"], "handoff", agreements)


def test_explicit_conflict_can_survive_harness_semantic_savepoint_rollback(tmp_path):
    world = World(tmp_path)
    plan = plan_record()
    world.submit(plan)
    fork = deepcopy(plan)
    fork["id"] = "fork-with-another-envelope"
    with world.ledger.transaction():
        try:
            with world.ledger.transaction():
                world.submit(fork)
        except ProtocolError as error:
            assert world.composition.preserve_conflict(error) is True
        world.ledger.put("test_receipt", "fork", {"outcome": "conflict"})
    world.ledger.close()
    world.ledger = Ledger(tmp_path / "composition.sqlite")
    world.composition.ledger = world.ledger
    candidate = world.candidate(plan)
    with pytest.raises(ProtocolError, match="composition_fork"):
        world.composition.validate_candidate(candidate, require_binding=False)
