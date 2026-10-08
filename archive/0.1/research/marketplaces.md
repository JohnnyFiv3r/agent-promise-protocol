# Recursive comparator audit: BotVibes, Duami, ERABI

Reviewed 2026-10-08. This is a read-only primary-source comparison against the current Agent Bazaar contract, publication contract, and product specification. No accounts were created, agents contacted, transactions submitted, or downloaded project code executed.

## Decision

**The current Bazaar contract is not identical to these three systems. Duami is the closest interaction-level comparator.** The generic product story—publish a need, discover a provider, negotiate, accept, fulfill—is already implemented or specified by competitors. Symmetric wants/offers, negotiation over A2A, anti-spam controls, and composing a pre-payment layer with AP2/x402 cannot individually carry the novelty claim.

The distinct contribution to prove is **portable semantics for who expressed interest, who owns each proposed provide/receive promise, who actually adopted it, and which consent and commercial route authorize each subsequent transition**. The meaningful test is whether another service can carry the records without silently turning publication into contact permission, a requested reciprocal into somebody else's promise, or an accepted commercial offer into execution/payment authority. This is a comparison conclusion, not a claim that no other project anywhere addresses those semantics.

## Sources and provenance

| Comparator | Primary material actually inspected | Version/evidence boundary |
|---|---|---|
| BotVibes | [Official site](https://botvibes.io/), linked public repository, protocol spec, SDK, rate-limit ADR, escrow spec, current [hosted OpenAPI](https://botvibes.io/openapi.json) | GitHub `main` resolved to [`2c7b5474534afd369d219155c23fe03002a07884`](https://github.com/Axsar/botvibes/commit/2c7b5474534afd369d219155c23fe03002a07884), commit timestamp 2026-03-09. Hosted API advertises 1.9.0. Public SDK/spec inspection does not establish private engine behavior. |
| Duami | [Official manual](https://duami.ai/llms.txt), [OpenAPI](https://duami.ai/openapi.json), [terms](https://duami.ai/terms), public discovery metadata | OpenAPI 0.1.0. A third-party registry's linked source repository returned 404; no implementation source was verified. Published behavior is documented behavior, not transaction-tested behavior. |
| ERABI | Official [repository](https://github.com/HMAKT99/Erabi), linked normative schemas, exchange/auction/bridge code, A2A card, AP2 interop and delegation documents | GitHub `main` resolved to [`07505e37936afd573b7688c0dfd9b98a8aee1938`](https://github.com/HMAKT99/Erabi/commit/07505e37936afd573b7688c0dfd9b98a8aee1938), commit timestamp 2026-07-15. Source read, not executed. |

Mutable document fingerprints retrieved during this audit:

- Duami manual: `sha256:9b4d03ed6d24e938a1c8b1138ad35ab257e3cd53a9440d81c5bb758364b05462`.
- Duami OpenAPI: `sha256:2e8bd8e463df108eef97892324758142966ac388060f77b1a3fb6f1fb0738cfe`.
- BotVibes hosted OpenAPI: `sha256:364ab6ca7800bac8a1f8df96cd382f9420017c69342c05d8325dcfb568940239`.

## Functional overlap matrix

“Not found” below means absent from the inspected public interface/specification, not proof of absence from every implementation or future version.

| Bazaar concern | BotVibes | Duami | ERABI | Implication for Bazaar |
|---|---|---|---|---|
| Interest distinct from a later transaction | Listing/RFQ precede quote acceptance [B1] | Want/offer intent precedes bid acceptance [D1] | Consumer intent precedes candidate selection/outcome [E1] | This separation in a workflow is established prior art. |
| Symmetric supply/demand expression | Separate listings and RFQs [B1] | One intent object with `want`/`offer` [D1] | Consumer intent versus provider standing bid [E2] | Duami defeats a novelty claim based simply on two-sided intent. |
| Iterative offers and acceptance | Quotes may expire/withdraw; delivery revisions are distinct [B1/B2] | Counterproposals update a bid; only the other side accepts [D1/D2] | Provider can replace its standing bid payload [E3] | Promise ownership, immutable revisions, and adoption semantics must do useful work beyond counteroffers. |
| Anti-spam/admission | Operation rate limits, exposure tiers, trust floor [B1/B3] | Registration PoW, API quotas, reputation gates [D1/D2] | Sponsorship opt-in, ratio caps, owner-controlled autonomous consent [E4] | Differentiate portable recipient consent, not the existence of budgets or opt-in. |
| A2A/MCP | Hosted API documents both contract/access surfaces [B4] | Direct A2A negotiation; MCP/REST service access [D1] | A2A discovery card and MCP integration [E5] | “Uses A2A/MCP” is already shared. A versioned semantic extension remains a more specific claim. |
| AP2/x402 composition | Native escrow/credits and Stripe checkout described [B4/B5] | Money/goods exchange remains between parties [D3] | Explicit AP2/checkout/x402 composition document [E6] | A pre-payment composition layer is not unique. Exact accepted-term and route binding is the relevant contribution. |
| Self-owned typed provide/receive promises, requested reciprocals, explicit per-author adoption | Not found in inspected contract/quote fields | Not found in inspected bid/message fields | Signed author ownership exists; these promise primitives not found | This is the strongest semantic difference in this set. Do not equate ordinary authentication with the full model. |
| Portable publication consent and complete commercial route pinned by both parties | Not found | Not found | Rail field exists; complete two-party route binding not found | Keep this in the standard and demonstrate rejection when a mapping drops it. |

## BotVibes: an overlapping marketplace loop with a larger operational stack

**B1 — protocol recursion.** The site's SDK link leads to the public repository and its [Agent Commons Protocol specification](https://github.com/Axsar/botvibes/blob/2c7b5474534afd369d219155c23fe03002a07884/protocol/SPEC.md). Listings carry price/SLA, exposure tier and trust floor; RFQs carry need, constraints, budget and deadline; a provider's quote is a firm offer; acceptance creates a contract and funds escrow. Signed immutable receipts bind artifact hashes. Thus outcome procurement, conditional eligibility, promise-like service terms and a distinct acceptance transition all predate this proposal. The inspected spec does not define general provide/receive promise polarity or per-author adoption of each promise.

**B2 — SDK recursion.** [The public SDK](https://github.com/Axsar/botvibes/blob/2c7b5474534afd369d219155c23fe03002a07884/sdk/client.py) has `create_rfq`, `create_quote`, `accept_quote`, `withdraw_quote`, and direct hiring. Quote submission requires a listing owned by the provider according to its documented API contract. Quote acceptance supports `internal_ledger` or `external` escrow. This is more than a landing-page concept, but the SDK delegates enforcement to the server. No bilateral immutable counteroffer chain was found in those inspected methods.

**B3 — anti-spam recursion.** The [rate-limit ADR](https://github.com/Axsar/botvibes/blob/2c7b5474534afd369d219155c23fe03002a07884/docs/adr/006-rate-limiting.md) specifies agent/operation sliding windows and payload limits. It also describes per-process resets and lack of shared worker state. These are operational controls rather than a portable recipient-issued negotiation consent budget.

**B4 — hosted interface correction.** The current [OpenAPI](https://botvibes.io/openapi.json) contains admin-created A2A contracts with agent allowlists, call caps, rates, expiry and feature gates, plus MCP contracts with skill allowlists. The A2A endpoint documents `tasks/send`, `tasks/get` and `tasks/cancel`; this is not proof of conformance to current A2A 1.0. Its `QuoteCreate.max_revisions` means delivery rejection count, not iterative commercial offers. Payment endpoints expose Stripe credit purchases. The inspected schemas do not show Bazaar-style promise adoption, publication consent, AP2 binding, or complete processor/settlement route pinning. It would be inaccurate to describe BotVibes as lacking A2A/MCP integration merely because the homepage foregrounds marketplace APIs.

**B5 — settlement recursion.** The [escrow specification](https://github.com/Axsar/botvibes/blob/2c7b5474534afd369d219155c23fe03002a07884/protocol/ESCROW.md) combines acceptance, funding, release/refund/slash and CAS versioning. Its timeout/default-acceptance policies differ from Bazaar's research profile's unresolved review outcome. Bazaar should delegate escrow to such native providers instead of rebuilding this subsystem.

The [repository README](https://github.com/Axsar/botvibes/blob/2c7b5474534afd369d219155c23fe03002a07884/README.md) explicitly says the engine source is not yet public and local deployment/federation remain forthcoming. Accessible hosted documentation and counters are not evidence of independent adoption, successful commercial transactions, or federation.

## Duami: the highest risk of designing the same user journey

**D1 — official manual.** Duami already publishes both demand and supply, matches complementary intents, negotiates either party's counterproposals and accepts only the other party's latest proposal. One agent has one open bid per intent; acceptance is documented as atomic with one winner. It recommends direct A2A negotiation and recording the final terms back in Duami. Registration PoW and per-key quotas constrain abuse. These behaviors directly overlap Bazaar's user journey. Its public Agent Card guidance lets others open tasks, unlike Bazaar's separate contact consent requirement. [Manual](https://duami.ai/llms.txt).

**D2 — schema recursion.** The [OpenAPI](https://duami.ai/openapi.json) separates `Intent`, `Bid`, and `Message`. `CreateMessage.proposal` changes amount/currency/terms and hands acceptance to the other side; `last_proposer` governs assent. Price is optional and fulfillment includes digital, physical and service categories. Private disclosure and minimum reputation constrain who sees details or bids. Its inspected schemas do not model typed own promises versus requested counterpromises, immutable offer digests, portable audience/use/contact permissions, or a mandatory accepted-offer-to-AP2 route. Do not call its ordinary bilateral acceptance “no consent”; Bazaar proposes more granular and portable consent/adoption semantics.

**D3 — commercial boundary.** Duami's [terms](https://duami.ai/terms) place execution, goods and money outside the platform. This is meaningful scope restraint, so “we don't move money ourselves” is also not a differentiator.

**Design consequence:** Building a new intent directory with bid threads, A2A links, ratings and match notifications would reproduce much of Duami. Using Duami-like discovery as an adapter while carrying the additional promise and consent semantics is consistent with the user's thesis. A plain translation from Bazaar's accepted terms into an untyped `terms` string is not semantic interoperability.

## ERABI: relevant selection semantics and explicit composition prior art

**E1 — spec recursion.** The [specification](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/spec/README.md) defines signed envelopes, structured intent, consideration sets, disclosure and dual-signed outcomes. Its central invariant is inspectable paid influence and money-independent organic ranking. The loop is selection and outcome attribution, rather than bilateral adoption of service promises.

**E2 — normative schemas.** The [Intent schema](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/packages/schemas/json/intent.schema.json) records a bounded consumer choice with constraints, context hash and human-in-loop flag. The [Bid schema](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/packages/schemas/json/bid.schema.json) is a provider's standing sponsorship bid: category targeting, `cpa`/`cpc`/`rev_share`, creative, daily budget and rail choice. A signed bid is not a negotiated promise to fulfill a buyer's complete deliverable specification. The distinction is structural, not dependent on whether ERABI uses Promise Theory terminology.

**E3 — implementation recursion.** In [exchange service code](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/services/exchange/src/service.ts), `placeBid` checks that envelope signer matches provider, verifies the signature and refuses takeover of another provider's bid ID. Existing bid payloads are updated. `submitIntent` likewise verifies the consumer and expiry. This is real self-authorship enforcement; Bazaar cannot claim that signing only one's own expression is novel by itself. [Auction code](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/services/exchange/src/auction.ts) implements quality-weighted second-price sponsored-slot allocation, not alternating bilateral offer negotiation.

**E4 — consent recursion.** [Scope policy](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/spec/SCOPE-POLICY.md) and inspected exchange code separate consumer sponsorship opt-in from owner authorization to receive sponsorship in autonomous decisions. [Delegation documentation](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/spec/DELEGATION.md) distinguishes current verified-owner payout binding from future narrowing delegation chains. These are real consent/authority boundaries, but a different domain from publication/contact consent and adoption of reciprocal performance promises.

**E5 — A2A recursion.** The [A2A card](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/integrations/a2a/agent-card.json) advertises registration, discovery, intent and outcome-reporting skills. An Agent Card is evidence of a published integration surface, not sufficient evidence of a bilateral negotiation extension or runtime conformance.

**E6 — payment recursion.** The [AP2 interoperability document](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/spec/INTEROP-AP2.md) explicitly locates ERABI before authorization, checkout and x402 settlement. Its mapping uses older AP2 IntentMandate/CartMandate terms; it does not establish the current Bazaar AP2 order profile. The same document labels the x402 payout facilitator call stubbed and AP2 payout adapter TODO. The [x402 bridge code](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/services/bridges/x402/src/index.ts) implements paywall probing, provider/standing-bid registration and receipt-to-outcome handling; that is different from executing a verified AP2-to-x402 purchase. The current [README](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/README.md) explicitly describes a pre-release, ledger-only economy with no real-money conversion of ledger balances.

## Product guardrails and the proof to build

1. **Keep the unit of standardization the semantic record and transition.** Discovery, matching, ratings, auction allocation, escrow, identity issuance and processors remain interchangeable providers. Rebuilding them would pull Bazaar toward BotVibes/Duami/ERABI product duplication.
2. **Make Promise Theory change validator behavior.** A provider's requested buyer promise must remain a request until the buyer authors/adopts it. A `receive` promise must not be inferred from `seek_result`. A supply intent must not become a firm offer. An adapter must reject these changes even if a marketplace would accept an ordinary bid.
3. **Demonstrate portability across independently implemented services.** Publish once through two discovery adapters, negotiate over A2A, preserve the same consent/revision budget across delivery paths, and verify exact offer/promise ownership without relying on the discovery operator's database.
4. **Show one commercial handoff with loss detection.** The selected complete route, accepted terms and native AP2 order validation must bind the downstream exchange. A processor change outside that selection must force renewed agreement. A `settlement_rail` string or correlation ID alone is insufficient.
5. **Reuse the established journey without calling it the invention.** The existing source-backed research demo is appropriate, but ordinary successful procurement proves too little. Its distinguishing scenes should be rejected false adoption, forbidden contact despite visible publication, stale revision rejection, cross-carrier budget exhaustion, and changed-route refusal.

These recommendations fit the user's thesis: an agent can acquire a capability it was not built with while each autonomous participant retains control over its own commitments. The addition is a shared, enforceable meaning for that acquisition across services—not another requirement to join one marketplace.
