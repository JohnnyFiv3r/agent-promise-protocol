"""RP1 policy enforcement point and explicit controlled-test policy.

OPA failure, undefined policy, unknown output, or stale state always blocks.
Installing owner-approved bundles/data and constructing input from authenticated
state are caller responsibilities. No caller-supplied decision is trusted.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import re
import time

from .crypto import MAX_SAFE, PROFILE, PROFILE_URI, canonical, check_ref, digest
from .errors import ProtocolError
from .transport import _safe_url, pinned_https_request

INPUT_FIELDS = frozenset(
    {
        "profile",
        "decision_id",
        "actor",
        "act",
        "recipient_scope_id",
        "subject_ref",
        "subject",
        "action_ref",
        "authority_refs",
        "clearance_refs",
        "dependency_evidence_refs",
        "native_authorization_refs",
        "authority_scope_id",
        "authority_revision",
        "boundary_state_digest",
        "policy_bundle_ref",
        "policy_data_ref",
        "clock",
    }
)
RESULT_FIELDS = frozenset(
    {
        "allow",
        "reason_codes",
        "input_digest",
        "policy_bundle_ref",
        "policy_data_ref",
        "authority_revision",
        "boundary_state_digest",
        "valid_until",
    }
)
ACTS = frozenset(
    {
        "submit_record",
        "finalize_candidate",
        "query_status",
        "read_evidence",
        "notice",
        "refuse",
        "prepare_handoff",
        "dispatch_handoff",
        "reconcile_handoff",
        "report_evidence",
        "authority_commit",
    }
)
REASONS = frozenset(
    {
        "ok",
        "in_progress",
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
        "already_finalized",
        "recipient_declined",
        "contact_closed",
        "internal_unresolved",
        "policy_denied",
        "principal_refused",
        "clearance_pending",
        "dependency_unmet",
        "native_authority_absent",
        "resource_unavailable",
    }
)


def timestamp_ms(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3})?Z", value
    ):
        raise ProtocolError(
            "invalid_record", "UTC timestamp with millisecond precision required"
        )
    try:
        return int(
            datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000
        )
    except ValueError as exc:
        raise ProtocolError("invalid_record", "invalid UTC timestamp") from exc


def timestamp(ms: int) -> str:
    return (
        datetime.fromtimestamp(ms / 1000, timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _reference(value):
    return (
        isinstance(value, dict)
        and not set(value) - {"id", "digest", "locator"}
        and isinstance(value.get("id"), str)
        and bool(value["id"])
        and isinstance(value.get("digest"), str)
        and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", value["digest"]))
    )


def validate_input(value, *, policy_bundle_ref, policy_data_ref, now_ms):
    canonical(value)
    if (
        not isinstance(value, dict)
        or set(value) != INPUT_FIELDS
        or value["profile"] != "app-rp1/0.1-draft"
        or not isinstance(value["act"], str)
        or value["act"] not in ACTS
    ):
        raise ProtocolError("policy_denied", "unsupported policy input shape or act")
    if any(
        not isinstance(value.get(key), str) or not value[key]
        for key in ("decision_id", "recipient_scope_id", "authority_scope_id")
    ):
        raise ProtocolError("policy_denied", "policy input identity/scope missing")
    actor = value["actor"]
    if (
        not isinstance(actor, dict)
        or set(actor) != {"agent_id", "principal_id", "transport_certificate_digest"}
        or any(not isinstance(field, str) or not field for field in actor.values())
        or not re.fullmatch(
            r"sha256:[0-9a-f]{64}", actor["transport_certificate_digest"]
        )
    ):
        raise ProtocolError("identity_mismatch", "authenticated actor required")
    for name in ("subject_ref", "policy_bundle_ref", "policy_data_ref"):
        if not _reference(value[name]):
            raise ProtocolError("policy_denied", "invalid policy reference")
    for name in (
        "authority_refs",
        "clearance_refs",
        "dependency_evidence_refs",
        "native_authorization_refs",
    ):
        if not isinstance(value[name], list) or any(
            not _reference(ref) for ref in value[name]
        ):
            raise ProtocolError("policy_denied", "invalid evidence-reference array")
    if value["action_ref"] is not None and (
        not isinstance(value["action_ref"], dict)
        or set(value["action_ref"]) != {"promiser_agent_id", "promise_id"}
        or any(not isinstance(v, str) or not v for v in value["action_ref"].values())
    ):
        raise ProtocolError("policy_denied", "invalid action reference")
    if not isinstance(value["subject"], dict):
        raise ProtocolError("policy_denied", "complete subject required")
    check_ref(value["subject_ref"], value["subject"])
    if (
        value["policy_bundle_ref"] != policy_bundle_ref
        or value["policy_data_ref"] != policy_data_ref
    ):
        raise ProtocolError(
            "policy_denied", "owner-approved policy/data references differ"
        )
    revision = value["authority_revision"]
    if (
        isinstance(revision, bool)
        or not isinstance(revision, int)
        or not 0 <= revision <= MAX_SAFE
        or not isinstance(value["boundary_state_digest"], str)
        or not re.fullmatch(r"sha256:[0-9a-f]{64}", value["boundary_state_digest"])
    ):
        raise ProtocolError("policy_denied", "invalid authority state")
    clock = value["clock"]
    if (
        not isinstance(clock, dict)
        or set(clock) != {"now", "uncertainty_ms"}
        or isinstance(clock["uncertainty_ms"], bool)
        or not isinstance(clock["uncertainty_ms"], int)
        or not 0 <= clock["uncertainty_ms"] <= 1000
    ):
        raise ProtocolError("policy_denied", "untrusted or uncertain clock")
    maximum = 5000 if value["act"] == "dispatch_handoff" else 30000
    if not timestamp_ms(clock["now"]) <= now_ms < timestamp_ms(clock["now"]) + maximum:
        raise ProtocolError(
            "evidence_stale",
            "policy input is future dated or stale at enforcement time",
        )


def validate_result(result, request, *, now_ms, require_allow=True):
    canonical(result)
    if (
        not isinstance(result, dict)
        or set(result) != RESULT_FIELDS
        or type(result["allow"]) is not bool
    ):
        raise ProtocolError("policy_denied", "undefined or unsupported policy result")
    reasons = result["reason_codes"]
    if (
        not isinstance(reasons, list)
        or not reasons
        or any(not isinstance(reason, str) for reason in reasons)
        or len(reasons) != len(set(reasons))
        or set(reasons) - REASONS
        or (result["allow"] and reasons != ["ok"])
        or (not result["allow"] and "ok" in reasons)
    ):
        raise ProtocolError("policy_denied", "unsupported policy reason/obligation")
    if result["input_digest"] != digest(request) or any(
        result[key] != request[key]
        for key in (
            "policy_bundle_ref",
            "policy_data_ref",
            "authority_revision",
            "boundary_state_digest",
        )
    ):
        raise ProtocolError(
            "policy_denied", "decision does not bind exact input/policy/state"
        )
    valid_until = timestamp_ms(result["valid_until"])
    maximum = 5000 if request["act"] == "dispatch_handoff" else 30000
    if not now_ms < valid_until <= timestamp_ms(request["clock"]["now"]) + maximum:
        raise ProtocolError("evidence_stale", "expired or overlong policy decision")
    if require_allow and result["allow"] is not True:
        failure = ProtocolError(reasons[0], "owner policy denied act")
        failure.policy_result = copy.deepcopy(result)
        raise failure
    return copy.deepcopy(result)


def check_commit(result, *, authority_revision, boundary_state_digest, now_ms):
    if (
        result.get("allow") is not True
        or result.get("authority_revision") != authority_revision
        or result.get("boundary_state_digest") != boundary_state_digest
        or timestamp_ms(result["valid_until"]) <= now_ms
    ):
        raise ProtocolError(
            "evidence_stale",
            "policy must be reevaluated under serialized current boundary",
        )


def decision_evidence(signer, request, result, *, evaluated_at_ms):
    validate_result(result, request, now_ms=evaluated_at_ms, require_allow=False)
    return signer.sign(
        {
            "id": request["decision_id"],
            "profile": PROFILE,
            "type_uri": PROFILE_URI + "#rp1-opa/policy-decision",
            "issuer_agent_id": signer.agent_id,
            "issued_at": timestamp(evaluated_at_ms),
            "body": {
                "input": request,
                "result": result,
                "evaluated_at": timestamp(evaluated_at_ms),
            },
        }
    )


class OPAClient:
    def __init__(
        self,
        url,
        *,
        tls_context,
        server_certificate_digest,
        policy_bundle_ref,
        policy_data_ref,
    ):
        parsed = _safe_url(url)
        if parsed.path != "/v1/data/agent_promise_protocol/rp1/authorize":
            raise ProtocolError(
                "policy_denied", "exact RP1 OPA decision endpoint required"
            )
        self.url, self.tls_context, self.server_certificate_digest = (
            url,
            tls_context,
            server_certificate_digest,
        )
        self.policy_bundle_ref, self.policy_data_ref = (
            copy.deepcopy(policy_bundle_ref),
            copy.deepcopy(policy_data_ref),
        )

    def evaluate(self, request, now_ms):
        validate_input(
            request,
            policy_bundle_ref=self.policy_bundle_ref,
            policy_data_ref=self.policy_data_ref,
            now_ms=now_ms,
        )
        started = time.monotonic()
        _, raw = pinned_https_request(
            self.url,
            method="POST",
            body=canonical({"input": request}),
            headers={"Content-Type": "application/json"},
            tls_context=self.tls_context,
            certificate_digest=self.server_certificate_digest,
            max_bytes=65536,
        )
        from .crypto import strict_loads

        response = strict_loads(raw, max_bytes=65536)
        if not isinstance(response, dict) or "result" not in response:
            raise ProtocolError("policy_denied", "OPA returned no defined result")
        return validate_result(
            response["result"],
            request,
            now_ms=now_ms + int((time.monotonic() - started) * 1000),
        )


class TestPolicy:
    """Explicit in-process fixture policy, never an OPA outage fallback.

    Grants require agent_id, principal_id, acts, subject_kinds and authority_scope_id.
    Optional subject_ids/recipient_scope_ids further narrow their matching scope.
    Production owner policies require the authenticated OPA endpoint instead.
    """

    __test__ = False

    def __init__(self, *, policy_bundle_ref, policy_data_ref, grants):
        self.policy_bundle_ref, self.policy_data_ref = (
            copy.deepcopy(policy_bundle_ref),
            copy.deepcopy(policy_data_ref),
        )
        self.grants = copy.deepcopy(grants)
        for grant in self.grants:
            if not {
                "agent_id",
                "principal_id",
                "acts",
                "subject_kinds",
                "authority_scope_id",
            } <= set(grant):
                raise ValueError(
                    "test grants must explicitly bind actor, principal, acts, kinds and authority scope"
                )

    def evaluate(self, request, now_ms):
        validate_input(
            request,
            policy_bundle_ref=self.policy_bundle_ref,
            policy_data_ref=self.policy_data_ref,
            now_ms=now_ms,
        )
        if not request["authority_refs"]:
            raise ProtocolError("authority_absent", "delegation evidence required")
        if request["act"] == "dispatch_handoff":
            if not request["native_authorization_refs"]:
                raise ProtocolError(
                    "native_authority_absent", "current native authority required"
                )
            if not request["clearance_refs"]:
                raise ProtocolError("clearance_pending", "verified clearance required")
        for grant in self.grants:
            if grant.get("revoked", False) or not grant.get(
                "not_before_ms", 0
            ) <= now_ms < grant.get("valid_until_ms", MAX_SAFE):
                continue
            if (
                grant["agent_id"] != request["actor"]["agent_id"]
                or grant["principal_id"] != request["actor"]["principal_id"]
                or request["act"] not in grant["acts"]
                or request["subject"].get("kind", request["subject"].get("type_uri"))
                not in grant["subject_kinds"]
                or request["authority_scope_id"] != grant["authority_scope_id"]
            ):
                continue
            if (
                "subject_ids" in grant
                and request["subject"]["id"] not in grant["subject_ids"]
            ):
                continue
            if (
                "recipient_scope_ids" in grant
                and request["recipient_scope_id"] not in grant["recipient_scope_ids"]
            ):
                continue
            maximum = 5000 if request["act"] == "dispatch_handoff" else 30000
            result = {
                "allow": True,
                "reason_codes": ["ok"],
                "input_digest": digest(request),
                "policy_bundle_ref": request["policy_bundle_ref"],
                "policy_data_ref": request["policy_data_ref"],
                "authority_revision": request["authority_revision"],
                "boundary_state_digest": request["boundary_state_digest"],
                "valid_until": timestamp(
                    min(now_ms + maximum, grant.get("valid_until_ms", MAX_SAFE))
                ),
            }
            return validate_result(result, request, now_ms=now_ms)
        maximum = 5000 if request["act"] == "dispatch_handoff" else 30000
        denial = {
            "allow": False,
            "reason_codes": ["policy_denied"],
            "input_digest": digest(request),
            "policy_bundle_ref": request["policy_bundle_ref"],
            "policy_data_ref": request["policy_data_ref"],
            "authority_revision": request["authority_revision"],
            "boundary_state_digest": request["boundary_state_digest"],
            "valid_until": timestamp(timestamp_ms(request["clock"]["now"]) + maximum),
        }
        # A definite owner decision is distinguishable from unavailable/undefined
        # policy evaluation. validate_result attaches the exact verified denial.
        return validate_result(denial, request, now_ms=now_ms)
