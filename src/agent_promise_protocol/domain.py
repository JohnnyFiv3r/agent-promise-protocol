"""Application-selected meanings and enrollment. This is not a core taxonomy."""

from dataclasses import dataclass, field
from typing import Callable
from .errors import ProtocolError
from .records import same_ref, ref_key


@dataclass
class Enrollment:
    principal_id: str
    principal_policy_ref: dict
    capability_refs: list[dict]
    action_types: set[str]
    features: set[str]
    admission_policy_ref: dict
    refusal_duration_ms: int
    notice_target_ref: dict
    notice_profile_ref: dict
    refusal_mechanism_ref: dict
    control_agents: set[str]
    notice_agent_id: str
    authority_scope_id: str
    active: bool = True


@dataclass
class ActionMeaning:
    semantics_ref: dict
    validate: Callable[[dict], bool]
    occurrence: Callable[[dict, dict], bool]


@dataclass
class Domain:
    actions: dict[str, ActionMeaning] = field(default_factory=dict)
    understood_uris: set[str] = field(default_factory=set)
    trusted_refs: set[str] = field(default_factory=set)
    selection: dict[str, dict] = field(default_factory=dict)
    # Adopters choose complete agreement and dependency meanings, not just labels.
    agreement_checks: dict[str, Callable[[dict], bool]] = field(default_factory=dict)
    requirement_checks: dict[str, Callable[[dict, dict, dict], bool]] = field(
        default_factory=dict
    )
    evidence_checks: dict[str, Callable[..., bool]] = field(default_factory=dict)

    arrangement_checks: dict[str, Callable[[dict, list], bool]] = field(
        default_factory=dict
    )
    candidate_checks: dict[str, Callable[[dict, list], bool]] = field(
        default_factory=dict
    )
    qualification_checks: dict[str, Callable[[dict, str], bool]] = field(
        default_factory=dict
    )

    health_checks: dict[str, Callable[..., bool]] = field(default_factory=dict)

    def trust(self, ref):
        self.trusted_refs.add(ref_key(ref))

    def require_ref(self, ref):
        if ref_key(ref) not in self.trusted_refs:
            raise ProtocolError(
                "unsupported_semantics",
                "unapproved policy or evidence definition: " + ref["id"],
            )

    def validate_action(self, action):
        meaning = self.actions.get(action["action_type"])
        if meaning is None or not same_ref(
            meaning.semantics_ref, action["semantics_ref"]
        ):
            raise ProtocolError("unsupported_semantics", action["action_type"])
        if meaning.validate(action) is not True:
            raise ProtocolError(
                "invalid_record", "action parameters do not match the selected meaning"
            )

    def typed(self, value):
        if value["type_uri"] not in self.understood_uris:
            raise ProtocolError("unsupported_semantics", value["type_uri"])

    def requirement(self, requirement, candidate, plan):
        fn = self.requirement_checks.get(requirement["type_uri"])
        return fn is not None and fn(requirement, candidate, plan) is True
