# Reference authorization policy

`rp1.rego` is an original Rego v1 policy for **Open Policy Agent 1.21.1**. It
matches explicit approved grants by agent, principal, act, subject kind and
authority scope. Optional subject IDs, recipient scopes, validity intervals and
revocation further restrict a grant. Every grant requires authority evidence;
dispatch also requires clearance and native authorization references. These
references must already have been verified by the enforcement point. A list of
references does not prove the underlying predicates.

The administrator must authenticate owner approval of the exact policy bundle,
data snapshot and delegation before installing them. The reference service data
has `agent_promise_protocol_policy` containing `policy_bundle_ref` and `policy_data_ref`,
plus `agent_promise_protocol_grants`, an array of grants. A minimal grant shape is:

```json
{
  "agent_id": "agent:example",
  "principal_id": "principal:example",
  "acts": ["submit_record"],
  "subject_kinds": ["offer"],
  "authority_scope_id": "authority:example"
}
```

The optional fields are `subject_ids`, `recipient_scope_ids`, `not_before_ms`,
`valid_until_ms` and `revoked`. Omitting either ID restriction permits all IDs
within the other explicitly granted dimensions. Omitting time bounds means no
additional grant-specific expiry; policy decisions still last at most 30 seconds
or 5 seconds for dispatch. `TestPolicy` implements this fixture policy in process
only when explicitly selected; `OPAClient` never falls back to it.

Run an approved local OPA service with the matching CA, server certificate and
private key:

```sh
.tools/opa run --server --addr 127.0.0.1:8181 --authentication=tls \
  --min-tls-version=1.3 --tls-ca-cert-file ca.pem \
  --tls-cert-file server.pem --tls-private-key-file server.key \
  policies/rp1.rego approved-data.json
```

`OPAClient` posts the exact RP1 input to
`/v1/data/agent_promise_protocol/rp1/authorize`. It validates TLS 1.3, the configured CA,
server hostname and enrolled leaf digest before sending request bytes. It checks
all result fields, reason codes, exact input digest, approved policy references,
ledger revision, state digest and lifetime. The harness must compare the decision
to current serialized state immediately before committing the authorized act.
`decision_evidence` signs the enforcement point's recorded input/result; it does
not represent an OPA signature. A verified denial raises `ProtocolError` with its
result in `policy_result`, allowing the caller to preserve denial evidence.

## Canonical representation limit

The request is serialized with the `rfc8785` library. OPA preserves its numeric
lexemes. The Rego policy reverses only Go's optional HTML/JavaScript string
escaping, protecting literal escaped backslashes before replacement. Tests cover
HTML characters, ordinary Unicode, supplementary characters in string values,
line/paragraph separators, literal backslash-u text, and JCS number vectors.

OPA sorts object member names by Unicode codepoint, while JCS requires UTF-16
ordering. An object mixing certain supplementary-plane and BMP member names can
therefore produce a different digest. The enforcement point detects this and
**blocks the decision**. It never changes the required digest or treats the
decision as authorized. The current reference policy does not claim support for
every JCS-valid arbitrary object-key vocabulary.

## Local trust and verification limits

`Registry.register` and `Registry.enroll` are trusted administrative configuration
APIs. No incoming Agent Card, `kid`, JWK, certificate, record or locator enrolls an
identity. Current key revocation is checked separately from historical verification
at a preserved admission time. Compromise uncertainty blocks historical reliance.
Keep the actual historical registry snapshot and admission evidence; the timestamp
argument does not establish that history by itself. This module does not implement
network distribution or monotonic installation of signed registry revisions.

The runtime also understands three explicitly named evidence documents, exposed as
`RUNTIME_PROFILE_TYPES`: `rp1-principal-inbox/availability` records designated inbox
availability; `rp1-durable-authority/recovery-observation` records the authority's
current principal recovery observation; `rp1-durable-authority/operation-outcome`
records a durable operation outcome. Each is appended to the exact profile URI as
a fragment. The harness supplies and checks its meaning. Additional document
types require explicit signer and verifier configuration; a valid signature alone
cannot teach the runtime a new predicate.

The tests use temporary CA/server/client certificates and real loopback sockets.
`test_real_opa_1211_over_tls13_mtls` runs when `.tools/opa` exists and requires its
reported version to equal 1.21.1. The local Darwin ARM64 executable was downloaded
from the official release asset and has SHA-256
`a00a6469a0968c47c01137ed0dacaa88148be5d0eaa8524310cd371f3a98a169`.
It is ignored and not vendored. Reproduce the source selection from the
[OPA 1.21.1 release](https://github.com/open-policy-agent/opa/releases/tag/v1.21.1).
