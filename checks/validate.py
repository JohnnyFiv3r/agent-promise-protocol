"""Check v0.4 document structure and local references only.

This is an artifact-integrity helper, not a protocol conformance or behavior test.
Requires Python 3 and jsonschema. Run from the repository root: python3 checks/validate.py
No cryptographic proof, principal policy, authority, capability, clock, A2A, or
native order/payment mechanism is verified. Behavioral test proposals are in tests/PROPOSED.md; they are not executed here.
"""
from pathlib import Path
import hashlib
import json

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'abp/0.4-draft'
ADMISSION_PROFILE = 'abp/admission-policy/0.4-draft'


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
    schemas = {
        name: json.loads((ROOT / 'schemas' / f'{name}.schema.json').read_text())
        for name in ('contract', 'interaction', 'admission-policy')
    }
    registry = Registry().with_resources(
        (schema['$id'], Resource.from_contents(schema)) for schema in schemas.values()
    )
    validators = {}
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        validators[name] = Draft202012Validator(
            schema, registry=registry, format_checker=FormatChecker()
        )
    examples = {
        path.name: json.loads(path.read_text())
        for path in sorted((ROOT / 'examples').glob('*.json'))
    }
    groups = {'contract': {}, 'interaction': {}, 'admission-policy': {}}
    for name, value in examples.items():
        if value.get('profile') == ADMISSION_PROFILE:
            groups['admission-policy'][name] = value
        elif value.get('profile') == PROFILE:
            category = 'interaction' if value['kind'] in ('interaction_request', 'interaction_receipt') else 'contract'
            groups[category][name] = value
    records = {name: value for group in groups.values() for name, value in group.items()}
    for category, group in groups.items():
        for name, value in group.items():
            errors = sorted(validators[category].iter_errors(value), key=lambda error: str(list(error.path)))
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
            for field in ('previous_digest', 'previous_option_digest', 'previous_status_digest', 'previous_receipt_digest'):
                prior = item.get(field)
                if prior is not None and prior not in known_digests:
                    raise ValueError(f'{name}: unresolved {field}')
        if name in records:
            unsigned_payload = {key: item for key, item in value.items() if key != 'proofs'}
            for proof in value['proofs']:
                if proof['signed_payload_digest'] != fixture_digest(unsigned_payload):
                    raise ValueError(f'{name}: proof-reference payload digest does not match fixture bytes')

    print(json.dumps({
        'schema_structure': 'Three Draft 2020-12 schemas valid',
        'semantic_record_shapes': len(groups['contract']),
        'interaction_shapes': len(groups['interaction']),
        'admission_declaration_shapes': len(groups['admission-policy']),
        'supporting_documents_not_schema_validated': len(examples) - len(records),
        'local_content_references_checked': references,
        'fixture_payload_digest_references': 'consistent',
        'cryptographic_proofs': 'nonvalidating fictional references; not verified',
        'capability_authority_status_and_clock_semantics': 'not verified',
        'runtime_and_protocol_testing': 'proposed; not implemented or performed',
    }, indent=2))


if __name__ == '__main__':
    main()
