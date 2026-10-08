# Additional neighbors discovered during the recursive audit

**Baseline note:** this comparison was authored against draft 0.1. Statements about Bazaar’s former proposal-only offers, fixed validity or payment scope are historical. The [draft 0.2 decisions](../decisions-v0.2.md) govern the current contract; external findings remain source-review observations.

Checked October 8, 2026. These primary documents were inspected through web retrieval. Source/code coverage differs by project and is stated below. No runtime or native payment integration was executed. Mutable sources are observations, not immutable release pins.

## A202: direct overlap with the proposed system boundary

A202 specifies a carrier-neutral commercial layer and an explicit A2A extension. Its binding separates carrier/task events from commercial state, requires understood extension semantics and preserves signed object meaning. This directly invalidates differentiation based only on being an A2A agreement extension. [A2A binding §§1–6](https://a202.org/bindings/a2a-binding-v0.1/).

The canonical model has demand/supply intent, offers, acceptance, agreement, commitments and obligations. It supports independently operated bilateral formation. Its `Commitment` is derived from an agreement; its `Intent` payload is explicitly deferred in the inspected version. Those are concrete differences from Bazaar's typed emitted intent and general independently issued provide/receive promises. They do not prevent A202 from adding those semantics. [Canonical model §§5, 9–10](https://a202.org/schemas/canonical-commercial-model-v0.1/).

A202 invitations constrain participation in one transaction and require the invited principal's own authority; the operator cannot manufacture it. They primarily address counterparty onboarding. Bazaar's publication contract governs high-level discovery uses and recipient-controlled interaction before a transaction exists. Distinguish these scopes instead of saying A202 lacks consent. [Invitation specification §§3–4](https://a202.org/discovery/counterparty-invitation-v0.1/).

A202 also delegates payment execution. Its handoff names the agreement, obligation, payer/payee, trigger, rail and idempotency key. Bazaar's selected AP2-to-exchange route is a composition choice, not the invention of a rail-neutral commercial handoff. [Settlement handoff §§1–5](https://a202.org/fulfillment/settlement-handoff-v0.1/).

A202's authority system is broader: it defines its own commercial mandates and policy objects; Bazaar proposes bindings to existing authority systems. The initial audit inspected specification text and encountered some raw schema/code retrieval failures. Follow-up source inspection at `8473b0421fdc2a0d9e4bcd299cf9937ee68bf556` verified an Apache-2.0 Python reference implementation and a manifest with 148 fixtures, without executing them. Release status is unresolved: the repository README asserts tagged `v0.1.0`, while the public tags API returned an empty list, the release page returned 404 and the website still describes pre-release work. [Reuse assessment and pinned sources](../reuse-and-licensing.md), [authority comparison](https://a202.org/comparison/).

**Design implication:** an expanding Bazaar agreement/obligation/dispute engine would approach A202. Keep the independent intent/promise and reception semantics explicit, and test an adapter to its formation records before adding another general commercial subsystem.

## Consent-scoped agent negotiation (CSNP)

CSNP separates consent to open discussion from consent to commit and bounds rounds, disclosed option counts and lifetime. It negotiates selections from a mutually known option catalog. Its declared scope excludes free-form price negotiation and discovery. Thus consent plus finite iteration is established comparison material, while its constrained decision domain differs from open-ended capability acquisition. [Repository and library example](https://github.com/molanocortes/consent-scoped-agent-negotiation).

Its design document explicitly connects the work to Contract Net, FIPA and a possible layer over A2A. Its distinctive mechanism restricts wire content to known option identifiers and enforces disclosure budgets through a local guard. Bazaar does not supply that confidentiality guarantee merely by having a publication policy. [Design and prior art](https://github.com/molanocortes/consent-scoped-agent-negotiation/blob/main/DESIGN.md), [threat model](https://github.com/molanocortes/consent-scoped-agent-negotiation/blob/main/THREAT-MODEL.md).

The initial audit read the README, design and threat model while direct `SPEC.md` fetches failed. Follow-up inspection at `f2c0502de6674a5667b72f12e081d30e9d696847` verified MIT licensing and source for the Python consent guard, message validation and negotiation state. Its MCP adapter is explicitly a skeleton with commitment unimplemented. No code was executed; this is not an exhaustive field comparison. [Reuse assessment and pinned sources](../reuse-and-licensing.md).

## Two projects named Agent Negotiation Protocol

The vendor-negotiation ANP defines signed identities, discussion/disclosure mandates, typed offers and counteroffers, and a verifiable session log. Its v0.1 is buyer-hosted HTTPS and retains local acceptance authority. It is close commercial-negotiation prior art; Bazaar's A2A/reception/promise boundary is a different scope. [ANP v0.1 specification](https://raw.githubusercontent.com/fredrikfilipsson-svg/agent-negotiation-protocol/main/protocol/SPEC.md).

A separate ANP repository describes bounded price counteroffers followed by x402 payment for a `DEAL` session. It defeats any claim that negotiated offers before paid-resource exchange are by themselves novel. This audit used its published interface description, not its live service. [ANP-Protocol repository](https://github.com/ANP-Protocol/Agent-Negotiation-Protocol).

## Agent Capability Negotiation and Binding Protocol

ACNBP describes capability discovery through an Agent Name Service, candidate screening, negotiation, the provider's binding confirmation, execution and final commitment updates. Its stated purpose is acquiring capabilities beyond an agent's own scope. That broad product outcome is prior art. The paper prescribes a larger discovery/security/orchestration process than Bazaar's proposed small A2A interaction profile. [ACNBP paper, §§III–IV](https://arxiv.org/html/2506.13590v1).

The full paper text was available; its linked implementation was not executed or audited here. This is a specification-level comparison, not validation of the paper's capability-attestation or deployment claims.

## x402 Bazaar and name collisions

x402 Bazaar already describes dynamic discovery and consumption of payable HTTP endpoints and MCP tools through facilitator discovery surfaces. Therefore dynamic capability acquisition and reusing service discovery are not unique. It is a natural external discovery input for the proposed interaction contract. [Official Bazaar documentation](https://github.com/x402-foundation/x402/blob/main/docs/extensions/bazaar.mdx).

The name Agent Bazaar is also used by a [Solana marketplace project](https://github.com/Agent-Bazaar/Agent-Bazaar), an [economic-alignment research framework](https://arxiv.org/abs/2605.17698), and an [ETHGlobal RFQ/escrow project](https://ethglobal.com/showcase/agent-bazaar-m6if0). These are naming and positioning collisions. This audit does not treat their titles as evidence of identical semantics.
