# Agent-governing contracts

**ABP 0.4-draft · normative · MIT**

The default is **one bilateral agreement**: an agent asks, a counterpart offers its own qualified actions, the originator distributes one exact candidate, both agents adopt it, and every represented principal retains a protected opportunity to refuse. An ordinary agreement requires no transaction plan, composition engine, auction, atomic bundle, or native adapter.

These eight contracts define one agreement model. C1–C6 govern the baseline. C7 and C8 add explicitly negotiated features over that same model. A conforming harness verifies applicable requirements and preserves recoverable outcomes; it cannot grant itself authority, manufacture capability, or compel an autonomous agent to perform.

| Contract | Applies to | Governs and produces |
|---|---|---|
| [C1 — Publication and policy](01-publication-policy.md) | Baseline | Principal consent, privacy, permitted contact, current policy, and attributable publication permission |
| [C2 — Qualified actions](02-qualified-actions.md) | Baseline | Scoped intent, self-authored promises, offers, requests, capability, and authority |
| [C3 — Admission and negotiation](03-admission-negotiation.md) | Baseline | Bounded interaction, independent options, durable operations, receipts, retries, and withdrawal |
| [C4 — Exact formation](04-formation.md) | Baseline | One exact bilateral candidate, each party's adoption, protected selection, and one immutable accepted object |
| [C5 — Principal refusal](05-principal-refusal.md) | Baseline | Qualifying notice, positive protected periods, refusal, and pending/cleared/unresolved recovery evidence |
| [C6 — A2A and portable proof](06-a2a-evidence.md) | Baseline and selected features | Native carriage, feature activation, exact content identity, proof, and retrievable evidence |
| [C7 — Composition](07-composition.md) | Optional `composition` | Immutable component requirements, exact candidate bindings, phase-specific dependencies, and authorized rejection propagation |
| [C8 — Adapter boundary and lifecycle evidence](08-adapter-boundary.md) | Optional `adapter-handoff` and `lifecycle-evidence` | Protected preparation/dispatch/reconciliation and separate attributable native-execution, fulfillment, assessment, and settlement claims |

## One complete default path

[RP1](../profiles/reference-profile.md) selects the concrete verification, policy, ordering, retrieval, and notice mechanisms. Its default `supported_features` is `["bilateral"]`. Applications supply the capability's meaning, principal-approved permissions, truthful constraints/capacity, and relevant application and notice hooks. The [harness interface](../profiles/harness-interface.md) assigns protocol mechanics to the reusable harness; neither document claims a shipped implementation.

`composition`, `adapter-handoff`, and `lifecycle-evidence` are separate advertised features. `adapter-handoff` requires `lifecycle-evidence`; neither requires composition. Required features and semantics must be understood and accepted by every affected participant. Unsupported required meaning blocks the affected act instead of being approximated. Schema availability does not activate a feature.

Baseline portable proofs and current authority/status evidence remain mandatory. The optional `lifecycle-evidence` feature concerns downstream typed observations; it does not make core signature, delegation, or principal-recovery verification optional.

## Reading and authority

The [core contract](../contract.md) supplies shared semantics. [Current decisions](../decisions-v0.4.md) explicitly reconcile lifecycle scope and proposed testing with the [earlier decisions](../decisions-v0.2.md). C1–C8 provide the applicable normative requirements; advanced features do not create additional categories of agreement.

`MUST` and `MUST NOT` are requirements. `SHOULD` permits a documented exception preserving every `MUST`. `MAY` identifies an allowed choice. Conformance is to the selected version, negotiated features, and understood profiles. Schema validity alone does not establish cross-record correctness, authority, current status, or ordering.

## Machine-readable surfaces

- [Semantic records](../schemas/contract.schema.json): baseline publication through accepted-object recovery, plus feature-scoped composition, handoff, and lifecycle evidence.
- [Interaction requests and receipts](../schemas/interaction.schema.json): explicit recipient, admission basis, stable operation identity, and attributable processing outcome. The bilateral path uses `submit_record`, `finalize_candidate`, and `query_status`.
- [Admission declaration](../schemas/admission-policy.schema.json): shared accounting scope, eligibility, finite policy-selected allowances, replenishment, and protected control traffic.

These are interoperability surfaces, not a requirement to create a separate service for every contract. Existing identity, delegation, proof, policy, storage, and clock mechanisms retain their native responsibilities. Continuing permission is not a standing promise.

## Boundary and status

**Agent agreement, principal clearance, and downstream authorization remain separate.** Positive principal-recovery periods and usable refusal paths are universal. Optional handoff does not waive them; RP1 holds externally effective dispatch until relevant periods clear and current native authority is established.

Bazaar governs exact commitments, optional composition, the selected adapter boundary, and interpretation of attributed evidence. Native systems perform execution, commerce validation, payments, fulfillment, assessment, and settlement. No native implementation or live integration is supplied here.

[Worked examples](../examples/lifecycle-walkthroughs.md) are schematic. [Proposed tests](../tests/PROPOSED.md) stop at controlled adapter substitutes and injected evidence. The specification, profile, and proposed checks are not executed runtime-conformance or native-transaction evidence.
