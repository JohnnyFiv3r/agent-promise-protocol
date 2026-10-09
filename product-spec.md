# Product specification: Agent Promise Protocol

**APP 0.4-draft · Owner: John Inniger · MIT licensed**

An agent expresses what it seeks. Other agents offer qualified actions. The originator selects and distributes one exact candidate for each counterparty agreement. Both agents adopt those terms, and every represented principal retains a protected opportunity to refuse.

Agent Promise Protocol makes that interaction portable across agent harnesses, discovery services, and product domains. Its default is one bilateral agreement. A service can offer an MCP endpoint, API capability, dataset, document analysis, physical service, or noncommercial information exchange without adopting a different agreement format.

## Start with the ordinary agreement

1. The principal supplies permission to publish, receive contact, issue qualified actions, and adopt terms, together with real limits and the designated notice/refusal integration.
2. The agent emits an intent. Its qualified act of declaring or seeking an outcome does not promise to purchase, supply, or successfully obtain that outcome.
3. A counterpart issues an offer when current recipient policy permits it. A bounded first offer needs no additional invitation when the policy already admits it. The offer issues only its author's conditional own promises.
4. Agents clarify or revise offers within their budgets. Several named alternatives may coexist, with explicit shared-capacity or exclusivity constraints. Validity is policy-defined; silence and exhausted budgets do not invent a resolution.
5. The declared originator/coordinator distributes one exact candidate reference containing complete terms, selected actions, current policy requirements, and positive principal-recovery rules. Participants do not independently reconstruct equivalent-looking terms.
6. Each agent adopts that same candidate and only its own required actions. Direct acceptance does not require a reciprocal offer or an invented performance obligation. The coordinator records one immutable accepted object.
7. The harness provides qualifying notice, a usable refusal path, and authoritative status. The application distinguishes agreement formed from recovery pending, cleared, refused, or unresolved. A valid refusal remains absorbing for that accepted object.
8. Any subsequent native action still requires its own current authorization and must preserve the relevant principal rights. Agreement, clearance, and native authority are separate facts.

This path requires no transaction plan, composition engine, auction, atomic bundle, native adapter, or payment mechanism. The baseline operations are `submit_record`, `finalize_candidate`, and `query_status`.

## Three adoption layers

| Layer | Responsibility |
|---|---|
| Universal contracts | Qualified self-authorship, exact terms and adoption, agent autonomy, principal recovery, and semantics of selected optional features |
| [Default reference profile](profiles/reference-profile.md) and [harness interface](profiles/harness-interface.md) | Concrete verification, policy evaluation, exact-reference handling, durable replay/order, evidence retrieval, admission, and notice/refusal/status mechanics |
| Application integration | Domain meaning, truthful capability and capacity, principal-approved permissions, real constraints, and authorized application hooks |

Applications should connect an existing capability and its policies without inventing protocol machinery. The harness cannot manufacture competence, legitimate delegation, sufficient capacity, truthful native evidence, or reversible effects. RP1 specifies one complete default interoperability path. The [reference runtime](docs/runtime.md) supplies Python implementation hooks; the high-level facade in the [harness interface](profiles/harness-interface.md) remains a proposed SDK interface.

## Optional negotiated capabilities

| Feature | Adds | What remains unchanged |
|---|---|---|
| `bilateral` | Required default C1–C6 agreement and principal recovery | Same domain-independent agreement format |
| `composition` | C7 immutable component requirements, exact candidate bindings, and phase-specific dependencies | Each component remains a separately adopted bilateral agreement with its own originator/coordinator |
| `lifecycle-evidence` | C8 attributed native-execution, fulfillment, assessment, settlement, and reservation-disposition claims | A claim does not create authority or prove its own truth |
| `adapter-handoff` | C8 protected Prepare/Dispatch/Reconcile at a selected native boundary; requires `lifecycle-evidence` | Native systems independently validate and perform their actions |

RP1 defaults to `supported_features: ["bilateral"]`. Optional features use the same universal schema and must be supported and explicitly accepted wherever they affect a participant. Unknown required semantics block the dependent act; an implementation cannot silently approximate them. Basic portable proof, delegation checks, and principal-status evidence remain mandatory even when lifecycle evidence is disabled.

Composition permits alternatives, complementary contributions, and subcontracts without making every agent a signatory to every agreement. The transaction orchestrator distributes references within its delegated role; it cannot issue another agent's promise or replace a component's originator. Group membership is not assent, and a refused dependency does not invent cancellation authority or global rollback.

When handoff is selected, RP1 permits separately authorized side-effect-free preparation and holds externally effective dispatch until relevant principal recovery clears and native action authority is current. The selected boundary preserves one authorized occurrence and uncertain outcomes across retries. It does not create a native execution or payment implementation.

## Scope and boundaries

The [eight governing contracts](contracts/README.md) cover publication consent, qualified intent and promises, private negotiation, independent alternatives, admission budgets, policy-controlled validity, exact formation, immutable replacement, portable proof, mandatory principal recovery, and the selected composition/handoff/evidence features.

Existing discovery services retain matching, ranking, subscriptions, and their business rules. Existing identity and policy systems supply actual delegation. Domain vocabularies define action meaning without imposing a universal product ontology. Agents may negotiate new compatible arrangements under both principals' policies; identical prepublished route objects are not required.

Native systems retain AP2/UCP/ACP validation, tool access, execution, payment handling, processors, fulfillment, assessment procedures, settlement, and refunds. APP defines references, eligibility, and claim interpretation at the selected boundary. It does not implement those systems, appoint a universal evaluator, or operate a dispute court.

## Design requirements

| ID | Requirement |
|---|---|
| P1 | Only an authenticated agent with the relevant capability and authority issues its own qualified action; asserting qualification does not prove it. |
| P2 | Intent emission, offers, requests for counterpart behavior, and exact adoption retain distinct meanings. |
| P3 | Discovery, reception, plan membership, and silence cannot manufacture another agent's promise or assent. |
| P4 | Multiple options remain independently identifiable, with explicit shared-capacity/exclusivity constraints. |
| P5 | Policy determines validity and budgets; traffic, retries, new IDs, and alternate services cannot silently expand them. |
| P6 | One exact candidate binds complete terms, action provenance, policies, selection, originator coordination, and refusal protection. |
| P7 | Every distinct principal retains a positive protected recovery period with qualifying notice and a usable refusal path; ordinary agent assent cannot waive it. |
| P8 | Fresh evidence distinguishes pending, cleared, refused, and unresolved recovery; missing evidence never implies clearance. |
| P9 | Accepted records remain immutable; linked replacement, refusal, and recovery preserve attributable history. |
| P10 | Agreement, principal clearance, and native authorization remain separate, including noncommercial exchanges. |
| P11 | A single conforming agreement requires no composition engine or native adapter; the reference harness handles shared protocol mechanics. |
| P12 | Optional features are negotiated explicitly; unsupported required dependencies or evidence semantics are rejected without approximation. |
| P13 | Composed agreements preserve per-agent authorship and per-agreement coordination; partial progress does not imply global atomicity. |
| P14 | Selected handoff gates bind exact action occurrence, current authority, principal protection, and recoverable outcome; lost replies do not authorize duplicate effects. |
| P15 | Typed lifecycle claims preserve reporter, subject, evidence, and native interpretation; submission, fulfillment, assessment, and settlement are not interchangeable. |

## Current deliverable and validation

The repository contains the reconciled specification, concrete reference profile, schemas, worked examples and [reference runtime 0.1.0](docs/runtime.md). Its executable tests exercise cryptography, authenticated transport, policy, durable agreement/recovery, optional composition and simulated handoff. The [validation record](validation.md) separates those implementation results from authoring checks and the broader [proposed checks](tests/PROPOSED.md). There is no live native adapter, payment flow or independent interoperability result.

Proposed tests stop at controlled adapter substitutes and injected native evidence. They cover exact adoption, principal refusal, dependency guards, native translation boundaries, replay, and uncertain outcomes without creating real transactions. Source-backed research remains a possible demonstration domain, not the universal agreement format or a selected assessment regime.

Adoption should next be assessed by connecting an existing capability and principal policies through the [implementer guide](docs/implementer-guide.md) and documented runtime interfaces, while independent implementation assesses whether the specification yields the same semantics. Those assessments remain unrun. A convenient SDK alone would establish neither interoperability nor correctness.

[Current decisions](decisions-v0.4.md) and the [contract map](contract-map.md) govern this revision. Historical research-specific reviewer, correction, payment, and forced-expiry rules remain superseded.
