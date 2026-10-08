# C6 — A2A invocation and portable evidence

**ABP 0.4-draft.** This contract specifies how an agent invokes Bazaar through A2A and how another agent verifies the resulting evidence. The [core contract](../contract.md) determines which semantic transition is permitted. This binding neither creates a transport nor changes an A2A task state.

## 1. Version and extension identity

The normative carrier for this binding is **A2A specification 1.0.0, JSON-RPC over HTTPS**, using wire version `1.0`. The extension identifier is:

```text
https://github.com/JohnnyFiv3r/agent-bazaar/blob/main/protocol-architecture.md#v04
```

This URI identifies the `abp/0.4-draft` contract. It is compared as an exact identifier; dereferencing a mutable GitHub page is not version negotiation or proof. Participants MUST use their understood, pinned contract and schemas. A breaking change requires a distinct identifier and profile. The identifier does not claim that an endpoint, proof suite or integration has been deployed.

A2A defines `SendMessage`, message data parts, direct message/task responses and endpoint-local context/task identifiers. This binding narrows those native structures without adding an RPC or enum value. [Pinned A2A 1.0.0 definition](https://raw.githubusercontent.com/a2aproject/A2A/v1.0.0/specification/a2a.proto).

## 2. Advertisement and activation

The Agent Card MUST advertise this URI in `capabilities.extensions`. An endpoint that requires Bazaar interpretation MUST set that extension's `required` flag to `true`. Its `supportedInterfaces` entry MUST declare `protocolBinding: "JSONRPC"` and `protocolVersion: "1.0"` for this binding.

The extension's `params` object has these fields:

| Field | Type and requirement |
|---|---|
| `profiles` | Required array of distinct semantic-profile strings; includes `abp/0.4-draft`. |
| `supported_features` | Required array of distinct understood feature strings; includes `bilateral`. Optional features are `composition`, `adapter-handoff` and `lifecycle-evidence`; `adapter-handoff` also requires `lifecycle-evidence`. |
| `recipientScopeId` | Required nonempty string identifying the recipient's shared admission/accounting scope. It does not confer admission. |
| `admissionPolicyRef` | Required Bazaar content reference to the current disclosed admission-policy document. Its authority and freshness must be verified independently. |
| `proofProfiles` | Required array of distinct URI strings identifying understood existing proof profiles. An empty array advertises no ability to process authenticated Bazaar acts. |
| `evidenceRetrievalProfiles` | Required array of distinct URI strings identifying understood evidence-retrieval profiles. Each selected profile defines authentication, request/response form, content types, bounds and integrity checks. |
| `referenceProfileUri`, `profileManifestRef` | Optional paired fields: an understood reference-profile URI and exact content reference to its authenticated deployment manifest. Both are required when advertising RP1. Neither may appear alone. |

Additional advertisement fields require a declared understood extension. A cached card does not override newer known policy or authority status. Credentials use the endpoint's native A2A security declarations; none of these fields is a credential.

The baseline feature is `bilateral`; it requires no transaction plan or adapter. Feature advertisement establishes claimed support only, never admission, delegation, native authority or successful implementation. Before a dependent transition, including candidate adoption, each required participant MUST explicitly support its effective required features under a verified compatible profile. The harness checks the intersection of that support, not merely the receiver's advertisement. [RP1](../profiles/reference-profile.md) supplies one fixed preset and authenticated realm manifest; mechanisms are not renegotiated per transaction.

For each request the caller MUST send `A2A-Version: 1.0` and include the exact Bazaar URI in `A2A-Extensions`. It MUST also activate any required dependencies that are themselves A2A extensions. The `Message.extensions` field marks the data carried by that message; it does not replace request activation.

A conforming server MUST acknowledge activation by including the URI in the response's `A2A-Extensions` header. A caller MUST NOT treat a response without that acknowledgment as an authenticated Bazaar outcome. It preserves an unknown operation outcome and reconciles the original operation; it MUST NOT manufacture a fresh operation to escape uncertainty. Acknowledgment alone establishes no semantic success.

A Bazaar-required endpoint receiving no activation returns the native `ExtensionSupportRequiredError`. Unsupported A2A versions use `VersionNotSupportedError`. A server that does not implement Bazaar may ignore an unknown extension under native A2A rules; the caller's required acknowledgment prevents silent fallback. Core A2A recommends an activation response header; this contract makes it mandatory for this binding. [A2A extension declaration and activation](https://a2a-protocol.org/latest/topics/extensions/).

## 3. One explicit operation per message

A Bazaar request is an A2A `SendMessage` whose message carries exactly one Bazaar data part with this shape:

```text
Part = {
  mediaType: "application/json",
  data: {
    bazaar: InteractionRequest | InteractionReceipt,
    records: JSONRecord[]
  }
}
```

This is shape notation, not a complete request. `bazaar` and `records` are the only members of this data object. `records` is present and may be empty. The A2A part has no legacy `kind: "data"` discriminator. For this binding, the message contains only this part. Human-readable explanations belong in the corresponding typed record fields; an extra text part cannot modify an operation.

`InteractionRequest` and `InteractionReceipt` MUST satisfy [the interaction schema](../schemas/interaction.schema.json), including `profile: "abp/0.4-draft"`, the appropriate `kind`, issuer, record ID, creation time, `required_features` and proof references. Every semantic record and interaction MUST carry a signed, nonempty, duplicate-free `required_features` array containing `bilateral`. A request body's fields are:

| Field | Binding rule |
|---|---|
| `operation_id` | Stable logical operation identity across retries. |
| `recipient_agent_id` | Exact intended recipient, checked against the receiving agent identity. |
| `recipient_scope_id` | The declared recipient accounting scope, checked independently of URL, tenant and transport IDs. |
| `purpose` | Baseline: `submit_record`, `finalize_candidate` or `query_status`. With `adapter-handoff`: `prepare_handoff`, `dispatch_handoff` or `reconcile_handoff`. |
| `subject_ref` | Exact content reference to the subject appropriate to the selected purpose; each handoff purpose names the same exact `handoff_request`. |
| `admission_basis_ref` | Exact reference to the applicable publication permission, admission policy, recipient-issued grant or supported native admission evidence. |

The body is authenticated as part of the envelope. A relay cannot alter the recipient, scope, subject or purpose. Submission of another issuer's record preserves that record's proof and is allowed only under the governing admission/delegation rules; the relaying caller does not become its promiser.

`submit_record` asks the recipient to apply the subject's defined Bazaar transition. An `admission_grant`, `clarification` or `negotiation_close` uses the same operation. Its subject MUST be a semantic record admitted by the policy, never another interaction envelope or a receipt-of-receipt. `finalize_candidate` asks the declared coordinator to form or recover the exact candidate's accepted outcome under C4. An applied receipt returns that accepted object; pending is not acceptance. `query_status` asks for the authoritative current status of its exact accepted-offer subject; it grants no permission to revise it. These are the three baseline purposes.

The three optional handoff purposes invoke [C8](08-adapter-boundary.md)'s side-effect-free preparation, guarded dispatch and read-only reconciliation. All retain one exact `handoff_request` subject and its semantic effect identity. They require `adapter-handoff` and `lifecycle-evidence`; they add no A2A RPC or task state. An applied interaction receipt proves processing of that phase request, not native execution or settlement. The referenced `prepared_handoff`, `handoff_receipt` and evidence supply their own attributable facts.

Effective feature requirements are the union of the signed declaration and the features implied by the record kind, fields, purpose, resolved subject and evidence needed for the transition. In particular, a `transaction_plan`, `composition_binding` or candidate `composition` field requires `composition`; handoff records/purposes require `adapter-handoff` and `lifecycle-evidence`; a `lifecycle_evidence` record requires `lifecycle-evidence`. A baseline candidate's policy-filled `handoff_rules` alone does not require an adapter. Omitting an implied feature is invalid and MUST block application; a verifier MUST NOT silently amend signed bytes or treat the omission as permission to downgrade. Unknown or unsupported effective requirements block the dependent transition before adoption or reliance. A bounded failure receipt may identify the unsupported requirement without claiming to have interpreted or applied it.

Only the record selected by `subject_ref` is submitted for application. Other entries in `records` supply referenced terms, policies or evidence. Inclusion in the batch MUST NOT independently issue, adopt or apply those records. In particular, an embedded candidate does not issue its counterpart's promises, and evidence returned with a receipt does not admit an unsolicited counteroffer. A new counteroffer or clarification answer requires its own admitted `submit_record` request.

Merely pasting a record in ordinary chat, attaching a JSON file, showing an intent in discovery or carrying a proof in another message does not invoke this interface. Invocation requires the active binding, explicit interaction envelope, valid authority and recipient admission.

## 4. Record identity and materialization

Each embedded record MUST be a complete JSON object. An embedded signed record includes its full proof-reference array. The receiver resolves the subject and required references from this batch, already verified local content, or a locator under a selected evidence-retrieval profile. Unavailable or unverifiable required content blocks its dependent transition.

The canonical-content rule is RFC 8785 JCS, UTF-8 and SHA-256. A `content_ref.digest` identifies the complete canonical referenced object, including its proof references when present. A proof's `signed_payload_digest` instead identifies that record with its top-level `proofs` member removed. These are different digests and MUST NOT be substituted for one another.

Embedding JSON preserves canonical content, not incidental whitespace, member order or a transport's original byte serialization. Implementations MUST reject duplicate member names before lossy parsing and reject values outside the canonical JSON profile. They MUST NOT round numbers, omit fields, change explicit nulls or rewrite native proof material to make a digest match. Native signatures and credentials keep their original native bytes at their referenced location and use their selected verifier.

The common `content_ref` always addresses a complete JCS JSON object. Opaque native requests, proofs or evidence therefore require an immutable JSON wrapper that preserves their original bytes and encoding under the selected profile. The outer reference digest hashes that whole wrapper; any native/raw-byte digest inside it is a different check. Raw native bytes MUST NOT be treated as JCS or substituted for the outer digest. RP1 specifies the native payload wrapper and its exact byte-preserving encoding; Bazaar does not reinterpret its contents as a core payment or tool schema.

The semantic record identity is `(authenticated issuer_agent_id, id)`. The first admissible record pins its unsigned payload digest. The receiver MUST reject a later object claiming that identity with different unsigned content. Variants differing only in top-level proof references have distinct full content digests and MUST be verified separately; they do not create another semantic act or replace an exact reference already adopted. Required original proof variants MUST remain retrievable. A batch containing several variants must resolve each reference by its full digest, never by record ID alone.

Records outside the dependency closure of the subject, result or required evidence MUST NOT be processed as hidden operations. All embedded bytes count toward the applicable admission/response limits, including duplicates and support records. Locator retrieval follows the selected profile's access and size rules; a URI alone grants no access.

Optional `Message.metadata[extensionURI]` may carry `interaction_ref`, a content reference to the embedded envelope, and `subject_ref`. They are indexing hints: if present, they MUST match the authenticated data; they cannot supply or override missing fields. The same rule applies to artifact metadata.

## 5. Request, response and receipt

The JSON-RPC method is `SendMessage`. Its `params.message.messageId` MUST be retained when replaying the same interaction request. The JSON-RPC request `id` correlates that transport call and may differ on replay. `messageId` is not the Bazaar operation identity: deduplication uses the recipient scope, authenticated issuer and `operation_id`, together with the interaction request's unsigned payload digest under C3. A saved receipt retains the full `request_ref` of the first admitted proof variant; a separately verified equivalent variant retrieves that same outcome and never changes the saved reference.

A new message uses native `ROLE_USER` for client-to-server direction. A direct response uses `result.message` and `ROLE_AGENT`, with the server's `contextId`. These roles never determine buyer/provider, principal/agent or promise polarity. An initial caller need not invent a task or context ID. Where native tasks are used, the caller retains the server's accepted identifiers and native operations. [A2A message and response types](https://raw.githubusercontent.com/a2aproject/A2A/v1.0.0/specification/a2a.proto).

For this profile, `SendMessage` MUST return a direct semantic receipt message, rather than requiring a long-lived native task to represent the negotiation. An operation awaiting resolution returns the governing `pending` receipt after its durable operation identity is recorded. Native tasks may still support other communication and evidence services; they are not the receipt. The response carries an `interaction_receipt` in `data.bazaar`, with any referenced result records in `data.records`. A receipt MUST bind the exact `request_ref`, `operation_id` and `recipient_scope_id`. Its `revision` and `previous_receipt_digest` describe the durable receipt chain. Its `outcome` is `pending`, `applied`, `declined`, `blocked` or `conflict`; `reason_code`, `result_refs` and `evidence_refs` have the meanings defined by the governing interaction contract.

`applied` means only that the requested subject's defined operation was applied. An applied offer submission is not the receiver's adoption. An applied adoption submission is not finalization. A `query_status` result does not itself alter accepted-object status. Only the attributable result records establish those later facts. A `pending` receipt never authorizes a second operation or implies success through silence.

An HTTP success, JSON-RPC response, extension acknowledgment, task submission, stream event or native task completion is **not** a Bazaar semantic receipt. A receipt is itself neither an offer nor a promise adoption. Native `CancelTask` cancels native task processing where supported; it cannot substitute for `negotiation_close`, withdrawal or principal refusal.

Calling this binding admits one immediate, bounded response to the caller under the disclosed admission policy's response allowance. The server MUST remain within that allowance, using references when full supporting records do not fit. A request does not authorize an unsolicited stream of receipts, messages or offers. There are no receipts of receipts and no automatic acknowledgment loops. Genuine status/replay, principal refusal and authorized withdrawal retain their separately admitted control paths. Clarification questions and answers consume negotiation traffic; wrapping them as control messages cannot bypass exhausted budgets.

## 6. Errors, replay and unknown outcomes

Authentication, unsupported A2A capability/version, malformed native messages and other native protocol failures retain their A2A errors. A syntactically recognizable authenticated Bazaar request whose semantic transition cannot be applied receives the applicable typed Bazaar receipt. Unsupported action, policy, proof or required extension meaning is a semantic block, not permission to drop that meaning and continue. When identity or parsing fails before a safe receipt can be formed, native failure is sufficient; no model-generated reply is required.

The receiver MUST durably bind admission and outcome to the operation before acknowledging application. Exact replay retrieves that operation's current durable receipt, including a later valid revision where the governing receipt rules permit progress. Replay MUST NOT reapply the semantic act or consume a fresh logical offer allowance. Native ingress and retrieval limits still apply. Reusing an operation identity with changed request content is a conflict.

The requester obtains an uncertain operation's outcome by replaying the same signed request. `query_status` is for accepted-object status, not a second name for resubmitting an act. If formation was coordinator-initiated or its accepted reference is unknown, an admitted `finalize_candidate` request uses the exact candidate to recover the same C4 formation result. It cannot create another result for that formation key. Response loss never justifies inventing a new operation ID to escape an uncertain operation. If a receipt references unavailable evidence, the requester preserves the unresolved observation and retrieves the exact evidence through its selected locator profile.

A2A message history or streaming alone is insufficient as the durable outcome store. The implementation MUST retain required receipts and records in retrievable native artifacts or an authenticated repository for the governing retention horizon. A2A's send-message idempotency is optional; this contract requires operation-level deduplication for Bazaar. [A2A operation semantics and message persistence](https://a2a-protocol.org/v1.0.0/specification/).

## 7. Evidence and semantic compatibility

Both the interaction envelope and each authority-bearing subject/result require the proofs selected by their governing policy. Verifiers MUST check the native suite, verification method, issuer, signed payload digest and scope against the exact record. Transport authentication and a signed Agent Card do not authenticate every later record or delegate power to issue another agent's promises.

Required semantics include effective `required_features`, explicitly listed extensions and any action, qualification, admission, privacy, selection, commercial, status or proof profile necessary to interpret the act. A receiver MUST NOT apply a dependent transition while one is unsupported or unresolved. An unknown optional extension can be preserved without interpretation only when ignoring it changes none of the act's promises, admission, authority, selected terms, refusal rights or effect eligibility. Unknown content cannot become an implicit permission.

Required A2A extension dependencies are activated through A2A. Domain semantic/profile URIs are interpreted under Bazaar's required-semantics rules; merely listing them in an HTTP header does not implement them. No core A2A enum or field is extended by an undeclared property.

Core semantics permit different understood concrete profiles. [RP1](../profiles/reference-profile.md) selects a complete default, including its proof and retrieval mechanisms; it is an authored design, not a deployed verifier, credential or endpoint. [Wire examples](../examples/a2a/README.md) remain construction templates. [Boundary tests](../tests/PROPOSED.md) are proposals for later verification. Neither establishes authenticated interoperability or downstream payment compatibility.
