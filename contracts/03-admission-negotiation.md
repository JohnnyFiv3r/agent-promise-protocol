# C3 — Admission and negotiation

**APP 0.4-draft · normative · MIT**

This contract governs how a recipient admits work while allowing iterative offers. It applies to the [semantic records](../schemas/contract.schema.json), [interaction envelope](../schemas/interaction.schema.json) and [admission declaration](../schemas/admission-policy.schema.json). Numbers, validity and replenishment are policy choices, not protocol defaults.

## C3-01 — Actors and authority

The recipient controls its admission scope. Its principal or explicitly authorized policy administrator selects eligibility, limits and enforcement authority. A discovery service or relay MAY enforce delegated admission but MUST NOT expand it. The sender chooses what to request within that permission; it cannot mint allowance by changing transport, identity aliases, option IDs or negotiation IDs.

Co-hosting recipients does not merge their allowances. Accounting MUST follow the declared recipient/allowance scope, including any owner-authorized shared scope across senders or routes. An unrelated recipient's options MUST NOT consume a local live-option allowance solely because their journals share a physical database. Conversely, a new sender alias, offer, session or routing service MUST NOT reset an allowance covering that same scope.

An `admission_grant` is recipient-authored permission under a referenced publication/admission policy. It is the invitation when contact policy requires one. It is not a service offer, acceptance, standing promise or reservation of the recipient's capacity. The grant's peer, purpose, allowance and validity MUST be subsets of the issuer's current delegated permission. A native admission mechanism MAY supply equivalent understood evidence instead. No grant is required where current publication policy already admits the first offer.

## C3-02 — Required admission declaration

An understood declaration MUST expose recipient identity, stable `recipient_scope_id`, accounting authority, a native authority reference, eligibility semantics, allowed record kinds, validity, authenticated freshness/status semantics and finite allowance pools. Each pool specifies admitted record kinds, the explicit `operation_purposes` it admits, messages, aggregate canonical payload bytes, work units, in-flight operations and live options. The baseline purposes are `submit_record`, `query_status` and `finalize_candidate`; enabled C8 handoff adds `prepare_handoff`, `dispatch_handoff` and `reconcile_handoff`. For submission, both the purpose and record kind must be allowed. A grant declares `operation_purposes` as a subset of its governing pools. Merely enabling a feature grants no traffic allowance. Work-unit meaning is explicit; an unbounded unit is not a finite allowance.

Pools MUST distinguish negotiation traffic from protected control traffic. Refusal, notice, withdrawal, current-status retrieval and operation recovery have applicable bounded paths that do not depend on remaining offer allowance. Control allowance MUST NOT be spendable on offers or clarifications. New C7 plan/binding submissions and C8 prepare/dispatch work consume explicitly provisioned bounded work pools; they cannot borrow the principal-refusal reserve. Reconciliation has its separately provisioned bounded recovery path. An authority MUST reserve or prioritize enough service to honor its admitted principal-refusal rules; arbitrary unauthenticated traffic cannot consume another principal's protected allowance. An unavailable required path makes the dependent claim unresolved, never cleared by default.

Eligibility and pool selection MUST be derived by the enforcement authority from authenticated identity and the exact policy. The sender's claimed scope/pool is not evidence. The authority MUST aggregate every carrier serving the same declared scope and apply any shared principal/capacity limits. Native policy syntax may vary, but its disclosed result MUST be verifiable under the selected profile.

## C3-03 — Request identity and bounded return path

Each request names its recipient, recipient scope, admission basis, stable `operation_id`, purpose and exact `subject_ref`. `submit_record` requests application of the referenced record; `finalize_candidate` asks the declared coordinator to finalize the exact referenced candidate under C4; `query_status` asks the selected authority for the status of the referenced accepted object. Optional C8 purposes operate on one exact `handoff_request`; they do not add transport methods. The subject and necessary exact evidence may accompany the request or be retrieved under the selected bounded retrieval profile.

The operation key is `(recipient_scope_id, authenticated issuer_agent_id, operation_id)`. Its immutable value is the request payload digest excluding top-level proofs. The recipient MUST pin that value durably on first admission. A duplicate key and value reuses the same operation. A different value at that key is a conflict, regardless of native A2A message/task ID. Re-signing the same unsigned request does not create new allowance; a changed native proof is still verified.

Sending a request opts into one bounded direct receipt on its authenticated return path, under the requester's own authority to request that interaction. It does not opt into unsolicited later marketing, another offer, or third-party disclosure. Payload and receipt size are bounded by the disclosed policy/transport limits. A sender lacking permission for this return path MUST NOT send the request. A receipt MUST NOT elicit a receipt-of-receipt. Deferred progress is retrieved by replaying the same operation under the recovery policy; no repeated new offer is necessary.

## C3-04 — Admission before model processing

The recipient MUST perform these gates before invoking an agent model or domain work:

1. Bound ingress size and parse one understood interaction profile. Reject duplicate JSON names and invalid canonical values.
2. Authenticate request/subject issuers, recipient, scope and required proof semantics. Apply native access controls before disclosing existence or private outcomes.
3. Check durable operation identity. For an exact replay, authenticate current authority to recover/disclose the saved outcome and return its current receipt. Do not reapply the original act's now-expired admission, withdrawn subject, or exhausted quota as new-action guards. A revoked read/recovery permission may withhold disclosure but MUST NOT change the stored disposition. Reject conflicting reuse without overwriting the original operation. An unauthenticated replay never receives a private saved result.
4. For a new operation, resolve the exact admission basis and required policy/status evidence using bounded retrieval. Verify sender eligibility, purpose, subject scope, current validity and reply permission.
5. Atomically reserve the applicable message/byte/work/in-flight allowance and persist a pending operation before dispatching work. Apply live-option and selection constraints separately where required.

Malformed or unauthorized ingress may be dropped or receive a bounded native error; producing a signed APP receipt is not an obligation to spend unbounded resources. Perimeter parsing/authentication abuse limits remain native responsibilities. The semantic quota cannot be evaded through these distinctions.

## C3-05 — Accounting and recovery

All new options, revisions and clarification operations consume their applicable allowance. Model/system retries for the same admitted operation MUST remain inside its reservation or obtain an explicit authorized increment. Duplicates do not consume the logical negotiation allowance again, though native ingress limits may still apply. A rejected operation has no semantic side effect; policy defines whether its incurred admission work consumes quota.

The selected accounting profile MUST define when reserved work is consumed, released or left in doubt, including crashes and cancellation. Releasing in-flight slots is separate from undoing a promise, adoption or capacity reservation. An uncertain semantic outcome MUST be recovered by operation key before reapplication. The harness MUST NOT apply a transition twice after a crash between recording its effect and responding. Atomicity may use a transactional store or a recoverable native mechanism; the protocol selects no database.

Retention MUST outlast the period in which the operation could be retried or its effect relied on. A policy with no finite validity bound needs durable identity/tombstone retention or an explicit authenticated epoch retirement rule that rejects old requests. Eviction from a cache cannot make an old ID fresh. Epoch retirement is not negotiation expiry and cannot erase an accepted record.

## C3-06 — Receipts and errors

A receipt is issued by the addressed recipient or its explicitly delegated authority. It binds the original request, operation key, monotonic receipt revision, previous receipt digest, outcome, reason and exact result/evidence references. It reports processing, not another agent's consent.

| Outcome | Required meaning | Retry effect |
|---|---|---|
| `pending` | Operation admitted or being recovered; no completed semantic effect is asserted | Same key retrieves progress; it does not reserve a second allowance |
| `applied` | Identified recipient-side transition or status read completed; `result_refs` identify the exact retained result | Terminal; replay retrieves it |
| `declined` | Recipient made an authorized, scoped choice not to apply the request | Terminal for this operation; promises/options are otherwise unchanged |
| `blocked` | A prerequisite was absent, unavailable, unsupported or exhausted; no semantic transition applied | Terminal for this attempt; a new operation requires the impediment resolved and fresh admission |
| `conflict` | Identity, lineage, capacity or existing formation conflicts with the request | Terminal; resolve the conflict explicitly |

A receipt may advance from `pending` to a terminal outcome; terminal outcomes do not turn back into pending or another terminal outcome. A new authoritative record correcting a discovered error preserves the original evidence and marks affected reliance unresolved; it is not a rewritten receipt. The receipt chain is keyed by the operation key and its pinned unsigned request digest. Conflicting reuse of an operation key MUST NOT replace its original saved outcome. An `operation_conflict` response binds the conflicting request in a separate terminal chain with `revision = 1` and `previous_receipt_digest = null`; it never appends to the original chain. Repeated identical conflicts retrieve that same response where retained under the recovery/ingress policy.

`applied` to an offer means the recipient recorded that offer under its semantics. It does not mean terms adoption. `applied` to an adoption means it was recorded; it does not mean finalization. Only the properly authored resulting semantic record can establish the associated act. `pending` without such a record cannot be treated as successful formation.

`finalize_candidate` is admitted only from a participant or an explicitly authorized representative to the candidate's coordinator. A pending receipt preserves an in-doubt formation; applied MUST return the exact accepted object in `result_refs`. The formation key in C4 additionally prevents new operation IDs from producing a second accepted object for the same candidate. A coordinator may trigger the same guarded operation locally without sending itself an A2A message; it MUST retain the same recoverable candidate outcome. A peer can use an admitted `finalize_candidate` invocation for that candidate to recover that outcome even when it never received the accepted-object reference. No new adoptions are invented by this request.

Reasons are typed: `ok`, `in_progress`, `permission_absent`, `unsupported_semantics`, `invalid_record`, `identity_mismatch`, `authority_absent`, `quota_exhausted`, `evidence_unavailable`, `evidence_stale`, `lineage_conflict`, `selection_conflict`, `operation_conflict`, `already_finalized`, `recipient_declined`, `contact_closed` or `internal_unresolved`. Human-readable detail is optional and cannot broaden the effect. Sensitive reasons/results may be withheld under access policy; opacity is not consent.

## C3-07 — Options, revisions and clarification

An option key is `(negotiation_id, issuer_agent_id, option_id)`. Publication and intent lineage keys use `(issuer_agent_id, contract_id)` and `(issuer_agent_id, intent_id)`. Revision 1 has no predecessor; revision n advances exactly n−1 and names that record's full digest. The issuer cannot branch a lineage silently. Replays do not add options; divergent successors are conflicts until explicitly resolved.

Revising one option replaces that option's unselected head, not another option and not bytes pinned by an adoption. A candidate MUST name exact revisions. Selected options must satisfy their shared capacity/exclusivity rules; a new option ID never creates capacity. C4 governs pins and the serialization of revisions/withdrawal against formation.

A `clarification` is a question or answer about an exact subject in the negotiation. It creates no new performance promise, permission or adoption. A material term change needs a new offer revision or candidate, not an interpretation of free text as amended agreed terms. Natural-language assistance may propose a next typed operation but MUST NOT apply it without the same guards.

## C3-08 — Closing, withdrawal and validity

`negotiation_close` expresses its author's decision to stop further discretionary negotiation contact in that identified negotiation. It cannot close another agent's internal state, withdraw any existing promise/adoption, refuse an accepted object or block protected control traffic. Further negotiation needs attributable renewed permission under policy. The issuer's still-live offer options continue to occupy their declared capacity until separately disposed of.

A `withdrawal_event` targets one exact publication, intent, promise, offer, admission grant, candidate or adoption. Only the issuer or an explicitly authorized representative may withdraw it. The applicable policy determines when the withdrawal takes effect; authoring or transmitting it does not prove ordering at another authority. C4 orders adoption/option withdrawal against finalization; C5 governs refusal of already accepted terms. Withdrawal of a prior revision does not automatically withdraw its successor.

Validity MUST follow the declared policy: deadline, until withdrawn or another understood rule. Budget exhaustion, lack of response, closed transport, task cancellation and elapsed local time do not invent a semantic outcome. Replenishment is absent by default; when allowed it is explicit, finite per applicable rule and authorized. Neither automatic retries nor new operation IDs renew permission.
