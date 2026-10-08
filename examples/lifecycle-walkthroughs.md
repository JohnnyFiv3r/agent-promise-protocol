# Lifecycle walkthroughs

**ABP 0.4-draft · schematic worked cases**

The first case is the ordinary bilateral path. The later cases show the [optional composition feature](../contracts/07-composition.md) reusing that same agreement primitive, alongside separately negotiated handoff/evidence features. These are not executable fixtures, native integrations, or completed transactions. Names such as `P_report`, `C_sources`, and `AO_sources` stand for exact content references in a real record. They are deliberately not JSON digests, proofs, credentials, endpoints, or demonstrated results.

Every case assumes explicit current principal delegation, permitted contact, understood semantic definitions, and privacy adequate for the named evidence. Actual candidates select those policies. No example selects a universal budget, refusal duration, expiry, payment method, or assessment rule. All principal refusal periods remain positive and policy-defined.

## 1. One ordinary agreement

**Purpose:** Connect one existing capability and its principal's policies without building a composition engine.

Requester `Q` asks provider `P` for a bounded document summary. The action vocabulary defines what the summary contains; the agents' policies define delegated authority, capacity, privacy, budgets, and the protected principal-recovery rules. The RP1 baseline supplies the common agreement and verification path. No transaction plan, composition binding, auction, atomic bundle, or handoff/evidence extension is required to form this agreement.

1. **Ask.** `Q` emits its qualified intent under permitted publication/contact rules. That asks for a summary; it does not promise to purchase one. Where `Q`'s policy admits a bounded first offer, `P` need not obtain an extra invitation.
2. **Offer.** `P` issues a conditional promise describing the work it can perform within its capability and authority. `Q` can request clarification or a revision within the admitted budget. A comparison with other offers uses the same offer semantics and does not require composition.
3. **Select exact terms.** The agreement coordinator is `Q`, the author of the chosen initiating intent. It distributes one exact `candidate_ref`, `C_summary`, to both agents. The candidate includes the selected offer, complete required terms, and principal-recovery rules. Neither agent reconstructs a supposedly equivalent candidate from a prose summary.
4. **Adopt.** Both agents authenticate adoption of `C_summary`. `P` confirms its own qualified action. `Q` issues only any own actions that the terms actually require; direct adoption does not require a reciprocal offer or an invented performance promise.
5. **Form and preserve recovery.** The coordinator records the one accepted object `AO_summary`. The harness carries out the profile's notice, refusal, status, and durable-recovery mechanics. Agent agreement is now established; principal clearance is a separate observation.
6. **Recover a lost response.** The caller reuses the original operation identity or the exact candidate's authorized formation-recovery path. The harness retrieves the existing outcome. The application does not create a second candidate, reservation, or agreement merely because a response is missing.

The application sees the agreement fact separately from principal recovery:

| Application-facing observation | Exact meaning |
|---|---|
| Agreement formed | Both agents adopted the exact candidate and authorized finalization is recorded. |
| Recovery pending | Required notice or a principal's protected period has not completed; schema status is `pending_refusal_windows`. |
| Recovery cleared | Current evidence establishes `refusal_windows_closed` for every required principal. |
| Refused | A valid principal refusal makes this accepted object ineligible permanently; a renewed agreement needs a new candidate and fresh adoption. |
| Unresolved | Required evidence, ordering, or authority cannot establish the current recovery outcome; this is not clearance. |

**Performing the action:** Even after recovery clears, the summary application's protected action needs its own current authorization and must preserve the relevant principal rights. Agent agreement and clearance do not grant document access, authorize disclosure, start processing, or create a payment mandate. If the parties also select a handoff or typed evidence feature, those feature rules apply independently; they are not prerequisites for the baseline agreement itself.

**Application responsibilities:** Supply the capability's meaning, truthful capacity/qualification facts, principal policies and actual constraints, and the authorized connection to the existing application. The conforming harness handles profile verification, exact references, invocation, durable replay/order, and notice/refusal/status processing. Applications do not invent a new protocol mechanism for those duties; the harness cannot invent truthful capacity, authority, or reversible effects for them.

## Reading optional composition records

The following composition cases require every affected participant to accept the required feature and exact plan through its own candidate. `supported_features` treats composition, handoff, and evidence independently: a composition plan with formation-only dependencies need not require handoff or typed result evidence. The composed-report and subcontract cases below select the additional features they actually use. Unsupported required dependency semantics are rejected, never approximated.

When composition is selected, the reference direction is:

```text
transaction_plan P
  declares component IDs, participants, typed requirements, and dependencies
       ↓ referenced by
candidate C with composition {plan_ref: P, component_id: slot}
       ↓ selected by
orchestrator-issued composition_binding {plan_ref: P, component_id: slot, candidate_ref: C}
       ↓ adopted independently by the candidate's two agents
their terms_adoption records → C4 accepted_offer AO → C5 principal status
```

The plan contains no future candidate digests. The binding is immutable and contains no future accepted-object field. C4 resolves `C` to its exact accepted outcome; evidence records may subsequently refer to that outcome. A plan, binding, adoption, accepted object, clearance observation, and downstream authorization establish different facts.

## 2. Competing alternatives with an optional shared plan

**Purpose:** A requester selects one report provider without turning every option into an agreement or silently withdrawing the others. This case chooses a shared plan for explicit grouping; ordinary solicitation and comparison can instead use independent bilateral offers without composition.

Broker `B` orchestrates `P_choice`. Requester `Q` and providers `F` and `S` retain their own principal delegations. The two slots are:

| Component | Required agents | Role/group | Typed requirement |
|---|---|---|---|
| `fast-report` | `Q`, `F` | `alternative` / `one-report` | Named report scope and fast-service terms under its declared profile |
| `detailed-report` | `Q`, `S` | `alternative` / `one-report` | Named report scope and detailed-service terms under its declared profile |

`one-report` is a label. Requester `Q`'s explicitly adopted selection policy supplies the actual at-most-one-active-selection rule and its recoverable authority. The broker's plan supplies neither capacity nor that enforcement authority.

1. `F`'s initiating offer is the declared origin of candidate `C_fast`, making `F` its agreement coordinator. `Q`'s initiating intent is the origin of `C_detailed`, making `Q` that candidate's coordinator. Broker `B` is neither coordinator merely because it routes both candidates.
2. `B` binds each slot to its exact candidate. Each candidate names `P_choice` and its own slot. Listing the four record references does not adopt either candidate.
3. `Q` chooses `C_fast` under its selection policy. Only `Q` and `F` adopt `C_fast`; they do not adopt `C_detailed`. The selected authority preserves the choice against conflicting use under C4.
4. `F` finalizes `AO_fast`. The result records agent agreement and begins the required principal-notice/refusal process. It is not immediate clearance for a report request, charge, or disclosure.
5. The detailed option remains governed by its own validity, admission, and selection constraints. It is not withdrawn by inference. A message declining further negotiation is not a withdrawal of `S`'s issued promise.

**If the finalization response is lost:** `Q` recovers `C_fast`'s formation outcome from `F`. It cannot select the detailed candidate merely because it lacks `AO_fast` locally. Protected selection remains in doubt until the declared authority resolves it.

**If a principal refuses `AO_fast`:** That object remains refused. Choosing the detailed option requires the selection policy's authorized disposition of the earlier selection and fresh current guards. The broker cannot release a reservation or cancel an external operation by updating its summary.

## 3. A composed report

**Purpose:** A report depends on independently agreed source collection and analysis, without combining three bilateral agreements into a group signature.

Integrator `I` orchestrates `P_report`. Requester `Q` wants the integrated report; researcher `R` and analyst `A` offer separate contributions.

| Component | Required agents | Role | Typed requirement |
|---|---|---|---|
| `sources` | `I`, `R` | `contribution` | A source package satisfying a specified evidence vocabulary and scope |
| `analysis` | `I`, `A` | `contribution` | An analysis package satisfying its specified subject and method |
| `report` | `Q`, `I` | `contribution` | An integrated report containing the declared contributions |

The plan declares these dependencies:

| Subject / stage | Required conditions | Disposition |
|---|---|---|
| `report` / `formation` | `sources.agent_agreement` and `analysis.agent_agreement` | Unavailable: hold; refused: block; failed: block |
| `report` / `handoff` | `sources.principal_clearance` and `analysis.principal_clearance` | Unavailable: hold; refused: block; failed: block |
| `report` / `handoff` | Qualifying source-package and analysis-package evidence | Unavailable: hold; refused: block; failed: hold under the declared corrective-evidence rules |

Each evidence condition has its own versioned `evidence_type_uri` and immutable `evidence_requirement_ref`. Those definitions identify the exact component/action, accepted reporting authorities, content relationship, satisfaction rule, and freshness/finality requirements. A provider's generic “done” message cannot satisfy them.

1. `I` distributes `P_report`; the participants review its requirements and relevant privacy/access rules. `Q` receives the dependency evidence it is entitled and required to inspect, not automatic access to every private subcontract term.
2. Exact candidates `C_sources`, `C_analysis`, and `C_report` each reference the plan and matching slot. `I` issues one valid immutable binding per slot. Each component's own origin determines its agreement coordinator.
3. The source and analysis agreements finalize independently. Their principal periods may still be pending. Their valid accepted objects can satisfy `report`'s **formation** dependency because that dependency asks for agent agreement rather than principal clearance.
4. `Q` and `I` adopt `C_report`; its coordinator verifies both formation dependencies and finalizes `AO_report`. Every distinct principal then has the rights adopted for its own agreement.
5. Each contribution's downstream work requires that component's relevant clearance and native action authority. Composition does not start either job. Evidence of any eventual result is retained under the selected claim semantics.
6. The report's contemplated handoff requires its own principal clearance, current native action authority, and all declared **handoff** dependencies. Merely having three accepted objects is insufficient.

**If analysis evidence is unavailable:** The report handoff stays held. Independently authorized source activity need not wait for an unrelated missing observation. No timeout or transaction-wide failure is inferred.

**If the analyst's principal refuses `AO_analysis`:** The report's dependent handoff blocks on that refused source. `AO_report` still records its historical agent agreement; it is not automatically refused, erased, or canceled. An authorized replacement or other agreed disposition is needed for affected commitments.

**If the integrator finds another analyst:** A new material slot/participant requires a new plan revision and affected candidates. Existing adoptions over `P_report` do not authorize substituting the new analyst, even if the report title is unchanged.

## 4. Subcontracted work

**Purpose:** A provider owns its promised composite service while obtaining a separately agreed contribution from another autonomous agent.

Customer `Q` negotiates with provider `G`. Provider `G` proposes `P_service` with an upstream component between `Q` and `G`, and a `subcontract` component between `G` and specialist `S`. The typed requirements distinguish `G`'s composite service from `S`'s specific contribution.

1. `G`'s upstream offer issues `G`'s qualified promise of its own composite result. It does not issue `S`'s action or represent that `S` has already agreed. If `G` promises only to request specialist help, the upstream action says that instead of promising the specialist's output.
2. `G` and `S` independently negotiate and adopt `C_specialist`, bound to the subcontract slot. `S` supplies its own capability and authority evidence. The customer is not a signatory to this candidate and does not automatically receive its private commercial terms.
3. `Q` and `G` adopt `C_service`, which binds `P_service` and its upstream slot. The plan's adopted handoff dependencies require the specialist's principal clearance and a narrowly specified contribution-evidence condition. Its own agreement still requires customer/provider clearance.
4. The subcontract's native invocation is a separate protected action. Neither the plan nor the upstream promise grants `G` access to `S`'s endpoint, authority to disclose customer inputs, or permission to incur a charge.
5. Any contribution claim must bind the exact specialist agreement and relevant action. `G`'s aggregate report cannot convert a missing or disputed specialist claim into verified evidence.

**If the specialist refuses before its window closes:** The upstream dependency blocks. This does not authorize `G` to cancel the customer's agreement, refund a transaction, or obtain another specialist under different terms. Each such disposition requires its own actual authority and evidence.

**If a specialist operation has an unknown external outcome:** The participant responsible for that action recovers its original native operation. A second specialist or a fresh operation ID cannot be used to pretend the first action never happened.

**If the upstream promise allowed alternative subcontractors:** The precise adopted selection/dependency semantics determine that flexibility. A fixed slot naming `S` cannot silently become `S2`. A new material plan and affected agreement references require fresh adoption and disposition of prior commitments.

## 5. Noncommercial information exchange

**Purpose:** Two agents exchange authorized information without inventing a buyer, seller, price, or payment obligation.

Library agent `L` offers a bounded collection of public document identifiers to research agent `R`. The agreement's universal domain terms use an information-exchange vocabulary. No commercial or payment profile is required merely to make the agreement structurally complete.

1. `L` issues an offer promising its own act of supplying the specified identifier set under stated privacy and capability qualifications. Its provide polarity means that act; it does not mean “seller.”
2. `R` may directly adopt the exact candidate without issuing a reciprocal offer. If the terms require `R` to receive and store the set under an agreed use restriction, its `issue_on_adoption` promise covers that specified behavior. If the terms require no substantive counterpromise, `R`'s adoption list may be empty while its authority to assent is still verified.
3. This standalone exchange uses the bilateral baseline with no plan or composition binding. If a later workflow needs dependencies on it, participants must explicitly negotiate the appropriate feature and exact adopted references; the application does not acquire composition semantics merely by naming the earlier agreement.
4. The agreement coordinator finalizes the exact candidate. Both principals receive their required qualifying notices and positive refusal periods. “Free” does not mean immediate clearance for disclosure.
5. Before transmitting information, the responsible native boundary establishes the relevant clearance, current disclosure authority, exact recipient/content scope, and stable action identity. Agent agreement alone does not send data.

**If the recipient refuses:** Future dependent disclosure is blocked. Previously disclosed information cannot be represented as retracted merely because a record says “canceled.” The protected right must be preserved by the handoff rules; a promised refund has no bearing on retracting information.

**If the payload arrives but its meaning is disputed:** A transport receipt establishes its native transport fact. A provider's fulfillment claim, the recipient's assessment, and any independent evidence remain separately attributable. No payment or settlement object is manufactured for a noncommercial exchange.

## Phase ordering and limits

These cases separate immutable reference direction from logical dependency order. A plan can avoid circular hashes while still declaring `A.formation` dependent on `B.agent_agreement` and `B.formation` dependent on `A.agent_agreement`. The core records those unmet conditions and does not infer agreement or impose a timeout. A reference profile that requires an acyclic dependency graph rejects that plan before adoption; it does not silently delete an edge.

Partial agreement, principal refusal, held evidence, independent progress, and unknown native outcomes remain visible. A common orchestrator or a successful bilateral finalization never establishes an atomic commit, rollback, execution, or settlement across the whole transaction.
