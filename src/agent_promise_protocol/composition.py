"""Optional C7 composition over authenticated records and one authority ledger.

Authentication/admission precedes this internal API. Predicate callbacks are explicit
realm configuration, not statements supplied by an incoming plan or its orchestrator.
They must establish current evidence; no universal business vocabulary is inferred.
"""

from __future__ import annotations

from copy import deepcopy
import time

from .crypto import content_ref, digest, unsigned_digest
from .errors import ProtocolError
from .guards import milliseconds


def same_ref(left, right):
    return (
        isinstance(left, dict)
        and isinstance(right, dict)
        and all(
            left.get(k) is not None and left.get(k) == right.get(k)
            for k in ("id", "digest")
        )
    )


class Composition:
    """Durable plan lineages, semantic slots, and stage-specific conjunctions.

    ``requirement_check(requirement, candidate, plan)`` and
    ``validity_check(plan, now_ms)`` must return exactly True. The latter checks the
    current policy/withdrawal state in addition to the local expiration check.
    ``evidence_check(requirement, candidate, accepted_or_none, stage)`` returns an
    observation with state, evidence_refs, evaluator, policy_ref. Only ``established``
    is positive. Callbacks receive verified exact records, never mutable summaries.
    """

    def __init__(
        self,
        ledger,
        resolve,
        *,
        requirement_check=None,
        validity_check=None,
        now_ms=None,
    ):
        self.ledger = ledger
        self.resolve_external = resolve
        self.requirement_check = requirement_check
        self.validity_check = validity_check
        self.now_ms = now_ms or (lambda: int(time.time() * 1000))

    @staticmethod
    def _conflict_error(code, detail, entries):
        error = ProtocolError(code, detail)
        # The harness may roll back an enclosing semantic savepoint. Carry only
        # this admitted conflict's exact facts out of that rollback, so its outer
        # C3 receipt boundary can preserve the conflict without other partial work.
        error.composition_conflict_entries = deepcopy(entries)
        return error

    def preserve_conflict(self, error):
        """Retain a raised C7 conflict after a caller rolled back its savepoint.

        Call inside the outer admission/receipt transaction's exception handler.
        This is an internal harness hook: errors come from the authenticated call,
        never from a wire object. It does not turn a conflict into an admitted act.
        """
        entries = getattr(error, "composition_conflict_entries", None)
        if (
            error.code not in {"composition_fork", "composition_conflict"}
            or not entries
        ):
            return False
        with self.ledger.transaction():
            for namespace, key, value in entries:
                self.ledger.put(namespace, key, value)
        return True

    def _resolve(self, ref):
        record = self.ledger.get("composition_records", ref["digest"])
        if record is None:
            record = self.resolve_external(ref)
        if record is None or not same_ref(content_ref(record), ref):
            raise ProtocolError(
                "dependency_unavailable", "exact content reference unavailable"
            )
        return record

    @staticmethod
    def _lineage(plan):
        return digest([plan["issuer_agent_id"], plan["body"]["transaction_id"]])

    @staticmethod
    def _slot(plan, component_id):
        return digest(
            [plan["issuer_agent_id"], plan["id"], unsigned_digest(plan), component_id]
        )

    @staticmethod
    def _components(plan):
        result = {}
        for component in plan["body"]["components"]:
            component_id = component["component_id"]
            if component_id in result:
                raise ProtocolError(
                    "composition_invalid", "duplicate component identity"
                )
            participants = component["required_agents"]
            if (
                len(participants) != 2
                or len({p["agent_id"] for p in participants}) != 2
            ):
                raise ProtocolError(
                    "composition_invalid", "component must have two distinct agents"
                )
            if not all(p.get("principal_id") for p in participants):
                raise ProtocolError(
                    "composition_invalid", "component principal missing"
                )
            requirement = component.get("requirement", {})
            if not requirement.get("type_uri") or not isinstance(
                requirement.get("parameters"), dict
            ):
                raise ProtocolError(
                    "composition_invalid", "typed component requirement required"
                )
            result[component_id] = component
        if not result:
            raise ProtocolError("composition_invalid", "empty plan")
        return result

    def _validate_graph(self, plan):
        components = self._components(plan)
        # RP1 deliberately selects a component DAG across every declared stage.
        # Checking only the currently requested stage could admit a hidden cycle.
        edges = {component_id: set() for component_id in components}
        ids = set()
        for dependency in plan["body"]["dependencies"]:
            if dependency["dependency_id"] in ids:
                raise ProtocolError(
                    "composition_invalid", "duplicate dependency identity"
                )
            ids.add(dependency["dependency_id"])
            subject = dependency["subject_component_id"]
            if subject not in components or dependency["stage"] not in {
                "formation",
                "handoff",
            }:
                raise ProtocolError(
                    "composition_invalid", "unknown dependency subject or stage"
                )
            if (
                dependency.get("on_unavailable") != "hold"
                or dependency.get("on_refused") != "block"
                or dependency.get("on_failed") not in {"hold", "block"}
            ):
                raise ProtocolError(
                    "composition_invalid", "unsupported dependency disposition"
                )
            if not dependency["requires"]:
                raise ProtocolError("composition_invalid", "empty dependency")
            for requirement in dependency["requires"]:
                source = requirement["component_id"]
                if source not in components:
                    raise ProtocolError(
                        "composition_invalid", "dependency outside exact plan"
                    )
                condition = requirement["condition"]
                if condition not in {
                    "agent_agreement",
                    "principal_clearance",
                    "evidence",
                }:
                    raise ProtocolError(
                        "unsupported_semantics", "unknown dependency condition"
                    )
                if condition == "evidence" and not (
                    requirement.get("evidence_type_uri")
                    and requirement.get("evidence_requirement_ref")
                ):
                    raise ProtocolError(
                        "composition_invalid",
                        "evidence predicate lacks immutable semantics",
                    )
                edges[subject].add(source)
        visiting, visited = set(), set()

        def visit(node):
            if node in visiting:
                raise ProtocolError("composition_cycle", "RP1 requires an acyclic plan")
            if node in visited:
                return
            visiting.add(node)
            for source in edges[node]:
                visit(source)
            visiting.remove(node)
            visited.add(node)

        for node in edges:
            visit(node)

    def submit_plan(self, plan):
        if plan.get("kind") != "transaction_plan":
            raise ProtocolError("composition_invalid", "not a transaction plan")
        body = plan["body"]
        if plan["issuer_agent_id"] != body["orchestrator_agent_id"]:
            raise ProtocolError(
                "authority_denied", "plan author is not the orchestrator"
            )
        self._validate_graph(plan)
        lineage = self._lineage(plan)
        revision = body["revision"]
        if (
            isinstance(revision, bool)
            or not isinstance(revision, int)
            or not 1 <= revision <= 9007199254740991
        ):
            raise ProtocolError("composition_invalid", "invalid plan revision")
        full_ref = content_ref(plan)
        revision_key = digest([lineage, revision])
        conflict = False
        conflict_entries = []
        with self.ledger.transaction():
            existing = self.ledger.get("composition_revisions", revision_key)
            if existing and (
                existing["record_id"] != plan["id"]
                or existing["unsigned_digest"] != unsigned_digest(plan)
            ):
                existing["conflicted"] = True
                existing.setdefault("conflict_refs", []).append(full_ref)
                self.ledger.put("composition_revisions", revision_key, existing)
                self.ledger.put("composition_records", full_ref["digest"], plan)
                conflict_entries = [
                    ("composition_revisions", revision_key, existing),
                    ("composition_records", full_ref["digest"], plan),
                ]
                conflict = True
            else:
                if revision == 1:
                    if body["previous_digest"] is not None:
                        raise ProtocolError(
                            "composition_lineage", "initial predecessor must be null"
                        )
                else:
                    predecessor = self.ledger.get(
                        "composition_revisions", digest([lineage, revision - 1])
                    )
                    if not predecessor or predecessor.get("conflicted"):
                        raise ProtocolError(
                            "composition_lineage",
                            "missing or conflicted immediate predecessor",
                        )
                    if body["previous_digest"] not in predecessor["full_digests"]:
                        raise ProtocolError(
                            "composition_lineage",
                            "predecessor must be an exact prior full digest",
                        )
                if existing and existing.get("conflicted"):
                    conflict = True
                    conflict_entries = [
                        ("composition_revisions", revision_key, existing)
                    ]
                else:
                    entry = existing or {
                        "record_id": plan["id"],
                        "unsigned_digest": unsigned_digest(plan),
                        "full_digests": [],
                        "conflicted": False,
                    }
                    if full_ref["digest"] not in entry["full_digests"]:
                        entry["full_digests"].append(full_ref["digest"])
                    self.ledger.put("composition_revisions", revision_key, entry)
                    self.ledger.put("composition_records", full_ref["digest"], plan)
        if conflict:
            raise self._conflict_error(
                "composition_fork",
                "conflicting plan revision remains unresolved",
                conflict_entries,
            )
        return full_ref

    def _plan(self, ref):
        plan = self._resolve(ref)
        if plan.get("kind") != "transaction_plan":
            raise ProtocolError("composition_invalid", "plan reference has wrong kind")
        lineage = self._lineage(plan)
        for revision in range(1, plan["body"]["revision"] + 1):
            entry = self.ledger.get(
                "composition_revisions", digest([lineage, revision])
            )
            if not entry or entry.get("conflicted"):
                raise ProtocolError(
                    "composition_fork", "unadmitted or conflicted plan lineage"
                )
            if (
                revision == plan["body"]["revision"]
                and ref["digest"] not in entry["full_digests"]
            ):
                raise ProtocolError(
                    "composition_invalid", "unadmitted full plan reference"
                )
        return plan

    def _valid(self, plan):
        now = self.now_ms()
        validity = plan["body"].get("validity", {})
        if validity.get("mode") == "expires_at":
            try:
                deadline = milliseconds(validity["expires_at"])
            except (ProtocolError, KeyError):
                raise ProtocolError(
                    "composition_invalid", "invalid plan expiration"
                ) from None
            if now >= deadline:
                raise ProtocolError("composition_expired", "plan is expired")
        if self.validity_check is None or self.validity_check(plan, now) is not True:
            raise ProtocolError(
                "composition_unavailable", "current plan validity is not established"
            )

    def _match(self, candidate, plan, component_id):
        if candidate.get("kind") != "candidate_terms":
            raise ProtocolError(
                "composition_mismatch", "component must bind a candidate record"
            )
        composition = candidate.get("body", {}).get("composition", {})
        if composition.get("component_id") != component_id or not same_ref(
            composition.get("plan_ref"), content_ref(plan)
        ):
            raise ProtocolError(
                "composition_mismatch",
                "candidate does not name the exact plan and slot",
            )
        component = self._components(plan).get(component_id)
        if component is None:
            raise ProtocolError("composition_mismatch", "unknown component")
        participants = candidate["body"]["participants"]
        if len(participants) != 2 or {
            (p["agent_id"], p["principal_id"]) for p in participants
        } != {(p["agent_id"], p["principal_id"]) for p in component["required_agents"]}:
            raise ProtocolError(
                "composition_mismatch", "required agents/principals differ"
            )
        if (
            self.requirement_check is None
            or self.requirement_check(component["requirement"], candidate, plan)
            is not True
        ):
            raise ProtocolError(
                "unsupported_semantics",
                "complete component requirement not established",
            )

    def bind(self, binding):
        body = binding["body"]
        conflict = False
        conflict_entries = []
        with self.ledger.transaction():
            plan = self._plan(body["plan_ref"])
            if (
                binding.get("kind") != "composition_binding"
                or binding["issuer_agent_id"] != plan["issuer_agent_id"]
            ):
                raise ProtocolError(
                    "authority_denied",
                    "binding must be issued by the exact plan orchestrator",
                )
            self._valid(plan)
            candidate = self._resolve(body["candidate_ref"])
            self._match(candidate, plan, body["component_id"])
            slot = self._slot(plan, body["component_id"])
            prior = self.ledger.get("composition_slots", slot)
            if prior and (
                not same_ref(prior["candidate_ref"], body["candidate_ref"])
                or not same_ref(prior["plan_ref"], body["plan_ref"])
            ):
                prior["conflicted"] = True
                prior.setdefault("conflict_refs", []).append(content_ref(binding))
                self.ledger.put("composition_slots", slot, prior)
                self.ledger.put(
                    "composition_records", content_ref(binding)["digest"], binding
                )
                conflict_entries = [
                    ("composition_slots", slot, prior),
                    ("composition_records", content_ref(binding)["digest"], binding),
                ]
                conflict = True
            elif prior and prior.get("conflicted"):
                conflict = True
                conflict_entries = [("composition_slots", slot, prior)]
            else:
                if prior is None:
                    prior = {
                        "plan_ref": body["plan_ref"],
                        "candidate_ref": body["candidate_ref"],
                        "binding_ref": content_ref(binding),
                        "conflicted": False,
                    }
                    self.ledger.put("composition_slots", slot, prior)
                self.ledger.put(
                    "composition_records", content_ref(binding)["digest"], binding
                )
        if conflict:
            raise self._conflict_error(
                "composition_conflict",
                "slot resolution is immutable and conflicted",
                conflict_entries,
            )
        return prior

    def validate_candidate(self, candidate, *, require_binding=True):
        composition = candidate.get("body", {}).get("composition")
        if composition is None:
            return None
        plan = self._plan(composition["plan_ref"])
        self._valid(plan)
        self._match(candidate, plan, composition["component_id"])
        binding = self.ledger.get(
            "composition_slots", self._slot(plan, composition["component_id"])
        )
        if binding is None and not require_binding:
            return {"plan": plan, "binding": None}
        if not binding or binding.get("conflicted"):
            raise ProtocolError("composition_unbound", "slot is unbound or conflicted")
        if not same_ref(binding["plan_ref"], composition["plan_ref"]) or not same_ref(
            binding["candidate_ref"], content_ref(candidate)
        ):
            raise ProtocolError(
                "composition_mismatch", "candidate differs from pinned exact binding"
            )
        return {"plan": plan, "binding": binding}

    def dependency_agreements(self, candidate, stage, agreement_for_candidate):
        """Exact accepted records in the transitive declared prerequisite closure.

        Only dependencies at ``stage`` contribute; unrelated components do not.
        This proves neither principal clearance nor native authority. The caller
        must check each returned agreement's current recovery observation at its
        serialized handoff gate. Missing agreements retain a nonpositive outcome.
        """
        if stage not in {"formation", "handoff"}:
            raise ProtocolError("composition_invalid", "unknown transition stage")
        with self.ledger.transaction():
            validated = self.validate_candidate(candidate)
            if validated is None:
                return []
            plan = validated["plan"]
            visited = {candidate["body"]["composition"]["component_id"]}
            accepted_records = []

            def visit(component_id):
                for dependency in plan["body"]["dependencies"]:
                    if (
                        dependency["subject_component_id"] != component_id
                        or dependency["stage"] != stage
                    ):
                        continue
                    for requirement in dependency["requires"]:
                        source_id = requirement["component_id"]
                        if source_id in visited:
                            continue
                        visited.add(source_id)
                        binding = self.ledger.get(
                            "composition_slots", self._slot(plan, source_id)
                        )
                        if (
                            not binding
                            or binding.get("conflicted")
                            or not same_ref(binding["plan_ref"], content_ref(plan))
                        ):
                            raise ProtocolError(
                                "dependency_unavailable",
                                "prerequisite closure has an unbound/conflicted component",
                            )
                        source = self._resolve(binding["candidate_ref"])
                        self._match(source, plan, source_id)
                        accepted = agreement_for_candidate(binding["candidate_ref"])
                        if accepted is None:
                            raise ProtocolError(
                                "dependency_unavailable",
                                "prerequisite agreement not established",
                            )
                        if accepted.get("kind") != "accepted_offer" or not same_ref(
                            accepted["body"].get("candidate_ref"),
                            binding["candidate_ref"],
                        ):
                            raise ProtocolError(
                                "dependency_mismatch",
                                "closure accepted object differs from pinned candidate",
                            )
                        accepted_records.append(accepted)
                        visit(source_id)

            visit(candidate["body"]["composition"]["component_id"])
            return accepted_records

    @staticmethod
    def _status(status):
        if status is None:
            return "unknown"
        if isinstance(status, str):
            return status
        body = status.get("body", status)
        return body.get("status", body.get("state", "unknown"))

    def check(
        self,
        candidate,
        stage,
        agreement_for_candidate,
        status_for_agreement,
        evidence_check,
    ):
        if stage not in {"formation", "handoff"}:
            raise ProtocolError("composition_invalid", "unknown transition stage")
        with self.ledger.transaction():
            validated = self.validate_candidate(candidate)
            if validated is None:
                return True
            plan, own = (
                validated["plan"],
                candidate["body"]["composition"]["component_id"],
            )
            observations = []
            for dependency in plan["body"]["dependencies"]:
                if (
                    dependency["subject_component_id"] != own
                    or dependency["stage"] != stage
                ):
                    continue
                for requirement in dependency["requires"]:
                    binding = self.ledger.get(
                        "composition_slots",
                        self._slot(plan, requirement["component_id"]),
                    )
                    if (
                        not binding
                        or binding.get("conflicted")
                        or not same_ref(binding["plan_ref"], content_ref(plan))
                    ):
                        raise ProtocolError(
                            "dependency_unavailable",
                            "required exact component binding missing/conflicted",
                        )
                    source = self._resolve(binding["candidate_ref"])
                    self._match(source, plan, requirement["component_id"])
                    accepted = agreement_for_candidate(binding["candidate_ref"])
                    if accepted is not None:
                        if accepted.get("kind") != "accepted_offer" or not same_ref(
                            accepted["body"].get("candidate_ref"),
                            binding["candidate_ref"],
                        ):
                            raise ProtocolError(
                                "dependency_mismatch",
                                "accepted object is not for the exact bound candidate",
                            )
                    status = (
                        status_for_agreement(content_ref(accepted))
                        if accepted is not None
                        else None
                    )
                    if accepted is not None and isinstance(status, dict):
                        status_body = status.get("body", status)
                        observed_ref = status_body.get("accepted_offer_ref")
                        if observed_ref is not None and not same_ref(
                            observed_ref, content_ref(accepted)
                        ):
                            raise ProtocolError(
                                "dependency_mismatch",
                                "status describes another exact agreement",
                            )
                    state = self._status(status)
                    # Current refusal is checked even for historical agent_agreement.
                    if state == "refused":
                        raise ProtocolError(
                            "dependency_refused",
                            "source agreement has an absorbing refusal",
                        )
                    if accepted is not None and state not in {
                        "pending_refusal_windows",
                        "refusal_windows_closed",
                        "cleared",
                        "pending",
                    }:
                        raise ProtocolError(
                            "dependency_unavailable",
                            "current source observation unavailable",
                        )
                    condition = requirement["condition"]
                    observation = {
                        "dependency_id": dependency["dependency_id"],
                        "stage": stage,
                        "binding_ref": binding["binding_ref"],
                        "candidate_ref": binding["candidate_ref"],
                        "agreement_ref": content_ref(accepted) if accepted else None,
                        "status": status,
                    }
                    if condition in {"agent_agreement", "principal_clearance"}:
                        if accepted is None:
                            raise ProtocolError(
                                "dependency_unmet",
                                "exact component agreement has not formed",
                            )
                        if condition == "principal_clearance" and state not in {
                            "refusal_windows_closed",
                            "cleared",
                        }:
                            raise ProtocolError(
                                "dependency_unmet",
                                "source principal periods have not cleared",
                            )
                    else:
                        result = (
                            evidence_check(requirement, source, accepted, stage)
                            if evidence_check
                            else None
                        )
                        if (
                            not isinstance(result, dict)
                            or result.get("state") != "established"
                        ):
                            failed = (
                                isinstance(result, dict)
                                and result.get("state") == "failed"
                            )
                            unmet = (
                                isinstance(result, dict)
                                and result.get("state") == "unmet"
                            )
                            code = (
                                "dependency_failed"
                                if failed
                                else "dependency_unmet"
                                if unmet
                                else "dependency_unavailable"
                            )
                            disposition = dependency["on_failed"] if failed else "hold"
                            raise ProtocolError(
                                code,
                                "typed evidence predicate is not established; disposition="
                                + disposition,
                            )
                        if (
                            not result.get("evidence_refs")
                            or not result.get("evaluator")
                            or not result.get("policy_ref")
                        ):
                            raise ProtocolError(
                                "dependency_unavailable",
                                "predicate provenance is incomplete",
                            )
                        observation["evidence"] = result
                    observations.append(observation)
            self.ledger.put(
                "composition_observations",
                digest([content_ref(candidate), stage, self.ledger.revision]),
                observations,
            )
            return True
