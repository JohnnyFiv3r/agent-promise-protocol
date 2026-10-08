# Proposed contract and adapter-boundary tests

**ABP 0.4-draft · 27 proposed scenarios · every behavioral and adoption scenario below is unrun**

This document proposes the test regime for the [governing contracts](../contracts/README.md), including [composition](../contracts/07-composition.md), the [adapter boundary](../contracts/08-adapter-boundary.md) and the [reference profile](../profiles/reference-profile.md). It contains no executable tests and authorizes no live service, payment or settlement. The revision and reference profile must be locked before executable conformance fixtures or independent interoperability testing are implemented. Worked scenarios may expose a contract disagreement; they do not silently decide the contract.

## Evidence status

The repository's [authoring checker](../checks/validate.py) checks authored schema shapes, fixture structure and local reference/digest consistency within its documented limits. Its recorded output for a particular revision is evidence only of those checks. This proposal does not rerun that checker or claim that an earlier run validates the completed 0.4 draft.

None of the scenarios below has been implemented or executed. Current fictional proof references are not signatures and cannot establish authenticated authorship. A future cryptographic case requires the selected real proof mechanism and controlled test keys; a future behavior case requires an instrumented participant implementation. A fake adapter result establishes only handling of that fake's contract, never actual fulfillment, settlement or AP2 interoperability.

## Proposed test boundary and oracle

Use controlled identities, explicit principal policies, a controllable authoritative clock/order, durable operation observations and deterministic fake dependency/adapter authorities. Keep simulated policy numbers local to each case; no sample duration, quota or timeout becomes a protocol default. Exercise both qualifying and disqualifying evidence where specified.

The oracle is the attributable result and permitted side effects: exact references, operation/receipt history, quota disposition, formation/clearance facts, adapter calls and retained uncertainty. Natural-language output or a native task's success alone is never the oracle. Fake probes count dispatch attempts separately from simulated external effects and distinguish lookup/reconciliation from a new execution request.

## Publication, qualified actions and bounded negotiation

### P01 — Symmetric intent and permitted first offer

- **Setup:** Two agents publish authorized seeking/availability intents with declaration-only `emission_promise`; the recipient permits a bounded first offer.
- **Stimulus:** Deliver each intent, then submit a qualified first offer within the permitted scope without an invitation.
- **Oracle:** Intent processing creates no service/purchase promise or adoption. The offer can be admitted under its own authority and budget. Reversing buyer/provider posture does not change these rules.
- **Boundary:** Publication through offer admission; no model quality, discovery ranking or external performance claim.

### P02 — Invitation and disclosure scope

- **Setup:** Recipient policy requires an invitation; a grant names one peer, topic, purposes and finite allowance. Private terms have a narrower audience than the public intent.
- **Stimulus:** Try no grant, an unrelated peer, a mismatched topic/purpose and a valid grant; attempt to redistribute private terms using public-intent permission.
- **Oracle:** Only the qualifying contact is admitted. Publication permission does not authorize private disclosure, adoption or external action. Grant receipt creates no service promise.
- **Boundary:** Admission and disclosure enforcement; no claim of preventing an authorized recipient from copying information elsewhere.

### P03 — Shared allowance and protected control

- **Setup:** Two carriers use one declared accounting scope with finite negotiation and separate protected control allowance.
- **Stimulus:** Submit new options/revisions/clarifications through both carriers to exhaust the negotiation allowance; replay an admitted operation; submit an authorized refusal/status/recovery operation.
- **Oracle:** Carriers and new IDs do not reset the shared allowance. Exact replay does not consume another logical negotiation allocation. Negotiation exhaustion blocks further discretionary work without consuming or disabling the protected control path.
- **Boundary:** Instrumented admission and fake work reservations; no broad denial-of-service or Sybil-resistance claim.

### P04 — Validity does not create a forced outcome

- **Setup:** One option is `until_withdrawn`; another has an explicit deadline; no agreement has formed.
- **Stimulus:** Advance the controlled clock, exhaust a conversation budget, close transport and deliver a native task cancellation.
- **Oracle:** Only the explicitly expired option becomes ineligible under its policy. No event invents adoption, refusal, agreement, failure of promised performance or release of an in-doubt earlier commitment.
- **Boundary:** Negotiation eligibility; no universal liveness or automatic cleanup guarantee.

### P05 — Direct adoption and promise provenance

- **Setup:** One selected offer has the issuer's qualified promise and a requested counterpart action. Prepare one exact candidate using `previously_issued` and `issue_on_adoption` bindings; prepare another legitimate candidate needing no substantive action from its assenting peer.
- **Stimulus:** Copy the request as if already issued; change a sourced action; attempt valid direct adoption without a reciprocal offer; use an empty own-promise list only for the legitimate assenter.
- **Oracle:** Fabricated or mismatched provenance fails. The named actor's qualified adoption can issue its own pending action. Direct acceptance and genuine assent without an invented reciprocal service remain representable.
- **Boundary:** Issuance/adoption semantics and evidence; no proof that the promised service can actually be performed.

## Exact formation, races and composition

### P06 — Exact candidate and proof variants

- **Setup:** Both participants receive one selected full candidate reference. Produce another proof-only variant and a materially changed candidate claiming the same immutable identity.
- **Stimulus:** Substitute the variant for an already adopted full reference; combine adoptions for different full references; submit the same unsigned request with an independently valid proof variant.
- **Oracle:** No substituted reference or mixed adoption creates formation. Proof-only variants remain separately retrievable, do not create another act and recover the same already-pinned operation where permitted. Changed required content at the immutable identity is a conflict.
- **Boundary:** Canonical identity, proof verification and exact adoption; not equivalence of free-text terms.

### P07 — Option withdrawal and finalization order

- **Setup:** Both adoptions are available and selection is protected under one explicit ordering mechanism.
- **Stimulus:** In separate controlled runs, order withdrawal before finalization, finalization before withdrawal, and leave their relative order unknown.
- **Oracle:** Withdrawal first prevents finalization on the old evidence; finalization first preserves the accepted bytes; unknown order yields no asserted new success or conflicting release. Sender timestamps cannot choose the winner.
- **Boundary:** Declared authoritative ordering; no claim that separate uncoordinated stores are atomic.

### P08 — Capacity shared across agreement coordinators

- **Setup:** Two candidate agreements under different originators compete for one exclusive resource controlled by one designated capacity authority.
- **Stimulus:** Attempt concurrent finalization; lose one response after the authority records its decision; advance an unrelated local timer.
- **Oracle:** At most one qualifying commitment consumes the resource. The uncertain operation is recovered; its reservation is not released or reused solely because its reply or timer expired.
- **Boundary:** Fake resource authority and declared scope; no guarantee against undisclosed promises outside that scope.

### P09 — Formation and receipt recovery

- **Setup:** Admit `finalize_candidate`; interrupt after the durable result but before delivery. Later expire/withdraw the original action admission basis while retaining authorized outcome-recovery access.
- **Stimulus:** Replay the same operation, then query formation through a different admitted operation for the same candidate; reuse the first operation key with changed content.
- **Oracle:** All valid recovery returns the original accepted result without another formation. Recovery uses current disclosure permission rather than reapplying expired action eligibility. Conflicting reuse has a separate conflict response and cannot replace the original receipt chain. Repeat with recovery access revoked: withhold protected output without changing its durable disposition.
- **Boundary:** Crash/replay semantics in controlled storage; no real crash tolerance claimed before implementation.

### P10 — Composition retains separate exact agreements

- **Setup:** An immutable plan defines A–B and A–C component slots and their required agents; attributable bindings resolve each slot to a distinct exact candidate under its proper originator/coordinator.
- **Stimulus:** Use B's adoption to satisfy A–C; substitute a similar candidate; bind the wrong participants to a slot; re-sign the same unsigned plan and use its new full digest to bind a second candidate into the same component; have the transaction orchestrator replace a component reference after material terms were adopted.
- **Oracle:** None establishes the missing assent or authorized replacement. Each candidate's plan/slot association must match the binding and adopted requirements. Proof-only plan variants share one semantic slot key; they neither create another slot nor replace the pinned full plan/candidate references. Membership and orchestration do not create adoption, coordinator authority or access to another component's private terms. Resolution requires no circular candidate/accepted-object digest.
- **Boundary:** Composition membership/resolution and bilateral formation; no multiparty agreement primitive.

### P11 — Phase-specific dependencies and refusal consequences

- **Setup:** One component is independent; another requires a named component's principal clearance before handoff; a third uses a separately declared fulfillment-evidence gate.
- **Stimulus:** Supply formation alone, then clearance, then the required evidence in separate steps; refuse the prerequisite agreement; present an unresolved/circular prerequisite configuration.
- **Oracle:** Each gate responds only to its adopted phase and evidence meaning. Refusal blocks affected eligibility without fabricating cancellation of independent components. An unsupported or unsatisfied cycle produces no guessed progress or forced failure; any declared valid progress path must be evaluated as specified.
- **Boundary:** Dependency interpretation, not cross-system atomicity or guaranteed eventual completion.

### P12 — Subcontract and composite-result authorship

- **Setup:** A promises its own composite result; a separate A–B agreement may provide an input. Also prepare A's narrower promise merely to request B's work.
- **Stimulus:** Treat the request as B's promise; omit B's exact agreement evidence; report B's refusal/failure.
- **Oracle:** A request never supplies B's issuance. Dependency eligibility follows the exact adopted rules. A's own composite commitment is not silently rewritten into a request-only promise or discharged by a subcontractor's failure.
- **Boundary:** Promise/dependency interpretation; no automatic damages, dispute decision or substitute procurement.

## Mandatory principal recovery and handoff

### P13 — Every distinct principal has protected review

- **Setup:** Bilateral agreements represent either two distinct principals or one shared principal; a composition contains several agreements for the same principal.
- **Stimulus:** Attempt zero duration, an ordinary-agent waiver, a missing principal descriptor, duplicate conflicting descriptors and a purported transaction-wide waiver.
- **Oracle:** Every agreement preserves exactly one effective positive descriptor per distinct represented principal. A shared principal within one agreement is not counted twice; the same principal across separate agreements does not silently lose any agreement-specific rights.
- **Boundary:** Terms/adoption and admission requirements; not a claim of human reading or express human approval.

### P14 — Notice, outage and window derivation

- **Setup:** Finalized accepted terms have declared notice/refusal rules and positive durations.
- **Stimulus:** Provide a queue acknowledgment, notice for wrong terms, inaccessible terms, an unusable refusal action, then qualifying notice. Repeat the qualifying notice later; introduce an outage governed by the adopted policy.
- **Oracle:** Only qualifying notice can start a window; no missing notice invents a deadline. Repetition does not restart/shorten it. Outage effects follow the adopted rule; absent sufficient evidence, clearance stays pending/unresolved.
- **Boundary:** Fake notice/refusal mechanisms and controlled clock; no real delivery or human-read claim.

### P15 — Deadline refusal, false freshness and incomplete order

- **Setup:** One authoritative order defines notice, refusal admission and closure; use the profile's bounded clock uncertainty and freshness rules.
- **Stimulus:** Admit refusal exactly at the deadline; attempt closure at the deadline; supply a stale or sender-backdated active snapshot, a newer revocation, a forked status or a still-pending event that could be timely.
- **Oracle:** Timely refusal wins and remains absorbing. Closure requires strictly later authoritative order, reconciled relevant events and valid current evidence. A favorable timestamp or historical signature cannot substitute for those facts.
- **Boundary:** Authenticity plus the declared authority's ordering rules; not proof that a dishonest authority has disclosed its entire history.

### P16 — Irreversible handoff stays withheld

- **Setup:** The adapter probe exposes a separately authorized irreversible action for an exact agreement, promise and adopted action occurrence, with its applicable dependencies.
- **Stimulus:** Request `dispatch_handoff` while one required window is unstarted/open/refused, a dependency is unresolved, or action authority is absent. Then provide all qualifying prerequisites without changing the action.
- **Oracle:** No execution call reaches the fake adapter before every required gate qualifies. Qualifying inputs permit only the exact authorized handoff. Unrelated independent components do not become implicit prerequisites; a `prepared` receipt alone never permits dispatch.
- **Boundary:** Bazaar-to-fake-adapter gate; no actual service, transfer or settlement.

### P17 — Side-effect-free preparation and no early effects

- **Setup:** One `prepare_handoff` operation only assembles/verifies payload and references; another purported preparation would cause a native reservation, charge or disclosure. The reference profile excludes early native effects.
- **Stimulus:** Request both before clearance; supply separate action authority, a refund field or an alleged recovery mechanism to justify the external effect.
- **Oracle:** Side-effect-free preparation may yield `prepared`. The effectful operation cannot be hidden in preparation or bypass required clearance. Separate authority, refund text and unsupported recovery equivalence do not override the profile's no-early-effects rule.
- **Boundary:** Policy interpretation and fake effect classification; no proof that all real-world effects are reversible.

### P18 — Native authority remains separate

- **Setup:** A valid agreement has cleared principal review. The fake adapter can independently return missing, stale, mismatched or current native authority for a specific actor/action.
- **Stimulus:** Present only Bazaar proofs, a clearance status, an unrelated native credential and finally matching current authority.
- **Oracle:** Agreement and clearance never become a mandate or execution credential. Only separately qualified native authorization can permit the exact adapter action, still subject to the other handoff gates.
- **Boundary:** A controlled native-authority probe; no claim of validating AP2/UCP/ACP or a payment provider.

### P19 — Handoff recheck and correction after dispatch

- **Setup:** A handoff decision has a declared authoritative boundary and freshness/order rules.
- **Stimulus:** Revoke required permission or establish timely refusal before that boundary. Separately, simulate an already dispatched action followed by recovered evidence that an earlier closure claim was faulty.
- **Oracle:** The earlier disqualifier prevents dispatch. Later discovery invalidates future reliance but does not assert that the external effect was undone; any disposition needs its own authority and outcome evidence.
- **Boundary:** Selected handoff ordering and fake native effects; no impossible guarantee of instantaneous cross-service revocation.

### P20 — Stable dispatch identity and unknown native outcome

- **Setup:** A fake adapter records an external effect under the fixed agreement/action-occurrence correlation, then loses the acknowledgment. The adopted action semantics define which occurrence is authorized.
- **Stimulus:** Retry through another carrier/restart; make outcome lookup temporarily unavailable; attempt new request and action-instance IDs for the same occurrence; invoke `reconcile_handoff`; finally reveal the original effect.
- **Oracle:** Recovery preserves correlation and yields no second simulated external effect. Uncertainty is retained as `in_doubt` until authoritative reconciliation. Reconciliation never executes. New IDs cannot authorize another occurrence or escape an unknown result; genuinely recurring actions need separately authorized occurrence rules. Record lookup separately from execution attempts.
- **Boundary:** Adapter contract with a deterministic fake; no proven native idempotency until that specific adapter is independently verified.

## Evidence interpretation and adapter isolation

### P21 — Claims do not become facts by signature

- **Setup:** Use separately typed provider fulfillment, recipient receipt, assessor judgment and native submission/settlement claims, each bound to an exact action/agreement.
- **Stimulus:** Substitute one claim type for another, sign an unsupported assertion, change its subject, or introduce contradictory evidence from a required source.
- **Oracle:** Authorship verifies only the attributed claim. Required assessment/finality evidence remains independently necessary; wrong-subject or contradictory evidence cannot establish a universal completed state.
- **Boundary:** Typed evidence interpretation; no judgment of actual service quality or actual settled value.

### P22 — Native evidence correlation and revisions

- **Setup:** Two agreements have similar descriptions and amounts but distinct native operation correlations; the selected evidence semantics permit later corrections or finality changes.
- **Stimulus:** Attach one operation's receipt to the other agreement; strip native qualifications; supply a superseding correction while retaining an older favorable observation.
- **Oracle:** Descriptive similarity is insufficient correlation. Native evidence and meaning remain preserved; current interpretation follows the declared revision/finality rules without deleting prior observations.
- **Boundary:** Fake native evidence and exact correlation; no new universal financial finality rule.

### P23 — Private dependencies and authorized evidence access

- **Setup:** A participant may learn a specified dependency fact but not every component's terms; the selected profile defines the evidence it can legitimately verify.
- **Stimulus:** Demand undisclosed terms, present unverifiable redacted material as a complete proof, or return the permitted qualifying evidence.
- **Oracle:** Composition does not widen disclosure. Insufficient verifiable evidence leaves the gate unresolved; permitted sufficient evidence can satisfy only its declared fact. No unselected privacy-proof mechanism is assumed.
- **Boundary:** Access control and evidence sufficiency; no universal selective-disclosure or secrecy guarantee.

### P24 — Fake-only adapter containment

- **Setup:** The eventual adapter-boundary test environment contains only controlled probes and synthetic identities/evidence; no live native credentials or service endpoint is supplied.
- **Stimulus:** Submit a request naming a real external endpoint or claiming a fake result demonstrates native AP2/payment/service interoperability.
- **Oracle:** The test boundary refuses live dispatch. Reports identify simulated results and unrun integrations; no fake evidence is labeled paid, settled, delivered or AP2-verified in the real world.
- **Boundary:** Test-environment containment and reporting accuracy; it is not a native integration test.

## Adoption and independent implementation — assessed separately

The following adoption scenarios assess whether the ordinary path is usable and whether the written standard is sufficient, separately from the correctness cases above. They are proposed and unrun. The SDK/reference harness is not implemented by this specification work; these scenarios cannot presently establish ease of adoption. Neither a convenient SDK nor a successful walkthrough proves independent interoperability.

### P25 — Builder adoption through the default harness

- **Setup:** After contract/profile lock and future SDK availability, give a builder who did not author the protocol the [quick-start](../docs/quickstart.md), [default profile](../profiles/reference-profile.md), future SDK and [application/harness interface](../profiles/harness-interface.md). Supply a controlled peer. The builder connects one existing capability, explicit principal policy, its actual capability/capacity constraints, the principal-designated notice/refusal channel and controlled native hook implementations. Native hooks remain fake probes in this test; the harness must not invent their authority or facts.
- **Stimulus:** Using only the published materials, have the builder form one exact bilateral agreement and exercise a principal refusal through the designated channel. Ask the builder to identify agreement, pending/cleared/refused/unresolved principal status and separate downstream authorization. Record application integration changes, protocol-specific custom machinery and any undocumented explanations needed.
- **Oracle:** The builder can complete the flow by supplying application facts, policy and declared hooks. The SDK handles the selected profile's proof/retrieval, durable operations, replay/ordering and notice/status mechanics without a bespoke protocol engine. Both principals retain positive protected periods; valid refusal is preserved and prevents dependent handoff. No principal authority, truthful capacity, waiver or native permission is inferred for convenience. Required undocumented protocol rules or application-authored replacements for promised harness mechanics are adoption gaps, even if the resulting flow is otherwise correct.
- **Boundary:** Future SDK adoption in a controlled environment. Capability quality and real external performance are not assessed. No native execution or settlement occurs; observations about integration effort do not create an invented duration target or claim that today's design is already easy to adopt.

### P26 — Independent participant without the SDK

- **Setup:** After lock, an independent builder implements a participant from the normative contracts, schemas, selected profile and public semantic vocabularies without using the reference SDK or its implementation code as the specification. A separately implemented controlled peer uses the same advertised profile.
- **Stimulus:** Exchange intent and a qualified offer, adopt the same exact candidate, finalize, exercise qualifying notice and timely principal refusal, and recover a lost response. Include a required unsupported semantic feature and an operation replay; do not supply private clarification of unstated rules.
- **Oracle:** The independently authored participant exchanges and interprets the same exact records and outcomes, preserves principal rights and recovers the same operation without duplicate formation. Required unsupported semantics block the dependent act. Any ambiguity requiring author-only knowledge is a normative/profile completeness gap; copying SDK behavior is not an acceptable substitute for resolving it in the specification.
- **Boundary:** Proposed two-implementation interoperability against the locked profile. This is separate from SDK usability, does not establish universal compatibility, and requires actual implementation and execution before it can be reported as verified.

### P27 — Minimal bilateral path and explicit optional capabilities

- **Setup:** Two participants advertise support for ordinary bilateral negotiation under the default profile. Neither supports composition, atomic bundles or downstream handoff. They have the required principal policies, notice/refusal channels and selected local durability/ordering mechanism; the application supplies real constraints rather than global coordination infrastructure.
- **Stimulus:** Form and refuse a simple bilateral agreement without a transaction plan, composition binding, transaction orchestrator, global atomicity mechanism, native adapter hooks or handoff code. Separately propose an optional advanced feature, first as unrequired metadata and then as a required condition of an automated act.
- **Oracle:** The ordinary agreement/refusal flow remains available without advanced subsystems. Capability advertisement and required-semantics checks make unsupported advanced requirements explicit; they block only the dependent act instead of being silently approximated. Ignoring unrequired metadata is allowed only when it changes no authority, promise, adopted condition or recovery right. The minimal path still enforces exact adoption, applicable capacity constraints, durable recovery and every principal's protected period.
- **Boundary:** Minimal integration surface and capability negotiation, not a weakened conformance mode. Negotiation-only participants have no implied native action authority or obligation to implement downstream execution.

## Proposed sequence after contract lock

1. Pin the exact contract/schema/profile revision and resolve any scenario whose oracle still depends on an undecided semantic rule.
2. Author executable structural and cryptographic fixtures with explicit trust roots and negative cases; preserve the distinction from current nonvalidating examples.
3. Implement the behavioral scenarios against a participant harness and deterministic fake authorities/adapters. Retain authoritative ordering and side-effect evidence for failures and successful cases.
4. Assess builder adoption through the future SDK and independent implementation without it as separate activities. Exercise independently implemented participants using the same pinned binding/profile; report usability, normative completeness and interoperability separately from single-implementation or fake-adapter results.
5. Propose any particular live native adapter qualification separately, with its actual authority and integration boundary. These tests neither select nor authorize such an integration.

Passing the eventual suite would support only the advertised profile, declared trust assumptions and exercised boundaries. It would not prove honest counterparties, universal compatibility, real-world delivery, payment or settlement.
