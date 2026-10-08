# Reconciled lifecycle decisions

**ABP 0.4-draft · October 8, 2026.** This revision implements the requested lifecycle reconciliation and reference-profile design. The [0.3 snapshot](archive/0.3/README.md) preserves the previous formation-only boundary. The earlier [fifteen decisions](decisions-v0.2.md) remain controlling except for the explicit scope and test-planning changes below.

| Decision | Reconciled requirement |
|---|---|
| Scope: replaces decision 14's semantic stopping point | Bazaar now specifies composition, protected handoff and interpretation of lifecycle evidence. Native execution, commerce validation, payments, fulfillment and settlement remain external mechanisms. |
| Universal agreement | One bilateral candidate/adoption/accepted-object model covers monetary and nonmonetary exchanges. `agreement_terms` and `transaction_policy_ref` replace commercial-only names; domain meanings remain versioned vocabularies. |
| Layers | Universal semantics, domain vocabularies and concrete interoperability profiles remain distinct. RP1 selects mechanisms without making its topology, limits or example domain universal. |
| Adoption simplicity | Bilateral is the default; it requires no transaction plan, composition engine or native adapter. Signed required features and advertised support gate optional composition, handoff and evidence. The future reference harness owns mechanics; the application owns capability, permissions, truthful limits and its principal channel. |
| Composition | A plan declares stable component identities and immutable requirements/dependencies. A candidate adopts an exact plan/slot. An attributable binding resolves the slot to one exact candidate without circular content hashes. |
| Authority | The transaction orchestrator distributes selected references within its delegated role. Each agreement retains the authenticated initiating-record author as coordinator. Group membership does not issue promises, create assent or cancel another agreement. |
| Principal recovery | Positive protected periods remain mandatory for every distinct principal. No immediate-clearance or ordinary-agent waiver. Agent agreement, principal clearance and downstream authority remain separate. |
| Handoff | Irreversible effects normally wait for relevant clearance and current native authority. An early-effect profile must prove equivalent protection; RP1 rejects early effects and supports only side-effect-free preparation before clearance. |
| Retry safety | Handoff identity follows the authorized action occurrence, independently of adapter or carrier. Uncertain dispatch is reconciled before any possible reuse; native outcome is never inferred from timeout. |
| Evidence | Common attributed records distinguish native execution, fulfillment, assessment, settlement and reservation disposition. Typed claims and their native verification semantics determine what they establish. |
| Trust | Local enforcement, detectable violations and dependencies on trusted authorities/external systems are stated separately. No universal identity, reputation or dispute infrastructure is added. |
| Reference profile | RP1 selects existing cryptographic, transport and policy mechanisms plus concrete retrieval, ordering and notice rules. It is a design, not an implemented integration. |
| Tests: refines decision 15's timing | The user now requests proposed tests. This revision specifies scenarios/oracles through a substituted adapter boundary; runtime conformance fixtures and native integration tests are not implemented or claimed. |

The current profile identifier is `abp/0.4-draft`; old peers must not silently reinterpret 0.3 records with these semantics. Existing action qualifications, independent alternatives, policy-defined validity, flexible negotiated arrangements, privacy, self-authorship, immutable replacement and absorbing refusal remain required.
