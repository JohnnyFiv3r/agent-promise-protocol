# Agent Bazaar A2A extension contract

**Standards proposal 0.1 · ABP 0.1-draft · A2A 1.0.0 binding · October 8, 2026**

`MUST`, `MUST NOT`, and `SHOULD` express requirements of this proposed profile. They describe what a conforming participant agrees to validate and enforce locally. They do not give the network power to compel an autonomous counterparty.

## 1. Purpose and theoretical boundary

Agent Bazaar is an A2A behavioral extension. It defines intent, reception consent, offers, promise adoption, agreement and their semantic bindings. It reuses A2A communication/tasks, MCP interfaces where offered or used, AP2 order validation and commitment, and x402, Machine Payments Protocol or other selected payment contracts. The [architecture and wire mapping](protocol-architecture.md) are part of this contract.

The protocol preserves five distinct questions: **What do I seek? What will I listen to? What do I propose? What do I promise myself? What am I permitted to do?** A counterpart answers the same questions independently.

This is an engineering application of Promise Theory, not a claim that the book specifies this wire protocol. The precise theoretical references and reading record are in [sources](sources-and-decisions.md). In particular, the word `intent` below names a protocol object. It does not assert that a disclosed intention lies outside the book's broad category of promises.

### Three independent dimensions

| Dimension | Examples | Must not imply |
|---|---|---|
| Market posture | Seek a result; seek work; seek collaboration | Promise polarity, duty to buy, or duty to sell |
| Speech act | Declare interest; invite contact; propose terms; issue a promise | Automatic advancement to a later act |
| Promise polarity | Provide (`+`); receive/accept/use (`−`, with behavior specified) | Good/bad, buyer/seller, assent to a contract, or result quality |

An agent seeking a report might promise to provide inputs (`+`) and to receive and review a report (`−` plus a specified review behavior). A provider might promise to receive those inputs (`−`) and produce a report (`+`). Each arrow belongs to its own author. A recipient's willingness to listen does not promise to accept an offer.

## 2. Invariants

1. **Self-authorship.** Only authenticated adoption by the identified promiser can issue its promise. A relay preserves original authorship. Proposed counterpart behavior remains a request until that counterpart adopts it.
2. **Separate declaration from exchange.** An `intent` does not create a service offer, a purchasing promise, a reservation, an agreement, or execution permission.
3. **Reception is explicit.** Delivery of a proposal requires the recipient's current admission policy or a recipient-issued permit. Public visibility is not consent to direct messages.
4. **No forced reciprocity.** Matching complementary needs, capabilities, or promise descriptions creates no reciprocal promise.
5. **Immutable meaning.** Offers, promises, accepted terms, and evidence are content-identified. Corrections create new records; no silent mutation or deletion of history.
6. **Finite negotiation.** Every channel has an absolute expiry and finite directional message and byte allowances. Activity cannot reset them.
7. **Local authority.** Commitment authority, reception permission, execution authority, and payment authority are distinct. One cannot be substituted for another.
8. **Independent assessment.** A delivery or an evaluator's finding remains attributable to its author. A selected acceptance procedure does not erase other assessments or establish universal truth.
9. **Explicit uncertainty.** Missing evidence, unsupported semantics, conflicting heads, and unknown external effects block dependent transitions. Silence is never assent.

## 3. Common record and identity rules

A protocol record carries `profile`, `kind`, `id`, `issuer_agent_id`, `issuer_principal_id`, `created_at`, its typed `body`, and required-extension identifiers. Signed statements additionally bind the intended recipients, disclosure policy, and the exact canonical record digest.

Canonical bytes use RFC 8785 JCS, UTF-8, and SHA-256. Duplicate JSON member names, nonfinite numbers, and values outside the chosen JSON profile MUST be rejected before canonicalization. Money is a decimal integer string in explicitly identified minor units. Missing fields and explicit null are distinct. Signed records and all referenced content MUST be retained as exact bytes for replay and audit.

An identity binding maps the authenticated A2A caller or verified original record issuer to its principal and allowed acts, using the deployment's existing identity and authorization systems. The research demonstration uses an allowlist within that system. Agent Bazaar defines no identity provider, key registry, login flow, or credential format; self-asserted identity fields are insufficient. An agent may be a declared composite service, but its external promise is that service's promise, not a fabricated signature from every component. Claims of capability are separately assessed.

Disclosure audience describes permitted dissemination in this profile; Promise Theory's scope describes agents informed about a promise. Neither grants execution authority. A receive/use promise specifies reception behavior independently of assent to terms and later quality acceptance.

The profile enforces structured authorship and required policy evidence. It cannot determine from arbitrary prose whether an actor truly controls every behavior, possesses the claimed skill, or will keep a promise. Unknown required behavior types or unresolved ownership questions MUST prevent automatic adoption.

The A2A binding uses native transport authentication and selects an existing proof suite or authenticated original retrieval for portable promise authorship. The release pins that profile and its verification requirements. Agent Bazaar defines no new signature algorithm or authentication exchange. Its JSON Schemas cover semantic bodies; the selected native mechanisms validate authentication and authority.

Canonicalization above applies to Agent Bazaar records. Native mandates, payment offers, credentials, and receipts retain their original bytes and native verification procedure; they MUST NOT be rewritten into an Agent Bazaar signature envelope.

## 4. Intent emission and publication

A `publication_contract` declares the issuer's high-level consent and commercial eligibility rules. Existing discovery and subscription services interpret it as sales/business rules: who may discover or receive a publication, which uses and interactions are allowed, and which complete commercial routes are eligible. They may add matching, subscription, ranking or other capabilities on top. The contract does not promise an offer, availability, negotiation, purchase, execution or payment.

The record includes a stable contract ID, immutable revision chain, validity interval, current-status reference, discovery consent, contact/admission profile and policy references, and `eligible_commercial_routes`. Its issuer controls its own consent. Referenced policies are immutable, content-identified documents; a current status source supplies withdrawal/revision status under the deployment's existing authentication. A cached document alone is insufficient to establish current consent. The [publication schema guide](publication-contract.md) defines field semantics.

Each external commercial route is one complete supported combination of AP2 order-validation profile, paid-exchange protocol/profile, native processor configuration, and settlement scheme/asset/network, with an immutable native route-policy reference. These MUST NOT be interpreted as freely mixable option lists. `none` and `simulated` routes are explicit. Publication contains identifiers and policy references, never credentials or a spending grant. Native route policy retains restrictions already defined by the underlying frameworks.

An `intent` includes a stable intent ID, revision, previous revision digest, market posture, desired outcome, preferences, disclosure audience, expiry, and `publication_contract_ref` naming exact publication bytes. Its semantic label is `interest_declaration`.

- `seek_result`: the emitter seeks an outcome.
- `seek_work`: the emitter seeks opportunities to supply a capability.
- `seek_collaboration`: the emitter seeks a reciprocal relationship not yet assigned buyer/provider roles.

These labels select discovery interpretation, not a promise to transact. Indicative price or capability claims MUST be labeled as preferences or claims; they are not an accepted quote or proof of availability. Intent disclosure MUST fit within the referenced publication's audience and permitted uses; neither field can broaden the other.

Publication means making a declaration available for permitted discovery or delivering it through a permitted subscription. “Broadcast” MUST NOT mean unsolicited messages to every reachable agent. Services may narrow distribution or eligibility; they MUST NOT broaden consent, reinterpret intent as an offer, or substitute an unadvertised processor or settlement route.

Identical `(issuer, intent_id, revision, digest)` deliveries are duplicate observations. Conflicting content at one revision is quarantined. The previous-digest chain must verify before a revision becomes current. Republishing cannot reset admission quotas or turn one desire into multiple purchases.

Expiry, withdrawal or supersession closes new delivery/contact under that publication revision. Pending offer formation MUST revalidate current applicable publication consent, referenced policy status and route eligibility. Previously admitted channels may use their bounded status/closure path; further proposals require current consent. Changed material policy or route selections require a fresh offer. Already finalized agreements keep their accepted terms: withdrawing discovery consent is not agreement cancellation, mandate revocation, rollback or refund.

## 5. Invitation and negotiation admission

The core contract defines the meaning and limits of consent. A named admission profile, supplied by an existing discovery/subscription service or another implementer, defines how that consent is established and enforced. The profile MUST be understood and accepted by the recipient; unknown required semantics prevent admission. Missing policy means closed.

Every conforming admission profile MUST provide:

1. Authenticated, recipient-controlled permission for the topic, sender or eligible sender class, and interaction being admitted. Only that recipient can broaden its reception consent.
2. Finite message/byte limits and an absolute lifetime for each negotiation, plus finite aggregate ingress and active-negotiation limits. Limits apply before model inference; changing intent, carrier, or channel identifiers does not reset the recipient's aggregate limits.
3. Durable deduplication of logical operations, explicit offer revision/supersession, and rejection of conflicting reuse of an operation identity. Replays do not create new offers or commitments.
4. No implicit renewal through traffic or silence. Additional interaction requires current consent under the selected policy. Iterative offers are explicitly permitted within that policy and consume its finite allowances.
5. A bounded means to close negotiation and reconcile an already-pending commitment even when proposal capacity is exhausted. Status reads cannot submit fresh proposals or create acknowledgment loops.
6. Consistent enforcement across carriers serving the same recipient, with a defined source of current policy status. Unavailable enforcement or required status evidence blocks dependent admission.

Implementers may use existing subscription entitlements, gateway admission, bilateral invitations, or another documented mechanism to meet these requirements. Ranking, targeting, commercial eligibility, subscription management, routing and capacity allocation remain service business rules. The schema exposes their versioned policy references; it does not standardize their algorithms or service APIs.

The [reception-permit reference profile](reference-negotiation-profile.md) supplies one concrete implementation contract: directional permits, atomic sequence/byte accounting, a coordinator for duplicate open requests, and demonstration budgets. These details apply only when that profile is selected. Network denial-of-service and Sybil resistance still depend on the deployment's security controls; bounding admitted negotiation does not eliminate hostile network traffic.

## 6. Offers, counteroffers, and promises

An `offer` is a proposed exchange containing:

- The author's proposed **own promises**, each with a typed behavior, promiser, promisees, provide/receive polarity, conditions, limits, and assessment method.
- **Requested counterpromises**, visibly marked as descriptions the counterpart has not adopted.
- Channel ID, author-local offer sequence, previous own-offer digest, optional peer-offer basis, expiry, exclusions, and required extensions.

Every offer carries both parties' exact `publication_contract_refs`, an `offering` descriptor, a `performance_terms_ref`, its proposed settlement terms, and a `commercial_route_selection` containing `route_id` and `route_digest`. Candidate terms carry the identical selection and the exact referenced performance terms. A route digest covers the entire route object. Both applicable publication contracts MUST contain that identical route object; route IDs are shared identifiers for a complete combination, not permission to substitute a similarly named route. Matching services can propose additions through a new issuer-approved publication revision, never silently synthesize compatibility.

`offering` identifies a product, service or capability and its fulfillment mode: MCP endpoint, A2A task, artifact, subscription, physical fulfillment or an explicitly specified other mode. Its specification reference identifies the exact promised product/service. Offering an MCP endpoint does not require Agent B to call an MCP tool; it may be the endpoint's provider. The selected performance profile defines fulfillment, inputs, assessment and deadlines. Unknown required profiles prevent adoption. The research profile contains its report inputs, deliverables, rubric and review windows; those are not mandatory fields for every product.

Competing offers MAY differ in offering, scope, price, performance terms or route. The two offer heads selected for one candidate agreement MUST agree on that candidate's offering, performance terms, route and settlement terms before formation. Disagreement remains negotiation; the coordinator cannot insert a different price, processor, deliverable or rubric into the final bundle.

Either party may offer first or counteroffer. The first profile permits proposals only; it does not silently embed a firm service promise inside an `offer`. A standing conditional service promise is a separate `promise_issued` statement.

Each party has one live offer head per channel. A new offer supersedes only that party's prior head and must identify it exactly. Identical content is a no-op and cannot renew expiry, create another commercial obligation, or replenish quota. Changed content always consumes a new allowance. Repeated old content with a new ID is still subject to all rate and byte limits.

Crossed offers are permitted. They are not mutual assent. A proposed bundle identifies both complete offer heads; an implementation MUST NOT cherry-pick an old price and a new scope. Stale or forked heads require explicit resolution within the remaining budget. Offers are private to the channel unless separately published with the participants' consent.

`promise_issued` is an autonomous act by its promiser, referencing an exact promise description and commitment-authority evidence. Promises may exist before or outside a bilateral agreement. Each may be conditional, time-bounded, or later withdrawn by its author; withdrawal does not erase historical issuance or counterparty assessments.

The profile's behavioral fields require `performer_agent_id = promiser_agent_id = authenticated adopter`. “I will ask another agent” promises the asking, not the other's delivery. A third-party dependency has no attributed promise coverage until that party issues its own promise, or it is covered by an explicitly modeled composite service's own promise. Promise coverage alone does not establish fulfillment. Subcontracting is unsupported in the first execution profile.

Each condition identifies its meaning, who reports/assesses it, required evidence, and when it is checked. Cyclic prerequisites with no initiating action are ineligible for execution. `unknown` is distinct from false and true. A mere string such as “if satisfied” is insufficient.

Channel close, expiry, or quota exhaustion prevents further offers. If no award is pending and no agreement exists, the outcome is `no_agreement`. A pending award resolves under its deadline through the reserved control path; quota exhaustion alone does not discard an admitted acceptance. The award deadline MUST be no later than the channel expiry. Closing communication does not automatically withdraw an independently issued promise. No party can force convergence, responsiveness, or continued negotiation.

## 7. Bilateral reference formation profile

The general primitives are symmetric. Candidate terms explicitly select `formation_profile`. The bilateral reference profile, `https://example.org/extensions/agent-bazaar/profiles/bilateral/v0.1`, chooses the buyer as a **local formation coordinator**, with both parties' prior consent. It requires a buyer-owned procurement slot and may serve any product or service, including the research demonstration. This operational choice gives the coordinator no power to author the provider's promises. Another declared formation profile must preserve self-authored adoption, exact terms, durable unambiguous acceptance evidence, and prevention/reconciliation of duplicate commitments. Its implemented semantics must be understood before adoption; an unknown profile cannot establish accepted-offer evidence. The core does not require another profile to copy this slot mechanism.

1. **Candidate:** compile exact current offers into complete agreement terms, including parties, input/deliverable specifications, reciprocal promises, acceptance procedure, conditions, deadlines, cancellation, correction budget, data limits, and the selected `none`, `simulated`, or `external` payment binding. Both agents inspect the same bytes.
2. **Award:** the buyer atomically selects one candidate under a buyer-scoped procurement slot, adopts only its own listed conditional promises, and issues an award naming the terms digest and acceptance deadline. It has at most one outstanding award in that slot across all carriers.
3. **Provider adoption:** the provider checks the candidate, offer heads, its own capacity and authority, then adopts its own listed conditional promises. Its signed acceptance references the exact award and terms digests. It may decline.
4. **Finalization:** the buyer validates and durably records the provider's acceptance before its own award deadline, checks the award is still active, verifies both parties' commitment-authority evidence and formation pins, revalidates both current publication policies and the complete selected route, and atomically consumes the slot. It signs an `agreement_finalized` receipt naming both adoption records, offer digests, and terms digest.

Award atomically pins the buyer's referenced own offer; provider adoption atomically pins the provider's referenced own offer after checking it remains current. A pin does not extend offer validity: the award deadline MUST be no later than both referenced offers' expiry and the channel expiry. A pin prohibits silently superseding that head within the pending formation attempt. A desired revision requires explicit award close/reconciliation first. Close/withdrawal requests admitted by the coordinator serialize against finalization: close first makes acceptance ineligible; finalization first preserves the agreement and later withdrawal becomes an attributed post-formation event. A peer cannot free a pending reservation on a lost response or its own timestamp alone; it must reconcile the durable outcome. An agent remains able to refuse future execution or withdraw its promise, but that act does not rewrite prior signatures or retroactively undo finalization.

Formation depends on the coordinator's authenticated receipt order, not a provider-supplied timestamp. A provider's acceptance without finalization remains pending from that observer's perspective. A lost finalization response requires retrieving the same record; it is not permission to start or to select another provider.

Finalized terms cannot be amended in place. Material changes require a new candidate and explicit adoption of any changed promises. The reference profile prohibits changing a finalized agreement; terminate/reconcile it before forming a linked replacement.

In the research performance profile, the delivery window begins at the native runtime's first durable execution-admission receipt for this agreement, and the review window begins when the buyer durably admits the first complete digest-verified delivery. The agreement selects that admission clock and evidence source. Retries and the single correction do not reset either window. The execution binding records the resulting absolute deadline; it does not alter the native authorization lifetime. If human review cannot fit, the outcome remains unresolved or the parties explicitly replace the agreement; no unstated extension is inferred. Other performance profiles define their own timing and correction terms.

An unfinalized award may be closed before another is issued. A finalized slot is never reopened, even after cancellation. A new procurement needs a new linked slot and fresh authority. The one-winner guarantee is within a conforming buyer's declared slot; it cannot stop a malicious buyer signing inconsistent records or creating another slot for equivalent work.

The signed bundle is a protocol agreement, not a representation of legal enforceability. A promise's independent lifecycle and each observer's assessment remain available alongside the agreement's projection.

## 8. Native fulfillment, order commitment, and payment binding

A2A mediates communication between Agent A and Agent B. The offering determines fulfillment: B may supply an MCP endpoint, run a task, deliver an artifact, activate a subscription, or supply another product or service. Native MCP access and invocation remain MCP's responsibility. Agent Bazaar MUST NOT create substitute task operations, tool schemas, authorization credentials or financial state machines.

### Mandatory paid-transaction sequence

For the Agent Bazaar paid profile, the order is **accepted offer → AP2 order validation/commitment → selected paid exchange → native processing and settlement**. Here, accepted offer means finalized agreement evidence covering the exact current offers and each party's own adopted promises. Merely publishing an intent, proposing an offer or sending an acceptance without the required finalization is insufficient. This is the Bazaar composition contract, not a claim that native x402 or Machine Payments Protocol independently requires Bazaar or AP2.

1. The finalized agreement pins both publication revisions, complete route, offering, performance terms, payee, and exact native commercial terms (including price/amount basis, units, limits and trigger).
2. The transaction-specific AP2 Checkout and Payment Mandates MUST authorize that same order. Native verification checks the merchant-signed checkout, checkout hash, transaction identity, mandates and applicable constraints under the selected AP2 profile. Successful verification establishes an **authorized order commitment carrying the payment obligation defined by the accepted terms**. It is not payment execution or evidence that the deliverable was accepted.
3. Only after accepted-offer evidence and successful native order validation may the selected x402, Machine Payments Protocol or other paid exchange authorize or initiate that transaction's payment. Native processors, schemes and settlement execute the selected route and return native outcomes. No processor, asset, network or verification-profile fallback outside the accepted route is permitted; a material change requires fresh offers and acceptance.
4. Native receipts are retained as they become available. A final AP2 Checkout Receipt can follow payment, so the prerequisite is successful native verification, not an already-successful final checkout receipt. Missing or unknown verification blocks payment; missing payment outcome requires reconciliation of the same action identity.

Open AP2 mandates and principal delegation may exist before discovery or negotiation. They do not accept a particular offer. Bazaar's downstream gate applies to closing/presenting transaction-specific mandates and initiating payment for that order. Existing native APIs still own mandate closure, verification and receipt generation. [AP2 specification](https://ap2-protocol.org/ap2/specification/), [authorization framework](https://ap2-protocol.org/ap2/agent_authorization/), [native flow ordering](https://ap2-protocol.org/ap2/flows/).

Payment may occur before fulfillment, at an agreed milestone, or after **delivery acceptance**. Every such trigger remains downstream of **offer acceptance** and order validation. A paid-resource challenge encountered while fulfilling the job creates no new authority: the charge must fit an already accepted offer/order and authorized route, or a separate accepted transaction must be formed. Charging for discovery or negotiation is likewise a separate transaction under previously accepted service terms. Native free discovery/quote inspection does not itself execute payment. `none` and `simulated` routes create no payment obligation or payment authority and do not invoke AP2 or a paid exchange. The research demonstration selects simulated payment.

### Bindings and native verification

An `external_binding` identifies the exact agreed terms in `agreement_digest` and the exact finalization receipt in `finalized_agreement_ref`, together with subject, stable action identity, native protocol/version, native subject identifier and native evidence references. Its purpose is `authorization`, `order_validation`, `payment` or `commerce`. Commercial bindings include `selected_route_digest`; payment bindings also identify the successful AP2 order-validation binding through `order_validation_binding_ref`. All linked records MUST name the same finalized terms, route and applicable native order/payment subject. A candidate terms digest alone does not prove acceptance.

Bindings preserve original native bytes, media type, digest and access-controlled location. Native signatures, mandate/quote validity, parties, resource, currency/asset, amount, timing and outcomes are verified using the native protocol. The extension then checks those facts against the exact agreed subject and route. Native commercial terms referenced during negotiation are terms or quotes; a downstream mandate/receipt is separately bound after acceptance. No circular requirement makes an offer contain a future payment receipt. See [binding fields](protocol-architecture.md#native-authority-and-payment-bindings).

The selected native binding profile MUST establish an authenticated association between the native order/payment identity and the exact finalized agreement and obligation. Matching only parties, resource and amount is insufficient. An Agent Bazaar wrapper cannot manufacture that association: it must be verifiable from native signed evidence or the selected native system's authenticated, durable correlation mechanism. The same native payment effect MUST NOT satisfy multiple obligations merely because multiple bindings reference it. Any split or allocation requires explicit accepted terms, native support and verification of the allocations without double counting. If the native integration cannot establish this association, that route is unsupported.

The selected execution-authority verifier checks its own grants, scope, validity and revocation. The extension verifies coverage for the exact executor, operation, plan, inputs, resources and limits. AP2 order commitment is not arbitrary tool or data-access authority. A native grant may narrow work; a binding cannot expand it. Unknown, stale, mismatched or unsupported evidence blocks the dependent action. Storing any binding grants nothing and establishes no settlement status.

The research runtime enforces public-source reads and the designated artifact sink immediately before protected actions, including credential, redirect, egress, resource and spending policy. Concurrent action/budget admission must be atomic; unknown effects retain their reservation until reconciled. These are requirements on the selected existing enforcement mechanism. Credentials, wallet custody, charging, escrow, settlement, refunds and native checkout/order lifecycles remain with their selected protocols and providers. UCP/ACP may supply the native commerce context underneath AP2 and the chosen payment route; they do not bypass the accepted-offer or order-validation gates.

The A2A binding MUST advertise and activate the versioned extension, require activation acknowledgment, carry records in native messages/artifacts, and use existing task operations. Commercial states remain extension data. `ROLE_USER` / `ROLE_AGENT` never determine the buyer, provider, or promiser. Negotiation tasks bind intent/channel references; execution tasks add the finalized agreement. Task/context IDs retain their server-local endpoint/tenant meaning. Cross-server linkage uses extension agreement/action references; clients MUST NOT invent task IDs or assume context IDs are portable.

| Native observation | Extension interpretation |
|---|---|
| Task submitted / working | Provider reports queued/running; native admission evidence must bind task, action and authority |
| Input required | Obtain information using A2A; material changes still require new agreed terms |
| Authorization required | Complete the native authorization flow; the status itself grants nothing |
| Task completed | Native execution finished; assess delivered artifacts under the agreement |
| Failed / rejected / canceled | Retain native outcome and known effects; apply separate agreement consequences |
| Timeout or lost response | Preserve unknown outcome and reconcile the original operation |

Invoke native `GetTask`, subscriptions and `CancelTask` instead of defining replacements. A2A cancellation is an attempt; a terminal task is not reopened. A permitted correction uses another task linked to the same agreement and correction allowance. Use native idempotency where provided and require durable agreement-level record/action deduplication where core A2A does not guarantee it. A lost task or payment response MUST NOT create a new execution or charge identity.

## 9. Delivery, assessment, acceptance, and cancellation

A delivery uses native A2A artifacts and extension references binding agreement, execution, input and artifact digests. It identifies source evidence, limitations, observed effects and consumption, with attributable provider evidence under the selected native proof/trust profile. A URL is a locator, not immutable content or proof of truth.

An assessment binds the exact delivery, criterion IDs, rubric version/digest, evaluator identity, observations, and `pass`, `fail`, or `indeterminate` per criterion. The research profile uses deterministic structural checks plus a named human semantic reviewer. Buyer acceptance is a separate signed statement referencing delivery and assessment digests. A receive/use promise is not this acceptance decision.

Timeout, missing sources, insufficient evidence, reviewer disagreement, and remaining failures after the correction budget produce `unresolved` or explicit rejection. They never produce automatic acceptance. Independent conflicting assessments are retained. No reputation update may masquerade as a source-verification fact.

Cancellation references native A2A requests/results and records their agreement-level consequences and remaining effects. Native authority revocation prevents future admitted actions at conforming enforcement points; it cannot undo in-flight or completed effects. A canceled task is not proof of rollback or refund. Replacement work remains blocked while duplicate effects cannot be excluded.

Native payment evidence is retained under the external binding in section 8. Simulated quotes cannot produce a paid receipt. Payment timing and remedies follow the selected contract; acceptance, payment authorization and payment outcome remain distinct.

## 10. Errors, replay, and extensibility

Receipts distinguish transport receipt, admission, semantic validation, promise adoption, and finalization. A transport acknowledgment must never be interpreted as another stage. Durable replay/tombstone retention MUST outlive all accepted record lifetimes and the declared retry horizon. Restart must not reset quotas, reopen slots, or forget canceled work.

| Code | Meaning / permitted next step |
|---|---|
| `CONTACT_NOT_INVITED` | No permitted initial interaction; stop |
| `PERMIT_EXPIRED`, `PERMIT_REVOKED` | Stop or await explicitly renewed consent |
| `RATE_LIMITED`, `BUDGET_EXHAUSTED` | Respect policy; no alternate-carrier bypass |
| `REPLAY_CONFLICT`, `HEAD_CONFLICT` | Quarantine conflicting bytes; resolve explicitly |
| `COUNTERPART_PROMISE_NOT_ADOPTED` | Await that actor's own adoption |
| `CONDITION_UNKNOWN` | Block transitions requiring the condition; recording a conditional promise/agreement remains possible; unknown proves neither fulfillment nor breach |
| `UNSUPPORTED_REQUIRED_SEMANTICS` | Do not finalize or execute under an uninterpretable required feature |
| `PUBLICATION_STALE`, `ROUTE_INELIGIBLE` | Resolve current policy or revise the offer; no silent fallback |
| `OFFER_NOT_ACCEPTED`, `ORDER_NOT_VALIDATED` | Block transaction-specific payment; obtain missing native evidence |
| `AWARD_CLOSED`, `SLOT_CONSUMED` | Reconcile existing records; never reopen implicitly |
| `AUTHORITY_INVALID`, `SCOPE_MISMATCH` | Block protected action |
| `REMOTE_OUTCOME_UNKNOWN` | Status reconciliation; no replacement effect |

Unknown required extensions MUST be rejected. Unknown optional extensions may be preserved without taking authority from them. An adapter that cannot preserve required meaning MUST fail visibly, not silently drop a field. Breaking semantic changes require a new profile identifier and fresh adoption.
