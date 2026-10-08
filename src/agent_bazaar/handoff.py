"""C8/RP1 frozen adapter boundary with a durable, never-redelivered dispatch key.

All incoming records must already have passed the harness's authentication and C3
admission. No native service is implemented here. Callbacks are trusted deployment
configuration, and cannot be selected by an untrusted request.
"""

from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import re

from .composition import same_ref
from .crypto import canonical, content_ref, digest, unsigned_digest
from .errors import ProtocolError


def native_wrapper(record_id, media_type, payload):
    """Freeze exact opaque bytes; no native parse/serialize round trip is allowed."""
    if (
        not isinstance(payload, bytes)
        or not isinstance(media_type, str)
        or not media_type
    ):
        raise ProtocolError(
            "native_request_invalid", "native payload must be bytes with a media type"
        )
    return {
        "id": record_id,
        "media_type": media_type,
        "payload_encoding": "base64url",
        "payload": base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii"),
        "payload_digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
    }


def decode_native_wrapper(wrapper, ref):
    if (
        not isinstance(wrapper, dict)
        or set(wrapper)
        != {"id", "media_type", "payload_encoding", "payload", "payload_digest"}
        or not same_ref(content_ref(wrapper), ref)
        or wrapper["payload_encoding"] != "base64url"
        or not isinstance(wrapper["media_type"], str)
        or not wrapper["media_type"]
        or not isinstance(wrapper["payload"], str)
        or not re.fullmatch(r"[A-Za-z0-9_-]*", wrapper["payload"])
    ):
        raise ProtocolError(
            "native_request_invalid", "invalid native wrapper/reference"
        )
    try:
        payload = base64.urlsafe_b64decode(
            wrapper["payload"] + "=" * (-len(wrapper["payload"]) % 4)
        )
    except (ValueError, TypeError):
        raise ProtocolError(
            "native_request_invalid", "invalid native base64url bytes"
        ) from None
    if (
        base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")
        != wrapper["payload"]
        or "sha256:" + hashlib.sha256(payload).hexdigest() != wrapper["payload_digest"]
    ):
        raise ProtocolError(
            "native_request_invalid", "native payload digest/encoding mismatch"
        )
    return payload


def handoff_key(accepted, action_ref, action_instance):
    return digest(
        {
            "accepted_issuer_agent_id": accepted["issuer_agent_id"],
            "accepted_offer_id": accepted["id"],
            "accepted_unsigned_payload_digest": unsigned_digest(accepted),
            "promiser_agent_id": action_ref["promiser_agent_id"],
            "promise_id": action_ref["promise_id"],
            "action_instance": action_instance,
        }
    )


class Handoff:
    """Shared ledger enforcement for explicitly enrolled adapter contracts.

    emit(kind, body) returns a signed record. action_check(request, accepted,
    candidate) must establish occurrence/cardinality, requester permission and
    adopted semantics, returning exactly True. gate_check(request, prepared,
    native_authority, now_ms) returns allow, valid_until_ms, an exact
    authorization_decision_ref and nonempty gate_evidence_refs; it establishes
    current clearance, dependencies and delegated authorization in this ledger
    transaction. Its maximum lifetime is 5000 ms. clock() returns current ms.

    Prepare never calls dispatch. Dispatch is forbidden inside a caller's outer
    transaction because committing a savepoint is insufficient durability.
    Reconcile only calls the adapter's read-only reconcile hook.
    """

    def __init__(
        self, ledger, resolve, *, emit, action_check, gate_check, clock, failpoint=None
    ):
        self.ledger = ledger
        self.resolve_external = resolve
        self.emit = emit
        self.action_check = action_check
        self.gate_check = gate_check
        self.clock = clock
        self.failpoint = failpoint or (lambda _: None)
        self.adapters = {}

    def register(
        self,
        adapter_agent_id,
        adapter_profile_uri,
        adapter,
        contract_ref,
        *,
        final_absence_check=None,
    ):
        """Enroll one contract; final absence is unsupported unless explicitly verified.

        final_absence_check(observation, prepared) is an administrator-configured
        predicate for this exact contract, returning True only for authenticated
        final absence. An adapter's ``final_absence`` label is insufficient alone.
        """
        if not adapter_agent_id or not adapter_profile_uri or not contract_ref:
            raise ProtocolError(
                "adapter_unsupported",
                "explicit adapter identity/profile/contract required",
            )
        for hook in ("prepare", "verify_native_authority", "dispatch", "reconcile"):
            if not callable(getattr(adapter, hook, None)):
                raise ProtocolError("adapter_unsupported", "adapter lacks " + hook)
        identity = (adapter_agent_id, adapter_profile_uri)
        if identity in self.adapters:
            previous = self.adapters[identity]
            if (
                previous["adapter"] is not adapter
                or not same_ref(previous["contract_ref"], contract_ref)
                or previous["final_absence_check"] is not final_absence_check
            ):
                raise ProtocolError(
                    "adapter_conflict",
                    "adapter enrollment is immutable for this runtime",
                )
        self.adapters[identity] = {
            "adapter": adapter,
            "contract_ref": deepcopy(contract_ref),
            "final_absence_check": final_absence_check,
        }

    def resolve(self, ref):
        obj = self.ledger.get("handoff_objects", ref["digest"])
        if obj is None:
            obj = self.resolve_external(ref)
        if obj is None or not same_ref(content_ref(obj), ref):
            raise ProtocolError(
                "evidence_unavailable", "exact handoff evidence reference unavailable"
            )
        return obj

    def _save(self, record):
        self.ledger.put("handoff_objects", content_ref(record)["digest"], record)
        return record

    def _emit(self, kind, body):
        record = self.emit(kind, deepcopy(body))
        if record.get("kind") != kind or record.get("body") != body:
            raise ProtocolError(
                "handoff_invalid", "record emitter changed the frozen body"
            )
        return self._save(record)

    def _context(self, request, *, check_action=True):
        if request.get("kind") != "handoff_request":
            raise ProtocolError("handoff_invalid", "not a handoff request")
        body = request["body"]
        accepted = self.resolve(body["agreement_ref"])
        if accepted.get("kind") != "accepted_offer":
            raise ProtocolError("handoff_invalid", "exact formed agreement required")
        candidate = self.resolve(accepted["body"]["candidate_ref"])
        if candidate.get("kind") != "candidate_terms":
            raise ProtocolError("handoff_invalid", "accepted candidate not available")
        rules = candidate["body"].get("handoff_rules", {})
        if rules.get("preclearance") != "no_effects" or "recovery_profile_ref" in rules:
            raise ProtocolError("unsupported_semantics", "RP1 permits only no_effects")
        action = body["action_ref"]
        own = [
            p
            for p in candidate["body"]["own_promises"]
            if p["promiser_agent_id"] == action["promiser_agent_id"]
            and p["promise_id"] == action["promise_id"]
        ]
        if len(own) != 1:
            raise ProtocolError(
                "action_mismatch", "action is not an exact candidate promise"
            )
        if check_action:
            adopted = False
            for ref in accepted["body"]["adoption_refs"]:
                adoption = self.resolve(ref)
                if (
                    adoption.get("kind") == "terms_adoption"
                    and adoption["issuer_agent_id"] == action["promiser_agent_id"]
                    and same_ref(
                        adoption["body"]["candidate_ref"],
                        accepted["body"]["candidate_ref"],
                    )
                    and action["promise_id"]
                    in adoption["body"]["adopted_own_promise_ids"]
                ):
                    adopted = True
                self._save(adoption)
            if not adopted:
                raise ProtocolError(
                    "action_mismatch", "action has not been adopted by its own author"
                )
        instance = body["action_instance"]
        if not instance.get("type_uri") or not isinstance(
            instance.get("parameters"), dict
        ):
            raise ProtocolError("unsupported_semantics", "typed occurrence required")
        if check_action and (
            self.action_check is None
            or self.action_check(request, accepted, candidate) is not True
        ):
            raise ProtocolError(
                "action_authority_absent",
                "occurrence/cardinality or requester authority not established",
            )
        return accepted, candidate, handoff_key(accepted, action, instance)

    def _adapter(self, request, slot=None):
        body = request["body"]
        registration = self.adapters.get(
            (body["adapter_agent_id"], body["adapter_profile_uri"])
        )
        if registration is None:
            raise ProtocolError(
                "adapter_unsupported", "adapter contract is not enrolled"
            )
        if slot and not same_ref(
            slot["adapter_contract_ref"], registration["contract_ref"]
        ):
            raise ProtocolError(
                "adapter_conflict",
                "enrolled contract differs from frozen adapter contract",
            )
        return registration

    @staticmethod
    def _compatible(request, slot):
        original = slot["request"]["body"]
        proposed = request["body"]
        for field in ("agreement_ref", "request_payload_ref"):
            if not same_ref(original[field], proposed[field]):
                raise ProtocolError(
                    "handoff_conflict", "exact frozen " + field + " cannot be replaced"
                )
        for field in (
            "action_ref",
            "action_instance",
            "adapter_agent_id",
            "adapter_profile_uri",
            "effect_class",
        ):
            if original[field] != proposed[field]:
                raise ProtocolError(
                    "handoff_conflict",
                    "frozen handoff " + field + " cannot be replaced",
                )

    def _receipt(self, slot, phase, outcome, reason, *, gate=None, native_refs=None):
        previous = slot.setdefault("receipts", {}).get(phase)
        prepared = slot.get("prepared")
        body = {
            "handoff_ref": content_ref(slot["request"]),
            "handoff_key": slot["key"],
            "phase": phase,
            "revision": previous["body"]["revision"] + 1 if previous else 1,
            "previous_receipt_digest": content_ref(previous)["digest"]
            if previous
            else None,
            "outcome": outcome,
            "gate_evidence_refs": [slot["adapter_contract_ref"]],
            "native_evidence_refs": native_refs or [],
            "reason_code": reason,
        }
        if prepared:
            body["prepared_plan_ref"] = content_ref(prepared)
            body["native_operation_key"] = prepared["body"]["native_operation_key"]
        actual_gate = gate or slot.get("gate")
        if actual_gate:
            body["gate_evidence_refs"] = actual_gate["gate_evidence_refs"]
            body["authorization_decision_ref"] = actual_gate[
                "authorization_decision_ref"
            ]
        receipt = self._emit("handoff_receipt", body)
        slot["receipts"][phase] = receipt
        self.ledger.put("handoff_slots", slot["key"], slot)
        return receipt

    def prepare(self, request):
        with self.ledger.transaction():
            accepted, candidate, key = self._context(request, check_action=False)
            existing = self.ledger.get("handoff_slots", key)
            if existing:
                self._compatible(request, existing)
                self._adapter(request, existing)
                return {
                    "prepared": existing["prepared"],
                    "receipt": existing["receipts"]["prepare"],
                }
            self._context(request)
            registration = self._adapter(request)
            payload = self.resolve(request["body"]["request_payload_ref"])
            native_key = "abp-rp1-" + key.removeprefix("sha256:")
            translation = registration["adapter"].prepare(
                deepcopy(request), deepcopy(payload), native_key
            )
            if (
                not isinstance(translation, dict)
                or not translation.get("authorization_requirement_refs")
                or not translation.get("reconciliation_profile_ref")
            ):
                raise ProtocolError(
                    "adapter_unsupported",
                    "complete native authorization and reconciliation requirements required",
                )
            wrapper = native_wrapper(
                "native-request:" + key,
                translation["media_type"],
                translation["native_bytes"],
            )
            self._save(wrapper)
            prepared_body = {
                "handoff_ref": content_ref(request),
                "handoff_key": key,
                "adapter_profile_uri": request["body"]["adapter_profile_uri"],
                "native_request_ref": content_ref(wrapper),
                "native_operation_key": native_key,
                "effect_class": request["body"].get(
                    "effect_class", "externally_effective"
                ),
                "authorization_requirement_refs": translation[
                    "authorization_requirement_refs"
                ],
                "reconciliation_profile_ref": translation["reconciliation_profile_ref"],
            }
            prepared = self._emit("prepared_handoff", prepared_body)
            self._save(request)
            self._save(accepted)
            self._save(candidate)
            slot = {
                "key": key,
                "request": request,
                "prepared": prepared,
                "adapter_contract_ref": registration["contract_ref"],
                "dispatch_attempt_started": False,
                "receipts": {},
            }
            receipt = self._receipt(slot, "prepare", "prepared", "translation_frozen")
            return {"prepared": prepared, "receipt": receipt}

    @staticmethod
    def _fresh(result, now, *, native=False):
        if not isinstance(result, dict) or result.get("allow") is not True:
            raise ProtocolError(
                "native_authority_absent" if native else "handoff_blocked",
                "current authority is not established",
            )
        deadline = result.get("valid_until_ms")
        if (
            isinstance(deadline, bool)
            or not isinstance(deadline, int)
            or not now < deadline <= now + 5000
        ):
            raise ProtocolError(
                "authority_stale",
                "authority must expire within five seconds and remain live",
            )
        refs = (
            result.get("evidence_refs") if native else result.get("gate_evidence_refs")
        )
        if not refs or (not native and not result.get("authorization_decision_ref")):
            raise ProtocolError(
                "authority_unavailable",
                "attributable current authority evidence required",
            )

    def dispatch(self, request):
        if self.ledger.in_transaction:
            raise ProtocolError(
                "dispatch_transaction",
                "dispatch marker must commit outside any caller transaction",
            )
        with self.ledger.transaction():
            _, _, key = self._context(request, check_action=False)
            slot = self.ledger.get("handoff_slots", key)
            if slot is None:
                raise ProtocolError(
                    "handoff_unprepared", "first prepare the exact action"
                )
            self._compatible(request, slot)
            registration = self._adapter(request, slot)
            if slot["dispatch_attempt_started"]:
                return slot["receipts"]["dispatch"]
            prepared = slot["prepared"]
            native_bytes = decode_native_wrapper(
                self.resolve(prepared["body"]["native_request_ref"]),
                prepared["body"]["native_request_ref"],
            )
            try:
                self._context(request)
                now = self.clock()
                native_auth = registration["adapter"].verify_native_authority(
                    deepcopy(request), deepcopy(prepared), native_bytes, now
                )
                self._fresh(native_auth, now, native=True)
                gate = (
                    self.gate_check(request, prepared, native_auth, now)
                    if self.gate_check
                    else None
                )
                self._fresh(gate, now)
                if self.clock() >= min(
                    gate["valid_until_ms"], native_auth["valid_until_ms"]
                ):
                    raise ProtocolError(
                        "authority_stale",
                        "authority expired before durable dispatch decision",
                    )
            except ProtocolError as error:
                return self._receipt(slot, "dispatch", "blocked", error.code)
            slot["gate"] = gate
            slot["native_authority"] = native_auth
            slot["dispatch_attempt_started"] = True
            slot["dispatch_started_at_ms"] = self.clock()
            # The in-doubt receipt and marker commit together BEFORE crossing the boundary.
            self._receipt(
                slot, "dispatch", "in_doubt", "dispatch_attempt_started", gate=gate
            )
        self.failpoint("after_dispatch_marker")
        if self.clock() >= min(gate["valid_until_ms"], native_auth["valid_until_ms"]):
            with self.ledger.transaction():
                slot = self.ledger.get("handoff_slots", key)
                return self._receipt(
                    slot,
                    "dispatch",
                    "not_dispatched",
                    "authority_expired_before_native_call",
                )
        try:
            observation = registration["adapter"].dispatch(
                native_bytes, prepared["body"]["native_operation_key"]
            )
        except Exception:
            # Timeout/lost reply may conceal a completed effect; preserve the marker.
            observation = {"outcome": "in_doubt", "native_evidence_refs": []}
        self.failpoint("after_native_dispatch")
        with self.ledger.transaction():
            slot = self.ledger.get("handoff_slots", key)
            return self._observe(slot, "dispatch", observation)

    def _observe(self, slot, phase, observation):
        if not isinstance(observation, dict):
            observation = {}
        outcome = observation.get("outcome", "in_doubt")
        refs = observation.get("native_evidence_refs", [])
        if outcome not in {"not_dispatched", "dispatched", "in_doubt", "resolved"}:
            outcome = "in_doubt"
        if outcome in {"resolved", "dispatched"} and not refs:
            outcome = "in_doubt"
        if outcome == "not_dispatched":
            # Even a final absence observation cannot authorize redelivery. Missing
            # lookup results alone are never authoritative evidence of no effect.
            absence_check = self._adapter(slot["request"], slot)["final_absence_check"]
            if (
                observation.get("final_absence") is not True
                or not refs
                or absence_check is None
                or absence_check(deepcopy(observation), deepcopy(slot["prepared"]))
                is not True
            ):
                outcome = "in_doubt"
            prior = slot.get("native_observation", {})
            if prior.get("outcome") in {"dispatched", "resolved"}:
                outcome = "in_doubt"
        previous = slot.get("native_observation")
        if previous:
            slot.setdefault("native_observation_history", []).append(previous)
        slot["native_observation"] = {"outcome": outcome, "native_evidence_refs": refs}
        return self._receipt(
            slot, phase, outcome, "native_observation", native_refs=refs
        )

    def reconcile(self, request):
        # Native lookup is read-only. Admission/read authority is checked by the harness.
        with self.ledger.transaction():
            _, _, key = self._context(request, check_action=False)
            slot = self.ledger.get("handoff_slots", key)
            if slot is None:
                raise ProtocolError(
                    "handoff_unprepared", "no protected handoff disposition exists"
                )
            self._compatible(request, slot)
            registration = self._adapter(request, slot)
            if not slot["dispatch_attempt_started"]:
                return self._receipt(
                    slot, "reconcile", "not_dispatched", "no_dispatch_attempt"
                )
            native_key = slot["prepared"]["body"]["native_operation_key"]
        try:
            observation = registration["adapter"].reconcile(native_key)
        except Exception:
            observation = {"outcome": "in_doubt", "native_evidence_refs": []}
        with self.ledger.transaction():
            slot = self.ledger.get("handoff_slots", key)
            return self._observe(slot, "reconcile", observation)


class FakeAdapter:
    """Deterministic TEST-ONLY adapter: no network, orders, payments or fulfillment.

    The native ledger and evidence are synthetic. Inject the same ``operations``
    dictionary after a harness restart to model an independent native observation.
    This is not native adapter qualification or evidence of real-world execution.
    """

    test_only = True

    def __init__(
        self,
        *,
        contract_ref=None,
        operations=None,
        authorized=True,
        lose_reply=False,
        native_bytes=None,
    ):
        self.contract_ref = contract_ref or {
            "id": "test-only-adapter-contract",
            "digest": digest({"test_only": True}),
        }
        self.operations = operations if operations is not None else {}
        self.authorized = authorized
        self.lose_reply = lose_reply
        self.native_bytes = native_bytes
        self.dispatch_calls = 0
        self.prepare_calls = 0
        self.reconcile_calls = 0

    def prepare(self, request, payload, native_operation_key):
        self.prepare_calls += 1
        native = (
            self.native_bytes
            if self.native_bytes is not None
            else canonical(
                {
                    "test_only": True,
                    "native_operation_key": native_operation_key,
                    "request_payload": payload,
                }
            )
        )
        return {
            "native_bytes": native,
            "media_type": "application/json",
            "authorization_requirement_refs": [self.contract_ref],
            "reconciliation_profile_ref": self.contract_ref,
        }

    def verify_native_authority(self, request, prepared, native_bytes, now_ms):
        return {
            "allow": self.authorized,
            "valid_until_ms": now_ms + 1000,
            "evidence_refs": [self.contract_ref],
        }

    def dispatch(self, native_bytes, native_operation_key):
        self.dispatch_calls += 1
        if native_operation_key in self.operations:
            raise AssertionError("TEST ONLY: repeated native dispatch is forbidden")
        evidence = {
            "id": "test-only-native:" + native_operation_key,
            "native_key": native_operation_key,
            "payload_digest": "sha256:" + hashlib.sha256(native_bytes).hexdigest(),
        }
        self.operations[native_operation_key] = {
            "outcome": "dispatched",
            "native_evidence_refs": [content_ref(evidence)],
        }
        if self.lose_reply:
            raise TimeoutError("TEST ONLY: effect recorded but reply lost")
        return deepcopy(self.operations[native_operation_key])

    def reconcile(self, native_operation_key):
        self.reconcile_calls += 1
        return deepcopy(
            self.operations.get(
                native_operation_key,
                {"outcome": "in_doubt", "native_evidence_refs": []},
            )
        )
