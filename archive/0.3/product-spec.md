# Product specification: Agent Bazaar

**Draft 0.3 · Owner: John Inniger · MIT licensed**

An agent should be able to express what it seeks, discover a counterpart, negotiate alternatives and form an exact accepted offer under its principal's policy. It should not need to have been built around that counterpart's API or product catalog.

The product is an A2A interaction contract from publication through accepted offer. Existing discovery/subscription services connect through publication contracts. A service source may expose an MCP endpoint, API, proprietary dataset or any other product/service. Either harness may emit the initiating intent, make offers and coordinate the resulting negotiation according to its role as originator.

## Product behavior

1. A principal sets permission to publish, receive contact, issue qualified actions and accept terms. Existing policy systems hold that delegation.
2. An agent emits an intent under that policy. The qualified act of declaring or seeking an outcome is distinct from promising the outcome itself.
3. A permitted recipient may make a first offer directly when policy allows it, or request an invitation. Discovery visibility alone does not permit contact.
4. Agents issue qualified offers and may retain several named alternatives. Offer revisions replace one named option without erasing other options. Budgets limit admitted traffic; policies determine validity.
5. Agents negotiate scope, price and commercial route as far as their principals allow. A new compatible route need not have been published as an identical object by both parties.
6. Both agents adopt exact candidate terms, selected option revisions, policy evidence, coordinator identity and principal refusal rules. The originator records finalization in an immutable accepted-offer object.
7. Each affected principal receives the final terms and a usable refusal path. The policy-defined review window preserves a human right of refusal after the agent-only handshake. The accepted object initially has pending-window status.
8. Authenticated current status records refusal, closed windows or uncertainty. The object and status can then be interpreted by a downstream consumer. They never substitute for its own authorization.

## Scope

Included: attributable publication consent; qualified intent and action promises; offers as promises; multiple alternatives; private bilateral negotiation; policy-controlled validity and budgets; originator coordination; exact adoption; immutable replacement; portable proof; principal notification/refusal and accepted-object status.

Outside: discovery/ranking engines, identity providers, credential issuance, native AP2/UCP/ACP validation, payment handling, processors, settlement, fulfillment execution, delivery assessment and refunds. Named commercial conditions and service specifications are data agreed in the accepted terms, not implementations of those systems.

## Design requirements

| ID | Requirement |
|---|---|
| P1 | Only an authenticated agent with the required capability and authority can issue its own qualified action; declarations do not prove qualification merely by asserting it. |
| P2 | Intent emission, service offers, counterpart requests and exact adoption retain distinct meanings. |
| P3 | Receiving an offer or discovering an intent cannot manufacture the recipient's promise. |
| P4 | Multiple options remain independently identifiable, with explicit shared-capacity/exclusivity constraints. |
| P5 | Validity comes from policy; traffic, retries and duplicate discovery paths cannot silently expand budgets or consent. |
| P6 | Exact terms, selected alternatives, relevant policies and originator coordination are bound into portable proof. |
| P7 | Agent agreement preserves principal refusal for the agreed positive window after notice of that agreement. |
| P8 | Fresh evidence is required to interpret status; unavailable evidence never means refusal rights have been cleared. |
| P9 | Accepted records are immutable; replacement and refusal leave attributable history. |
| P10 | The same accepted object can be consumed by independent commerce systems without becoming a substitute for native authority. |

## Implementation and testing

The specification and original implementation will be MIT licensed. Comparison systems are conceptual references only. No comparison source, schemas or tests are adopted.

The user has selected source-backed research as a potential first demonstration. The testing regime is deferred until this contract is written. An internal toy consumer may simulate downstream payment; simulation is not part of Bazaar and does not establish a native integration or real transaction.

[User decisions](decisions-v0.2.md) and [contract map](contract-map.md) identify the current design. The archived draft's fixed research reviewer, correction budget and payment workflow are superseded.
