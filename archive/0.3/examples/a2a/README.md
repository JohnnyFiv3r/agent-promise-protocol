# A2A 1.0 / Bazaar 0.3 construction templates

These files specify the native wire shape. They are **templates, not schema-valid signed fixtures**: angle-bracket strings identify values the author must supply. No digest, signature, proof suite, retrieval profile, working endpoint or authenticated integration is asserted. The example.org locators are documentation addresses. The selected proof suite must authenticate the completed records before any submission.

- [Agent Card fragment](agent-card-fragment.json) is merged into a complete native Agent Card, including its normal identity, skills, media modes and security declarations.
- [SendMessage request](interaction-send-message.json) invokes one `submit_record` operation. Its empty `records` list demonstrates locating the complete subject through the declared retrieval profile. Alternatively, embed the complete subject and required supporting JSON records in that list. Merely embedding an additional record does not submit another act.

The extension's exact identifier is:

```text
https://github.com/JohnnyFiv3r/agent-bazaar/blob/main/protocol-architecture.md#v03
```

The request uses native credentials from the receiving Agent Card and these headers:

```http
Content-Type: application/json
A2A-Version: 1.0
A2A-Extensions: https://github.com/JohnnyFiv3r/agent-bazaar/blob/main/protocol-architecture.md#v03
```

The server echoes the extension header and returns a native JSON-RPC response whose `result.message` has `messageId`, `role: "ROLE_AGENT"`, its accepted `contextId`, the extension URI in `extensions`, and one part:

```text
{
  mediaType: "application/json",
  data: {
    bazaar: <complete authenticated interaction_receipt>,
    records: [<complete referenced result/evidence records>]
  }
}
```

This is shape notation. The receipt authenticates the exact `request_ref`, `operation_id`, `recipient_scope_id`, `revision`, `previous_receipt_digest`, `outcome`, `reason_code`, `result_refs` and `evidence_refs`, as defined in the [interaction schema](../../schemas/interaction.schema.json). It does not become an adoption or accepted offer merely because the HTTP response succeeds.

To request formation or recover a coordinator-initiated outcome, use `purpose: "finalize_candidate"`, reference the exact candidate, and address its coordinator under a policy that permits finalization. Its applied receipt returns the accepted object; it cannot produce a second object for the same formation key.

To query accepted-object status, use `purpose: "query_status"`, reference the exact accepted object in `subject_ref`, and supply admission for the status path. To reconcile an uncertain earlier operation, replay that original signed request with the same A2A `messageId` and Bazaar `operation_id`; do not change it into a status query or create a replacement operation. The JSON-RPC correlation `id` may change between transport attempts.

`ROLE_USER` and `ROLE_AGENT` describe client/server direction. They do not identify buyer/provider or promise polarity. No native task is required for an immediate receipt. When a native task exists, its task/context identifiers remain local to the endpoint/tenant and do not replace Bazaar operation, negotiation or accepted-object identity.

[C6 — A2A invocation and portable evidence](../../contracts/06-a2a-evidence.md) specifies activation failure, record identity, response allowance and replay behavior. A record pasted in ordinary chat is not an invocation of this interface.
