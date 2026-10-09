# Changelog

## APP 0.4 Reference Draft — `app-v0.4-draft.1`

Release date: October 9, 2026. Includes RP1 0.1-draft and the MIT Python reference runtime 0.1.0.

This release packages the protocol from consented publication through exact bilateral agreement and protected principal recovery. It adds optional composition and an explicit adapter boundary while keeping native execution, order authorization, payment and settlement in downstream systems.

Changes since the public 0.2 draft:

- Renamed Agent Bazaar (ABP) to Agent Promise Protocol (APP), including the repository, Python package/CLI and exact wire/proof/schema identifiers. This is an explicit namespace transition; APP does not relabel old signed records. See the [transition note](docs/namespace-transition.md).
- Eight governing contracts, with C1–C6 as the bilateral baseline and C7/C8 as optional composition and adapter features.
- Qualified action and promise provenance, exact candidate/adoption references, recipient-scoped admission budgets, durable replay and principal-refusal handling.
- A2A 1.0 JSON-RPC binding, three versioned JSON schemas and an explicit required-feature model.
- RP1's concrete choices for proofs, policy, transport, evidence and scoped authority, with the APP identifiers pinned in release metadata.
- Optional multi-agent plans composed from ordinary bilateral agreements, with immutable component bindings and explicit dependency gates.
- Participant-owned or delegated journal custody, optional connector/discovery providers and scoped decision authority. No mandatory APP operator or global ledger.
- A Python runtime with real JCS/Ed25519 verification, OPA integration, mutual TLS, durable SQLite state, controlled principal recovery and a fake adapter.
- Executable correctness and integration tests, release checks, an installed-package smoke check and an implementer guide.

The runtime demonstrates one explicitly delegated shared authority realm. Complete independent-store formation, independently authored interoperability, hosted tenant isolation, production principal channels and scale qualification remain separate work. The release makes no claim of live AP2/UCP/ACP, service delivery, payment or settlement integration.

The [validation record](validation.md) distinguishes historical runs from the machine-readable report attached to this release. Fictional authored examples remain separate from dynamically signed runtime fixtures.

## Earlier Agent Bazaar public contract draft 0.2

Published October 8, 2026 at [`0011b50`](https://github.com/JohnnyFiv3r/agent-promise-protocol/commit/0011b504b706970c54a780d700be3efe444d4898). This was the initial public repository snapshot. Earlier 0.1 and intermediate 0.3 design material remain available in the archive; their superseded requirements are not current requirements.
