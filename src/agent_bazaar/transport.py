"""Strict native A2A 1.0 JSON-RPC carriage and pinned TLS1.3-mTLS I/O.

No transport acknowledgment implies semantic success. Callers must verify the
returned receipt and its referenced records through the harness.
"""

from __future__ import annotations

import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ssl
import threading
import time
from urllib.parse import unquote, urlsplit

from .crypto import canonical, check_ref, strict_loads
from .errors import ProtocolError
from .schema import validate

EXTENSION_URI = (
    "https://github.com/JohnnyFiv3r/agent-bazaar/blob/main/protocol-architecture.md#v04"
)
MAX_REQUEST = 1024 * 1024
HEADERS = {
    "A2A-Version": "1.0",
    "A2A-Extensions": EXTENSION_URI,
    "Content-Type": "application/json",
    "Accept-Encoding": "identity",
}


class NativeError(ProtocolError):
    def __init__(self, code: str, rpc_code: int, detail: str = ""):
        super().__init__(code, detail)
        self.rpc_code = rpc_code


def _headers(headers, *, response=False):
    result = {}
    for key, value in headers.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise NativeError("InvalidRequestError", -32600, "invalid header type")
        key = key.lower()
        if key in result:
            raise NativeError("InvalidRequestError", -32600, "duplicate HTTP header")
        result[key] = value
    if result.get("a2a-version") != "1.0":
        raise NativeError("VersionNotSupportedError", -32009)
    activated = [entry.strip() for entry in result.get("a2a-extensions", "").split(",")]
    if EXTENSION_URI not in activated:
        if response:
            raise ProtocolError(
                "internal_unresolved",
                "missing extension acknowledgment; recover the original operation",
            )
        raise NativeError("ExtensionSupportRequiredError", -32008)
    if result.get("content-encoding", "identity") != "identity":
        raise NativeError("InvalidRequestError", -32600, "compression is forbidden")
    if (
        result.get("content-type", "").split(";", 1)[0].strip().lower()
        != "application/json"
    ):
        raise NativeError("ContentTypeNotSupportedError", -32005)
    return result


def _message(envelope, records, *, message_id, context_id=None, response=False):
    validate(envelope)
    if not isinstance(message_id, str) or not message_id:
        raise NativeError("InvalidParamsError", -32602, "messageId required")
    if (
        not isinstance(records, list)
        or len(records) > 64
        or any(not isinstance(record, dict) for record in records)
    ):
        raise NativeError("InvalidParamsError", -32602, "embedded records limit/shape")
    message = {
        "messageId": message_id,
        "role": "ROLE_AGENT" if response else "ROLE_USER",
        "parts": [
            {
                "mediaType": "application/json",
                "data": {"bazaar": envelope, "records": records},
            }
        ],
        "extensions": [EXTENSION_URI],
    }
    if context_id is not None:
        message["contextId"] = context_id
    return message


def encode_request(request, records, *, message_id, rpc_id=1):
    if not isinstance(request, dict) or request.get("kind") != "interaction_request":
        raise NativeError("InvalidParamsError", -32602, "interaction_request required")
    if isinstance(rpc_id, bool) or not isinstance(rpc_id, (str, int)):
        raise NativeError(
            "InvalidRequestError", -32600, "JSON-RPC ID must be a string or integer"
        )
    wire = canonical(
        {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": "SendMessage",
            "params": {"message": _message(request, records, message_id=message_id)},
        }
    )
    if len(wire) > MAX_REQUEST:
        raise NativeError("InvalidRequestError", -32600, "request size limit")
    return dict(HEADERS), wire


def _parse_message(message, *, response=False):
    if not isinstance(message, dict) or set(message) - {
        "messageId",
        "contextId",
        "role",
        "parts",
        "extensions",
        "metadata",
    }:
        raise NativeError(
            "InvalidParamsError", -32602, "unsupported native message field"
        )
    if (
        message.get("role") != ("ROLE_AGENT" if response else "ROLE_USER")
        or not isinstance(message.get("messageId"), str)
        or not message["messageId"]
    ):
        raise NativeError(
            "InvalidParamsError", -32602, "invalid native message role/ID"
        )
    if response and (
        not isinstance(message.get("contextId"), str) or not message["contextId"]
    ):
        raise NativeError(
            "InvalidAgentResponseError", -32006, "server contextId required"
        )
    if "contextId" in message and (
        not isinstance(message["contextId"], str) or not message["contextId"]
    ):
        raise NativeError("InvalidParamsError", -32602, "invalid contextId")
    if message.get("extensions") != [EXTENSION_URI]:
        raise NativeError(
            "InvalidParamsError", -32602, "unsupported message extensions"
        )
    parts = message.get("parts")
    if (
        not isinstance(parts, list)
        or len(parts) != 1
        or not isinstance(parts[0], dict)
        or set(parts[0]) != {"mediaType", "data"}
        or parts[0].get("mediaType") != "application/json"
    ):
        raise NativeError(
            "InvalidParamsError", -32602, "exactly one JSON data part required"
        )
    data = parts[0]["data"]
    if (
        not isinstance(data, dict)
        or set(data) != {"bazaar", "records"}
        or not isinstance(data["records"], list)
        or len(data["records"]) > 64
        or any(not isinstance(record, dict) for record in data["records"])
    ):
        raise NativeError(
            "InvalidParamsError", -32602, "invalid Bazaar data part or record count"
        )
    envelope = data["bazaar"]
    if not isinstance(envelope, dict) or envelope.get("kind") != (
        "interaction_receipt" if response else "interaction_request"
    ):
        raise NativeError(
            "InvalidParamsError", -32602, "incorrect interaction envelope"
        )
    validate(envelope)
    if "metadata" in message:
        metadata = message["metadata"]
        if (
            not isinstance(metadata, dict)
            or set(metadata) != {EXTENSION_URI}
            or not isinstance(metadata[EXTENSION_URI], dict)
        ):
            raise NativeError(
                "InvalidParamsError", -32602, "unsupported message metadata"
            )
        hints = metadata[EXTENSION_URI]
        if set(hints) - {"interaction_ref", "subject_ref"}:
            raise NativeError("InvalidParamsError", -32602, "unknown metadata hint")
        if "interaction_ref" in hints:
            check_ref(hints["interaction_ref"], envelope)
        if "subject_ref" in hints:
            actual = envelope["body"].get("subject_ref")
            if (
                actual is None
                or not isinstance(hints["subject_ref"], dict)
                or {k: hints["subject_ref"].get(k) for k in ("id", "digest")}
                != {k: actual.get(k) for k in ("id", "digest")}
            ):
                raise NativeError(
                    "InvalidParamsError", -32602, "subject metadata mismatch"
                )
    return {
        "message_id": message["messageId"],
        "context_id": message.get("contextId"),
        "receipt" if response else "request": envelope,
        "records": data["records"],
    }


def decode_request(raw, headers):
    _headers(headers)
    wire = strict_loads(raw, max_bytes=MAX_REQUEST)
    if (
        not isinstance(wire, dict)
        or set(wire) != {"jsonrpc", "id", "method", "params"}
        or wire.get("jsonrpc") != "2.0"
        or isinstance(wire.get("id"), bool)
        or not isinstance(wire.get("id"), (str, int))
    ):
        raise NativeError("InvalidRequestError", -32600)
    if wire["method"] != "SendMessage":
        raise NativeError("MethodNotFoundError", -32601)
    if not isinstance(wire["params"], dict) or set(wire["params"]) != {"message"}:
        raise NativeError("InvalidParamsError", -32602)
    return {"rpc_id": wire["id"], **_parse_message(wire["params"]["message"])}


def encode_response(receipt, records, *, rpc_id, message_id, context_id):
    if (
        not isinstance(receipt, dict)
        or receipt.get("kind") != "interaction_receipt"
        or not isinstance(context_id, str)
        or not context_id
    ):
        raise NativeError("InvalidAgentResponseError", -32006)
    wire = canonical(
        {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "message": _message(
                    receipt,
                    records,
                    message_id=message_id,
                    context_id=context_id,
                    response=True,
                )
            },
        }
    )
    return dict(HEADERS), wire


def decode_response(raw, headers, *, request=None, rpc_id=None, max_bytes=MAX_REQUEST):
    _headers(headers, response=True)
    wire = strict_loads(raw, max_bytes=max_bytes)
    if (
        not isinstance(wire, dict)
        or set(wire) != {"jsonrpc", "id", "result"}
        or wire.get("jsonrpc") != "2.0"
        or not isinstance(wire["result"], dict)
        or set(wire["result"]) != {"message"}
    ):
        raise ProtocolError(
            "internal_unresolved",
            "direct semantic receipt absent; recover original operation",
        )
    if rpc_id is not None and wire["id"] != rpc_id:
        raise ProtocolError("internal_unresolved", "JSON-RPC correlation mismatch")
    parsed = {
        "rpc_id": wire["id"],
        **_parse_message(wire["result"]["message"], response=True),
    }
    if request is not None:
        body = parsed["receipt"]["body"]
        check_ref(body["request_ref"], request)
        if any(
            body.get(key) != request["body"].get(key)
            for key in ("operation_id", "recipient_scope_id", "recipient_agent_id")
        ):
            raise ProtocolError(
                "identity_mismatch", "receipt operation binding mismatch"
            )
    return parsed


def client_tls_context(*, cafile, certfile, keyfile):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.load_cert_chain(certfile, keyfile)
    return context


def server_tls_context(*, cafile, certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile=cafile)
    context.load_cert_chain(certfile, keyfile)
    return context


def _safe_url(url):
    try:
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
            or parsed.query
            or any(c in url for c in "\r\n\\")
        ):
            raise ValueError("unsupported URL")
        path = unquote(parsed.path or "/")
        if (
            any(part in {".", ".."} for part in path.split("/"))
            or "%" in path
            or any(c in path for c in "\r\n\\")
        ):
            raise ValueError("ambiguous path")
        return parsed
    except (ValueError, TypeError, AttributeError) as exc:
        raise ProtocolError(
            "evidence_unavailable", "forbidden evidence/service locator"
        ) from exc


def pinned_https_request(
    url,
    *,
    method="GET",
    body=None,
    headers=None,
    tls_context,
    certificate_digest,
    max_bytes,
    deadline=None,
):
    """Validate PKIX/hostname and leaf pin before sending any HTTP request bytes."""
    parsed = _safe_url(url)
    if (
        tls_context.verify_mode != ssl.CERT_REQUIRED
        or not tls_context.check_hostname
        or tls_context.minimum_version < ssl.TLSVersion.TLSv1_3
    ):
        raise ProtocolError(
            "authority_absent", "TLS1.3 PKIX and hostname validation required"
        )
    expires = (
        min(time.monotonic() + 15, deadline)
        if deadline is not None
        else time.monotonic() + 15
    )
    connection = http.client.HTTPSConnection(
        parsed.hostname,
        parsed.port or 443,
        context=tls_context,
        timeout=max(0.001, min(5, expires - time.monotonic())),
    )
    try:
        connection.connect()
        peer = connection.sock.getpeercert(binary_form=True)
        if (
            connection.sock.version() != "TLSv1.3"
            or "sha256:" + hashlib.sha256(peer).hexdigest() != certificate_digest
        ):
            raise ProtocolError("identity_mismatch", "TLS peer pin/version mismatch")
        connection.sock.settimeout(max(0.001, expires - time.monotonic()))
        outgoing = {
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            **(headers or {}),
        }
        connection.request(method, parsed.path or "/", body=body, headers=outgoing)
        response = connection.getresponse()
        response_headers = {}
        for key, value in response.getheaders():
            key = key.lower()
            if key in response_headers and key in {
                "content-length",
                "content-type",
                "content-encoding",
                "a2a-version",
                "a2a-extensions",
            }:
                raise ProtocolError(
                    "evidence_unavailable", "ambiguous duplicate response header"
                )
            response_headers[key] = value
        if (
            response.status != 200
            or response_headers.get("content-encoding", "identity") != "identity"
            or response_headers.get("content-type", "").split(";", 1)[0].strip().lower()
            != "application/json"
        ):
            raise ProtocolError(
                "evidence_unavailable",
                "HTTP status, media type or encoding is unusable",
            )
        length = response_headers.get("content-length")
        if length is not None and (not length.isdecimal() or int(length) > max_bytes):
            raise ProtocolError("evidence_unavailable", "response byte limit exceeded")
        response_socket = response.fp.raw._sock
        chunks, size = [], 0
        while not response.isclosed():
            remaining = expires - time.monotonic()
            if remaining <= 0:
                raise ProtocolError(
                    "evidence_unavailable", "response deadline exceeded"
                )
            # HTTPResponse may detach connection.sock after Connection: close.
            response_socket.settimeout(remaining)
            chunk = response.read1(min(65536, max_bytes + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > max_bytes:
                raise ProtocolError(
                    "evidence_unavailable", "response byte limit exceeded"
                )
        if length is not None and size != int(length):
            raise ProtocolError("evidence_unavailable", "incomplete response body")
        return response_headers, b"".join(chunks)
    except (OSError, http.client.HTTPException, ValueError) as exc:
        if isinstance(exc, ProtocolError):
            raise
        raise ProtocolError(
            "evidence_unavailable", "HTTPS evidence/policy request failed"
        ) from exc
    finally:
        connection.close()


class EvidenceRetriever:
    """One instance per semantic decision; explicit service allowlist and budget."""

    def __init__(self, *, tls_context, services, id_to_locator=None):
        self.tls_context = tls_context
        # Each administrator-configured service has origin, path_prefix,
        # certificate_digest, audience. No incoming object can add a service.
        self.services = list(services)
        self.id_to_locator = dict(id_to_locator or {})
        self.requests, self.bytes = 0, 0
        self._reserved_bytes = 0
        self.deadline = time.monotonic() + 30
        self._lock = threading.Lock()
        self._slots = threading.BoundedSemaphore(4)

    def retrieve(self, reference, *, wrapper_kind="semantic"):
        limits = {
            "semantic": 2 * 1024 * 1024,
            "proof": 3 * 1024 * 1024,
            "native": 4 * 1024 * 1024,
        }
        if wrapper_kind not in limits:
            raise ProtocolError("unsupported_semantics", "unknown wrapper profile")
        locator = reference.get("locator") or self.id_to_locator.get(
            reference.get("id")
        )
        parsed = _safe_url(locator)
        origin = f"https://{parsed.netloc}"
        path = unquote(parsed.path or "/")
        services = [
            service
            for service in self.services
            if service["origin"] == origin
            and (
                path == service["path_prefix"].rstrip("/")
                or path.startswith(service["path_prefix"].rstrip("/") + "/")
            )
        ]
        if len(services) != 1 or not services[0].get("audience"):
            raise ProtocolError(
                "evidence_unavailable", "locator outside enrolled service scope"
            )
        with self._lock:
            remaining_bytes = 16 * 1024 * 1024 - self.bytes - self._reserved_bytes
            if (
                self.requests >= 32
                or remaining_bytes <= 0
                or time.monotonic() >= self.deadline
            ):
                raise ProtocolError(
                    "evidence_unavailable", "decision retrieval budget exhausted"
                )
            byte_limit = min(limits[wrapper_kind], remaining_bytes)
            self._reserved_bytes += byte_limit
            self.requests += 1
        if not self._slots.acquire(timeout=max(0, self.deadline - time.monotonic())):
            with self._lock:
                self._reserved_bytes -= byte_limit
            raise ProtocolError(
                "evidence_unavailable", "retrieval concurrency deadline"
            )
        accounted = False
        try:
            _, raw = pinned_https_request(
                locator,
                tls_context=self.tls_context,
                certificate_digest=services[0]["certificate_digest"],
                max_bytes=byte_limit,
                deadline=self.deadline,
            )
            with self._lock:
                self._reserved_bytes -= byte_limit
                self.bytes += len(raw)
                accounted = True
                if self.bytes > 16 * 1024 * 1024:
                    raise ProtocolError(
                        "evidence_unavailable",
                        "decision retrieval byte budget exhausted",
                    )
            record = strict_loads(raw, max_bytes=limits[wrapper_kind])
            if not isinstance(record, dict):
                raise ProtocolError(
                    "evidence_unavailable", "retrieved object must be JSON object"
                )
            check_ref(reference, record)
            return record
        finally:
            if not accounted:
                with self._lock:
                    # Failed/truncated responses cannot silently reset byte budget.
                    self._reserved_bytes -= byte_limit
                    self.bytes += byte_limit
            self._slots.release()


def make_handler(
    callback, registry, clock_ms, context_id, *, max_response_bytes=MAX_REQUEST
):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_):
            pass  # Never log confidential negotiation bytes or credentials.

        def do_POST(self):
            rpc_id = None
            self.close_connection = True
            try:
                if (
                    not isinstance(self.connection, ssl.SSLSocket)
                    or self.connection.version() != "TLSv1.3"
                ):
                    raise ProtocolError(
                        "identity_mismatch", "authenticated TLS1.3 socket required"
                    )
                peer = registry.authenticate_peer(
                    self.connection.getpeercert(binary_form=True), clock_ms()
                )
                self.connection.settimeout(15)
                _headers(self.headers)
                lengths = self.headers.get_all("Content-Length", [])
                if (
                    len(lengths) != 1
                    or not lengths[0].isdecimal()
                    or not 0 < int(lengths[0]) <= MAX_REQUEST
                    or self.headers.get("Transfer-Encoding") is not None
                ):
                    raise NativeError(
                        "InvalidRequestError", -32600, "bounded content length required"
                    )
                raw = self.rfile.read(int(lengths[0]))
                if len(raw) != int(lengths[0]):
                    raise NativeError("JSONParseError", -32700)
                parsed = decode_request(raw, self.headers)
                rpc_id = parsed["rpc_id"]
                if peer["agent_id"] != parsed["request"]["issuer_agent_id"]:
                    raise ProtocolError(
                        "identity_mismatch",
                        "mTLS peer does not match interaction issuer",
                    )
                outcome = callback(parsed["request"], parsed["records"], peer)
                if (
                    not isinstance(outcome, (tuple, list))
                    or len(outcome) != 2
                    or not isinstance(outcome[0], dict)
                    or not isinstance(outcome[1], list)
                ):
                    raise NativeError(
                        "InvalidAgentResponseError",
                        -32006,
                        "callback must return receipt and supporting records",
                    )
                receipt, records = outcome
                if not isinstance(receipt.get("id"), str) or not receipt["id"]:
                    raise NativeError(
                        "InvalidAgentResponseError",
                        -32006,
                        "callback receipt ID required",
                    )
                response_headers, body = encode_response(
                    receipt,
                    records,
                    rpc_id=rpc_id,
                    message_id=receipt["id"],
                    context_id=context_id,
                )
                if len(body) > max_response_bytes:
                    raise NativeError(
                        "InvalidAgentResponseError",
                        -32006,
                        "reply exceeds disclosed bound",
                    )
                self.send_response(200)
                for key, value in response_headers.items():
                    self.send_header(key, value)
            except (ProtocolError, OSError) as exc:
                code = exc.rpc_code if isinstance(exc, NativeError) else -32600
                name = (
                    exc.code
                    if isinstance(exc, ProtocolError)
                    else "InvalidRequestError"
                )
                body = canonical(
                    {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "error": {"code": code, "message": name},
                    }
                )
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("A2A-Version", "1.0")
                self.send_header("A2A-Extensions", EXTENSION_URI)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)

    return Handler


def serve_tls(address, handler, ssl_context):
    if (
        ssl_context.minimum_version < ssl.TLSVersion.TLSv1_3
        or ssl_context.verify_mode != ssl.CERT_REQUIRED
    ):
        raise ProtocolError(
            "authority_absent", "server requires TLS1.3 mutual PKIX authentication"
        )
    server = ThreadingHTTPServer(address, handler)
    server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
    return server
