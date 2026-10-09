"""ABP semantic enforcement and signed A2A interaction outcomes.

A harness owns one agent's signer. Peers never receive that key. All participants
in this reference deployment explicitly delegate conflicting state to one ledger.
"""

from copy import deepcopy
from dataclasses import asdict
from .policy import check_commit
from uuid import uuid4
from .crypto import canonical, content_ref, digest, unsigned_digest
from .schema import validate
from .errors import ProtocolError
from .records import RecordStore, same_ref, ref_key
from .guards import Guards, need, timestamp, milliseconds
from .recovery import Recovery
from .composition import Composition
from .handoff import Handoff

P = "https://github.com/JohnnyFiv3r/agent-bazaar/blob/main/profiles/reference-profile.md"
PROFILE = "abp/0.4-draft"
CONTROL = {
    "publication_contract",
    "admission_grant",
    "accepted_offer",
    "finalization_notice",
    "refusal_event",
    "status_snapshot",
    "withdrawal_event",
    "negotiation_close",
}
FEATURES = {"bilateral", "composition", "adapter-handoff", "lifecycle-evidence"}


class Harness:
    def __init__(
        self,
        *,
        signer,
        registry,
        ledger,
        policy,
        clock,
        domain,
        enrollments,
        authority_scope,
        recipient_scope,
        failpoint=None,
    ):
        self.signer, self.registry, self.ledger, self.policy, self.clock = (
            signer,
            registry,
            ledger,
            policy,
            clock,
        )
        self.domain, self.enrollments = domain, enrollments
        self.authority_scope, self.recipient_scope = authority_scope, recipient_scope
        self.agent_id = signer.agent_id
        self.principal_id = signer.principal_id
        self.store = RecordStore(ledger)
        self.guards = Guards(self)
        self.recovery = Recovery(ledger)
        self.failpoint = failpoint or (lambda name: None)
        self.composition = Composition(
            ledger,
            self.resolve,
            requirement_check=domain.requirement,
            now_ms=self.now,
            validity_check=lambda plan, now: self.guards.validity(plan),
        )
        self.handoff = Handoff(
            ledger,
            self.resolve,
            emit=self.emit,
            action_check=self._action_check,
            gate_check=self._handoff_gate,
            clock=self.now,
            failpoint=self.failpoint,
        )

    def now(self):
        return self.clock.read().now_ms

    def resolve(self, ref):
        try:
            return self.store.resolve(ref)
        except ProtocolError as error:
            wrapper = self.ledger.get("handoff_objects", ref["digest"])
            if wrapper is None or not same_ref(content_ref(wrapper), ref):
                raise error
            return wrapper

    def boundary_digest(self):
        # Bind all mutable authority state and locally enrolled configuration.
        # Immutable object bytes are already bound by their exact references.
        def jsonable(value):
            if isinstance(value, (set, frozenset)):
                return sorted(value)
            if isinstance(value, dict):
                return {k: jsonable(v) for k, v in value.items()}
            if isinstance(value, (tuple, list)):
                return [jsonable(v) for v in value]
            return value

        return digest(
            jsonable(
                {
                    "ledger": self.ledger.snapshot(),
                    "enrollments": {k: asdict(v) for k, v in self.enrollments.items()},
                    "identities": self.registry.identities,
                    "keys": {k: asdict(v) for k, v in self.registry.keys.items()},
                    "profile_types": self.registry.profile_types,
                    "trusted_refs": self.domain.trusted_refs,
                    "understood_uris": self.domain.understood_uris,
                    "selection": self.domain.selection,
                    "actions": {
                        k: v.semantics_ref for k, v in self.domain.actions.items()
                    },
                    "policy_bundle_ref": self.policy.policy_bundle_ref,
                    "policy_data_ref": self.policy.policy_data_ref,
                    "configured_test_grants": getattr(self.policy, "grants", None),
                }
            )
        )

    def emit(self, kind, body, *, features=None, identifier=None):
        record = {
            "profile": PROFILE,
            "kind": kind,
            "id": identifier or f"{kind}:{uuid4()}",
            "issuer_agent_id": self.agent_id,
            "issuer_principal_id": self.principal_id,
            "created_at": timestamp(self.now()),
            "required_extensions": [],
            "required_features": sorted(features or self.features_for(kind, body)),
            "body": deepcopy(body),
        }
        signed, proof = self.signer.sign(record)
        self.store.put(proof)
        validate(signed)
        self.store.put(signed)
        return signed

    def emit_profile(self, type_uri, body):
        record = {
            "id": f"evidence:{uuid4()}",
            "profile": PROFILE,
            "type_uri": type_uri,
            "issuer_agent_id": self.agent_id,
            "issued_at": timestamp(self.now()),
            "body": deepcopy(body),
        }
        signed, proof = self.signer.sign(record)
        self.store.put(proof)
        self.store.put(signed)
        return signed

    @staticmethod
    def features_for(kind, body):
        f = {"bilateral"}
        if kind in ("transaction_plan", "composition_binding") or "composition" in body:
            f.add("composition")
        if kind in (
            "handoff_request",
            "prepared_handoff",
            "handoff_receipt",
        ) or body.get("purpose") in (
            "prepare_handoff",
            "dispatch_handoff",
            "reconcile_handoff",
        ):
            f.update(("adapter-handoff", "lifecycle-evidence"))
        if kind == "lifecycle_evidence":
            f.add("lifecycle-evidence")
        return f

    def verify(self, record):
        validate(record)
        entry = self.registry.verify(record, self.resolve, self.now())
        e = self.guards.enrollment(record["issuer_agent_id"])
        need(
            record["issuer_principal_id"] == e.principal_id,
            "identity_mismatch",
            "principal not enrolled",
        )
        if "required_features" in record:
            f = set(record["required_features"])
            need(
                self.features_for(record["kind"], record["body"]) <= f <= FEATURES,
                "unsupported_semantics",
                "omitted or unknown required feature",
            )
            need(
                f <= e.features and f <= self.guards.enrollment(self.agent_id).features,
                "unsupported_semantics",
                "peer feature intersection",
            )
            need(
                set(record["required_extensions"]) <= self.domain.understood_uris,
                "unsupported_semantics",
                "required extension unavailable",
            )
        return entry

    def require_admitted(self, ref):
        need(
            self.store.is_admitted(ref),
            "evidence_unavailable",
            "record has not been semantically admitted: " + ref["id"],
        )

    def _lineage(self, record):
        b = record["body"]
        kind = record["kind"]
        actor = record["issuer_agent_id"]
        if kind == "offer":
            return (
                f"offer:{actor}:{b['negotiation_id']}:{b['option_id']}",
                b["revision"],
                b["previous_option_digest"],
            )
        if kind == "publication_contract":
            return (
                f"publication:{actor}:{b['contract_id']}",
                b["revision"],
                b["previous_digest"],
            )
        if kind == "intent":
            return (
                f"intent:{actor}:{b['intent_id']}",
                b["revision"],
                b["previous_digest"],
            )
        return None

    def require_head(self, record):
        lineage = self._lineage(record)
        if lineage:
            need(
                not self.ledger.get("lineage_conflicts", lineage[0]),
                "lineage_conflict",
                "lineage has unresolved authenticated fork",
            )
            old = self.ledger.get("heads", lineage[0])
            need(
                old is not None and old["unsigned_digest"] == unsigned_digest(record),
                "lineage_conflict",
                "superseded option/publication/intent",
            )

    def _check_lineage_fork(self, record):
        lineage = self._lineage(record)
        if not lineage:
            return
        key, revision, _ = lineage
        need(
            not self.ledger.get("lineage_conflicts", key),
            "lineage_conflict",
            "lineage has unresolved authenticated fork",
        )
        known = self.ledger.get("lineage_history", key + ":" + str(revision))
        if known and known["unsigned_digest"] != unsigned_digest(record):
            error = ProtocolError(
                "lineage_conflict", "authenticated competing revision"
            )
            error.lineage_conflict_entry = (
                key,
                {"original_ref": known["ref"], "conflicting_ref": content_ref(record)},
            )
            raise error

    def _preserve_conflict(self, error):
        self.composition.preserve_conflict(error)
        entry = getattr(error, "lineage_conflict_entry", None)
        if entry:
            self.ledger.put("lineage_conflicts", entry[0], entry[1])

    def _advance_lineage(self, record):
        lineage = self._lineage(record)
        if not lineage:
            return
        key, revision, previous = lineage
        old = self.ledger.get("heads", key)
        if old and old["unsigned_digest"] == unsigned_digest(record):
            return
        if old:
            need(
                revision == old["revision"] + 1 and previous == old["ref"]["digest"],
                "lineage_conflict",
                "missing predecessor or divergent lineage",
            )
            need(
                not self.ledger.get("pins", ref_key(old["ref"])),
                "selection_conflict",
                "option pinned by an unresolved or finalized agreement",
            )
        else:
            need(
                revision == 1 and previous is None,
                "lineage_conflict",
                "lineage must start at revision 1",
            )
        entry = {
            "revision": revision,
            "ref": content_ref(record),
            "unsigned_digest": unsigned_digest(record),
        }
        self.ledger.put("heads", key, entry)
        self.ledger.put("lineage_history", key + ":" + str(revision), entry)

    def authorize(
        self,
        actor,
        act,
        subject,
        *,
        clearance_refs=(),
        dependency_refs=(),
        native_refs=(),
        action_ref=None,
    ):
        e = self.guards.enrollment(actor)
        reading = self.clock.read()
        bundle = self.policy.policy_bundle_ref
        data = self.policy.policy_data_ref
        self.domain.require_ref(bundle)
        self.domain.require_ref(data)
        inp = {
            "profile": "abp-rp1/0.1-draft",
            "decision_id": f"decision:{uuid4()}",
            "actor": {
                "agent_id": actor,
                "principal_id": e.principal_id,
                "transport_certificate_digest": self.ledger.get(
                    "transport_identity", actor, ""
                ),
            },
            "act": act,
            "recipient_scope_id": self.recipient_scope,
            "subject_ref": content_ref(subject),
            "subject": subject,
            "action_ref": action_ref,
            "authority_refs": [e.principal_policy_ref],
            "clearance_refs": list(clearance_refs),
            "dependency_evidence_refs": list(dependency_refs),
            "native_authorization_refs": list(native_refs),
            "authority_scope_id": self.authority_scope,
            "authority_revision": self.ledger.revision,
            "boundary_state_digest": self.boundary_digest(),
            "policy_bundle_ref": bundle,
            "policy_data_ref": data,
            "clock": {
                "now": timestamp(reading.now_ms),
                "uncertainty_ms": reading.uncertainty_ms,
            },
        }
        try:
            result = self.policy.evaluate(inp, now_ms=self.now())
        except ProtocolError as error:
            error.policy_failure = True
            error.policy_input = inp
            raise
        check_commit(
            result,
            authority_revision=self.ledger.revision,
            boundary_state_digest=self.boundary_digest(),
            now_ms=self.now(),
        )
        return self.emit_profile(
            P + "#rp1-opa/policy-decision",
            {"input": inp, "result": result, "evaluated_at": timestamp(self.now())},
        )

    def submit(self, record):
        """Authenticated local authority entry; network callers use invoke for admission."""
        try:
            with self.ledger.transaction():
                self.verify(record)
                self.authorize(record["issuer_agent_id"], "submit_record", record)
                return self._apply(record)
        except ProtocolError as error:
            with self.ledger.transaction():
                self._preserve_conflict(error)
            raise

    def _apply(self, record):
        ref = content_ref(record)
        if self.store.is_admitted(ref):
            return record
        self.store.put(record)
        kind, b, actor = record["kind"], record["body"], record["issuer_agent_id"]
        self.authorize(actor, "submit_record", record)
        self._check_lineage_fork(record)
        pinned = self.ledger.get("semantic_identity", actor + "\x00" + record["id"])
        if (
            pinned is not None
            and pinned != unsigned_digest(record)
            and kind == "transaction_plan"
        ):
            self.composition.submit_plan(record)
        need(
            pinned is None or pinned == unsigned_digest(record),
            "lineage_conflict",
            "immutable identity reused",
        )
        if pinned is not None:
            self.store.admit_identity(record)
            return self.resolve(
                self.ledger.get("semantic_refs", actor + "\x00" + record["id"])
            )
        if kind == "publication_contract":
            self.guards.publication(record)
            if actor == self.agent_id:
                self.ledger.put("recipient_publication", self.agent_id, ref)
        elif kind == "intent":
            self.require_admitted(b["publication_contract_ref"])
            p = self.resolve(b["publication_contract_ref"])
            need(
                p["issuer_agent_id"] == actor,
                "identity_mismatch",
                "intent publication issuer",
            )
            self.guards.publication(p)
            self.require_head(p)
            need(
                set(b["disclosure_audience"])
                <= set(p["body"]["discovery"]["audiences"]),
                "permission_absent",
                "intent exceeds publication audience",
            )
            self.guards.own_promise(b["emission_promise"], actor)
            self.guards.validity(record)
        elif kind == "promise":
            self.require_admitted(b["publication_contract_ref"])
            need(
                self.resolve(b["publication_contract_ref"])["issuer_agent_id"] == actor,
                "identity_mismatch",
                "promise publication issuer",
            )
            self.guards.own_promise(b["own_promise"], actor)
        elif kind == "offer":
            self.guards.offer(record)
            need(
                not self.ledger.get(
                    "contact_closed", f"{b['negotiation_id']}:{self.agent_id}"
                ),
                "contact_closed",
                "recipient closed negotiation",
            )
        elif kind == "candidate_terms":
            self.guards.candidate(record)
        elif kind == "terms_adoption":
            candidate = self.guards.adoption(record)
            key = ref_key(b["candidate_ref"]) + ":" + actor
            old = self.ledger.get("adoptions", key)
            if old:
                need(
                    unsigned_digest(self.resolve(old)) == unsigned_digest(record),
                    "lineage_conflict",
                    "adoption already pinned; withdraw/dispose explicitly",
                )
            self.ledger.put("adoptions", key, ref)
            for o in candidate["body"]["selected_options"]:
                pins = self.ledger.get("pins", ref_key(o["offer_ref"]), [])
                if b["candidate_ref"] not in pins:
                    pins.append(b["candidate_ref"])
                self.ledger.put("pins", ref_key(o["offer_ref"]), pins)
        elif kind == "admission_grant":
            self._grant(record)
        elif kind == "clarification":
            self.guards.origin(b["origin"])
            self.require_admitted(b["subject_ref"])
            self.domain.require_ref(b["privacy_policy_ref"])
            need(
                not self.ledger.get(
                    "contact_closed", f"{b['negotiation_id']}:{self.agent_id}"
                ),
                "contact_closed",
                "clarification after close",
            )
        elif kind == "negotiation_close":
            self.guards.origin(b["origin"])
            self.ledger.put("contact_closed", f"{b['negotiation_id']}:{actor}", True)
        elif kind == "withdrawal_event":
            self._withdraw(record)
        elif kind == "transaction_plan":
            self.require_admitted(b["origin_ref"])
            self.domain.require_ref(b["privacy_policy_ref"])
            self.guards.validity(record)
            self.composition.submit_plan(record)
        elif kind == "composition_binding":
            self.require_admitted(b["plan_ref"])
            self.require_admitted(b["candidate_ref"])
            self.composition.bind(record)
        elif kind == "finalization_notice":
            self._notice(record)
        elif kind == "refusal_event":
            self._refuse(record)
        elif kind == "lifecycle_evidence":
            self._lifecycle(record)
        elif kind == "handoff_request":
            self._action_check(
                record,
                self.resolve(b["agreement_ref"]),
                self.resolve(self.resolve(b["agreement_ref"])["body"]["candidate_ref"]),
            )
        else:
            # Results must come from the authority operation, not a peer supplying a claimed result.
            raise ProtocolError(
                "authority_absent", "authority result requires its governing operation"
            )
        self._advance_lineage(record)
        self.store.admit_identity(record)
        return record

    def _grant(self, record):
        b = record["body"]
        actor = record["issuer_agent_id"]
        e = self.guards.enrollment(actor)
        need(
            actor == b["recipient_agent_id"]
            and same_ref(b["admission_policy_ref"], e.admission_policy_ref),
            "authority_absent",
            "grant issuer/policy",
        )
        need(
            self.guards.enrollment(b["grantee_agent_id"]).principal_id
            == b["grantee_principal_id"],
            "identity_mismatch",
            "grant principal",
        )
        policy = self.resolve(e.admission_policy_ref)
        self.verify(policy)
        pools = [p for p in policy["pools"] if p["allowance_id"] in b["allowance_ids"]]
        need(
            len(pools) == len(set(b["allowance_ids"])),
            "permission_absent",
            "unknown allowance",
        )
        need(
            set(b["allowed_record_kinds"])
            <= set().union(*(set(p["record_kinds"]) for p in pools)),
            "permission_absent",
            "grant kind expansion",
        )
        need(
            set(b["operation_purposes"])
            <= set().union(*(set(p["operation_purposes"]) for p in pools)),
            "permission_absent",
            "grant purpose expansion",
        )
        self.require_admitted(b["publication_contract_ref"])
        publication = self.resolve(b["publication_contract_ref"])
        need(
            publication.get("kind") == "publication_contract"
            and publication["issuer_agent_id"] == actor,
            "authority_absent",
            "grant publication issuer",
        )
        self.guards.publication(publication)
        self.require_head(publication)
        need(
            b["recipient_scope_id"] == policy["recipient_scope_id"],
            "permission_absent",
            "grant scope expansion",
        )
        # Every named allowance still enforces its own validity at use time.
        self.guards.validity(policy)
        self.guards.validity(record)

    def _withdraw(self, record):
        b = record["body"]
        target = self.resolve(b["target_ref"])
        self.require_admitted(b["target_ref"])
        need(
            target["kind"] == b["target_kind"]
            and target["issuer_agent_id"] == record["issuer_agent_id"],
            "authority_absent",
            "withdrawal actor/target",
        )
        for r in b["authority_refs"]:
            self.domain.require_ref(r)
        original_ref = (
            self.ledger.get(
                "semantic_refs", target["issuer_agent_id"] + "\x00" + target["id"]
            )
            or b["target_ref"]
        )
        if target["kind"] in ("candidate_terms", "terms_adoption", "offer"):
            candidate_ref = (
                b["target_ref"]
                if target["kind"] == "candidate_terms"
                else target["body"].get("candidate_ref")
            )
            if candidate_ref:
                need(
                    self.agreement_for_candidate(candidate_ref) is None,
                    "selection_conflict",
                    "formed agreement requires refusal or replacement",
                )
            elif self.ledger.get("pins", ref_key(original_ref)):
                raise ProtocolError(
                    "selection_conflict",
                    "pinned option requires ordered candidate disposition",
                )
        self.ledger.put("withdrawn", ref_key(b["target_ref"]), content_ref(record))
        self.ledger.put(
            "withdrawn_semantic",
            target["issuer_agent_id"] + "\x00" + target["id"],
            content_ref(record),
        )
        if target["kind"] == "candidate_terms":
            for o in target["body"]["selected_options"]:
                pins = self.ledger.get("pins", ref_key(o["offer_ref"]), [])
                self.ledger.put(
                    "pins",
                    ref_key(o["offer_ref"]),
                    [p for p in pins if not same_ref(p, b["target_ref"])],
                )

    def agreement_for_candidate(self, ref):
        candidate = self.resolve(ref)
        key = self.formation_key(candidate)
        saved = self.ledger.get("formations", key)
        if not saved:
            return None
        need(
            same_ref(saved["candidate_ref"], ref),
            "lineage_conflict",
            "formation pinned another full candidate reference",
        )
        return self.resolve(saved["accepted_ref"])

    @staticmethod
    def formation_key(candidate):
        return digest(
            [
                candidate["body"]["origin"]["coordinator_agent_id"],
                candidate["issuer_agent_id"],
                candidate["id"],
            ]
        )

    def finalize(self, candidate_ref, *, caller=None):
        with self.ledger.transaction():
            candidate = self.resolve(candidate_ref)
            actor = caller or self.agent_id
            need(
                candidate.get("kind") == "candidate_terms",
                "invalid_record",
                "finalization requires candidate",
            )
            need(
                actor in {p["agent_id"] for p in candidate["body"]["participants"]},
                "authority_absent",
                "formation requester not participant",
            )
            need(
                candidate["body"]["origin"]["coordinator_agent_id"] == self.agent_id,
                "identity_mismatch",
                "wrong coordinator",
            )
            existing = self.agreement_for_candidate(candidate_ref)
            if existing:
                self.authorize(actor, "query_status", existing)
                return existing
            self.require_admitted(candidate_ref)
            self.guards.candidate(candidate, stage="formation")
            self.composition.check(
                candidate,
                "formation",
                self.agreement_for_candidate,
                self._status_for_composition,
                self._evidence_check,
            )
            b = candidate["body"]
            adoptions = []
            participant_decisions = []
            for p in b["participants"]:
                ref = self.ledger.get(
                    "adoptions", ref_key(candidate_ref) + ":" + p["agent_id"]
                )
                need(ref is not None, "evidence_unavailable", "missing exact adoption")
                record = self.resolve(ref)
                self.verify(record)
                self.guards.adoption(record)
                adoptions.append(ref)
                participant_decisions.append(
                    content_ref(
                        self.authorize(p["agent_id"], "authority_commit", candidate)
                    )
                )
            decision = self.authorize(actor, "finalize_candidate", candidate)
            self._reserve_capacity(candidate)
            accepted = self.emit(
                "accepted_offer",
                {
                    "accepted_offer_id": f"agreement:{uuid4()}",
                    "candidate_ref": candidate_ref,
                    "origin": b["origin"],
                    "adoption_refs": adoptions,
                    "finalized_at": timestamp(self.now()),
                    "principal_refusal_windows": b["principal_refusal_windows"],
                    "clock_profile_ref": b["clock_profile_ref"],
                    "status_authority_agent_id": b["status_authority_agent_id"],
                    "status_policy_ref": b["status_policy_ref"],
                    "status_ref": f"https://example.invalid/status/{candidate['id']}",
                    "finalization_check_refs": [content_ref(decision)]
                    + participant_decisions,
                    "initial_status": "pending_refusal_windows",
                },
                features=candidate["required_features"],
            )
            self.store.admit_identity(accepted)
            self.ledger.put(
                "formations",
                self.formation_key(candidate),
                {"candidate_ref": candidate_ref, "accepted_ref": content_ref(accepted)},
            )
            self.recovery.register(
                content_ref(accepted),
                candidate_ref=candidate_ref,
                finalized_at_ms=self.now(),
                principal_ids=[p["principal_id"] for p in b["participants"]],
                descriptors=b["principal_refusal_windows"],
            )
            self.failpoint("before_formation_commit")
        self.failpoint("after_formation_commit")
        return accepted

    def _reserve_capacity(self, candidate):
        demands = {}
        for r in candidate["body"]["selection_constraints_refs"]:
            rules = self.domain.selection.get(ref_key(r))
            need(
                rules is not None, "unsupported_semantics", "unknown capacity semantics"
            )
            for resource, units in rules.get("resources", {}).items():
                need(
                    type(units) is int and units > 0,
                    "invalid_record",
                    "capacity quantity",
                )
                demands[resource] = demands.get(resource, 0) + units
        for resource, units in demands.items():
            config = self.ledger.get("resource_limits", resource)
            need(
                config is not None and config["scope"] == self.authority_scope,
                "authority_absent",
                "resource outside delegated authority",
            )
            used = self.ledger.get("resource_used", resource, 0)
            need(
                used + units <= config["limit"],
                "selection_conflict",
                "insufficient shared capacity",
            )
            self.ledger.put("resource_used", resource, used + units)
        self.ledger.put("commitments", self.formation_key(candidate), demands)

    def _principal_enrollment(self, accepted, principal):
        c = self.resolve(accepted["body"]["candidate_ref"])
        agents = [
            p["agent_id"]
            for p in c["body"]["participants"]
            if p["principal_id"] == principal
        ]
        need(bool(agents), "identity_mismatch", "principal not represented")
        return self.enrollments[agents[0]]

    def _verified_profile(self, ref, type_uri, issuer):
        record = self.resolve(ref)
        self.registry.verify(record, self.resolve, self.now())
        need(
            record.get("type_uri") == type_uri and record["issuer_agent_id"] == issuer,
            "identity_mismatch",
            "wrong evidence authority/type",
        )
        return record

    def _notice(self, record):
        b = record["body"]
        accepted = self.resolve(b["accepted_offer_ref"])
        self.require_admitted(b["accepted_offer_ref"])
        e = self._principal_enrollment(accepted, b["principal_id"])
        need(
            record["issuer_agent_id"] == e.notice_agent_id
            and accepted["body"]["status_authority_agent_id"] == self.agent_id,
            "authority_absent",
            "notice authority",
        )
        proof = self._verified_profile(
            b["delivery_evidence_ref"],
            P + "#rp1-principal-inbox/availability",
            e.notice_agent_id,
        )
        pb = proof["body"]
        need(
            pb.get("principal_id") == b["principal_id"]
            and same_ref(pb.get("accepted_offer_ref"), b["accepted_offer_ref"])
            and same_ref(pb.get("candidate_ref"), b["terms_ref"]),
            "identity_mismatch",
            "notice evidence target",
        )
        need(
            pb.get("terms_available") is True and pb.get("refusal_available") is True,
            "evidence_unavailable",
            "notice path not usable",
        )
        at = milliseconds(b["notice_at"])
        need(
            at <= self.now() and at == pb.get("verified_at_ms"),
            "invalid_record",
            "notice time not evidenced",
        )
        self.recovery.notice(
            b["accepted_offer_ref"],
            prevalidated_notice={
                "evidence_ref": content_ref(record),
                "principal_id": b["principal_id"],
                "accepted_offer_ref": b["accepted_offer_ref"],
                "candidate_ref": b["terms_ref"],
                "notice_target_ref": b["notice_target_ref"],
                "notice_profile_ref": b["notice_profile_ref"],
                "refusal_mechanism_ref": b["refusal_mechanism_ref"],
                "review_duration_ms": b["review_duration_ms"],
                "verified_at_ms": at,
                "authority_order": self.ledger.revision + 1,
            },
        )

    def health(self, evidence):
        """Ingest designated authority's signed health interval; never infer it from a probe."""
        with self.ledger.transaction():
            self.registry.verify(evidence, self.resolve, self.now())
            b = evidence["body"]
            accepted = self.resolve(b["accepted_offer_ref"])
            e = self._principal_enrollment(accepted, b["principal_id"])
            need(
                evidence["issuer_agent_id"] == e.notice_agent_id
                and evidence["type_uri"] == P + "#rp1-principal-inbox/health-interval",
                "authority_absent",
                "health authority",
            )
            need(
                all(
                    k in b
                    for k in (
                        "interval_end_ms",
                        "service_evidence_refs",
                        "continuity_evidence_ref",
                    )
                )
                and isinstance(b["service_evidence_refs"], list),
                "invalid_record",
                "incomplete health evidence",
            )
            need(
                b["interval_end_ms"] <= self.now(),
                "invalid_record",
                "future health evidence",
            )
            for ref in b["service_evidence_refs"] + [b["continuity_evidence_ref"]]:
                self.domain.require_ref(ref)
                self.resolve(ref)
            descriptor = next(
                w
                for w in accepted["body"]["principal_refusal_windows"]
                if w["principal_id"] == b["principal_id"]
            )
            predicate = self.domain.health_checks.get(
                ref_key(descriptor["notice_profile_ref"])
            )
            need(
                predicate is not None
                and predicate(evidence, descriptor, self.clock.read()) is True,
                "evidence_unavailable",
                "health continuity and adopted channels not established",
            )
            self.store.put(evidence)
            self.recovery.health(
                b["accepted_offer_ref"],
                prevalidated_health={**b, "evidence_ref": content_ref(evidence)},
            )

    def _refuse(self, record, operation_key=None):
        b = record["body"]
        accepted = self.resolve(b["accepted_offer_ref"])
        self.require_admitted(b["accepted_offer_ref"])
        identity = record["issuer_agent_id"] + "\x00" + record["id"]
        original = self.ledger.get("semantic_refs", identity)
        if original:
            need(
                self.ledger.get("semantic_identity", identity)
                == unsigned_digest(record),
                "lineage_conflict",
                "refusal identity changed",
            )
            self.store.admit_identity(record)
            return self.resolve(original)
        need(
            accepted["body"]["status_authority_agent_id"]
            == self.agent_id
            == b["status_authority_agent_id"],
            "identity_mismatch",
            "wrong refusal authority",
        )
        e = self._principal_enrollment(accepted, b["refusing_principal_id"])
        need(
            record["issuer_agent_id"] in e.control_agents,
            "authority_absent",
            "ordinary negotiation authority cannot refuse",
        )
        need(
            same_ref(b["authority_ref"], e.principal_policy_ref),
            "authority_absent",
            "refusal delegation",
        )
        op = operation_key or (
            self.recipient_scope,
            record["issuer_agent_id"],
            record["id"],
        )
        reading = self.clock.read()
        self.recovery.admit_refusal(
            b["accepted_offer_ref"],
            principal_id=b["refusing_principal_id"],
            operation_key=op,
            request_digest=unsigned_digest(record),
            peer_agent_id=record["issuer_agent_id"],
            admitted_lower_ms=reading.now_ms - reading.uncertainty_ms,
            admitted_upper_ms=reading.now_ms + reading.uncertainty_ms,
        )
        self.recovery.resolve_refusal(
            b["accepted_offer_ref"],
            operation_key=op,
            prevalidated_refusal={
                "evidence_ref": content_ref(record),
                "principal_id": b["refusing_principal_id"],
                "accepted_offer_ref": b["accepted_offer_ref"],
                "refusal_authority_ref": b["authority_ref"],
                "authority_order": self.ledger.revision + 1,
            },
        )
        return record

    def status(self, accepted_ref, *, caller=None):
        with self.ledger.transaction():
            accepted = self.resolve(accepted_ref)
            self.require_admitted(accepted_ref)
            need(
                accepted.get("kind") == "accepted_offer",
                "invalid_record",
                "status requires accepted offer",
            )
            need(
                accepted["body"]["status_authority_agent_id"] == self.agent_id,
                "identity_mismatch",
                "wrong status authority",
            )
            decision = self.authorize(caller or self.agent_id, "query_status", accepted)
            reading = self.clock.read()
            c = self.resolve(accepted["body"]["candidate_ref"])
            active = all(
                self.enrollments[p["agent_id"]].active
                for p in c["body"]["participants"]
            )
            obs = self.recovery.observe(
                accepted_ref,
                now_ms=reading.now_ms,
                uncertainty_ms=reading.uncertainty_ms,
                clock_evidence_ref=reading.evidence_ref,
                authority_evidence_refs=[content_ref(decision)] if active else [],
            )
            previous = self.ledger.get("status_records", ref_key(accepted_ref))
            windows = []
            for p in obs["principals"]:
                state = {
                    "notice_pending": "awaiting_notice",
                    "window_open": "open",
                }.get(p["state"], p["state"])
                if obs["status"] == "refused" and state != "closed":
                    state = "refused"
                w = {"principal_id": p["principal_id"], "state": state}
                if p.get("notice_ref"):
                    w["notice_ref"] = p["notice_ref"]
                if p.get("starts_at_ms") is not None:
                    w["starts_at"] = timestamp(p["starts_at_ms"])
                    w["deadline"] = timestamp(p["effective_deadline_ms"])
                windows.append(w)
            checks = []
            for principal in sorted(
                {p["principal_id"] for p in c["body"]["participants"]}
            ):
                e = self._principal_enrollment(accepted, principal)
                checks.append(
                    {
                        "principal_id": principal,
                        "policy_status_ref": e.principal_policy_ref,
                        "authority_status_ref": content_ref(decision),
                    }
                )
            evidence = self.emit_profile(
                P + "#rp1-durable-authority/recovery-observation", obs
            )
            record = self.emit(
                "status_snapshot",
                {
                    "accepted_offer_ref": accepted_ref,
                    "revision": 1 if not previous else previous["revision"] + 1,
                    "previous_status_digest": None
                    if not previous
                    else previous["ref"]["digest"],
                    "status": obs["status"],
                    "as_of": timestamp(self.now()),
                    "freshness_policy_ref": accepted["body"]["status_policy_ref"],
                    "clock_evidence_ref": reading.evidence_ref,
                    "notice_refs": [
                        p["notice_ref"]
                        for p in obs["principals"]
                        if p.get("notice_ref")
                    ],
                    "principal_windows": windows,
                    "current_policy_authority_checks": checks,
                    "refusal_event_refs": obs["refusal_event_refs"],
                    "status_authority_event_refs": [content_ref(evidence)],
                },
                features=c["required_features"],
            )
            self.store.admit_identity(record)
            self.ledger.put(
                "status_records",
                ref_key(accepted_ref),
                {"revision": record["body"]["revision"], "ref": content_ref(record)},
            )
            return record

    def _status_for_composition(self, accepted):
        # Current authoritative facts from the common ledger, even for a different coordinator.
        ref = content_ref(accepted) if "body" in accepted else accepted
        reading = self.clock.read()
        a = self.resolve(ref)
        c = self.resolve(a["body"]["candidate_ref"])
        authorities = [
            self.enrollments[p["agent_id"]].principal_policy_ref
            for p in c["body"]["participants"]
            if self.enrollments[p["agent_id"]].active
        ]
        obs = self.recovery.observe(
            ref,
            now_ms=reading.now_ms,
            uncertainty_ms=reading.uncertainty_ms,
            clock_evidence_ref=reading.evidence_ref,
            authority_evidence_refs=authorities if len(authorities) == 2 else [],
        )
        return obs

    def _evidence_check(self, requirement, source_candidate, source_accepted, stage):
        fn = self.domain.evidence_checks.get(requirement.get("evidence_type_uri"))
        if fn is None:
            return {"state": "unknown"}
        return fn(requirement, source_candidate, source_accepted, stage)

    def _lifecycle(self, record):
        b = record["body"]
        accepted = self.resolve(b["agreement_ref"])
        self.require_admitted(b["agreement_ref"])
        self.domain.typed(b["claim"])
        fn = self.domain.evidence_checks.get(b["evidence_profile_uri"])
        need(
            fn is not None and fn(record, accepted) is True,
            "unsupported_semantics",
            "claim reporter/predicate not verified",
        )
        for r in b["native_evidence_refs"]:
            self.resolve(r)

    def _action_check(self, request, accepted, candidate):
        b = request["body"]
        self.require_admitted(b["agreement_ref"])
        need(
            accepted["kind"] == "accepted_offer"
            and same_ref(accepted["body"]["candidate_ref"], content_ref(candidate)),
            "invalid_record",
            "handoff agreement",
        )
        actor = b["action_ref"]["promiser_agent_id"]
        need(
            request["issuer_agent_id"] == actor,
            "authority_absent",
            "handoff requires own action",
        )
        ps = [
            p
            for p in candidate["body"]["own_promises"]
            if p["promise_id"] == b["action_ref"]["promise_id"]
            and p["promiser_agent_id"] == actor
        ]
        need(len(ps) == 1, "invalid_record", "unknown adopted action")
        self.guards.own_promise(ps[0], actor, stage="performance")
        replacement = candidate["body"].get("replacement")
        if replacement:
            prior = replacement["accepted_offer_ref"]
            for _, slot in self.ledger.items("handoff_slots"):
                if (
                    same_ref(slot["request"]["body"]["agreement_ref"], prior)
                    and slot["dispatch_attempt_started"]
                ):
                    observation = slot.get("native_observation", {})
                    need(
                        observation.get("outcome") in ("resolved", "not_dispatched"),
                        "evidence_unavailable",
                        "replacement cannot bypass uncertain prior effect",
                    )
        meaning = self.domain.actions[ps[0]["action"]["action_type"]]
        need(
            meaning.occurrence(ps[0]["action"], b["action_instance"]) is True,
            "authority_absent",
            "unadopted occurrence/cardinality",
        )
        need(
            any(
                same_ref(r, self.enrollments[actor].principal_policy_ref)
                for r in b["authority_refs"]
            ),
            "authority_absent",
            "handoff delegated authority",
        )
        return True

    def _handoff_gate(self, request, prepared, native, now_ms):
        b = request["body"]
        accepted = self.resolve(b["agreement_ref"])
        candidate = self.resolve(accepted["body"]["candidate_ref"])
        self._action_check(request, accepted, candidate)
        status = self._status_for_composition(accepted)
        need(
            status["status"] == "refusal_windows_closed",
            "authority_absent",
            "principal recovery not cleared",
        )
        self.composition.check(
            candidate,
            "handoff",
            self.agreement_for_candidate,
            self._status_for_composition,
            self._evidence_check,
        )
        clearance = [
            content_ref(
                self.emit_profile(
                    P + "#rp1-durable-authority/recovery-observation", status
                )
            )
        ]
        dependencies = []
        for prerequisite in self.composition.dependency_agreements(
            candidate, "handoff", self.agreement_for_candidate
        ):
            observed = self._status_for_composition(prerequisite)
            need(
                observed["status"] == "refusal_windows_closed",
                "authority_absent",
                "dependency principal recovery not cleared",
            )
            dependencies.append(content_ref(prerequisite))
            clearance.append(
                content_ref(
                    self.emit_profile(
                        P + "#rp1-durable-authority/recovery-observation", observed
                    )
                )
            )
        decision = self.authorize(
            request["issuer_agent_id"],
            "dispatch_handoff",
            request,
            clearance_refs=clearance,
            dependency_refs=dependencies + b["dependency_evidence_refs"],
            native_refs=native["evidence_refs"],
            action_ref=b["action_ref"],
        )
        return {
            "allow": True,
            "valid_until_ms": milliseconds(decision["body"]["result"]["valid_until"]),
            "authorization_decision_ref": content_ref(decision),
            "gate_evidence_refs": clearance + dependencies + [content_ref(decision)],
        }

    def _option_key(self, subject):
        body = subject["body"]
        return digest(
            [
                self.recipient_scope,
                subject["issuer_agent_id"],
                body["negotiation_id"],
                body["option_id"],
            ]
        )

    def _option_is_live(self, entry):
        ref = entry["ref"]
        record = self.resolve(ref)
        return not (
            self.ledger.get("withdrawn", ref_key(ref))
            or self.ledger.get(
                "withdrawn_semantic", record["issuer_agent_id"] + "\x00" + record["id"]
            )
            or self.ledger.get("offer_disposed", ref_key(ref))
        )

    def _check_option_pool(self, subject, admission):
        """Count applied options in the recipient's selected allowance only.

        A membership survives revisions and record/proof replays. Its first
        applied pool stays pinned, so a revision cannot move to unused allowance.
        This is scope accounting inside the trusted authority, not a tenant ACL.
        """
        need(
            isinstance(admission, dict)
            and type(admission.get("max_live_options")) is int
            and admission["max_live_options"] >= 0,
            "internal_unresolved",
            "retained offer admission requires operator reconciliation",
        )
        # Older runtimes did not retain recipient/pool option memberships. Do not
        # interpret an absent index as unused allowance on an existing ledger.
        # Reconciliation is an explicit operator task, never inferred from heads.
        for _, operation in self.ledger.items("operations"):
            if not operation["terminal"] or not operation.get("admission"):
                continue
            request = self.resolve(operation["request_ref"])
            body = request["body"]
            if (
                body["recipient_scope_id"] != self.recipient_scope
                or body["purpose"] != "submit_record"
            ):
                continue
            receipt = self.resolve(operation["receipt_ref"])
            if receipt["body"]["outcome"] != "applied":
                continue
            applied = self.resolve(body["subject_ref"])
            if applied["kind"] != "offer":
                continue
            membership = self.ledger.get("admitted_options", self._option_key(applied))
            need(
                membership is not None
                and membership["pool"] == operation["admission"]["pool"],
                "internal_unresolved",
                "retained offer allowance requires operator reconciliation",
            )
        key = self._option_key(subject)
        old = self.ledger.get("admitted_options", key)
        need(
            old is None or old["pool"] == admission["pool"],
            "quota_exhausted",
            "option is bound to another allowance pool",
        )
        entry = {
            "recipient_scope_id": self.recipient_scope,
            "pool": admission["pool"],
            "ref": content_ref(subject),
            "revision": subject["body"]["revision"],
        }
        if old and old["revision"] >= entry["revision"]:
            entry = old
        live = sum(
            1
            for _, value in self.ledger.items("admitted_options")
            if value["recipient_scope_id"] == self.recipient_scope
            and value["pool"] == admission["pool"]
            and self._option_is_live(value)
        )
        adding = self._option_is_live(entry) and (
            old is None or not self._option_is_live(old)
        )
        need(
            not adding or live < admission["max_live_options"],
            "quota_exhausted",
            "live option budget",
        )
        return key, entry

    def _admission(self, request, subject, size):
        b = request["body"]
        actor = request["issuer_agent_id"]
        e = self.guards.enrollment(self.agent_id)
        policy = self.resolve(e.admission_policy_ref)
        self.verify(policy)
        self.guards.validity(policy)
        need(
            policy["recipient_agent_id"] == self.agent_id
            and policy["recipient_scope_id"] == self.recipient_scope,
            "identity_mismatch",
            "admission scope mismatch",
        )
        basis = self.resolve(b["admission_basis_ref"])
        grant = None
        if same_ref(b["admission_basis_ref"], e.admission_policy_ref):
            # Permitted bounded first contact; invitation-only publication overrides this.
            publication_ref = self.ledger.get("recipient_publication", self.agent_id)
            if publication_ref:
                publication = self.resolve(publication_ref)
                self.guards.publication(publication)
                need(
                    publication["body"]["contact"]["admission_kind"] == "first_offer"
                    or subject["kind"] in CONTROL,
                    "permission_absent",
                    "invitation required or contact closed",
                )
        elif basis.get("kind") == "admission_grant":
            grant = basis
            self.require_admitted(b["admission_basis_ref"])
            self._grant(grant)
            need(
                grant["body"]["grantee_agent_id"] == actor
                and grant["body"]["recipient_scope_id"] == self.recipient_scope,
                "permission_absent",
                "grant does not cover peer/scope",
            )
            need(
                b["purpose"] in grant["body"]["operation_purposes"],
                "permission_absent",
                "grant purpose",
            )
            if b["purpose"] == "submit_record":
                need(
                    subject["kind"] in grant["body"]["allowed_record_kinds"],
                    "permission_absent",
                    "grant record kind",
                )
            if grant["body"].get("negotiation_id"):
                need(
                    subject["body"].get("negotiation_id")
                    == grant["body"]["negotiation_id"],
                    "permission_absent",
                    "grant negotiation scope",
                )
            if grant["body"].get("origin_ref") and subject["body"].get("origin"):
                need(
                    same_ref(
                        grant["body"]["origin_ref"],
                        subject["body"]["origin"].get("record_ref"),
                    ),
                    "permission_absent",
                    "grant origin scope",
                )
        else:
            raise ProtocolError("permission_absent", "unrecognized admission basis")
        self.domain.require_ref(policy["eligibility_ref"])
        self.domain.require_ref(policy["recovery_policy_ref"])
        eligible = self.resolve(policy["eligibility_ref"])
        need(
            actor in eligible.get("agents", []),
            "permission_absent",
            "sender not policy eligible",
        )
        # Each accepted principal has a protected initial refusal independent of proposals.
        if subject["kind"] == "refusal_event" and b["purpose"] == "submit_record":
            rb = subject["body"]
            accepted = self.resolve(rb["accepted_offer_ref"])
            pe = self._principal_enrollment(accepted, rb["refusing_principal_id"])
            need(
                actor in pe.control_agents and subject["issuer_agent_id"] == actor,
                "authority_absent",
                "not principal control agent",
            )
            need(
                accepted["body"]["status_authority_agent_id"]
                == self.agent_id
                == rb["status_authority_agent_id"],
                "identity_mismatch",
                "refusal authority",
            )
            need(
                same_ref(rb["authority_ref"], pe.principal_policy_ref),
                "authority_absent",
                "refusal delegation",
            )
            key = ref_key(rb["accepted_offer_ref"]) + ":" + rb["refusing_principal_id"]
            if not self.ledger.get("refusal_reserved_used", key):
                self.ledger.put("refusal_reserved_used", key, request["id"])
                return {
                    "pool": "protected_initial_refusal",
                    "policy_ref": e.admission_policy_ref,
                }
        self._control_rate(request, subject)
        traffic = (
            "control"
            if (
                subject["kind"] in CONTROL
                or b["purpose"]
                in ("query_status", "finalize_candidate", "reconcile_handoff")
            )
            else "negotiation"
        )
        candidates = [
            p
            for p in policy["pools"]
            if p["traffic_class"] == traffic
            and b["purpose"] in p["operation_purposes"]
            and (
                b["purpose"] != "submit_record" or subject["kind"] in p["record_kinds"]
            )
        ]
        if grant:
            candidates = [
                p
                for p in candidates
                if p["allowance_id"] in grant["body"]["allowance_ids"]
            ]
        need(bool(candidates), "permission_absent", "no admitted pool")
        for pool in candidates:
            self.guards.validity(
                {"id": pool["allowance_id"], "body": {"validity": pool["validity"]}}
            )
            self.domain.require_ref(pool["work_semantics_ref"])
            work = self.resolve(pool["work_semantics_ref"])
            need(
                work.get("work_unit") == "one_bounded_transition",
                "unsupported_semantics",
                "work-cost interpretation missing",
            )
            key = self.recipient_scope + ":" + pool["allowance_id"]
            used = self.ledger.get(
                "quota", key, {"messages": 0, "bytes": 0, "work": 0, "in_flight": 0}
            )
            if not (
                used["messages"] + 1 <= pool["max_messages"]
                and used["bytes"] + size <= pool["max_bytes"]
                and used["work"] + 1 <= pool["max_work_units"]
                and used["in_flight"] + 1 <= pool["max_in_flight"]
            ):
                continue
            admission = {"pool": key, "policy_ref": e.admission_policy_ref}
            if subject["kind"] == "offer":
                admission["max_live_options"] = pool["max_live_options"]
                try:
                    self._check_option_pool(subject, admission)
                except ProtocolError as error:
                    if error.code != "quota_exhausted":
                        raise
                    continue
            used = {
                "messages": used["messages"] + 1,
                "bytes": used["bytes"] + size,
                "work": used["work"] + 1,
                "in_flight": used["in_flight"] + 1,
            }
            self.ledger.put("quota", key, used)
            return admission
        raise ProtocolError("quota_exhausted", "finite admission budget exhausted")

    def _control_rate(self, request, subject):
        actor = request["issuer_agent_id"]
        if not any(actor in e.control_agents for e in self.enrollments.values()):
            return
        if (
            subject.get("kind") != "refusal_event"
            and request["body"]["purpose"] != "query_status"
        ):
            return
        now = self.now()
        recent = [
            t for t in self.ledger.get("control_rate", actor, []) if t > now - 60_000
        ]
        need(
            len(recent) < 32,
            "quota_exhausted",
            "principal control recovery rate exceeded",
        )
        self.ledger.put("control_rate", actor, recent + [now])

    @staticmethod
    def _definitive_rejection(error):
        if getattr(error, "policy_result", None) is not None:
            return error.policy_result["allow"] is False
        if getattr(error, "policy_failure", False):
            return False
        # Unavailable/undefined/stale evidence is not proof a timely act is invalid.
        return error.code in {
            "invalid_record",
            "identity_mismatch",
            "permission_absent",
            "authority_absent",
            "operation_conflict",
            "lineage_conflict",
            "selection_conflict",
            "contact_closed",
            "quota_exhausted",
        }

    @staticmethod
    def _reason(error):
        known = {
            "permission_absent",
            "unsupported_semantics",
            "invalid_record",
            "identity_mismatch",
            "authority_absent",
            "quota_exhausted",
            "evidence_unavailable",
            "evidence_stale",
            "lineage_conflict",
            "selection_conflict",
            "operation_conflict",
            "recipient_declined",
            "contact_closed",
            "internal_unresolved",
        }
        if error.code in known:
            return error.code
        if "conflict" in error.code:
            return "selection_conflict"
        if "unsupported" in error.code:
            return "unsupported_semantics"
        if "unknown" in error.code or "unavailable" in error.code:
            return "evidence_unavailable"
        return "invalid_record"

    def _receipt(self, request, outcome, reason, results, evidence, previous=None):
        b = request["body"]
        return self.emit(
            "interaction_receipt",
            {
                "request_ref": content_ref(request),
                "operation_id": b["operation_id"],
                "recipient_agent_id": self.agent_id,
                "recipient_scope_id": self.recipient_scope,
                "revision": 1 if previous is None else previous["body"]["revision"] + 1,
                "previous_receipt_digest": None
                if previous is None
                else content_ref(previous)["digest"],
                "outcome": outcome,
                "reason_code": reason,
                "result_refs": [content_ref(v) for v in results],
                "evidence_refs": [content_ref(evidence)],
            },
            features=request["required_features"],
        )

    def invoke(self, request, records=(), peer=None):
        """Authenticated ingress records a potential refusal before proof/OPA work.

        Transport adapters supply the enrolled mTLS identity. This pre-admission
        proves arrival, not authority or refusal: failed validation resolves it as
        rejected; crashes leave it pending and prevent premature clearance.
        """
        records = tuple(records)
        size = len(canonical({"request": request, "records": list(records)}))
        need(
            size <= 1024 * 1024 and len(records) <= 64,
            "invalid_record",
            "bounded ingress exceeded",
        )
        need(
            isinstance(peer, dict)
            and peer.get("agent_id") == request.get("issuer_agent_id"),
            "identity_mismatch",
            "authenticated transport actor",
        )
        actor = peer["agent_id"]
        entry = self.registry.identities.get(actor)
        certificate = peer.get(
            "certificate_digest", peer.get("transport_certificate_digest")
        )
        reading = self.clock.read()
        need(
            entry is not None
            and certificate in entry["certificate_digests"]
            and entry["active_from_ms"] <= reading.now_ms < entry["valid_until_ms"],
            "identity_mismatch",
            "current enrolled transport identity required",
        )
        validate(request)
        need(
            request["kind"] == "interaction_request",
            "invalid_record",
            "expected interaction request",
        )
        body = request["body"]
        need(
            body["recipient_agent_id"] == self.agent_id
            and body["recipient_scope_id"] == self.recipient_scope,
            "identity_mismatch",
            "wrong recipient",
        )
        for record in records:
            self.store.put(record)
        self.store.put(request)
        self.verify(request)
        subject = self.resolve(body["subject_ref"])
        validate(subject)
        ingress = None
        if body["purpose"] == "submit_record" and subject["kind"] == "refusal_event":
            rb = subject["body"]
            accepted = self.resolve(rb["accepted_offer_ref"])
            self.require_admitted(rb["accepted_offer_ref"])
            e = self._principal_enrollment(accepted, rb["refusing_principal_id"])
            # A valid transport principal can hold only its own protected path.
            eligible = (
                actor in e.control_agents
                and subject["issuer_agent_id"] == actor
                and accepted["body"]["status_authority_agent_id"]
                == self.agent_id
                == rb["status_authority_agent_id"]
                and same_ref(rb["authority_ref"], e.principal_policy_ref)
            )
            if eligible:
                with self.ledger.transaction():
                    key = digest([self.recipient_scope, actor, body["operation_id"]])
                    saved = self.ledger.get("operations", key)
                    incoming = unsigned_digest(request)
                    prior_ingress = self.ledger.get("refusal_ingress", key)
                    need(
                        prior_ingress is None
                        or prior_ingress["unsigned_digest"] == incoming,
                        "operation_conflict",
                        "refusal ingress identity reused",
                    )
                    semantic = self.ledger.get(
                        "semantic_refs", actor + "\x00" + subject["id"]
                    )
                    recent = [
                        t
                        for t in self.ledger.get("control_rate", actor, [])
                        if t > reading.now_ms - 60_000
                    ]
                    first = not self.ledger.get(
                        "refusal_reserved_used",
                        ref_key(rb["accepted_offer_ref"])
                        + ":"
                        + rb["refusing_principal_id"],
                    )
                    if (
                        not semantic
                        and (not saved or not saved["terminal"])
                        and (first or len(recent) < 32)
                    ):
                        op = (self.recipient_scope, actor, body["operation_id"])
                        self.recovery.admit_refusal(
                            rb["accepted_offer_ref"],
                            principal_id=rb["refusing_principal_id"],
                            operation_key=op,
                            request_digest=unsigned_digest(subject),
                            peer_agent_id=actor,
                            admitted_lower_ms=reading.now_ms - reading.uncertainty_ms,
                            admitted_upper_ms=reading.now_ms + reading.uncertainty_ms,
                        )
                        self.ledger.put(
                            "refusal_ingress",
                            key,
                            prior_ingress
                            or {
                                "unsigned_digest": incoming,
                                "request_ref": content_ref(request),
                            },
                        )
                        ingress = (rb["accepted_offer_ref"], op)
        try:
            result = self._invoke(request, records, peer)
        except ProtocolError as error:
            if ingress and self._definitive_rejection(error):
                with self.ledger.transaction():
                    self.recovery.reject_refusal(
                        ingress[0],
                        operation_key=ingress[1],
                        reason=self._reason(error),
                        evidence_ref=content_ref(request),
                    )
            raise
        if ingress and result["body"]["outcome"] not in ("applied", "pending"):
            with self.ledger.transaction():
                self.recovery.reject_refusal(
                    ingress[0],
                    operation_key=ingress[1],
                    reason=result["body"]["reason_code"],
                    evidence_ref=content_ref(request),
                )
        return result

    def _invoke(self, request, records=(), peer=None):
        """C3 entry from a verified transport adapter; returns the exact durable receipt.

        Local test drivers explicitly supply pre-enrolled peer identity. Production
        callers obtain peer from transport.make_handler's mutual TLS verification.
        """
        size = len(canonical({"request": request, "records": list(records)}))
        need(
            size <= 1024 * 1024 and len(records) <= 64,
            "invalid_record",
            "bounded ingress exceeded",
        )
        need(
            peer is not None and peer["agent_id"] == request.get("issuer_agent_id"),
            "identity_mismatch",
            "authenticated transport actor",
        )
        certificate = peer.get(
            "certificate_digest", peer.get("transport_certificate_digest")
        )
        need(
            isinstance(certificate, str) and certificate.startswith("sha256:"),
            "identity_mismatch",
            "transport certificate binding absent",
        )
        identity = self.registry.identities.get(peer["agent_id"])
        need(
            identity is not None and certificate in identity["certificate_digests"],
            "identity_mismatch",
            "transport certificate not enrolled for actor",
        )
        # Materialization is not submission. Extra records never execute transitions.
        for record in records:
            self.store.put(record)
        self.store.put(request)
        self.verify(request)
        need(
            request["kind"] == "interaction_request",
            "invalid_record",
            "expected one interaction request",
        )
        b = request["body"]
        need(
            b["recipient_agent_id"] == self.agent_id
            and b["recipient_scope_id"] == self.recipient_scope,
            "identity_mismatch",
            "wrong recipient",
        )
        self.ledger.put("transport_identity", request["issuer_agent_id"], certificate)
        key = digest(
            [self.recipient_scope, request["issuer_agent_id"], b["operation_id"]]
        )
        ud = unsigned_digest(request)
        subject = self.resolve(b["subject_ref"])
        validate(subject)
        need("kind" in subject, "invalid_record", "subject must be a semantic record")
        expected = {
            "finalize_candidate": "candidate_terms",
            "query_status": "accepted_offer",
            "prepare_handoff": "handoff_request",
            "dispatch_handoff": "handoff_request",
            "reconcile_handoff": "handoff_request",
        }
        need(
            b["purpose"] not in expected or subject["kind"] == expected[b["purpose"]],
            "invalid_record",
            "subject does not match purpose",
        )
        if b["purpose"] == "submit_record":
            need(
                subject["kind"]
                not in (
                    "interaction_request",
                    "interaction_receipt",
                    "admission_policy_declaration",
                ),
                "invalid_record",
                "not a submittable semantic subject",
            )
        required = set(subject.get("required_features", [])) | self.features_for(
            subject["kind"], subject.get("body", {})
        )
        need(
            required <= set(request["required_features"]),
            "unsupported_semantics",
            "interaction hides subject feature",
        )
        # Refusal admission occurs before expensive semantic work, in the durable pending boundary.
        with self.ledger.transaction():
            saved = self.ledger.get("operations", key)
            if saved:
                evidence = self.authorize(
                    request["issuer_agent_id"],
                    "read_evidence",
                    self.resolve(saved["request_ref"]),
                )
                self._control_rate(request, subject)
                if saved["unsigned_digest"] != ud:
                    conflict_key = key + ":" + ud
                    old = self.ledger.get("operation_conflicts", conflict_key)
                    if old:
                        return self.resolve(old)
                    receipt = self._receipt(
                        request, "conflict", "operation_conflict", [], evidence
                    )
                    self.ledger.put(
                        "operation_conflicts", conflict_key, content_ref(receipt)
                    )
                    return receipt
                if saved["terminal"]:
                    return self.resolve(saved["receipt_ref"])
                original = self.resolve(saved["request_ref"])
                request = original
                b = original["body"]
                subject = self.resolve(b["subject_ref"])
            else:
                self.verify(subject)
                ingress_act = (
                    "prepare_handoff"
                    if b["purpose"] == "dispatch_handoff"
                    else b["purpose"]
                )
                evidence = self.authorize(
                    request["issuer_agent_id"], ingress_act, subject
                )
                try:
                    admission = self._admission(request, subject, size)
                except ProtocolError as error:
                    if subject[
                        "kind"
                    ] == "refusal_event" and not self._definitive_rejection(error):
                        raise
                    receipt = self._receipt(
                        request, "blocked", self._reason(error), [], evidence
                    )
                    self.ledger.put(
                        "operations",
                        key,
                        {
                            "request_ref": content_ref(request),
                            "unsigned_digest": ud,
                            "receipt_ref": content_ref(receipt),
                            "terminal": True,
                            "admission": None,
                        },
                    )
                    return receipt
                receipt = self._receipt(request, "pending", "in_progress", [], evidence)
                saved = {
                    "request_ref": content_ref(request),
                    "unsigned_digest": ud,
                    "receipt_ref": content_ref(receipt),
                    "terminal": False,
                    "admission": admission,
                }
                self.ledger.put("operations", key, saved)
                if (
                    subject["kind"] == "refusal_event"
                    and b["purpose"] == "submit_record"
                    and not self.ledger.get(
                        "semantic_refs",
                        subject["issuer_agent_id"] + "\x00" + subject["id"],
                    )
                ):
                    rb = subject["body"]
                    reading = self.clock.read()
                    self.recovery.admit_refusal(
                        rb["accepted_offer_ref"],
                        principal_id=rb["refusing_principal_id"],
                        operation_key=(
                            self.recipient_scope,
                            request["issuer_agent_id"],
                            b["operation_id"],
                        ),
                        request_digest=unsigned_digest(subject),
                        peer_agent_id=request["issuer_agent_id"],
                        admitted_lower_ms=reading.now_ms - reading.uncertainty_ms,
                        admitted_upper_ms=reading.now_ms + reading.uncertainty_ms,
                    )
        self.failpoint("after_operation_admission")
        if b["purpose"] in ("prepare_handoff", "dispatch_handoff", "reconcile_handoff"):
            # C8 commits its marker before external calls. Never nest Dispatch under this receipt transaction.
            try:
                self.verify(subject)
                if b["purpose"] == "prepare_handoff":
                    result = self.handoff.prepare(subject)["receipt"]
                elif b["purpose"] == "dispatch_handoff":
                    result = self.handoff.dispatch(subject)
                else:
                    result = self.handoff.reconcile(subject)
                outcome, reason = "applied", "ok"
            except ProtocolError as error:
                result = None
                outcome, reason = "blocked", self._reason(error)
            with self.ledger.transaction():
                return self._finish(key, request, result, outcome, reason)
        with self.ledger.transaction():
            # Another worker may have completed the pending request while we waited.
            current = self.ledger.get("operations", key)
            if current["terminal"]:
                return self.resolve(current["receipt_ref"])
            try:
                with self.ledger.transaction():
                    self.verify(subject)
                    if b["purpose"] == "submit_record":
                        self.authorize(
                            request["issuer_agent_id"], "submit_record", subject
                        )
                        if subject["kind"] == "refusal_event":
                            result = self._refuse(
                                subject,
                                (
                                    self.recipient_scope,
                                    request["issuer_agent_id"],
                                    b["operation_id"],
                                ),
                            )
                            self.store.admit_identity(subject)
                        else:
                            result = self._apply(subject)
                            if subject["kind"] == "offer":
                                # Recheck under the same serialized commit as the
                                # semantic effect. Pending/invalid requests own no
                                # live-option slot and cannot overbook this pool.
                                option_key, membership = self._check_option_pool(
                                    result, current["admission"]
                                )
                                self.ledger.put(
                                    "admitted_options", option_key, membership
                                )
                    elif b["purpose"] == "finalize_candidate":
                        result = self.finalize(
                            b["subject_ref"], caller=request["issuer_agent_id"]
                        )
                    elif b["purpose"] == "query_status":
                        result = self.status(
                            b["subject_ref"], caller=request["issuer_agent_id"]
                        )
                    else:
                        raise ProtocolError("unsupported_semantics", "unknown purpose")
                outcome, reason = "applied", "ok"
            except ProtocolError as error:
                self._preserve_conflict(error)
                result = None
                reason = self._reason(error)
                outcome = "conflict" if "conflict" in reason else "blocked"
                if subject["kind"] == "refusal_event":
                    if not self._definitive_rejection(error):
                        return self.resolve(current["receipt_ref"])
                    self.recovery.reject_refusal(
                        subject["body"]["accepted_offer_ref"],
                        operation_key=(
                            self.recipient_scope,
                            request["issuer_agent_id"],
                            b["operation_id"],
                        ),
                        reason=reason,
                        evidence_ref=content_ref(request),
                    )
            return self._finish(key, request, result, outcome, reason)

    def _finish(self, key, request, result, outcome, reason):
        saved = self.ledger.get("operations", key)
        if saved["terminal"]:
            return self.resolve(saved["receipt_ref"])
        previous = self.resolve(saved["receipt_ref"])
        evidence = self.emit_profile(
            P + "#rp1-durable-authority/operation-outcome",
            {
                "operation_key": key,
                "request_ref": saved["request_ref"],
                "outcome": outcome,
                "reason_code": reason,
                "authority_revision": self.ledger.revision,
            },
        )
        receipt = self._receipt(
            request, outcome, reason, [result] if result else [], evidence, previous
        )
        admission = saved["admission"]
        if admission and admission["pool"] != "protected_initial_refusal":
            used = self.ledger.get("quota", admission["pool"])
            used["in_flight"] = max(0, used["in_flight"] - 1)
            self.ledger.put("quota", admission["pool"], used)
        saved.update(receipt_ref=content_ref(receipt), terminal=True)
        self.ledger.put("operations", key, saved)
        self.failpoint("before_operation_result_commit")
        return receipt
