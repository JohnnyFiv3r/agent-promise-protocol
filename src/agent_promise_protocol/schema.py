"""Structural validation against the pinned repository schemas plus RP1 features."""

from importlib.resources import files
import json
import re
from datetime import datetime

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry as SchemaRegistry, Resource

from .crypto import PROFILE, PROFILE_TYPES, canonical, required_features
from .errors import ProtocolError

SCHEMA_FILES = (
    "contract.schema.json",
    "interaction.schema.json",
    "admission-policy.schema.json",
)
_RESOURCES = files("agent_promise_protocol").joinpath("schemas")
_SCHEMAS = [
    json.loads(_RESOURCES.joinpath(name).read_text(encoding="utf-8"))
    for name in SCHEMA_FILES
]
_REGISTRY = SchemaRegistry().with_resources(
    (schema["$id"], Resource.from_contents(schema)) for schema in _SCHEMAS
)
_FORMATS = FormatChecker()


@_FORMATS.checks("date-time", raises=ValueError)
def _date_time(value):
    if not isinstance(value, str):
        return True
    if not re.fullmatch(
        r"\d{4}-\d\d-\d\d[Tt]\d\d:\d\d:\d\d(?:\.\d+)?(?:[Zz]|[+-]\d\d:\d\d)", value
    ):
        return False
    datetime.fromisoformat(value.upper().replace("Z", "+00:00"))
    return True


@_FORMATS.checks("uri")
def _uri(value):
    return not isinstance(value, str) or bool(
        re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s<>]*$", value)
    )


_VALIDATORS = [
    Draft202012Validator(schema, registry=_REGISTRY, format_checker=_FORMATS)
    for schema in _SCHEMAS
]


def validate(record: dict, *, profile_types=PROFILE_TYPES) -> None:
    canonical(record)
    if not isinstance(record, dict):
        raise ProtocolError("invalid_record", "record must be object")
    if "kind" in record and not isinstance(record["kind"], str):
        raise ProtocolError("invalid_record", "record kind must be string")
    if "type_uri" in record:
        expected = {
            "id",
            "profile",
            "type_uri",
            "issuer_agent_id",
            "issued_at",
            "body",
            "proofs",
        }
        if (
            set(record) != expected
            or record.get("profile") != PROFILE
            or not isinstance(record.get("type_uri"), str)
            or record["type_uri"] not in profile_types
        ):
            raise ProtocolError("unsupported_semantics", "unsupported profile document")
        if (
            any(
                not isinstance(record.get(key), str) or not record[key]
                for key in ("id", "issuer_agent_id", "issued_at")
            )
            or not isinstance(record["body"], dict)
            or not isinstance(record["proofs"], list)
            or not record["proofs"]
        ):
            raise ProtocolError("invalid_record", "malformed profile document")
        if not _FORMATS.conforms(record["issued_at"], "date-time"):
            raise ProtocolError("invalid_record", "invalid profile document timestamp")
        return
    index = (
        1
        if record.get("kind") in {"interaction_request", "interaction_receipt"}
        else 2
        if record.get("kind") == "admission_policy_declaration"
        else 0
    )
    errors = list(_VALIDATORS[index].iter_errors(record))
    if errors:
        raise ProtocolError("invalid_record", errors[0].message[:500])
    required_features(record)
