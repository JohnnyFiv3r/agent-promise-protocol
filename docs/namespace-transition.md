# Agent Promise Protocol naming and namespace

The active project is **Agent Promise Protocol (APP)**. The public repository is `JohnnyFiv3r/agent-promise-protocol`, the Python distribution and CLI are `agent-promise-protocol`, and the import package is `agent_promise_protocol`.

This release uses a distinct APP wire namespace. The earlier Agent Bazaar (ABP) name and identifiers remain only in historical records, archives, related-work references and explicit compatibility tests.

| Surface | Earlier ABP identifier | APP reference draft |
|---|---|---|
| Semantic/interaction profile | `abp/0.4-draft` | `app/0.4-draft` |
| Admission profile | `abp/admission-policy/0.4-draft` | `app/admission-policy/0.4-draft` |
| RP1 runtime profile | `abp-rp1/0.1-draft` | `app-rp1/0.1-draft` |
| Schema namespace | `urn:agent-bazaar:draft:0.4:*` | `urn:agent-promise-protocol:draft:0.4:*` |
| A2A data wrapper | `{bazaar, records}` | `{app, records}` |
| JWS type and critical headers | `abp-record+jws`, `abp_profile`, `abp_scope` | `app-record+jws`, `app_profile`, `app_scope` |
| Native operation-key prefix | `abp-rp1-` | `app-rp1-` |

The exact extension and profile URIs now use the `agent-promise-protocol` repository path, as recorded in [release metadata](../release.json) and [C6](../contracts/06-a2a-evidence.md). A GitHub redirect for the old repository name does not make the old and new protocol identifiers equal.

APP does not silently accept or translate ABP envelopes, proof headers or A2A wrappers. Identical-looking application terms do not make differently signed namespaces interchangeable. This release includes no compatibility adapter or ledger migration utility.

Existing signed records, adoptions, accepted objects, refusals and unresolved native-operation identities must retain their original bytes and governing profile. Do not relabel or replay an unresolved ABP act as a new APP act. Any transition involving existing commitments must preserve their original evidence, recover their outcomes and follow the previously adopted replacement/recovery rules. A new APP agreement requires its own qualified issuance and exact adoption.

The authored JSON examples were regenerated as fictional APP examples, including content references and illustrative proof-payload digests. They are not migrated live records and still contain no authentic proofs. Historical validation JSON files are unchanged and describe the earlier ABP sources at their recorded commits. The new release report identifies and verifies the actual APP sources.
