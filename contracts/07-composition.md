# C7 — Composition and dependency coordination

**Normative contract · APP 0.4-draft**

Composition is an **optional negotiated feature over the ordinary bilateral agreement**. The default reference profile's baseline is the bilateral path: ask, offer, select one exact candidate, adopt, form the agreement, and preserve each principal's protected recovery. A single agreement does not require a transaction plan or composition machinery.

This contract applies when participants select composition. It uses [C1 publication/policy](01-publication-policy.md), [C2 qualified actions](02-qualified-actions.md), [C3 admission/recovery](03-admission-negotiation.md), [C4 formation](04-formation.md), [C5 principal refusal](05-principal-refusal.md), and [C6 evidence](06-a2a-evidence.md). The [schema](../schemas/contract.schema.json) defines the optional `transaction_plan`, `composition_binding`, and candidate `composition` fields. Composition reuses exact bilateral agreements; it creates no category of collective assent.

## Actors, plan identity, and consent

### C7-01

An ordinary bilateral agreement MUST NOT require a plan, composition binding, composition engine, auction, atomic bundle, or cross-market coordination. Implementations MAY support those additional arrangements only through their explicitly negotiated features and semantics. Mandatory principal recovery, exact adoption, and agent autonomy apply equally with or without composition.

The transaction orchestrator MAY publish a plan, distribute exact candidate references, bind component slots within its authority, and report attributable dependency observations. The plan's authenticated issuer MUST equal `orchestrator_agent_id`. Orchestration MUST NOT grant authority to issue another agent's promise, adopt its terms, clear its principal's refusal rights, or control its resources.

### C7-02

Each component agreement MUST retain its own C4 originator/coordinator. The transaction plan's `origin_ref` records the larger transaction's initiating provenance; it MUST NOT replace a component's adopted origin. The orchestrator and a component coordinator MAY be the same agent, but their acts MUST be verified under their separate roles and authority.

### C7-03

A `transaction_plan` MUST identify `transaction_id`, immutable revision and predecessor, orchestrator, exact origin reference, component declarations, phase-specific dependencies, privacy policy, and validity. Its complete content reference identifies the adopted plan revision. A mutable transaction name, latest-plan URL, or orchestrator summary MUST NOT substitute for that reference.

The plan lineage key is `(authenticated orchestrator_agent_id, transaction_id)`. Revision 1 MUST have `previous_digest = null`. Revision n greater than 1 MUST advance exactly n−1 in that lineage, with `previous_digest` resolving the full content digest of that immediately preceding plan revision. The predecessor's authenticated author and transaction identity MUST match; missing or conflicting lineage evidence blocks dependent admission rather than permitting a skipped or inferred revision.

At each lineage key and revision, the first admissible plan pins its C6 semantic record identity and unsigned payload digest. Different required content or another envelope `id` at that same lineage revision is a fork, even if the purported successor uses a new operation ID. A fork MUST remain an explicit conflict; arrival time cannot select the authoritative branch or create an additional slot namespace. Proof-only variants of the pinned semantic plan are corroborating variants under C6, not new revisions or branches. Their full references remain distinct and retrievable; no variant may replace a full reference already pinned by a binding or adopted candidate.

### C7-04

Each component MUST have a plan-unique `component_id`, exactly two distinct `required_agents` with their principal identities, a declared role, and a typed `requirement` containing `type_uri` and `parameters`. The requirement MUST constrain which exact agreement may fill the slot under understood semantics; listing two agents or a role label alone is insufficient.

### C7-05

Declaring an agent, principal, component, or dependency in a plan MUST NOT establish membership consent, promise issuance, adoption, or reservation. A participant joins the declared component only by adopting the exact bilateral candidate whose `composition` identifies that plan and slot. It does not thereby sign another component's candidate or undertake the orchestrator's behavior.

### C7-06

The optional capabilities use the exact `supported_features` strings `composition`, `adapter-handoff`, and `lifecycle-evidence`. `adapter-handoff` requires `lifecycle-evidence`; `composition` and standalone `lifecycle-evidence` do not imply support for other optional features. A participant MUST advertise and understand the required capability dependencies. Advertising support MUST NOT imply consent to a particular plan. Every participant affected by a component's adopted obligations or dependency gates MUST explicitly accept composition and all features and semantics required by that exact candidate before those rules may govern it. Listing potential participants in a plan does not supply that acceptance or create a transaction-wide agreement barrier.

Before adopting a composed candidate, each participant MUST resolve and understand the exact plan, its own component requirement, relevant dependencies and qualification semantics, orchestrator authority, and privacy restrictions. Unsupported required composition/dependency semantics or unavailable required evidence MUST block adoption; an implementation MUST NOT approximate them, drop an edge, or proceed as though the candidate were an independent agreement. A private dependency need not disclose unrelated terms, but its authorized evidence must suffice for the dependent decision.

## Acyclic references and exact component resolution

### C7-07

The plan MUST declare stable component identities and requirements without embedding digests of the later candidates that reference it. A candidate's `composition` MUST contain `{plan_ref, component_id}`. This direction separates the immutable declaration from subsequent resolution and MUST NOT be replaced by circular plan/candidate hashes or a mutable placeholder digest.

### C7-08

A `composition_binding` MUST name exactly `plan_ref`, `component_id`, and `candidate_ref`, and be issued by that plan's authenticated orchestrator. The referenced candidate MUST identify the same exact plan and slot, match the component's required agents/principals, and satisfy its complete typed requirement. A binding that fails these checks MUST NOT occupy the slot.

### C7-09

The slot key is `(plan_issuer_agent_id, plan_record_id, plan_unsigned_payload_digest, component_id)`. The plan identity fields are its authenticated issuer, envelope `id`, and unsigned payload digest under C6. A full plan reference includes proof references and MUST NOT itself create a new slot namespace: proof-only variants of one semantic plan remain the same slot.

The first valid binding MUST durably pin the selected full `plan_ref` and one exact `candidate_ref` at that key. An identical resolution is another observation of the existing binding; a different candidate at the same slot is a conflict. A later plan or candidate proof variant may corroborate authenticity under C6 but MUST NOT create another slot, replace either pinned full reference, or substitute for the exact bytes already adopted. C7-08's exact candidate/plan association remains required; a verifier MUST NOT rewrite references merely because unsigned content is equivalent.

### C7-10

The orchestrator MUST distribute the same pinned `candidate_ref` to the component's required adopters and coordinator. Each adopter MUST compare it with the candidate it signs. A binding authenticates the orchestrator's resolution only; neither binding, distribution, nor receipt proves that the required agents adopted the candidate.

### C7-11

The binding MUST NOT be mutated to add a later accepted-offer reference. Formation and recovery resolve the bound candidate's accepted object through C4. A consumer MUST verify that object's exact candidate and adoptions. A different agreement between the same agents, an agreement about a similar subject, or an orchestrator's acceptance claim MUST NOT fill the slot.

### C7-12

Before finalizing a composed candidate, its coordinator MUST verify the valid slot binding, exact participant/requirement match, current plan validity, and all applicable `formation` dependencies in addition to C4's guards. Adoption MAY precede satisfaction of a declared later formation prerequisite when current commitment authority permits that conditional adoption; finalization MUST NOT assume the prerequisite.

## Dependency predicates and stage gates

### C7-13

Every dependency MUST identify a unique `dependency_id`, its `subject_component_id`, a stage of `formation` or `handoff`, and one or more required component conditions. All component references MUST resolve within that exact plan. All listed requirements are conjunctive. A participant MUST NOT substitute a requirement from another stage, component, or plan revision.

### C7-14

`agent_agreement` requires the exact bound component's valid C4 accepted object. It establishes agent agreement only. `principal_clearance` additionally requires C5 clearance for every principal of that object under current applicable evidence. Neither condition establishes fulfillment, another component's clearance, or native permission to perform an external action.

### C7-15

An `evidence` requirement MUST specify both `evidence_type_uri` and an immutable `evidence_requirement_ref`. The requirement MUST define the qualifying claim, authorized reporting/verification roles, exact component/action subject relationship, satisfaction rule, and applicable observation, freshness, and finality rules. A matching type label, signature, or receipt alone MUST NOT establish satisfaction.

### C7-16

Dependency evaluation MUST preserve the exact binding, accepted-object reference where required, source evidence, evaluator, and applicable policy/version. It MUST distinguish an established condition, an unmet condition, unknown evidence, a refused source agreement, and an established failure under the adopted predicate. The orchestrator's summary MUST NOT override contradictory authoritative source evidence.

### C7-17

`on_unavailable = hold` requires the dependent gate to remain pending when required evidence or authority cannot be established. `on_refused = block` prohibits the dependent transition on that refused source object. `on_failed = block` prohibits the transition on the established failure; `on_failed = hold` retains a pending gate for recovery permitted by the predicate. None of these dispositions issues an external command or automatically refuses the dependent agreement.

### C7-18

Known valid refusal of a dependency's accepted object MUST retain its C5 effect even when an older snapshot claims clearance or the historical agent-agreement fact remains true. Subsequent handoff checks MUST block on that refusal. A formation that validly occurred earlier remains attributable; later source refusal MUST NOT rewrite it as though no agreement existed.

### C7-19

A `handoff` dependency MUST be checked at the dependent action's authoritative handoff boundary with the current evidence required by its policy. The subject component's own principal clearance and native action authorization remain separately required. A declared `agent_agreement` dependency MUST NOT bypass protected recovery for another principal whose resources or rights the proposed action would affect.

### C7-20

Unrelated components MAY proceed independently when their own guards and applicable dependencies are satisfied. A transaction-wide label such as “ready,” “accepted,” or “complete” MUST NOT replace the three distinct facts of component agent agreement, relevant principal clearance, and downstream action authorization. No universal all-components-ready barrier is inferred.

## Alternatives, subcontracting, and changes

### C7-21

The roles `alternative`, `contribution`, and `subcontract` classify a component without creating additional authority or obligations. `selection_group` is descriptive unless the adopted selection constraints define an owner-authorized shared rule. Alternative selection MUST obey that rule; choosing one option MUST NOT silently withdraw another, release its capacity, or establish cross-system atomic selection.

### C7-22

A subcontract MUST form through its own exact bilateral candidate, adoptions, coordinator, and principal-recovery process. The upstream agent MAY promise its own composite result or its own request to the subcontractor as C2 permits. A subcontract link MUST NOT transfer authorship, guarantee the subcontractor's behavior, or make the upstream customer a signatory to the subcontract.

### C7-23

Changing a slot's bound candidate, required participants, material requirement, dependency rule, refusal protection, or other adopted composition term MUST use a new plan revision and new affected candidates with fresh adoption. The new revision MUST name its exact predecessor. Existing candidates retain their original `plan_ref`; membership and obligations MUST NOT migrate to a newer plan automatically.

### C7-24

A new plan or candidate MUST NOT cancel, amend, or supersede a prior accepted component by implication. A replacement affecting existing commitments requires the linked replacement and authorized disposition specified by C4. Unaffected existing agreements remain governed by their own adopted plan and terms; the orchestrator cannot reslot them into a new plan through an unsigned mapping.

## Recovery and limits of composition

### C7-25

After lost binding, formation, or dependency responses, participants MUST recover the same slot and operation outcomes under C3/C4/C6 before attempting conflicting resolution or releasing protected capacity. Unknown outcomes MUST remain unknown. A plan becoming invalid or communication ending MUST NOT erase a possibly completed component formation or external effect.

### C7-26

Refusal or failed dependency MAY block future eligibility as the adopted rules specify. Cancellation, release, reversal, compensation, or disclosure of another component's private state requires its own actual authority and attributable result. A plan's rejection-propagation rule MUST NOT manufacture those powers or describe an attempted recovery as completed.

### C7-27

Logical dependency cycles MAY remain pending in the core; they MUST NOT be treated as satisfied through circular inference. A selected reference profile MAY require an acyclic stage/dependency graph and reject an unsupported plan before adoption. That restriction must be explicit; neither core composition nor a cycle diagnostic imposes a timeout, failure, or forced agreement outcome.

### C7-28

Recoverable bilateral formation and a common orchestrator MUST NOT imply global atomic formation, execution, or settlement. Any stronger guarantee requires separately adopted semantics, actual authority, and evidence of a mechanism supplying it. The baseline MUST preserve partial success, refusal, and unresolved states rather than compress them into a fictional transaction-wide commit or rollback.
