from datetime import datetime, timedelta, timezone
import hashlib
from http.server import BaseHTTPRequestHandler
import ipaddress
import ssl
import threading

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from agent_promise_protocol.crypto import (
    Registry,
    Signer,
    canonical,
    content_ref,
    strict_loads,
)
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.transport import (
    EXTENSION_URI,
    EvidenceRetriever,
    NativeError,
    client_tls_context,
    decode_request,
    decode_response,
    encode_request,
    encode_response,
    make_handler,
    pinned_https_request,
    serve_tls,
    server_tls_context,
)
from test_crypto import record


def certificates(path):
    """Real temporary test PKI, not a TLS-verification bypass."""
    now = datetime.now(timezone.utc)
    ca_key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "APP test CA")])
    ca = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(False, False, False, False, False, True, True, False, False),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )
    (path / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    result = {"ca": str(path / "ca.pem")}
    for label, usage in (
        ("server", ExtendedKeyUsageOID.SERVER_AUTH),
        ("client", ExtendedKeyUsageOID.CLIENT_AUTH),
    ):
        key = ec.generate_private_key(ec.SECP256R1())
        cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, label)]))
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=1))
            .not_valid_after(now + timedelta(days=1))
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                    ]
                ),
                critical=False,
            )
            .add_extension(x509.ExtendedKeyUsage([usage]), critical=False)
            .sign(ca_key, hashes.SHA256())
        )
        (path / f"{label}.pem").write_bytes(
            cert.public_bytes(serialization.Encoding.PEM)
        )
        (path / f"{label}.key").write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        result[label] = {
            "certfile": str(path / f"{label}.pem"),
            "keyfile": str(path / f"{label}.key"),
            "pin": "sha256:"
            + hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest(),
        }
    return result


def signed_request():
    return Signer("agent:a", "principal:a").sign(record())[0]


def receipt_for(request):
    body = request["body"]
    ref = {"id": "result", "digest": "sha256:" + "c" * 64}
    result = {
        "id": "receipt:1",
        "profile": request["profile"],
        "kind": "interaction_receipt",
        "issuer_agent_id": "agent:b",
        "issuer_principal_id": "principal:b",
        "created_at": request["created_at"],
        "required_features": ["bilateral"],
        "required_extensions": [],
        "body": {
            "request_ref": content_ref(request),
            "operation_id": body["operation_id"],
            "recipient_agent_id": body["recipient_agent_id"],
            "recipient_scope_id": body["recipient_scope_id"],
            "revision": 1,
            "previous_receipt_digest": None,
            "outcome": "applied",
            "reason_code": "ok",
            "result_refs": [ref],
            "evidence_refs": [ref],
        },
    }
    return Signer("agent:b", "principal:b").sign(result)[0]


def test_native_a2a_roundtrip_and_receipt_binding():
    request = signed_request()
    headers, raw = encode_request(request, [], message_id="message:1", rpc_id="call:1")
    decoded = decode_request(raw, headers)
    assert decoded["request"] == request
    assert decoded["message_id"] == "message:1"
    receipt = receipt_for(request)
    headers, raw = encode_response(
        receipt, [], rpc_id="call:1", message_id="response:1", context_id="ctx:1"
    )
    assert (
        decode_response(raw, headers, request=request, rpc_id="call:1")["receipt"]
        == receipt
    )
    with pytest.raises(ProtocolError):
        decode_response(raw, headers, request=request, rpc_id="wrong-call")
    headers.pop("A2A-Extensions")
    with pytest.raises(ProtocolError, match="original operation"):
        decode_response(raw, headers, request=request)


@pytest.mark.parametrize(
    "mutate",
    [
        "extra_part",
        "old_kind",
        "old_role",
        "hidden_operation",
        "wrong_hint",
        "too_many_records",
        "method",
    ],
)
def test_reject_malformed_native_carriers(mutate):
    headers, raw = encode_request(signed_request(), [], message_id="message:1")
    wire = strict_loads(raw)
    message = wire["params"]["message"]
    if mutate == "extra_part":
        message["parts"].append({"text": "accept"})
    elif mutate == "old_kind":
        message["parts"][0]["kind"] = "data"
    elif mutate == "old_role":
        message["role"] = "user"
    elif mutate == "hidden_operation":
        message["parts"][0]["data"]["operation"] = "accept"
    elif mutate == "wrong_hint":
        message["metadata"] = {
            EXTENSION_URI: {
                "interaction_ref": {"id": "wrong", "digest": "sha256:" + "a" * 64}
            }
        }
    elif mutate == "too_many_records":
        message["parts"][0]["data"]["records"] = [{}] * 65
    elif mutate == "method":
        wire["method"] = "app/accept"
    with pytest.raises(ProtocolError):
        decode_request(canonical(wire), headers)


def test_native_activation_and_version_errors():
    headers, raw = encode_request(signed_request(), [], message_id="message:1")
    headers["A2A-Version"] = "0.3"
    with pytest.raises(NativeError) as failure:
        decode_request(raw, headers)
    assert failure.value.rpc_code == -32009
    headers["A2A-Version"] = "1.0"
    del headers["A2A-Extensions"]
    with pytest.raises(NativeError) as failure:
        decode_request(raw, headers)
    assert failure.value.rpc_code == -32008


@pytest.mark.parametrize("value", [None, [], "interaction_request", {"kind": []}])
def test_codec_rejects_untyped_envelopes(value):
    with pytest.raises(NativeError):
        encode_request(value, [], message_id="message:1")
    with pytest.raises(NativeError):
        encode_response(
            value, [], rpc_id=1, message_id="message:1", context_id="context:1"
        )


def test_untyped_embedded_envelope_kind_fails_before_callback():
    headers, raw = encode_request(signed_request(), [], message_id="message:1")
    wire = strict_loads(raw)
    wire["params"]["message"]["parts"][0]["data"]["app"]["kind"] = []
    with pytest.raises(NativeError):
        decode_request(canonical(wire), headers)


def test_real_tls13_mtls_a2a_handler(tmp_path):
    pki = certificates(tmp_path)
    caller = Signer("agent:a", "principal:a")
    registry = Registry()
    registry.register(caller, certificate_digests=[pki["client"]["pin"]])
    observed = []
    invalid_callback = [False]

    def apply(request, records, peer):
        observed.append(peer)
        if invalid_callback[0]:
            return None
        return receipt_for(request), []

    handler = make_handler(apply, registry, lambda: 100, "context:server")
    context = server_tls_context(
        cafile=pki["ca"],
        certfile=pki["server"]["certfile"],
        keyfile=pki["server"]["keyfile"],
    )
    server = serve_tls(("127.0.0.1", 0), handler, context)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client_context = client_tls_context(
        cafile=pki["ca"],
        certfile=pki["client"]["certfile"],
        keyfile=pki["client"]["keyfile"],
    )
    request, _ = caller.sign(record())
    headers, raw = encode_request(request, [], message_id="message:1")
    url = f"https://127.0.0.1:{server.server_port}/a2a"
    try:
        response_headers, response_raw = pinned_https_request(
            url,
            method="POST",
            body=raw,
            headers=headers,
            tls_context=client_context,
            certificate_digest=pki["server"]["pin"],
            max_bytes=1024 * 1024,
        )
        assert (
            decode_response(response_raw, response_headers, request=request)["receipt"][
                "body"
            ]["outcome"]
            == "applied"
        )
        assert observed[0]["agent_id"] == "agent:a"
        with pytest.raises(ProtocolError, match="pin"):
            pinned_https_request(
                url,
                method="POST",
                body=raw,
                headers=headers,
                tls_context=client_context,
                certificate_digest="sha256:" + "0" * 64,
                max_bytes=1024 * 1024,
            )
        assert len(observed) == 1  # pin mismatch sent no HTTP operation.
        no_client_cert = ssl.create_default_context(cafile=pki["ca"])
        no_client_cert.minimum_version = ssl.TLSVersion.TLSv1_3
        with pytest.raises(ProtocolError):
            pinned_https_request(
                url,
                method="POST",
                body=raw,
                headers=headers,
                tls_context=no_client_cert,
                certificate_digest=pki["server"]["pin"],
                max_bytes=1024 * 1024,
            )
        invalid_callback[0] = True
        with pytest.raises(ProtocolError):
            pinned_https_request(
                url,
                method="POST",
                body=raw,
                headers=headers,
                tls_context=client_context,
                certificate_digest=pki["server"]["pin"],
                max_bytes=1024 * 1024,
            )
        invalid_callback[0] = False
        response_headers, response_raw = pinned_https_request(
            url,
            method="POST",
            body=raw,
            headers=headers,
            tls_context=client_context,
            certificate_digest=pki["server"]["pin"],
            max_bytes=1024 * 1024,
        )
        assert (
            decode_response(response_raw, response_headers, request=request)["receipt"][
                "body"
            ]["outcome"]
            == "applied"
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_real_tls_evidence_digest_allowlist_and_budget(tmp_path):
    pki = certificates(tmp_path)
    value = {"id": "urn:evidence:1", "body": {"test": "controlled"}}

    class EvidenceHandler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            body = canonical(value)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = serve_tls(
        ("127.0.0.1", 0),
        EvidenceHandler,
        server_tls_context(
            cafile=pki["ca"],
            certfile=pki["server"]["certfile"],
            keyfile=pki["server"]["keyfile"],
        ),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"https://127.0.0.1:{server.server_port}"
    retriever = EvidenceRetriever(
        tls_context=client_tls_context(
            cafile=pki["ca"],
            certfile=pki["client"]["certfile"],
            keyfile=pki["client"]["keyfile"],
        ),
        services=[
            {
                "origin": origin,
                "path_prefix": "/evidence/",
                "certificate_digest": pki["server"]["pin"],
                "audience": "controlled-evidence-service",
            }
        ],
    )
    reference = {**content_ref(value), "locator": origin + "/evidence/1"}
    try:
        assert retriever.retrieve(reference) == value
        with pytest.raises(ProtocolError):
            retriever.retrieve({**reference, "digest": "sha256:" + "a" * 64})
        for suffix in (
            "/private/1",
            "/evidence/../private/1",
            "/evidence/%2e%2e/private/1",
            "/evidence/1?token=secret",
            "/evidence/1#frag",
        ):
            with pytest.raises(ProtocolError):
                retriever.retrieve({**reference, "locator": origin + suffix})
        retriever.requests = 32
        with pytest.raises(ProtocolError, match="budget"):
            retriever.retrieve(reference)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
