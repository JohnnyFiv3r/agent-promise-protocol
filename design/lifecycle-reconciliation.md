# Lifecycle feedback: reconciliation with ABP 0.3

**Design note · October 8, 2026 · not a normative contract revision**

This note considers the supplied feedback beginning “expand the protocol's coverage without prescribing its implementation.” It records how that direction changes the current draft and what the next authoring pass must resolve. This is the historical reconciliation brief. The [0.3 snapshot](../archive/0.3/contracts/README.md) preserves its starting point; the resulting [0.4 decisions](../decisions-v0.4.md), [contracts](../contracts/README.md) and [reference profile](../profiles/reference-profile.md) now implement the authoring direction. No runtime, conformance suite or native integration is implemented here.

## Material change to the boundary

[Controlling decision 14](../decisions-v0.2.md) deliberately ended the contract at the accepted-offer object and its interpretation. The feedback proposes extending semantic coverage through composition, downstream handoff and interpretation of fulfillment, assessment and settlement evidence. That is a material scope change to record explicitly in the next decision register.

The proposed new boundary is: Bazaar specifies attributable acts, exact agreement, dependencies, protected principal recovery, handoff prerequisites and evidence interpretation throughout a transaction. Native systems own execution, order validation, payment, settlement and their own authority. Recording a native result is not performing it; recording an authorization claim is not issuing that authority.

## What changes and what is already required

| Feedback | Current 0.3 position | Next authoring work |
|---|---|---|
| Competing alternatives | C3/C4 already preserve separate options, validity and shared capacity constraints | Connect discovery/selection to a larger transaction without implicitly withdrawing unselected alternatives. |
| Composed transactions | Each candidate is bilateral; no common composition/dependency record exists | Define exact membership, dependencies, progress gates and authorized refusal/failure dispositions. Preserve bilateral agreement formation. |
| Delegated/subcontracted work | C2 distinguishes promising one's own composite result from promising a request to another actor | Bind independently formed subcontract agreements and their evidence to declared dependencies without transferring authorship. |
| One universal model | C2 is domain independent; candidate structure still requires a field named `commercial_terms` | Separate universal agreement terms, domain vocabularies and interoperability choices. Noncommercial exchanges must not invent payment or commercial obligations. |
| Mandatory principal recovery | C1/C5 already require a positive period per distinct principal, qualifying notice and usable refusal; there is no immediate-clearance waiver | Make that protection an explicit admission and handoff requirement across dependencies and external effects. |
| Exact selected candidate | C4/C6 require exact shared references and preserve adopted proof variants | State who distributes the selected reference and distinguish transaction orchestration from each agreement's originator/coordinator. |
| Abstract coordination guarantees | C4 already permits different mechanisms and preserves unknown outcomes | Define composition guarantees without inferring cross-system atomicity from an orchestrator's existence. |
| Trust and failures | Existing rules distinguish authorship from capability and require current evidence | Consolidate the trust assumptions, locally enforceable rules, detectable violations and externally dependent guarantees. |
| Complete reference profile | C6 has a concrete carrier shape, but proof, policy, retrieval and ordering choices remain unselected | Choose and document one coherent set of existing mechanisms without narrowing the core to the demonstration domain. |
| Contract before tests | Decision 15 and the conformance note explicitly defer the test regime | Reconcile the contract and reference profile first; worked examples expose disagreements without becoming hidden requirements. |

## Three distinct boundaries

1. **Agent agreement:** Required agents adopted the same exact candidate and the authorized coordinator recorded formation.
2. **Principal clearance:** Every principal-recovery requirement relevant to the action has cleared under its adopted policy and current evidence.
3. **Downstream authorization:** The particular actor is independently authorized to perform the particular external action under that system's rules.

These facts must not collapse into one `accepted`, `ready` or `completed` status. Execution, observed fulfillment, assessment and native settlement also need separate meanings and attributable evidence.

## Composition choices that require explicit semantics

**Group membership is not assent.** A transaction can contain several bilateral agreements with distinct exact candidates. Membership does not make every agent a signatory to every candidate or grant access to every component's private terms. A participant receives the dependency evidence it is authorized and required to interpret.

**Dependencies must be adopted and immutable where they affect obligations.** A transaction orchestrator cannot change a shared plan after adoption to widen someone's obligation or release condition. A declaration must identify which component/action depends on which fact and at which stage: formation, clearance, handoff or a later observed result. It must identify whose evidence establishes that fact and what happens when it is refused, unavailable or disputed.

**Avoid circular content references.** A composition document containing candidate digests cannot also be embedded by digest into those same candidates. The design needs a deliberate acyclic declaration/resolution structure: stable component identities and exact dependency rules, followed by attributable resolution to concrete agreement references. Any resolution that changes material adopted obligations requires fresh adoption. This is an authoring problem to solve, not permission to substitute a mutable plan for exact terms.

**Clearance follows the action's declared dependencies.** An independently eligible component need not wait for unrelated agreements. A dependent component cannot proceed using only its own cleared window. Refusal propagates through the adopted dependency rules and actors' actual authority; it does not automatically cancel the whole group or another principal's unrelated agreement.

**Preserve agreement-level coordination.** Use “transaction orchestrator” for the role coordinating a larger plan and “agreement coordinator” for the authenticated originator defined by C4. They may be the same agent. A transaction-level role does not silently replace an agreement's originator or give it control of another principal's resources. The selected candidate reference for an agreement is distributed consistently to its required adopters.

**Do not imply atomic composition.** Individual recoverable formation does not imply all-or-nothing execution or settlement across component systems. Any advertised stronger guarantee needs declared semantics, authority, evidence and a mechanism that actually supplies it. Unresolved dependencies can remain pending without universal timeouts or inferred failure.

## Recovery must survive the handoff

The default gate should hold irreversible action until the relevant principal periods have cleared and current native action authority is established. Separately authorized preparatory work may be admitted only when its effects preserve the protected right, including any costs or capacity commitments imposed on the principals.

An earlier-effect arrangement must demonstrate effective recovery under its adopted mechanism. Merely adding refund, cancellation or compensation fields does not establish equivalence. A financial reimbursement does not retract disclosed information or undo every irreversible service. The authoring pass must define what the protected right guarantees before any early-effect profile can claim to preserve it.

The handoff decision must bind exact action and agreement references, applicable dependency/clearance observations, current native action authority and a stable operation identity at a declared authoritative boundary. A prior clearance check alone does not establish permission at a later irreversible dispatch. The profile must bound freshness and ordering, preserve dispatch outcomes across retries and recover unknown external effects before attempting the action again. These are observable guarantees; they do not select a database or coordination algorithm.

On refusal, the protocol must distinguish blocking future eligibility from evidence of a completed release, cancellation, reversal or compensation. Each external act requires its own authority and attributable outcome. Uncertain outcomes remain uncertain. Refusal stays absorbing for the accepted object; any renewed agreement has a new candidate and fresh adoption.

## Evidence and trust model

Use one common evidence relationship with typed, versioned claim semantics. Bind each assertion to the exact agreement, action, reporting actor, authority, native reference, observation time and applicable verification/finality rules. Preserve the native evidence rather than translating away qualifications.

- A provider's fulfillment claim is not an independent assessment.
- A receipt or transport acknowledgment is not proof of the claimed external effect.
- A payment submission is not settled value; native systems define their own result and finality semantics.
- A valid signature authenticates the statement; it does not establish competence, sufficient capacity, honest reporting or future availability.
- An orchestrator's summary cannot override contradictory component evidence or invent absent authority.

The trust section should classify each guarantee as locally enforced, detectable from attributable records, or dependent on a designated authority/external mechanism. It should state failure behavior for missing or conflicting evidence and unavailable authorities. It should not introduce a global reputation service or general dispute court.

## Scoped reference-profile design

The next profile document should choose exact existing mechanisms and versions for A2A carriage, identity/delegation verification, canonicalization and proof, policy interpretation, evidence retrieval/access, durable operation recovery, clock/order, principal notice/refusal and downstream evidence correlation. It must explain how its mechanisms realize the advertised guarantees and how participants recognize unsupported requirements.

Transport, action vocabularies and concrete profile choices remain separate from universal transaction structure. A particular payment rail or research-report scenario must not become required merely because it is used by a later demonstration. Current construction templates are not implemented interoperability evidence.

## Next authoring pass

1. Record the lifecycle boundary change and reconcile the controlling decisions, core contract, C1–C6 and downstream note.
2. Define the universal composition/dependency, handoff and evidence semantics; explicitly resolve the pitfalls above.
3. Update schemas and worked examples together. Include competing alternatives, a composed outcome, subcontracted work and a noncommercial exchange as explanatory cases, without prescribing an evaluation regime.
4. Complete the reference-profile design and consolidated trust/failure model.
5. Lock the agreed revision/profile before conformance fixtures, runtime implementation and independent interoperability testing.

The current draft remains reviewable while this scope change is reconciled. This note adds no new authority to agents and changes no accepted-object state.
