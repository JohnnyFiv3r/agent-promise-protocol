# Agent Bazaar

**ABP 0.4-draft · Python reference runtime 0.1 · [MIT](LICENSE)**

An agent expresses an outcome. Other agents offer actions they are capable and authorized to perform. The originator selects an exact candidate for each counterparty agreement. Both agents adopt that same reference, and every represented principal retains a protected opportunity to refuse.

Agent Bazaar standardizes those promises and their supporting evidence. An intent does not issue another agent's promise; an accepted agreement does not establish principal clearance, native execution authority, fulfillment or payment.

## Run the reference runtime

The repository now contains an independently implemented Python runtime and executable tests against the contracts, schemas and RP1 profile frozen at **`f4a01e2`**. Python 3.11 or newer and [uv](https://docs.astral.sh/uv/) are required for the locked setup:

```sh
uv sync --locked --extra dev
uv run --locked agent-bazaar demo
uv run --locked --extra dev python -m pytest tests/runtime -q -ra
uv run --locked --extra dev python checks/validate.py
```

The CLI runs signed bilateral formation, principal refusal/restart recovery, a three-agent composition and guarded fake-adapter handoff. It prints structured observations and writes durable SQLite ledgers into a fresh temporary directory. Use `agent-bazaar demo --directory PATH` to choose a fresh output directory.

**The demo is a controlled simulation.** Its Ed25519 signatures, RFC 8785 digests, schema checks and SQLite transactions are real. Its capability evidence, principal policies, clock, inbox/health observations, peer transport identities and native adapter are explicitly controlled fixtures. It uses `TestPolicy` and makes no network calls, real service requests, orders or payments. Separate integration tests exercise actual TLS 1.3 mutual authentication and a local OPA 1.21.1 service; installing the Python package does not install OPA.

Start with the **[runtime and integration guide](docs/runtime.md)**. [Validation](validation.md) records evidence categories and reproduction commands; [conformance](conformance.md) explains the remaining assessment scope. Passing this implementation's tests does not establish full RP1 deployment conformance, independent interoperability or ease of adoption by another builder.

## One agreement first

The bilateral primitive does not require a transaction plan or native adapter. Composition, adapter handoff and lifecycle evidence are additional declared features. Unknown required features or meanings block the dependent act.

Applications supply understood action semantics, truthful capability and constraints, principal-approved permissions, and a usable principal notice/refusal channel. The package supplies protocol checks and integration boundaries; it cannot manufacture those application facts. The current authority arrangement is one explicitly delegated realm sharing one SQLite ledger. It does not provide federated consensus or fencing against a separate database copy.

Keep **agent agreement**, **principal clearance**, and **downstream authorization** separate. A positive refusal-window status never fabricates native action authority or a human signature.

## Contracts and design baseline

- [Eight governing contracts](contracts/README.md): C1–C6 define bilateral formation and recovery; C7 adds composition; C8 defines the adapter boundary and evidence.
- [Core model](contract.md), [current decisions](decisions-v0.4.md), [architecture](protocol-architecture.md), and [trust/failure model](design/trust-and-failure-model.md).
- [RP1 reference profile](profiles/reference-profile.md), [application/harness design](profiles/harness-interface.md), and [conceptual quick-start](docs/quickstart.md).
- [Semantic schemas](schemas/contract.schema.json), [interaction envelopes](schemas/interaction.schema.json), and [admission declaration](schemas/admission-policy.schema.json).
- [Fictional authored examples](examples/README.md), [worked scenarios](examples/lifecycle-walkthroughs.md), [runtime source](src/agent_bazaar/), and [executable tests](tests/runtime/).

The normative contracts/profile remain frozen design inputs. Their statements about implementation status describe the baseline when written; this README and the runtime guide describe the later implementation. [P01–P27](tests/PROPOSED.md) remain proposed assessment scenarios, with partial coverage by executable tests. They are not a checklist in which every proposal has passed.

## Native boundary and current limits

The runtime freezes a preparation, journals a stable dispatch attempt before invoking an enrolled adapter, and reconciles uncertain outcomes without automatically dispatching again. The provided adapter is a deterministic fake. No AP2, UCP, ACP, payment rail or live service integration has been qualified.

Production authenticated time/NTS, qualifying HTTPS principal inbox operation, signed registry distribution and failover fencing remain integration work. `policy_defined` validity is unsupported. Some unusual object-key orderings cannot produce a matching OPA/JCS decision digest and fail closed. See the [runtime limits](docs/runtime.md#current-limits) and [policy implementation notes](policies/README.md).

Original specification, schemas, runtime and examples are MIT licensed. Ordinary general-purpose dependencies are declared in [pyproject.toml](pyproject.toml) and pinned in [uv.lock](uv.lock). Related projects provide [research and inspiration](research/README.md); comparator implementation code and imported test suites are not used. See [contribution guidance](CONTRIBUTING.md). Historical snapshots preserve [0.3](archive/0.3/README.md), [0.1](archive/0.1/README.md), and [0.2 in Git history](https://github.com/JohnnyFiv3r/agent-bazaar/tree/0011b504b706970c54a780d700be3efe444d4898).
