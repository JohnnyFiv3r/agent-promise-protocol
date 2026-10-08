# Original Agent Bazaar reference policy. No comparator/framework implementation.
# Load only administrator-verified owner-approved data with this policy.
package agent_bazaar.rp1

import rego.v1

now_ms := time.parse_rfc3339_ns(input.clock.now) / 1000000

kind := object.get(input.subject, "kind", object.get(input.subject, "type_uri", ""))

grant_matches(grant) if {
    grant.agent_id == input.actor.agent_id
    grant.principal_id == input.actor.principal_id
    input.act in grant.acts
    kind in grant.subject_kinds
    grant.authority_scope_id == input.authority_scope_id
    not object.get(grant, "revoked", false)
    now_ms >= object.get(grant, "not_before_ms", 0)
    now_ms < object.get(grant, "valid_until_ms", 9007199254740991)
    input.subject.id in object.get(grant, "subject_ids", [input.subject.id])
    input.recipient_scope_id in object.get(grant, "recipient_scope_ids", [input.recipient_scope_id])
}

dispatch_ready if input.act != "dispatch_handoff"
dispatch_ready if {
    input.act == "dispatch_handoff"
    count(input.native_authorization_refs) > 0
    count(input.clearance_refs) > 0
}

default allowed := false
allowed if {
    input.profile == "abp-rp1/0.1-draft"
    input.policy_bundle_ref == data.agent_bazaar_policy.policy_bundle_ref
    input.policy_data_ref == data.agent_bazaar_policy.policy_data_ref
    input.clock.uncertainty_ms >= 0
    input.clock.uncertainty_ms <= 1000
    count(input.authority_refs) > 0
    some grant in data.agent_bazaar_grants
    grant_matches(grant)
    dispatch_ready
}

lifetime_ms := 5000 if input.act == "dispatch_handoff"
else := 30000

reasons := ["ok"] if allowed
else := ["policy_denied"]

expiration_ms := min({now_ms + lifetime_ms} | {object.get(grant, "valid_until_ms", 9007199254740991) |
    some grant in data.agent_bazaar_grants
    grant_matches(grant)
})

# JSON encoding protects all backslashes in JSON strings. A literal NUL cannot
# occur in encoded JSON. Temporarily protect escaped backslashes before undoing
# Go's optional HTML/JavaScript escaping, then restore them. This preserves a
# user's literal "\\u003c" text as distinct from "<".
jcs_compatible_json := replace(strings.replace_n({
    "\\u003c": "<", "\\u003e": ">", "\\u0026": "&",
    "\\u2028": "\u2028", "\\u2029": "\u2029",
}, replace(json.marshal(input), "\\\\", "\u0000")), "\u0000", "\\\\")

# The PEP independently recomputes RFC8785. Canonical request numeric lexemes
# survive OPA parsing. OPA sorts keys by codepoint rather than UTF16; a mixed
# supplementary/BMP key ordering mismatch therefore safely blocks authorization.
authorize := {
    "allow": allowed,
    "reason_codes": reasons,
    "input_digest": sprintf("sha256:%s", [crypto.sha256(jcs_compatible_json)]),
    "policy_bundle_ref": input.policy_bundle_ref,
    "policy_data_ref": input.policy_data_ref,
    "authority_revision": input.authority_revision,
    "boundary_state_digest": input.boundary_state_digest,
    "valid_until": time.format([expiration_ms * 1000000, "UTC", "2006-01-02T15:04:05.000Z"]),
}
