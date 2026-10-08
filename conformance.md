# Conformance status and proposed assessment

**ABP 0.4-draft · contract and reference-profile design · no implemented conformance suite**

The normative requirements are in the [core contract](contract.md), [governing interfaces C1–C8](contracts/README.md), selected [reference profile](profiles/reference-profile.md) and their schemas. Schema validity is only one part of conformance: authentic authority, exact adoption, shared ordering, principal recovery, protected handoff and evidence interpretation require the corresponding semantic checks.

## Scope of a claim

The ordinary bilateral path preserves publication/admission rules, qualified self-authorship, exact agreement, durable recovery and each distinct principal's protected refusal period. It does not require a transaction plan, composition machinery, an atomic bundle or downstream handoff code merely to negotiate and form an agreement.

Composition, handoff and lifecycle-evidence support are explicitly advertised features under the selected profile. An implementation must understand every feature and semantic requirement needed by its particular act, or block that dependent act. Advertising one feature does not imply another. Optional capabilities do not create a weaker bilateral mode or waive principal authority or recovery rights.

Conformance claims must identify the exact contract/profile version, supported features, understood action/evidence vocabularies, verification mechanisms and boundaries actually exercised. The [trust and failure model](design/trust-and-failure-model.md) distinguishes local enforcement, detectable violations and guarantees dependent on designated authorities or external systems. A declaration of support is not itself verification of those guarantees.

## What exists now

The [authoring checker](checks/validate.py) supplies feedback on schema validity, authored record structure, content references and selected consistency constraints. Its results belong in [validation.md](validation.md), with the revision and actual output. These checks do not demonstrate runtime conformance, cryptographic authorship, truthful capability, qualifying principal notice or live interoperability.

The user has authorized a proposed testing regime. [tests/PROPOSED.md](tests/PROPOSED.md) contains **27 unrun scenarios, P01–P27**, each with setup, stimulus, oracle and boundary. It is a reviewable proposal, not an implemented or passed acceptance suite. The contract and reference profile must be locked before executable conformance fixtures and independent interoperability testing are implemented.

The earlier [0.1 conformance plan](archive/0.1/conformance.md) is a historical artifact with different semantics. It is not the current suite or evidence that any current requirement has been exercised.

## Separate assessments after lock

- **Correctness and recovery:** Exercise the applicable normative guards and permitted effects, including exact references, authority, admission accounting, ordering, uncertain outcomes, principal protection and adapter-boundary evidence. Keep structural, cryptographic and behavioral results distinct.
- **Builder adoption:** Give an independent builder the [quick-start](docs/quickstart.md), default profile and future SDK/harness. Determine whether application capability, principal policy, actual constraints and declared hooks suffice without inventing protocol machinery or relying on undocumented explanations. P25 and P27 cover this separately from correctness.
- **Independent implementation:** A participant written from the specification without the reference SDK must reproduce the same agreed semantics and interoperate with a separately implemented peer. P26 exposes missing normative detail that a convenient SDK could conceal.

The SDK/harness design is not an implemented SDK. These assessments remain proposed and unrun; no ease-of-adoption or independent-interoperability result is claimed.

## Adapter and evidence boundary

Proposed boundary tests use deterministic fake adapters and controlled evidence. They may observe translated requests, eligibility decisions, stable operation correlation, reported dispositions and interpretation of claims. They stop before real native activity: no real service performance, order creation, mandate request, account charge, transfer or settlement is performed or verified.

A fake reports only a simulated fact under its declared semantics. A signature authenticates an assertion, not necessarily its underlying event; a successful submission is not fulfillment or settlement. Any later qualification of a specific native adapter, including AP2/UCP/ACP compatibility, requires its own explicit scope and evidence. This document selects or authorizes no such live integration, performance benchmark or general evaluator.
