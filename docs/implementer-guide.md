# Implement Agent Promise Protocol

**APP 0.4-draft · RP1 0.1-draft · reference runtime 0.1.0**

Start with one bilateral agreement. An agent publishes a permitted intent, another issues a qualified offer, and both adopt the same exact terms. The originator coordinates finalization; each principal retains a protected refusal period. Composition repeats that agreement primitive with explicit dependencies. It is optional.

## 1. Read the bilateral contract

The [quickstart](quickstart.md) follows one capability through agreement and principal recovery. Read the [core contract](../contract.md) and governing contracts C1–C6 for the required behavior:

| Contract | What your participant preserves |
|---|---|
| [C1 — Publication](../contracts/01-publication-policy.md) | Principal consent, audience, disclosure and contact rules |
| [C2 — Qualified actions](../contracts/02-qualified-actions.md) | Each author's own capability- and authority-bounded promises; intent remains distinct from an offer |
| [C3 — Admission and negotiation](../contracts/03-admission-negotiation.md) | Bounded iterative offers, immutable option revisions, replay and policy-defined validity |
| [C4 — Formation](../contracts/04-formation.md) | Exact candidate, both adoptions, originator coordination and recoverable finalization |
| [C5 — Principal recovery](../contracts/05-principal-refusal.md) | Qualifying notice, protected refusal and current attributable status |
| [C6 — A2A and evidence](../contracts/06-a2a-evidence.md) | Authenticated invocation, extension activation, portable proof and exact content references |

The baseline feature is `bilateral`. Keep agreement formation, principal clearance and any later native performance as separate observations. An A2A task completion or successful tool call establishes none of those on its own.

## 2. Select RP1 and configure the participant

[RP1](../profiles/reference-profile.md) fixes the transport, proofs, policy interface and authority/recovery mechanisms. Pin its understood content and schemas, using the exact identifiers in its identifier table. A mutable web URL is not version negotiation.

The participant provider configures authenticated agent/principal enrollment, key custody, approved policy and data, recipient admission scopes, designated principal channels, and resource-authority assignments. RP1 requires one mutually accepted authority for each affected resource conflict domain. Hosting a journal does not itself grant that authority.

An assistant can embed the participant or reach it through an optional MCP connector. Sellers can host their own A2A endpoints. The [deployment model](../deployment-model.md) separates those product entry points from protocol authority: discovery, ranking and shopping interfaces belong to applications; APP requires no global marketplace or ledger. The reference runtime currently uses one trusted shared SQLite authority store. Independent hosting still needs the [separate-participant runtime work](../design/independent-participant-slice.md) described there.

## 3. Use the schemas and existing A2A carrier

The authoritative schemas are:

- [Semantic records](../schemas/contract.schema.json): intentions, qualified offers, candidates, adoptions, accepted objects and status.
- [Interactions](../schemas/interaction.schema.json): signed operation requests and receipts.
- [Admission policy](../schemas/admission-policy.schema.json): disclosed traffic and work allowances.

Follow [C6](../contracts/06-a2a-evidence.md) and the [A2A architecture](../protocol-architecture.md) for Agent Card advertisement, activation and carriage through native `SendMessage`. The baseline operation purposes are `submit_record`, `finalize_candidate` and `query_status`; they are not new A2A RPC methods. Retries preserve the original signed logical operation and its identity.

The [authored examples](../examples/README.md) explain record shape and references. Their illustrative proofs are not signatures. The [runtime fixtures](../src/agent_promise_protocol/fixtures.py) generate real signed records for controlled scenarios; neither set supplies real principal delegation or truthful commercial facts for your application.

## 4. Run the reference implementation

From a checkout of this release, with Python 3.11 or newer and uv installed:

```sh
uv sync --locked --extra dev
uv run --locked agent-promise-protocol demo
uv run --locked --extra dev python checks/validate.py
uv run --locked --extra dev python -m pytest tests/runtime -q -ra
```

The demo creates a fresh temporary directory and prints retained ledger paths, exact agreement references and separate recovery/handoff observations. It runs a bilateral agreement, refusal with restart/replay, and an optional three-agent composition. Signatures, hashing and SQLite persistence are real. Policy grants, clock, inbox health and native effects are controlled fixtures; no order, payment or service is performed.

The October 8 deployment follow-up recorded **155 passed, 0 failed, 0 skipped** against the pre-rename ABP source, including real OPA and mutual TLS. The [APP release evidence](../validation.md#published-release-evidence) identifies the current namespace's exact checked revision, results and artifacts. Reproducing the OPA case requires the separately installed **OPA 1.21.1** executable at `.tools/opa`; otherwise pytest reports a skip. Use the [validation instructions](../validation.md#reproduce-the-checks) and inspect the result rather than treating a skipped case as verified. Those results are implementation-specific evidence, not proof of complete RP1 conformance or separate-provider interoperability.

## 5. Connect real application inputs

The [runtime guide](runtime.md) documents `Domain`, `ActionMeaning`, `Enrollment`, `Registry` and `Harness`. Use those actual Python interfaces; the convenient method names in the [harness design](../profiles/harness-interface.md) are a proposed application facade.

| You supply | The runtime checks or maintains |
|---|---|
| Understood action semantics and truthful capability/capacity facts | Exact meanings, qualification guards and declared conflicts |
| Authenticated principal delegation and approved policy/data | Bound policy decisions and authority at each relevant transition |
| Enrolled keys, peers and trust configuration | Signature scope, issuer identity and authenticated ingress |
| Real notice/refusal channel and qualified time/health evidence | Protected-window accounting, refusal admission and recoverable status |
| Durable custody and explicitly assigned authority roles | Operation identities, serialized local transitions and replay outcomes |

Use `Harness.invoke(request, records, peer)` behind authenticated transport. The transport determines `peer`; an untrusted caller cannot select its own authenticated identity. Internal authority helpers must not become unauthenticated public endpoints. Persist keys, enrollment and recovery configuration independently of a chat session; the controlled demo does not supply that operational custody.

Stop at the accepted object and current recovery status when your application only negotiates. Enable [C7 composition](../contracts/07-composition.md) only for declared dependencies between agreements. Enable [C8 handoff](../contracts/08-adapter-boundary.md) only when an adapter supplies the selected native mechanism and independently establishes its authority. The included `FakeAdapter` tests that boundary; APP does not implement native AP2/UCP/ACP validation, payments or settlement.

The [conformance assessment](../conformance.md) identifies current coverage and remaining production integrations. External-builder adoption and a separately authored interoperating implementation are still explicit next assessments; they are not implied by the controlled demo.
