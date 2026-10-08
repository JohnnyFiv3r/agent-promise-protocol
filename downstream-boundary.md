# Accepted-offer compatibility with downstream commerce

**Informative integration note · October 8, 2026.** Bazaar's contract ends at its accepted-offer object and the proof/current status needed to interpret it. This document defines no Bazaar payment workflow, mandate, payment instruction or receipt.

## What a consumer receives

A consumer can retrieve the immutable accepted object, exact candidate terms, selected options, initiating intent/promise provenance, both adoption proofs, relevant policy references and current principal-window status. Commercial terms can include a negotiated price or route under their own versioned semantics. Those terms express agreement; they are not native payment authority.

The object initially records agent agreement while principal refusal remains possible. The consumer must distinguish that historical fact from a fresh authenticated observation that all required refusal windows have closed without refusal. A timestamp, stale cached closure or valid historical signature alone does not establish the latter.

## AP2-compatible association

The official AP2 specification defines a merchant-signed Checkout and native mandates covering it. The Checkout Mandate's `checkout_hash` binds the signed Checkout; the Payment Mandate references that same Checkout. The Checkout content is extensible, and native commerce such as UCP can supply its shape. AP2 does not define Bazaar's accepted object or its post-handshake refusal window. [AP2 specification](https://ap2-protocol.org/ap2/specification/), [Checkout Mandate](https://ap2-protocol.org/ap2/checkout_mandate/).

A downstream adapter should retain the accepted-object and terms digests in an authenticated native Checkout/commerce extension or another native authenticated correlation supported by its selected profile. That association should identify the particular accepted commercial subject, rather than matching only descriptive text and price. The adapter independently obtains and validates all native authority. Copying a Bazaar proof into a field does not make it an AP2 mandate.

Native authority and transaction-specific consent remain distinct. AP2's authorization framework uses its own delegated authority and trusted user interaction; Bazaar's window closure cannot manufacture a fresh human approval in that system. [AP2 authorization framework](https://ap2-protocol.org/ap2/agent_authorization/).

## Boundary for implementation

The downstream consumer owns Checkout/UCP/ACP construction, mandate handling and validation, action authorization, exchange-protocol selection, payment execution, processor interaction, settlement and any resulting receipt or refund. It also owns how native authority can be revoked after its own effects begin. None of those records or lifecycles belongs in Bazaar's schema.

Bazaar owns the truth of what its records assert: exact agent terms, authenticated self-authorship, conditions on those terms, principal refusal rights and current accepted-object status. A consumer that cannot preserve those distinctions cannot claim a faithful mapping.

## Internal toy model

A later internal consumer may simulate downstream payments using an accepted object. Its simulation results are not Bazaar record kinds and do not demonstrate AP2, UCP, ACP, payment or settlement compatibility. The testing regime and which integrations to exercise remain undecided until contract review.
