# Agent-governing contracts

**ABP 0.3-draft · normative · MIT**

These contracts specify what an Agent Bazaar participant MUST verify, may change and must preserve when communicating with another participant. A conforming harness enforces them before authorizing agent actions. They govern protocol behavior; they do not grant authority, compel another autonomous agent to perform, or replace native commerce contracts.

| Contract | Governs | Principal outputs |
|---|---|---|
| [C1 — Publication and policy](01-publication-policy.md) | Consent between principals, discovery/service sources and agent harnesses | Attributable publication permission and its current status |
| [C2 — Qualified actions](02-qualified-actions.md) | Emitted intent, own promises, offers and requests for another's promises | Qualified, self-authored acts with exact semantics |
| [C3 — Admission and negotiation](03-admission-negotiation.md) | Invitation, bounded interaction, multiple options, retries and withdrawal | Admitted operations, exact receipts and independent offer histories |
| [C4 — Exact formation](04-formation.md) | Candidate terms, each party's adoption, capacity and originator finalization | One immutable accepted object for the exact candidate |
| [C5 — Principal refusal](05-principal-refusal.md) | Notice, protected refusal period, ordering and current status | Evidence of pending windows, refusal, closed windows or unresolved status |
| [C6 — A2A and evidence](06-a2a-evidence.md) | Wire carriage, extension activation, content identity and portable proof | Attributable, retrievable records without changing native A2A semantics |

## Reading and authority

The [core contract](../contract.md) supplies common semantics. C1–C6 supply the normative operational requirements; their requirement identifiers are stable within this draft. [The fifteen design decisions](../decisions-v0.2.md) remain controlling. [The 0.3 authoring decisions](../decisions-v0.3.md) explain how previously implicit rules are made concrete.

`MUST` and `MUST NOT` are requirements. `SHOULD` permits a documented exception that preserves every `MUST`. `MAY` identifies an allowed choice. Conformance is always to the selected version and understood profiles. Schema validity alone is insufficient; cross-record, authority and ordering requirements remain normative even when JSON Schema cannot express them.

## Machine-readable surfaces

- [Semantic records](../schemas/contract.schema.json): publication, intent, promise, offer, invitation grant, clarification, contact closure, candidate, adoption, accepted object, notice, refusal, status and withdrawal.
- [Interaction requests and receipts](../schemas/interaction.schema.json): recipient, admission basis, stable operation identity and attributable processing outcome.
- [Admission declaration](../schemas/admission-policy.schema.json): shared accounting scope, eligibility, finite policy-selected allowances, replenishment and protected control traffic. Existing policy systems authenticate and enforce it.

The admission declaration is an interoperability surface for a principal's selected policy system. It does not replace that system or turn continuing permission into a standing promise. Existing proof suites, identity/delegation systems, storage and clocks retain their native verification rules.

## Boundary

The output is an accepted-offer object and the evidence needed to interpret it. AP2/UCP/ACP validation, paid-resource exchange, processors, settlement, fulfillment and delivery assessment remain downstream. No payment or executable agent runtime is authored here. The examples are fictional; the later testing regime remains undecided.
