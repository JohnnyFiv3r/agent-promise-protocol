# Contributing to Agent Promise Protocol

Agent Promise Protocol is an original MIT-licensed protocol specification in draft. Contributions should clarify interoperable behavior from publication policy through agreement, protected recovery, composition and adapter handoff/evidence. A2A carries communication; native order validation, payment, settlement and fulfillment remain beyond the adapter boundary.

Describe the concrete ambiguity or use case a change addresses. Keep the normative contract, schema, illustrative records and design decisions consistent. Clearly distinguish a proposed choice from an adopted requirement. Preserve the historical draft in `archive/0.1/` rather than bringing its superseded requirements into the current contract.

Use related projects as cited inspiration. Do not copy third-party implementation code, schemas or test suites into this repository. Submit original contributions under the repository's [MIT license](LICENSE), and keep secrets, credentials and private customer or negotiation records out of examples.

Start with the [implementer guide](docs/implementer-guide.md) and run the [document and runtime checks](validation.md#reproduce-the-checks) relevant to your change. Changes to runtime behavior need a regression that checks the affected guarantee; schema or fixture changes must keep the packaged schema copies and authored references consistent. Report the exact checked revision, commands, failures and skips. The actual OPA test requires the separately installed pinned executable; a skipped integration is not a successful check.

The repository includes reference runtime **0.1.0** for **APP 0.4-draft** and implementation-specific behavioral tests. Keep those results separate from schema validation, the broader [proposed scenarios](tests/PROPOSED.md), and independent interoperability. The [conformance assessment](conformance.md) records the remaining coverage and deployment limits. Do not replace historical validation artifacts with claims about a newer source state.
