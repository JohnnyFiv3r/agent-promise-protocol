# Agent Bazaar

**ABP 0.4-draft · October 8, 2026 · [MIT](LICENSE)**

An agent expresses an outcome. Other agents offer actions they are capable and authorized to perform. The originator selects an exact candidate for each counterparty agreement. Both agents adopt that same reference, and every represented principal retains a protected opportunity to refuse.

Agent Bazaar standardizes those promises and the evidence needed to coordinate them. It uses existing discovery, A2A communication and native execution/payment systems. An intent is not an offer to buy or supply the sought outcome; an offer is its author's qualified promise. Neither can issue another agent's promise.

## Start with one agreement

Read the **[quick-start design](docs/quickstart.md)** and **[default reference profile](profiles/reference-profile.md)**. The application supplies its capability, principal permissions, real constraints and relevant application/notice hooks. The reference harness is responsible for protocol mechanics. [The harness interface](profiles/harness-interface.md) specifies that division; an SDK/runtime has not been implemented.

The default path is bilateral. It does not require a transaction plan, composition engine, auction or atomic bundle. Composition, adapter handoff and lifecycle evidence are explicitly negotiated features over the same universal agreement model. Unknown required features block the affected act.

Keep three facts separate: **agent agreement**, **principal clearance**, and **downstream authorization**. Principal clearance never fabricates native action authority or a human signature.

## Contract and profile

- [Eight governing contracts](contracts/README.md): C1–C6 define the normal agreement path; C7 adds composition and C8 defines the adapter boundary and evidence.
- [Core model](contract.md) and [current decisions](decisions-v0.4.md): universal semantics and the explicit expansion of the earlier formation-only boundary.
- [Architecture](protocol-architecture.md), [adapter boundary](downstream-boundary.md), and [trust/failure model](design/trust-and-failure-model.md).
- [Schemas](schemas/contract.schema.json), [interaction envelopes](schemas/interaction.schema.json), and [admission declaration](schemas/admission-policy.schema.json).
- [Worked scenarios](examples/lifecycle-walkthroughs.md), [fictional records](examples/README.md), and [proposed tests](tests/PROPOSED.md).

The default reference profile chooses concrete existing verification, transport, policy and ordering mechanisms. Domain vocabularies define particular actions; the profile is not a research-report or payment-specific agreement format. Other understood profiles may realize the same core guarantees.

## Adapter boundary

Bazaar governs preparation, eligibility to dispatch, recovery of uncertain outcomes and interpretation of attributed evidence. Native systems perform execution, order validation, payment, fulfillment, assessment and settlement. Tests proposed here stop at controlled adapter substitutes and injected native evidence; they neither operate nor qualify those native systems.

Principal recovery is mandatory. RP1 allows side-effect-free preparation before clearance and holds externally effective dispatch until relevant windows clear and current native authority is established. A signature, refund field or `success` response cannot replace those checks.

## Status and checks

This is an authored specification and reference-profile design, with fictional examples. It is not a running harness, signed live agreement, conformance result or demonstrated interoperability. [Validation](validation.md) states exactly what has been checked. The test proposals are for review before contract/profile lock and later implementation.

With Python 3.10 or newer, from this repository:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python checks/validate.py
```

These checks validate schema structure and local fixture references, not cryptography, runtime behavior or native services.

Original specification, schemas and examples are MIT licensed. Related projects provide [research and inspiration](research/README.md); no comparator implementation code or imported test suites are used. See [contribution guidance](CONTRIBUTING.md). Historical snapshots preserve [0.3](archive/0.3/README.md) and [0.1](archive/0.1/README.md); [0.2](https://github.com/JohnnyFiv3r/agent-bazaar/tree/0011b504b706970c54a780d700be3efe444d4898) is in Git history.
