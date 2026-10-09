"""Renaming the project does not create implicit cross-namespace compatibility."""

from copy import deepcopy

import pytest

from agent_promise_protocol.crypto import (
    _b64,
    _unb64,
    canonical,
    content_ref,
    strict_loads,
)
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.schema import validate
from agent_promise_protocol.transport import NativeError, decode_request, encode_request
from test_crypto import setup_signed


def test_app_schema_rejects_legacy_abp_profile():
    _, _, signed, _ = setup_signed()
    validate(signed)
    legacy = deepcopy(signed)
    legacy["profile"] = "abp/0.4-draft"
    with pytest.raises(ProtocolError):
        validate(legacy)


def test_app_rejects_legacy_jws_headers_even_when_rehashed_and_signed():
    signer, registry, signed, proof = setup_signed()
    h, payload, _ = proof["compact_jws"].split(".")
    header = strict_loads(_unb64(h))
    header["typ"] = "abp-record+jws"
    header["abp_profile"] = header.pop("app_profile")
    header["abp_scope"] = header.pop("app_scope")
    header["crit"] = ["abp_profile", "abp_scope"]
    h = _b64(canonical(header))
    # Valid Ed25519 cryptography cannot turn an unsupported header into APP proof.
    signature = signer.private_key.sign((h + "." + payload).encode("ascii"))
    proof["compact_jws"] = h + "." + payload + "." + _b64(signature)
    signed["proofs"][0]["native_proof_ref"] = content_ref(proof)
    with pytest.raises(ProtocolError):
        registry.verify(signed, lambda ref: proof, 100)


def test_app_transport_rejects_legacy_wrapper_and_extension_identity():
    _, _, request, proof = setup_signed()
    headers, wire = encode_request(request, [proof], message_id="message:namespace")
    assert decode_request(wire, headers)["request"] == request
    legacy = strict_loads(wire)
    data = legacy["params"]["message"]["parts"][0]["data"]
    data["bazaar"] = data.pop("app")
    with pytest.raises(NativeError):
        decode_request(canonical(legacy), headers)
    old_headers = dict(headers)
    old_headers["A2A-Extensions"] = (
        "https://github.com/JohnnyFiv3r/agent-bazaar/blob/main/protocol-architecture.md#v04"
    )
    with pytest.raises(NativeError, match="ExtensionSupportRequiredError"):
        decode_request(wire, old_headers)
