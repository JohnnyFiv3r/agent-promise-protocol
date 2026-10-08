# Product spec: Agent Bazaar

**Version:** standards proposal 0.1. **Owner:** John Inniger. **Architecture:** A2A extension. **Date:** October 8, 2026.

**License and authorship:** original Bazaar material is [MIT licensed](LICENSE). The comparison frameworks inform design and review only; no direct implementation code, copied schemas or test suites will be adopted from them. The [contract map](contract-map.md) derives the required interfaces from the user's diagram.

## 1. Problem and thesis

A task-oriented agent often knows the desired result before it knows the provider or API. It needs to discover candidates, compare offers, and acquire a product, service, or capability. The difficult handoff is turning an open-ended request into an agreement whose meaning survives delegation.

The starting primitive is **emitted intent**. A buyer can say “I want a source-backed report” without offering money. A provider can say “I seek research work” without offering to perform a particular job. These broadcasts invite only the interaction their authors explicitly permit.

The next primitive is an **offer of self-owned promises**. Either side can propose what it would provide or receive/use, and request reciprocal promises from someone else. The recipient alone can issue those reciprocal promises. Offers can iterate under a bounded channel policy without turning every change into another broadcast.

Agent Bazaar standardizes these distinctions as an A2A extension. Its scope is intent, high-level publication and reception consent, iterative offers, self-owned promises, agreement, and their links to execution and outcome evidence. Existing discovery and subscription services enforce their sales and admission business rules. A2A mediates communication between the agents. An agent may offer an MCP endpoint, another service, a digital product, or a physical product; MCP retains its native interaction and authorization mechanisms when used.

For paid exchanges, the sequence is **accepted offer → AP2 order validation and commitment → x402 or Machine Payments Protocol (MPP) → native processors and settlement**. The publication contract declares eligible complete commercial routes, and both parties pin one route in accepted terms. Agent Bazaar binds the native records to that agreement; AP2 and the selected payment systems retain their validation, payment, and settlement mechanisms.

The standard gives different agents and marketplaces the same language for expressing intent and negotiating cooperation without assigning one agent's promises to another. The [architecture diagrams](protocol-architecture.md) define how that language composes with existing protocols. [Related work](sources-and-decisions.md) informs interoperability and design review.

## 2. Participants and responsibilities

| Participant | Responsibility | Authority limit |
|---|---|---|
| Human or organizational principal | Sets purchasing, data-access, execution, and acceptance policy | Delegates only authority it holds |
| Buyer agent | Emits intent, evaluates offers, adopts its own promises | Operates within principal-issued negotiation and commitment authority |
| Provider agent | Offers a product or service, adopts its own promises, fulfills the accepted terms | Cannot promise another autonomous party's behavior or grant itself buyer resources |
| Discovery or subscription service | Publishes, matches, and routes permitted intent under its business rules; checks commercial-route compatibility | Cannot broaden the publisher's consent, select an unauthorized payment route, or accept an offer for a party |
| Admission service or recipient runtime | Enforces recipient consent and bounded iteration under its selected policy | Cannot turn permission to contact into commercial assent |
| Evaluator | Assesses named criteria against identified evidence | Reports findings; cannot change terms or grant execution authority |
| Native authorization and payment systems | Validate authority, execute payment contracts, and return native evidence | Agent Bazaar references their decisions and outcomes; it does not mint substitute authority or receipts |

A person can fill several roles. The signed objects must still distinguish the roles and their principals. A single agent identifier does not imply an organization has delegated authority to it.

## 3. User journey

1. The principal describes the desired outcome and constraints. Either agent emits an intent and references its publication contract. Ambiguity remains visible until resolved.
2. Existing discovery and subscription services apply the declared audience, permitted uses, contact conditions, and commercial-route eligibility alongside their own sales business rules. Private documents and credentials stay outside discovery. Publication does not create an offer or authorize unlimited replies.
3. Matching parties communicate through A2A under the recipient's selected admission policy. Either may propose and revise an offer containing self-owned promises, requested reciprocals, the product or service specification, fulfillment method, dependencies, deadline, commercial route, assessment conditions, and exclusions. Changes stay within the consented negotiation; a capability claim remains a claim.
4. The buyer compares eligible offers and records why one was chosen. Ranking is local policy. An incompatible commercial route or violated mandatory constraint makes an offer ineligible regardless of price.
5. Both parties adopt the same complete terms, including exact publication-contract references, the offering specification, and one selected commercial route. The research profile uses buyer-coordinated finalization through one procurement slot. Commercial offer acceptance establishes the agreement; it does not establish delivery acceptance.
6. For a paid exchange, AP2 validates the accepted order and the relevant authority and records the commitment associated with its payment obligation. An existing or open mandate may precede negotiation, but it must cover the accepted terms before a dependent payment proceeds. Final native records and receipts may follow the payment.
7. The selected x402 or MPP exchange invokes the eligible native processor and settlement path at the agreed trigger. Payment may occur before fulfillment, at a milestone, or after delivery acceptance; it always follows commercial offer acceptance and the required AP2 validation. Unknown payment outcomes require reconciliation under the original action identity.
8. The provider fulfills the agreement through the selected product or service interface, including an MCP endpoint when that is the offering. A2A supplies agent communication, tasks, and available fulfillment artifacts. Native execution and access authorization must cover each protected action; an accepted agreement alone cannot grant it.
9. The provider supplies fulfillment evidence. The agreed evaluator assesses it, and the buyer records delivery acceptance, rejection, or an unresolved result. Native payment receipts remain separate evidence about the payment obligation. The research demo uses `none` or `simulated` payment.

## 4. Initial scope

### Included

- Bilateral agreements for products, services, or MCP endpoint access, with explicit self-authored promises and a referenced offering specification.
- Symmetric demand/supply intent emission, with no implied offer or reciprocal promise.
- High-level publication and contact consent, versioned publication contracts, and eligible complete commercial routes.
- Existing discovery, subscription, and admission services with independently implemented business rules that preserve the contract's consent and bounded-iteration semantics.
- Multiple concurrent counterparties and bounded iterative offers within each bilateral channel.
- Self-authored provide/use promises, explicit requested reciprocals, immutable offer revisions, selection, and exact accepted terms.
- Binding existing principal/agent identity, signatures, and authority evidence to exact agreement content.
- A selected formation profile; the research demonstration uses a buyer-owned selection slot shared across carriers.
- Agreement-level requirements for native execution permission, retries, cancellation, and uncertain outcomes.
- A2A delivery artifacts, separate assessment/acceptance, and references to native settlement evidence.
- Exportable evidence and adapters that reject mappings which lose required meaning.
- Accepted-offer bindings to AP2 order validation/commitment, x402 or MPP exchange, and the selected native processor and settlement path.

### Deferred

Agent Bazaar does not define a discovery service, subscription engine, sales rules engine, mandatory inbox-permit mechanism, transport, tool protocol, identity provider, credential issuer, mandate engine, wallet, payment rail, escrow implementation, universal capability ontology, ranking algorithm, or legal dispute system. Those remain with their existing protocols and providers. The [reference negotiation profile](reference-negotiation-profile.md) supplies one concrete permit and budget mechanism for the demonstration.

The research demonstration defers live payment execution, public enrollment, subcontractor promise graphs, and multi-provider teams. Its report inputs, rubric and correction budget belong to the research performance profile; its procurement slot belongs to the selected bilateral formation profile. They are not requirements on every product or service offering. External payment and authority bindings are part of the standard's architecture, including compatibility checks against each selected native profile.

### Publication and route selection

An intent carries `publication_contract_ref`. Offers and agreement terms carry `publication_contract_refs`, `offering`, and `commercial_route_selection`. The offering identifies its `kind`, `fulfillment`, `description`, and immutable `specification_ref`. Route selection identifies a `route_id` and `route_digest`.

Offers bind exact `performance_terms_ref` content. Candidate terms include `performance_terms`, whose `profile` identifies the fulfillment and assessment semantics and whose `terms` hold that profile's data. Research inputs, deliverables, acceptance rubric, and delivery/review windows live inside those research terms. Unknown required profiles block adoption.

The publication contract states whose consent applies, permitted discovery uses and audiences, contact conditions, applicable policy references, validity, and eligible complete commercial routes. A route describes a compatible order-validation, paid-exchange, processor, and settlement combination. Discovery can add matching, ranking, subscriptions, pricing, or admission capabilities without changing the meaning of that consent.

Additional paid-exchange profiles can be supported through compatible published routes while retaining the accepted-offer and AP2 validation gates. The [publication guide](publication-contract.md) defines the route and consent fields.

Formation revalidates the referenced policies and selects a route admitted by both parties. Withdrawal prevents new contact under the withdrawn permission; it does not retroactively cancel an accepted agreement. Missing or stale required policy evidence, unknown required semantics, or incompatible routes block the dependent transition. Accepted terms freeze the selected route. A different processor, scheme, asset, network, or weaker validation path requires renewed agreement when outside that selection; an adapter cannot silently fall back.

## 5. Research demonstration

**Task:** Compare A2A, MCP, and AP2 using official documentation available when the run begins. Explain the boundary of each protocol and identify unresolved or version-sensitive claims. This is a proposed demo input, not a report already produced.

The solicitation requires one Markdown report and one structured evidence file. Each substantive factual claim has an ID, protocol name, source URL, retrieved-at timestamp, source version when available, supporting passage locator, and explanation of how the source supports the claim. Unverifiable claims are visibly labeled. URLs alone do not establish support.

| Fictional provider | Simulated quote | Offer | Buyer assessment |
|---|---|---|---|
| QuickScan | USD 8.00 | Blog-based summary in five minutes | Ineligible: violates primary-source requirement |
| SourceCheck | USD 15.00 | Official-source report in fifteen minutes; claim evidence included | Eligible under the example rubric |
| DeepReview | USD 24.00 | Official sources plus repository inspection in thirty minutes | Eligible but over the example USD 20.00 simulated budget |

These prices, names, and durations are synthetic scenario inputs, not provider observations or project delivery dates. The buyer chooses SourceCheck because it meets the constraints. The comparison must expose that reason; selection is not a hidden model score.

Before selection, SourceCheck asks to narrow repository inspection out of scope and the buyer requests an explicit uncertainty appendix. Each party revises its own offer. The final candidate includes both current offers; it cannot splice a price from an expired revision into the scope of another. The same negotiation is then shown with roles reversed: SourceCheck first emits that it seeks research assignments and the buyer initiates contact. No offer exists until one is explicitly issued.

The initial execution permits public HTTPS reads and delivery to a designated artifact sink. It disallows authenticated browsing, private network access, arbitrary file reads, external posting, purchases, and subcontracting. The provider funds its own model/runtime consumption unless separately authorized; a simulated quote is not an API spending grant.

### Research delivery acceptance rubric

| Criterion | Evaluator and method | Pass condition |
|---|---|---|
| Artifact shape | Deterministic schema and digest checks | Both files present; identifiers and references resolve; expected digests match |
| Required coverage | Deterministic topic check plus human review | All three protocols addressed and their role boundaries explained |
| Provenance | Structural check followed by source review | Every asserted material factual claim identifies a primary source, retrieval time, and supporting location |
| Support and fidelity | Named human reviewer, `research-rubric/0.1` | Reviewed sources support claims; no known material unsupported or overstated claim |
| Uncertainty | Same reviewer | Missing evidence and version ambiguity are disclosed without being presented as confirmed facts |

Passing structural validation does not establish source quality, entailment, factual completeness, or honesty. A later model evaluator would need a separate agreed method, configuration, uncertainty policy, and human escalation rule.

The first profile permits one bounded correction submission. Rejection must name failed criteria and evidence. After the correction, remaining disagreement becomes `unresolved`; it does not silently turn into acceptance. The agreed review deadline expiring also becomes `unresolved`.

## 6. Product requirements

| ID | Requirement | Reviewable outcome |
|---|---|---|
| P1 | Separate intent, commercial offer acceptance, permission, and delivery acceptance | User can inspect each record and its issuer |
| P2 | Comparable offers | Constraints, exclusions, and price mode are visible before award |
| P3 | Reproducible agreement | Independent verifier reconstructs the same terms digest and endorsement chain |
| P4 | Narrow execution | Expired, revoked, mismatched, or broadened permission prevents the next protected action |
| P5 | Honest progress | Delivered, accepted, stopped, failed, and unknown are distinguishable |
| P6 | Auditable research in the reference profile | A reader can move from a report claim to the source evidence and evaluator finding |
| P7 | Portable carrier | Carrier changes do not change accepted terms, actor identity, or operation identity |
| P8 | Recoverable retries | Duplicate delivery does not create a new award, execution, correction, or obligation |
| P9 | Explicit uncertainty | Unknown remote state and insufficient evidence require reconciliation or review |
| P10 | Intent is never promoted implicitly | Broadcasting, matching, viewing, or acknowledging intent creates no additional service/purchase promise, offer, agreement, or action grant |
| P11 | Promises belong to their authors | A buyer cannot sign a provider's promise; a provider cannot sign the buyer's promise to pay or use the result |
| P12 | Iteration without spam | Recipient-selected admission policy bounds iterative offers across carriers; activity, relays, and new IDs cannot renew consent |
| P13 | Portable publication consent | Discovery and subscription implementations interpret the same permitted uses, audience, contact conditions, and policy revisions |
| P14 | Commercial-route compatibility | Discovery filters complete eligible routes; accepted terms pin one route and reject unauthorized fallback |
| P15 | Ordered paid exchange | Commercial offer acceptance precedes AP2 order validation/commitment and the selected x402 or MPP exchange; native processors and settlement retain their own behavior |
| P16 | General product and service scope | MCP endpoint access and other offerings use their own specifications without requiring research-only fields |

## 7. Evidence of success

The first useful artifact is a full trace of the research journey, including symmetric intent emission, publication-consent checks, compatible route selection, a negotiated offer revision, a duplicate broadcast, an exhausted reply budget under the reference profile, one failed criterion corrected before delivery acceptance, and one authorization failure that prevents execution. Exported records must distinguish synthetic setup, real tool execution, human assessment, and simulated settlement.

Interoperability requires a second independently written participant to consume the same contract and pass the conformance cases without sharing the reference participant's state machine. Agreement with a shared bug in a single SDK is weak evidence. Each adapter must publish its protocol version, supported profile features, and known limitations.

Useful measures are agreement interpretation mismatches, blocked unauthorized actions, duplicate starts, claim-source coverage, reviewer disagreement, completion/review latency, and actual metered runtime cost. Report numerators, denominators, and unresolved cases. Do not turn a staged demo into evidence of adoption or economic viability.

## 8. Work sequence after design review

First complete the normative objects and A2A extension mapping. Implement the extension in an existing A2A runtime and attach a research provider using existing tools and policy enforcement. Add a second independent implementation. Exercise external authorization and payment bindings against their native conformance requirements.

These are dependency steps, not scheduled commitments. This request produces the spec and contracts; runtime implementation is a subsequent explicit task.
