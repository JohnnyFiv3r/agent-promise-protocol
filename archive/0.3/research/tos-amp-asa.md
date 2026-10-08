# Recursive comparison: TOS Intent Exchange, AMP and ASA

**Baseline note:** this comparison was authored against draft 0.1. Statements about Bazaar’s former proposal-only offers, fixed validity or payment scope are historical. The [draft 0.2 decisions](../decisions-v0.2.md) govern the current contract; external findings remain source-review observations.

Checked October 8, 2026. This is a source and code inspection, not an execution or adoption audit.

## Finding

**TOS is the strongest collision. The broad thesis “symmetric emitted intent → nonbinding proposals → self-authorized agreement → separately authorized execution/payment” is already present, including code for important authorization invariants.** AMP plus ASA also covers discovery, quotes, bounded negotiation, two-party agreement, quality verification and payment integration. None of those steps establishes differentiation by itself.

Agent Bazaar has a distinct architectural target: a small, portable behavioral contract carried directly by A2A, combining independently authored provide/receive behavior with service-independent publication/reception consent. The distinction becomes meaningful when it produces observable interoperability across existing discovery providers, without requiring their matching algorithms, identity stack, runtime, evaluator or settlement machinery. Renaming obligations as promises would not accomplish that.

## Method and exact scope

Retrieved public repositories without running their code:

| Source | Exact revision | Inspected surface |
|---|---|---|
| [TOS service specification](https://github.com/tosnetwork/tos-service-spec/tree/80739a8f670e335e581e5b99eef54ad032d5cf3d) | `80739a8f670e335e581e5b99eef54ad032d5cf3d` | Intent Exchange; root operation architecture; Messenger contact/admission and conversation-to-commerce; A2A adapter; x402 decision; Guarantor firm-offer profile; implementation report; commerce schema and reference verifier |
| [TOS protocol implementation](https://github.com/tosnetwork/tos-service-protocol/tree/a70ee803611dcd51a584b42015154b0f443d4d55) | `a70ee803611dcd51a584b42015154b0f443d4d55` | `pkg/agentcommerce/intent.go`, `application.go`, `agreement.go`, `agreement_profiles.go` and corresponding tests |
| [Agent Matchmaking Protocol](https://github.com/alexfleetcommander/agent-matchmaking/tree/40a55ca3804fc806dee6e96a942b69ef5af53018) | `40a55ca3804fc806dee6e96a942b69ef5af53018` | Whitepaper; schemas; capability conversion; federation; RFQ/pricing and tests |
| [Agent Service Agreements](https://github.com/alexfleetcommander/agent-service-agreements/tree/d86945286402a298a7262e297c2d9bade38e48ea) | `d86945286402a298a7262e297c2d9bade38e48ea` | Whitepaper; agreement; negotiation; configuration and lifecycle tests |

Also opened the [AMP hosted whitepaper](https://www.vibeagentmaking.com/whitepaper/matchmaking/). Pinned repository files govern this comparison where versions differ. No market-share, independent-deployment or production-transaction inference is made from a README or test name.

Compared against local [contract](../contract.md), [publication contract](../publication-contract.md) and [schema](../schemas/contract.schema.json).

## Feature matrix

**D** means explicitly documented. **C** means supporting code was inspected; it does not mean runtime verified. “Not found” refers to the inspected surface, not a proof of ecosystem-wide absence.

| Thesis element | TOS Intent Exchange and linked protocols | AMP plus ASA | Agent Bazaar consequence |
|---|---|---|---|
| Symmetric demand/supply/collaboration declarations | **D+C:** REQUEST, OFFER, BUY, SELL, EXCHANGE, COLLABORATE and ANNOUNCE modes. Advertisement fields do not establish availability or authority. [T1][T2] | **D+C:** requester task and supplier capability profiles; matching and RFQ. Less symmetric object model, but both market sides exist. [A1][A2] | Symmetry alone is shared prior art. |
| Intent is not an accepted offer or authority | **D:** publication, application, proposal, agreement and actions are separate. **C:** application and agreement have distinct types/validators. [T1][T3] | **D+C:** quotes, selection, negotiation and signing are separate structures/actions. [A2][S1] | Necessary invariant, not a novel discovery. |
| Only an actor can authorize its own behavior | **C:** each obligation requires its obligor's predicate; authorization requires exact scoped evidence; wrong-obligor and missing-evidence cases exist. [T4][T5] | **D+C:** client/provider signing precedes active agreement, although inspected signing method only stores signature strings. [S1] | Self-authorship safety already overlaps materially. |
| Provide/receive polarity independent of buyer/seller roles | No explicit Promise Theory polarity grammar found in inspected code/docs. Generic obligation kinds/subjects could express such behavior through a profile. [T4] | No explicit polarity grammar found in inspected schemas. Contracts are organized around client/provider/service/evaluator. [S1][S2] | A specific interoperable behavior grammar remains a design difference; field naming alone is insufficient. |
| Standalone authored promises independent of bilateral formation | No general provide/receive promise-issuance primitive found. The linked Guarantor profile does define a pre-acceptance firm commitment, bound to exact coverage terms. [T4][T12] | No equivalent found in inspected agreement/negotiation surface. [S1][S3] | General standalone promise semantics remain a candidate difference; pre-acceptance commitments alone do not. |
| Recipient controls first contact | **D:** Messenger descriptor commits to open, invite-only, allowlisted or proof-limited inbox policy. [T6] | AMP gives registries control over exposure and discusses query privacy; recipient-first commercial-contact policy not found in inspected schema. [A1] | Do not claim TOS lacks consent. Bazaar can standardize its meaning across non-TOS services. |
| Finite iteration and anti-spam controls | **D:** operation budgets, inbox tickets, quotas and bounded counteroffer policy; linked negotiation document is incubation with precedence explicitly assigned to Intent Exchange. [T7][T8] | **D+C:** ASA max-round counteroffers; timeout configuration. No equivalent directional byte budgets and cross-carrier aggregate limits found in inspected implementation. [S3][S4] | Iteration bounds are shared; portable recipient-owned aggregate enforcement is a narrower contribution. |
| Existing discovery services remain independent | **D:** replaceable carriers/indexes; root operation/identity/propagation substrate remains TOS-defined. [T7] | **D+C:** registry adapters, federated queries and normalization; AMP standardizes matching and trust ranking. [A1][A3] | Reuse AMP/discovery as providers; do not build another matching/ranking protocol. |
| Thin A2A-native behavioral extension | TOS has an A2A extension, but the inspected one transports paid software work into TOS authority, quote and escrow gates. Generic negotiation uses Messenger. [T9] | A2A/MCP conversion and communication compatibility documented; an A2A wire extension for the entire consent/promise negotiation was not found. [A4][S2] | This is a concrete boundary difference, not a claim that competitors ignore A2A. |
| AP2 after accepted offer; exchange and settlement downstream | TOS commits settlement adapters/parameters, has external adapters, and mentions AP2 strategically. Inspected x402 adapter is deferred; native TOS settlement remains that profile's authority. [T10][T11] | AMP lists ACP/UCP/x402/ERC-8183 and ASA handoffs; ASA defines external escrow binding. No matching AP2 order-commitment profile found in inspected code. [A1][S2] | Exact bindings could differentiate composition, but an unimplemented flow diagram is not integration evidence. |

## What the recursive inspection changed

### TOS is more than an intent bulletin board

The Intent Exchange document explicitly separates nonauthorizing advertisements/proposals from agreements and side effects. Its settlement preferences are invitations; exact selection moves into an agreement. It supports varied products and reciprocal exchanges. These overlap the product thesis directly. [T1]

The stronger collision is in code: `ValidateAgreementBody` checks each obligation's obligor predicate; `ValidateAgreementAuthorization` requires complete evidence. `TestAgreementRequiresAcyclicObligorAuthorizedGraph` deliberately removes the proper obligor authorization, and `TestCompleteAgentEvidenceAuthorizesAgreement` rejects incomplete evidence and replay onto altered terms. That is the operational counterpart of “you cannot promise another autonomous agent's behavior for it.” [T4][T5]

Following the links also finds inbox policies, admission proofs and quotas. It would be incorrect to manufacture differentiation by saying TOS permits unlimited unsolicited offers. Its system boundary is broader: TOS specifies operation identity, authority and propagation, with Messenger and optional native settlement. Bazaar's intended boundary is the behavioral semantics carried over existing A2A deployments. [T6][T7][T9]

A further recursive check reaches the Guarantor profile: its targeted firm coverage offer is a bounded commitment before customer acceptance, backed by reserved exposure and pinned agreement terms. Therefore “only Bazaar supports promises before bilateral acceptance” would also be too broad. No general-purpose provide/receive promise grammar was found in that specialized profile. [T12]

The header's “implementation-complete release candidate” is the project's status claim; it also says external production acceptance is pending. The code inspection corroborates specific primitives, not the entire claimed lifecycle. [T1]

### AMP and ASA must be compared as a composition

AMP's RFQ path solicits task-specific quotes from matched agents; its whitepaper hands accepted matches to ASA. The reference `RFQSession` collects/ranks/selects quotes, while federation uses adapters. ASA then provides proposed/countered/accepted terms and a separate signing transition. Treating AMP as just a directory would miss the closest overlap. [A1][A2][A3][S1]

ASA's negotiation code enforces a round maximum. It carries `timeout_seconds`, but the inspected proposal/counter/accept methods do not check elapsed time. It computes asymmetry violations in `counter()` without acting on that result. Its `sign()` method activates once both signature strings are populated and does not itself authenticate them. These are implementation limits, not evidence that the documented concepts belong uniquely to Bazaar. [S1][S3][S4]

ASA also standardizes quality dimensions, evaluator behavior and escrow release. Those are attractive optional performance profiles for Bazaar, but reproducing them inside Bazaar core would drift toward ASA's system. [S2]

## Distinct product angle and design constraints

A defensible formulation is:

> Agent Bazaar standardizes how autonomous agents disclose interest, admit conversation, propose their own provide/receive behaviors and adopt exact promises across existing discovery services and A2A implementations. It binds the resulting agreement to existing order and payment protocols.

The contribution is the **portable semantic and consent contract**, not the invention of agent intent markets, autonomous offers or authenticated assent.

Preserve these boundaries:

1. **Make polarity produce behavior.** Demonstrate independent promises to provide inputs, receive inputs, produce an artifact and receive/review it. Show that receiving an artifact, assenting to terms and accepting quality are distinct events. A `receive` string with no interoperable checks would be decorative.
2. **Demonstrate the service boundary.** One publication passes through two independently implemented discovery/subscription providers. Neither broadens contact consent; duplicates and revisions cannot replenish a shared negotiation budget. That tests the user’s business-rule thesis rather than recreating a marketplace.
3. **Keep existing systems useful.** AMP can supply discovery results. ASA can supply a selected performance/evaluation profile. A TOS adapter could preserve its native acceptance evidence. Bazaar must not require replacing those systems to use its promise grammar.
4. **Do not claim a unique self-authorship invariant.** Attribute the broader intent/proposal/obligation pattern as prior art. Test the stronger claim: independent parties and intermediaries preserve the same speech-act meaning across protocols.
5. **Bind downstream protocols precisely.** An accepted offer must pin the selected publication route and exact native order scope. Confirm the AP2/exchange adapter actually enforces that relationship before using end-to-end interoperability as evidence.

Recommended novelty proof: two discovery services, two independent A2A agents, one externally specified service, reciprocal own-behavior offers, finite revisions, one attempted unauthorized third-party promise, one consent withdrawal, and one accepted offer that alone permits downstream order/payment progression. Keep the source-backed research deliverable as the payload; the novel behavior is in the cross-system semantics.

## Pinned primary pointers

- [T1 — Intent Exchange §§2, 4–6, 9–10, 19](https://github.com/tosnetwork/tos-service-spec/blob/80739a8f670e335e581e5b99eef54ad032d5cf3d/docs/AGENT_INTENT_EXCHANGE_V1.md)
- [T2 — symmetric intent modes and typed publication payload](https://github.com/tosnetwork/tos-service-protocol/blob/a70ee803611dcd51a584b42015154b0f443d4d55/pkg/agentcommerce/intent.go#L34-L158)
- [T3 — intent application conformance case](https://github.com/tosnetwork/tos-service-protocol/blob/a70ee803611dcd51a584b42015154b0f443d4d55/pkg/agentcommerce/application_test.go#L8-L30)
- [T4 — obligation validation and authorization](https://github.com/tosnetwork/tos-service-protocol/blob/a70ee803611dcd51a584b42015154b0f443d4d55/pkg/agentcommerce/agreement.go#L355-L461)
- [T5 — obligor, incomplete evidence and altered-body rejection tests](https://github.com/tosnetwork/tos-service-protocol/blob/a70ee803611dcd51a584b42015154b0f443d4d55/pkg/agentcommerce/agreement_test.go#L149-L228)
- [T6 — Messenger §10.2 inbox admission policy](https://github.com/tosnetwork/tos-service-spec/blob/80739a8f670e335e581e5b99eef54ad032d5cf3d/docs/AGENT_NATIVE_MESSENGER_V1.md#L1570-L1601)
- [T7 — root architecture and spam/admission controls](https://github.com/tosnetwork/tos-service-spec/blob/80739a8f670e335e581e5b99eef54ad032d5cf3d/docs/TOS_AGENTIC_INTERNET_OPERATION_ARCHITECTURE_V1.md#L281-L315)
- [T8 — conversation profile precedence and bounded negotiation](https://github.com/tosnetwork/tos-service-spec/blob/80739a8f670e335e581e5b99eef54ad032d5cf3d/docs/AGENT_NATIVE_MESSENGER_CONVERSATION_AND_COMMERCE_V1.md#L280-L303)
- [T9 — existing TOS A2A software-work extension](https://github.com/tosnetwork/tos-service-spec/blob/80739a8f670e335e581e5b99eef54ad032d5cf3d/docs/A2A_ADAPTER_V1.md)
- [T10 — x402 adapter decision](https://github.com/tosnetwork/tos-service-spec/blob/80739a8f670e335e581e5b99eef54ad032d5cf3d/docs/X402_ADAPTER_DECISION.md)
- [T11 — AP2 and surrounding protocols in TOS strategy](https://github.com/tosnetwork/tos-service-spec/blob/80739a8f670e335e581e5b99eef54ad032d5cf3d/docs/PRODUCT_STRATEGY.md#L102-L169)
- [T12 — Guarantor profile, especially §§3 and 6: firm offers and separate acceptance](https://github.com/tosnetwork/tos-service-spec/blob/80739a8f670e335e581e5b99eef54ad032d5cf3d/docs/AGENT_GUARANTOR_SERVICE_V1.md)
- [A1 — AMP specification, especially §§3.5, 7.4 and 8](https://github.com/alexfleetcommander/agent-matchmaking/blob/40a55ca3804fc806dee6e96a942b69ef5af53018/agent_matchmaking_whitepaper.md)
- [A2 — executable RFQ structure](https://github.com/alexfleetcommander/agent-matchmaking/blob/40a55ca3804fc806dee6e96a942b69ef5af53018/agent_matchmaking/pricing.py#L85-L215)
- [A3 — registry adapters and federation router](https://github.com/alexfleetcommander/agent-matchmaking/blob/40a55ca3804fc806dee6e96a942b69ef5af53018/agent_matchmaking/federation.py)
- [A4 — A2A and MCP capability converters](https://github.com/alexfleetcommander/agent-matchmaking/blob/40a55ca3804fc806dee6e96a942b69ef5af53018/agent_matchmaking/ucp.py#L199-L257)
- [S1 — ASA agreement representation and signing lifecycle](https://github.com/alexfleetcommander/agent-service-agreements/blob/d86945286402a298a7262e297c2d9bade38e48ea/agent_service_agreements/agreement.py#L24-L143)
- [S2 — ASA specification, especially §§4, 7–8 and 11.4](https://github.com/alexfleetcommander/agent-service-agreements/blob/d86945286402a298a7262e297c2d9bade38e48ea/agent_service_agreements_whitepaper.md)
- [S3 — ASA negotiation implementation](https://github.com/alexfleetcommander/agent-service-agreements/blob/d86945286402a298a7262e297c2d9bade38e48ea/agent_service_agreements/negotiation.py#L21-L178)
- [S4 — ASA negotiation tests, including max rounds](https://github.com/alexfleetcommander/agent-service-agreements/blob/d86945286402a298a7262e297c2d9bade38e48ea/tests/test_negotiation.py)

No source inspected establishes that an independent standards body or broad installed base has adopted any of these proposals. No absence claim in this report should be read as proof that no other implementation or extension exists.
