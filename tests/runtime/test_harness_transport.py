"""Real TLS1.3/mTLS A2A carriage into the signed semantic harness.

Only the application domain and policy/clock are controlled fixtures. This test
uses certificate-chain validation, leaf pinning, HTTP, the native A2A codec,
real Ed25519 verification, C3 admission, C4 formation, and durable replay.
"""

import threading

from agent_bazaar.crypto import Registry, check_ref, content_ref
from agent_bazaar.fixtures import Environment
from agent_bazaar.harness import FEATURES
from agent_bazaar.records import ref_key
from agent_bazaar.transport import (
    client_tls_context,
    decode_response,
    encode_request,
    make_handler,
    pinned_https_request,
    serve_tls,
    server_tls_context,
)
from test_transport import certificates


def test_real_mtls_a2a_finalization_and_durable_replay(tmp_path):
    env = Environment(tmp_path / "realm")
    pki_dir = tmp_path / "pki"
    pki_dir.mkdir()
    pki = certificates(pki_dir)
    server = None
    thread = None
    try:
        bilateral = env.bilateral(finalize=False)
        candidate = bilateral["candidate"]
        assert env.ledger.items("formations") == []
        # Replace the explicitly simulated local peer with the actual test PKI
        # client certificate before generating or admitting the wire operation.
        wire_registry = Registry()
        for alias, signer in env.signers.items():
            certificate = (
                pki["client"]["pin"]
                if alias == "researcher"
                else env.ledger.get("transport_identity", signer.agent_id)
            )
            wire_registry.register(
                signer,
                features=FEATURES,
                roles=("principal-control",)
                if alias.endswith("_control")
                else ("agent", "notice"),
                certificate_digests=[certificate],
            )
        env.registry = wire_registry
        for harness in env.harnesses.values():
            harness.registry = wire_registry
        env.ledger.put("transport_identity", "agent:researcher", pki["client"]["pin"])
        request = env.make_request(
            "researcher",
            "requester",
            "finalize_candidate",
            candidate,
            operation_id="operation:real-mtls-finalize",
        )
        observed_peers = []

        def apply(incoming, records, peer):
            observed_peers.append(peer)
            receipt = env.harnesses["requester"].invoke(
                incoming, records=records, peer=peer
            )
            support = {}

            def include(record):
                support[ref_key(content_ref(record))] = record
                for proof in record.get("proofs", []):
                    wrapper = env.store.resolve(proof["native_proof_ref"])
                    support[ref_key(content_ref(wrapper))] = wrapper

            # Receipt itself is the A2A envelope. Its native proof and every
            # returned semantic result travel as actual supporting records.
            for proof in receipt["proofs"]:
                include(env.store.resolve(proof["native_proof_ref"]))
            for reference in (
                receipt["body"]["result_refs"] + receipt["body"]["evidence_refs"]
            ):
                include(env.store.resolve(reference))
            return receipt, list(support.values())

        handler = make_handler(
            apply, env.registry, lambda: env.clock.now_ms, "context:real-harness"
        )
        server = serve_tls(
            ("127.0.0.1", 0),
            handler,
            server_tls_context(
                cafile=pki["ca"],
                certfile=pki["server"]["certfile"],
                keyfile=pki["server"]["keyfile"],
            ),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        client_context = client_tls_context(
            cafile=pki["ca"],
            certfile=pki["client"]["certfile"],
            keyfile=pki["client"]["keyfile"],
        )
        # Independent client trust contains the enrolled authority key. Response
        # signature verification resolves wrappers exclusively from wire bytes.
        client_registry = Registry()
        client_registry.register(
            env.signers["requester"],
            features=FEATURES,
            certificate_digests=[pki["server"]["pin"]],
        )
        embedded = [candidate]
        embedded += [
            env.store.resolve(p["native_proof_ref"])
            for p in candidate["proofs"] + request["proofs"]
        ]
        results = []
        quota_after_first = None
        for attempt in range(2):
            rpc_id = f"rpc:finalize:{attempt}"
            headers, raw = encode_request(
                request,
                embedded,
                message_id=f"message:finalize:{attempt}",
                rpc_id=rpc_id,
            )
            response_headers, response_raw = pinned_https_request(
                f"https://127.0.0.1:{server.server_port}/a2a",
                method="POST",
                body=raw,
                headers=headers,
                tls_context=client_context,
                certificate_digest=pki["server"]["pin"],
                max_bytes=1024 * 1024,
            )
            decoded = decode_response(
                response_raw, response_headers, request=request, rpc_id=rpc_id
            )
            assert decoded["context_id"] == "context:real-harness"
            receipt = decoded["receipt"]
            response_records = {
                ref_key(content_ref(record)): record for record in decoded["records"]
            }

            def resolve_response(reference):
                record = response_records[ref_key(reference)]
                check_ref(reference, record)
                return record

            client_registry.verify(receipt, resolve_response, env.clock.now_ms)
            assert receipt["issuer_agent_id"] == "agent:requester"
            assert receipt["body"]["outcome"] == "applied"
            assert (
                receipt["body"]["revision"] == 2
            )  # pending admission, then committed result
            assert len(receipt["body"]["result_refs"]) == 1
            accepted = resolve_response(receipt["body"]["result_refs"][0])
            client_registry.verify(accepted, resolve_response, env.clock.now_ms)
            assert accepted["kind"] == "accepted_offer"
            assert accepted["body"]["candidate_ref"] == content_ref(candidate)
            assert accepted["body"]["initial_status"] == "pending_refusal_windows"
            results.append((receipt, accepted))
            if attempt == 0:
                quota_after_first = env.ledger.items("quota")
            else:
                assert env.ledger.items("quota") == quota_after_first

        assert results[0] == results[1]
        assert len(observed_peers) == 2
        assert all(peer["agent_id"] == "agent:researcher" for peer in observed_peers)
        assert all(
            peer["transport_certificate_digest"] == pki["client"]["pin"]
            for peer in observed_peers
        )
        assert len(env.ledger.items("formations")) == 1
        assert env.ledger.get("resource_used", "research-slots:researcher") == 1
        assert env.adapter.dispatch_calls == 0
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=5)
            assert not thread.is_alive()
        env.close()
