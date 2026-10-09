# Contract map: one agreement, optional composition and lifecycle features

**APP 0.4-draft · eight interface contracts**

The default path is one bilateral agreement governed by C1–C6. The same primitive supports monetary and noncommercial exchanges. C7 and C8 add explicitly negotiated capabilities; they are not required services or prerequisites for an ordinary agreement.

| ID | Contract | Scope and result |
|---|---|---|
| C1 | [Publication and policy](contracts/01-publication-policy.md) | Each principal controls consent, audience, permitted uses, admission, validity, privacy, and transaction eligibility. |
| C2 | [Qualified actions](contracts/02-qualified-actions.md) | An agent issues only its own qualified actions. Intent covers declaring/seeking; an offer issues conditional own promises. Requests do not issue another agent's promise. |
| C3 | [Admission and negotiation](contracts/03-admission-negotiation.md) | Recipient policy bounds traffic and work, may admit a first offer, and preserves independent options and recoverable operations. |
| C4 | [Exact formation](contracts/04-formation.md) | The initiating-record author coordinates each bilateral agreement. Both agents adopt one exact candidate under current authority, qualification, and selection guards. |
| C5 | [Principal refusal](contracts/05-principal-refusal.md) | Every represented principal retains a positive protected period with qualifying notice and usable refusal. Current evidence distinguishes pending, cleared, refused, and unresolved recovery. |
| C6 | [A2A and portable proof](contracts/06-a2a-evidence.md) | Existing A2A carries explicit operations and attributable exact records. Native message/task outcomes never substitute for semantic agreement or clearance. |
| C7 | [Optional composition](contracts/07-composition.md) | `composition` declares component requirements and dependencies, then binds each slot to one exact bilateral candidate without circular hashes or implied assent. |
| C8 | [Optional adapter boundary and lifecycle evidence](contracts/08-adapter-boundary.md) | `adapter-handoff` governs protected native handoff; `lifecycle-evidence` governs attributed downstream claims. Neither performs the native act it describes. |

## Adoption layers

| Layer | Responsibility |
|---|---|
| Universal contracts | Authorship, qualified promises, exact adoption, autonomy, protected principal recovery, and the semantics of selected optional features |
| [RP1 profile](profiles/reference-profile.md) and [harness interface](profiles/harness-interface.md) | Concrete verification, policy evaluation, durable replay/order, evidence retrieval, notice/refusal/status processing, and typed results |
| Application integration | Understood action semantics, truthful capability/capacity, principal-approved permissions, real constraints, and authorized application hooks |

RP1 defaults to `supported_features: ["bilateral"]`. `composition`, `lifecycle-evidence`, and `adapter-handoff` are explicit feature names. Handoff requires lifecycle evidence; the other features are not implied. An endpoint need not provide an adapter, plan, composition engine, auction, or atomic bundle to form a bilateral agreement and honor refusal.

Each affected participant must support and accept required feature semantics. A requested advanced feature cannot silently degrade to a simpler operation. Portable proof and principal-status evidence remain part of the baseline even when `lifecycle-evidence` is absent.

## Shared reference documents

- [Core contract](contract.md) and [current decisions](decisions-v0.4.md): shared model and explicit scope reconciliation.
- [Publication guide](publication-contract.md) and [promise model](promise-model.md): permission and qualified self-authorship.
- [Accepted-offer object](accepted-offer.md): agent agreement and principal-recovery interpretation.
- [Architecture](protocol-architecture.md) and [downstream boundary](downstream-boundary.md): how existing protocols retain their responsibilities.
- [Implementer guide](docs/implementer-guide.md), [quick-start](docs/quickstart.md) and [worked scenarios](examples/lifecycle-walkthroughs.md): one ordinary agreement before optional composition.

## Explicit boundary

Agent agreement does not establish principal clearance; clearance does not grant downstream authority. The optional handoff feature binds an exact action occurrence, frozen native translation, current eligibility, operation identity, and attributable observations. It does not issue native credentials or mandates, execute services, transfer funds, or establish native settlement.

The optional evidence feature can retain a fulfillment claim, assessment, native execution observation, settlement claim, or reservation disposition. Their selected semantics and native evidence determine what they establish. A claim, receipt, or orchestrator summary cannot manufacture an external result.

[Proposed tests](tests/PROPOSED.md) define the broader assessment through controlled adapter substitutes. The [reference runtime](docs/runtime.md) now has executable tests covering portions of that scope; [validation](validation.md) and [conformance](conformance.md) distinguish actual results from complete scenario qualification, live payment qualification and independent interoperability. The earlier formation-only boundary remains preserved in the [0.3 archive](archive/0.3/README.md).
