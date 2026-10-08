"""Semantic guards layered above structural and cryptographic verification."""

from datetime import datetime, timezone
from .crypto import content_ref
from .errors import ProtocolError
from .records import ref_key, same_ref


def timestamp(ms):
    return (
        datetime.fromtimestamp(ms / 1000, timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def milliseconds(value):
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def need(condition, code, detail):
    if not condition:
        raise ProtocolError(code, detail)


class Guards:
    def __init__(self, harness):
        self.h = harness

    def enrollment(self, agent):
        e = self.h.enrollments.get(agent)
        need(
            e is not None and e.active,
            "authority_absent",
            "agent lacks current enrollment",
        )
        need(
            e.authority_scope_id == self.h.authority_scope,
            "authority_absent",
            "incompatible authority domain",
        )
        return e

    def validity(self, record):
        ref = content_ref(record)
        identity = record.get("issuer_agent_id", "") + "\x00" + record.get("id", "")
        need(
            not self.h.ledger.get("withdrawn", ref_key(ref))
            and not self.h.ledger.get("withdrawn_semantic", identity),
            "authority_absent",
            "record withdrawn",
        )
        value = record.get("body", record).get("validity")
        if value:
            self.h.domain.require_ref(value["policy_ref"])
            if value["mode"] == "expires_at":
                need(
                    self.h.now() + self.h.clock.read().uncertainty_ms
                    <= milliseconds(value["expires_at"]),
                    "evidence_stale",
                    "validity expired",
                )
            elif value["mode"] != "until_withdrawn":
                raise ProtocolError(
                    "unsupported_semantics",
                    "policy-defined validity needs a registered implementation",
                )
        return True

    def origin(self, origin, candidate=None):
        source = self.h.resolve(origin["record_ref"])
        self.h.require_admitted(origin["record_ref"])
        need(
            source["kind"] == origin["record_kind"]
            and source["kind"] in ("intent", "promise", "offer"),
            "invalid_record",
            "origin kind mismatch",
        )
        need(
            source["issuer_agent_id"]
            == origin["originator_agent_id"]
            == origin["coordinator_agent_id"],
            "identity_mismatch",
            "coordinator must be origin author",
        )
        need(
            source["issuer_principal_id"] == origin["originator_principal_id"],
            "identity_mismatch",
            "origin principal mismatch",
        )
        self.validity(source)
        if candidate:
            need(
                origin["coordinator_agent_id"]
                in [p["agent_id"] for p in candidate["body"]["participants"]],
                "identity_mismatch",
                "coordinator not a participant",
            )
        return source

    def own_promise(self, promise, issuer=None, stage="issuance"):
        actor = promise["promiser_agent_id"]
        e = self.enrollment(actor)
        if issuer is not None:
            need(
                actor == issuer,
                "identity_mismatch",
                "cannot issue another actor promise",
            )
        action = promise["action"]
        self.h.domain.validate_action(action)
        need(
            action["action_type"] in e.action_types,
            "authority_absent",
            "action outside delegated scope",
        )
        need(
            any(same_ref(r, e.principal_policy_ref) for r in promise["authority_refs"]),
            "authority_absent",
            "missing principal delegation",
        )
        need(
            all(
                any(same_ref(r, c) for c in e.capability_refs)
                for r in promise["capability_refs"]
            ),
            "authority_absent",
            "unapproved capability evidence",
        )
        for r in promise["authority_refs"] + promise["capability_refs"]:
            self.h.domain.require_ref(r)
            self.h.resolve(r)
        for condition in promise["qualifications"]:
            predicate = self.h.domain.qualification_checks.get(condition["type_uri"])
            need(
                predicate is not None and predicate(promise, stage) is True,
                "unsupported_semantics",
                "qualification phase/evidence not established",
            )
        for v in promise["qualifications"] + [action["subject"]] + action["resources"]:
            self.h.domain.typed(v)
        self.validity(
            {"id": promise["promise_id"], "body": {"validity": promise["validity"]}}
        )

    def publication(self, record):
        e = self.enrollment(record["issuer_agent_id"])
        b = record["body"]
        need(
            same_ref(b["principal_policy_ref"], e.principal_policy_ref),
            "authority_absent",
            "publication delegation mismatch",
        )
        need(
            same_ref(b["contact"]["admission_policy_ref"], e.admission_policy_ref),
            "authority_absent",
            "publication admission mismatch",
        )
        for r in (
            b["discovery"]["distribution_policy_ref"],
            b["transaction_policy_ref"],
        ):
            self.h.domain.require_ref(r)
        self.validity(record)

    def publication_refs(self, refs, agents):
        publications = [self.h.resolve(r) for r in refs]
        need(
            {p["issuer_agent_id"] for p in publications} == set(agents)
            and len(publications) == len(set(agents)),
            "identity_mismatch",
            "publication coverage mismatch",
        )
        for r, p in zip(refs, publications):
            self.h.require_admitted(r)
            need(
                p["kind"] == "publication_contract",
                "invalid_record",
                "not a publication",
            )
            self.publication(p)
            self.h.require_head(p)

    def offer(self, record):
        b = record["body"]
        actor = record["issuer_agent_id"]
        if b["origin"].get("self_origin"):
            o = b["origin"]
            need(
                o["record_id"] == record["id"]
                and o["originator_agent_id"] == actor == o["coordinator_agent_id"]
                and o["originator_principal_id"] == record["issuer_principal_id"],
                "identity_mismatch",
                "invalid self-origin",
            )
        else:
            self.origin(b["origin"])
        agents = [
            self.h.resolve(r)["issuer_agent_id"] for r in b["publication_contract_refs"]
        ]
        need(actor in agents, "identity_mismatch", "offer author missing publication")
        self.publication_refs(b["publication_contract_refs"], agents)
        for promise in b["own_promises"]:
            self.own_promise(promise, actor)
            need(
                set(promise["promisee_ids"]) <= set(agents),
                "identity_mismatch",
                "promisee outside negotiation",
            )
        for request in b["requested_counterpromises"]:
            need(
                request["requested_of_agent_id"] in agents
                and request["requested_of_agent_id"] != actor,
                "identity_mismatch",
                "counterpromise target",
            )
            self.h.domain.validate_action(request["action"])
            for q in request["qualifications"]:
                self.h.domain.typed(q)
        self.terms(b, record)
        self.h.domain.require_ref(b["selection_constraints_ref"])
        need(
            ref_key(b["selection_constraints_ref"]) in self.h.domain.selection,
            "unsupported_semantics",
            "selection semantics unavailable",
        )
        self.validity(record)

    def terms(self, b, record):
        terms = b["agreement_terms"]
        fn = self.h.domain.agreement_checks.get(terms["profile_uri"])
        need(
            fn is not None and fn(terms) is True,
            "unsupported_semantics",
            "agreement terms not understood/permitted",
        )
        for r in terms["policy_refs"] + [b["privacy_policy_ref"]]:
            self.h.domain.require_ref(r)
        if b["route_selections"]:
            predicate = self.h.domain.arrangement_checks.get(terms["profile_uri"])
            publications = [self.h.resolve(r) for r in b["publication_contract_refs"]]
            need(
                predicate is not None and predicate(record, publications) is True,
                "unsupported_semantics",
                "complete commercial arrangement not established under both principal policies",
            )
        # Route meaning is explicitly registered; no native route translator is implied.
        for route in b["route_selections"]:
            need(
                route["profile_uri"] in self.h.domain.understood_uris,
                "unsupported_semantics",
                "unknown route",
            )
            for r in route["policy_refs"]:
                self.h.domain.require_ref(r)

    def candidate(self, record, stage="issuance"):
        b = record["body"]
        participants = b["participants"]
        agents = [p["agent_id"] for p in participants]
        need(
            len(set(agents)) == 2 and record["id"] == b["candidate_id"],
            "invalid_record",
            "candidate identity/participants",
        )
        self.origin(b["origin"], record)
        need(
            record["issuer_agent_id"] == b["origin"]["coordinator_agent_id"],
            "identity_mismatch",
            "candidate distribution belongs to coordinator",
        )
        for p in participants:
            e = self.enrollment(p["agent_id"])
            need(
                e.principal_id == p["principal_id"],
                "identity_mismatch",
                "principal binding",
            )
            need(
                set(record["required_features"]) <= e.features,
                "unsupported_semantics",
                "participant lacks required feature",
            )
        self.publication_refs(b["publication_contract_refs"], agents)
        self.terms(b, record)
        selected = {}
        for option in b["selected_options"]:
            offer = self.h.resolve(option["offer_ref"])
            self.h.require_admitted(option["offer_ref"])
            need(
                offer["kind"] == "offer",
                "invalid_record",
                "selected object is not an offer",
            )
            self.offer(offer)
            self.h.require_head(offer)
            need(
                offer["issuer_agent_id"] == option["agent_id"] in agents
                and offer["body"]["option_id"] == option["option_id"],
                "identity_mismatch",
                "selected option mismatch",
            )
            need(
                offer["body"]["negotiation_id"] == b["negotiation_id"],
                "invalid_record",
                "mixed negotiations",
            )
            need(
                same_ref(
                    offer["body"]["selection_constraints_ref"],
                    option["selection_constraints_ref"],
                ),
                "invalid_record",
                "selection policy changed",
            )
            need(
                offer["body"]["agreement_terms"] == b["agreement_terms"]
                and offer["body"]["route_selections"] == b["route_selections"],
                "invalid_record",
                "spliced agreement terms",
            )
            selected[ref_key(option["offer_ref"])] = offer
        selected_constraints = {
            ref_key(o["selection_constraints_ref"]) for o in b["selected_options"]
        }
        aggregate_constraints = {ref_key(r) for r in b["selection_constraints_refs"]}
        need(
            selected_constraints <= aggregate_constraints
            and len(aggregate_constraints) == len(b["selection_constraints_refs"]),
            "invalid_record",
            "selected capacity constraints omitted or duplicated",
        )
        if any(o["body"]["requested_counterpromises"] for o in selected.values()):
            predicate = self.h.domain.candidate_checks.get(
                b["agreement_terms"]["profile_uri"]
            )
            need(
                predicate is not None
                and predicate(record, list(selected.values())) is True,
                "unsupported_semantics",
                "requested actions require complete option reconciliation",
            )
        need(
            len({(p["promiser_agent_id"], p["promise_id"]) for p in b["own_promises"]})
            == len(b["own_promises"]),
            "invalid_record",
            "duplicate action",
        )
        promises = {
            (p["promiser_agent_id"], p["promise_id"]): p for p in b["own_promises"]
        }
        bindings = {
            (p["promiser_agent_id"], p["promise_id"]): p for p in b["promise_bindings"]
        }
        need(
            len(bindings) == len(b["promise_bindings"])
            and promises.keys() == bindings.keys(),
            "invalid_record",
            "incomplete action provenance",
        )
        for key, p in promises.items():
            need(
                key[0] in agents and set(p["promisee_ids"]) <= set(agents),
                "identity_mismatch",
                "foreign promise in candidate",
            )
            self.own_promise(p, stage=stage)
            binding = bindings[key]
            if binding["basis"] == "previously_issued":
                source = self.h.resolve(binding["source_ref"])
                self.h.require_admitted(binding["source_ref"])
                need(
                    source["issuer_agent_id"] == key[0],
                    "identity_mismatch",
                    "source does not issue actor promise",
                )
                need(
                    source["kind"] == "promise"
                    or ref_key(binding["source_ref"]) in selected,
                    "invalid_record",
                    "unselected offer provenance",
                )
                self.validity(source)
                if source["kind"] == "promise":
                    publication = self.h.resolve(
                        source["body"]["publication_contract_ref"]
                    )
                    self.publication(publication)
                    self.h.require_head(publication)
                choices = (
                    [source["body"]["own_promise"]]
                    if source["kind"] == "promise"
                    else source["body"]["own_promises"]
                )
                matched = [
                    v
                    for v in choices
                    if v["promise_id"] == binding["source_promise_id"]
                ]
                need(
                    len(matched) == 1 and matched[0] == p,
                    "invalid_record",
                    "changed sourced promise",
                )
            elif "request_source" in binding:
                src = binding["request_source"]
                offer = self.h.resolve(src["offer_ref"])
                need(
                    ref_key(src["offer_ref"]) in selected,
                    "invalid_record",
                    "unselected request source",
                )
                req = [
                    v
                    for v in offer["body"]["requested_counterpromises"]
                    if v["request_id"] == src["request_id"]
                ]
                need(
                    len(req) == 1 and req[0]["requested_of_agent_id"] == key[0],
                    "identity_mismatch",
                    "request provenance",
                )
        # A selected offer is complete: no disappearing condition or substantive own action.
        for source in selected.values():
            for p in source["body"]["own_promises"]:
                need(
                    promises.get((p["promiser_agent_id"], p["promise_id"])) == p,
                    "invalid_record",
                    "selected offer action omitted",
                )
        principals = {p["principal_id"] for p in participants}
        windows = b["principal_refusal_windows"]
        need(
            len(windows) == len(principals)
            and {w["principal_id"] for w in windows} == principals,
            "invalid_record",
            "principal recovery coverage",
        )
        for w in windows:
            applicable = [
                self.enrollment(p["agent_id"])
                for p in participants
                if p["principal_id"] == w["principal_id"]
            ]
            for e in applicable:
                need(
                    w["duration_ms"] == e.refusal_duration_ms > 0,
                    "authority_absent",
                    "recovery duration not approved",
                )
                for field in (
                    "notice_target_ref",
                    "notice_profile_ref",
                    "refusal_mechanism_ref",
                ):
                    need(
                        same_ref(w[field], getattr(e, field)),
                        "authority_absent",
                        "principal channel/rule mismatch",
                    )
                need(
                    same_ref(w["principal_policy_ref"], e.principal_policy_ref)
                    and same_ref(w["refusal_authority_ref"], e.principal_policy_ref),
                    "authority_absent",
                    "refusal authority changed",
                )
        for r in b["selection_constraints_refs"] + [
            b["clock_profile_ref"],
            b["status_policy_ref"],
            b["handoff_rules"]["policy_ref"],
        ]:
            self.h.domain.require_ref(r)
        need(
            b["handoff_rules"]["preclearance"] == "no_effects",
            "unsupported_semantics",
            "RP1 excludes early effects",
        )
        need(
            b["status_authority_agent_id"] == b["origin"]["coordinator_agent_id"],
            "unsupported_semantics",
            "runtime requires coordinator-local status authority",
        )
        if "replacement" in b:
            # Do not infer cancellation/release; application must attest and authorize disposition.
            self.h.domain.require_ref(b["replacement"]["disposition_ref"])
            self.h.resolve(b["replacement"]["accepted_offer_ref"])
        if "composition" in b:
            self.h.composition.validate_candidate(record, require_binding=False)
        self.validity(record)

    def adoption(self, record):
        b = record["body"]
        candidate = self.h.resolve(b["candidate_ref"])
        self.h.require_admitted(b["candidate_ref"])
        self.candidate(candidate, stage="adoption")
        self.h.composition.validate_candidate(candidate, require_binding=True)
        actor = record["issuer_agent_id"]
        agents = [p["agent_id"] for p in candidate["body"]["participants"]]
        need(
            actor in agents and b["origin"] == candidate["body"]["origin"],
            "identity_mismatch",
            "adoption actor/origin",
        )
        need(
            set(record["required_features"]) == set(candidate["required_features"]),
            "unsupported_semantics",
            "adoption omits candidate feature",
        )
        needed = {
            p["promise_id"]
            for p in candidate["body"]["own_promises"]
            if p["promiser_agent_id"] == actor
        }
        need(
            set(b["adopted_own_promise_ids"]) == needed,
            "invalid_record",
            "adoption does not cover own promises",
        )
        e = self.enrollment(actor)
        need(
            any(same_ref(r, e.principal_policy_ref) for r in b["authority_refs"]),
            "authority_absent",
            "adoption delegation absent",
        )
        for key in (
            "authority_refs",
            "capability_status_refs",
            "policy_status_refs",
            "selection_status_refs",
        ):
            for r in b[key]:
                self.h.domain.require_ref(r)
                self.h.resolve(r)
        self.validity(record)
        return candidate
