# Reference runtime 0.1 implementation slice

Authorized October 8, 2026. Contract/schema/RP1 baseline: Git commit `f4a01e2`.
The runtime implements the bilateral primitive, optional DAG composition, and a controlled
adapter boundary. Real external services, orders and payments remain out of scope.
Independent MIT implementation; dependencies are ordinary general-purpose libraries.

## Shared module interfaces

Python package `agent_bazaar` under `src/`. Use `ProtocolError(code, detail)` from `errors`.
Records are ordinary JSON dictionaries satisfying the existing schemas. References are
`{id, digest}` plus optional locator. Full reference equality ignores locator differences,
but compares id/digest. Authentication and authority are separate.

- `crypto`: `canonical(value)->bytes`, `digest(value)->str`, `unsigned_digest(record)->str`,
  `content_ref(record)->dict`; `Signer(agent_id, principal_id, private_key=None, kid=None)`;
  `Signer.sign(record)->(signed_record, proof_wrapper)`; `Signer.public_jwk()`;
  `Registry.register(signer, features=..., roles=...)`; `Registry.verify(record, resolve, now_ms)`.
  Registry explicitly enrolled, not populated from incoming records. Additional configuration
  for revocation/principal binding belongs in the module. `resolve(ref)` returns exact JSON.
- `schema`: `validate(record)` rejects malformed semantic/interaction/admission records.
- `policy`: real OPA HTTP client + original Rego policy; local explicitly configured policy
  implementation may support controlled tests but must never be a silent OPA fallback.
- `storage`: `Ledger(path)`; `transaction()` context (nested savepoints); `get(namespace,key,default=None)`,
  `put(namespace,key,value)`, `delete(namespace,key)`, `items(namespace)->list[(key,value)]`,
  `revision` property, `close()`. JSON copy-in/copy-out. Namespace keys strings. Transactions
  serialize conflicting writers across connections. Each successful outer write transaction
  advances one ledger revision. WAL + FULL durability for files. No automatic tombstone expiry.
- `recovery`: `Recovery(ledger)`, register/notice/health/refusal/observe operations. Purely
  internal authority interface; public authenticated records are checked by the harness.
  Recovery owner sends exact signatures to root before integration. Use integer milliseconds.
- `composition`: `Composition(ledger, resolve)`; `submit_plan(plan)`, `bind(binding)`,
  `validate_candidate(candidate)`, `check(candidate,stage,agreement_for_candidate,status_for_agreement,
  evidence_check)`. Callbacks resolve current exact agreement/status/evidence; missing returns
  nonpositive; no guessed success. Methods raise ProtocolError on absent/invalid predicates.
- `handoff`: C8 boundary with Prepare/Dispatch/Reconcile and an explicitly registered adapter;
  owner sends exact interface to root before integration. It must use shared Ledger and
  crypto helpers, reserve marker before effects, never auto-redeliver, and expose failpoints
  for crash-window tests. No native API/payment clients.
- `harness` (root): authenticated record ingestion, registered domain semantics, publication/
  authority/admission, exact action provenance, offer lineage, adoption, formation/capacity,
  signed outcomes, C3 replay/receipts, C5 orchestration, integration of optional modules.
- `transport` (trust lane): strict C6 A2A JSON-RPC codec/HTTPS handler and bounded mTLS retrieval;
  no native core A2A enum modifications. Handler delegates to harness callable.

## Ownership

Trust lane: crypto.py, schema.py, policy.py, transport.py, policies/, corresponding tests.
Durability lane: storage.py, recovery.py and corresponding tests.
Composition lane: composition.py, handoff.py and corresponding tests.
Root: package/build config, harness, semantic validation/domain fixtures, executable demo,
end-to-end tests, documentation and integration. No agent commits or edits another lane.
