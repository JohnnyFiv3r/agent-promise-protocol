# Independent participant runtime slice

**Implementation boundary and acceptance proposal · not an implemented federated profile**

The [deployment model](../deployment-model.md) supports a connector-accessed or embedded buyer participant, separately hosted seller participants, and optional discovery/aggregation. This slice is the remaining ABP machinery needed to demonstrate those participants negotiating with separate stores. It preserves the existing C1–C8 boundaries and builds no provider search, indexing, ranking, subscription service, comparison engine, connector tools, shopping UI or payment integration.

## First topology

Use two separately addressed processes with distinct private keys, stores, public-only peer enrollment and principal policy evaluators. Exchange the same signed core records through C6. Neither participant receives the other's database handle, signer, private policy state or fixture object. Endpoints can be configured directly; no directory or central account service is needed.

Start with a mutually selected RP1 conflict authority for the affected resources, explicitly delegated by both owners where necessary. It may be operated by one participant or a selected third party. The authority is scoped infrastructure, not a mandatory Bazaar service. Separate participant evidence stores do not remove the need for that one authority's recoverable order. A topology with incompatible resource authorities is a different profile task and remains blocked until its formation/withdrawal/recovery mechanism is defined and verified.

## Runtime responsibilities

1. **Peer enrollment and routing:** validate advertised profile/features, principal bindings, credentials, authority assignments and exact references before contact or adoption. A connector/host cannot override authenticated actor identity through request parameters.
2. **Evidence exchange and receipt recovery:** materialize only explicit authorized evidence, verify original proofs, retain full variants and stable operation outcomes, and recover missing responses through the original recipient. Possession, verification and semantic admission remain distinct.
3. **Remote governing results:** implement authenticated reliance on the actual coordinator's accepted object and the selected authority's status/selection evidence. Receiving a result must not re-run local formation or treat a peer-supplied result as a local authority command. Existing C6 result/evidence carriage suffices; any profile-specific authority service binding must be specified rather than invented inside a fixture.
4. **Authority boundary:** define the authenticated invocation, decision evidence, atomic ordering and recovery bindings used with the selected conflict authority. Preserve owner scope across all competing coordinators. Local `Ledger.get` shortcuts cannot stand in for remote current facts.
5. **Principal recovery:** provide each principal's qualifying notice and protected refusal path independently of the assistant's chat session. Bind status to the exact accepted object, selected authority, continuity, health and freshness. Recover potentially timely admissions before closure; withhold reliance during unresolved communication/authority failures.
6. **Custody and scoped disclosure:** allow each participant to retain its permitted evidence without unrestricted access to another customer's terms. Separate principal identities, policy/authority checks, recipient accounting and record access must survive hosting by a common provider. Shared infrastructure is not proof of tenant isolation.
7. **Optional controlled handoff:** use an enrolled fake adapter only. Verify fresh remote clearance and native-authority substitutes at the gate; preserve the original dispatch key across crash, retry and host/routing changes. No live order, service, mandate, charge or settlement.

## Required demonstrations

- Direct buyer/seller formation through A2A with no discovery service or MCP product implementation. Separate stores contain only records explicitly exchanged or locally authored.
- The same seller endpoint works with a second independently configured buyer provider. No global provider account, proprietary buyer field or hidden original database is required by ABP.
- A relay carries the same signed intent/offer without acquiring its author's coordinator, promiser or principal authority. Optional routing does not broaden disclosure or reply consent.
- A coordinator restart after committed formation and before delivery returns the original accepted object. A new carrier/session does not create another formation, allocation or refusal window.
- A refusal durably admitted at the selected authority before/equal to the deadline remains effective when its response and the seller's status connection are lost. After reconnection, the seller observes the refusal and performs zero fake effects.
- A refusal unable to reach the designated boundary is not falsely reported as admitted. Adopted notice/path-health and uncertainty rules prevent claiming clearance where its required evidence is missing; do not claim every possible client network outage is observable.
- Two coordinators compete for one resource through its same authoritative scope. At most one succeeds; no local observation or timeout frees an unresolved selection.
- Missing, stale, forged or contradictory remote accepted/status/authority evidence blocks reliance. An authenticated copied record is not automatically a locally admitted transition.
- Exhausting one recipient/allowance does not consume an unrelated recipient's budget. Conversely, aliases, new offers, new sessions and additional routing paths do not reset a deliberately shared scope.
- Disconnecting the shopping interface leaves the required notice, refusal and replay routes usable under the selected profile. A reconnect recovers the exact agreement and current status.
- Incompatible authority profiles fail explicitly before adoption. A permissive fallback or copied common database must not turn that failure into a successful demonstration.

These are future integration acceptance checks. The current [portable-evidence tests](../tests/runtime/test_deployment_portability.py) cover carriage, identity, custody and explicit incompatibility only. They do not implement or certify this complete slice. Independent implementation and external-builder assessment remain separate from a two-process test using the same library.
