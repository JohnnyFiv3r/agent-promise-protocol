# Agent Bazaar: recursive overlap and product-thesis audit

**Decision: proceed with the A2A intent-and-promise interaction contract. Keep that boundary narrow.** The current design is not an identical copy of an inspected system, but much of its surrounding agreement machinery overlaps TOS and A202. The contribution to establish is portable, explicit Promise Theory semantics across independently operated services. Neither an intent marketplace nor an A2A agreement layer is new by itself.

**Checked October 8, 2026.** This audit reconstructs the comparison list from the referenced chat, follows relevant specs into schemas/code and linked complementary protocols, and then searches for counterexamples to the proposed differentiators. It evaluates designs regardless of adoption or release maturity. A prior design counts even when pre-release. Runtime tests, live purchases and adoption verification were outside this source review.

**Subsequent implementation direction:** Bazaar is independently authored and MIT licensed. Comparators are inspiration and interoperability references only where permitted; no direct implementation code, copied schemas or imported tests will be adopted. References below to reuse concern existing external services/protocols and conceptual design, not importing comparison frameworks. See the [contract map](contract-map.md) and [licensing record](reuse-and-licensing.md).

The earlier comparison's “not broadly adopted” framing does not establish novelty and is not needed to justify this standards proposal.

## Product thesis and system boundary

The product thesis is that an autonomous agent can acquire a capability it was not built with by expressing an outcome, finding counterparties, negotiating and adopting its own promises. It can acquire MCP access, API access, a proprietary dataset, a deliverable or another product/service while keeping its principal's authority and reception consent intact.

The user's clarified boundary is decisive: **Agent Bazaar is the A2A interaction between the harnesses.** Existing discovery and service offerings feed that interaction through publication contracts. Order validation, payment exchange, processors and settlement are downstream integration points. The [architecture](protocol-architecture.md) now draws that boundary explicitly.

Recommended standards statement:

> Agent Bazaar defines a portable A2A interaction contract for emitted intent, permission to engage, proposed reciprocal behavior and each agent's adoption of its own provide/receive promises. Existing discovery and service providers can carry and implement that contract without becoming the source of another agent's commitments. Accepted terms plug into existing order and payment machinery.

This is a specific standardization target. Its value must come from preserving meaning between independent systems, not from renaming their offers or obligations.

## Recursive coverage and closest collisions

| Comparator | What already overlaps | Consequence |
|---|---|---|
| **TOS Intent Exchange + Messenger + Guarantor** | Symmetric nonauthorizing intent, proposals, own-obligor authorization, inbox policies, bounded negotiation, settlement adapters; a specialized pre-acceptance firm offer | Strongest semantic collision. Do not claim self-authorization, nonbinding intent or pre-acceptance commitment as unique. [Pinned audit](research/tos-amp-asa.md) |
| **A202** — newly found | A2A commercial extension, invitations, exact agreements, party commitments and external settlement handoffs | Strongest collision with “thin agreement layer” positioning. Its general intent payload is deferred; its commitment derives from agreement. [Primary model](https://a202.org/schemas/canonical-commercial-model-v0.1/), [A2A binding](https://a202.org/bindings/a2a-binding-v0.1/) |
| **Duami** | Symmetric want/offer listings, counterproposals, direct A2A negotiation and atomic single-winner acceptance | Closest user journey. A new directory with bid threads and A2A links would duplicate much of it. [Official manual](https://duami.ai/llms.txt) |
| **AMP → Agent Service Agreements** | Capability matching/RFQ, bounded counteroffers, signing, assessment and payment integration | Compare the composition, not AMP alone. Reuse matchmaking and performance mechanisms through profiles. [Pinned audit](research/tos-amp-asa.md) |
| **BotVibes** | RFQ/firm quote/contract/verification/escrow plus published A2A/MCP access-contract surfaces | Research procurement and native agent interfaces alone are shared. [Protocol](https://github.com/Axsar/botvibes/blob/2c7b5474534afd369d219155c23fe03002a07884/protocol/SPEC.md), [hosted API](https://botvibes.io/openapi.json) |
| **ERABI** | Signed intent and sponsorship selection; explicit AP2/commerce/x402 composition | Payment-stack composition alone is shared. Its sponsorship bid has a different meaning from a bilateral performance promise. [Pinned audit](research/marketplaces.md) |
| **Beckn / ONDC lineage** | Broad resource/offer/commitment/contract schemas; negotiated exchange; autonomous engagement and capacity controls | A substantial semantic comparator, not merely a retail catalog. Inspected Beckn v2 features must not be attributed automatically to ONDC deployments. [Primary API](https://github.com/beckn/protocol-specifications-v2/blob/main/api/v2.0.0/beckn.yaml) |
| **Contract Net / FIPA** | Distinct speech acts, iterative bidding and conditional self-commitment | A binding FIPA proposal is different from Bazaar's unadopted description; an adapter must preserve that difference. [Primary-document audit](research/foundational-prior-art.md) |
| **CSNP** — newly found | Separate discussion/commit consent, finite rounds, option-disclosure limits and expiry | Consent plus bounded negotiation is shared; its closed-option privacy model is a different mechanism. [Primary repository](https://github.com/molanocortes/consent-scoped-agent-negotiation) |
| **ANP / ACNBP** — newly found | Structured commercial offers, local authority, bounded negotiation or capability binding | More prior art for negotiation and acquiring unfamiliar capabilities. [Additional-neighbor audit](research/additional-neighbors.md) |
| **Agent Bounties** | Published exact terms, authorized claims, evidence and native settlement | A successful research delivery proves little differentiation by itself. [Autonomous protocol](https://github.com/NSPG13/agent-bounties/blob/main/docs/autonomous-protocol.md) |
| **Crypto solvers / x402 Bazaar** | Desired-outcome execution, competitive counterparties or dynamic paid-endpoint discovery | Reuse these inputs/outputs; never silently turn exploratory interest into an executable payment order. [Foundational audit](research/foundational-prior-art.md), [discovery documentation](https://github.com/x402-foundation/x402/blob/main/docs/extensions/bazaar.mdx) |

The recursive paths matter: **AMP → ASA** supplies the agreement layer absent from AMP alone; **TOS → Messenger** supplies contact consent, and **TOS → Guarantor** supplies a firm commitment before acceptance; **ERABI → AP2 interop** already supplies the architectural composition story. The expanded search adds **A202**, which directly occupies A2A commercial semantics. None can be dismissed based on an earlier high-level description.

## What remains distinct in our design

The inspected systems do not present the complete proposed combination as the same small A2A interaction profile. This is a bounded comparison result, not a claim of universal priority. Three aspects merit development together:

1. **Market posture, speech act and promise polarity remain independent.** Seeking work or an outcome is different from proposing behavior, adopting behavior, or promising to receive/use something. Either market side can provide and receive. A receive/use promise is not contract assent, acceptance of delivered quality, or payment authority.
2. **Promises have an attributable lifecycle outside the transaction projection.** A proposed counterpart promise remains a description until its own author adopts it. General provide/receive promises can be independently issued, withdrawn and assessed without manufacturing a bilateral agreement. TOS already has own-obligor authorization and specialized firm offers; our difference is the general shared model, not the mere existence of authenticated or pre-acceptance commitments.
3. **Consent and those semantics survive service boundaries.** A publication can be carried by existing discovery systems and discussed over A2A while preserving audience/use/contact distinctions, finite iteration, immutable revisions and exact adoption. Providers retain their own discovery, admission and execution machinery. A translation that loses required meaning must fail explicitly.

The differentiation is the **combination and interoperable behavior**. A polarity field, an extra signature or the phrase Promise Theory does not by itself produce it. Existing protocols can be extended to express similar semantics; the standard should make those extensions compatible rather than depend on their inability to evolve.

## Where the present draft risks duplication

| Current area | Keep in Bazaar | Reuse or keep outside the core |
|---|---|---|
| Publication | Meaning of consent and immutable references; upstream commercial eligibility | Discovery service, subscription engine, ranking, registry, identity enrollment |
| Promise records | Own versus requested behavior, explicit adoption, independent polarity and lifecycle | A universal product ontology or claims that arbitrary prose proves actual capability |
| Iterative offers | Supersession, recipient-owned bounds, closure/reconciliation invariants | Mandatory permit transport, shared market coordinator or one proprietary admission engine |
| Formation | Evidence that exact terms and each party's commitments were accepted | Buyer award/finalization as the only possible formation mechanism; another full A202-like commercial kernel |
| Fulfillment | Links from promises to agreed evidence and assessment semantics | General evaluator marketplace, reputation algorithm, escrow policy or dispute engine |
| Downstream integrations | Exact accepted-term and route association to AP2/exchange evidence | New mandate formats, payment execution, processor routing implementation or settlement state machines |

Several recent changes already move in this direction: reference-only permits, explicit formation/performance profiles, native evidence bindings and a separate ancillary integration boundary. The remaining work is to make the core small enough that a TOS, Duami, AMP or A202 participant can add it without replacing its platform.

Two draft details need proof before becoming interoperability claims. `behavior`, `limits` and condition descriptions still contain prose; the first profile needs enough agreed behavioral vocabulary and validation rules for independent interpretation. Complete route objects currently must produce the same canonical route digest across both publication contracts; that is deterministic, but broad compatibility requires an explicit adapter/configuration process so both platforms agree on the complete object, including its route ID and native policy references. JSON formatting and key order need not be identical. These are concrete design questions, not reasons to build a larger marketplace.

## The demonstration that proves this thesis

Keep the selected source-backed research deliverable. Change what the demo proves:

1. Use two independently implemented discovery/admission adapters and two independently implemented A2A participants. Run the same scenario through both adapters; a single shared in-memory marketplace is insufficient.
2. Run buyer-emitted “I seek a report” and provider-emitted “I seek research work.” Neither creates a quote, spend instruction, reservation or the other's promise.
3. Model both parties' provide/receive behaviors. Attempt to promote a requested reciprocal into an adopted promise and reject it. Show a standalone promise without a purchase.
4. Relay duplicates and revisions through both discovery paths. Duplicates leave consent, budgets and offer heads unchanged. Each admitted revision advances its author's offer head and consumes its allowance once across both paths; it cannot renew consent or lifetime. A visible publication with closed contact policy cannot trigger an offer to the recipient.
5. Include a valid conversation that ends without an agreement. A decision not to transact is a successful protocol outcome.
6. Exercise a native mapping with different firmness semantics: a FIPA binding bid, BotVibes firm quote, bounty claim or payment order. Require explicit adoption/authority before that transition; reject a conversion that would silently create commitment. These are mapping targets, not integrations already built.
7. Finalize one exact offer and route. Demonstrate the boundary handoff into existing AP2/payment mechanisms; refuse a changed processor or payment challenge lacking accepted-order evidence. Simulated payment must remain labeled simulated.

The acceptance criterion is observable: **another implementation preserves the same promises and consent without sharing our reference runtime or surrendering its existing infrastructure.** That tests the product thesis more directly than “three agents bid, one wins, a report arrives.”

## Recommendation and record of changes

Proceed as an **A2A intent-and-promise profile**, with Agent Bazaar naming the interaction. Write compatibility mappings before adding more native lifecycle machinery. Treat close projects as candidate implementers and integration targets; no outreach has been sent.

This audit adds research findings and revises the requested architecture/README diagrams. It does not silently redesign the normative contract or implement a runtime. Proposed scope adjustments and demo requirements above are reviewable recommendations. The [source ledger](research/README.md) distinguishes code inspection, public specification and retrieval gaps.
