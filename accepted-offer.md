# Accepted-offer object and principal refusal

**Draft 0.2.** The output is an immutable record of exact agent agreement, accompanied by authenticated current status. Agent agreement is subject to the agreed post-handshake right of principal refusal. These semantics distinguish delegated agent negotiation from an exchange in which the humans themselves have just assented.

## Formation inputs

A candidate identifies:

- The initiating intent/promise/offer, its immutable content and author. That author is the declared coordinator.
- The parties and principals, exact selected offer options/revisions, own qualified promises and complete terms.
- The offering/action semantics and commercial arrangement, including the relevant policy references and eligibility evidence.
- Selection/capacity constraints, privacy rules and any linked replacement/disposition of prior commitments.
- Each principal's refusal-policy reference, positive duration, notice destination/rule, refusal/status authority and clock/freshness policy.

Both agents adopt the same candidate content. Each adoption authenticates its author, authority and own selected promises. Offer issuance already issued conditional promises; adoption selects their exact reciprocal terms rather than issuing another party's requested behavior. Material differences require a new candidate and fresh adoptions.

An agent may accept directly without creating a reciprocal offer. Its own adoption can issue the qualified reciprocal actions requested of it, with its own capability/authority evidence. A candidate's description of those requested actions is not their issuance. The selected-options list can contain one or several compatible options; the agreement remains between two agents. Refusal windows cover distinct principals, so two agents acting for one principal need one applicable principal window rather than inventing a second principal.

## Finalization

The coordinator MUST verify both exact adoptions, selected current options, capability/authority qualifications, current policy eligibility and selection constraints. It serializes finalization with option withdrawal/revision and any competing use of the same declared capacity. It then emits `accepted_offer`, referencing the candidate and both adoptions and fixing `finalized_at`.

The coordinator is the author of the explicitly named initiating record, not necessarily the buyer. An intermediary relay does not become coordinator. Parties resolving crossed openings must explicitly select the same origin before adoption. There is no global earliest-message inference.

An initiating offer may use a self-origin marker without a self-referential digest. The candidate and accepted object then reference the complete signed offer by its ordinary content digest; they cannot claim self-origin themselves.

Finalization records the agent handshake. The initial accepted-object status is `pending_refusal_windows`. Finalization alone MUST NOT be represented as completed principal review, irrevocable human consent, execution permission or payment authority.

## Portable evidence

The accepted object preserves its origin, parties, exact candidate reference, option selection, adoptions and principal-window descriptors. Existing cryptographic mechanisms authenticate the content digest, issuer and proof scope. Referenced candidate and adoption bytes must remain retrievable and digest-verifiable under the privacy policy. Unresolvable references do not establish acceptance.

Proofs are independent of mutable status. A verifier may authenticate historical agreement while correctly concluding that it is currently refused or unresolved. Proof verification is not native AP2 validation; [the downstream note](downstream-boundary.md) describes that separation.

## Notice and start of the principal window

Each principal's policy designates a notification channel and refusal mechanism. A finalization notice MUST expose the exact accepted terms, applicable review duration/deadline and a usable refusal action. It must identify the relevant accepted-object digest.

Only authenticated delivery or availability at the designated principal-controlled channel satisfies the notice rule. A queued notification or the negotiating agent's unsupported `notified` flag is insufficient. Delivery does not claim that a human has read the notice. A policy may require acknowledgment in addition to delivery.

For each principal, the start is no earlier than both `finalized_at` and the verified notice event satisfying that principal's rule. The default derivation is `start = max(finalized_at, verified_notice_time)` and `deadline = start + adopted_duration`. The agreed duration must be positive. No universal number is imposed. The actual event/derived times appear in subsequent evidence and status; they do not mutate the accepted object or introduce new terms.

Missing notice evidence leaves that principal's window unstarted and the object pending or unresolved. It cannot clear by waiting out an invented deadline. For several principals, all applicable windows must be resolved before status can report them closed without refusal.

## Refusal and ordering

A principal, or an explicitly authorized representative exercising that principal's right, may issue an authenticated refusal directed at this exact accepted object. An agent or relay cannot reject another principal's refusal because its own negotiation quota is exhausted. The selected refusal/status mechanism must provide a reachable, bounded means of recording it.

The declared authority uses its authenticated clock and durable ordering. A valid refusal admitted at or before the deadline prevails. Window closure is recorded only after the deadline and after resolving admitted/refused/duplicate event order. A retry preserves operation identity; it cannot create a second refusal or erase one. A network timestamp supplied solely by an untrusted sender cannot establish timely admission.

A timely refusal makes the accepted object `refused` for downstream reliance. The historical adoptions and finalization remain intact. Removing or retracting the refusal cannot revive that object; renewed agreement requires a linked replacement and fresh adoptions. Bazaar performs no refund, reversal or cancellation of an external native transaction.

## Current status

| State | Meaning |
|---|---|
| `pending_refusal_windows` | Agent terms are finalized, but at least one required notice/window is pending. |
| `refused` | A valid principal refusal prevents reliance on this accepted object. |
| `refusal_windows_closed` | Authoritative evidence shows all required windows closed with no timely refusal. This is not a payment/execution authorization. |
| `unresolved` | Required notice, ordering, policy or status evidence is unavailable or conflicting. |

A status snapshot binds the accepted-object digest, monotonic revision, authenticated authority, exact notice/refusal evidence, derived window times, observation time and policy-defined freshness. Closing the windows is an explicit verified state observation, not a client guessing from its clock. A stale prior closure cannot override a newer known refusal or unresolved conflict.

The window expiring does not create a human signature. The underlying basis remains the principal's earlier delegation, which authorized agent action subject to this right of refusal. Any later withdrawal beyond the adopted window follows the referenced policies and native downstream rules; it does not rewrite historical consent or automatically undo external effects.

## Consumers and immutable replacement

A consumer MUST distinguish the immutable handshake proof from current review status. It cannot rely on the object as having cleared principal refusal without sufficiently fresh authenticated status proving that result. It must separately satisfy its own execution, commerce or payment authority requirements.

A replacement identifies the prior accepted object and how prior unperformed commitments are superseded or otherwise disposed of. New terms receive fresh agent adoptions and principal windows. The replacement does not silently combine an old price, a new scope and an expired permission, nor erase any existing downstream effect. Implementations retain all relevant historical records.

Bazaar ends at this accepted object and the evidence needed to interpret it. It defines no payment, fulfillment or assessment state machine.
