# Conformance plan

These are **specified cases, not executed runtime tests**. Structural artifact checks are separate in [validation](validation.md).

Core cases apply to every implementation of the declared feature. Paid-route cases apply to real paid exchanges; `none` and `simulated` do not execute them. Reference negotiation cases apply to the concrete mechanism in [reference-negotiation-profile.md](reference-negotiation-profile.md), and research cases apply to the source-backed research demonstration. An alternative discovery, subscription, or admission service proves the core guarantees through its own mechanism; it need not reproduce the reference permits or counters.

## Core behavioral cases

| ID | Input / race | Required observation |
|---|---|---|
| C01 | Buyer publishes interest in research | No service/purchase promise, offer, reservation, agreement, or execution is inferred |
| C02 | Provider publishes interest in research work | Same distinction with roles reversed |
| C03 | Buyer constructs a proposed provider promise | It stays a description until provider-authenticated adoption |
| C04 | A issues a promise with B as performer/promiser | Reject autonomous self-promise validation; do not manufacture B's adoption |
| C05 | Agent promises to receive proposals | It has not promised commercial assent, delivery acceptance, or payment |
| C06 | A standalone conditional promise is issued | Record it without requiring bilateral agreement or granting execution authority |
| C07 | Intent has no valid publication/contact consent | Do not initiate unsolicited direct contact |
| C08 | Same intent is relayed by two carriers | One declaration; retained provenance; no extra purchasing demand or reception allowance |
| C10 | Offer arrives before reception consent | Reject under the recipient's selected admission policy before negotiation model work |
| C14 | Clarification loop reaches an admission-policy limit | No clarification bypass or automatic renewal; negotiation may end without agreement |
| C15 | Offer changes price, scope, route, or conditions | New immutable revision; old head superseded; remaining limits still apply |
| C16 | Delayed old offer or crossed counteroffers arrive | No silent acceptance; no head rollback; only an explicit compatible bundle proceeds |
| C17 | Identical offer is republished with a fresh ID | No additional promise; bounded-admission protection remains; lifetime does not reset |
| C18 | One provider negotiates while another responds | Independent consented negotiations; one does not silently reserve all demand |
| C20 | Unknown conditional prerequisite | Keep conditional statement; block only transitions requiring the established condition |
| C21 | Mutually dependent conditions lack an initiating action | Flag deadlock; do not start work on assumed prerequisites |
| C25 | Agreement exists but native execution authority is absent, expired, or revoked | No protected action begins |
| C26 | Plan, input, executor, resource, or audience differs from verified native authority | Scope mismatch; block |
| C27 | A2A reports completed | Fulfillment observation recorded; no automatic delivery acceptance or payment |
| C28 | Execution dispatch times out | Unknown state retained; same operation reconciled before a replacement |
| C29 | Cancellation arrives during an action | Apply native cancellation and stop future admission where enforceable; preserve in-flight and completed-effect uncertainty |
| C33 | Two observers disagree on a promise | Preserve both attributed assessments and the named acceptance procedure |
| C34 | Unknown required extension or lossy adapter mapping | Fail visibly before dependent formation or execution |
| C35 | Simulated settlement record | Never reported as real payment or a spending grant |
| C36 | Required A2A extension is not acknowledged | No dependent negotiation, adoption, or execution transition |
| C37 | Provider acts as A2A client and buyer as server | Message roles do not invert promise authorship or assign market roles |
| C38 | A valid native payment receipt is present | Validate it natively and bind it to the obligation; do not infer delivery acceptance |
| C39 | A native payment/authorization profile cannot be validated | Reject that binding; do not create an ABP substitute credential or receipt |
| C40 | Agreement selects an upfront native payment flow | Commercial offer acceptance and required AP2 validation precede payment; delivery acceptance need not precede payment; never charge twice |
| C41 | Native mandate, quote, or receipt bytes pass through a carrier | Preserve signed bytes and native verification; changed agreement subjects require renewed binding |

## Publication, consent, and general offerings

| ID | Input / race | Required observation |
|---|---|---|
| C42 | Publication permits indexing and matching but excludes direct contact | A service may perform only the permitted uses; visibility or a match does not authorize a message |
| C43 | A relay or subscription service proposes a broader audience or redistribution use | Require the publisher's consent for that use; the service cannot enlarge it |
| C44 | Discovery or admission service uses its own subscription/rules engine | Accept a conforming implementation that preserves consent, bounded iteration, durable deduplication, and reconciliation without issuing reference-profile permits |
| C45 | Publication permission is withdrawn while an intent remains cached | Stop new contact under that permission; preserve historical records and independently accepted agreements |
| C46 | Referenced policy is expired, stale, unavailable, or superseded during formation | Revalidate current applicable permission; unresolved eligibility blocks formation; no silent policy substitution |
| C47 | Discovery returns a combination assembled from individually supported payment components | Reject unless the combination is an eligible complete commercial route under both parties' applicable contracts |
| C48 | Parties reference different publication-contract revisions or route digests | Continue negotiation or reject; acceptance must pin the same complete terms and eligible route |
| C49 | Accepted route later becomes unavailable | Block dependent payment and reconcile; do not silently fall back to another processor, scheme, asset, network, or validation profile |
| C50 | An adapter ignores an unknown required consent or route constraint | Reject the adapter mapping before dependent contact, formation, or payment; an optional annotation grants no permission |
| C51 | Provider offers MCP endpoint access | Use the offering specification and native MCP access/authorization rules; no research report, rubric, or procurement slot is required by the core |
| C52 | Provider offers another product or service | Preserve its offering kind, fulfillment method, specification digest, promises, and assessment terms; A2A remains agent communication |
| C53 | Referenced offering specification or performance terms change, or candidate performance terms differ from the offer's reference | Digest mismatch blocks dependent formation, fulfillment, or acceptance; location identity cannot replace content identity; unknown required performance profiles prevent adoption |

## Paid-route cases

| ID | Input / race | Required observation |
|---|---|---|
| C54 | Agent receives an x402 or MPP payment challenge before accepting an offer | No payment is authorized by the intent, discovery result, contact consent, or challenge; complete commercial acceptance first |
| C55 | Accepted offer exists but AP2 validation/commitment is missing, mismatched, or invalid | Block the dependent paid exchange until native order and authority validation covers the exact accepted terms and obligation |
| C56 | Open or previously issued AP2 mandate predates negotiation | Preserve its native lifecycle; validate that its authority covers the accepted order before payment; prior existence alone does not constitute accepted terms |
| C57 | Valid AP2 order commitment is followed by the selected x402 exchange | Native exchange uses only the pinned eligible processor and settlement path; bind its native evidence to the same agreement and obligation |
| C58 | Valid AP2 order commitment is followed by the selected Machine Payments Protocol exchange | Apply the selected MPP profile natively and preserve the same route, agreement, and obligation bindings |
| C59 | Native final records or receipts become available only after payment | Require pre-payment validation evidence appropriate to the native flow; record later evidence under the same action without fabricating an earlier receipt |
| C60 | Paid exchange or processor response is lost after submission | Preserve unknown outcome, action identity, and native reservation state; reconcile before any retry that could create another charge |
| C61 | Native receipt names another payee, amount, asset, resource, or operation | Reject the agreement binding even if the native signature is valid; do not infer settlement of this obligation |
| C62 | Agreement uses `none` or `simulated` | Keep the selected non-paying mode explicit; no live AP2 payment commitment, x402/MPP charge, or processor settlement is inferred |
| C63 | One authentic native payment receipt is rebound to two finalized obligations with identical commercial values | Require authenticated native association to the exact obligation; reject double counting unless an explicit, verified native allocation is authorized by accepted terms |

## Reference negotiation and research cases

| ID | Profile | Input / race | Required observation |
|---|---|---|---|
| C09 | Reference negotiation | Simultaneous bootstrap requests with the same trigger set | One canonical negotiation episode; bounded setup messages; no echo loop; different trigger sets remain subject to aggregate quotas |
| C11 | Reference negotiation | Same permit sequence and bytes arrive twice | Return original receipt once; no extra consumption or semantic transition |
| C12 | Reference negotiation | Different bytes reuse a permit sequence | Replay conflict; neither variant overwrites the other |
| C13 | Reference negotiation | Parallel messages consume last allowance through different carriers | Exactly one is admitted by shared recipient authority |
| C19 | Reference negotiation | Close after negotiation quota is exhausted | Bounded control allowance still permits close; later substantive messages rejected |
| C22 | Research formation | Award expires concurrently with provider acceptance | Coordinator admission order determines finalization; provider timestamp cannot win race |
| C23 | Research formation | Awarded offer is superseded or withdrawn while acceptance is pending | Apply the formation freeze/closure rule; never mix revisions |
| C24 | Research formation | Lost finalization acknowledgment, then restart | Retrieve same frozen agreement; do not issue a second winner |
| C30 | Research assessment | Result passes schema but source does not support a claim | Human rubric assessment fails or remains indeterminate; structure is not truth |
| C31 | Research assessment | Review deadline passes | Unresolved, not accepted |
| C32 | Research assessment | Correction delivered after correction budget exhausted | No implied new task or acceptance; explicit new agreement required for more work |

## Demonstration trace

The research trace must contain both buyer-first and provider-first intent publication, high-level consent and publication-contract references, at least two independent provider channels, an ineligible proposal, a valid counteroffer exchange, one selected simulated route, and a single finalized winner. It then shows a valid public-source execution, one failed claim assessment corrected within budget, and final delivery acceptance.

Separate adverse traces must show replay across carriers, exhausted reference negotiation budget, attempted authorship of another agent's promise, withdrawn publication consent, incompatible commercial routes, revoked authority, lost dispatch response, and review timeout. None may be edited into a clean success path after the fact.

Paid-route conformance requires separate native evidence for commercial acceptance, AP2 validation/commitment, the x402 or MPP exchange, and the selected processor/settlement outcome. The simulated research trace does not establish that these live flows have executed. Test payment timing both before fulfillment and after delivery acceptance under explicitly agreed triggers.

## Interoperability evidence

Each implementation exports exact records, publication-contract and consent evidence, applicable policy revisions, route selection, local admission outcomes, offer-head history, promise adoption references, agreement-formation evidence, native authority decisions, task mappings, artifact digests, assessments, and unresolved states. Reference-profile participants additionally export their permit and sequence evidence. Replay those records in a second independently implemented participant.

Compare the normalized meaning of consent, accepted terms, selected route, and the reasons for rejecting invalid transitions. Different admission implementations must agree on these meanings without sharing a permit format or rules engine. Sharing a schema or SDK is insufficient proof of independent interpretation. Report unsupported features explicitly. A passing local implementation cannot by itself establish cross-market adoption, adversarial security, real payment settlement, or a standards body's approval.
