# Conformance status and assessment

**APP 0.4 / RP1 · reference runtime 0.1 · historical ABP baseline at `f4a01e2`**

The repository contains a Python reference implementation and executable structural, cryptographic, behavioral and local integration tests. Those tests provide evidence for their actual assertions under their stated trust assumptions. They do not establish complete RP1 deployment conformance, independent interoperability or builder adoption.

This is published as an **APP 0.4 Reference Draft** with an MIT reference runtime. The release's verification report identifies the actual checked revision and artifacts; it is not a certificate for a provider's deployment. See [release metadata](release.json), [validation](validation.md) and the [implementer guide](docs/implementer-guide.md).

The normative requirements remain the [core contract](contract.md), [C1–C8](contracts/README.md), [RP1](profiles/reference-profile.md) and the frozen schemas. The implementation does not redefine a requirement when a test is easier to satisfy. An unsupported required meaning must block the act.

## Scope of a claim

A conformance claim must name the exact contract/profile revision, supported features, action/evidence vocabularies, authenticated identity/policy configuration, authority arrangement and external boundaries actually exercised. Schema validity, signature validity, current permission, exact adoption, principal clearance and native performance are separate observations.

The bilateral primitive needs no transaction plan or native adapter. Optional `composition`, `lifecycle-evidence` and `adapter-handoff` features retain the same authorship, authority and principal-recovery rules. Declaring a feature does not establish that a deployment has qualified every external dependency required to operate it.

This reference realm uses explicit participant and resource-owner delegation to one shared SQLite authority ledger. Its tests exercise local transactional serialization and recovery. There is no claim of federated consensus, distributed failover fencing, exclusive control over undisclosed external allocations, or atomic settlement across native systems.

## Executable evidence

| Evidence | Location | What it can establish |
|---|---|---|
| Authoring checks | [`checks/validate.py`](checks/validate.py) | Fictional fixture structure, local references and implemented document consistency constraints |
| Canonicalization and proofs | [`test_crypto.py`](tests/runtime/test_crypto.py), [`test_schema.py`](tests/runtime/test_schema.py) | Real JCS/Ed25519 verification, malformed-input and proof-substitution rejection, enrolled identity/scope checks and schema packaging consistency |
| Native carrier and policy integration | [`test_transport.py`](tests/runtime/test_transport.py), [`test_policy.py`](tests/runtime/test_policy.py) | Actual loopback TLS 1.3 mutual authentication and certificate pinning; native A2A carriage; bounded retrieval; actual OPA 1.21.1 evaluation when that executable is installed |
| Durable authority and principal recovery | [`test_storage.py`](tests/runtime/test_storage.py), [`test_recovery.py`](tests/runtime/test_recovery.py) | Local writer serialization, committed-state crash recovery, exact principal descriptors, notice/window accounting and durable refusal admission |
| Optional composition | [`test_composition.py`](tests/runtime/test_composition.py) | DAG validation, exact slot bindings, proof-variant identity, current and transitive dependency checks under configured predicates |
| Adapter boundary | [`test_handoff.py`](tests/runtime/test_handoff.py) | Frozen native bytes, stable dispatch identity, current authority gates, marker-before-call behavior and uncertainty-preserving fake reconciliation |
| Integrated reference behavior | [`test_harness.py`](tests/runtime/test_harness.py) | Signed bilateral formation, admission/replay, exact promise provenance, shared capacity, protected refusal, optional composition and fake handoff through one implementation |
| Deployment boundaries | [`test_deployment_portability.py`](tests/runtime/test_deployment_portability.py), [`test_admission_scope.py`](tests/runtime/test_admission_scope.py) | Separate-store evidence preserves authorship without semantic admission; recipient/allowance accounting remains scoped; neither proves distributed formation or hosted tenant isolation |

[Validation](validation.md) separates the initial 142-test runtime run from the deployment/accounting follow-up, with source manifests, reproduction commands and the limits of each category. A skipped OPA integration test is not an OPA pass. Passing local A2A tests against this implementation does not show interoperability with a separately authored A2A/APP participant.

## P01–P27 remain assessment proposals

[`tests/PROPOSED.md`](tests/PROPOSED.md) is the design proposal preserved from the contract freeze. Its scenario IDs are broader assessment oracles, not aliases for individual pytest functions. Some assertions now have executable coverage; the complete proposal has not been promoted to a passed conformance suite.

| Proposed area | Related executable coverage | Remaining distinction |
|---|---|---|
| P01–P05: publication, admission, validity and provenance | Harness, schema and policy tests | Controlled meanings/policies do not establish every proposed disclosure, symmetric-role or application-validity scenario |
| P06–P09: exact formation, variants, capacity and recovery | Crypto, harness and storage tests | The tested conflict boundary is one delegated local ledger; arbitrary external capacity and distributed authority are unqualified |
| P10–P12: composition and dependency authorship | Composition and harness tests | Named registered predicates and exact agreements are exercised; actual subcontract performance and all application meanings remain external |
| P13–P15: principal notice, health, timing and refusal | Recovery and harness tests | Clock and service-health inputs are controlled; production NTS and a real principal inbox/refusal service are not qualified |
| P16–P20: preparation, native authority, dispatch and replay | Handoff, policy and harness tests | Native authority and effect observations come from controlled adapters; no real native execution/finality is demonstrated |
| P21–P24: evidence meaning, correlation, privacy and containment | Composition, handoff and transport tests provide selected guard coverage | No comprehensive private-evidence mechanism, real service assessment, settlement finality or live adapter qualification is claimed |
| P25–P27: builder adoption, independent implementation and minimal integration | A bilateral reference path exists and its mechanics are tested | The proposed external-builder and independent-participant assessments remain unrun; an internal fixture is not their result |

This is a partial topic map. It neither states that every oracle in a row has been exercised nor converts all proposed scenarios into passes. The [historical 0.1 plan](archive/0.1/conformance.md) also remains a historical artifact with different semantics.

## Remaining deployment and assessment work

Current implementation limits include `policy_defined` validity, production authenticated time/continuity and HTTPS inbox qualification, signed registry revision installation, deployment key custody and distributed successor fencing. Rare OPA/JCS object-key ordering differences fail closed. See the [runtime guide](docs/runtime.md#current-limits) and [policy notes](policies/README.md).

The [deployment model](deployment-model.md) permits embedded or connector-accessed buyers, independent sellers, optional discovery and separately held journals. RP1 still requires one selected authority for a conflict scope. Its remote bindings and complete separate-store formation/recovery remain the [next runtime slice](design/independent-participant-slice.md), not an outcome of portable-record tests.

Builder adoption must be assessed with a builder who did not author the runtime, supplying actual capability semantics, principal permissions, constraints and controlled integrations using the published materials. Record undocumented rules and bespoke protocol machinery rather than inferring usability from an internal walkthrough.

Independent interoperability requires a separately authored participant built from the frozen specification and shared public vocabulary, exchanging and recovering the same exact records with another implementation. No such two-implementation result is claimed.

The supplied fake adapter records simulated submission/lookup observations only. Signatures authenticate those claims, not real fulfillment or settlement. Any live service, order, AP2/UCP/ACP, payment or settlement adapter requires a separately scoped native-authority, correlation, idempotency, finality and outcome qualification. Nothing in this test suite performs or establishes that live integration.
