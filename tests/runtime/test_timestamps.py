"""Schema-accepted timestamps retain their meaning through durable admission."""

from copy import deepcopy

import pytest

from agent_promise_protocol.crypto import content_ref
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.fixtures import Environment
from agent_promise_protocol.guards import timestamp
from test_composition import World, plan_record


@pytest.mark.parametrize("remaining_ms", [1000, -1000])
def test_signed_lowercase_validity_finishes_operation_and_releases_allowance(
    tmp_path, remaining_ms
):
    env = Environment(tmp_path)
    try:
        original = env.intent("lowercase")
        record = deepcopy(original)
        record["id"] = "intent:lowercase:revision2"
        record["body"].update(
            revision=2, previous_digest=content_ref(original)["digest"]
        )
        record["body"]["validity"].update(
            mode="expires_at",
            expires_at=timestamp(env.clock.now_ms + remaining_ms).lower(),
        )
        signed = env.sign("requester", record)
        receipt = env.invoke("requester", "requester", "submit_record", signed)
        request = env.last_request
        expected = "applied" if remaining_ms > 0 else "blocked"
        assert receipt["body"]["outcome"] == expected
        if remaining_ms < 0:
            assert receipt["body"]["reason_code"] == "evidence_stale"
        assert env.store.is_admitted(content_ref(signed)) is (remaining_ms > 0)
        assert all(value["terminal"] for _, value in env.ledger.items("operations"))
        assert all(value["in_flight"] == 0 for _, value in env.ledger.items("quota"))
        env.restart()
        assert env.deliver(request) == receipt
    finally:
        env.close()


def test_lowercase_plan_expiration_is_enforced_at_the_same_instant(tmp_path):
    world = World(tmp_path)
    try:
        plan = plan_record()
        plan["body"]["validity"].update(
            mode="expires_at", expires_at="1970-01-01t00:00:02.000z"
        )
        world.submit(plan)
        candidate = world.candidate(plan)
        world.bind(plan, candidate)
        world.composition.now_ms = lambda: 2000
        with pytest.raises(ProtocolError, match="composition_expired"):
            world.composition.validate_candidate(candidate)
    finally:
        world.ledger.close()
