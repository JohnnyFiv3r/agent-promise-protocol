# C4 — Exact adoption and originator-coordinated formation

**ABP 0.4-draft · normative interface contract**

This contract governs candidate creation, each agent's adoption and one durable accepted-offer result. It implements the controlling decisions in the [core contract](../contract.md); [record schemas](../schemas/contract.schema.json) define the structural fields. It uses [publication/policy](01-publication-policy.md), [qualified actions](02-qualified-actions.md), [admission/negotiation](03-admission-negotiation.md) and [portable A2A evidence](06-a2a-evidence.md). Principal refusal after finalization is governed by [C5](05-principal-refusal.md).

Local lifecycle terms below describe facts an implementation must preserve. They do not define a new transport, require a shared database, or impose a negotiation deadline.

## C4.1 Actors and authority

| Actor | Authorized formation act | Limit |
|---|---|---|
| Candidate author | Assemble an immutable candidate for review under the negotiation's policy | Its signature does not issue another agent's promises or record that agent's adoption |
| Each participating agent | Issue its own `terms_adoption`, or withdraw its own adoption before effective finalization under the agreed ordering rule | It must authenticate the exact candidate and act within current delegated authority |
| Declared originator/coordinator | Validate adoptions and finalization evidence; serialize the formation outcome | It cannot manufacture an adoption or overrule a selection authority |
| Owner-designated selection authority | Admit, reserve, commit or release the capacity/selection facts it controls | Its authority covers its declared resources and ordering scope, not every negotiation in the network |

The candidate MUST identify exactly two distinct participating agents and their authenticated principal bindings. Those agents MAY act for one shared principal. An agent identifier in a body is not an identity or delegation proof.

The origin is the explicitly selected initiating `intent`, `promise` or `offer`. Its authenticated author MUST be the declared coordinator and a participant in this formation. A relay, the buyer role, and an earlier unauthenticated timestamp cannot replace that author. Crossed openings MUST select the same origin before either agent adopts a shared candidate. A conflicting origin is a different proposed formation, not a correction inferred by the receiver.

Only an initiating offer may use the self-origin marker specified in core contract section 7. Every candidate and adoption MUST resolve an ordinary immutable reference to that complete initiating record. A self-origin marker in a candidate, adoption or accepted offer MUST be rejected.

## C4.2 Candidate identity and complete terms

A candidate MUST bind:

1. Its stable record identity, selected origin, negotiation and participating agents/principals.
2. One or more complete selected option revisions and their selection constraints. It MUST NOT silently combine a price, qualification or action from different revisions.
3. The exact qualified action descriptions, their `promise_bindings`, and all material agreement, privacy and policy terms.
4. Applicable current-policy and qualification requirements and the mechanism for establishing selection eligibility.
5. One positive refusal-window descriptor per distinct principal, plus the notice, refusal, clock, freshness and status-authority policies required by C5.
6. The exact `handoff_rules` policy and protection mode; the default `no_effects` rule needs no enabled adapter.
7. Any optional C7 plan/slot and its required features, requirements and dependencies. A bilateral candidate omits composition.
8. Any linked prior accepted offer and the authorized disposition of its outstanding commitments.

A candidate is immutable after issuance. Its `body.candidate_id` MUST equal its envelope `id`; they are two representations of the same identity. A changed required field, promise qualification, policy pin or agreement condition requires a new candidate identity and fresh adoptions. A new candidate does not invalidate an earlier one merely because it was created later.

For each item in `own_promises`, the candidate MUST contain exactly one `promise_bindings` entry matching its `promise_id` and `promiser_agent_id`:

- `previously_issued` MUST resolve the exact action in an attributable selected offer or explicit promise. `source_promise_id` MUST identify that action in `source_ref`. Action parameters, qualifications, authority/capability references and validity MUST agree with that source; merely reusing its promise ID is insufficient.
- `issue_on_adoption` describes an action that only the named promiser may issue through its own adoption. An optional `request_source` MUST identify the actual request in the referenced offer. Neither the request nor the candidate author supplies the promiser's issuance.

There MUST be no unmatched binding, duplicate action identity with different content, or binding that attributes issuance to a different actor. An unknown required action or condition meaning prevents adoption. Conditions for future behavior MUST be interpreted under C2's phase rules; they MUST NOT be treated as already fulfilled merely because the candidate names them.

Direct acceptance requires no reciprocal offer. A candidate may select a single offered option. An agent may adopt with an empty `adopted_own_promise_ids` list when it assents without taking on a separate substantive performance action. Its adoption is still an authenticated, qualified act. When it does undertake actions, its adoption MUST identify every candidate action whose promiser is that agent; it cannot accept the complete candidate while silently omitting one of its own required actions.

## C4.3 Current eligibility and selection across negotiations

Before issuance/adoption and again at finalization where relevant, the participant MUST establish the policy-defined capability, capacity and commitment-authority facts for its own act. Evidence MUST cover the exact action, candidate, principal and applicable constraints. A signature, a capability description, or a stale policy document is not sufficient evidence by itself.

Every selected `selection_constraints_ref` MUST resolve an understood policy specifying at least:

- The owner-designated authority, affected resources/options, exclusivity or capacity units, and the scope across which conflicting selections are ordered.
- The point at which a selection becomes reserved or otherwise protected from a conflicting finalization.
- The required evidence, validity rules, conditional-commit behavior, release/disposition rules and recovery procedure.
- How pending withdrawal, stale status, authority failure, restart and an unknown finalization outcome affect eligibility.

No particular reservation service or algorithm is mandatory. A policy may select a reservation mechanism or another recoverable atomic admission mechanism. Its semantics MUST prevent two conforming finalizations from independently consuming the same exclusive or exhausted capacity. An unprotected check-then-act snapshot is insufficient where concurrent candidates can conflict.

The authority controlling a resource MUST enforce its declared scope across every related negotiation, origin coordinator and carrier. Two different coordinators cannot each treat a local lock as protection for the same provider capacity. Agents MUST preserve the relevant evidence in `selection_status_refs`; finalization MUST preserve its current selection/commit evidence in `finalization_check_refs`.

Adoption or finalization MAY remain pending while protection is established. The selected mechanism MUST explain how a participant can determine whether a held selection became an accepted commitment, remains pending, or was authoritatively released. A lost reply or elapsed local timer MUST NOT release an in-doubt reservation. Policy-defined expiry may make a record ineligible for a new transition; it does not prove that no earlier finalization occurred. Recovery must establish the authoritative outcome before conflicting reuse.

Finalizing one candidate does not automatically withdraw every other option. The applicable capacity/exclusivity predicates determine which other options remain eligible. Any resulting withdrawal or status change MUST be attributable and retained.

## C4.4 Adoption guards and effects

Before admitting a `terms_adoption` as usable formation evidence, a verifier MUST establish all of the following:

1. The original adopter and its principal match one candidate participant; the proof authenticates the required content and scope.
2. The exact candidate, its origin, required definitions and private references resolve. The adopter has adopted the complete candidate, including its refusal rules.
3. Each identified own action belongs to the adopter. New `issue_on_adoption` actions satisfy that adopter's issuance requirements. Previously issued actions resolve their source bindings.
4. The relevant publication, commitment authority, action qualifications, validity and transaction-policy predicates permit this adoption.
5. The selected option revisions and capacity evidence are eligible under the declared selection mechanism; no known withdrawal, supersession or conflicting selection has precedence.

The adoption's logical admission and its effect on the issuer's selected-option/capacity state MUST be atomic at the selected authority boundary. A returned admission result MUST distinguish transport receipt, semantic rejection, pending reconciliation and usable adoption evidence. Transport success alone does not satisfy these guards.

Both agents MUST adopt the same candidate content. An adoption for a different candidate cannot be combined because some individual fields happen to match. There is no partial or inferred adoption of required terms.

An admitted adoption remains subject to its declared validity, current required qualification and explicitly ordered withdrawal rules until formation resolves. There is no universal automatic adoption expiry or forced outcome on silence.

## C4.5 Revision and withdrawal ordering

The selected mechanism MUST serialize candidate retirement, terms-adoption withdrawal, relevant option revision/withdrawal and finalization within their declared ordering scopes. Each such event MUST identify its target and authenticated author. An actor may withdraw its own issued records; it cannot withdraw the other actor's adoption.

| Authoritatively ordered fact | Required result |
|---|---|
| A required option/adoption is withdrawn or made ineligible before finalization | That candidate MUST NOT finalize on the old evidence; retain the withdrawal and reconcile affected reservations |
| A candidate is retired by its authorized author before finalization | Later adoption delivery cannot revive that candidate; use a new candidate for renewed negotiation |
| Finalization precedes a withdrawal or option revision | Preserve the accepted bytes; process the later act according to its policy without rewriting or retroactively deleting acceptance |
| A candidate or adoption is expired under its explicit policy before the proposed finalization point | It is ineligible for new finalization; recover any possibly earlier outcome before releasing protected selections |
| The relative order or protected capacity outcome is unknown | Keep dependent formation and conflicting reuse blocked until reconciliation |

An issuer's local wish to revise a pinned option is not proof that a pending remote formation has closed. The mechanism MUST preserve a recoverable order between that revision and finalization. No participant may resolve this race using a sender-supplied timestamp alone.

Withdrawal of a publication, intent, promise, option, candidate and adoption are different target operations. One MUST NOT be silently substituted for another. Principal refusal of a finalized accepted object is governed by C5; it is not implemented by deleting an adoption.

## C4.6 Durable finalization boundary

The C3 `finalize_candidate` request names the exact candidate as `subject_ref` and is addressed to its declared coordinator. Only a participant or explicitly delegated representative may request this operation. A coordinator may trigger the equivalent guarded operation locally. An applied outcome MUST identify the exact accepted object; a pending outcome carries no acceptance claim. Replaying a request recovers its operation outcome. A separately admitted request for the same formation key MUST recover the existing accepted outcome if one exists, rather than creating another accepted identity, including when the caller previously lacked its reference. Existing-outcome disclosure uses current read/recovery authority; it does not revalidate expired formation inputs as though forming a new agreement.

The coordinator MUST perform or obtain an authoritative atomic decision covering:

1. Verification of both exact adoptions and all candidate/refusal descriptors.
2. Current required policy, commitment-authority and qualification checks under their agreed freshness rules.
3. Eligibility of the selected option revisions and the mechanism's protected capacity/selection evidence.
4. Absence of a preceding applicable retirement/withdrawal or already-finalized outcome for this formation identity.
5. Verified support for every effective required feature; when composed, the valid C7 binding and current formation-stage predicates.
6. Durable recording of the exact `accepted_offer`, its finalization time/evidence, both adoption references and the committed selection disposition.

These are one logical finalization boundary. If underlying authorities are separate, the selected profile MUST establish an equivalent recoverable decision; a coordinator cannot claim atomicity merely by issuing several requests in sequence. Unknown partial outcomes remain in doubt and cannot be reported as a new success or used to release conflicting capacity.

The formation key is `(coordinator_agent_id, authenticated candidate issuer_agent_id, candidate envelope id)`. The first admissible candidate binds that key to its unsigned content identity under C6. Reusing it with different required content is a conflict. Re-signing or attaching another proof to unchanged candidate content MUST NOT create a second formation. Exact reference/proof variants must be reconciled under C6 without changing the terms already adopted. A new transport or operation ID does not change this formation key.

The accepted record MUST preserve the candidate's principal-window descriptors and status/clock authorities exactly. Finalization may record its authoritative time; it MUST NOT introduce a shorter duration, weaker notice rule, substitute principal, or new waiver. Its initial status is `pending_refusal_windows`.

The coordinator MUST persist the outcome before returning finalization success. Duplicate finalization requests retrieve that existing outcome. After a lost response or restart, a participant MUST recover the same formation result; it cannot infer failure, create a replacement accepted identity for the same operation, or reuse protected selections solely because the response is missing.

## C4.7 Failure results and retention

Errors MUST identify the failed guard and the exact subject, without disclosing material outside the privacy policy. At minimum, implementations must distinguish invalid proof/actor, unresolved reference, candidate-content conflict, missing/mismatched adoption, unsupported semantics, current-policy/authority failure, option/capacity conflict, withdrawal/retirement precedence and unknown outcome. A pending or unknown result is not a refusal or acceptance by either party.

Receipts, candidate bindings, adoption/withdrawal order, selection evidence and finalized outcomes MUST survive process restart for as long as their associated records may validly be relied on or replayed. An `until_withdrawn` record cannot lose its replay protection because an unrelated local cache timer expired. Implementations may retain these facts through an authoritative external mechanism rather than one local store, provided recovery preserves the same outcomes.

Immutable replacement requires a new candidate, fresh adoptions and explicit authorized disposition of the prior commitments. Naming a prior object is not itself authority to cancel it or free its capacity. This contract establishes no downstream execution, payment, fulfillment or result-assessment authority.
