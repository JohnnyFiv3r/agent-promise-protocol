"""Executable, explicitly simulated research domain for the reference runtime.

Every protocol record is freshly signed with Ed25519 and content-addressed.
The enrolled policies, capability definitions, local peer identities, service
health, clock and native adapter are controlled fixtures, not external claims.
No network service, researcher, inbox, payment or native order is contacted.
"""

from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from .clock import ControlledClock
from .crypto import Signer, Registry, content_ref, digest, KINDS
from .domain import Domain, Enrollment, ActionMeaning
from .errors import ProtocolError
from .guards import timestamp
from .handoff import FakeAdapter
from .harness import Harness, P, PROFILE, FEATURES
from .policy import TestPolicy, ACTS
from .records import RecordStore, ref_key
from .schema import validate
from .storage import Ledger


U = "urn:agent-bazaar:controlled-research:"
AUTHORITY = U + "authority"
START_MS = 1_791_484_800_000
DURATION_MS = 100
PARTICIPANTS = ("requester", "researcher", "reviewer")


class Environment:
    """An independently enrolled local realm, with three negotiating actors.

    ``restart`` reconnects the authority ledger while retaining this fixture's
    enrollment keys and simulated native observations. A new Environment must
    use a fresh directory; no private keys are written to the artifact directory.
    """

    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "authority.sqlite"
        if self.path.exists():
            raise FileExistsError(
                "Use a fresh fixture directory, or Environment.restart()"
            )
        self.ledger = Ledger(self.path)
        self.store = RecordStore(self.ledger)
        self.records = {}
        self.requests = {}
        self.receipts = []
        self.domain = Domain()
        self.registry = Registry()
        self.signers = {}
        self.enrollments = {}
        self.publications = {}
        self._health_ends = {}
        self._serial = 0

        for name in PARTICIPANTS:
            for alias in (name, name + "_control"):
                signer = Signer("agent:" + alias, "principal:" + name)
                self.signers[alias] = signer
                certificate = digest({"simulated_mtls_peer": signer.agent_id})
                self.registry.register(
                    signer,
                    features=FEATURES,
                    roles=("principal-control",)
                    if alias.endswith("_control")
                    else ("agent", "notice"),
                    certificate_digests=[certificate],
                )
                self.ledger.put("transport_identity", signer.agent_id, certificate)

        self.clock_ref = self.document(
            "controlled-clock",
            {"mechanism": "deterministic-test-clock", "external_nts": False},
        )
        self.clock = ControlledClock(START_MS, self.clock_ref)
        self.clock_policy = self.document(
            "clock-policy",
            {
                "max_uncertainty_ms": 1000,
                "outage_rule": "credit_only_verified_usable_time",
            },
        )
        self.privacy_ref = self.document(
            "privacy", {"audience": "controlled-fixture-only"}
        )
        self.distribution_ref = self.document(
            "distribution", {"audiences": ["fixture:research"]}
        )
        self.commercial_ref = self.document("commercial", {"consideration": "none"})
        self.notice_profile = self.document(
            "notice-profile", {"mechanism": "simulated-durable-inbox"}
        )
        self.refusal_mechanism = self.document(
            "refusal-mechanism", {"mechanism": "separate-principal-control"}
        )
        self.adapter_contract = self.document(
            "adapter-contract",
            {
                "mechanism": "FakeAdapter",
                "native_effects": "in-memory-simulation-only",
                "preclearance": "no_effects",
                "automatic_redelivery": False,
            },
        )
        self.work_ref = self.document(
            "bounded-work", {"work_unit": "one_bounded_transition"}
        )
        self.eligibility_ref = self.document(
            "eligible-agents", {"agents": [s.agent_id for s in self.signers.values()]}
        )
        self.recovery_policy = self.document(
            "admission-recovery", {"first_refusal_reserved": True}
        )
        self.policy_bundle = self.document(
            "explicit-test-policy", {"engine": "TestPolicy", "opa_fallback": False}
        )
        self.policy_data = self.document(
            "owner-approved-fixture-data", {"authority_scope_id": AUTHORITY}
        )
        self.semantics_ref = self.document(
            "research-meanings",
            {
                "actions": ["declare_interest", "produce_report", "review_report"],
                "cardinality": "one exact report occurrence per adopted action",
            },
        )
        self.domain.understood_uris.update(
            {U + "report", U + "one-report", U + "component"}
        )
        for action_name in ("declare_interest", "produce_report", "review_report"):
            self.domain.actions[U + action_name] = ActionMeaning(
                self.semantics_ref, self._valid_action, self._valid_occurrence
            )
        self.domain.agreement_checks[U + "no-consideration"] = lambda terms: (
            set(terms["terms"]) == {"consideration", "report_id"}
            and terms["terms"]["consideration"] == "none"
            and isinstance(terms["terms"]["report_id"], str)
            and bool(terms["terms"]["report_id"])
        )
        self.domain.requirement_checks[U + "component"] = (
            lambda requirement, candidate, plan: (
                candidate["body"]["agreement_terms"]["terms"]["report_id"]
                == requirement["parameters"].get("report_id")
            )
        )
        self.domain.health_checks[ref_key(self.notice_profile)] = (
            lambda evidence, descriptor, reading: (
                evidence["body"]["service_evidence_refs"]
                == [
                    descriptor["notice_target_ref"],
                    descriptor["refusal_mechanism_ref"],
                ]
                and evidence["body"].get("continuity_evidence_ref") == self.clock_ref
                and evidence["body"].get("monotonic_elapsed_ms")
                == evidence["body"]["interval_end_ms"]
                - evidence["body"]["interval_start_ms"]
                and 0
                <= evidence["body"]["interval_start_ms"]
                < evidence["body"]["interval_end_ms"]
                <= reading.now_ms
            )
        )

        self.principal_policies = {}
        self.capabilities = {}
        self.notice_targets = {}
        self.selections = {}
        for name in PARTICIPANTS:
            self.principal_policies[name] = self.document(
                name + "-principal-policy",
                {
                    "principal_id": "principal:" + name,
                    "refusal_duration_ms": DURATION_MS,
                    "refusal_agents": ["agent:" + name + "_control"],
                    "authority_scope_id": AUTHORITY,
                },
            )
            self.notice_targets[name] = self.document(
                name + "-notice-target",
                {
                    "principal_id": "principal:" + name,
                    "inbox": "fixture://inbox/" + name,
                },
            )
            self.capabilities[name] = self.document(
                name + "-capability",
                {
                    "agent_id": "agent:" + name,
                    "mechanism": "controlled-research-domain",
                    "real_performance_qualified": False,
                },
            )
            self.selections[name] = self.document(
                name + "-selection", {"resource": "research-slots:" + name, "units": 1}
            )
            self.domain.selection[ref_key(self.selections[name])] = {
                "resources": {"research-slots:" + name: 1}
            }
            self.ledger.put(
                "resource_limits",
                "research-slots:" + name,
                {"scope": AUTHORITY, "limit": 8},
            )

        admission_refs = {}
        for alias in self.signers:
            owner = alias.removesuffix("_control")
            admission_refs[alias] = content_ref(self._admission_policy(alias, owner))
            self.enrollments[self.signers[alias].agent_id] = Enrollment(
                principal_id="principal:" + owner,
                principal_policy_ref=self.principal_policies[owner],
                capability_refs=[self.capabilities[owner]],
                action_types=set()
                if alias.endswith("_control")
                else set(self.domain.actions),
                features=set(FEATURES),
                admission_policy_ref=admission_refs[alias],
                refusal_duration_ms=DURATION_MS,
                notice_target_ref=self.notice_targets[owner],
                notice_profile_ref=self.notice_profile,
                refusal_mechanism_ref=self.refusal_mechanism,
                control_agents={"agent:" + owner + "_control"},
                notice_agent_id="agent:requester",
                authority_scope_id=AUTHORITY,
            )

        self.policy = TestPolicy(
            policy_bundle_ref=self.policy_bundle,
            policy_data_ref=self.policy_data,
            grants=[
                {
                    "agent_id": signer.agent_id,
                    "principal_id": signer.principal_id,
                    "acts": ["submit_record", "query_status", "read_evidence"]
                    if alias.endswith("_control")
                    else sorted(ACTS),
                    "subject_kinds": [
                        "refusal_event",
                        "accepted_offer",
                        "interaction_request",
                    ]
                    if alias.endswith("_control")
                    else sorted(KINDS),
                    "authority_scope_id": AUTHORITY,
                    "recipient_scope_ids": [self.scope(name) for name in self.signers],
                }
                for alias, signer in self.signers.items()
            ],
        )
        self.adapter = FakeAdapter(contract_ref=self.adapter_contract)
        self._build_harnesses()
        for alias in PARTICIPANTS:
            publication = self.emit(
                alias,
                "publication_contract",
                {
                    "contract_id": "publication:" + alias,
                    "revision": 1,
                    "previous_digest": None,
                    "validity": self.validity(alias),
                    "principal_policy_ref": self.principal_policies[alias],
                    "discovery": {
                        "audiences": ["fixture:research"],
                        "permitted_uses": ["index", "match"],
                        "distribution_policy_ref": self.distribution_ref,
                    },
                    "contact": {
                        "admission_kind": "first_offer",
                        "admission_policy_ref": admission_refs[alias],
                    },
                    "transaction_policy_ref": self.commercial_ref,
                },
                identifier="publication:" + alias,
            )
            self.require_applied(
                self.invoke(alias, alias, "submit_record", publication)
            )
            self.publications[alias] = publication
            self.harnesses[alias].publication_id = publication["id"]

    @staticmethod
    def scope(alias):
        return "scope:controlled:" + alias

    def _build_harnesses(self):
        self.harnesses = {
            alias: Harness(
                signer=signer,
                registry=self.registry,
                ledger=self.ledger,
                policy=self.policy,
                clock=self.clock,
                domain=self.domain,
                enrollments=self.enrollments,
                authority_scope=AUTHORITY,
                recipient_scope=self.scope(alias),
            )
            for alias, signer in self.signers.items()
        }
        for harness in self.harnesses.values():
            for provider in ("researcher", "reviewer"):
                harness.handoff.register(
                    "agent:" + provider,
                    U + "fake-adapter",
                    self.adapter,
                    self.adapter_contract,
                )

    def document(self, name, body):
        """Explicitly enroll a local definition; no invented external attestation."""
        record = {"id": "fixture:" + name, "test_only": True, **deepcopy(body)}
        self.records[record["id"]] = record
        ref = self.store.put(record)
        self.domain.trust(ref)
        return ref

    def save(self, record):
        self.records[record["id"]] = deepcopy(record)
        self.store.put(record)
        return record

    def sign(self, actor, record):
        signed, proof = self.signers[actor].sign(record)
        self.save(proof)
        validate(signed)
        self.save(signed)
        return signed

    def emit(self, actor, kind, body, *, features=None, identifier=None):
        self._serial += 1
        return self.sign(
            actor,
            {
                "profile": PROFILE,
                "kind": kind,
                "id": identifier or f"{kind}:fixture:{self._serial}",
                "issuer_agent_id": self.signers[actor].agent_id,
                "issuer_principal_id": self.signers[actor].principal_id,
                "created_at": timestamp(self.clock.now_ms),
                "required_extensions": [],
                "required_features": sorted(
                    features or Harness.features_for(kind, body)
                ),
                "body": deepcopy(body),
            },
        )

    def emit_profile(self, actor, type_uri, body):
        self._serial += 1
        return self.sign(
            actor,
            {
                "id": f"evidence:fixture:{self._serial}",
                "profile": PROFILE,
                "type_uri": type_uri,
                "issuer_agent_id": self.signers[actor].agent_id,
                "issued_at": timestamp(self.clock.now_ms),
                "body": deepcopy(body),
            },
        )

    def validity(self, actor):
        owner = actor.removesuffix("_control")
        return {
            "mode": "until_withdrawn",
            "policy_ref": self.principal_policies[owner],
            "status_ref": "https://fixture.invalid/status/" + actor,
        }

    def _admission_policy(self, actor, owner):
        kinds = KINDS - {
            "interaction_request",
            "interaction_receipt",
            "admission_policy_declaration",
        }
        control = {
            "publication_contract",
            "admission_grant",
            "accepted_offer",
            "finalization_notice",
            "refusal_event",
            "status_snapshot",
            "withdrawal_event",
            "negotiation_close",
        }
        pools = []
        for traffic, record_kinds, purposes in (
            (
                "negotiation",
                kinds - control,
                ["submit_record", "prepare_handoff", "dispatch_handoff"],
            ),
            (
                "control",
                control,
                [
                    "submit_record",
                    "query_status",
                    "finalize_candidate",
                    "reconcile_handoff",
                ],
            ),
        ):
            pools.append(
                {
                    "allowance_id": actor + ":" + traffic,
                    "traffic_class": traffic,
                    "record_kinds": sorted(record_kinds),
                    "max_messages": 256,
                    "max_bytes": 16 * 1024 * 1024,
                    "max_work_units": 256,
                    "max_in_flight": 16,
                    "max_live_options": 32,
                    "work_semantics_ref": self.work_ref,
                    "validity": self.validity(actor),
                    "replenishment": {"mode": "none"},
                    "operation_purposes": purposes,
                }
            )
        return self.sign(
            actor,
            {
                "profile": "abp/admission-policy/0.4-draft",
                "kind": "admission_policy_declaration",
                "id": "admission:" + actor,
                "issuer_agent_id": "agent:" + actor,
                "issuer_principal_id": "principal:" + owner,
                "created_at": timestamp(self.clock.now_ms),
                "recipient_agent_id": "agent:" + actor,
                "recipient_scope_id": self.scope(actor),
                "accounting_authority_id": "agent:requester",
                "authority_ref": self.principal_policies[owner],
                "eligibility_ref": self.eligibility_ref,
                "status_policy_ref": self.clock_policy,
                "status_ref": "https://fixture.invalid/admission/" + actor,
                "validity": self.validity(actor),
                "recovery_policy_ref": self.recovery_policy,
                "reply_max_bytes": 1024 * 1024,
                "pools": pools,
            },
        )

    @staticmethod
    def _valid_action(action):
        parameters = action["parameters"]
        return (
            set(parameters) == {"report_id", "scope"}
            and all(isinstance(v, str) and bool(v) for v in parameters.values())
            and action["subject"]
            == {"type_uri": U + "report", "parameters": {"id": parameters["report_id"]}}
            and action["resources"] == []
            and action["polarity"] == "provide"
        )

    @staticmethod
    def _valid_occurrence(action, instance):
        return action["action_type"] != U + "declare_interest" and instance == {
            "type_uri": U + "one-report",
            "parameters": {
                "report_id": action["parameters"]["report_id"],
                "ordinal": 1,
            },
        }

    def promise(self, actor, other, name, action_name):
        return {
            "promise_id": "promise:" + name + ":" + actor,
            "promiser_agent_id": "agent:" + actor,
            "promisee_ids": ["agent:" + other],
            "action": {
                "action_type": U + action_name,
                "semantics_ref": self.semantics_ref,
                "polarity": "provide",
                "subject": {"type_uri": U + "report", "parameters": {"id": name}},
                "resources": [],
                "parameters": {
                    "report_id": name,
                    "scope": "Controlled fixture: " + action_name,
                },
            },
            "capability_refs": [self.capabilities[actor]],
            "authority_refs": [self.principal_policies[actor]],
            "qualifications": [],
            "validity": self.validity(actor),
        }

    def make_request(self, actor, recipient, purpose, subject, *, operation_id=None):
        op = operation_id or "operation:" + str(uuid4())
        body = {
            "operation_id": op,
            "recipient_agent_id": "agent:" + recipient,
            "recipient_scope_id": self.scope(recipient),
            "purpose": purpose,
            "subject_ref": content_ref(subject),
            "admission_basis_ref": self.enrollments[
                "agent:" + recipient
            ].admission_policy_ref,
        }
        required = set(
            subject.get("required_features", ["bilateral"])
        ) | Harness.features_for("interaction_request", body)
        request = self.emit(
            actor,
            "interaction_request",
            body,
            features=required,
            identifier="request:" + op,
        )
        self.requests[op] = request
        return request

    def deliver(self, request):
        actor = request["issuer_agent_id"].removeprefix("agent:")
        recipient = request["body"]["recipient_agent_id"].removeprefix("agent:")
        self.last_request = request
        receipt = self.harnesses[recipient].invoke(
            request,
            peer={
                "agent_id": "agent:" + actor,
                "certificate_digest": self.ledger.get(
                    "transport_identity", "agent:" + actor
                ),
            },
        )
        self.save(receipt)
        self.receipts.append(receipt)
        return receipt

    def invoke(self, actor, recipient, purpose, subject, operation_id=None):
        return self.deliver(
            self.make_request(
                actor, recipient, purpose, subject, operation_id=operation_id
            )
        )

    def require_applied(self, receipt):
        if receipt["body"]["outcome"] != "applied":
            raise ProtocolError(
                receipt["body"]["reason_code"],
                "fixture transition blocked: " + receipt["body"]["operation_id"],
            )
        results = [
            self.save(self.store.resolve(ref)) for ref in receipt["body"]["result_refs"]
        ]
        return results[0] if results else None

    def intent(self, name):
        result = self.emit(
            "requester",
            "intent",
            {
                "intent_id": "intent:" + name,
                "revision": 1,
                "previous_digest": None,
                "market_posture": "seek_result",
                "topic": "controlled research",
                "desired_outcome": "A simulated report, with no claim of real research performance.",
                "preferences": ["Attributable evidence"],
                "disclosure_audience": ["fixture:research"],
                "publication_contract_ref": content_ref(self.publications["requester"]),
                "validity": self.validity("requester"),
                "emission_promise": self.promise(
                    "requester", "researcher", name + ":interest", "declare_interest"
                ),
            },
            identifier="intent:" + name,
        )
        self.require_applied(
            self.invoke("requester", "requester", "submit_record", result)
        )
        return result

    def bilateral(
        self,
        name="research",
        provider="researcher",
        composition=None,
        *,
        origin=None,
        finalize=True,
    ):
        first_receipt = len(self.receipts)
        intent = origin or self.intent(name)
        origin_body = {
            "record_kind": "intent",
            "record_ref": content_ref(intent),
            "originator_agent_id": "agent:requester",
            "originator_principal_id": "principal:requester",
            "coordinator_agent_id": "agent:requester",
        }
        publications = [
            content_ref(self.publications[actor]) for actor in ("requester", provider)
        ]
        terms = {
            "profile_uri": U + "no-consideration",
            "terms": {"consideration": "none", "report_id": name},
            "policy_refs": [
                self.principal_policies[actor] for actor in ("requester", provider)
            ],
        }
        promise = self.promise(
            provider,
            "requester",
            name,
            "review_report" if provider == "reviewer" else "produce_report",
        )
        offer = self.emit(
            provider,
            "offer",
            {
                "semantics": "issued_qualified_promises",
                "origin": origin_body,
                "negotiation_id": "negotiation:" + name,
                "option_id": "option:" + name,
                "revision": 1,
                "previous_option_digest": None,
                "publication_contract_refs": publications,
                "selection_constraints_ref": self.selections[provider],
                "validity": self.validity(provider),
                "own_promises": [promise],
                "requested_counterpromises": [],
                "agreement_terms": terms,
                "route_selections": [],
                "privacy_policy_ref": self.privacy_ref,
            },
            identifier="offer:" + name,
        )
        self.require_applied(self.invoke(provider, "requester", "submit_record", offer))
        windows = []
        for actor in ("requester", provider):
            e = self.enrollments["agent:" + actor]
            windows.append(
                {
                    "principal_id": e.principal_id,
                    "principal_policy_ref": e.principal_policy_ref,
                    "duration_ms": e.refusal_duration_ms,
                    "notice_target_ref": e.notice_target_ref,
                    "notice_profile_ref": e.notice_profile_ref,
                    "refusal_authority_ref": e.principal_policy_ref,
                    "refusal_mechanism_ref": e.refusal_mechanism_ref,
                }
            )
        body = {
            "candidate_id": "candidate:" + name,
            "origin": origin_body,
            "negotiation_id": "negotiation:" + name,
            "participants": [
                {"agent_id": "agent:" + actor, "principal_id": "principal:" + actor}
                for actor in ("requester", provider)
            ],
            "selected_options": [
                {
                    "agent_id": "agent:" + provider,
                    "option_id": "option:" + name,
                    "offer_ref": content_ref(offer),
                    "selection_constraints_ref": self.selections[provider],
                }
            ],
            "publication_contract_refs": publications,
            "own_promises": [promise],
            "agreement_terms": terms,
            "route_selections": [],
            "selection_constraints_refs": [self.selections[provider]],
            "principal_refusal_windows": windows,
            "clock_profile_ref": self.clock_policy,
            "status_authority_agent_id": "agent:requester",
            "status_policy_ref": self.clock_policy,
            "validity": self.validity("requester"),
            "privacy_policy_ref": self.privacy_ref,
            "promise_bindings": [
                {
                    "promise_id": promise["promise_id"],
                    "promiser_agent_id": "agent:" + provider,
                    "basis": "previously_issued",
                    "source_ref": content_ref(offer),
                    "source_promise_id": promise["promise_id"],
                }
            ],
            "handoff_rules": {
                "policy_ref": self.adapter_contract,
                "preclearance": "no_effects",
            },
        }
        if composition:
            body["composition"] = composition
        candidate = self.emit(
            "requester", "candidate_terms", body, identifier="candidate:" + name
        )
        self.require_applied(
            self.invoke("requester", "requester", "submit_record", candidate)
        )
        binding = None
        if composition:
            binding = self.emit(
                "requester",
                "composition_binding",
                {**composition, "candidate_ref": content_ref(candidate)},
            )
            self.require_applied(
                self.invoke("requester", "requester", "submit_record", binding)
            )
        adoptions = []
        for actor in ("requester", provider):
            adoption = self.emit(
                actor,
                "terms_adoption",
                {
                    "candidate_ref": content_ref(candidate),
                    "origin": origin_body,
                    "adopted_own_promise_ids": [promise["promise_id"]]
                    if actor == provider
                    else [],
                    "authority_refs": [self.principal_policies[actor]],
                    "capability_status_refs": [self.capabilities[actor]],
                    "policy_status_refs": [self.principal_policies[actor]],
                    "selection_status_refs": [self.selections[provider]],
                    "validity": self.validity(actor),
                },
                features=candidate["required_features"],
            )
            self.require_applied(
                self.invoke(actor, "requester", "submit_record", adoption)
            )
            adoptions.append(adoption)
        accepted = (
            self.require_applied(
                self.invoke(provider, "requester", "finalize_candidate", candidate)
            )
            if finalize
            else None
        )
        return {
            "intent": intent,
            "candidate": candidate,
            "accepted": accepted,
            "offers": [offer],
            "adoptions": adoptions,
            "binding": binding,
            "receipts": self.receipts[first_receipt:],
        }

    def compose(self, name="research-chain"):
        intent = self.intent(name)
        components = [("sources", "researcher"), ("review", "reviewer")]
        plan = self.emit(
            "requester",
            "transaction_plan",
            {
                "transaction_id": "transaction:" + name,
                "revision": 1,
                "previous_digest": None,
                "orchestrator_agent_id": "agent:requester",
                "origin_ref": content_ref(intent),
                "components": [
                    {
                        "component_id": component,
                        "required_agents": [
                            {
                                "agent_id": "agent:requester",
                                "principal_id": "principal:requester",
                            },
                            {
                                "agent_id": "agent:" + provider,
                                "principal_id": "principal:" + provider,
                            },
                        ],
                        "role": "contribution",
                        "requirement": {
                            "type_uri": U + "component",
                            "parameters": {"report_id": name + ":" + component},
                        },
                    }
                    for component, provider in components
                ],
                "dependencies": [
                    {
                        "dependency_id": "review-needs-sources",
                        "subject_component_id": "review",
                        "stage": "handoff",
                        "requires": [
                            {
                                "component_id": "sources",
                                "condition": "principal_clearance",
                            }
                        ],
                        "on_unavailable": "hold",
                        "on_refused": "block",
                        "on_failed": "block",
                    }
                ],
                "privacy_policy_ref": self.privacy_ref,
                "validity": self.validity("requester"),
            },
        )
        self.require_applied(
            self.invoke("requester", "requester", "submit_record", plan)
        )
        agreements = {
            component: self.bilateral(
                name + ":" + component,
                provider,
                {"plan_ref": content_ref(plan), "component_id": component},
                origin=intent,
            )
            for component, provider in components
        }
        return {"plan": plan, "components": agreements}

    def notify(self, accepted):
        receipts = []
        for descriptor in accepted["body"]["principal_refusal_windows"]:
            inbox_key = accepted["id"] + ":" + descriptor["principal_id"]
            existing_bundle = self.ledger.get("fixture.inboxes", inbox_key)
            if existing_bundle:
                selected = self.store.resolve(
                    self.store.resolve(existing_bundle)["body"]["notice_ref"]
                )
                receipt = self.invoke(
                    "requester", "requester", "submit_record", selected
                )
                self.require_applied(receipt)
                receipts.append(receipt)
                continue
            evidence = self.emit_profile(
                "requester",
                P + "#rp1-principal-inbox/availability",
                {
                    "principal_id": descriptor["principal_id"],
                    "accepted_offer_ref": content_ref(accepted),
                    "candidate_ref": accepted["body"]["candidate_ref"],
                    "terms_available": True,
                    "refusal_available": True,
                    "verified_at_ms": self.clock.now_ms,
                    "test_only": True,
                },
            )
            notice = self.emit(
                "requester",
                "finalization_notice",
                {
                    "accepted_offer_ref": content_ref(accepted),
                    "principal_id": descriptor["principal_id"],
                    "notice_target_ref": descriptor["notice_target_ref"],
                    "notice_profile_ref": descriptor["notice_profile_ref"],
                    "notice_kind": "made_available",
                    "notice_at": timestamp(self.clock.now_ms),
                    "clock_evidence_ref": self.clock_ref,
                    "delivery_evidence_ref": content_ref(evidence),
                    "terms_ref": accepted["body"]["candidate_ref"],
                    "review_duration_ms": descriptor["duration_ms"],
                    "refusal_mechanism_ref": descriptor["refusal_mechanism_ref"],
                },
                features=accepted["required_features"],
            )
            # This is a local, digest-verifiable simulated inbox. Persist its
            # complete bundle before its designated monitor admits the notice.
            bundle = self.emit_profile(
                "requester",
                P + "#rp1-principal-inbox/notice-bundle",
                {
                    "principal_id": descriptor["principal_id"],
                    "accepted_offer_ref": content_ref(accepted),
                    "terms_refs": [accepted["body"]["candidate_ref"]],
                    "notice_ref": content_ref(notice),
                    "duration_ms": descriptor["duration_ms"],
                    "initial_deadline": timestamp(
                        self.clock.now_ms + descriptor["duration_ms"]
                    ),
                    "effective_deadline": timestamp(
                        self.clock.now_ms + descriptor["duration_ms"]
                    ),
                    "health_evidence_refs": [],
                    "refusal_endpoint": "https://fixture.invalid/principal-refusal",
                    "refusal_agent_ids": [
                        "agent:"
                        + descriptor["principal_id"].removeprefix("principal:")
                        + "_control"
                    ],
                },
            )
            self.ledger.put("fixture.inboxes", inbox_key, content_ref(bundle))
            receipt = self.invoke("requester", "requester", "submit_record", notice)
            self.require_applied(receipt)
            receipts.append(receipt)
            self._health_ends.setdefault(
                (accepted["id"], descriptor["principal_id"]), self.clock.now_ms
            )
        return receipts

    def advance_healthy(self, accepted_or_list, elapsed_ms=101):
        agreements = (
            accepted_or_list
            if isinstance(accepted_or_list, list)
            else [accepted_or_list]
        )
        self.clock.advance(elapsed_ms)
        for accepted in agreements:
            for descriptor in accepted["body"]["principal_refusal_windows"]:
                key = (accepted["id"], descriptor["principal_id"])
                start = self._health_ends[key]
                if start == self.clock.now_ms:
                    continue
                evidence = self.emit_profile(
                    "requester",
                    P + "#rp1-principal-inbox/health-interval",
                    {
                        "principal_id": descriptor["principal_id"],
                        "accepted_offer_ref": content_ref(accepted),
                        "interval_start_ms": start,
                        "interval_end_ms": self.clock.now_ms,
                        "state": "usable",
                        "service_evidence_refs": [
                            descriptor["notice_target_ref"],
                            descriptor["refusal_mechanism_ref"],
                        ],
                        "monotonic_elapsed_ms": self.clock.now_ms - start,
                        "continuity_evidence_ref": self.clock_ref,
                    },
                )
                self.harnesses["requester"].health(evidence)
                self._health_ends[key] = self.clock.now_ms
                inbox_key = accepted["id"] + ":" + descriptor["principal_id"]
                bundle = self.store.resolve(
                    self.ledger.get("fixture.inboxes", inbox_key)
                )
                updated_body = deepcopy(bundle["body"])
                updated_body["health_evidence_refs"].append(content_ref(evidence))
                updated = self.emit_profile(
                    "requester", P + "#rp1-principal-inbox/notice-bundle", updated_body
                )
                self.ledger.put("fixture.inboxes", inbox_key, content_ref(updated))

    def status(self, accepted):
        return self.require_applied(
            self.invoke("requester", "requester", "query_status", accepted)
        )

    def refuse(self, accepted, principal="researcher"):
        record = self.emit(
            principal + "_control",
            "refusal_event",
            {
                "accepted_offer_ref": content_ref(accepted),
                "refusing_principal_id": "principal:" + principal,
                "authority_ref": self.principal_policies[principal],
                "status_authority_agent_id": "agent:requester",
                "clock_evidence_ref": self.clock_ref,
                "reason": "Controlled principal refusal; no external effect.",
            },
            features=accepted["required_features"],
        )
        return self.invoke(principal + "_control", "requester", "submit_record", record)

    def handoff_request(self, accepted):
        candidate = self.store.resolve(accepted["body"]["candidate_ref"])
        promise = candidate["body"]["own_promises"][0]
        provider = promise["promiser_agent_id"].removeprefix("agent:")
        report_id = promise["action"]["parameters"]["report_id"]
        payload = self.document(
            "native-input:" + report_id,
            {"target": "fixture-only-report-sink", "report_id": report_id},
        )
        return self.emit(
            provider,
            "handoff_request",
            {
                "handoff_id": "handoff:" + report_id,
                "agreement_ref": content_ref(accepted),
                "action_ref": {
                    "promiser_agent_id": promise["promiser_agent_id"],
                    "promise_id": promise["promise_id"],
                },
                "action_instance": {
                    "type_uri": U + "one-report",
                    "parameters": {"report_id": report_id, "ordinal": 1},
                },
                "adapter_agent_id": "agent:" + provider,
                "adapter_profile_uri": U + "fake-adapter",
                "request_payload_ref": payload,
                "dependency_evidence_refs": [],
                "clearance_refs": [],
                "authority_refs": [self.principal_policies[provider]],
                "effect_class": "externally_effective",
            },
            features=set(accepted["required_features"])
            | {"adapter-handoff", "lifecycle-evidence"},
        )

    def handoff_phase(self, request, phase):
        provider = request["issuer_agent_id"].removeprefix("agent:")
        return self.require_applied(
            self.invoke(provider, "requester", phase + "_handoff", request)
        )

    def restart(self):
        self.ledger.close()
        self.ledger = Ledger(self.path)
        self.store = RecordStore(self.ledger)
        self._build_harnesses()
        for alias, record in self.publications.items():
            self.harnesses[alias].publication_id = record["id"]

    def close(self):
        self.ledger.close()
