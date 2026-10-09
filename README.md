# Agent Promise Protocol (APP)

**APP 0.4-draft · Python reference runtime 0.1 · [MIT](LICENSE)**

[APP 0.4 Reference Draft release](https://github.com/JohnnyFiv3r/agent-promise-protocol/releases/tag/app-v0.4-draft.1) · [Implementer guide](docs/implementer-guide.md) · [Changes](CHANGELOG.md)

An agent expresses an outcome. Other agents offer actions they are capable and authorized to perform. The originator selects an exact candidate for each counterparty agreement. Both agents adopt that same reference, and every represented principal retains a protected opportunity to refuse.

Agent Promise Protocol standardizes those promises and their supporting evidence. An intent does not issue another agent's promise; an accepted agreement does not establish principal clearance, native execution authority, fulfillment or payment.

## Run the reference runtime

The repository contains an independently implemented Python runtime and executable tests for the APP contracts, schemas and RP1 profile. Its earlier ABP implementation baseline is preserved at **`f4a01e2`**; the [namespace transition](docs/namespace-transition.md) identifies the release's APP wire and package names. Python 3.11 or newer and [uv](https://docs.astral.sh/uv/) are required for the locked setup:

```sh
uv sync --locked --extra dev
uv run --locked agent-promise-protocol demo
uv run --locked --extra dev python -m pytest tests/runtime -q -ra
uv run --locked --extra dev python checks/validate.py
```

The CLI runs signed bilateral formation, principal refusal/restart recovery, a three-agent composition and guarded fake-adapter handoff. It prints structured observations and writes durable SQLite ledgers into a fresh temporary directory. Use `agent-promise-protocol demo --directory PATH` to choose a fresh output directory.

**The demo is a controlled simulation.** Its Ed25519 signatures, RFC 8785 digests, schema checks and SQLite transactions are real. Its capability evidence, principal policies, clock, inbox/health observations, peer transport identities and native adapter are explicitly controlled fixtures. It uses `TestPolicy` and makes no network calls, real service requests, orders or payments. Separate integration tests exercise actual TLS 1.3 mutual authentication and a local OPA 1.21.1 service; installing the Python package does not install OPA.

Start with the **[implementer guide](docs/implementer-guide.md)**, then the [runtime and integration guide](docs/runtime.md). [Validation](validation.md) records evidence categories and reproduction commands; [conformance](conformance.md) explains the remaining assessment scope. Passing this implementation's tests does not establish full RP1 deployment conformance, independent interoperability or ease of adoption by another builder.

## One agreement first

The bilateral primitive does not require a transaction plan or native adapter. Composition, adapter handoff and lifecycle evidence are additional declared features. Unknown required features or meanings block the dependent act.

Applications supply understood action semantics, truthful capability and constraints, principal-approved permissions, and a usable principal notice/refusal channel. The package supplies protocol checks and integration boundaries; it cannot manufacture those application facts. The current authority arrangement is one explicitly delegated realm sharing one SQLite ledger. It does not provide federated consensus or fencing against a separate database copy.

Keep **agent agreement**, **principal clearance**, and **downstream authorization** separate. A positive refusal-window status never fabricates native action authority or a human signature.

## Hosting and ownership

A buyer can use one connector to its delegated APP participant, or an embedded participant. Sellers expose independently hosted A2A APP endpoints. Discovery, intent routing and offer aggregation are optional application services. Each participant may retain its own permitted signed evidence; the core requires no APP-operated ledger or mandatory discovery provider.

The [deployment model](deployment-model.md) distinguishes journal custody from scoped coordinator, resource and refusal/status authority. RP1 currently selects a common conflict authority, and runtime 0.1 uses a shared SQLite store. The [independent-participant slice](design/independent-participant-slice.md) is the remaining distributed-runtime work; separate-store portability tests do not claim it has already been implemented.

## Contracts and design baseline

- [Eight governing contracts](contracts/README.md): C1–C6 define bilateral formation and recovery; C7 adds composition; C8 defines the adapter boundary and evidence.
- [Core model](contract.md), [current decisions](decisions-v0.4.md), [architecture](protocol-architecture.md), and [trust/failure model](design/trust-and-failure-model.md).
- [RP1 reference profile](profiles/reference-profile.md), [application/harness design](profiles/harness-interface.md), and [conceptual quick-start](docs/quickstart.md).
- [Semantic schemas](schemas/contract.schema.json), [interaction envelopes](schemas/interaction.schema.json), and [admission declaration](schemas/admission-policy.schema.json).
- [Fictional authored examples](examples/README.md), [worked scenarios](examples/lifecycle-walkthroughs.md), [runtime source](src/agent_promise_protocol/), and [executable tests](tests/runtime/).

The original ABP contract/profile baseline is preserved at `f4a01e2`. The current draft adds [deployment and ownership clarifications](deployment-model.md) and uses APP's distinct wire namespace. The underlying commitment and RP1 authority guarantees are preserved; old identifiers and signed records are not silently accepted as APP. Historical archives retain their original names and status. [P01–P27](tests/PROPOSED.md) remain proposed assessment scenarios, with partial coverage by executable tests. They are not a checklist in which every proposal has passed.

## Reference release and compatibility

The tag `app-v0.4-draft.1` fixes the reference draft, RP1 profile, schemas, examples and runtime source as one identifiable release. [Release metadata](release.json) lists their distinct versions and normative sources. The release assets include the source bundle, wheel, source distribution, verification report, release manifest and SHA-256 checksums. The report names the exact tested source commit and package hashes.

The extension and profile URIs are exact identifiers. Their `main` URLs do not make mutable page content authoritative: implementations pin the understood contract/schema revision. The [APP namespace transition](docs/namespace-transition.md) explicitly replaces the earlier ABP names without translating existing acts. Breaking semantic changes require new protocol/profile identifiers and explicit understanding by participants. A documentation correction or implementation repair must not reinterpret an already adopted agreement. Maintainers review changes through pull requests; [contribution](CONTRIBUTING.md) and [release](RELEASING.md) guidance explain that process.

## Native boundary and current limits

The runtime freezes a preparation, journals a stable dispatch attempt before invoking an enrolled adapter, and reconciles uncertain outcomes without automatically dispatching again. The provided adapter is a deterministic fake. No AP2, UCP, ACP, payment rail or live service integration has been qualified.

Production authenticated time/NTS, qualifying HTTPS principal inbox operation, signed registry distribution and failover fencing remain integration work. `policy_defined` validity is unsupported. Some unusual object-key orderings cannot produce a matching OPA/JCS decision digest and fail closed. See the [runtime limits](docs/runtime.md#current-limits) and [policy implementation notes](policies/README.md).

Original specification, schemas, runtime and examples are MIT licensed. Ordinary general-purpose dependencies are declared in [pyproject.toml](pyproject.toml) and pinned in [uv.lock](uv.lock). Related projects provide [research and inspiration](research/README.md); comparator implementation code and imported test suites are not used. See [contribution guidance](CONTRIBUTING.md). Historical snapshots preserve [0.3](archive/0.3/README.md), [0.1](archive/0.1/README.md), and [0.2 in Git history](https://github.com/JohnnyFiv3r/agent-promise-protocol/tree/0011b504b706970c54a780d700be3efe444d4898).
