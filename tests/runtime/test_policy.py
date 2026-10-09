import json
from pathlib import Path
import socket
import subprocess
import time

import pytest

from agent_promise_protocol.crypto import content_ref, digest
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.policy import (
    OPAClient,
    TestPolicy,
    check_commit,
    timestamp,
    validate_result,
)
from agent_promise_protocol.transport import client_tls_context
from test_transport import certificates

NOW = 1791417600000


def policy_input():
    subject = {"id": "urn:subject:1", "kind": "offer", "body": {"test": "controlled"}}
    ref = {"id": "urn:owner-approval", "digest": "sha256:" + "c" * 64}
    return {
        "profile": "app-rp1/0.1-draft",
        "decision_id": "decision:1",
        "actor": {
            "agent_id": "agent:a",
            "principal_id": "principal:a",
            "transport_certificate_digest": "sha256:" + "a" * 64,
        },
        "act": "submit_record",
        "recipient_scope_id": "scope:b",
        "subject_ref": content_ref(subject),
        "subject": subject,
        "action_ref": None,
        "authority_refs": [ref],
        "clearance_refs": [],
        "dependency_evidence_refs": [],
        "native_authorization_refs": [],
        "authority_scope_id": "authority:1",
        "authority_revision": 1,
        "boundary_state_digest": "sha256:" + "b" * 64,
        "policy_bundle_ref": {"id": "bundle", "digest": "sha256:" + "d" * 64},
        "policy_data_ref": {"id": "data", "digest": "sha256:" + "e" * 64},
        "clock": {"now": timestamp(NOW), "uncertainty_ms": 50},
    }


def grants():
    return [
        {
            "agent_id": "agent:a",
            "principal_id": "principal:a",
            "acts": ["submit_record", "dispatch_handoff"],
            "subject_kinds": ["offer"],
            "authority_scope_id": "authority:1",
        }
    ]


def test_explicit_fixture_policy_scopes_and_current_state():
    request = policy_input()
    policy = TestPolicy(
        policy_bundle_ref=request["policy_bundle_ref"],
        policy_data_ref=request["policy_data_ref"],
        grants=grants(),
    )
    result = policy.evaluate(request, NOW)
    assert result["input_digest"] == digest(request)
    check_commit(
        result,
        authority_revision=1,
        boundary_state_digest=request["boundary_state_digest"],
        now_ms=NOW + 1,
    )
    with pytest.raises(ProtocolError):
        check_commit(
            result,
            authority_revision=2,
            boundary_state_digest=request["boundary_state_digest"],
            now_ms=NOW + 1,
        )
    with pytest.raises(ProtocolError):
        check_commit(
            result,
            authority_revision=1,
            boundary_state_digest=request["boundary_state_digest"],
            now_ms=NOW + 30000,
        )
    request["actor"]["principal_id"] = "other"
    with pytest.raises(ProtocolError):
        policy.evaluate(request, NOW)


def test_definite_owner_denial_retains_verified_decision_separate_from_outage():
    request = policy_input()
    policy = TestPolicy(
        policy_bundle_ref=request["policy_bundle_ref"],
        policy_data_ref=request["policy_data_ref"],
        grants=[],
    )
    with pytest.raises(ProtocolError) as failure:
        policy.evaluate(request, NOW)
    assert failure.value.code == "policy_denied"
    denial = failure.value.policy_result
    assert denial["allow"] is False
    assert denial["input_digest"] == digest(request)
    assert validate_result(denial, request, now_ms=NOW, require_allow=False) == denial
    request["clock"]["uncertainty_ms"] = 1001
    with pytest.raises(ProtocolError) as failure:
        policy.evaluate(request, NOW)
    assert not hasattr(failure.value, "policy_result")


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown",
        "stale_revision",
        "digest",
        "too_long",
        "undefined_allow",
        "unknown_reason",
    ],
)
def test_unknown_or_unbound_policy_results_fail_closed(mutation):
    request = policy_input()
    policy = TestPolicy(
        policy_bundle_ref=request["policy_bundle_ref"],
        policy_data_ref=request["policy_data_ref"],
        grants=grants(),
    )
    result = policy.evaluate(request, NOW)
    if mutation == "unknown":
        result["obligations"] = ["send secret"]
    elif mutation == "stale_revision":
        result["authority_revision"] = 0
    elif mutation == "digest":
        result["input_digest"] = "sha256:" + "0" * 64
    elif mutation == "too_long":
        result["valid_until"] = timestamp(NOW + 30001)
    elif mutation == "undefined_allow":
        result["allow"] = 1
    elif mutation == "unknown_reason":
        result["reason_codes"] = ["all_good"]
    with pytest.raises(ProtocolError):
        validate_result(result, request, now_ms=NOW)


def test_dispatch_needs_native_authority_and_has_five_second_lifetime():
    request = policy_input()
    policy = TestPolicy(
        policy_bundle_ref=request["policy_bundle_ref"],
        policy_data_ref=request["policy_data_ref"],
        grants=grants(),
    )
    request["act"] = "dispatch_handoff"
    with pytest.raises(ProtocolError, match="native_authority_absent"):
        policy.evaluate(request, NOW)
    request["native_authorization_refs"] = request["authority_refs"]
    with pytest.raises(ProtocolError, match="clearance_pending"):
        policy.evaluate(request, NOW)
    request["clearance_refs"] = request["authority_refs"]
    assert policy.evaluate(request, NOW)["valid_until"] == timestamp(NOW + 5000)


def test_real_opa_1211_over_tls13_mtls(tmp_path):
    root = Path(__file__).resolve().parents[2]
    binary = root / ".tools/opa"
    if not binary.exists():
        pytest.skip("optional pinned OPA1.21.1 executable not installed in .tools")
    version = subprocess.check_output([str(binary), "version"], text=True)
    assert "Version: 1.21.1\n" in version
    pki = certificates(tmp_path)
    request = policy_input()
    data = {
        "agent_promise_protocol_policy": {
            "policy_bundle_ref": request["policy_bundle_ref"],
            "policy_data_ref": request["policy_data_ref"],
        },
        "agent_promise_protocol_grants": grants(),
    }
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps(data))
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    listener.close()
    process = subprocess.Popen(
        [
            str(binary),
            "run",
            "--server",
            "--addr",
            f"127.0.0.1:{port}",
            "--authentication=tls",
            "--min-tls-version=1.3",
            "--tls-ca-cert-file",
            pki["ca"],
            "--tls-cert-file",
            pki["server"]["certfile"],
            "--tls-private-key-file",
            pki["server"]["keyfile"],
            str(root / "policies/rp1.rego"),
            str(data_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        for _ in range(100):
            try:
                connection = socket.create_connection(("127.0.0.1", port), timeout=0.1)
                connection.close()
                break
            except OSError:
                if process.poll() is not None:
                    pytest.fail(process.stderr.read().decode())
                time.sleep(0.02)
        client = OPAClient(
            f"https://127.0.0.1:{port}/v1/data/agent_promise_protocol/rp1/authorize",
            tls_context=client_tls_context(
                cafile=pki["ca"],
                certfile=pki["client"]["certfile"],
                keyfile=pki["client"]["keyfile"],
            ),
            server_certificate_digest=pki["server"]["pin"],
            policy_bundle_ref=request["policy_bundle_ref"],
            policy_data_ref=request["policy_data_ref"],
        )
        assert client.evaluate(request, NOW)["allow"] is True
        for value in (
            "é😀中文",
            "<&>",
            "\u2028\u2029",
            r"literal\u003c\u2028",
            "\\<&>\u2028",
            [1e30, 4.5, 0.002, 1e-27, 333333333.33333329],
        ):
            request["subject"]["body"]["test"] = value
            request["subject_ref"] = content_ref(request["subject"])
            assert client.evaluate(request, NOW)["allow"] is True
        request["subject"]["body"]["test"] = {"\ue000": 1, "😀": 2}
        request["subject_ref"] = content_ref(request["subject"])
        with pytest.raises(ProtocolError, match="exact input"):
            client.evaluate(request, NOW)
        request["subject"]["body"]["test"] = "controlled"
        request["subject_ref"] = content_ref(request["subject"])
        request["actor"]["principal_id"] = "not-the-owner"
        with pytest.raises(ProtocolError):
            client.evaluate(request, NOW)
        request["actor"]["principal_id"] = "principal:a"
        request["act"] = "dispatch_handoff"
        with pytest.raises(ProtocolError):
            client.evaluate(request, NOW)
    finally:
        process.terminate()
        process.communicate(timeout=5)
