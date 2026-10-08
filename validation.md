# Draft 0.2 authoring verification

**Checked October 8, 2026.** Run `python3 checks/validate.py` from this directory (Python 3 and `jsonschema` required).

- The current semantic schema is valid JSON Schema Draft 2020-12.
- Nineteen protocol-record examples and twenty-one illustrative policy/evidence documents have been inspected by the structural/reference checker.
- All 210 local content references resolve with matching fixture digests; proof-reference payload digests match the authored unsigned payloads.
- Current Markdown links and code fences pass across twenty-two files outside the archive.
- Read-only semantic review checked offers-as-promises, policy-defined validity, independent alternatives, originator coordination, direct acceptance, distinct-principal windows and the post-handshake refusal boundary.

Proof fixtures explicitly reference an unimplemented documentation profile and fictional native evidence. No cryptographic proof, current authority, actual capability, human notification, refusal ordering, runtime negotiation, native integration, delivery quality or payment is verified by these checks. The digest helper is limited to the authored ASCII/safe-integer fixture values and is not a general RFC 8785 implementation.

The testing regime is deferred by the user. These checks are document-authoring validation, not an adopted conformance or runtime test suite. The archived draft's 63 cases, fixed research reviewer and payment workflow are superseded. No runtime or payment work was performed.
