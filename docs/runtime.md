# Python reference runtime

**Runtime 0.1 · APP 0.4 / RP1 · historical ABP baseline at `f4a01e2`**

This package implements protocol mechanics for a controlled, explicitly enrolled authority realm. It provides a runnable bilateral path, optional acyclic composition, principal recovery, and an explicit adapter boundary. It is an independent MIT implementation using general-purpose libraries. The [APP namespace transition](namespace-transition.md) distinguishes this release from the earlier ABP baseline; the runtime does not certify a production RP1 deployment.

The [deployment clarification](../deployment-model.md) keeps independent hosting and optional connector/aggregation providers within the existing core semantics. The [independent-participant slice](../design/independent-participant-slice.md) is not implemented by this runtime: formation reads both adoptions and capacity locally; recovery and composition read the common authority store. Transported evidence can be independently verified without thereby installing a remote accepted/status result as locally authoritative state. Shared database access is trusted authority access, not a multi-customer isolation layer.

## Install, run and inspect

Use Python 3.11 or newer. The checked-in `uv.lock` pins runtime and development dependency versions and distribution hashes; the build backend is pinned in `pyproject.toml`.

```sh
uv sync --locked --extra dev
uv run --locked agent-promise-protocol demo
uv run --locked --extra dev python -m pytest tests/runtime -q -ra
uv run --locked --extra dev python checks/validate.py
```

`agent-promise-protocol demo --directory PATH` accepts a fresh output directory. Without that option, the CLI creates one in the system temporary directory. Each scenario retains a SQLite authority ledger and prints exact agreement references and separate formation, recovery and handoff observations.

The demo covers a bilateral agreement and guarded dispatch; refusal at the deadline followed by restart and replay; and three negotiating agents forming two bilateral agreements with a handoff dependency. It uses real signatures, hashes, schemas and durable local storage, with controlled capability/authority evidence, `TestPolicy`, `ControlledClock`, simulated inbox health and `FakeAdapter`. Its enrolled peer certificate identifiers are fixture values, not a live TLS exchange. The separate transport tests perform real mutual TLS.

A fixture restart reopens the ledger while preserving that fixture's enrolled keys and fake native observations in the running test. A new process is not able to recover those private keys from the demo directory: the fixture does not write them there. Deployment key custody and enrollment persistence require separate configuration.

The Python package can be built without OPA:

```sh
uv build --wheel --sdist
```

Schemas are loaded through `importlib.resources`, independently of the working directory. The wheel includes all three runtime schemas; the source distribution also includes the authoritative repository schemas. A drift test compares the packaged copies byte for byte with `schemas/`. An installed-wheel check has validated and rejected records in an isolated environment outside the checkout.

## Package responsibilities

| Module | Current responsibility |
|---|---|
| [`crypto`](../src/agent_promise_protocol/crypto.py) | RFC 8785 via `rfc8785`, SHA-256, Ed25519 JWS via `cryptography`, exact protected header/scope checks, explicitly enrolled principal/agent/key bindings and revocation checks |
| [`schema`](../src/agent_promise_protocol/schema.py) | Pinned structural schemas, format checks and required-feature declarations |
| [`transport`](../src/agent_promise_protocol/transport.py) | Native A2A 1.0 `SendMessage` JSON-RPC codec, extension activation/acknowledgment, bounded TLS 1.3 mutual authentication, leaf pinning and HTTPS evidence retrieval |
| [`policy`](../src/agent_promise_protocol/policy.py) and [`rp1.rego`](../policies/rp1.rego) | Exact RP1 OPA input/result checks, approved reference/state binding, decision lifetime and explicit fixture policy |
| [`harness`](../src/agent_promise_protocol/harness.py), [`guards`](../src/agent_promise_protocol/guards.py), [`records`](../src/agent_promise_protocol/records.py) | Authenticated ingestion, application meanings, admission, promise provenance, exact adoption/formation, operation replay and signed outcomes |
| [`storage`](../src/agent_promise_protocol/storage.py) | SQLite WAL/FULL durability, serialized writes, nested savepoints, revision accounting and retained operation state |
| [`recovery`](../src/agent_promise_protocol/recovery.py) | Per-principal notice/refusal state, durable pending refusal admission, conservative credited-time accounting and absorbing refusal |
| [`composition`](../src/agent_promise_protocol/composition.py) | Plan/DAG validation, immutable exact slot bindings and stage-specific current dependencies |
| [`handoff`](../src/agent_promise_protocol/handoff.py) | Frozen native-byte wrappers, current gates, durable dispatch markers, stable native correlation and read-only reconciliation |

These modules provide integration hooks, rather than a claim that every facade name proposed in the frozen [harness design](../profiles/harness-interface.md) has shipped as an application SDK.

## Application meaning and enrollment

The public Python integration types live in [`domain.py`](../src/agent_promise_protocol/domain.py). An application must supply real facts and evaluators before relying on an action.

`ActionMeaning(semantics_ref, validate, occurrence)` binds an action type to an exact semantic definition. `validate(action)` checks its complete parameter meaning. `occurrence(action, action_instance)` determines whether a requested occurrence is within the adopted action and cardinality. A label or new random occurrence ID is insufficient authority for another effect.

`Domain` holds the explicitly installed meanings and predicates:

- `actions` maps action-type URIs to `ActionMeaning`.
- `trusted_refs` and `trust(ref)` record exact administrator-approved definitions/evidence; `understood_uris` records understood required vocabulary.
- `selection` supplies the understood selection/capacity declarations.
- `agreement_checks` checks the selected complete agreement terms.
- `arrangement_checks(record, publications)` checks a complete commercial arrangement against the relevant publications; `candidate_checks(candidate, selected_offers)` checks the resulting candidate against the selected offers.
- `qualification_checks(promise, stage)` supplies a required qualification's stage-specific predicate. `requirement_checks` and `evidence_checks` supply named composition and evidence meanings.
- `health_checks(evidence, descriptor, ClockReading)` qualifies service-health observations under the exact designated notice profile. Its backing service-evidence references must resolve and be explicitly trusted; signing an interval does not by itself prove its entire duration usable.

Trusting a digest does not itself implement a predicate. Missing required meaning or an evaluator that does not return the required positive result blocks the transition. The controlled research vocabulary in [`fixtures.py`](../src/agent_promise_protocol/fixtures.py) is an example configuration, not a universal action taxonomy or verified research capability.

An `Enrollment` binds an agent to its `principal_id`, exact principal policy and capability references, allowed action types/features, admission policy, positive refusal duration, designated notice/refusal references and control agents, notice authority, and common authority scope. `active` is current trusted enrollment state. Constructing this object is administrative configuration; incoming messages cannot create enrollment or grant themselves these powers.

`Registry.register`/`enroll` separately configure public keys, principal identity, understood features, roles, certificate pins, active intervals and proof scopes. Signature validity authenticates a statement; `Domain`, `Enrollment`, policy and the relevant protocol guards determine whether the act is authorized. Principal-control agents require their own explicit authority. Ordinary negotiation permission does not confer refusal authority.

The main composition point is:

```python
from agent_promise_protocol.harness import Harness

# Each argument is previously authenticated deployment/application configuration.
harness = Harness(
    signer=signer, registry=registry, ledger=ledger, policy=policy,
    clock=clock, domain=domain, enrollments=enrollments,
    authority_scope=authority_scope, recipient_scope=recipient_scope,
)
```

This shows the constructor contract; it is not a ready-made production enrollment. The complete runnable controlled configuration is `fixtures.Environment`. The runtime does not silently infer missing principal permissions, truthful capacity, policy approval or notice usability.

## Authenticated ingress and policy

`Harness.invoke(request, records, peer)` is the admitted interaction boundary. `peer` must come from the authenticated transport boundary, or from an explicitly selected test fixture. Merely supplying a dictionary over a network does not establish a peer. Direct helpers such as `submit` are internal authority interfaces and must not be exposed as unauthenticated public RPCs.

The transport functions `encode_request`/`decode_request` and `encode_response`/`decode_response` carry one native A2A data part with `{app, records}`. `make_handler` obtains peer identity from the actual TLS socket and its enrolled leaf certificate; `serve_tls` requires a TLS 1.3 context with mandatory client authentication. A trusted callback invokes the harness and returns `(receipt, supporting_records)`. The callback must materialize permitted result/proof evidence within the response allowance; support records do not independently execute operations.

A missing extension acknowledgment preserves an unknown outcome. Recover the same signed logical operation instead of inventing a new operation ID. Native transport success, an interaction receipt, accepted terms and native performance are separate observations.

Live-option accounting follows the addressed recipient and selected allowance pool, even when several recipients share this trusted ledger. The first applied revision pins an option to that pool; revisions and proof variants do not gain fresh allowance. Pending or semantically rejected offers occupy no live-option slot, and application rechecks capacity in the same transaction as the semantic effect.

Ledgers created before this accounting index need explicit operator reconciliation if they retain applied offers without consistent recipient/pool memberships. New offer admission then fails with `internal_unresolved`; exact historical operation replay remains available. Resuming an old pending offer whose saved admission lacks the live-option limit also returns a durable blocked result without applying the offer. There is no automatic backfill from global offer heads and no permission to clear the journal or reset consumed quotas. This guard preserves uncertainty; it is not a supplied migration utility or a tenant access-control mechanism.

`OPAClient` calls the exact RP1 REST Data API endpoint over the configured mutual-TLS connection. It checks the result's exact input digest, approved policy/data references, authority revision, boundary digest, reason codes and lifetime. OPA errors, missing results, extra obligations, mismatched state and expired decisions deny the act. There is no automatic fallback to `TestPolicy`.

The original policy and service instructions are in [`policies/README.md`](../policies/README.md). The realm administrator remains responsible for authenticating owner approval and installing the approved bundle/data. The enforcement point signs its recorded policy input/result; OPA itself is not claimed to have signed that evidence.

The OPA integration test uses a separately installed `.tools/opa` and requires version **1.21.1**. It launches that real executable on loopback with a temporary CA and client/server certificates. When the executable is absent, that test reports a skip; package installation and the controlled CLI still work. Inspect `pytest -ra` output when reporting whether real OPA was exercised.

## Authority, recovery and native hooks

Every participating resource owner must explicitly delegate the relevant decisions to one common authority scope. Participants in the reference realm share the same SQLite ledger. `BEGIN IMMEDIATE` serializes conflicting writers against that database; WAL/FULL commits and retained tombstones support local restart/replay. A separate database copy is a separate state history. This implementation does not provide cross-realm commit, leader election, network-partition consensus or a distributed successor-fencing protocol.

Recovery uses signed exact-target notice/health/refusal evidence and conservative time bounds. Missing notice does not create a deadline. Gaps, conflicting health evidence and unknown restart continuity do not earn usable review time. Equality at the deadline remains timely for refusal; pending admissions that could be timely prevent closure. A valid refusal remains absorbing for its accepted object after restart and replay.

The included `ControlledClock` supplies deterministic test readings. No production NTS client or time-source qualification is provided. Likewise, the demo signs simulated availability and health observations; it does not operate or qualify a real HTTPS principal inbox or establish that a person read the terms.

An optional adapter is enrolled through `Handoff.register(adapter_agent_id, adapter_profile_uri, adapter, contract_ref, ...)`. Its hooks are `prepare`, `verify_native_authority`, `dispatch` and `reconcile`; exact signatures are documented by [`handoff.py`](../src/agent_promise_protocol/handoff.py). Preparation freezes byte-preserving native content without externally material effects. Dispatch rechecks gates and journals the stable attempt marker before invoking the adapter. Reconciliation observes the original key and cannot dispatch again.

A crash after the marker may leave `in_doubt` even if no call escaped. The runtime preserves that uncertainty; it does not infer native absence or retry automatically. Definitive absence needs the explicitly registered native contract's authenticated final-absence predicate. `FakeAdapter` is the supplied controlled implementation. It does not demonstrate a real provider's idempotency, finality, payment authorization or outcome truth.

## Current limits

- The implementation preserves the commitment model of the historical **`f4a01e2`** baseline with the declared APP namespace and deployment clarifications; its release tag identifies the actual contracts and schemas. It is not a blanket conformance certificate for every requirement or deployment.
- `expires_at` and `until_withdrawn` validity have runtime handling. `policy_defined` validity lacks an installed interpreter and fails closed.
- Production NTS/clock continuity, qualifying HTTPS inbox availability, signed registry revision distribution/installation, key custody and distributed authority fencing require additional integration and qualification.
- The current OPA policy corrects optional HTML/JavaScript string escaping and independently checks real RFC 8785 digests. Rare object-key combinations sort differently in OPA and JCS; those decisions are rejected. It does not approximate the required digest.
- Native adapters, truthful capabilities/capacity and external evidence require application-specific implementation. No live service, order, AP2/UCP/ACP flow, payment, transfer or settlement is implemented or validated here.
- Proposed builder-adoption and independent-implementation assessments remain unrun. The runtime's tests and controlled walkthrough do not establish those outcomes.

See [validation evidence](../validation.md) and the [conformance assessment](../conformance.md) for the executable-test map and the distinction from P01–P27.
