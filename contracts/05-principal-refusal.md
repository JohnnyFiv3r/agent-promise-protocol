# C5 — Principal notice, refusal and accepted-offer status

**APP 0.4-draft · normative interface contract**

This contract governs interpretation of the immutable `accepted_offer` produced by [C4](04-formation.md). It uses [publication/policy](01-publication-policy.md), [qualified authority](02-qualified-actions.md) and [portable A2A evidence](06-a2a-evidence.md). The [core contract](../contract.md) and [record schemas](../schemas/contract.schema.json) define the common vocabulary.

The accepted object records agent agreement. A separate current status establishes whether its adopted principal-refusal rules have been satisfied. Neither the object nor this status authorizes a downstream action or creates a human signature.

The selected refusal/status authority is scoped to the accepted object and its adopted policies; it need not be an APP-wide service or the custodian of every participant's journal. Independent ingress, hosting or replicas MUST preserve the profile's logical admission order and recovery guarantees. A participant's local copy, missing reply or elapsed local timer MUST NOT replace authenticated current authority evidence. A hosted assistant or connector MUST preserve the required principal notice/refusal and outcome-recovery paths across chat-session termination; ordinary negotiation authority cannot waive them. See the [deployment model](../deployment-model.md).

## C5.1 Adopted rights and authorized actors

The candidate MUST specify exactly one refusal-window descriptor for each distinct authenticated principal represented by its two agents. Identity is determined by the selected trust mechanism, not by counting distinct JSON objects. If both agents represent the same principal, that principal has one effective descriptor. Conflicting applicable delegations or refusal rules MUST be resolved through the principal's authorized policy mechanism before adoption; an agent cannot select whichever rule is shorter.

Each descriptor MUST bind a positive policy-defined duration, the principal's policy, designated notice channel/rule, refusal authority and usable refusal mechanism. The candidate also MUST select the authenticated clock/order, status authority and evidence-freshness policy. Both agents adopt these fields before finalization. They MUST be preserved in the accepted object.

| Actor | Permitted act | Required authority boundary |
|---|---|---|
| Principal | Exercise its own refusal right for the exact accepted object | Authenticate that principal under the adopted mechanism |
| Explicit representative | Submit that principal's refusal | Prove current authority specifically covering exercise of that principal's refusal right |
| Notice mechanism | Attest delivery/availability satisfying the principal's notice rule | Authenticate the designated channel and the evidence required by that rule |
| Status/refusal authority | Admit and order refusal events; derive and publish current status | Stay within the authority and clock/order scope adopted for that object |
| Negotiating agent or relay | Carry records and perform any separately delegated role | Its ordinary offer/adoption signature is neither principal notice, principal refusal nor waiver |

Agents MUST NOT shorten or erase an adopted refusal right through finalization, a status update, a policy-reference substitution or ordinary agent assent. A later policy revision cannot retroactively change the adopted duration or invent notice. Its effects on current authority and future reliance are evaluated under the applicable policies and preserved separately from historical agreement.

## C5.2 Qualifying finalization notice

A qualifying notice MUST identify and make available to the principal:

1. The exact accepted-object digest and retrievable, digest-verifiable adopted terms.
2. The applicable positive review duration, its adopted time/notice rule, and the derived deadline when it can be established.
3. A usable authenticated refusal mechanism for that accepted object, including any required principal or representative authentication.

The notice evidence MUST establish delivery or availability at the principal-designated channel under the adopted rule. A queue entry, an attempted send, or the negotiating agent's unsupported `notified` flag is insufficient. Where policy requires acknowledgment as well as delivery, both facts MUST be established before the notice qualifies. This is acknowledgment required by that policy, not an inferred human signature.

The verifier MUST authenticate the notice issuer's role, principal/channel, accepted and candidate references, duration, refusal mechanism and required delivery evidence. A notice for different terms, a different principal, inaccessible required content or an unusable refusal action cannot start this object's window.

For each principal, select the first notice event that satisfies the adopted notice rule in its authoritative ordering. Preserve that selection and its evidence. Retransmission, a later duplicate, another carrier or a later status query MUST NOT reset or shorten an established window. If an earlier alleged notice never satisfied the rule, it remains part of the evidence history; the first later qualifying notice may establish the previously unstarted window. A contested earlier notice requires reconciliation, not an arbitrary choice of the shorter deadline.

## C5.3 Time derivation and unavailable evidence

The default adopted derivation is:

`starts_at = max(finalized_at, verified_notice_time)`

`deadline = starts_at + adopted_duration`

The profile MUST make these times comparable under its clock, precision and permitted-skew rules. If evidence cannot establish the required ordering or minimum positive duration, the authority MUST NOT claim the window has closed. Any different derivation must be explicit in the policy adopted before finalization and must preserve the required minimum relationship to finalization and qualifying notice.

No notice means no derived start or deadline for that principal. It is forbidden to invent a deadline from record creation, delivery attempts, a local timer or the other principal's notice. The absence of a qualifying notice can remain pending indefinitely; it does not force refusal, acceptance or expiry.

The notice/refusal policy MUST define how loss of required term access, an unavailable refusal endpoint or unresolved clock/ordering faults affect an open window. An implementation MUST NOT use such an outage to infer successful closure. If the adopted policy does not establish a usable outcome or required evidence is missing, reliance remains pending or unresolved. No automatic extension, re-notification or changed terms may be invented outside that policy.

## C5.4 Refusal operation and authoritative admission

A refusal MUST name the exact accepted offer, refusing principal, attributable author and authority evidence. A representative's authority MUST cover the principal-refusal act; general authority to negotiate or adopt is insufficient. Refusal evidence MUST preserve the stable logical operation identity, content identity and authoritative admission/order evidence under C6. Reusing an operation identity with changed content is a conflict.

A principal may refuse after finalization even while its notice/window remains unstarted. Missing notice cannot extinguish the refusal right. Before an accepted object exists, disagreement is handled by C4's formation/withdrawal operations, not by pretending that a nonexistent accepted offer has been refused.

The selected mechanism MUST define one authoritative admission boundary and clock source. All of its admitted refusal paths serving the object MUST feed the same recoverable order. It MUST establish identity, authority, target and policy eligibility for a refusal to count. The authoritative evidence must distinguish receipt, pending verification, valid admission and rejection; a transport acknowledgment is not automatically a valid refusal receipt.

Timeliness is determined by that declared admission event, not an untrusted sender timestamp. The profile MUST define treatment of verification queues and alternate permitted admission paths. Closure MUST wait for reconciliation of any relevant pending event whose declared admission order could precede the closure boundary. A service cannot report a complete closure while an in-doubt admitted event may still be a timely refusal.

A valid refusal admitted at or before the applicable deadline prevails. Equality is timely. Window closure MUST be strictly after the deadline in the agreed clock/order and must follow resolution of relevant admitted events. A submission received after the deadline cannot be backdated by the sender; evidence of an earlier authoritative admission, including a duplicate retried later, retains its original timeliness.

Proposal quotas MUST NOT disable the principal's declared refusal path. The refusal path has its own bounded admission and recovery policy. Repeated valid retries return the original logical outcome without consuming a new refusal or erasing the earlier one. An unknown reply means the caller must recover that operation's authoritative result; it is not proof of refusal or successful closure.

On the first valid timely refusal by any required principal, the status authority MUST durably record the refusal effect and make the object `refused` for reliance. A later withdrawal of that refusal, deletion request, ordinary adoption, stronger proof, or fresh notice MUST NOT revive this accepted object. Any renewed agreement requires C4's linked replacement and fresh adoptions.

An action outside the adopted refusal period may have consequences under other applicable policies, but MUST NOT be misreported as a timely refusal under this window. This contract does not infer or execute downstream reversal.

## C5.5 Current status and permitted transitions

The status authority MUST publish attributable `status_snapshot` records with a monotonic revision and immutable history, binding the exact accepted object, observation time, clock/freshness evidence, selected notice/refusal evidence and one observation per distinct principal. It MUST also preserve the required current policy/authority evidence. An identical status revision with conflicting content is a fork; the conflict MUST NOT be resolved by a client's wall clock or by selecting the favorable branch.

| Current fact/state | Permitted next state | Guard |
|---|---|---|
| Newly finalized object | `pending_refusal_windows` | C4 finalization is valid; no clearance is inferred |
| `pending_refusal_windows` | Same state | At least one required notice or window remains pending, with no valid refusal |
| `pending_refusal_windows` | `unresolved` | Required proof, authority, notice, timing or ordering cannot be established |
| `pending_refusal_windows` or `unresolved` | `refused` | A valid refusal with applicable authoritative order has been established |
| `pending_refusal_windows` or `unresolved` | `refusal_windows_closed` | Every required principal window is established and strictly past its deadline; relevant events are reconciled; no timely refusal exists; required current evidence is valid |
| `unresolved` | `pending_refusal_windows` | Reconciliation proves that some notice/window is still pending, without a refusal |
| `refusal_windows_closed` | Same state in a fresh snapshot | Closure facts and required current evidence continue to verify |
| `refusal_windows_closed` | `unresolved` | A relevant newer conflict or required-policy/authority uncertainty invalidates current reliance on the closure claim |
| `refusal_windows_closed` | `refused` | Reconciliation establishes a valid timely refusal omitted from or contradicting the earlier closure claim; retain that earlier claim as faulty history |
| `refused` | `refused` only | Refusal is absorbing for this accepted object |

`unresolved` is an evidence/ordering condition, not permission to erase a known authenticated refusal. A consumer that already has valid refusal evidence MUST continue to reject reliance on that object even if the status endpoint later fails. Similarly, a stale cached closure cannot override a newer known conflict. A consumer's observation that a status proof is unavailable does not itself manufacture a new authoritative snapshot.

Closing one principal's window does not close another's. A shared principal has one effective window, not two independent chances to shorten the same right. The status arrays MUST cover exactly the distinct principals in the accepted candidate; object-level JSON uniqueness is not sufficient.

The authority MUST retain the event order needed to substantiate its claim. No guessed absence of refusal from an incomplete replica, unprocessed inbox or missing status response supports `refusal_windows_closed`. Under a declared distributed mechanism, recovery must establish equivalent complete authoritative evidence for the relevant boundary.

## C5.6 Reliance procedure

Before treating the object as having cleared principal refusal, a consumer MUST:

1. Verify immutable accepted/candidate/adoption proofs and exact references under C4 and C6.
2. Resolve the adopted status authority and verify sufficiently fresh authenticated status under the agreed policy, including known newer revisions or conflicts.
3. Verify coverage of every distinct principal, each qualifying notice and derived window, authoritative closure ordering, and the required current policy/authority facts.
4. Establish `refusal_windows_closed` with no applicable valid refusal or unresolved conflict.

Any failed or unknown check prevents a positive clearance conclusion. `pending_refusal_windows` and `unresolved` remain nonclearance states. A `refused` object is ineligible for that reliance permanently. Elapsed local time, an agent's offer/adoption, native A2A task completion and the absence of a human reply cannot replace this procedure.

Even a verified `refusal_windows_closed` status means only that the adopted refusal process has cleared under earlier principal delegation. It is not a human signature, a guarantee of future performance or permission for a downstream execution/payment action.

## C5.7 Duplicates, failures and durable history

Notice, refusal and status operations use C6's logical operation/content rules and MUST preserve their outcome across restart and carrier changes. Duplicates cannot reset notice, create an extra refusal, spend another logical allowance or reopen a closed/refused object. Conflicting identity/content MUST remain visible for reconciliation.

At minimum, distinguish invalid principal/representative authority, wrong accepted-object target, invalid or incomplete notice, unresolved clock/order, duplicate/refusal conflict, late refusal, stale/forked status and missing evidence. A rejection of one malformed message is not a determination that the principal waived its right; the valid declared refusal path remains available under its policy.

Refusal evidence and replay/status history MUST remain available for the accepted object's applicable reliance and recovery lifetime. Local cache expiry cannot make a refused object appear eligible again. Archival or delegated storage is allowed only when verifiers can recover the same immutable and current facts under the privacy policy.

This contract establishes accepted-object clearance for [C7](07-composition.md) and [C8](08-adapter-boundary.md). Those contracts preserve the protected right through dependency checks and dispatch. Refusal is not cancellation of an external transaction. The [proposed tests](../tests/PROPOSED.md) examine the boundary using substituted adapters.
