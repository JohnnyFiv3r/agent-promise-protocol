# Trust and failure model

**APP 0.4-draft · specification companion · implementation evidence reported separately**

This document bounds the claims made by the [governing contracts](../contracts/README.md), including [composition](../contracts/07-composition.md) and the [adapter boundary](../contracts/08-adapter-boundary.md). It distinguishes requirements a conforming participant can enforce itself, violations attributable evidence can expose, and guarantees that require a designated authority or external system. It does not add a reputation service, universal dispute process, payment rail or mandatory coordination topology.

The lifecycle expansion described in the [reconciliation note](lifecycle-reconciliation.md) preserves three separate facts: agent agreement, principal clearance and authorization for a particular downstream action. Composition and evidence records do not merge those facts. [Proposed checks](../tests/PROPOSED.md) describe the full assessment scope; the [validation record](../validation.md) and [conformance map](../conformance.md) identify the reference runtime's actual coverage and remaining gaps. Implementation tests do not discharge every trust dependency below.

## Actors and trust boundaries

An agent acts within authority delegated by its principal. Another agent, a discovery service or a transaction orchestrator may relay that agent's records, but cannot acquire its authority through possession of those records. Transport authentication identifies a connection under its selected mechanism; semantic proof authenticates a particular statement. Neither alone establishes that the issuer had authority to make the statement's asserted commitment.

Each bilateral agreement retains its own originator/coordinator and exact candidate. A transaction orchestrator coordinates a larger grouping under its own authority. Its role does not replace an agreement coordinator, create a component adoption, reserve another participant's capacity or authorize cancellation of unrelated agreements.

An authority is trusted only for its declared scope. A principal-policy authority establishes delegated permission; a capacity authority establishes the resource facts it controls; a notice mechanism supplies the adopted notice evidence; a refusal/status authority orders the events used to determine principal clearance. An evidence reporter or assessor establishes only the claim assigned to its role and semantics. An adapter binds a separately authorized external operation to APP references; the native system defines its own execution and result semantics.

## Classification of guarantees

The categories below overlap. For example, a verifier can locally check an authority's signature, while the completeness and honesty of that authority's underlying event history remain assumptions.

| Property | Locally enforceable requirement | What remains detectable or dependent |
|---|---|---|
| Exact authorship and content | Verify the selected proof, issuer, scope, canonical digest and exact references; reject unsupported required semantics | Key custody, identity binding and delegation roots depend on the selected trust mechanism. A valid signature does not establish truthful content. |
| Own promises and adoption | Reject promises attributed to an unissuing actor; require exact provenance or issuance through that actor's adoption | An actor can still lie about its qualifications or promise incompatible work outside the observed scope. |
| Bounded admission | Enforce authenticated eligibility and finite pools before model/domain work; preserve operation identities across carriers | Shared limits depend on all covered ingress paths reaching the declared accounting authority. Network availability and resistance to every identity attack are not guaranteed. |
| Durable formation | Preserve exact candidate/adoption bindings, replay protection and one formation result within the declared ordering scope | Cross-authority capacity protection and recovery depend on the selected mechanism. Local records cannot prove that an unrelated system has not consumed the same resource. |
| Principal recovery | Require positive adopted periods, qualifying notice, usable refusal, authoritative ordering and fresh clearance evidence; withhold dependent irreversible handoff | Notice availability, clock/order integrity and completeness of refusal admission depend on the designated mechanisms. A signature cannot prove a principal actually read the terms. |
| Composition eligibility | Evaluate the adopted dependency rules against exact component references and required evidence; preserve each component's rights | A grouping provides neither global assent nor atomic execution. Progress depends on component authorities and the declared dependency structure. |
| Downstream handoff | Check the exact action, applicable clearance/dependencies and current native authority; preserve dispatch identity and unknown outcomes | Actual execution, duplicate suppression and recoverable native outcome depend on the selected adapter/native contract. APP records alone cannot impose those properties on a service. |
| Fulfillment, assessment and settlement evidence | Authenticate the reporter, claim type, subject, native correlation, observation and required verification/finality rules | Delivery quality, an assessor's correctness, native settlement finality and reversibility remain claims under their particular semantics and trusted sources. |
| Privacy | Enforce permitted disclosure and retrieval in the conforming participant's own paths | An authorized recipient can copy material outside those paths. Withdrawal of future permission cannot erase information already disclosed. |

## Evidence exposes some violations, not all violations

Two authenticated records can demonstrate an attributable contradiction: different required content at one immutable identity, divergent successors in one lineage, incompatible receipt/status histories, or a reporter asserting mutually exclusive facts under the same semantics. The dependent claim stays unresolved under its governing rules; the verifier does not select the more favorable branch by timestamp or arrival order.

Detectability requires access to the relevant evidence. A verifier with one apparently valid branch cannot conclude that no other branch exists. Similarly, silence, an empty search result or an incomplete inbox does not prove absence of an adoption, refusal, dispatch or external effect. An authenticated completeness assertion has only the scope and assurance supplied by its designated authority.

Proof of authorship is distinct from proof of competence, capacity, fulfillment or continuing authority. A provider's fulfillment report remains a provider report unless the adopted assessment semantics require and supply other evidence. An assessor's judgment is not another principal's assent. A native submission acknowledgment is not settlement. An orchestrator's summary cannot erase contrary component evidence or broaden the underlying claim.

## Failure behavior

| Failure or uncertainty | Required safe interpretation |
|---|---|
| Unsupported action, policy, proof or native-result semantics | Block the dependent automated act. Preserve permitted evidence without substituting a guessed meaning. |
| Missing, stale or unavailable required status | Do not assert current permission, clearance or dependency satisfaction. Preserve established historical facts and recover through the selected authority. |
| Known newer revocation or refusal | Do not prefer an older active/closed snapshot. A valid refusal remains absorbing for that accepted object even if its endpoint later becomes unavailable. |
| Clock uncertainty or incomplete refusal ordering | Do not assert a deadline boundary or completed clearance that the evidence cannot establish. A timely refusal at the adopted deadline remains timely. |
| Lost response or crash after an admitted operation | Recover its stable identity and durable disposition. Do not infer failure, mint a replacement operation or release protected capacity solely because a response is absent. |
| Expired or withdrawn original admission basis on replay | Apply current recovery/disclosure authorization to the saved outcome. Do not reapply the original act or treat its expired action permission as proof that it never occurred. |
| Conflicting capacity or an in-doubt reservation | Prevent conflicting reuse until the selected authority establishes disposition. A local timer alone cannot prove no earlier commitment occurred. |
| Failed or refused component agreement | Apply only the dependencies and authorized dispositions adopted by affected parties. Do not manufacture transaction-wide cancellation, release or replacement authority. |
| Unknown native dispatch outcome | Preserve the original external-operation correlation and use the adapter's reconciliation contract. A second independent dispatch cannot be justified by missing acknowledgment. |
| Contradictory fulfillment, assessment or native-result evidence | Retain the conflicting claims and their provenance; apply the selected interpretation rules. Do not flatten them into a universal success or failure. |
| Required notice, refusal or recovery path unavailable | Do not infer waiver or clearance. Protected control admission remains separate from exhausted negotiation allowance; availability itself still depends on the serving mechanisms. |

Recovery must not erase evidence of a prior effect. In particular, discovering a timely refusal after an erroneous clearance claim invalidates future reliance under the adopted rules; it does not physically undo an already dispatched native action. Any cancellation, release, reversal or compensation is a separate authorized operation with its own outcome evidence.

## Making principal protection effective

The default handoff rule withholds irreversible performance and settlement while a relevant principal period remains uncleared or a required dependency or action-authority check is unresolved. A transaction cannot claim compliant principal protection merely because its terms contain a refund or cancellation field.

`prepare_handoff` is side-effect-free preparation; its `prepared` result is not permission to dispatch. Native reservation, cost, disclosure or other external effects cannot be hidden inside preparation. Each is a separately governed action. The [reference profile](../profiles/reference-profile.md) admits no early-effect exception: every native effect waits for its relevant principal clearance and current action authority. A broader future profile would need an explicit account of what recovery protection an earlier-effect mechanism actually preserves and how that fact is established. Financial reimbursement does not retract disclosed information.

Protection is attached to the exact agreement and each distinct represented principal. A common principal appearing in several component agreements does not silently collapse their different terms, notices or periods into one transaction-wide waiver. A common notice mechanism can serve several agreements only to the extent that each agreement's exact notice and refusal requirements are independently satisfied.

## What a complete profile must make assessable

The [selected reference profile](../profiles/reference-profile.md) supplies concrete mechanisms for the claims above. It must make the following boundaries inspectable without changing the universal action model:

- Which identities, trust roots, delegation claims and revocation/freshness rules authorize each role.
- Which existing proof and retrieval mechanisms bind exact records and preserve native evidence.
- Which authority supplies each event order, time source, admissible uncertainty and completeness claim.
- Which resource/accounting scope is shared across negotiations, agents and carriers, and how recovery preserves its outcome.
- Which dependency and evidence semantics are understood; who may assess them; what false, unknown, disputed and final mean.
- Which adapter boundary can admit an action, correlate it to a native operation and reconcile an uncertain result without creating a duplicate effect.
- Which adopted action-occurrence rule fixes the dispatch identity and any permitted cardinality. A caller cannot create another occurrence of the same obligation merely by inventing a new identifier.
- Which retention and access guarantees allow authorized participants to recover the same relevant evidence.

Selecting these mechanisms is a design commitment, not evidence that an implementation interoperates. Cryptographic checks, authority checks, state-transition checks and live external integration are distinct claims and must be reported separately.

## Explicit limits

APP does not guarantee honest participants, universal capacity knowledge, eventual agreement, uninterrupted service, truthful providers, accurate assessors, universally reversible effects or settlement finality independent of the native system. It does not infer human approval from an elapsed period, claim all-or-nothing composition merely because an orchestrator exists, or impose a general dispute court.

The contracts require conforming participants to refuse unsupported conclusions, preserve attributable evidence and keep unknown outcomes unresolved. `dispatch_handoff` records its durable boundary before an attempt; `reconcile_handoff` retrieves the original outcome and never initiates the action. These requirements govern adapter calls and evidence interpretation. Actual native effects remain externally reported facts, not effects independently proven by the APP state machine, and live interoperability remains separate work.
