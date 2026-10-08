"""C5/RP1 principal recovery inside the authenticated authority boundary.

The ``prevalidated_*`` inputs are evidence produced by the harness after proof,
issuer-role, selected policy, and service/clock validation. They are not a public
RPC or a substitute for those checks. This module checks exact subjects,
descriptors, order, durable admission, and conservative time accounting. There
is deliberately no ``valid=True`` or ``notified=True`` shortcut.
"""

from __future__ import annotations

import json
import re

from .errors import ProtocolError
from .storage import Ledger, MAX_INTEGER


_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_DESCRIPTOR_REFS = (
    "principal_policy_ref",
    "notice_target_ref",
    "notice_profile_ref",
    "refusal_authority_ref",
    "refusal_mechanism_ref",
)


def _integer(value, label, minimum=0):
    if type(value) is not int or not minimum <= value <= MAX_INTEGER:
        raise ProtocolError(
            "invalid_record", f"{label} must be a safe integer >= {minimum}"
        )
    return value


def _string(value, label):
    if type(value) is not str or not value:
        raise ProtocolError("invalid_record", f"missing {label}")
    return value


def _ref(value):
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("id"), str)
        or not value["id"]
        or not isinstance(value.get("digest"), str)
        or not _DIGEST.fullmatch(value["digest"])
    ):
        raise ProtocolError("invalid_record", "an exact content reference is required")
    return {"id": value["id"], "digest": value["digest"]}


def _match(actual, expected, label):
    if _ref(actual) != _ref(expected):
        raise ProtocolError("identity_mismatch", f"wrong {label}")


def _operation(operation_key):
    if not isinstance(operation_key, (tuple, list)) or len(operation_key) != 3:
        raise ProtocolError(
            "invalid_record", "operation key must have scope, actor, operation"
        )
    return json.dumps(
        [_string(part, "operation key component") for part in operation_key],
        separators=(",", ":"),
    )


class Recovery:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def _load(self, accepted_ref):
        target = _ref(accepted_ref)
        obj = self.ledger.get("recovery.objects", target["id"])
        if obj is None:
            raise ProtocolError(
                "evidence_unavailable", "accepted object is not registered"
            )
        _match(target, obj["accepted_offer_ref"], "accepted object")
        return obj

    def _save(self, obj):
        self.ledger.put("recovery.objects", obj["accepted_offer_ref"]["id"], obj)

    @staticmethod
    def _principal(obj, principal_id):
        _string(principal_id, "principal")
        if principal_id not in obj["principals"]:
            raise ProtocolError(
                "identity_mismatch", "principal is not represented by this object"
            )
        return obj["principals"][principal_id]

    @staticmethod
    def _evidence(obj, evidence, kind):
        ref = _ref(evidence.get("evidence_ref"))
        previous = obj["evidence"].get(ref["id"])
        normalized = json.loads(json.dumps(evidence, allow_nan=False))
        if previous:
            if previous != {"kind": kind, "value": normalized}:
                raise ProtocolError(
                    "operation_conflict", "evidence identity was reused"
                )
            return True
        obj["evidence"][ref["id"]] = {"kind": kind, "value": normalized}
        return False

    def register(
        self,
        accepted_ref,
        *,
        candidate_ref,
        finalized_at_ms,
        principal_ids,
        descriptors,
    ):
        """Register a harness-validated formation and its adopted descriptors."""
        accepted_ref, candidate_ref = _ref(accepted_ref), _ref(candidate_ref)
        _integer(finalized_at_ms, "finalized_at_ms")
        if not isinstance(principal_ids, (list, tuple)) or not principal_ids:
            raise ProtocolError("invalid_record", "principal identities are required")
        required = {_string(p, "principal") for p in principal_ids}
        if not isinstance(descriptors, (list, tuple)):
            raise ProtocolError("invalid_record", "descriptors must be an array")
        selected = {}
        for descriptor in descriptors:
            if not isinstance(descriptor, dict):
                raise ProtocolError("invalid_record", "malformed principal descriptor")
            principal = _string(descriptor.get("principal_id"), "principal")
            if principal in selected:
                raise ProtocolError("invalid_record", "duplicate principal descriptor")
            duration = _integer(descriptor.get("duration_ms"), "duration_ms", 1)
            if finalized_at_ms + duration > MAX_INTEGER:
                raise ProtocolError(
                    "invalid_record", "deadline exceeds safe integer range"
                )
            selected[principal] = {
                "principal_id": principal,
                "duration_ms": duration,
                **{field: _ref(descriptor.get(field)) for field in _DESCRIPTOR_REFS},
            }
        if set(selected) != required:
            raise ProtocolError(
                "invalid_record", "descriptors must cover exactly distinct principals"
            )
        registration = {
            "accepted_offer_ref": accepted_ref,
            "candidate_ref": candidate_ref,
            "finalized_at_ms": finalized_at_ms,
            "descriptors": selected,
        }
        with self.ledger.transaction():
            existing = self.ledger.get("recovery.objects", accepted_ref["id"])
            if existing:
                if existing["registration"] != registration:
                    raise ProtocolError(
                        "operation_conflict", "accepted recovery context is immutable"
                    )
                return existing
            obj = {
                **registration,
                "registration": registration,
                "principals": {
                    p: {
                        "descriptor": d,
                        "notice": None,
                        "notices": [],
                        "health": [],
                        "published_deadline_ms": None,
                    }
                    for p, d in selected.items()
                },
                "admissions": {},
                "evidence": {},
                "refused": False,
                "refusal_event_refs": [],
                "snapshots": [],
            }
            self._save(obj)
            return self._load(accepted_ref)

    def notice(self, accepted_ref, *, prevalidated_notice):
        """Record designated-authority evidence of the complete qualifying bundle."""
        evidence = prevalidated_notice
        if not isinstance(evidence, dict):
            raise ProtocolError(
                "invalid_record", "prevalidated notice evidence is required"
            )
        with self.ledger.transaction():
            obj = self._load(accepted_ref)
            _match(
                evidence.get("accepted_offer_ref"),
                accepted_ref,
                "notice accepted object",
            )
            _match(
                evidence.get("candidate_ref"), obj["candidate_ref"], "notice candidate"
            )
            principal = self._principal(obj, evidence.get("principal_id"))
            descriptor = principal["descriptor"]
            for field in (
                "notice_target_ref",
                "notice_profile_ref",
                "refusal_mechanism_ref",
            ):
                _match(evidence.get(field), descriptor[field], field)
            duration = _integer(
                evidence.get("review_duration_ms"), "review_duration_ms", 1
            )
            if duration != descriptor["duration_ms"]:
                raise ProtocolError(
                    "identity_mismatch", "notice changes adopted duration"
                )
            verified = _integer(evidence.get("verified_at_ms"), "verified_at_ms")
            order = _integer(evidence.get("authority_order"), "authority_order", 1)
            start = max(obj["finalized_at_ms"], verified)
            _integer(start + duration, "initial deadline")
            if self._evidence(obj, evidence, "notice"):
                return principal["notice"]
            if (
                principal["notices"]
                and order <= principal["notices"][-1]["authority_order"]
            ):
                raise ProtocolError(
                    "lineage_conflict", "notice authority order did not advance"
                )
            notice = {
                "evidence_ref": _ref(evidence["evidence_ref"]),
                "authority_order": order,
                "verified_at_ms": verified,
                "starts_at_ms": start,
                "initial_deadline_ms": start + duration,
            }
            if principal["notice"] and verified < principal["notice"]["verified_at_ms"]:
                raise ProtocolError(
                    "lineage_conflict", "earlier qualifying notice needs reconciliation"
                )
            principal["notices"].append(notice)
            if principal["notice"] is None:
                principal["notice"] = notice
                principal["published_deadline_ms"] = notice["initial_deadline_ms"]
            self._save(obj)
            return principal["notice"].copy()

    def health(self, accepted_ref, *, prevalidated_health):
        """Journal service evidence; only proven monotonic intervals earn credit.

        The harness verifies monitor authority and continuity evidence. Missing
        continuity or an insufficient elapsed duration downgrades usable to
        unknown. Overlapping outages are unioned; contradictory states remain
        unresolved. Out-of-order arrival is normalized into ordered intervals.
        """
        evidence = prevalidated_health
        if not isinstance(evidence, dict):
            raise ProtocolError(
                "invalid_record", "prevalidated health evidence is required"
            )
        with self.ledger.transaction():
            obj = self._load(accepted_ref)
            _match(
                evidence.get("accepted_offer_ref"),
                accepted_ref,
                "health accepted object",
            )
            principal = self._principal(obj, evidence.get("principal_id"))
            if principal["notice"] is None:
                raise ProtocolError(
                    "evidence_unavailable", "health cannot precede selected notice"
                )
            start = _integer(evidence.get("interval_start_ms"), "interval_start_ms")
            end = _integer(evidence.get("interval_end_ms"), "interval_end_ms")
            if end <= start or start < principal["notice"]["starts_at_ms"]:
                raise ProtocolError(
                    "invalid_record", "health interval is outside the review window"
                )
            state = evidence.get("state")
            if state not in ("usable", "unusable", "unknown"):
                raise ProtocolError("invalid_record", "unknown health state")
            service = evidence.get("service_evidence_refs")
            if not isinstance(service, list) or not service:
                raise ProtocolError(
                    "evidence_unavailable", "service monitor evidence is required"
                )
            service = [_ref(ref) for ref in service]
            elapsed = _integer(
                evidence.get("monotonic_elapsed_ms", 0), "monotonic_elapsed_ms"
            )
            continuity = evidence.get("continuity_evidence_ref")
            if continuity is not None:
                continuity = _ref(continuity)
            if state == "usable" and (continuity is None or elapsed < end - start):
                state = "unknown"
            if self._evidence(obj, evidence, "health"):
                return {"state": state, "duplicate": True}
            interval = {
                "start": start,
                "end": end,
                "state": state,
                "evidence_ref": _ref(evidence["evidence_ref"]),
                "service_evidence_refs": service,
                "monotonic_elapsed_ms": elapsed,
                "continuity_evidence_ref": continuity,
            }
            principal["health"].append(interval)
            principal["health"].sort(key=lambda item: (item["start"], item["end"]))
            self._save(obj)
            return {"state": state, "duplicate": False}

    @staticmethod
    def _account(principal, until):
        notice = principal["notice"]
        if notice is None:
            return None
        start = notice["starts_at_ms"]
        until = max(start, until)
        intervals = [
            item
            for item in principal["health"]
            if item["start"] < until and item["end"] > start
        ]
        boundaries = sorted(
            {
                start,
                until,
                *[
                    max(start, min(until, item[edge]))
                    for item in intervals
                    for edge in ("start", "end")
                ],
            }
        )
        usable = nonusable = 0
        gap = conflict = False
        for left, right in zip(boundaries, boundaries[1:]):
            states = {
                item["state"]
                for item in intervals
                if item["start"] <= left and item["end"] >= right
            }
            if not states:
                gap = True
            # Unknown/unusable reports agree that no duration may be credited;
            # their overlap is one outage. A usable claim conflicts with either.
            if "usable" in states and len(states) > 1:
                conflict = True
            if states == {"usable"}:
                usable += right - left
            else:
                nonusable += right - left
        deadline = notice["initial_deadline_ms"] + nonusable
        _integer(deadline, "effective deadline")
        return {
            "starts_at_ms": start,
            "initial_deadline_ms": notice["initial_deadline_ms"],
            "effective_deadline_ms": deadline,
            "credited_usable_ms": usable,
            "nonusable_ms": nonusable,
            "health_gap": gap,
            "health_conflict": conflict,
        }

    def admit_refusal(
        self,
        accepted_ref,
        *,
        principal_id,
        operation_key,
        request_digest,
        peer_agent_id,
        admitted_lower_ms,
        admitted_upper_ms,
    ):
        """Commit the authenticated ingress interval *before* full act verification."""
        key = _operation(operation_key)
        _string(peer_agent_id, "authenticated peer")
        if peer_agent_id != operation_key[1]:
            raise ProtocolError(
                "identity_mismatch", "peer must match authenticated operation actor"
            )
        if not isinstance(request_digest, str) or not _DIGEST.fullmatch(request_digest):
            raise ProtocolError("invalid_record", "request digest is required")
        lower = _integer(admitted_lower_ms, "admitted_lower_ms")
        upper = _integer(admitted_upper_ms, "admitted_upper_ms")
        if lower > upper:
            raise ProtocolError("invalid_record", "inverted admission interval")
        with self.ledger.transaction():
            obj = self._load(accepted_ref)
            self._principal(obj, principal_id)
            if upper < obj["finalized_at_ms"]:
                raise ProtocolError(
                    "invalid_record", "refusal precedes accepted object"
                )
            existing = self.ledger.get("recovery.operation_tombstones", key)
            identity = {
                "accepted_offer_ref": _ref(accepted_ref),
                "principal_id": principal_id,
                "request_digest": request_digest,
                "peer_agent_id": peer_agent_id,
            }
            if existing:
                if existing["identity"] != identity:
                    raise ProtocolError(
                        "operation_conflict", "refusal operation identity was reused"
                    )
                return obj["admissions"][key]
            admission = {
                **identity,
                "operation_key": list(operation_key),
                "admitted_lower_ms": lower,
                "admitted_upper_ms": upper,
                "state": "pending",
                "evidence_ref": None,
            }
            obj["admissions"][key] = admission
            self.ledger.put(
                "recovery.operation_tombstones", key, {"identity": identity}
            )
            self._save(obj)
            return admission.copy()

    @staticmethod
    def _refusal_effect(obj, admission):
        principal = obj["principals"][admission["principal_id"]]
        account = Recovery._account(principal, admission["admitted_upper_ms"])
        deadline = (
            max(account["effective_deadline_ms"], principal["published_deadline_ms"])
            if account is not None
            else None
        )
        timely = deadline is None or admission["admitted_lower_ms"] <= deadline
        if timely:
            obj["refused"] = True
            if admission["evidence_ref"] not in obj["refusal_event_refs"]:
                obj["refusal_event_refs"].append(admission["evidence_ref"])
        return timely

    def resolve_refusal(self, accepted_ref, *, operation_key, prevalidated_refusal):
        evidence = prevalidated_refusal
        if not isinstance(evidence, dict):
            raise ProtocolError(
                "invalid_record", "prevalidated refusal evidence is required"
            )
        key = _operation(operation_key)
        with self.ledger.transaction():
            obj = self._load(accepted_ref)
            admission = obj["admissions"].get(key)
            if admission is None:
                raise ProtocolError(
                    "evidence_unavailable", "refusal has no durable admission"
                )
            _match(
                evidence.get("accepted_offer_ref"),
                accepted_ref,
                "refusal accepted object",
            )
            if evidence.get("principal_id") != admission["principal_id"]:
                raise ProtocolError(
                    "identity_mismatch", "refusal principal changed after ingress"
                )
            principal = self._principal(obj, evidence["principal_id"])
            _match(
                evidence.get("refusal_authority_ref"),
                principal["descriptor"]["refusal_authority_ref"],
                "refusal authority",
            )
            _integer(evidence.get("authority_order"), "authority_order", 1)
            if admission["state"] != "pending":
                if admission.get("verification") != evidence:
                    raise ProtocolError(
                        "operation_conflict", "terminal refusal result is immutable"
                    )
                return admission.copy()
            self._evidence(obj, evidence, "refusal")
            admission["evidence_ref"] = _ref(evidence["evidence_ref"])
            admission["verification"] = evidence
            admission["state"] = "valid"
            admission["outcome"] = (
                "refused" if self._refusal_effect(obj, admission) else "late"
            )
            self._save(obj)
            return admission.copy()

    def reject_refusal(self, accepted_ref, *, operation_key, reason, evidence_ref):
        """Record a negative verifier result; it can never clear another refusal."""
        key, evidence_ref = _operation(operation_key), _ref(evidence_ref)
        _string(reason, "rejection reason")
        with self.ledger.transaction():
            obj = self._load(accepted_ref)
            admission = obj["admissions"].get(key)
            if admission is None:
                raise ProtocolError(
                    "evidence_unavailable", "refusal has no durable admission"
                )
            if admission["state"] != "pending":
                if (
                    admission["state"] != "rejected"
                    or admission.get("reason") != reason
                    or admission["evidence_ref"] != evidence_ref
                ):
                    raise ProtocolError(
                        "operation_conflict", "terminal refusal result is immutable"
                    )
                return admission.copy()
            admission.update(state="rejected", reason=reason, evidence_ref=evidence_ref)
            self._save(obj)
            return admission.copy()

    def observe(
        self,
        accepted_ref,
        *,
        now_ms,
        uncertainty_ms,
        clock_evidence_ref,
        authority_evidence_refs,
    ):
        """Append an immutable current observation; strictly positive proof is required."""
        _integer(now_ms, "now_ms")
        if uncertainty_ms is not None:
            _integer(uncertainty_ms, "uncertainty_ms")
        clock_ref = _ref(clock_evidence_ref) if clock_evidence_ref is not None else None
        if not isinstance(authority_evidence_refs, list):
            raise ProtocolError(
                "invalid_record", "authority evidence references must be an array"
            )
        authority_refs = [_ref(ref) for ref in authority_evidence_refs]
        clock_ok = (
            uncertainty_ms is not None
            and uncertainty_ms <= 1000
            and clock_ref is not None
        )
        lower = max(0, now_ms - uncertainty_ms) if uncertainty_ms is not None else 0
        with self.ledger.transaction():
            obj = self._load(accepted_ref)
            if obj["snapshots"] and now_ms < obj["snapshots"][-1]["observed_at_ms"]:
                raise ProtocolError(
                    "lineage_conflict", "observation time cannot move backwards"
                )
            for admission in obj["admissions"].values():
                if admission["state"] == "valid":
                    self._refusal_effect(obj, admission)
            observations = []
            for principal_id, principal in obj["principals"].items():
                account = self._account(principal, lower)
                observation = {
                    "principal_id": principal_id,
                    "duration_ms": principal["descriptor"]["duration_ms"],
                    "notice_ref": principal["notice"]["evidence_ref"]
                    if principal["notice"]
                    else None,
                    "health_evidence_refs": [
                        h["evidence_ref"] for h in principal["health"]
                    ],
                }
                if account is None:
                    observation.update(state="notice_pending", pending_admissions=0)
                else:
                    deadline = max(
                        account["effective_deadline_ms"],
                        principal["published_deadline_ms"],
                    )
                    principal["published_deadline_ms"] = deadline
                    account["effective_deadline_ms"] = deadline
                    pending = sum(
                        1
                        for admission in obj["admissions"].values()
                        if admission["principal_id"] == principal_id
                        and admission["state"] == "pending"
                        and admission["admitted_lower_ms"] <= deadline
                    )
                    complete = (
                        not account["health_gap"] and not account["health_conflict"]
                    )
                    if not clock_ok or not authority_refs or not complete or pending:
                        state = "unresolved"
                    elif (
                        lower > deadline
                        and account["credited_usable_ms"] >= observation["duration_ms"]
                    ):
                        state = "closed"
                    else:
                        state = "window_open"
                    observation.update(account, state=state, pending_admissions=pending)
                observations.append(observation)
            if obj["refused"]:
                status = "refused"
            elif (
                not clock_ok
                or not authority_refs
                or any(p["state"] == "unresolved" for p in observations)
            ):
                status = "unresolved"
            elif all(p["state"] == "closed" for p in observations):
                status = "refusal_windows_closed"
            else:
                status = "pending_refusal_windows"
            previous = obj["snapshots"][-1] if obj["snapshots"] else None
            snapshot = {
                "accepted_offer_ref": _ref(accepted_ref),
                "status": status,
                "revision": (previous["revision"] + 1) if previous else 1,
                "observed_at_ms": now_ms,
                "time_lower_bound_ms": lower,
                "clock_uncertainty_ms": uncertainty_ms,
                "clock_evidence_ref": clock_ref,
                "authority_evidence_refs": authority_refs,
                "principals": observations,
                "refusal_event_refs": obj["refusal_event_refs"].copy(),
            }
            _integer(snapshot["revision"], "status revision", 1)
            obj["snapshots"].append(snapshot)
            self._save(obj)
            return json.loads(json.dumps(snapshot))

    def history(self, accepted_ref):
        return self._load(accepted_ref)["snapshots"]
