"""RP1 JCS/Ed25519 proofs and explicitly enrolled identity bindings.

Proof verification authenticates a statement. It never grants permission to act.
The registry is configured by the realm administrator, never by incoming JSON.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Callable

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .errors import ProtocolError

PROFILE = "abp/0.4-draft"
PROFILE_URI = "https://github.com/JohnnyFiv3r/agent-bazaar/blob/main/profiles/reference-profile.md"
PROOF_PROFILE = PROFILE_URI + "#rp1-jws-ed25519"
FEATURES = frozenset(
    {"bilateral", "composition", "lifecycle-evidence", "adapter-handoff"}
)
MAX_SAFE = 9007199254740991
KINDS = frozenset(
    {
        "publication_contract",
        "intent",
        "promise",
        "offer",
        "candidate_terms",
        "terms_adoption",
        "accepted_offer",
        "finalization_notice",
        "refusal_event",
        "status_snapshot",
        "withdrawal_event",
        "admission_grant",
        "clarification",
        "negotiation_close",
        "transaction_plan",
        "composition_binding",
        "handoff_request",
        "prepared_handoff",
        "handoff_receipt",
        "lifecycle_evidence",
        "interaction_request",
        "interaction_receipt",
        "admission_policy_declaration",
    }
)
RUNTIME_PROFILE_TYPES = frozenset(
    PROFILE_URI + suffix
    for suffix in (
        "#rp1-principal-inbox/availability",
        "#rp1-durable-authority/recovery-observation",
        "#rp1-durable-authority/operation-outcome",
    )
)
PROFILE_TYPES = RUNTIME_PROFILE_TYPES | frozenset(
    PROFILE_URI + suffix
    for suffix in (
        "#rp1-v01/manifest",
        "#rp1-v01/registry",
        "#rp1-opa/policy-decision",
        "#rp1-durable-authority/ledger-event",
        "#rp1-principal-inbox/notice-bundle",
        "#rp1-principal-inbox/health-interval",
    )
)


def _json_check(value: Any, depth: int = 0, max_depth: int = 32) -> None:
    if depth >= max_depth and isinstance(value, (list, dict)):
        raise ProtocolError("invalid_record", "JSON nesting exceeds bound")
    if value is None or isinstance(value, (bool, str)):
        if isinstance(value, str):
            try:
                value.encode("utf-8", "strict")
            except UnicodeError as exc:
                raise ProtocolError("invalid_record", "invalid Unicode") from exc
        return
    if isinstance(value, int):
        if not -MAX_SAFE <= value <= MAX_SAFE:
            raise ProtocolError(
                "invalid_record", "integer outside interoperable JCS range"
            )
        return
    if isinstance(value, float):
        # The RFC8785 implementation checks binary64 finiteness and serialization.
        return
    if isinstance(value, list):
        for child in value:
            _json_check(child, depth + 1, max_depth)
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ProtocolError(
                    "invalid_record", "JSON member names must be strings"
                )
            _json_check(key, depth + 1, max_depth)
            _json_check(child, depth + 1, max_depth)
        return
    raise ProtocolError("invalid_record", "unsupported JSON value")


def canonical(value: Any) -> bytes:
    _json_check(value)
    try:
        return rfc8785.dumps(value)
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ProtocolError("invalid_record", "value is not RFC8785 JSON") from exc


def strict_loads(
    raw: bytes | str, *, max_bytes: int = 2 * 1024 * 1024, max_depth: int = 32
) -> Any:
    if not isinstance(raw, (bytes, str)):
        raise ProtocolError("invalid_record", "JSON bytes or text required")
    try:
        encoded = raw.encode("utf-8", "strict") if isinstance(raw, str) else raw
        if len(encoded) > max_bytes:
            raise ProtocolError("invalid_record", "JSON byte limit exceeded")
        text = encoded.decode("utf-8", "strict")
        # Bound parser recursion before constructing an attacker-controlled tree.
        depth, quoted, escape = 0, False, False
        for char in text:
            if quoted:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char in "[{":
                depth += 1
                if depth > max_depth:
                    raise ProtocolError("invalid_record", "JSON nesting exceeds bound")
            elif char in "]}":
                depth -= 1

        def pairs(items):
            obj = {}
            for key, value in items:
                if key in obj:
                    raise ProtocolError("invalid_record", "duplicate JSON member")
                obj[key] = value
            return obj

        def constant(_):
            raise ProtocolError("invalid_record", "nonfinite JSON number")

        parsed = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
        _json_check(parsed, max_depth=max_depth)
        canonical(parsed)
        return parsed
    except (UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, ProtocolError):
            raise
        raise ProtocolError("invalid_record", "malformed JSON") from exc


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def unsigned_digest(record: dict) -> str:
    return digest({key: value for key, value in record.items() if key != "proofs"})


def content_ref(record: dict) -> dict:
    if not isinstance(record.get("id"), str) or not record["id"]:
        raise ProtocolError("invalid_record", "content requires a nonempty ID")
    return {"id": record["id"], "digest": digest(record)}


def check_ref(reference: dict, value: dict) -> None:
    if (
        not isinstance(reference, dict)
        or set(reference) - {"id", "digest", "locator"}
        or not isinstance(value, dict)
    ):
        raise ProtocolError("invalid_record", "malformed content reference")
    if content_ref(value) != {
        "id": reference.get("id"),
        "digest": reference.get("digest"),
    }:
        raise ProtocolError("evidence_unavailable", "content reference mismatch")


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ProtocolError("invalid_record", "noncanonical base64url")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except ValueError as exc:
        raise ProtocolError("invalid_record", "invalid base64url") from exc
    if _b64(decoded) != value:
        raise ProtocolError("invalid_record", "noncanonical base64url")
    return decoded


def scope_for(record: dict, *, profile_types=PROFILE_TYPES) -> list[str]:
    if not isinstance(record, dict):
        raise ProtocolError("invalid_record", "signed record must be JSON object")
    if "kind" in record:
        if not isinstance(record["kind"], str) or record["kind"] not in KINDS:
            raise ProtocolError("unsupported_semantics", "unknown record kind")
        return [PROFILE + "/record/" + record["kind"]]
    if (
        not isinstance(record.get("type_uri"), str)
        or record["type_uri"] not in profile_types
    ):
        raise ProtocolError("unsupported_semantics", "unknown profile document type")
    return [PROFILE + "/profile-document/" + record["type_uri"]]


def required_features(record: dict) -> set[str]:
    if "kind" not in record or record.get("kind") == "admission_policy_declaration":
        return {"bilateral"}
    declared = record.get("required_features")
    if not isinstance(declared, list) or any(not isinstance(f, str) for f in declared):
        raise ProtocolError(
            "unsupported_semantics", "required_features missing or invalid"
        )
    if (
        len(declared) != len(set(declared))
        or "bilateral" not in declared
        or set(declared) - FEATURES
    ):
        raise ProtocolError("unsupported_semantics", "unsupported required features")
    implied = {"bilateral"}
    body = record.get("body", {})
    if not isinstance(body, dict):
        raise ProtocolError("invalid_record", "record body must be object")
    if (
        record.get("kind") in {"transaction_plan", "composition_binding"}
        or "composition" in body
    ):
        implied.add("composition")
    if record.get("kind") in {
        "handoff_request",
        "prepared_handoff",
        "handoff_receipt",
    } or body.get("purpose") in {
        "prepare_handoff",
        "dispatch_handoff",
        "reconcile_handoff",
    }:
        implied.update({"adapter-handoff", "lifecycle-evidence"})
    if record.get("kind") == "lifecycle_evidence" or "adapter-handoff" in declared:
        implied.add("lifecycle-evidence")
    if not implied <= set(declared):
        raise ProtocolError(
            "unsupported_semantics", "implied feature omitted from signed declaration"
        )
    return set(declared)


class Signer:
    def __init__(
        self,
        agent_id: str,
        principal_id: str,
        private_key=None,
        kid: str | None = None,
        *,
        profile_types=PROFILE_TYPES,
    ):
        if not agent_id or not principal_id:
            raise ValueError("agent and principal IDs required")
        self.agent_id, self.principal_id = agent_id, principal_id
        self.profile_types = frozenset(profile_types)
        self.private_key = private_key or Ed25519PrivateKey.generate()
        if isinstance(self.private_key, bytes):
            self.private_key = Ed25519PrivateKey.from_private_bytes(self.private_key)
        self.kid = (
            kid
            or "urn:agent-bazaar:key:"
            + hashlib.sha256(
                self.private_key.public_key().public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw
                )
            ).hexdigest()
        )

    def public_jwk(self) -> dict:
        return {
            "kty": "OKP",
            "crv": "Ed25519",
            "alg": "Ed25519",
            "kid": self.kid,
            "use": "sig",
            "key_ops": ["verify"],
            "x": _b64(
                self.private_key.public_key().public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw
                )
            ),
        }

    def sign(self, record: dict) -> tuple[dict, dict]:
        if not isinstance(record, dict):
            raise ProtocolError("invalid_record", "signed record must be object")
        result = copy.deepcopy(record)
        if (
            result.get("issuer_agent_id") != self.agent_id
            or result.get("issuer_principal_id", self.principal_id) != self.principal_id
        ):
            raise ProtocolError("identity_mismatch", "signer is not record issuer")
        scopes = scope_for(result, profile_types=self.profile_types)
        required_features(result)
        unsigned = {k: v for k, v in result.items() if k != "proofs"}
        header = {
            "alg": "Ed25519",
            "kid": self.kid,
            "typ": "abp-record+jws",
            "abp_profile": PROFILE,
            "abp_scope": scopes,
            "crit": ["abp_profile", "abp_scope"],
        }
        signing = _b64(canonical(header)) + "." + _b64(canonical(unsigned))
        compact = signing + "." + _b64(self.private_key.sign(signing.encode("ascii")))
        wrapper = {
            "id": "urn:agent-bazaar:proof:"
            + hashlib.sha256(compact.encode("ascii")).hexdigest(),
            "media_type": "application/jose",
            "compact_jws": compact,
        }
        result["proofs"] = [
            {
                "suite_uri": PROOF_PROFILE,
                "verification_method": self.kid,
                "signed_payload_digest": digest(unsigned),
                "issuer_agent_id": self.agent_id,
                "scope": scopes,
                "native_proof_ref": content_ref(wrapper),
            }
        ]
        return result, wrapper


@dataclass
class _Key:
    agent_id: str
    jwk: dict
    from_ms: int
    until_ms: int
    scopes: frozenset[str]
    revoked_ms: int | None = None
    compromise: bool = False


class Registry:
    """Explicit local enrollment API; not an unauthenticated registry distribution API.

    Historical verification must use a preserved historical Registry instance and an
    authoritative admission time. Current revocations are still applied when known.
    """

    def __init__(self, *, understood_profile_types=PROFILE_TYPES):
        self.identities: dict[str, dict] = {}
        self.keys: dict[str, _Key] = {}
        self.profile_types = frozenset(understood_profile_types)

    def register(
        self,
        signer: Signer,
        *,
        features=("bilateral",),
        roles=(),
        certificate_digests=(),
        active_from_ms=0,
        valid_until_ms=MAX_SAFE,
        allowed_scopes=None,
    ) -> None:
        self.enroll(
            signer.agent_id,
            signer.principal_id,
            signer.public_jwk(),
            features=features,
            roles=roles,
            certificate_digests=certificate_digests,
            active_from_ms=active_from_ms,
            valid_until_ms=valid_until_ms,
            allowed_scopes=allowed_scopes,
        )

    def enroll(
        self,
        agent_id,
        principal_id,
        public_jwk,
        *,
        features=("bilateral",),
        roles=(),
        certificate_digests=(),
        active_from_ms=0,
        valid_until_ms=MAX_SAFE,
        allowed_scopes=None,
    ):
        if set(public_jwk) != {
            "kty",
            "crv",
            "alg",
            "kid",
            "use",
            "key_ops",
            "x",
        } or any(
            public_jwk.get(k) != v
            for k, v in {
                "kty": "OKP",
                "crv": "Ed25519",
                "alg": "Ed25519",
                "use": "sig",
                "key_ops": ["verify"],
            }.items()
        ):
            raise ProtocolError("identity_mismatch", "invalid public verification JWK")
        if (
            len(_unb64(public_jwk["x"])) != 32
            or not isinstance(public_jwk["kid"], str)
            or not public_jwk["kid"]
        ):
            raise ProtocolError("identity_mismatch", "invalid enrolled key")
        fs = set(features)
        if (
            fs - FEATURES
            or "bilateral" not in fs
            or ("adapter-handoff" in fs and "lifecycle-evidence" not in fs)
        ):
            raise ProtocolError("unsupported_semantics", "invalid enrolled features")
        if not 0 <= active_from_ms < valid_until_ms <= MAX_SAFE:
            raise ProtocolError("invalid_record", "invalid enrollment interval")
        previous = self.identities.get(agent_id)
        if previous and previous["principal_id"] != principal_id:
            raise ProtocolError(
                "identity_mismatch", "agent already bound to another principal"
            )
        if public_jwk["kid"] in self.keys:
            raise ProtocolError("identity_mismatch", "key identifier already enrolled")
        all_scopes = {PROFILE + "/record/" + kind for kind in KINDS} | {
            PROFILE + "/profile-document/" + kind for kind in self.profile_types
        }
        selected = all_scopes if allowed_scopes is None else set(allowed_scopes)
        if not selected or selected - all_scopes:
            raise ProtocolError(
                "unsupported_semantics", "unsupported enrolled proof scope"
            )
        self.identities[agent_id] = {
            "agent_id": agent_id,
            "principal_id": principal_id,
            "features": sorted(fs),
            "roles": list(roles),
            "certificate_digests": list(certificate_digests),
            "active_from_ms": active_from_ms,
            "valid_until_ms": valid_until_ms,
        }
        self.keys[public_jwk["kid"]] = _Key(
            agent_id,
            copy.deepcopy(public_jwk),
            active_from_ms,
            valid_until_ms,
            frozenset(selected),
        )

    def revoke(self, kid: str, effective_ms: int, *, compromise: bool = False) -> None:
        key = self.keys[kid]
        key.revoked_ms = (
            effective_ms
            if key.revoked_ms is None
            else min(effective_ms, key.revoked_ms)
        )
        key.compromise = key.compromise or compromise

    def authenticate_peer(self, certificate_der: bytes, now_ms: int) -> dict:
        pin = "sha256:" + hashlib.sha256(certificate_der).hexdigest()
        matches = [
            entry
            for entry in self.identities.values()
            if pin in entry["certificate_digests"]
            and entry["active_from_ms"] <= now_ms < entry["valid_until_ms"]
        ]
        if len(matches) != 1:
            raise ProtocolError(
                "identity_mismatch", "unregistered or ambiguous mTLS peer"
            )
        return {**copy.deepcopy(matches[0]), "transport_certificate_digest": pin}

    def verify(self, record: dict, resolve: Callable, now_ms: int) -> dict:
        return self._verify(record, resolve, now_ms, historical=False)

    def verify_historical(
        self, record: dict, resolve: Callable, admitted_at_ms: int
    ) -> dict:
        return self._verify(record, resolve, admitted_at_ms, historical=True)

    def _verify(
        self, record: dict, resolve: Callable, at_ms: int, *, historical: bool
    ) -> dict:
        canonical(record)
        if not isinstance(record, dict):
            raise ProtocolError("invalid_record", "signed record must be object")
        if any(
            not isinstance(record.get(name), str) or not record[name]
            for name in ("id", "profile", "issuer_agent_id")
        ):
            raise ProtocolError(
                "invalid_record",
                "signed record identity fields must be nonempty strings",
            )
        if "kind" in record and (
            not isinstance(record.get("issuer_principal_id"), str)
            or not record["issuer_principal_id"]
        ):
            raise ProtocolError(
                "identity_mismatch", "semantic issuer principal is required"
            )
        expected_profile = (
            "abp/admission-policy/0.4-draft"
            if record.get("kind") == "admission_policy_declaration"
            else PROFILE
        )
        if record.get("profile") != expected_profile:
            raise ProtocolError(
                "unsupported_semantics", "unsupported signed record profile"
            )
        scopes = scope_for(record, profile_types=self.profile_types)
        fs = required_features(record)
        issuer = self.identities.get(record.get("issuer_agent_id"))
        if (
            issuer is None
            or record.get("issuer_principal_id", issuer["principal_id"])
            != issuer["principal_id"]
        ):
            raise ProtocolError("identity_mismatch", "issuer/principal not enrolled")
        if not issuer["active_from_ms"] <= at_ms < issuer["valid_until_ms"]:
            raise ProtocolError(
                "authority_absent", "identity inactive at verification time"
            )
        if not fs <= set(issuer["features"]):
            raise ProtocolError(
                "unsupported_semantics", "issuer did not enroll required features"
            )
        proofs = record.get("proofs")
        if not isinstance(proofs, list) or not proofs:
            raise ProtocolError("identity_mismatch", "proofs required")
        payload = canonical({k: v for k, v in record.items() if k != "proofs"})
        for proof in proofs:
            if not isinstance(proof, dict) or set(proof) != {
                "suite_uri",
                "verification_method",
                "signed_payload_digest",
                "issuer_agent_id",
                "scope",
                "native_proof_ref",
            }:
                raise ProtocolError("identity_mismatch", "invalid proof fields")
            if (
                proof["suite_uri"] != PROOF_PROFILE
                or proof["issuer_agent_id"] != issuer["agent_id"]
                or proof["scope"] != scopes
                or proof["signed_payload_digest"] != unsigned_digest(record)
            ):
                raise ProtocolError(
                    "identity_mismatch",
                    "proof profile, issuer, digest or scope mismatch",
                )
            if not isinstance(proof["verification_method"], str):
                raise ProtocolError("identity_mismatch", "invalid verification key ID")
            key = self.keys.get(proof["verification_method"])
            if (
                key is None
                or key.agent_id != issuer["agent_id"]
                or not set(scopes) <= key.scopes
            ):
                raise ProtocolError(
                    "identity_mismatch",
                    "verification key not enrolled for issuer/scope",
                )
            if (
                key.compromise
                or not key.from_ms <= at_ms < key.until_ms
                or (key.revoked_ms is not None and at_ms >= key.revoked_ms)
            ):
                raise ProtocolError(
                    "authority_absent",
                    "revoked, compromised or inactive verification key",
                )
            try:
                wrapper = resolve(proof["native_proof_ref"])
                check_ref(proof["native_proof_ref"], wrapper)
                if (
                    set(wrapper) != {"id", "media_type", "compact_jws"}
                    or wrapper["media_type"] != "application/jose"
                ):
                    raise ProtocolError(
                        "identity_mismatch", "invalid native proof wrapper"
                    )
                if len(canonical(wrapper)) > 3 * 1024 * 1024:
                    raise ProtocolError("invalid_record", "proof wrapper exceeds bound")
                parts = wrapper["compact_jws"].split(".")
                if len(parts) != 3:
                    raise ProtocolError("identity_mismatch", "invalid compact JWS")
                encoded_header, encoded_payload, encoded_signature = parts
                header_bytes = _unb64(encoded_header)
                header = strict_loads(header_bytes, max_bytes=16384)
                expected = {
                    "alg": "Ed25519",
                    "kid": proof["verification_method"],
                    "typ": "abp-record+jws",
                    "abp_profile": PROFILE,
                    "abp_scope": scopes,
                    "crit": ["abp_profile", "abp_scope"],
                }
                if (
                    header != expected
                    or header_bytes != canonical(expected)
                    or _unb64(encoded_payload) != payload
                ):
                    raise ProtocolError(
                        "identity_mismatch",
                        "JWS exact protected header or payload mismatch",
                    )
                Ed25519PublicKey.from_public_bytes(_unb64(key.jwk["x"])).verify(
                    _unb64(encoded_signature),
                    (encoded_header + "." + encoded_payload).encode("ascii"),
                )
            except (
                InvalidSignature,
                KeyError,
                TypeError,
                AttributeError,
                ValueError,
            ) as exc:
                if isinstance(exc, ProtocolError):
                    raise
                raise ProtocolError(
                    "identity_mismatch", "invalid signature or unavailable native proof"
                ) from exc
        return copy.deepcopy(issuer)
