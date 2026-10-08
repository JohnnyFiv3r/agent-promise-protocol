# Sources and design decisions

**Research checked October 8, 2026.** Public documents establish documented concepts and author claims, not deployed behavior or independent adoption. These mutable URLs are not pinned release evidence.

## Promise Theory reading

Source: Jan A. Bergstra and Mark Burgess, [*Promise Theory: Principles and Applications*, second edition, 2019](https://markburgess.org/BookOfPromises.pdf).

A user-authorized GPT-6 Luna reader read the complete extracted text of all **318 PDF pages**, including notes, bibliography, and index. It repaired a skipped range and reread truncated output. The [coverage record](promise-theory-reading-coverage.json) identifies every range, the source SHA-256, and limitations. The coordinating agent separately reviewed the central definitions, conditional promises, conflicts, and invitation passages, and rendered PDF pages 104, 183, and 188. Not every equation or illustration received individual visual verification.

The book treats declared intention as a promise, distinguishes proposed descriptions from adopted promises, and leaves each agent responsible for its own behavior. Provide/receive polarity is independent of market roles. Promise scope concerns who knows of a promise; assessment belongs to observers. Invitations can progressively establish consent for interaction. Repetition does not create a new identical promise, though it can influence belief.

| Relevant section | Printed pages | PDF pages |
|---|---|---|
| Core concepts; promise proposals | 3–4, 27–28 | 19–20, 43–44 |
| Scope; polarity and cooperation | 31, 38–43 | 47, 54–59 |
| Idempotence; capacity | 47, 52–54 | 63, 68–70 |
| Assessment; conditional promises | 66–70, 78–84 | 82–86, 94–100 |
| Lifecycle; conflicts | 85–88, 96–98 | 101–104, 112–114 |
| Invitations and intrusive messages | 165–172 | 181–188 |

Reception permits, quotas, exact-term finalization, and native evidence bindings are the extension's engineering design. Existing runtimes supply enforcement and existing protocols supply authentication and payment mechanisms.

## Direct prior art

The [recursive overlap audit](novel-angle-audit.md) extends and qualifies this earlier comparison, including current TOS/AMP/ASA code, Duami and BotVibes interfaces, Beckn/FIPA, and newly identified A202/CSNP/ANP neighbors. Its source ledger distinguishes inspected behavior from implementation and adoption claims.

| Primary source | Observed content | Design implication |
|---|---|---|
| [TOS Agent Intent Exchange V1](https://github.com/tosnetwork/tos-service-spec/blob/main/docs/AGENT_INTENT_EXCHANGE_V1.md) | Separates intent advertisement, conversation, exact agreements, authority and settlement; labels external production acceptance pending | Compare intent/agreement semantics and define an interoperability mapping |
| [AMP whitepaper](https://www.vibeagentmaking.com/whitepaper/matchmaking/) and [repository](https://github.com/alexfleetcommander/agent-matchmaking) | Version-labeled whitepaper 1.0.0 and a research/prototyping implementation for matching and federation | Matching is replaceable; use interoperable profiles if useful |
| [Agent Service Agreements](https://github.com/alexfleetcommander/agent-service-agreements) | Alpha contract negotiation and quality-evaluation layer adjacent to AMP; escrow abstraction does not itself transfer funds | Compare promise authorship, invitation semantics, and offer revision behavior |
| [Agent-Bazaar repository](https://github.com/Agent-Bazaar/Agent-Bazaar) | Existing project uses the name for an agent marketplace | Retain an internal working name; choose public identity before publication |

Other related projects named in the source conversation include BotVibes, Duami, ERABI and Agent Bounties. The standards proposal defines its own semantics and conformance requirements; interoperability work can map these systems to the extension.

## Protocol boundaries

| Source | Intended use and boundary |
|---|---|
| [A2A 1.0.0](https://a2a-protocol.org/v1.0.0/specification/) and [extension documentation](https://a2a-protocol.org/latest/topics/extensions/) | A2A 1.0.0 is the base protocol. Agent Bazaar uses the extension mechanism, native messages/tasks/artifacts and native security integration; exact agreement semantics belong to the extension. |
| [A2A current authorization clarification](https://a2a-protocol.org/latest/specification/#764-in-task-authorization-scope) | Current text explicitly separates authorization-needed status from actual permission. This clarification is not present verbatim in the pinned 1.0.0 page. |
| [MCP 2026-07-28 authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) | Tool access can implement local actions; connected access is not automatically authorization for every contracted effect. |
| [AP2 authorization framework](https://ap2-protocol.org/ap2/agent_authorization/) and [payment specification](https://ap2-protocol.org/ap2/specification/) | Current standard mandate names are Checkout and Payment. The framework permits custom types; general Bazaar actions still need explicit constraint and validation semantics. |
| [x402](https://docs.x402.org/introduction), [Bazaar discovery](https://docs.x402.org/extensions/bazaar), [offers and receipts](https://docs.x402.org/extensions/offer-receipt) | Payment and discovery/evidence overlap already exists. Native payment offers and receipts remain x402 evidence linked to agreement obligations. |
| [UCP 2026-08-25](https://ucp.dev/2026-08-25/specification/overview/) | Optional commerce binding for suitable transactions; checkout and order behavior stay with UCP. Pin artifact digests as well as a dated version. |
| [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) | Canonicalization for extension-record digests; native signed evidence retains its own bytes and verification rules. |

## Decision register

| ID | Decision / status | Why it matters |
|---|---|---|
| D1 | **User-confirmed:** source-backed research demo | Gives promises an inspectable outcome and real assessment uncertainty |
| D2 | **User-confirmed direction:** emitted intent, self-owned promises, symmetric sides, bounded iterative offers | Core of the concept; not merely another agreement store |
| D3 | **User-directed:** high-level publication consent and sales business rules; discovery/subscription services own implementation | Existing services can add capabilities while preserving the common consent semantics |
| D4 | **Proposed:** proposals and explicit promise issuance are separate record types | A counterpart can discuss a promise it cannot issue |
| D5 | **Proposed:** offers remain proposals in the first profile; firm standing promises use a distinct statement | Avoids hidden commercial commitments in discovery and negotiation |
| D6 | **Reference admission profile:** directional permits/budgets; core requires bounded consent and deduplication | Other service profiles may enforce the same guarantees through their existing mechanisms |
| D7 | **Proposed:** buyer-coordinated procurement finalization | Makes expiry and one winner tractable; trust assumptions remain explicit |
| D8 | **Proposed:** named human semantic reviewer, one correction, timeout unresolved | Avoids equating schema validity or model judgment with source truth |
| D9 | **Reference-demo choice:** simulated payment; no subcontracting | The standard supports external payment bindings while the first demo isolates the research promise flow |
| D10 | **Release selection:** existing proof/trust profile and native authorization bindings | Reuse established authentication, mandate and revocation mechanisms; no custom identity or grant engine |
| D11 | **Publication decisions:** extension URI and standards participation; MIT licensing selected in D21 | Publish and implement under the A2A extension model |
| D12 | **Interoperability work:** TOS/AMP/ASA mapping and independent implementation | Exercise the same semantics and conformance requirements across participants |
| D13 | **Deployment policy:** production admission and abuse controls | Reuse gateway/security controls; extension-level reception consent and quotas remain mandatory |
| D14 | **User-directed:** frame Agent Bazaar as an A2A standards proposal | Define the extension directly and substantiate it through precise contracts and conformance |
| D15 | **User-directed:** reuse MCP, A2A, AP2, x402 and other payment contracts | Own promise/negotiation semantics and evidence bindings; delegate native protocol functions |

Questions for Mark's review: Does our mapping preserve the distinction between information about an intention, proposed promises, and adopted promises? Do reception promises accurately capture willingness to negotiate without commercial assent? Where should conditional dependencies be explicit? What is lost when the first profile excludes composite promise graphs? These are review questions, not a message sent to him.

## Additional composition references

[ACP architecture](https://www.agenticcommerce.dev/docs/concepts/architecture) and [Delegate Payment](https://www.agenticcommerce.dev/docs/reference/payments) separate commerce and payment operations. [Stripe machine payments](https://docs.stripe.com/payments/machine) documents MPP and x402 paid-call paths. These are selectable native bindings downstream of accepted offers and AP2 order validation in the Bazaar paid profile.

[A2A extension documentation](https://a2a-protocol.org/latest/topics/extensions/) permits independently defined and published extensions. Its [governance process](https://a2a-protocol.org/latest/topics/extension-and-binding-governance/) supplies the path for participation in the official extension lifecycle.

## Publication and payment composition revision

The user specified the commercial ordering and discovery boundary. The revised contract makes **accepted offer → AP2 order validation/commitment → paid exchange → selected processors and settlement** mandatory for the Bazaar paid profile. This composes existing protocols; it does not assert that their native use elsewhere requires Bazaar.

[AP2 v0.2 specification](https://ap2-protocol.org/ap2/specification/), [authorization framework](https://ap2-protocol.org/ap2/agent_authorization/), [native flows](https://ap2-protocol.org/ap2/flows/), and [Payment Mandate](https://ap2-protocol.org/ap2/payment_mandate/) ground the distinction between prior open delegation, transaction-specific verification and later receipts. Bazaar binds the verified order commitment to the payment obligation in accepted terms. A final Checkout Receipt may follow payment, so it is not the prerequisite used to start that payment. Machine Payments Protocol is written out to distinguish it from AP2's Merchant Payment Processor role.

| ID | Decision / status | Why it matters |
|---|---|---|
| D16 | **User-directed:** A2A mediates A/B; B can offer MCP endpoint access or any product/service | MCP is an offered interface or tool choice, not a mandatory fulfillment stage |
| D17 | **User-directed:** AP2 order validation/commitment follows accepted offers; paid exchange follows that | Intent and receipt of a payment challenge never create a payment obligation or authority |
| D18 | **User-directed:** select processor and settlement eligibility through publication/discovery | Complete routes are advertised upstream and one immutable route is selected by the accepted offer |
| D19 | **Contract design:** immutable bilateral publication pins, exact complete route selection, current status checks | Services cannot broaden consent, mix unsupported components, or silently downgrade the payment path |
| D20 | **Contract design:** separate admission, formation and performance profiles | Existing services can supply mechanisms; the research demo's rubric, slots and numerical defaults do not define every product |
| D21 | **User-directed:** original Bazaar specification and implementation are MIT licensed; comparators are inspiration only where permitted | No direct implementation code, copied schemas or test suites from comparison frameworks; supersedes the earlier component-adoption recommendation |
| D22 | **Contract decomposition:** eight responsibility contracts derived from the agreed diagram | Publication, intent, admission, offers/promises, formation, A2A binding, native handoff and fulfillment evidence remain explicit without creating new services |
