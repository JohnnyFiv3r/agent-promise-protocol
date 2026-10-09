# Sources and current decisions

**Draft 0.3 · October 8, 2026.** The [fifteen user decisions](decisions-v0.2.md) control this revision. Earlier D1–D22 entries are preserved with [archived 0.1](../0.1/sources-and-decisions.md); they are not a second current decision register.

## Promise Theory reading

Source: Jan A. Bergstra and Mark Burgess, [*Promise Theory: Principles and Applications*, second edition, 2019](https://markburgess.org/BookOfPromises.pdf).

A user-authorized GPT-6 Luna reader read the complete extracted text of all **318 PDF pages**, including notes, bibliography, and index. It repaired a skipped range and reread truncated output. The [coverage record](promise-theory-reading-coverage.json) identifies every range, the source SHA-256, and limitations. The coordinating agent separately reviewed the central definitions, conditional promises, conflicts, and invitation passages, and rendered PDF pages 104, 183, and 188. Not every equation or illustration received individual visual verification.

The book treats declared intention as a promise, distinguishes proposed descriptions from adopted promises, and leaves each agent responsible for its own behavior. Provide/receive polarity is independent of market roles. Promise scope concerns who knows of a promise; assessment belongs to observers. Invitations can progressively establish consent for interaction. Repetition does not create a new identical promise, though it can influence belief.

| Relevant section | Printed pages | PDF pages |
|---|---|---|
| Core concepts; promise proposals | 3–4, 27–28 | 19–20, 43–44 |
| Scope; polarity and cooperation | 31, 38–43 | 47, 54–59 |
| Idempotence; capacity | 47, 52–54 | 63, 68–70 |
| Assessment; conditional promises | 66–70, 78–84 | 82–86, 94–100 |
| Lifecycle; conflicts | 85–88, 96–98 | 101–104, 112–114 |
| Invitations and intrusive messages | 165–172 | 181–188 |

The qualified-action wire model, budgeting, exact-term finalization and principal refusal window are Bazaar engineering choices. The book does not prescribe these record types or lifecycle rules. Existing systems retain native authentication and downstream commerce functions.

## Native protocol sources and scope

| Source | Use in draft 0.3 |
|---|---|
| [A2A 1.0.0 specification](https://a2a-protocol.org/v1.0.0/specification/) and [extensions](https://a2a-protocol.org/latest/topics/extensions/) | Carrier/extension binding; native message, task and artifact meanings remain native. |
| [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) | Canonicalization for Bazaar content identity, excluding top-level proof references for the signed payload. Native proof bytes retain their own formats. |
| [AP2 specification](https://ap2-protocol.org/ap2/specification/) and [Checkout Mandate](https://ap2-protocol.org/ap2/checkout_mandate/) | Rechecked for an informative downstream association: exact Bazaar terms/proof can be correlated to native signed Checkout content; the consumer creates and validates native mandates. |
| [AP2 authorization framework](https://ap2-protocol.org/ap2/agent_authorization/) | Distinguish native delegated authority and trusted user interaction from Bazaar's post-handshake refusal evidence. |
| [MIT license](https://opensource.org/license/mit) | Standard license text applied to original Bazaar material; linked third-party material is not relicensed. |

The AP2 compatibility check found no native Bazaar accepted-offer type or principal-refusal window. Those are our contract semantics. The downstream note is not evidence of an implemented adapter, validated mandate or paid transaction.

## Related work

The [research ledger](research/README.md), [earlier overlap audit](novel-angle-audit.md) and [license findings](reuse-and-licensing.md) retain the source review. Comparators are inspiration and critique only where permitted; no implementation code, copied schemas or imported tests are adopted. Previous comparisons against proposal-only offers describe draft 0.1 and do not override the user's offer-as-promise decision.

## Authoring selections still requiring refinement

Draft 0.3 adds the [six governing interfaces](contracts/README.md) and records their [authoring choices](decisions-v0.3.md). These are original protocol engineering decisions, not requirements attributed to Promise Theory or copied from comparator implementations.

The [universal action shape](promise-model.md) is a concrete proposal requested by the user. The [accepted-object contract](accepted-offer.md) makes notice/start/deadline/order semantics explicit without choosing a universal duration. [C6](contracts/06-a2a-evidence.md) selects the draft extension identifier and A2A binding. Exact cryptographic suites, trust, policy, capacity and evidence-retrieval mechanisms remain deployment selections whose required outputs are specified by the contracts. Unknown required profiles block automatic interpretation rather than silently selecting a substitute.

The contract does not select an evaluation regime, correction budget, human reviewer, native payment route or runtime test suite. Those discussions follow contract authoring. Schema/reference checks are authoring validation only.
