# C2 — Qualified actions, promises, and adoption

**Normative contract · ABP 0.3-draft**

This contract governs the meaning and authorship of an agent's promises. It implements the controlling [decisions](../decisions-v0.2.md) and refines the [promise model](../promise-model.md). Names such as `own_promise` and `promise_bindings` refer to the [record schema](../schemas/contract.schema.json). The [publication contract](01-publication-policy.md) governs permission and disclosure.

## Actors and exact action scope

### C2-01

A promise MUST be attributable to the agent performing the promised action and to the principal whose authority covers that agent. The authenticated issuer MUST equal `promiser_agent_id` when it issues the action. A relay, candidate author, coordinator, or counterparty MUST NOT issue that actor's promise merely by describing or carrying it.

### C2-02

Each promise MUST identify `promise_id`, `promiser_agent_id`, `promisee_ids`, action semantics, capability evidence, authority evidence, qualifications, and validity. Promisees identify the intended counterparties of the action. Their identities MUST NOT be inferred from transport roles, market roles, record viewers, or the disclosure audience.

### C2-03

Within a candidate, each `(promiser_agent_id, promise_id)` MUST identify exactly one complete action description and exactly one provenance binding. A bare `promise_id` MUST NOT select among different actors or revisions. A verifier MUST compare the exact referenced containing record and action content; matching labels alone never establish the same promise.

### C2-04

`action_type` and immutable `semantics_ref` MUST define the action's parameters, subjects, resources, effects, prerequisites, and interpretation. Each typed value and required qualification MUST resolve to understood versioned semantics. Unknown or ambiguous required meaning MUST prevent automated issuance or adoption, even when the JSON is structurally valid.

### C2-05

The common action structure MUST remain independent of product-specific vocabulary. Extensions MAY define action meanings and typed parameters, but MUST NOT alter self-authorship, require another actor's unissued promise, or erase a core condition. Free-form explanation MUST NOT silently widen typed scope or authority; conflicting required meanings MUST be resolved before issuance/adoption.

### C2-06

`provide` describes the promiser supplying the named behavior or subject; `receive` describes the promiser receiving, using, or accepting the named subject in the specific sense defined by that action. Polarity MUST NOT imply buyer/provider role, positive/negative value, commercial assent, or satisfaction with a result. “Receive proposals” MUST NOT mean “accept their terms.”

### C2-07

The action MUST identify its subjects, relevant resources, parameters, limits, and conditions sufficiently to distinguish the promised behavior from adjacent acts. An intent's `emission_promise` covers declaring or seeking the stated outcome. It MUST NOT be interpreted as a promise to supply, purchase, reserve, or successfully obtain that outcome.

## Qualification and authority guards

### C2-08

Before issuance, the promiser MUST have evidence meeting the applicable policy for both capability and current authority to make that conditional commitment. Capability and authority MUST be checked separately. Possessing a credential or permission does not establish ability; possessing an ability, tool, or endpoint does not establish permission.

### C2-09

Capability evidence MUST cover the action and material capacity under the stated conditions. A signature, schema-valid reference, advertising claim, or evidence about another action MUST NOT automatically establish competence or capacity. The principal/counterparty policies determine acceptable evidence strength; unresolved required qualification prevents the dependent automatic act.

### C2-10

Authority evidence MUST distinguish permission to issue/adopt a conditional promise from permission to perform its future action. Future performance MAY depend on a later authorization or other explicit prerequisite only when current policy permits making that conditional commitment. An agent's expectation of future delegation MUST NOT substitute for current commitment authority.

### C2-11

Every material qualification MUST have named semantics specifying its check stage, decision authority, evidence requirement, and effect when true, false, or unknown. A known condition whose truth is deferred until a future action MAY be adopted as a condition. Unknown present authority or unknown meaning of the condition MUST NOT be treated as a satisfied future prerequisite.

### C2-12

Participants MUST refresh capability, capacity, and authority evidence wherever material to issuance, adoption, or finalization under the applicable policy. A previously valid offer MUST NOT establish present qualification after known revocation or material change. Future action conditions remain conditions of the accepted terms; Bazaar defines no execution, delivery, or assessment state machine.

### C2-13

An agent MAY promise its own declared composite service or its own act of requesting another agent's work. It MUST NOT attribute an autonomous third party's action to that party without that party's authenticated issuance. A request to a subcontractor promises the request, not the subcontractor's response, unless the issuer expressly owns the promised composite result.

### C2-14

Competing promises that share capacity, exclusivity, or another limiting resource MUST disclose the applicable selection dependency. Independent option identifiers MUST NOT multiply capacity or conceal mutually exclusive commitments. Selection MUST satisfy those constraints without claiming that every alternative is simultaneously performable.

## Issuance, requests, and conditional offers

### C2-15

Authenticated issuance of a `promise` record issues its `own_promise`; issuance of an `intent` issues its scoped `emission_promise`; issuance of an `offer` issues its `own_promises`. Each containing record's proof MUST authenticate the exact action content, issuer, and intended scope. Offer promises MUST NOT be relabeled as unissued suggestions awaiting the counterparty's signature.

### C2-16

An offer's issued promises remain subject to their stated agreement, selection, principal-review, and other qualifications. Issuance MUST NOT imply that those future conditions already hold. An offer cannot bind the counterparty's conduct, and accepting it cannot broaden the issuer's promised action or remove its conditions without fresh issuance/adoption of changed terms.

### C2-17

`requested_counterpromises` MUST be interpreted as requests addressed to `requested_of_agent_id`, with their requested action, qualifications, and validity. The requesting issuer's proof authenticates the request only. It MUST NOT supply the recipient's capability evidence, authority, issuance, or assent; silence and receipt issue none of them.

### C2-18

An issued promise MAY exist without an agreement when it identifies the specific action, author, qualifications, and validity. Continuing policy permission MUST NOT be transformed into a standing promise. `until_withdrawn` preserves only the identified action under its policy; it MUST NOT create unspecified recurring service or an undertaking to accept future work.

## Candidate binding and direct adoption

### C2-19

Every entry in candidate `own_promises` MUST have exactly one `promise_bindings` entry with the same `promise_id` and `promiser_agent_id`. Bindings MUST have no unmatched or duplicate targets. Candidate authorship establishes a proposed complete bundle, not issuance of another participant's actions.

### C2-20

For `basis = previously_issued`, `source_ref` MUST identify an exact selected offer or explicit promise record and `source_promise_id` MUST identify the issued action within it. The complete candidate action MUST equal that source action, including actor, promisees, semantics, parameters, qualifications, evidence references, and validity. A changed action requires a new issuance basis and fresh authorized adoption; a prior signature MUST NOT be stretched to cover it.

### C2-21

For `basis = issue_on_adoption`, the candidate contains a description awaiting its named promiser's adoption. An optional `request_source` MUST identify the exact `offer_ref` and `request_id` addressed to that promiser; it records request provenance and issues nothing. A revised response MUST be explicit in the complete candidate, never represented as identical requested behavior merely because its label matches.

### C2-22

Direct adoption MUST be permitted without a reciprocal offer. The adopting agent MAY issue its qualified own behavior through adoption of the exact candidate, supplying its own applicable capability and authority evidence. The candidate MUST NOT contain a circular reference to that future adoption. New own terms absent from a prior request require the same explicit complete-candidate adoption.

### C2-23

`terms_adoption.candidate_ref` MUST identify the exact candidate bytes, and each `adopted_own_promise_ids` entry MUST resolve unambiguously to that authenticated adopter's action in that candidate. The list MUST cover the actions the candidate requires that adopter to adopt, with no other actor's IDs. The adoption confirms previously issued actions or first issues `issue_on_adoption` actions as their bindings specify.

### C2-24

An empty `adopted_own_promise_ids` list MAY express assent when the candidate requires no substantive performance promise from that participant. The act of adopting terms MUST itself have the required capability, authority, and current policy evidence. Participants MUST NOT invent a reciprocal service promise solely to make the agreement appear symmetric.

### C2-25

Adoption MUST cover the complete candidate, including exact action bindings, conditions, commercial constraints, privacy, and principal refusal rules. A subset, stale candidate, or mixture of source revisions MUST NOT count as adoption of another bundle. Confirmation of an already issued action MUST NOT create a duplicate substantive obligation.

## Revision, withdrawal, and disclosure

### C2-26

Any change to an action's authenticated meaning MUST create new immutable issuance/adoption content with explicit linkage to its predecessor where applicable. The prior record MUST remain attributable. A new description or candidate MUST NOT silently supersede another independently issued promise or an accepted obligation; replacement requires its specified disposition and fresh adoption.

### C2-27

Promise validity MUST follow its declared policy, without mandatory universal expiry. Withdrawal MUST identify the exact affected issuance and authenticated withdrawal authority. It prevents new reliance where the governing policy so specifies, but MUST NOT rewrite prior issuance, erase accepted terms, or imply that principal refusal or a linked replacement has occurred.

### C2-28

Disclosure of promises and their qualification evidence MUST follow the applicable publication and negotiated privacy policies. Intended promisees, permitted observers, and authorized redistributors are distinct scopes. Portable proof establishes authorship of exact content; it MUST NOT be treated as proof that a promise was fulfilled, that every qualification remains true, or that a downstream act is authorized.
