# RP1 — Concrete reference profile

<a id="rp1-v01"></a>

**RP1 0.1-draft · APP 0.4-draft · normative profile.** The mechanisms below are requirements for an implementation claiming this profile. [Reference runtime 0.1.0](../docs/runtime.md) implements and tests a controlled subset, including real cryptography, OPA and mutual TLS. Its [validation evidence](../validation.md) does not establish every requirement, independent interoperability or a production deployment. Native execution and payment integrations remain outside that evidence.

RP1 binds the [core contracts](../contracts/README.md) to one interoperable set of mechanisms. Core semantics remain independent of this selection. `MUST`, `MUST NOT`, and `SHOULD` constrain an implementation claiming RP1. A value supplied by an authenticated principal policy is a required configuration input, not permission for an agent to invent a value.

## 1. Identifiers, dependencies and supported scope

Let `P` be the exact URI `https://github.com/JohnnyFiv3r/agent-promise-protocol/blob/main/profiles/reference-profile.md`. RP1 uses these identifiers:

| Purpose | Exact identifier |
|---|---|
| Reference profile | `P#rp1-v01` |
| Semantic envelope | `app/0.4-draft` |
| A2A extension | `https://github.com/JohnnyFiv3r/agent-promise-protocol/blob/main/protocol-architecture.md#v04` |
| Proof profile | `P#rp1-jws-ed25519` |
| Authorization decision interface | `P#rp1-opa` |
| Evidence retrieval | `P#rp1-https-get` |
| Authority/order profile | `P#rp1-durable-authority` |
| Notice/refusal profile | `P#rp1-principal-inbox` |
| Handoff boundary | `P#rp1-handoff-adapter` |

`P#…` in this table means textual expansion of `P`, not a relative identifier. Identifier comparison is exact. A mutable web page does not select a new version; participants MUST pin the understood contract, profile, policy and schema content. Unknown required profiles, fields, critical headers, action types, predicates or authority roles MUST fail closed. There is no fallback to ordinary chat, an older profile, or an alternative proof algorithm.

RP1's default is **one bilateral agreement**, using `submit_record`, `finalize_candidate` and `query_status`. It requires no transaction plan, multi-party coordinator, native adapter or payment mechanism. The ordinary application supplies its capability, the principal's permission and designated notice channel, truthful limits, and performance integration only when that optional feature is enabled. The reference harness is responsible for the mechanical protocol work described below. The Python runtime supplies implementation hooks; the high-level application facade in the [harness interface](harness-interface.md) remains a design contract rather than a published SDK API.

Advanced capabilities use the same universal schema and these independently advertised feature identifiers:

| Feature | Requirement and default |
|---|---|
| `bilateral` | Required and enabled by default; C1–C6 agreement and principal recovery |
| `composition` | Optional; C7 plans, bindings and dependency evaluation |
| `lifecycle-evidence` | Optional; typed C8 lifecycle evidence reporting and interpretation |
| `adapter-handoff` | Optional; C8 Prepare/Dispatch/Reconcile; requires `lifecycle-evidence` |

The Agent Card's APP extension `params` MUST additionally contain `referenceProfileUri`, `profileManifestRef` and `supported_features`. They name this exact RP1 profile, the signed realm manifest below and the distinct enabled feature strings. Default `supported_features` is `["bilateral"]`. Every signed core record and interaction carries `required_features`, including `bilateral`. Its declared features and those necessarily implied by its kind and fields MUST be a subset of the verified support of every participant required for that transition. The harness checks this intersection before the dependent transition and again before adoption; receipt of an advanced record does not activate it. A transaction plan or candidate `composition` field requires `composition`. Native handoff requires `adapter-handoff` and `lifecycle-evidence`. Neither is required for an ordinary agreement, and a policy-filled `handoff_rules` field by itself requires no adapter. Known optional features may be omitted; unknown required ones are blocked, never approximated.

Every supported formation's relevant commitment and resource conflicts are governed by one mutually accepted authority ledger. Every owner of a governed resource MUST explicitly delegate the relevant ledger decisions to that authority. A resource MUST use that same authority across all concurrent negotiations in RP1, not a different authority per offer. A formation spanning incompatible authorities is unsupported and MUST be blocked before adoption. Different independent domains may choose different authorities; RP1 does not require a global operator. Enabled composition additionally requires an acyclic C7 plan.

The component's originator/coordinator still authors its `accepted_offer`; the authority's durable formation evidence does not replace that authorship or either adoption. The authority serializes the decisions delegated to it. It does not acquire ownership of agents, invent promises, or grant itself control over native systems.

**Deployment scope:** this common conflict authority is selected for the affected owners and resources. It is not a mandatory APP operator, discovery provider or custodian of all participant records. Separately hosted participants MAY keep distinct keys and permitted evidence stores while using the accepted authority for the facts it orders. That topology still needs authenticated remote authority/evidence bindings and current-status recovery; runtime 0.1's shared SQLite access does not implement them. This clarification does not add a cross-authority commit algorithm, relax the same-scope rule or create another RP1 wire version. See the [deployment model](../deployment-model.md).

Every RP1 candidate MUST select `handoff_rules.preclearance = "no_effects"` and the exact RP1 policy reference. `recovery_profile_ref` MUST be absent. The profile permits no exception for early payment, irreversible execution, secret release, or externally material reservation. Side-effect-free preparation has the limited independent authorization described in section 10.

### Realm manifest and harness responsibilities

An RP1 harness MUST load one authenticated manifest at realm enrollment, then fill in the fixed mechanisms automatically. Applications and negotiating models do not select cryptography, transport, replay behavior or a policy engine per transaction. The manifest is a signed profile evidence document of type `P#rp1-v01/manifest`, with these exact body fields:

| Field | Required value |
|---|---|
| `realm_id` | Stable nonempty deployment realm identifier |
| `reference_profile_uri` | `P#rp1-v01` |
| `app_profile` | `app/0.4-draft` |
| `a2a_extension_uri` | Section 1's exact extension URI |
| `a2a_protocol_version`, `protocol_binding` | `1.0`, `JSONRPC` |
| `transport_security` | `TLS1.3-mTLS-PKIX-pinned-leaf` |
| `proof_profile_uri`, `evidence_retrieval_profile_uri` | `P#rp1-jws-ed25519`, `P#rp1-https-get` |
| `authorization_profile_uri`, `authority_profile_uri`, `notice_profile_uri` | `P#rp1-opa`, `P#rp1-durable-authority`, `P#rp1-principal-inbox` |
| `supported_features` | Unique strings from the preceding table; default `bilateral` only |
| `trust_registry_bootstrap_ref` | Exact administrator-approved initial registry reference |
| `authority_scope_id` | Mutually accepted section 6 scope |
| `domain_vocabulary_refs` | Exact understood capability/predicate vocabulary references; required even for ordinary domain meaning |
| `adapter_contract_refs` | Empty by default; exact enabled native contracts when `adapter-handoff` is enabled |

Administrative keys used to validate enrollment are configured out of band. The manifest cannot bootstrap trust from its own signature. Service endpoints, current keys and principal policies are resolved through its authenticated registry; endpoint values are deployment inputs, not new protocol choices. Registry revisions may update endpoints and keys under section 2, but may not silently change the selected profile or an adopted policy. A changed manifest requires explicit realm re-enrollment and preserves the old agreements' recovery context.

The harness owns schema/proof verification, policy evaluation, evidence resolution, durable replay and ordering, admission accounting, exact candidate distribution, principal notice/refusal/status processing and typed results. Applications provide real capability semantics, principal-approved scope, limits/capacity and designated notice integration. Applications enabling native performance additionally supply truthful adapter hooks and native authority/evidence. A harness cannot manufacture any of those facts. This division is implementation-neutral and does not mandate a separate operator-managed subsystem for each application.

## 2. Carrier and authenticated identity

Use **A2A specification 1.0.0, wire version `1.0`, JSON-RPC over HTTPS**, with C6's `SendMessage`, activation headers and one data part containing `{app, records}`. The native message is a carrier; its JSON-RPC result, extension acknowledgment, task state or transport receipt is not an APP semantic receipt. [Pinned A2A specification](https://a2a-protocol.org/v1.0.0/specification/).

Endpoints MUST require TLS 1.3 with mutual certificate authentication and advertise native A2A mutual-TLS security. Both peers validate certificate chains against configured roots, validity and endpoint identity, then match the leaf certificate's SHA-256 DER digest against the active registry entry. TLS termination and the policy enforcement point MUST share an authenticated channel that preserves the verified peer identity; an arbitrary forwarded header is insufficient. These are profile constraints using [TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446.html) and [PKIX certificate validation](https://www.rfc-editor.org/rfc/rfc5280.html).

RP1 selects a **preconfigured, versioned trust registry**, administered by the participating principals or their explicitly appointed administrator. It supplies local trust, not a universal agent identity system. Its administrative verification keys and certificate roots are installed out of band. Network discovery, an Agent Card, a self-signed record or a `kid` URL MUST NOT enroll a trusted identity.

Each immutable registry revision contains `registry_id`, positive integer `revision`, `previous_revision_ref` (null only initially), `issued_at`, `valid_until`, and these explicit entries:

| Entry | Required binding |
|---|---|
| Identity | `agent_id`, `principal_id`, active interval, authorized role names and exact transport certificate digests |
| Signing key | `kid`, `agent_id`, public JWK, active interval, allowed proof scopes, current revocation state and effective revocation time |
| Authority | `authority_scope_id`, authority agent, accepted ledger epoch, designated coordinator/status/notice roles, resource-owner delegation references |
| Service | Exact HTTPS origins and path prefixes for A2A, evidence, principal inbox, OPA and approved time sources; permitted credential audience |
| Policy | Exact policy-bundle and data-snapshot references, supported action/predicate type URIs, principal-control agents, notice rules and resource mappings |

An administrator signs the revision using section 3 and an already trusted administrative key. Installation MUST verify that signature and monotonic predecessor; a registry cannot authorize its own replacement root. Unknown, expired, revoked, forked or stale required registry state blocks a new act. Historical proof validity is evaluated against preserved authoritative admission time and the relevant historical registry; current action permission is evaluated anew. Unresolved compromise affecting that history blocks reliance rather than guessing that an old signature remains valid.

Delegation is selected through **owner-authorized Rego policy and data**, pinned by exact references in this registry. Each principal's authenticated approval binds the bundle/data digest and the delegated agents, acts, resources, authority scope, validity, refusal representatives and grant-revocation source. A deployment MUST reject a bundle lacking that approval. An agent cannot turn successful signature verification into additional principal authority. Ordinary negotiation authority does not include principal-refusal authority.

## 3. Canonical content and signatures

<a id="rp1-jws-ed25519"></a>

RP1 selects **RFC 8785 JCS, SHA-256 and JWS Compact Serialization with `alg: "Ed25519"`**. The fully specified JOSE identifier is registered by [RFC 9864](https://www.rfc-editor.org/rfc/rfc9864.html); generic `EdDSA` is not accepted in RP1. Public keys use the [RFC 8037](https://www.rfc-editor.org/rfc/rfc8037.html) OKP representation: `kty: "OKP"`, `crv: "Ed25519"`, `alg: "Ed25519"`, registered `kid`, `use: "sig"`, `key_ops: ["verify"]`, and `x` containing the unpadded base64url encoding of the 32-byte public key. Public registry entries MUST NOT contain private `d` material.

All signed objects and JSON content references MUST satisfy [JCS's input and serialization requirements](https://www.rfc-editor.org/rfc/rfc8785.html). Reject duplicate members, invalid Unicode, non-finite numbers and unsupported numeric representations before hashing. Do not normalize Unicode, reorder arrays, coerce numbers/strings or discard unknown fields to make a signature pass. Integer protocol counters MUST be in the exact interoperable range `0..9007199254740991`; overflow requires a new explicitly adopted scope, never wraparound.

For a semantic record or interaction envelope `R`:

1. `U` is the complete JSON object `R` with **only the top-level `proofs` member removed**.
2. `payload = UTF8(JCS(U))`.
3. `signed_payload_digest = "sha256:" + lowercase_hex(SHA256(payload))`.
4. The full `content_ref.digest` is `"sha256:" + lowercase_hex(SHA256(UTF8(JCS(R))))`, including `proofs` and native proof references.

Use an ordinary encoded payload in [JWS Compact Serialization](https://www.rfc-editor.org/rfc/rfc7515.html). The protected header MUST contain exactly these members:

| Header | Value |
|---|---|
| `alg` | `Ed25519` |
| `kid` | Exact registered verification-key URI; also equals `proof.verification_method` |
| `typ` | `app-record+jws` |
| `app_profile` | `app/0.4-draft` |
| `app_scope` | Nonempty, lexicographically sorted, duplicate-free string array equal to `proof.scope` |
| `crit` | Exactly `["app_profile", "app_scope"]` |

These two critical parameters are RP1-defined JWS extension parameters, not claims of IANA registration. `app_scope` authenticates the claimed signature purpose as well as the record bytes; moving a proof reference into a different scope MUST fail. The verifier MUST understand both critical parameters. It MUST reject unknown headers, `none`, detached payloads, `b64: false`, algorithm substitution, embedded keys and key-discovery URLs.

RP1 fixes the scope mechanically: a core semantic record or interaction uses the single scope string `"app/0.4-draft/record/" + R.kind`; a section 3 profile document uses `"app/0.4-draft/profile-document/" + R.type_uri`. Unknown kinds/types are rejected. `proof.suite_uri` MUST equal `P#rp1-jws-ed25519`; `proof.issuer_agent_id` MUST equal the signed record's `issuer_agent_id`; the key's registered agent and allowed scope MUST match. These checks authenticate the issuer's typed statement, not its permission to make it; section 4 supplies the latter.

Let `H = UTF8(JCS(protected_header))`. Sign the ASCII bytes of `BASE64URL(H) + "." + BASE64URL(payload)`, without base64url padding, using Ed25519. The final compact value appends `"." + BASE64URL(signature)`. Verification MUST recover exactly `payload`, check its digest, authenticate the record's issuer through `kid`, and validate every required proof scope and current/historical authority applicable to the act. Comparing a supplied digest without verifying the payload and signature is insufficient.

`proof.native_proof_ref` resolves to a JSON document containing exactly `{id, media_type, compact_jws}`, with `media_type = "application/jose"` and `id` equal to the reference ID. Its reference digest hashes JCS of that complete wrapper; `compact_jws` preserves the exact ASCII JWS string. The wrapper is created before the final `proofs` array. There is no circular digest: the signed payload excludes `proofs`, while the full record reference includes the resulting proof references.

Profile evidence documents that are not core semantic records use exactly `{id, profile, type_uri, issuer_agent_id, issued_at, body, proofs}`, with `profile = "app/0.4-draft"`; section 3 applies unchanged. Their type URI is the relevant section's `P#…` identifier plus a documented suffix such as `/policy-decision` or `/ledger-event`. They are referenced evidence, not new APP semantic kinds or automatic instructions. Unknown evidence types cannot satisfy a guard. Registry documents use this envelope with `type_uri = P#rp1-v01/registry` and the section 2 fields in `body`.

Different proof-only variants have distinct full content references but the same unsigned semantic identity. Preserve the exact full reference originally adopted. A valid re-signature cannot create another operation, accepted agreement, or handoff effect.

## 4. Policy decision interface

<a id="rp1-opa"></a>

RP1 selects **Open Policy Agent 1.21.1, Rego v1**, using its REST Data API. The enforcement point posts `{"input": <the object below>}` to `/v1/data/agent_promise_protocol/rp1/authorize` over the configured mTLS channel and reads the API's `result` object. The version is pinned to the [OPA 1.21.1 release](https://github.com/open-policy-agent/opa/releases/tag/v1.21.1); request/response framing follows the [OPA Data API](https://www.openpolicyagent.org/docs/rest-api). The repository supplies an original [reference Rego policy](../policies/rp1.rego) and [client integration](../src/agent_promise_protocol/policy.py). Their [configuration and canonicalization limits](../policies/README.md) remain implementation-specific; deployments must still authenticate approval of their actual policy and data.

The trusted enforcement point constructs the input from verified state. It MUST NOT forward an agent-supplied identity, clearance flag or policy result as trusted input. All fields below are required; nullable fields use JSON null rather than omission.

| Input field | Exact meaning/type |
|---|---|
| `profile` | `app-rp1/0.1-draft` |
| `decision_id` | New authority-scoped identifier for this evaluation |
| `actor` | `{agent_id, principal_id, transport_certificate_digest}` from current authentication |
| `act` | One of `submit_record`, `finalize_candidate`, `query_status`, `read_evidence`, `notice`, `refuse`, `prepare_handoff`, `dispatch_handoff`, `reconcile_handoff`, `report_evidence`, `authority_commit`; policy also checks the exact `subject.kind`/type and requested transition |
| `recipient_scope_id` | Current authenticated C3 scope |
| `subject_ref` | Exact subject content reference |
| `subject` | Complete digest-verified subject JSON |
| `action_ref` | C8 `{promiser_agent_id, promise_id}` or null |
| `authority_refs` | Exact validated delegation/policy references, array |
| `clearance_refs` | Validated current C5 status references, array |
| `dependency_evidence_refs` | Validated C7 evidence references, array |
| `native_authorization_refs` | Adapter-verified native authorization evidence references, array |
| `authority_scope_id`, `authority_revision` | Scope string and current nonnegative ledger revision |
| `boundary_state_digest` | Digest of the complete decision-relevant policy/registry/resource/status snapshot |
| `policy_bundle_ref`, `policy_data_ref` | Exact currently approved code and data references |
| `clock` | `{now, uncertainty_ms}` under section 8 |

The result object MUST contain exactly `{allow, reason_codes, input_digest, policy_bundle_ref, policy_data_ref, authority_revision, boundary_state_digest, valid_until}`. `allow` is a boolean; `reason_codes` is a nonempty, duplicate-free array drawn from C3's reason-code enumeration plus `policy_denied`, `principal_refused`, `clearance_pending`, `dependency_unmet`, `native_authority_absent` and `resource_unavailable`. `allow: true` requires exactly `["ok"]`; denial excludes `ok`. These codes describe the policy decision, not a native outcome; `input_digest` hashes JCS of the entire input object; references and state fields MUST equal the request's verified values. `valid_until` is a UTC timestamp. Unknown result fields/obligations, missing `result`, undefined decision, errors, stale data, or `allow != true` deny the act. A policy approval cannot override a core or RP1 MUST NOT.

The enforcement point MUST sign and retain `{input, result, evaluated_at}` as `P#rp1-opa/policy-decision` evidence. The evidence authenticates what that enforcement point evaluated and recorded; OPA itself has not signed it. A decision may authorize only this exact actor, act, subject and boundary state. Its maximum lifetime is **5 seconds for dispatch, 30 seconds for other acts**; an earlier `valid_until` applies. Any known relevant state change invalidates it immediately. A ledger commit MUST compare the recorded revision/state under the same serialized boundary; a mismatch requires reevaluation before the act.

OPA `allow` establishes permission under the installed owner policies. It is not a payment mandate, native OAuth grant, asset ownership proof, settlement event or authority to impersonate another agent. Dispatch additionally requires the native authorization evidence selected by the frozen adapter contract; the adapter MUST validate it at the native boundary.

## 5. Bounded evidence retrieval

<a id="rp1-https-get"></a>

A reference is resolved from a verified local object or by HTTPS `GET` of its exact `locator`. A missing locator may be resolved only through the configured authority's authenticated ID-to-locator map; that map never changes the required digest. Use mTLS and the per-service audience from section 2. HTTP retrieval follows [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html); RP1 adds these fixed limits:

| Limit | RP1 value |
|---|---|
| Decoded A2A request size | 1 MiB |
| Embedded records | 64 per message |
| JSON nesting depth | 32 |
| Retrieved semantic/profile JSON object | 2 MiB |
| Native JWS proof wrapper | 3 MiB, including its encoded payload |
| Native payload wrapper | 4 MiB, including its encoded payload |
| Evidence retrieval per semantic decision | 32 requests, 16 MiB total, at most 4 concurrent |
| Network time | 5 seconds to connect, 15 seconds per response, 30 seconds total per decision |
| Redirects, compression | No redirects; require identity content encoding |

Only registry-allowlisted HTTPS origins and path prefixes may be contacted. URI user information, fragment identifiers and credentials in query strings are forbidden. Do not forward credentials across audiences. Administrative configuration may explicitly allow a private origin; an untrusted locator cannot authorize private-network access. A locator is neither permission to retrieve a resource nor a reason to execute its content.

Objects resolved by a common `content_ref` MUST be returned as `application/json`, and that reference always hashes the complete JCS JSON object. The native proof wrapper uses this response media type even though its contained JWS is `application/jose`. Native request/evidence bytes use the immutable JSON wrapper defined in section 10; a native byte digest inside that wrapper does not replace the outer JCS digest. Raw native bytes MUST NOT be interpreted as though they were JCS JSON or assigned the common reference's digest directly. Oversized, malformed, incomplete or unsupported evidence fails the decision rather than being truncated into valid evidence.

Verify ID, media type, complete content digest, proof, authorized issuer, scope, freshness and the specific predicate before relying on an object. A successful HTTP response alone proves none of them. A 404, timeout, rate limit, failed authorization or exhausted retrieval budget means evidence is unavailable; it does not establish absence of a refusal, absence of a transaction, or satisfaction of a promise. A bounded failure may produce a semantic `blocked` receipt; recovery never substitutes a new logical act.

## 6. Durable authority and conflict domains

<a id="rp1-durable-authority"></a>

Each RP1 authority scope has exactly one active **fenced durable writer** and one monotonic event order. Participants and resource owners explicitly select its identity, ledger epoch and scope in policy. The storage product is not prescribed. The required observable operation is an atomic compare-and-append of the command result, affected resource/formation state, operation identity and receipt reference before acknowledgment. Crash recovery MUST return that same committed result. A successor writer MUST demonstrate exclusive fencing and complete recovery of the prior epoch before writing; uncertainty stops writes.

Every authority event is signed `P#rp1-durable-authority/ledger-event` evidence whose body contains exactly `{authority_scope_id, epoch, sequence, previous_event_digest, command_id, request_payload_digest, pre_state_revision, post_state_revision, committed_at, clock_uncertainty_ms, result_refs}`. Epoch is a nonempty identifier; sequence starts at 1; initial state revision is 0; each append increments state revision by exactly 1. Counters are safe integers. The first predecessor is null; later predecessors name the prior complete event digest. No sequence/revision reuse is permitted. This chain makes conflicting claims detectable; it does not prove an authority behaved honestly or that a missing tail never existed.

RP1 authorizes these serialized command classes: admission/accounting; publication/withdrawal; C4 formation; C7 slot binding/dependency observation; principal notice/refusal/status; owner-authorized resource disposition; and C8 preparation/dispatch/reconciliation evidence. They are internal authority commands reached through the existing contracts, not additional public RPC methods. A command's valid signed request, expected state revision, authority and relevant guards are checked before append. State updates and their receipt MUST commit together.

Formation checks and consumes the owner-authorized commitment capacity represented by that same ledger. All negotiations sharing that capacity MUST pass the same boundary. If the owner can simultaneously allocate the same resource outside the ledger, its exclusive-capacity claim is unsupported unless the owner supplies an effective native mechanism binding those allocations to this boundary. Merely observing an external capacity counter is not enough. An RP1 implementation MUST not advertise global atomicity or native resource exclusion it does not have.

Protected preclearance capacity is limited to internal accounting of delegated promise capacity. It MUST NOT create an externally material reservation, charge, secret release or irreversible effect. A native reservation requires its own authorized post-clearance handoff. When a service cannot guarantee native availability without such a reservation, its promise and later handoff retain that condition; the ledger MUST NOT report it as already reserved.

## 7. Replay, bounded contact and retained outcomes

The operation key is exactly `(recipient_scope_id, authenticated issuer_agent_id, operation_id)`. Its immutable value is the C6 **unsigned request digest**, not the full proof-bearing variant. First admission durably records that pair. A verified replay of the same value retrieves its existing receipt chain without reapplying expired offer admission or spending another logical offer allowance. A changed value at the same key produces conflict evidence without replacing the original. A proof-only variant must verify but cannot create another act.

Operation and formation tombstones are retained for the authority scope's lifetime, including terminal declines and conflicts. Required referenced bytes remain recoverable for the reliance/recovery lifetime of their objects. Local cache expiration, restart, key rotation, locator movement or withdrawal cannot make a used identifier fresh. Scope retirement requires an authenticated, explicit retirement policy and preserved historical recovery; it cannot revive old operations under a reused scope ID.

Negotiation uses disclosed C3 admission policy and recipient-issued grants. Initial application remains subject to its bounded proposal allowance and material-revision rule. Clarification questions and answers both consume the disclosed negotiation-traffic allowance; labeling a proposal as clarification cannot bypass quota, recipient close or admission requirements. Genuine status, semantic receipts, exact replay, principal refusal and authorized withdrawal use separately bounded reserved control lanes. Their payloads MUST remain within their defined control purpose; including a new proposal or clarification does not acquire protected admission. Exhausting negotiation traffic MUST NOT consume those control rights. A receipt grants no reply loop. An admitted request permits at most one current response receipt, with subsequent revisions fetched by replay/status rather than unsolicited receipt cascades.

The authority MUST reserve one first-refusal admission and recoverable result per accepted object and required principal. Valid duplicate refusals use the original operation outcome. Authorized refusal/status recovery is limited to **32 requests per minute per principal-control identity**, independently of proposals; excess attempts may be delayed, but cannot erase a first timely admission or disable the accepted object's reserved initial refusal. New accepted objects cannot be finalized if the authority cannot preserve their protected control capacity.

Terminal interaction outcomes remain terminal under C3. A new status evaluation can report current facts; it cannot rewrite an earlier terminal operation. A current authorization may permit recovery without permitting a fresh offer or execution. Transport acknowledgments and missing responses preserve uncertainty until the original operation is recovered.

## 8. Clock, principal notice and recovery accounting

<a id="rp1-principal-inbox"></a>

The authority uses UTC timestamps with millisecond precision, safe-integer millisecond durations and an authenticated time source using [NTPv4](https://www.rfc-editor.org/rfc/rfc5905.html) with [Network Time Security](https://www.rfc-editor.org/rfc/rfc8915.html). NTS authenticates time exchange; it does not by itself establish clock accuracy. The configured service and local clock monitor MUST provide a conservative uncertainty bound. RP1 permits at most **1,000 ms uncertainty** for positive time-based decisions. If this cannot be established, closure and dispatch stop. Local monotonic elapsed time MUST also substantiate the full credited review duration across restarts; a restart with insufficient continuity creates an uncredited interval.

Each principal designates, before candidate adoption, an authenticated HTTPS inbox and at least one separately authorized principal-control agent capable of submitting a C5 `refusal_event` through C6. The inbox origin, exact retrieval URI template, principal authentication mapping, control-agent identities and refusal A2A endpoint are pinned in that principal's policy. The inbox exposes a digest-verified JSON notice bundle by GET. Its body contains exactly `{principal_id, accepted_offer_ref, terms_refs, notice_ref, duration_ms, initial_deadline, effective_deadline, health_evidence_refs, refusal_endpoint, refusal_agent_ids}`. All linked terms needed for review MUST be accessible to that principal. The authority signs the bundle as `P#rp1-principal-inbox/notice-bundle`.

Qualifying notice is durable availability of that exact bundle, its terms and a usable authenticated refusal path at the predesignated inbox, established by the designated notice authority. A queued send, an inbox written for another principal or a negotiating agent's declaration is insufficient. This selected rule does not claim the principal read the notice. A principal requiring actual acknowledgment needs another explicitly selected notice profile; RP1 cannot silently downgrade that requirement.

The authority records the first qualifying notice for each distinct principal. Initially, C5's default remains:

`starts_at = max(finalized_at, verified_notice_time)`

`initial_deadline = starts_at + duration_ms`

`duration_ms` is a positive integer selected by that principal's authenticated policy and adopted before finalization. RP1 supplies no zero-duration waiver and does not choose a shorter competing delegation. Duplicate notices do not restart or shorten the window.

RP1's explicitly adopted outage rule is **credit only verified usable review time**. The same authority journals inbox/terms/refusal health and clock continuity, using evidence from its designated service monitors. Health evidence body is `{principal_id, accepted_offer_ref, interval_start, interval_end, state, service_evidence_refs}`, with state `usable`, `unusable` or `unknown`; it is signed as `P#rp1-principal-inbox/health-interval`. Intervals are half-open, ordered, nonoverlapping and account for every instant from the selected start through the proposed closure. `usable` requires accessible required terms, an accepting protected refusal path and valid clock/order for the entire interval. Monitoring silence, a gap, an unresolved conflicting report or lost restart continuity is `unknown`, not usable. A single success probe does not prove the whole preceding interval.

Intervals marked `unusable` or `unknown` do not consume the principal's review duration. The adopted effective deadline is `initial_deadline + total_nonusable_duration_before_closure`, where overlapping outage reports are unioned before summation. The authority MUST also verify credited monotonic usable duration is at least `duration_ms`. Until all relevant intervals and queued refusal admissions are reconciled, closure remains pending/unresolved. Extensions and their evidence MUST be made available in the inbox; none may shorten a published deadline. New terms require new formation, not outage bookkeeping. This policy protects service availability at the designated boundary; it does not attest every principal device or Internet route was online.

A refusal's timeliness uses its authority-admitted time, not its sender timestamp or eventual verification completion. The authenticated C6 ingress first durably records the target, operation, peer and conservative admission-time interval; complete validity is then established under the same ledger. Closure waits for every pending admission that could be timely. A valid event whose admission interval overlaps the deadline is treated as timely; uncertainty cannot subtract the principal's right. Equality is timely. Closure requires the authority's current time **lower bound** strictly after the effective deadline, sufficient credited duration, complete admission reconciliation and no valid timely refusal.

All component principals and all relevant dependency principals must meet this rule before externally effective handoff. Missing notice can leave a window unstarted indefinitely. A valid refusal is absorbing for its exact accepted object; replay, re-signing, later notice or an agent's fresh assent cannot revive it. This is delegated principal recovery, not a human signature or a native execution authorization.

## 9. Composition and current evidence

This section applies only when `composition` is enabled. It does not add a plan or orchestrator to the default bilateral path. RP1 rejects a C7 plan with cycles in the relevant stage/dependency graph before adoption. Plan declarations, immutable slot bindings, each bilateral adoption and each originator/coordinator remain separate facts. Membership is not assent. All ledger-governed formations and shared resource selections in a composed conflict domain MUST use section 6's one accepted authority; RP1 supplies no cross-authority commit algorithm.

Before a transition, the authority resolves exact candidate bindings, accepted objects and required dependency evidence from its current complete state. Required external observations may supplement that state only under a pinned predicate and authorized issuer/finality rule. `unknown`, stale, refused, forked or unavailable required evidence cannot be converted into readiness. All conditions are checked at their adopted stage; a formation prerequisite does not replace a handoff prerequisite.

Resource release, cancellation and compensation are distinct owner-authorized actions. A refused prerequisite blocks dependent eligibility as adopted; it does not itself cancel a native transaction or release another owner's resource. Partial formation, failed dependencies and in-doubt external effects remain individually attributable. RP1 does not infer all-or-nothing settlement from the common ledger.

## 10. Frozen preparation and native handoff

<a id="rp1-handoff-adapter"></a>

This section applies only when `adapter-handoff` and its `lifecycle-evidence` dependency are enabled. Use C8's `handoff_request`, `prepared_handoff`, `handoff_receipt` and `lifecycle_evidence` records. The interaction purposes are `prepare_handoff`, `dispatch_handoff` and `reconcile_handoff`; all name the **same exact handoff request** in `subject_ref`. No custom public RPC is added. An adapter contract is pinned in `adapter_profile_uri` plus its immutable policy/evidence reference; merely naming MCP, AP2, x402 or a payment service does not instantiate that contract. A bilateral-only endpoint may form agreements and expose principal recovery status; it MUST NOT advertise RP1 native dispatch support.

The C8 semantic key is:

```text
handoff_key = "sha256:" + lowercase_hex(SHA256(UTF8(JCS({
  accepted_issuer_agent_id,
  accepted_offer_id,
  accepted_unsigned_payload_digest,
  promiser_agent_id,
  promise_id,
  action_instance
}))))
```

Obtain the accepted identity and unsigned digest through verified C6 semantic identity. The exact adopted full `agreement_ref` remains in the request. `action_instance` contains the adopted `type_uri` and canonical `parameters`; its semantics and cardinality MUST match the promised permission. A random new instance identifier is not authorization for another effect. The key excludes handoff ID, proof variant, adapter, profile and carrier, so rerouting cannot multiply permission.

The common handoff gate ledger pins one selected adapter, exact `prepared_handoff` reference and native operation key to this key. `native_operation_key` is exactly `"app-rp1-" + the 64 lowercase hex characters of handoff_key`. An adapter unable to preserve that correlation in its native system cannot support externally effective RP1 dispatch. A different adapter or materially changed translation at an existing key is blocked. A replacement requires a fresh adopted candidate and explicit attributable disposition of the prior effect; a new candidate MUST NOT bypass a still-unknown prior effect.

| Boundary operation | Required behavior |
|---|---|
| **Prepare** | Authenticate request and authority; verify the exact adopted action; perform only separately authorized read-only metadata access and local validation; freeze translation and requirements in `prepared_handoff`; return a `prepare` receipt. No charge, native transaction creation, secret release, externally material reservation or other external effect. |
| **Dispatch** | Read the pinned preparation; validate current authority, all relevant principal clearances, adopted dependencies and native authorization; serialize the gate; durably record intent to dispatch the stable key; invoke the native adapter at most once for that key; preserve the actual outcome/evidence. |
| **Reconcile** | Read the existing ledger and native operation by the pinned key under current read authority; update attributable observations. It MUST NOT initiate, retry, replace or compensate the native action. |

`prepared_handoff.body` is exactly C8's `{handoff_ref, handoff_key, adapter_profile_uri, native_request_ref, native_operation_key, effect_class, authorization_requirement_refs, reconciliation_profile_ref}`. `native_request_ref` identifies an immutable JSON wrapper containing exactly `{id, media_type, payload_encoding, payload, payload_digest}`. Its `id` equals the reference ID; `media_type` describes the native payload; `payload_encoding` is exactly `base64url`; `payload` contains the unpadded base64url encoding of the exact native bytes; and `payload_digest` is `"sha256:" + lowercase_hex(SHA256(decoded_payload_bytes))`. The common `native_request_ref.digest` instead hashes JCS of the **whole wrapper**, as every C6 content reference does. Both checks are required. Decoding MUST preserve bytes without parsing, normalizing or reserializing the native payload. Native-specific signatures, digests or credentials remain in their original native representation inside those bytes and are verified separately under the pinned adapter contract.

This wrapper also carries native evidence when a C8 evidence reference must preserve opaque bytes. Its payload may be JSON or another native representation, but the outer common-reference digest always covers JCS JSON. The selected adapter contract must define a complete request representation covering the native target, operation and material parameters; a body-only wrapper cannot silently leave material request fields mutable. APP treats that payload as external content and does not copy AP2, MCP or payment schemas into its core. `authorization_requirement_refs` enumerate every required native authority check. The reconciliation profile identifies how to locate, authenticate and interpret the native outcome by the same operation key, including finality and absence rules. A missing requirement or unsupported native correlation blocks preparation.

Preparation does not authorize dispatch. At dispatch, the adapter verifies that its actual native request equals the frozen request, that the current authorization covers that exact action/resource/amount/audience where applicable, and that native evidence is sufficiently fresh. The PEP binds this evidence to its OPA decision and the same ledger revision. The native invocation must begin before that decision's `valid_until` and within its 5-second maximum lifetime; an expired decision cannot be queued for later execution. A delegation to negotiate or principal-window closure alone does not satisfy these native checks.

The authority writes `dispatch_attempt_started` and the pinned native key durably **before** any externally effective call can leave the adapter. Once that marker exists, no second effective invocation is permitted for that key, including after timeout, crash, lost acknowledgment or another carrier request. Repeated C8 requests recover the original phase outcome or reconcile it. An uncertain crash between marker and send sacrifices availability: it remains `in_doubt` until authoritative evidence resolves it. A missing native record is not proof that no effect occurred unless the pinned native reconciliation contract provides that exact final absence guarantee. Even a resolved absence does not trigger an automatic second Dispatch in RP1.

An adapter must supply a native mechanism supporting stable correlation and authenticated lookup, and must prevent an internal retry from producing another external effect. A service without those capabilities is unsupported for externally effective RP1 dispatch. This is at-most-one authorized dispatch behavior plus recoverable evidence, not a claim that an arbitrary external service supplies exactly-once execution or atomic payment.

`handoff_receipt` binds the exact request, key, phase, revision/predecessor, prepared plan, authorization decision, gate evidence and native evidence according to C8. `dispatched` establishes the evidenced native submission fact only. A transport ACK, native task completion, reported fulfillment, assessment and settlement are not interchangeable outcomes.

## 11. Lifecycle evidence and interpretation

This section applies when `lifecycle-evidence` is enabled. An RP1 adapter or other authorized reporter emits C8 `lifecycle_evidence` with the appropriate category: `fulfillment`, `assessment`, `native_execution`, `settlement` or `reservation_disposition`. Each claim retains its typed value, exact agreement/action/handoff subject, source references, authenticated reporting role, observation time and the policy governing verification and finality. A fact may be reported before it is assessed or final; its category MUST NOT silently upgrade that fact.

Before using a claim, the relying party verifies the exact type's predicate and permitted issuer. Provider self-report can establish an attributable fulfillment claim; independent acceptance requires the selected assessment authority. A native payment-submission record does not establish settlement. Reservation release requires owner/native evidence of release, not a negotiation close, timer or failed dependency. A verified negative or in-doubt result remains visible; later unavailable evidence cannot make it positive.

RP1 does not select a live payment rail. A future native adapter must pin the actual existing mechanism, its authorization/lookup/finality rules and any additional protected data handling before it can be admitted. Unsupported native execution is `blocked`; the generic contract is not advertised as a working integration.

## 12. Observable guarantees and remaining trust

| Boundary | What RP1 can require and verify | What remains a trust dependency |
|---|---|---|
| Parsing, signatures, references | Exact bytes, scopes, digests, issuer/key binding and profile rejection | Correct cryptographic implementation and trusted registry administration |
| Authority decisions | Owner-approved policy, exact input/result evidence, serialized revision comparison | Correct approved Rego policy, honest resource-owner delegation and enforcement |
| Formation/replay | Stable operation identities, durable results, one conflict authority, detected conflicting signed histories | Exclusive fencing, durable storage and completeness of authority state |
| Principal recovery | Exact notice, protected refusal admission, evidence-backed credited time, no dispatch before clearance | Honest designated notice/clock/health authorities and principal's chosen channel |
| Native boundary | Frozen request, fresh native authority, one journaled dispatch key, correlated evidence | Native authorization enforcement, idempotency/correlation, outcome truth and finality |

The boundary assessment should challenge these observable contracts: proof-scope substitution; request replay with altered bytes; competing resource formations; incompatible authorities; missing notice and unknown outage intervals; refusal at the deadline; stale policy at dispatch; rerouting the same effect to another adapter; crash after the dispatch marker; false native absence; and fulfillment evidence mislabeled as settlement. The [validation record](../validation.md) and [conformance map](../conformance.md) distinguish executable coverage from the remaining proposed targets. A profile requirement alone is not evidence that its implementation has passed an assessment.
