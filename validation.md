# Validation evidence

**ABP 0.4 / RP1 baseline frozen at `f4a01e2` · reference runtime 0.1**

The repository now has executable implementation tests in addition to its document-authoring checker. These evidence categories must remain separate. A successful structural check, signature verification, local policy decision, controlled behavioral test or fake adapter outcome does not establish the next category automatically.

The frozen contract/profile/schema commit is `f4a01e2c8c1ee6bb72cc6793933afbcedf91572c`. Implementation and documentation changes are assessed against that baseline; current run results must identify their actual checkout and cannot be inferred from the freeze commit alone.

## Recorded implementation run

On October 8, 2026, the final runtime suite completed with **142 passed, 0 failed, 0 skipped** in 21.19 seconds on Python 3.13.5/macOS arm64. This run included the actual OPA 1.21.1 and TLS 1.3 mutual-authentication cases, including a complete signed harness finalization/replay round trip.

The CLI's bilateral, deadline-refusal and three-agent/two-agreement scenarios passed. Wheel and source archive builds completed without warnings; an isolated wheel installation outside the checkout validated schemas and ran the full controlled demo. The source manifest, artifact hashes, commands, environment and bounded claims are recorded in [`validation/runtime-0.1.json`](validation/runtime-0.1.json). That manifest identifies the tested implementation independently of the earlier specification freeze.

## Reproduce the checks

From the repository root with Python 3.11 or newer and uv:

```sh
uv sync --locked --extra dev
uv run --locked --extra dev python checks/validate.py
uv run --locked --extra dev python -m pytest tests/runtime -q -ra
uv run --locked agent-bazaar demo
uv lock --check
uv build --wheel --sdist
```

The demo creates a fresh temporary output directory by default. An explicit `--directory PATH` must name a fresh fixture directory. Its JSON output identifies controlled inputs and keeps agreement, principal recovery, dispatch and simulated native-call observations distinct. See [`demo.py`](src/agent_bazaar/demo.py) and the integrated CLI assertions in [`test_harness.py`](tests/runtime/test_harness.py).

The Python lockfile does not install OPA. The actual OPA integration requires the separately installed **1.21.1** executable at `.tools/opa`; its version is asserted by the test. When absent, that case is skipped and must not be counted as a successful OPA exercise. TLS tests require permission to bind local loopback sockets.

For an explicit policy/transport run after installing the pinned OPA binary:

```sh
.tools/opa version
.tools/opa check --strict policies/rp1.rego
uv run --locked --extra dev python -m pytest tests/runtime/test_policy.py tests/runtime/test_transport.py -q -ra
```

The [policy notes](policies/README.md) identify the tested executable provenance and service configuration. Tests create temporary PKI and use real TLS 1.3 with client certificates, server-name/CA checks and pinned server leaf digests. They do not weaken TLS verification to make the fixture pass.

## What the executable checks exercise

| Check | Evidence boundary |
|---|---|
| [`test_crypto.py`](tests/runtime/test_crypto.py) | Real RFC 8785 serialization and Ed25519 JWS; exact protected headers/scopes/payloads; malformed JSON, unsupported features, unregistered keys/principal mismatches and current versus historical revocation |
| [`test_schema.py`](tests/runtime/test_schema.py) | Semantic/interaction/admission structural validation, feature requirements, formats and byte-for-byte equality between bundled schemas and authoritative sources |
| [`test_policy.py`](tests/runtime/test_policy.py) | Exact policy input/result binding, scope and lifetime checks, state-change rejection, distinct verified denial, and actual OPA REST allow/deny/native-gate checks when enabled |
| [`test_transport.py`](tests/runtime/test_transport.py) | Native A2A codec/activation/receipt binding; malformed carriers; actual mutual TLS; pin mismatch before request dispatch; bounded allowlisted HTTPS retrieval |
| [`test_storage.py`](tests/runtime/test_storage.py) | JSON copy isolation, nested rollback, local conflicting writers, process-crash recovery of committed state and retained tombstones |
| [`test_recovery.py`](tests/runtime/test_recovery.py) | Positive principal descriptors, missing/duplicate notice, deadline equality, uncertain/pending refusal admission, outage/gap handling and restart persistence |
| [`test_composition.py`](tests/runtime/test_composition.py) | Acyclic plans, exact bindings, proof variants, required predicates, current status and stage-specific/transitive dependency clearance |
| [`test_handoff.py`](tests/runtime/test_handoff.py) | Effect-free fake preparation, frozen native bytes, separate fresh native authority, durable markers, concurrent attempts, injected crash/reply-loss windows and read-only reconciliation |
| [`test_harness.py`](tests/runtime/test_harness.py) | Integrated signed formation, operation replay/conflict, provenance, capacity, refusal/control authority, controlled composition/handoff and CLI observations |

Additional integration regressions are in [`test_harness_guards.py`](tests/runtime/test_harness_guards.py), [`test_refusal_ingress.py`](tests/runtime/test_refusal_ingress.py) and [`test_harness_transport.py`](tests/runtime/test_harness_transport.py). They cover capacity-policy substitution, withdrawn provenance, current counterparty authority, uninterpreted commercial arrangements, proof variants, persistent lineage forks, protected control budgets, uncertain refusal verification and durable ingress observed through a second ledger connection. The transport case independently verifies signed results from response bytes and confirms that carrier replay preserves one formation and one allocation.

These are implementation-specific assertions, not a statement that every normative requirement or proposed P01–P27 oracle has passed. The [conformance assessment](conformance.md) maps partial coverage and identifies the unrun external-builder and independent-implementation work.

## Package verification

The wheel and source distribution were built into a temporary directory. Runtime dependencies were installed from the lockfile with package-hash verification into a separate temporary environment, then the wheel was installed there. An isolated Python process outside the checkout loaded all bundled schemas, accepted a structurally valid signed interaction and rejected an added unknown field. Wheel and source-distribution schema bytes were compared with the authoritative files.

This establishes the tested package's schema-resource independence from the source checkout. It does not establish production deployment, reproducibility across every Python/platform combination, or a durable deployment configuration for keys, policies and external services. The permanent schema-copy drift assertion is in [`test_schema.py`](tests/runtime/test_schema.py).

## Authoring fixtures remain fictional

[`checks/validate.py`](checks/validate.py) validates its implemented schema, fictional-record and local-reference constraints. The authored examples under [`examples/`](examples/README.md) remain design-review material. Their illustrative proof references and synthetic native evidence are not the dynamically signed runtime fixtures in [`fixtures.py`](src/agent_bazaar/fixtures.py).

The authoring run reports the following structural/reference coverage:

| Authored input | Count |
|---|---:|
| JSON Schema Draft 2020-12 schema documents | 3 |
| Fictional semantic records | 29 |
| Fictional interaction envelopes | 6 |
| Admission declarations | 2 |
| Supporting documents checked for reference integrity, without a complete policy/evidence schema | 27 |
| Local content references with matching digests | 327 |

Its runtime-testing status is **not assessed by this authoring checker**. Runtime execution is reported separately; none of these authoring counts is a cryptographic or behavioral test count.

The authoring helper's digest coverage remains limited to its documented authored value domain. It does not replace the runtime's real RFC 8785 implementation. A JSON construction template with placeholders can parse without being a complete authenticated A2A request. A reachable reference with a matching digest is not automatically valid authority or a truthful fact.

Historical authoring-only results must not be relabeled as current runtime validation. Current terminal output and exact checked state determine what a run establishes.

## Explicit limits of the evidence

The controlled demo uses `TestPolicy`, `ControlledClock`, signed simulated inbox/health observations and `FakeAdapter`. Actual OPA and HTTPS/mTLS are exercised in separate local integration tests, not silently substituted into that demo. No test performs real research, creates a native order, contacts a payment rail or establishes settlement.

The authority tests operate on one explicitly delegated shared SQLite ledger. Local transactional writer serialization does not provide federated consensus, failover fencing against a copied database or exclusion of allocations made outside the declared authority.

Production NTS/time continuity, real qualifying HTTPS principal inbox/refusal operation, authenticated registry-revision installation, deployment key custody and native adapter qualification remain external work. `policy_defined` validity and unsupported semantic predicates block. Rare object-key order differences between OPA and JCS also block instead of accepting a changed digest.

P01–P27 remain proposals with partial executable coverage. Builder-adoption, minimal integration by an independent builder and independently implemented participant interoperability have not been established. Passing controlled tests cannot be reported as verified AP2/UCP/ACP compatibility, real service delivery, human review, payment or settlement.
