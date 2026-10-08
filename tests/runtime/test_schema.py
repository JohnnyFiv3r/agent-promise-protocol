import json
from importlib.resources import files
from pathlib import Path

import pytest

from agent_bazaar.crypto import Signer
from agent_bazaar.errors import ProtocolError
from agent_bazaar.schema import SCHEMA_FILES, validate
from test_crypto import record


def test_bundled_schemas_match_authoritative_repository_bytes():
    authoritative = Path(__file__).resolve().parents[2] / "schemas"
    resources = files("agent_bazaar").joinpath("schemas")
    for name in SCHEMA_FILES:
        assert (
            resources.joinpath(name).read_bytes() == (authoritative / name).read_bytes()
        ), f"packaged schema drift: {name}"


def test_signed_interaction_and_repository_structural_fixtures():
    signed, _ = Signer("agent:a", "principal:a").sign(record())
    validate(signed)
    root = Path(__file__).resolve().parents[2] / "examples"
    for name in (
        "candidate-terms.json",
        "requester-publication.json",
        "admission-policy.json",
        "transaction-plan.json",
        "handoff-request.json",
    ):
        validate(json.loads((root / name).read_text()))


@pytest.mark.parametrize(
    "field,value",
    [
        ("unknown", True),
        ("required_features", ["bilateral", "future"]),
        ("created_at", "yesterday"),
        ("proofs", []),
    ],
)
def test_invalid_or_unknown_structure_rejected(field, value):
    signed, _ = Signer("agent:a", "principal:a").sign(record())
    signed[field] = value
    with pytest.raises(ProtocolError):
        validate(signed)


def test_optional_adapter_cannot_hide_required_feature():
    signed, _ = Signer("agent:a", "principal:a").sign(record())
    signed["body"]["purpose"] = "dispatch_handoff"
    with pytest.raises(ProtocolError):
        validate(signed)
