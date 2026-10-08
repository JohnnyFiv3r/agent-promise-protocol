# Agent Bazaar

> **Historical 0.3 snapshot.** Superseded by the [current draft](../../README.md). Preserves the formation-only boundary before lifecycle reconciliation.

**Contract draft 0.3 · October 8, 2026 · [MIT](LICENSE)**

Agent Bazaar is an A2A extension covering **publication contract → emitted intent → qualified offers → exact adoption → accepted-offer object**. It lets autonomous agents negotiate within their principals' policies while preserving each principal's right of refusal after the agent handshake.

A promise is an agent's qualified action: an action for which it has the capability and delegated authority, within explicit conditions and limits. **An offer is a promise.** Emitting an intent promises only the declared act of communicating or seeking; it does not promise to supply the sought outcome or purchase an offered service. A request for the other agent's behavior cannot issue that agent's promise.

Agents may keep several named offers open and negotiate any commercial arrangement their owners' policies permit. Policies determine validity and budgets. The protocol imposes no universal negotiation expiry or forced resolution. Principal policies govern continuing permission; there is no standing-promise object.

The author of the explicitly identified initiating intent or promise coordinates formation. Both agents adopt the same exact terms. The coordinator then records an immutable accepted-offer object, initially subject to each principal's policy-defined refusal window. Fresh, authenticated status distinguishes a pending window, refusal, closed windows and an unresolved result. An elapsed timer is not a human signature or payment authority.

## Read the contract

Start with the **[six agent-governing contracts](contracts/README.md)**. They define the actors, guards, permitted effects, ordering and failure behavior an agent harness must enforce. The documents below explain the shared model and its boundaries.

1. [Design decisions](decisions-v0.2.md): the fifteen controlling decisions; [0.3 authoring choices](decisions-v0.3.md) make their interaction rules concrete.
2. [Core contract](contract.md): normative semantics, states, admission, formation and refusal.
3. [Universal promise/action proposal](promise-model.md): the small shared shape and service-specific semantics to refine.
4. [Publication contract](publication-contract.md): owner policies, discovery/contact consent and commercial eligibility.
5. [Accepted-offer object](accepted-offer.md): exact adoption, portable proofs, notification, refusal windows and current status.
6. [Architecture and A2A binding](protocol-architecture.md): the Bazaar boundary and native transport.
7. [Contract map](contract-map.md): ownership of the required interfaces.
8. [Semantic schema](schemas/contract.schema.json), [interaction schema](schemas/interaction.schema.json), [admission declaration](schemas/admission-policy.schema.json), [illustrative records](examples/README.md) and [verification status](validation.md).

## Where Bazaar ends

AP2, UCP or ACP, paid-resource exchange, processors, settlement and fulfillment are downstream consumers or services. Bazaar neither constructs nor validates their orders or mandates, handles payments, assesses delivery, nor defines refunds. Negotiated commercial terms may name those services; the accepted-offer object carries exact terms and evidence for their consumers.

The [downstream boundary note](downstream-boundary.md) explains how an AP2 adapter can preserve agreement provenance without turning a Bazaar proof into a payment mandate. An internal toy model may later simulate payment outside Bazaar. The testing and delivery-assessment regime is deferred until the contract is written.

## Authorship and status

Original Bazaar specification, schemas, examples and eventual implementation are MIT licensed. Comparison projects provide inspiration and critique where permitted; no implementation code, copied schemas or imported test suites are used. Third-party references retain their own licenses. See [related-work research](research/README.md).

Draft 0.3 supersedes [0.2 in Git history](https://github.com/JohnnyFiv3r/agent-bazaar/tree/0011b504b706970c54a780d700be3efe444d4898) and [archived 0.1](../0.1/README.md). The 0.1 archive preserves the earlier proposal-only offers, fixed expiry, buyer coordination and downstream payment/fulfillment contracts; those are not current requirements. This package is a specification with illustrative records, not a running marketplace or proof of interoperability.

## Check the documents

With Python 3.10 or newer, run these commands from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python checks/validate.py
```

The helper checks the three current JSON Schemas, example record shapes and local fixture digest references. It does not verify cryptographic proofs, delegated authority, capabilities, refusal timing, A2A interoperability or payments. The protocol testing regime remains a future design decision; these are document-authoring checks. See [validation status](validation.md) for the exact scope.

For proposed changes, see [CONTRIBUTING.md](CONTRIBUTING.md). Normative interfaces live in `contracts/`, their shared model at the repository root, and schemas in `schemas/`. `examples/` contains fictional records, `research/` contains related-work notes, and `archive/0.1/` preserves the historical draft.
