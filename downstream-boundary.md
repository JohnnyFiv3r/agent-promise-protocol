# Protected handoff and downstream evidence

**APP 0.4-draft · integration guide · October 9, 2026 namespace revision**

This guide carries forward the October 8 ABP boundary under the distinct [APP namespace](docs/namespace-transition.md).

The ordinary bilateral path produces exact agent agreement and interpretable principal-recovery status without requiring a native adapter. The optional `adapter-handoff` and `lifecycle-evidence` features extend that same agreement model through the [C8 boundary](contracts/08-adapter-boundary.md). Native systems retain action authorization, execution, commerce validation, payment, fulfillment, assessment, and settlement.

## Three facts a consumer must keep separate

| Fact | Required basis | What it does not establish |
|---|---|---|
| Agent agreement | Exact candidate, both required adoptions, and authorized C4 finalization | Principal clearance or permission to perform an external action |
| Principal clearance | Current C5 evidence for every relevant positive protected period, qualifying notice, usable refusal, and authoritative closure | A human signature or native action authority |
| Downstream authorization | Current permission for the exact actor, action occurrence, payload, recipient/resource, and limits under the native system | That an action occurred, fulfilled its promise, or settled value |

An accepted object initially has pending principal-recovery status. A historical signature, local timer, absent reply, or stale closure snapshot cannot establish current clearance. Refusal remains absorbing for that accepted object. The same protection applies to free information exchanges and paid services.

## Optional feature selection

RP1's default `supported_features` is `["bilateral"]`. `adapter-handoff` and `lifecycle-evidence` are separate feature names; handoff requires lifecycle evidence. Neither requires `composition`. A party can interpret typed lifecycle claims without operating a handoff adapter, and it can form an ordinary agreement without either feature.

Every affected participant must support and accept the required semantics before the dependent act. Naming MCP, AP2, UCP, ACP, x402, MPP, a processor, or a native endpoint in terms does not activate an adapter or demonstrate compatibility. The enabled adapter profile must pin the actual translation, authorization, correlation, retrieval, and outcome rules. Unsupported requirements block the act rather than being dropped.

## Prepare, dispatch, reconcile

When `adapter-handoff` is selected, C8 adds three explicit boundary operations over one exact handoff request:

| Operation | APP-side guarantee | Native boundary |
|---|---|---|
| `prepare_handoff` | Validate the adopted action and freeze the exact translation, native operation key, authorization requirements, and recovery interpretation | No external effect; a prepared translation is not permission to execute |
| `dispatch_handoff` | Establish current clearance, relevant dependency predicates, exact action authority, and the protected disposition of the occurrence; durably record the decision | The selected native system performs the authorized attempt under its own contract |
| `reconcile_handoff` | Recover the existing attempt and interpret attributable observations under the same identity | Read-only with respect to the effect; it does not initiate or reissue it |

The semantic occurrence follows the accepted agreement and adopted action, not an adapter name or transport request ID. Changing carrier, adapter, proof variant, or request ID cannot authorize a second occurrence. A frozen translation cannot be silently replaced while an earlier effect is unresolved.

## Principal recovery at the boundary

Positive protected periods and usable refusal paths are universal participation requirements. Selecting an optional feature cannot waive them. [RP1](profiles/reference-profile.md) selects `no_effects`: separately authorized side-effect-free preparation may precede clearance, while externally effective dispatch waits for all relevant principal periods and current native action authority.

Disclosure to another party, charging, value transfer, access activation, material capacity consumption, publication, and native reservations are effects. Labeling them “preparation” does not bypass the gate. A policy-filled `handoff_rules` field preserves the principal's protection without requiring an application to provide an adapter.

The universal contract permits another understood early-effect profile only if it establishes equivalent effective recovery under C8; RP1 rejects that mode. A refund or cancellation field alone cannot prove recovery, and compensation cannot retract disclosed information.

If a dependent component is involved, its adopted C7 requirements apply at their named stage. An unrelated component does not become a global barrier. A refused dependency can block eligibility but cannot cancel another agreement, release another owner's reservation, reverse a transaction, or confer authority for compensation.

## What returned evidence means

`lifecycle-evidence` provides a common attributable claim shape for `native_execution`, `fulfillment`, `assessment`, `settlement`, and `reservation_disposition`. A claim binds its exact agreement/action subject, reporting authority, versioned semantics, observation, and original native evidence. The category is not a success predicate.

A provider's fulfillment claim remains its claim. An assessment requires the selected assessor and criteria. A payment submission does not establish settled value. An adapter acknowledgment does not establish native execution. A cancellation request does not establish release. Missing or contradictory required evidence leaves the dependent conclusion unresolved.

An uncertain dispatch retains its original operation identity and possible effect. Reconciliation must precede conflicting reuse. RP1 does not automatically redeliver after an ambiguous dispatch and does not claim exactly-once behavior from arbitrary native systems. Refusal, failed dependencies, and unavailable responses do not erase historical effects.

## Native commerce association

A native commerce adapter may correlate exact APP agreement/action references with a native order or Checkout using its selected authenticated extension mechanism. It must independently obtain and verify the native credentials, mandates, approvals, amounts, resource scope, and outcome evidence required by that system. Copying an APP signature into a native object does not create a native mandate.

AP2, UCP, ACP, paid-resource exchange protocols, and processors keep their own schemas, validation, effects, and finality rules. APP retains exact references and interprets attributed evidence through the adopted adapter profile. It neither duplicates their financial state machines nor turns principal-window closure into a native human approval.

## Authored scope and proposed checks

This repository supplies the contract and reference-profile design, not a native adapter implementation. No real mandate, order, payment, fulfillment, or settlement is performed or qualified here.

[Proposed tests](tests/PROPOSED.md) stop at controlled adapter substitutes and injected native evidence. They can challenge translation, clearance gates, replay, uncertain outcomes, and false result claims without creating native transactions. Any later native integration or qualification requires its own scoped implementation and evidence.
