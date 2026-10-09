# Required contracts: publication through accepted offer

**Draft 0.3.** Six interface contracts define one A2A extension. They are not separate required services. The [core contract](contract.md) and linked documents are normative for the draft; the [user decisions](decisions-v0.2.md) control the design.

| ID | Contract | Owner and result |
|---|---|---|
| C1 | Publication and policy | Each principal/agent sets audience, permitted uses, admission, validity and commercial eligibility; existing services carry and enforce those rules. |
| C2 | Qualified intent and promises | An agent issues only its own qualified actions; intent emission is scoped to declaring/seeking, while an offer promises its own proposed performance under conditions. |
| C3 | Admission and negotiation | Each recipient controls finite traffic budgets and policy-defined validity. Policies can admit invitations or first offers. Several named options may coexist. |
| C4 | Exact adoption and formation | The initiating record's author coordinates. Each party adopts the exact candidate terms and selected options, with current authority, capability and policy checks. |
| C5 | Accepted offer and principal refusal | The coordinator emits immutable proof of agent agreement. Principal notice, policy-defined refusal windows and authenticated status preserve the post-handshake right of refusal. |
| C6 | A2A and portable evidence | Native A2A carries the records; existing proof mechanisms authenticate exact content and authorship. Native task state never substitutes for agreement state. |

## Required documents

The **[C1–C6 governing contracts](contracts/README.md)** are the normative agent-facing interfaces for draft 0.3. They add the explicit request/receipt and admission-declaration schemas alongside the semantic record schema. The following root documents explain the shared model and provide focused reference material.

- [Publication contract](publication-contract.md) defines C1 and the declared policy surface for C3.
- [Universal promise proposal](promise-model.md) defines C2's shared semantic shape.
- [Core contract](contract.md) defines C2–C5 transitions, alternatives, withdrawal and immutable replacement.
- [Accepted-offer object](accepted-offer.md) details C4–C5 evidence and principal refusal.
- [Architecture and binding](protocol-architecture.md) defines C6.
- [Reference negotiation note](reference-negotiation-profile.md) illustrates policy-controlled admission without standardizing one permit service or fixed expiry.

## Explicit boundary

Bazaar can negotiate commercial conditions and identify downstream commerce/payment preferences. Its output is an accepted-offer object, exact terms, original proof and current refusal/withdrawal status. The status interface is part of interpreting that object; it does not administer execution, delivery, payment or settlement.

AP2/UCP/ACP, payment protocols and processors own their own validation and effects. An integration consumer determines whether and how to proceed using Bazaar evidence and its own authority requirements. [Downstream boundary](downstream-boundary.md) is an interoperability note, not another Bazaar transaction contract.

The earlier delivery/assessment contract and payment-binding state machine are removed from the current scope. Research remains a possible toy-model scenario; its test and evaluation regime is undecided.
