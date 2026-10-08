# Agent Bazaar: required contracts

**Design basis:** the user's October 8, 2026 diagram and accompanying decisions. **License:** [MIT](LICENSE) for original Bazaar work. Comparison frameworks supply conceptual reference and critical review, not implementation code, copied schemas or imported test suites.

The diagram provides enough definition to author the protocol. It establishes the participants, ownership boundary, upstream consent and downstream commercial sequence. This document decomposes that boundary into eight contracts. These are responsibilities within one A2A extension and its profiles, not eight new services or network protocols.

The normative behavior is in [contract.md](contract.md), with the publication and wire-binding details linked below. Where this map names an evidence record whose schema is unfinished, normative prose remains the draft source; the map does not imply an implemented wire contract.

## Contract inventory

| ID | Contract | Boundary | Required result |
|---|---|---|---|
| C1 | Publication and discovery consent | Existing discovery/subscription service or service source ↔ its agent harness | An attributable, current policy for carrying declarations and permitting contact |
| C2 | Intent emission | Emitter → permitted discovery recipients or A2A counterpart | A declaration of what is sought, without an implied exchange commitment |
| C3 | Negotiation admission and iteration | Each recipient ↔ counterpart and its delivery services | Bounded permission to engage, with consistent revision and replay accounting |
| C4 | Offers and self-authored promises | Agent A ↔ Agent B | Proposed behavior, requested reciprocals and actual promise issuance remain distinguishable |
| C5 | Accepted offer and agreement formation | Both agents → agreed formation procedure | Durable evidence of each party's adoption of the same exact terms and route |
| C6 | A2A extension binding | Each Bazaar harness ↔ native A2A interface | The same meaning and evidence survive native messages, tasks, artifacts and retries |
| C7 | Native commercial handoff | Accepted agreement ↔ AP2, selected checkout/payment protocols and processors | Native order/payment operations demonstrably correspond to the accepted agreement |
| C8 | Fulfillment and assessment binding | Accepted agreement ↔ offered service, evaluator and recipient | Attributed delivery and assessment evidence, interpreted under the selected performance profile |

## C1. Publication and discovery consent

Both upstream boxes use the same contract. One may express user-set discovery criteria; the other may express a provider's business rules and eligible offers. Buyer/provider roles are not fixed by which source supplied the harness.

The issuer declares its own publication subject, immutable revision, audience, permitted uses, contact policy, policy validity/status and complete eligible commercial routes. Criteria and service-specific sales rules are versioned policy references. Publication records contain no credentials or spending grants.

A participating discovery or delivery service MUST preserve the issuer and original policy references, check current applicable consent, restrict delivery and use accordingly, and refuse unsupported required semantics. The service may filter, rank or decline publications under its own rules. It cannot broaden consent, adopt another agent's promise, or accept commercial terms on an agent's behalf merely by carrying the publication. A carrier's obligation to honor this contract is its own behavior; the issuer's permission alone does not prove carrier compliance.

Withdrawal or expiry stops new activity under that permission. It does not erase history, cancel an accepted agreement or revoke a native mandate. The two parties' eligible routes constrain C5 and C7.

**Authoritative fields and behavior:** [publication contract](publication-contract.md), [core §4](contract.md#4-intent-emission-and-publication).

## C2. Intent emission

An intent names its emitter, revision chain, market posture, desired outcome, preferences, disclosure audience, expiry and exact C1 publication reference. `seek_result`, `seek_work` and `seek_collaboration` describe what the emitter seeks. Price preferences and capability assertions retain their stated status as preferences and claims.

An intent MUST NOT acquire offer, purchase, reservation or execution semantics because it was published, matched, relayed, received or acknowledged. The emitter owns revisions. Repeated observations of identical content are duplicates; conflicting content at one revision is rejected or quarantined. A revision cannot reset C3 allowances.

Broadcast means permitted dissemination through existing discovery/subscription services. It is not permission to send offers to every endpoint that can be located. A recipient may observe an intent and choose not to interact.

**Authoritative fields and behavior:** `intent` in the [schema](schemas/contract.schema.json), [core §4](contract.md#4-intent-emission-and-publication).

## C3. Negotiation admission and iteration

Each recipient controls admission to its own side of the conversation. Permission identifies the eligible sender or sender class, topic/intent, admitted message purposes, absolute lifetime and finite message/byte allowances. The selected admission profile also defines aggregate ingress and active-channel limits, enforcement and current policy status. Reciprocal communication needs the other recipient's consent too.

Admission MUST precede model inference. A relay, alternate discovery path, fresh channel identifier or restart cannot create a fresh allowance for the same logical interaction. Deduplication and budget updates must be consistent at the recipient's enforcement boundary. Revisions consume the selected allowance once; transport duplicates cannot create new offer heads, renew expiry or produce another commitment.

The profile MUST retain a bounded status/closure path for resolving already-pending acceptance after proposal capacity is exhausted. It must not allow proposals to masquerade as status messages. Silence does not renew consent. Ending with no agreement is a valid outcome.

These are protocol requirements derived from recipient autonomy; numerical limits are deployment/profile choices, not mathematical consequences of Promise Theory.

**Authoritative behavior:** [core §5](contract.md#5-invitation-and-negotiation-admission); [reference admission profile](reference-negotiation-profile.md) supplies concrete permits and demo limits.

## C4. Offers and self-authored promises

Either agent can issue an offer. An offer identifies its author, channel, previous own offer, relevant peer offer, offering specification, exact performance terms, publication references, proposed settlement terms, route and expiry. It separates proposed own promises from requested counterpart promises.

Each promise description identifies the promiser, promisees, provide or receive/use polarity, typed behavior, conditions, limits and assessment method. A request describing the counterpart's behavior MUST remain a request until that counterpart adopts it. Authenticated adoption and the relevant commitment authority are required to issue a promise. The protocol validates authorship and evidence; it cannot guarantee capability or future fulfillment from a claim.

Each party has one current offer head per channel. Its revision supersedes only its own previous head. Crossed proposals remain proposals. A candidate cannot combine an old price with a new scope without explicit agreement on that combination. Offer proposals and standalone issued promises retain separate lifecycles; closing a conversation does not silently withdraw every promise.

**Authoritative fields and behavior:** `offer`, `promise_description` and `promise_issued` in the [schema](schemas/contract.schema.json), [core §6](contract.md#6-offers-counteroffers-and-promises).

## C5. Accepted offer and agreement formation

An accepted offer is an evidence bundle, not a flag derived from matching messages. It names both current offer heads, exact terms and referenced specifications, each party's own adoptions, the formation profile, pinned publication policies and one eligible commercial route.

The selected procedure MUST define the acceptance point, capacity/selection limits, pending-state reconciliation, deadline authority and durable record retrieval. One party cannot finalize another party's unadopted promises. Material term changes require fresh adoption. A lost acknowledgment leaves the observer uncertain until it retrieves the original outcome; it does not authorize another purchase.

The first bilateral profile uses candidate → buyer award and own adoption → provider own adoption → buyer finalization. This procedure is a declared reference-profile choice. The core does not require every conforming deployment to use a buyer coordinator, but every formation profile must preserve exact acceptance, self-authorship and duplicate-commitment protection.

Commercial acceptance supplies the input to C7. It does not by itself grant native tool access, establish that work was delivered or prove payment.

**Authoritative behavior:** [core §7](contract.md#7-bilateral-reference-formation-profile). Candidate terms have a schema; complete formation-receipt wire schemas remain to be authored.

## C6. A2A extension binding

Agent Cards advertise the versioned extension and supported profiles; participants activate and acknowledge it before applying its semantics. Bazaar records travel in native A2A data parts and artifacts with exact content references. Negotiation and execution retain the native task lifecycle; Bazaar's commercial states remain extension data.

The binding maps authenticated native identity to the record issuer, preserves original authorship when forwarding, and requires retrievable durable adoption/finalization evidence. A message-role label, task completion or transport receipt MUST NOT substitute for a promise, agreement or fulfillment decision. Endpoint-local task/context identifiers remain local; shared agreement references link the participants.

Native authentication and proof mechanisms supply identity and cryptographic verification. Bazaar specifies the coverage and association they must establish. No new transport, task RPC or signature algorithm is required.

**Authoritative mapping:** [A2A extension binding](protocol-architecture.md#a2a-extension-binding), [A2A examples](examples/a2a/README.md).

## C7. Native commercial handoff

For a paid route, the required sequence is accepted offer → AP2 order validation/commitment → selected paid exchange → selected processors and settlement. UCP or ACP supplies native commerce objects when selected. Existing open delegation may precede the negotiation, but does not accept its eventual offer.

The binding MUST associate native order and payment evidence with the exact finalized agreement, agreed obligation, parties, route, commercial limits, trigger and stable action identity. That association must be authenticated and durable through the selected native system; a Bazaar wrapper cannot manufacture native authority. Terms and route checks are performed before the dependent external action.

A payment challenge creates no new permission. Unknown native outcomes require reconciliation under the original operation identity. The same native effect cannot be counted twice against different obligations. Changes outside the accepted route require renewed agreement. Native protocols own mandate validation, charging, custody, receipts, settlement and refunds; Bazaar authors the association and precondition contract.

**Authoritative fields and behavior:** `external_binding` in the [schema](schemas/contract.schema.json), [core §8](contract.md#8-native-fulfillment-order-commitment-and-payment-binding), [native binding map](protocol-architecture.md#native-authority-and-payment-bindings).

## C8. Fulfillment and assessment binding

The offering specification and performance profile define what is delivered: MCP endpoint access, an API, a proprietary dataset, a research artifact or another product/service. The accepted terms select evidence requirements, evaluator, acceptance procedure, timing and any corrections or remedies.

Provider delivery, evaluator assessment and recipient acceptance are separately attributable records. Native task completion is not proof that the promise was kept; payment is not acceptance of quality. Missing or disputed evidence retains an unresolved outcome under the selected profile. Cancellation records known effects and cannot imply rollback or refund without native evidence.

The core standardizes references and meaning; the performance profile defines product-specific criteria. The research demonstration supplies a source-backed report, claim-to-source evidence and named human assessment. It does not impose research fields on every service.

**Authoritative behavior:** [core §9](contract.md#9-delivery-assessment-acceptance-and-cancellation), [research profile](product-spec.md#5-research-demonstration). Complete assessment/acceptance wire schemas remain to be authored.

## What the diagram settles, and what the draft supplies

The diagram settles actor symmetry, the publication boundary, Bazaar's ownership of A2A negotiation through accepted offer, general service scope and the downstream commercial sequence. These are sufficient architectural inputs.

The draft supplies explicit choices for proposal firmness, revision identity, consent withdrawal, replay, race handling, no-agreement closure and acceptance evidence. Configurable admission limits, a selected proof/trust profile, a publication URI and exact native integration versions are profile/release selections. They do not require another product diagram or prevent contract authoring.

The current specification is a normative first draft with partial machine-readable coverage. Wire completion and conformance execution are distinct next steps: [validation status](validation.md). Neither the diagram nor source inspection establishes implemented interoperability.
