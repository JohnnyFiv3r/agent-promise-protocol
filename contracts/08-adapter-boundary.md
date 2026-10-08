# C8 — Handoff, recovery protection and lifecycle evidence

**ABP 0.4-draft · normative · MIT**

This contract defines the Bazaar side of an adapter boundary. `adapter-handoff` (which requires `lifecycle-evidence`) enables its handoff operations; `lifecycle-evidence` alone enables attributed reporting. The default `bilateral` path needs neither an adapter nor a lifecycle reporting subsystem. Its mandatory principal recovery and policy-filled `handoff_rules` still prevent agent assent from being treated as native authority. It applies to the same universal agreements used for information, access, computation, services, goods, money and noncommercial exchanges. [C4](04-formation.md) governs agent agreement; [C5](05-principal-refusal.md) governs principal clearance; [C7](07-composition.md) governs component eligibility. Native systems independently authorize and perform their own acts.

## C8-01 — Boundary and actors

The action's promiser or a specifically authorized representative may request a handoff. The selected adapter translates that exact action into its native request and reports attributable observations. A transaction orchestrator has no additional execution authority merely because it coordinates components. An assessor may issue an assessment only under the agreed assessment semantics and authority. An evidence relay preserves the original reporter and claim.

Bazaar governs the request, its eligibility, preservation of the principal's protected right, operation identity and interpretation of returned evidence. It does not issue AP2 mandates, construct a payment protocol, perform fulfillment or establish settlement by fiat. Native validation, execution, payment and settlement remain beyond the adapter boundary. A deployment claiming compliance MUST enforce the preconditions here at its handoff gate; a native connector's presence in terms is insufficient.

## C8-02 — Three separate decisions

1. **Agent agreement:** C4 has formed the exact accepted object from the required agents' exact adoptions.
2. **Principal clearance:** The relevant C5 periods have cleared with current authenticated evidence and no applicable refusal or unresolved conflict.
3. **Downstream authorization:** The particular actor, action, occurrence, payload, target and limits are currently permitted by the native system and applicable principal delegation.

None implies the next. A historical signature or a valid native credential alone cannot supply the missing decisions. The protocol MUST preserve these distinctions in records, status and user-facing claims. There is no universal transaction-wide `complete` state that substitutes for them.

## C8-03 — Recovery as participation and dispatch condition

Each represented principal MUST have a positive, nonwaivable C5 period with qualifying notice and a usable refusal path. An arrangement that cannot preserve that protection MUST NOT be admitted as an equivalent Bazaar transaction.

Candidates contain `handoff_rules`: an exact policy reference, a `preclearance` mode and, only when `protected_effects` is requested, an exact recovery profile. The default mode is `no_effects`. Its default handoff holds irreversible effects until every principal period relevant to that action and its declared dependencies has cleared and current native action authority is established. An unknown effect classification MUST be treated as externally effective.

Separately authorized, side-effect-free preparation MAY occur before clearance. Preparation MUST NOT disclose protected content to a new party, incur a charge, transfer value, activate access, consume promised service capacity, publish content or create a native reservation/obligation. Such actions are effects in their own right and require their own applicable gates. Local validation and permitted read-only authority/evidence retrieval are preparation, subject to privacy and admission rules.

The universal core allows an understood `protected_effects` profile only if it defines an effective recovery guarantee, authorized mechanisms, protected interests, evidence and failure behavior that preserve the same principal right despite earlier effects. Both parties MUST adopt it and demonstrate current eligibility. Refund, cancellation or compensation metadata alone does not establish that guarantee; compensation cannot retract an information disclosure. Unknown or unverifiable protection blocks early effects. A profile cannot waive the positive period. [RP1](../profiles/reference-profile.md) supports only `no_effects` and rejects `protected_effects`.

## C8-04 — Exact action occurrence and handoff identity

A `handoff_request` binds the exact accepted object, `action_ref = {promiser_agent_id, promise_id}`, typed `action_instance`, selected adapter identity/profile, native request input reference, relevant dependency/clearance evidence, authority references and declared effect class.

The action MUST exist in the accepted candidate and be adopted by its own author. The selected semantic vocabulary MUST define occurrence identity and cardinality. A one-time action cannot be repeated by inventing a new instance ID; a recurring action needs explicitly adopted occurrence and limit rules. A request for a different action, target, amount, disclosure, instance or route requires the authority and adoption applicable to that change.

The semantic handoff key is:

```text
sha256(JCS({
  accepted_issuer_agent_id,
  accepted_offer_id,
  accepted_unsigned_payload_digest,
  promiser_agent_id,
  promise_id,
  action_instance
}))
```

Use lowercase hex with `sha256:` prefix. The accepted fields identify the accepted record's authenticated issuer, envelope `id` and unsigned payload digest under C6. The action fields and typed instance are exact adopted/validated values. Adapter, endpoint, transport, request ID and top-level proof variants are deliberately absent: changing them MUST NOT permit a second instance of the same action. The chosen full accepted reference remains pinned and retrievable; this key does not replace exact adoption.

The selected enforcement mechanism MUST enforce that key across all carriers/adapters able to perform that occurrence. It MUST pin the selected adapter, prepared plan and native operation key before dispatch. Another handoff request with the same semantic key recovers or conflicts with that disposition; it cannot independently create another effect. Shared local storage is not required by the core, but an isolated per-adapter cache is insufficient to advertise this guarantee.

## C8-05 — Three adapter operations

The [interaction envelope](../schemas/interaction.schema.json) adds three purposes whose `subject_ref` identifies one exact `handoff_request`. Requests obey C3 admission, authentication, replay and privacy rules.

| Operation | Permitted behavior | Required output |
|---|---|---|
| `prepare_handoff` | Validate and translate the exact requested action without external effects; establish the selected adapter's authority and interpretation | An immutable `prepared_handoff` and a `prepared` receipt, or a bounded `blocked` receipt |
| `dispatch_handoff` | At the declared gate, verify current eligibility and separately supplied native authority; durably record the dispatch decision, then cross the adapter boundary under one stable native key | `not_dispatched`, `dispatched`, `in_doubt` or a supported resolved observation; never infer fulfillment or settlement from submission |
| `reconcile_handoff` | Read the durable handoff decision and selected adapter's native operation observation by the same key | Existing disposition and attributable evidence, or `in_doubt`; MUST NOT initiate or reissue the native effect |

A `prepared_handoff` binds `handoff_ref`, the computed key, adapter profile, the exact translated `native_request_ref`, stable `native_operation_key`, effect class, native authorization requirements and reconciliation profile. Native request content is opaque to the universal core and interpreted under the selected adapter profile; required verifiers must understand that profile. It is a frozen proposed translation, not authorization or evidence of execution.

Material differences between the adopted action and translated request MUST block preparation. Changes to an already pinned plan require explicit authorized disposition of the previous operation and any required new adoption; they cannot replace a plan while an external effect may be in doubt. RP1 fixes one plan/adapter per key and requires a new candidate plus explicit prior disposition for material replanning.

## C8-06 — Dispatch gate and current authority

Immediately before a first dispatch decision, the enforcing authority MUST establish and retain:

1. Exact agreement, own action, occurrence, selected adapter and prepared translation match, including any transaction plan/component binding.
2. The applicable C7 stage predicates are satisfied by the required authoritative evidence. Unbound components, failed predicates, stale evidence and unknown dependencies do not satisfy a gate.
3. Required principal periods for the action and its adopted dependency closure have cleared, with no known relevant refusal or unresolved conflict. Any supported early-effect exception satisfies C8-03 instead; RP1 has none.
4. Current delegated permission and native action authority cover this exact executor, action occurrence, payload, target and limits. A generic policy `allow` result is not itself an AP2 mandate or other native authorization.
5. The prepared plan and native operation key are still the protected disposition of the semantic handoff key, and no previous dispatch or unresolved attempt permits conflicting reuse.
6. The selected freshness, clock/order and gate mechanism provide the advertised observation guarantee through the durable dispatch boundary. Sequential stale checks must not be described as an atomic global snapshot.

The authority MUST persist its exact gate evidence and dispatch disposition before allowing the native attempt. If the relevant authority cannot make a decision, the outcome remains blocked or in doubt. A rejected dispatch must not secretly create a native effect.

Revocation, dependency change or newly discovered refusal after an earlier gate does not rewrite history. It blocks future reliance under the applicable rules and triggers only those separately authorized disposition actions that are actually available. The protocol does not claim instantaneous knowledge of independent services, nor that a later refusal record reverses an earlier native effect.

## C8-07 — Outcomes, retries and uncertain effects

A `handoff_receipt` binds the exact request/key, phase, immutable revision chain, outcome, prepared-plan reference when available, gate/authorization evidence, stable native key and native evidence references. Receipt identity is scoped by handoff key and phase; ordering/lineage is supplied by the declared adapter authority. C3's interaction receipt reports processing of this operation; the handoff receipt reports the boundary disposition. They are not interchangeable.

| Handoff outcome | What may be concluded |
|---|---|
| `prepared` | The frozen translation exists; no effect or clearance is asserted |
| `blocked` | A prerequisite for the requested step is missing; no new dispatch is authorized |
| `not_dispatched` | Authoritative evidence establishes that this attempt did not cross the native boundary; a missing reply alone cannot establish this |
| `dispatched` | The adapter reports a native submission under the stable key; no successful performance, assessment or settlement follows |
| `in_doubt` | The applicable attempt or native observation is unresolved; preserve its key and possible effect |
| `resolved` | Attributable evidence establishes the native disposition under its selected semantics; success and failure remain claims interpreted from that evidence |

Preparation can be blocked without creating a dispatch. After any potential dispatch, subsequent observations MUST preserve that historical fact: neither `blocked` nor `not_dispatched` may erase an earlier admitted native attempt. Conflicting receipts produce an unresolved observation while retaining their evidence. A `resolved` report may be superseded only by attributable later evidence permitted by the native semantics; it is not universally irreversible settlement.

Lost responses, process restarts, new agent request IDs and alternate adapters MUST NOT trigger a second native act. Reconciliation is read-only with respect to the effect. Any permitted redelivery must be proven by the selected native idempotency semantics to address the same single operation and preserve the protection; lack of such evidence leaves the operation in doubt. RP1 never automatically redelivers after an ambiguous dispatch.

A profile MUST state the limits of its native guarantee. Bazaar-side deduplication alone does not prove exactly-once execution by an external service. Supporting an adapter boundary does not establish that every native adapter can meet its requirements.

## C8-08 — Refusal and dependent disposition

A valid principal refusal remains absorbing for that accepted object. Undispatched dependent actions become ineligible where their adopted rules require it. Independent agreements retain their own validity and rights.

Reservation release, cancellation, reversal, compensation and replacement are separate actions with their own authority and outcomes. A blocking dependency or refusal does not itself execute any of them. The declared selection/recovery mechanism MUST describe how reservations and conditional commitments remain held, are released, or remain unresolved; an unknown external outcome is never proof that capacity is free.

Already-dispatched effects retain their native evidence and applicable native disposition procedures. A later corrective status record cannot make information undisclosed or settlement undone. Any renewed agreement uses a new candidate and fresh adoptions; it cannot delete a prior refusal or silently substitute component references.

## C8-09 — Lifecycle evidence

`lifecycle_evidence` is a common record shape for attributed observations. Its category is `native_execution`, `fulfillment`, `assessment`, `settlement` or `reservation_disposition`; category alone is not a success predicate. The record binds the exact agreement/action occurrence, reporter role, versioned typed claim, evidence semantics, native evidence references, observation time, authority references and related handoff where applicable.

The selected claim semantics MUST identify allowed reporters/verifiers, subject interpretation, assessment criteria where applicable, evidence requirements, freshness/finality and contradiction/correction behavior. They may define domain-specific states without adding a separate core agreement format. Unknown required meaning blocks reliance. Native signed bytes and references MUST remain accessible to authorized verifiers; an adapter's paraphrase cannot replace required original evidence.

A provider claim, recipient acknowledgment, assessor judgment and native settlement observation establish different facts. A signature authenticates a statement; it does not prove the underlying event. A `settlement` category with a claim such as “submitted” remains a submission claim. No core code may infer settled value, acceptable fulfillment or satisfied dependencies merely from a category, HTTP success or an `applied` interaction receipt.

Evidence may be incomplete, conflicting or subsequently corrected. The core preserves it and blocks any dependent conclusion not supported under the adopted rules. It does not appoint an evaluator, choose a research rubric, establish a dispute court or convert an assertion into another agent's promise. Evidence disclosure remains subject to C1/C7 privacy; sharing one component's result does not reveal every agreement in the transaction.

## C8-10 — Conformance boundary

Contract checks stop at adapter requests, frozen translations, gate decisions, operation identity, reported dispositions and interpretation of supplied evidence. [Proposed tests](../tests/PROPOSED.md) use deterministic adapter substitutes and injected evidence. They must not create native orders, request real mandates, charge accounts, transfer funds, deliver paid services or claim verified settlement. Native adapter qualification is a separate activity requiring its own scope and evidence.
