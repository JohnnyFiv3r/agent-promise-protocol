"""Check v0.2 document structure and local references only.

This is an artifact-integrity helper, not a protocol conformance or behavior test.
Requires Python 3 and jsonschema. Run from the repository root: python3 checks/validate.py
No cryptographic proof, principal policy, authority, capability, clock, A2A, or
native order/payment mechanism is verified. A runtime testing regime is deferred.
"""
from pathlib import Path
import hashlib
import json

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'abp/0.2-draft'


def fixture_digest(value):
    # JCS-equivalent only for these authored ASCII/safe-integer fixture values.
    # This is not a general-purpose RFC 8785 implementation.
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    return 'sha256:' + hashlib.sha256(encoded).hexdigest()


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main():
    schema = json.loads((ROOT / 'schemas/contract.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    examples = {
        path.name: json.loads(path.read_text())
        for path in sorted((ROOT / 'examples').glob('*.json'))
    }
    records = {name: value for name, value in examples.items() if value.get('profile') == PROFILE}
    for name, value in records.items():
        errors = sorted(validator.iter_errors(value), key=lambda error: str(list(error.path)))
        if errors:
            raise ValueError(f'{name}: ' + '; '.join(error.message for error in errors))

    by_id = {}
    for name, value in examples.items():
        identifier = value.get('id')
        if not identifier or identifier in by_id:
            raise ValueError(f'{name}: missing or duplicate top-level fixture id')
        by_id[identifier] = value
    known_digests = {fixture_digest(value) for value in examples.values()}
    references = 0
    for name, value in examples.items():
        for item in walk(value):
            if 'id' in item and 'digest' in item:
                target = by_id.get(item['id'])
                if target is None or fixture_digest(target) != item['digest']:
                    raise ValueError(f'{name}: unresolved or mismatched local reference {item["id"]}')
                references += 1
            for field in ('previous_digest', 'previous_option_digest', 'previous_status_digest'):
                prior = item.get(field)
                if prior is not None and prior not in known_digests:
                    raise ValueError(f'{name}: unresolved {field}')
        if value.get('profile') == PROFILE:
            unsigned_payload = {key: item for key, item in value.items() if key != 'proofs'}
            for proof in value['proofs']:
                if proof['signed_payload_digest'] != fixture_digest(unsigned_payload):
                    raise ValueError(f'{name}: proof-reference payload digest does not match fixture bytes')

    print(json.dumps({
        'schema_structure': 'Draft 2020-12 valid',
        'protocol_record_shapes': len(records),
        'illustrative_policy_and_evidence_documents': len(examples) - len(records),
        'local_content_references_checked': references,
        'fixture_payload_digest_references': 'consistent',
        'cryptographic_proofs': 'nonvalidating fictional references; not verified',
        'capability_authority_status_and_clock_semantics': 'not verified',
        'runtime_and_protocol_testing': 'deferred; not performed',
    }, indent=2))


if __name__ == '__main__':
    main()
