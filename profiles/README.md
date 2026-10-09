# Reference profiles

The [RP1 reference profile](reference-profile.md) supplies the default path for **APP 0.4-draft**: one bilateral agreement with protected principal recovery. The application supplies its capability, principal permission, truthful limits and designated notice channel. A realm manifest fixes the mechanical choices for the harness; an application does not design cryptography, replay or ordering per transaction.

RP1 selects A2A 1.0 JSON-RPC over HTTPS, mutual TLS, a configured trust registry, JCS/SHA-256, JWS Ed25519, Open Policy Agent authorization, bounded evidence retrieval and one accepted authority ledger per resource conflict domain. Composition, adapter handoff and lifecycle evidence are separately negotiated optional features using the same universal schema. An ordinary agreement requires none of them.

**Status: RP1 0.1-draft is the normative profile; reference runtime 0.1.0 implements a controlled subset.** The runtime includes real signatures, durable local authority state, an OPA client and Rego policy, mutual-TLS transport, principal-recovery mechanics and a simulated adapter. The October 8 deployment follow-up passed 155 tests against the pre-rename ABP source, including actual OPA and mutual TLS. Fresh [APP release evidence](../validation.md#published-release-evidence) identifies the checked APP revision and its results. These are implementation results, not certification of every RP1 requirement, a production notice service, a native payment integration or independent interoperability. See the [validation record](../validation.md) and [runtime limits](../docs/runtime.md#current-limits).

Core contracts specify which acts and inferences are valid. RP1 supplies a complete, deliberately narrow operating profile for those contracts. It requires relevant principal recovery windows to clear before externally effective dispatch. It supports composition only where the relevant parties and resource owners accept its common authority; other coordination or early-effect mechanisms require another profile.

The canonical profile identifier is:

```text
https://github.com/JohnnyFiv3r/agent-promise-protocol/blob/main/profiles/reference-profile.md#rp1-v01
```

An identifier is not a live service or a trust root. Participants pin the understood profile and their authenticated configuration before use. Unknown required mechanisms or missing configuration prevent use; advertising a profile does not establish that its requirements have been implemented. Start with the [implementer guide](../docs/implementer-guide.md) for the bilateral path, runtime commands and application responsibilities.
