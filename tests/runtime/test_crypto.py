import copy

import pytest

from agent_bazaar.crypto import (
    PROFILE,
    Registry,
    Signer,
    _b64,
    _unb64,
    canonical,
    content_ref,
    digest,
    strict_loads,
    unsigned_digest,
)
from agent_bazaar.errors import ProtocolError


def record():
    return {
        "id": "urn:request:1",
        "profile": PROFILE,
        "kind": "interaction_request",
        "issuer_agent_id": "agent:a",
        "issuer_principal_id": "principal:a",
        "created_at": "2026-10-08T00:00:00.000Z",
        "required_features": ["bilateral"],
        "required_extensions": [],
        "body": {
            "operation_id": "operation:1",
            "recipient_agent_id": "agent:b",
            "recipient_scope_id": "scope:b",
            "purpose": "submit_record",
            "subject_ref": {"id": "subject", "digest": "sha256:" + "a" * 64},
            "admission_basis_ref": {"id": "admission", "digest": "sha256:" + "b" * 64},
        },
    }


def setup_signed():
    signer = Signer("agent:a", "principal:a")
    registry = Registry()
    registry.register(signer)
    signed, proof = signer.sign(record())
    return signer, registry, signed, proof


def test_real_jcs_number_and_unicode_vectors():
    assert (
        canonical({"numbers": [333333333.33333329, 1e30, 4.50, 2e-3, 1e-27]})
        == b'{"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27]}'
    )
    assert canonical({"\ue000": 1, "\U0001f600": 2}) == '{"😀":2,"\ue000":1}'.encode()
    assert digest({"b": 2, "a": 1}) == digest({"a": 1, "b": 2})


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}',
        b'{"n":NaN}',
        b'{"n":Infinity}',
        b'{"s":"\\ud800"}',
        b'"\xff"',
        b'{"n":9007199254740992}',
        b"[" * 33 + b"0" + b"]" * 33,
    ],
)
def test_malformed_canonical_inputs_fail(raw):
    with pytest.raises(ProtocolError):
        strict_loads(raw)


def test_parse_is_bounded_and_does_not_count_braces_inside_strings():
    assert strict_loads(b'{"s":"[[[\\"{{{"}') == {"s": '[[["{{{'}
    with pytest.raises(ProtocolError):
        strict_loads(b'"abcd"', max_bytes=5)
    with pytest.raises(ProtocolError):
        canonical({"x": float("inf")})


def test_enrolled_signature_and_full_vs_unsigned_digest():
    signer, registry, signed, wrapper = setup_signed()
    assert (
        registry.verify(signed, lambda ref: wrapper, 100)["principal_id"]
        == "principal:a"
    )
    assert digest(signed) != unsigned_digest(signed)
    original = copy.deepcopy(signed)
    signed["body"]["operation_id"] = "changed"
    with pytest.raises(ProtocolError):
        registry.verify(signed, lambda ref: wrapper, 100)
    assert signer.sign(record())[0] == original  # Ed25519 deterministic exact proof.


@pytest.mark.parametrize(
    "mutation",
    ["extra_header", "algorithm", "scope", "payload", "signature", "embedded_key"],
)
def test_jws_tampering_cannot_hide_behind_rehashed_wrapper(mutation):
    signer, registry, signed, wrapper = setup_signed()
    h, p, s = wrapper["compact_jws"].split(".")
    header = strict_loads(_unb64(h))
    if mutation == "extra_header":
        header["extra"] = True
    elif mutation == "algorithm":
        header["alg"] = "EdDSA"
    elif mutation == "scope":
        header["abp_scope"] = [PROFILE + "/record/offer"]
    elif mutation == "payload":
        p = _b64(b"{}")
    elif mutation == "signature":
        s = _b64(b"\0" * 64)
    elif mutation == "embedded_key":
        header["jwk"] = signer.public_jwk()
    wrapper["compact_jws"] = _b64(canonical(header)) + "." + p + "." + s
    signed["proofs"][0]["native_proof_ref"] = content_ref(wrapper)
    with pytest.raises(ProtocolError):
        registry.verify(signed, lambda ref: wrapper, 100)


def test_incoming_keys_and_principal_claims_do_not_enroll_trust():
    _, _, signed, wrapper = setup_signed()
    with pytest.raises(ProtocolError):
        Registry().verify(signed, lambda ref: wrapper, 100)
    signer = Signer("agent:a", "principal:other")
    registry = Registry()
    registry.register(signer)
    signed["proofs"][0]["verification_method"] = signer.kid
    with pytest.raises(ProtocolError):
        registry.verify(signed, lambda ref: wrapper, 100)


def test_revoked_current_key_preserves_admitted_history_but_compromise_blocks():
    signer, registry, signed, wrapper = setup_signed()
    registry.revoke(signer.kid, 200)
    with pytest.raises(ProtocolError):
        registry.verify(signed, lambda ref: wrapper, 300)
    assert registry.verify_historical(signed, lambda ref: wrapper, 100)
    registry.revoke(signer.kid, 200, compromise=True)
    with pytest.raises(ProtocolError):
        registry.verify_historical(signed, lambda ref: wrapper, 100)


def test_scope_limit_and_required_features_are_not_inferred_from_new_record():
    signer, _, signed, wrapper = setup_signed()
    registry = Registry()
    registry.register(signer, allowed_scopes=[PROFILE + "/record/offer"])
    with pytest.raises(ProtocolError):
        registry.verify(signed, lambda ref: wrapper, 100)
    raw = record()
    raw["required_features"].append("future-feature")
    with pytest.raises(ProtocolError):
        signer.sign(raw)
    raw["required_features"] = ["bilateral"]
    raw["body"]["purpose"] = "dispatch_handoff"
    with pytest.raises(ProtocolError):
        signer.sign(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("issuer_agent_id", []),
        ("issuer_principal_id", None),
        ("kind", []),
        ("body", []),
        ("proofs", "pretend-proof"),
    ],
)
def test_untyped_untrusted_members_fail_with_protocol_error(field, value):
    _, registry, signed, wrapper = setup_signed()
    signed[field] = value
    with pytest.raises(ProtocolError):
        registry.verify(signed, lambda ref: wrapper, 100)
