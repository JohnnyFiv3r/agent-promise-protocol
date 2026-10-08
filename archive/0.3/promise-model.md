# Universal qualified-action proposal

**Draft 0.3 · proposal for refinement under user decision 4**

A **promise** is an attributable, qualified action by an agent: the agent has the capability and authority required to perform the action within its stated conditions and limits. An **offer is a promise** whose performance is conditional on the stated agreement and policy requirements. Neither term implies guaranteed future success.

The definition is the engineering meaning of this protocol, informed by Promise Theory's autonomous agents, self-authored behavior, provide/receive polarity, conditions, scope and assessment. It is not presented as a verbatim definition from the book.

## Shared shape

| Element | Meaning |
|---|---|
| Promise identity | Stable identifier for this specific action promise and its immutable version/content |
| Promiser | The agent issuing its own action; linked to the principal whose authority applies |
| Promisees | The identified intended counterparties; distinct from the permitted disclosure audience |
| Action type | Versioned semantic identifier for what the agent will do |
| Semantics reference | Immutable definition of the action's parameters, effects, prerequisites and interpretation |
| Polarity | `provide` or `receive`; describes action direction, not buyer/seller role or agreement acceptance |
| Parameters | Domain-specific typed inputs and subjects, interpreted under the named action definition |
| Capability references | Evidence supporting the agent's ability and relevant capacity to perform the action |
| Authority references | Existing principal-policy/delegation evidence covering issuance and the action under its conditions |
| Qualifications | Explicit conditions, limits and dependencies; each check has a named meaning and evidence requirement |
| Validity | The applicable policy-defined validity rule; no mandatory universal expiry |
| Disclosure | Who may learn or redistribute this record, under the publication and negotiated privacy rules |
| Portable proof | Existing proof mechanism authenticating issuer and exact content; it does not independently establish capability |

These elements are represented by the generic promise/action definitions in the [schema](schemas/contract.schema.json). The schema establishes structural compatibility; action-specific semantics establish what the parameters mean. An implementation that does not understand a required action definition MUST NOT automatically issue or adopt it.

## Why this is universal without becoming a product ontology

The shared structure answers who, what, in which direction, under which conditions, with what ability and authority, and for how long under policy. Service-specific profiles define resources, quantities, units, outputs and other domain terms.

Examples of independently defined action types include declaring interest in research, delivering a report, granting access to a dataset, receiving a notification, or making an API capability available. The core need not prescribe one schema for all those products. The same agent can provide inputs and receive a result; either market side can contain either polarity.

Free-form explanation may accompany typed parameters. Text cannot silently extend the typed action or authority. Unknown or ambiguous required behavior must be clarified before issuance/adoption rather than treated as compatible because descriptions sound similar.

## Intent, offer, request and adoption

**Intent emission** is scoped to communicating or seeking what the emitter identifies. Its `emission_promise` covers that act under publication authority. “I seek research” does not promise to buy research. “I seek research work” does not promise to deliver a particular report. The action's qualifications need to cover declaration/seeking, not an outcome that has not been offered.

**Offer issuance** is the author's own qualified, conditional promise of the specified behavior. It carries issued `own_promises`, not a list labeled unadopted proposals. The offer's conditions can include exact mutual terms, principal review and native downstream prerequisites. Offer issuance therefore has meaning before mutual acceptance, without activating every conditional future action.

**Requested counterpromises** describe what the author wants another agent to promise. They are addressed requests, not signed promises attributed to that agent. Only that agent can issue and adopt its own corresponding behavior.

**Terms adoption** is each party's own authenticated adoption of the complete candidate and its own identified promises under that candidate. It binds the same exact content and principal refusal rules as the other adoption. Neither signer can issue the other party's promise.

Direct acceptance is supported: the recipient need not create an offer solely to answer one. By adopting the exact candidate, it may issue the qualified own behavior requested of it, using its own capability and authority. The requesting party's candidate never supplies that issuance. The other party's acceptance cannot broaden an already-issued offer's conditions.

Agreement does not require inventing a second service obligation. A party may assent with no separate performance promise when the terms require none; its act of adoption remains a qualified, authorized act.

## Capability and authority

Capability and authority are independent: being able to perform an action does not authorize it, and permission does not establish the ability to perform it. Qualification must be checked when an offer is issued and again where material capability, capacity or authority affects adoption/finalization. Explicitly conditional authority is acceptable when the condition and the policy authorizing that conditional commitment are clear. A hoped-for future delegation is not current authority to promise.

Evidence strength is policy-defined. A claimed skill, schema-valid reference or cryptographic signature is not proof of actual competence. The issuer is accountable for its assertion; counterpart policies determine acceptable evidence before adopting terms. Unknown qualification prevents the dependent automatic transition.

An agent can promise its own composite service or its act of requesting a subcontractor. It cannot issue another autonomous agent's delivery promise. If several alternative offers depend on the same capacity, the selection constraints must state that dependency; publishing alternatives does not multiply available capacity.

## No standing-promise mechanism

Principal policies express continuing permission, eligibility and limits. They are not converted automatically into service promises. A qualified action may be issued outside an agreement, but it must identify a specific action, author, conditions and validity. `until_withdrawn` keeps only that specific issued action valid under policy. It must not be interpreted as an ambient undertaking to accept future work or as an automatically recurring service promise.

The protocol ends at the accepted-offer object. A future consumer may assess fulfillment against the agreed action, but Bazaar does not define delivery or assessment records in this version.
