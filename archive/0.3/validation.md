# Draft 0.3 authoring verification

**Checked October 8, 2026.** Follow the [setup instructions](README.md#check-the-documents), then run `python3 checks/validate.py` from the repository root.

- Three schemas are valid JSON Schema Draft 2020-12: semantic records, interaction envelopes and admission declarations.
- Twenty-two semantic records, six interaction envelopes and two admission declarations pass their respective structural schemas.
- Twenty-three supporting fictional policy/evidence documents have no adopted structural schema; they are included only in reference-integrity checks.
- All 264 local content references resolve with matching fixture digests; proof-reference payload digests match the authored unsigned payloads.
- The A2A construction templates parse as JSON and use explicit placeholders. They are not complete native requests, signed records or interoperability checks.
- Current Markdown local-link targets, code fences and Git whitespace are checked during authoring. The archived draft is historical.

The six contracts have undergone a read-only consistency review covering permitted actors, conditional issuance, direct adoption, capacity/withdrawal ordering, stable operation identity, refusal timing and absorbing refusal. Review is not proof that an implementation meets these requirements.

Proof fixtures reference an unimplemented documentation profile and fictional native evidence. No cryptographic proof, current authority, actual capability, human notification, refusal ordering, runtime negotiation, native integration, delivery quality or payment is verified. The digest helper is limited to the authored ASCII/safe-integer fixture values and is not a general RFC 8785 implementation.

The protocol testing regime remains deferred. These are document-authoring checks, not an adopted conformance or runtime test suite. No agent runtime or payment implementation was added.
