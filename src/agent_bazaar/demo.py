"""Run controlled protocol scenarios; never contact a real native service."""

import argparse
import json
from pathlib import Path
import tempfile

from .crypto import content_ref
from .fixtures import Environment


def run_demo(directory):
    directory = Path(directory)
    result = {
        "runtime": "Agent Bazaar reference runtime 0.1",
        "mode": "controlled simulation",
        "evidence_scope": {
            "protocol_signatures": "real Ed25519/JCS verification",
            "authority_storage": "local durable SQLite WAL/FULL",
            "clock": "ControlledClock; no NTS service",
            "policy": "explicit TestPolicy grants; no live OPA deployment",
            "principal_inbox_and_health": "signed simulated service evidence",
            "native_effects": "FakeAdapter in-memory observations only",
            "network_calls": 0,
            "real_orders_payments_or_research_performance": False,
        },
        "scenarios": {},
    }

    env = Environment(directory / "bilateral")
    try:
        agreement = env.bilateral()["accepted"]
        pending = env.status(agreement)["body"]["status"]
        request = env.handoff_request(agreement)
        preparation = env.handoff_phase(request, "prepare")
        before = env.handoff_phase(request, "dispatch")
        env.notify(agreement)
        env.advance_healthy(agreement)
        closed = env.status(agreement)["body"]["status"]
        dispatched = env.handoff_phase(request, "dispatch")
        env.handoff_phase(request, "dispatch")
        result["scenarios"]["bilateral"] = {
            "agreement_ref": content_ref(agreement),
            "initial_status": pending,
            "prepare_outcome": preparation["body"]["outcome"],
            "dispatch_before_clearance": before["body"]["outcome"],
            "cleared_status": closed,
            "dispatch_after_clearance": dispatched["body"]["outcome"],
            "simulated_native_calls_after_replay": env.adapter.dispatch_calls,
            "durable_ledger": str(env.path),
        }
    finally:
        env.close()

    env = Environment(directory / "refusal")
    try:
        agreement = env.bilateral("refusal")["accepted"]
        env.notify(agreement)
        env.advance_healthy(agreement, 100)
        receipt = env.refuse(agreement)
        env.require_applied(receipt)
        original_request = env.last_request
        refused = env.status(agreement)
        env.restart()
        recovered = env.deliver(original_request)
        current = env.status(agreement)
        handoff = env.handoff_request(agreement)
        env.handoff_phase(handoff, "prepare")
        blocked = env.handoff_phase(handoff, "dispatch")
        result["scenarios"]["refusal_at_deadline"] = {
            "agreement_ref": content_ref(agreement),
            "refusal_receipt": receipt["body"]["outcome"],
            "status": refused["body"]["status"],
            "status_after_restart": current["body"]["status"],
            "same_receipt_on_replay": content_ref(receipt) == content_ref(recovered),
            "dispatch_outcome": blocked["body"]["outcome"],
            "simulated_native_calls": env.adapter.dispatch_calls,
            "durable_ledger": str(env.path),
        }
    finally:
        env.close()

    env = Environment(directory / "composition")
    try:
        chain = env.compose()
        sources = chain["components"]["sources"]["accepted"]
        review = chain["components"]["review"]["accepted"]
        env.notify(review)
        env.advance_healthy(review)
        review_request = env.handoff_request(review)
        env.handoff_phase(review_request, "prepare")
        blocked = env.handoff_phase(review_request, "dispatch")
        env.notify(sources)
        env.advance_healthy([sources, review])
        source_request = env.handoff_request(sources)
        env.handoff_phase(source_request, "prepare")
        source_result = env.handoff_phase(source_request, "dispatch")
        review_result = env.handoff_phase(review_request, "dispatch")
        result["scenarios"]["three_agent_composition"] = {
            "negotiating_agents": [
                "agent:requester",
                "agent:researcher",
                "agent:reviewer",
            ],
            "bilateral_agreements": [content_ref(sources), content_ref(review)],
            "dependency": "review handoff requires sources principal clearance",
            "review_before_source_clearance": blocked["body"]["outcome"],
            "source_dispatch": source_result["body"]["outcome"],
            "review_after_source_clearance": review_result["body"]["outcome"],
            "simulated_native_calls": env.adapter.dispatch_calls,
            "durable_ledger": str(env.path),
        }
    finally:
        env.close()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Agent Bazaar controlled reference demonstrations"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser(
        "demo",
        help="run signed bilateral, refusal, composition and fake handoff scenarios",
    )
    demo.add_argument(
        "--directory",
        type=Path,
        help="fresh output directory for durable SQLite scenario ledgers",
    )
    args = parser.parse_args(argv)
    directory = args.directory or Path(tempfile.mkdtemp(prefix="agent-bazaar-demo-"))
    print(json.dumps(run_demo(directory), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
