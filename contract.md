# Agent Bazaar A2A interaction contract

**ABP 0.2-draft · October 8, 2026 · [MIT](LICENSE)**

`MUST`, `MUST NOT` and `SHOULD` state requirements for a conforming participant. Each participant enforces them under its own authority. They do not confer power over another autonomous agent.

## 1. Scope and controlling decisions

The contract covers **publication through the accepted-offer object**, including the proofs and principal-refusal status needed to interpret that object. It owns emitted intent, qualified promises, admission, iterative alternative offers, exact adoption and originator-coordinated finalization.

AP2/UCP/ACP validation, payment, settlement, fulfillment and delivery assessment are outside the contract. Bazaar may carry agreed references to those systems; it neither implements their state machines nor issues their authority. The [user decisions](decisions-v0.2.md) supersede draft 0.1. The [contract map](contract-map.md) identifies the six current interfaces.

## 2. Promise and act semantics

A promise is an agent's qualified action: the agent has the capability and delegated authority to perform the action within explicit conditions, limits and policy validity. Capability and authority are separate qualifications. A signature authenticates an assertion; it does not make a false capability assertion true.

An offer IS a promise. Issuing an offer adopts its author's identified conditional `own_promises`. There is no proposal-only offer that silently becomes a promise later. A request for counterpart behavior remains a request until the counterpart issues/adopts its own corresponding promise. Exact agreement selects the reciprocal terms and conditions on already qualified actions.

An intent's `emission_promise` is scoped to the qualified act of declaring or seeking. It does not promise the desired outcome, buy a service, reserve capacity or issue anyone else's performance promise. Market posture, action type and provide/receive polarity remain independent. Either agent may seek a result or work, provide inputs, receive information, offer a service or coordinate when it is the originator.

There is no standing-promise class. Continuing permission lives in principal policy. An explicit action promise may exist without an agreement, with its own scope and validity. Unknown required action semantics or unresolved qualification prevent automatic issuance/adoption. The [universal action proposal](promise-model.md) defines the shared structure and its extension boundary.

## 3. Common records, proof and policy

Records carry a versioned profile, kind, ID, issuer agent/principal, creation time, typed body, required-extension identifiers and proof references. Content identity uses RFC 8785 canonical JSON, UTF-8 and SHA-256. Duplicate member names and values outside the canonical JSON profile MUST be rejected. Money or precision-sensitive quantities use explicitly defined units and exact representations under their semantic profile.

Portable proof references name the existing suite and verification method, issuer, scope, signed payload digest and original native proof material. The payload digest covers the record excluding its top-level proof references. A conforming verifier MUST establish through the selected native suite that the proof authenticates those bytes, issuer and scope. Self-declared proof metadata is insufficient. Original native evidence retains its native bytes and verification rules.

Identity and authority are supplied by existing principal/delegation systems. Agent Card identity or transport authentication does not itself sign every later promise. Relay records preserve the original issuer and proof. Required referenced terms, policies, definitions and evidence must be accessible and digest-verifiable by authorized participants; an unresolved reference does not establish acceptance.

Each required policy selects its authenticated status authority, clock/order, finite evidence freshness and skew handling. Issuance, adoption and finalization preserve the evidence and decision order used. Known newer revocation cannot be replaced by stale active status. This establishes policy-defined freshness, not globally instantaneous withdrawal across independent services.

## 4. Publication and intent

The [publication contract](publication-contract.md) declares audience, permitted uses, contact mode, business-rule/delegation references, validity and commercial eligibility. Existing services may add discovery, ranking and subscriptions. They MUST NOT expand consent, manufacture offers, adopt promises for another agent or reinterpret matching as agreement.

Broadcast means permitted publication or subscription delivery. An intent includes exact publication policy and qualified emission/seeking scope, its requested outcome and preferences. Pricing/capability preferences are not the service offer the emitter has not yet issued. Revision chains preserve immutable history. Identical observations are duplicates; conflicting content at one revision is rejected or quarantined.

Publication and later negotiation are separately scoped. Negotiation is private by default, including offers and exact accepted terms. Explicit consent governs any additional disclosure.

## 5. Admission, budgets and validity

Recipients select admission mechanisms through their policies. A policy may permit a bounded first offer, require an invitation, or close contact. There is no mandatory preliminary invitation if current policy already admits the offer. Missing required permission means no admission.

Before model processing, the recipient MUST check sender, scope, policy, message purpose, validity, content size, operation identity and remaining allowances. Finite traffic/work and active-capacity budgets must be enforced consistently across discovery/transport paths serving that recipient. Logical admission, deduplication and accounting must be atomic at the recipient's chosen enforcement boundary.

Validity MUST be declared by policy and understood: an explicit deadline, until withdrawn, or another referenced rule. The protocol MUST NOT impose a universal negotiation lifetime or infer an outcome from inactivity. An exhausted budget restricts additional work; it does not terminate an offer, revoke a promise, force agreement or create new consent. Explicit, attributable policy may permit replenishment or extension. Sender traffic and fresh IDs cannot cause implicit renewal.

Duplicate identity/content returns the original logical outcome. Conflicting reuse is rejected. Alternative offers and clarifications consume their applicable allowances; they cannot masquerade as status/control traffic. The principal refusal and status mechanisms remain accessible under their declared bounded policies independently of proposal-budget exhaustion.

The [reference admission note](reference-negotiation-profile.md) is illustrative. No fixed quota, timer, permit format or coordination service is universal.

## 6. Alternative offers and qualification

Each negotiation may contain multiple named offer options from each agent. An option has an immutable identity, author and revision chain. A revision replaces only that option's prior revision. It does not close other options or mutate a selected/pinned candidate. Offers identify their own qualified actions, addressed counterpart requests, offering/terms semantics, applicable policies and commercial conditions.

Shared resources and mutually exclusive alternatives MUST be exposed through understood selection/capacity constraints. An agent cannot multiply its capacity by creating more option IDs. A promise conditional on one selection must say so. Capacity, authority and policy status are rechecked where relevant at issuance, adoption and finalization.

Competing options may differ in scope, price, timing and route. For one candidate, selected options must reconcile to a single exact set of terms. Neither coordinator nor consumer may splice a superseded price into a different scope or silently omit a counterpart condition. Material differences require further negotiation or a different candidate.

The agents may negotiate any complete commercial arrangement their owners' policies permit. They need not share an identical prepublished route object or registry identifier. Both policy checks must cover the same complete candidate arrangement; permitted components do not establish that their combination is allowed. Policy expansion requires the owner's actual authority, not an agent declaring its preferred route compatible.

## 7. Origin and exact adoption

A negotiation identifies its initiating intent/promise/offer by immutable reference. The authenticated author of that origin is the declared coordinator. Buyer/provider roles, relay position and untrusted arrival timestamps do not determine coordination. For crossed independent openings, participants must agree on one explicit origin before sharing a candidate; neither silently overrides the other.

If an offer is itself the first initiating record, its own `origin` uses an explicit self-origin marker containing its record ID and authenticated author/coordinator, without a digest of itself. All later records identify that offer with an ordinary content-digest reference. A self-origin marker is valid only on the initiating offer, never on candidate/adoption/accepted records; this avoids a circular content hash without weakening origin attribution.

A candidate identifies the origin/coordinator, agents/principals, selected option revisions, exact own promises, complete terms, policy references/eligibility evidence, selection constraints and refusal rules. Its refusal rules include each principal's positive review duration, notice rule/destination, refusal authority and current-status/clock policy. These rules are part of the terms both parties adopt.

Each party issues an authenticated `terms_adoption` for the same candidate digest and its own promises, within its delegated authority. It cannot adopt another party's requested action on that party's behalf. A transport acknowledgment, discovery match, unsigned paraphrase, silence or inferred conversational agreement is not an adoption record.

A party may directly accept an offered option without first issuing a reciprocal offer. Its adoption can confirm its previously issued qualified actions or issue the qualified own actions requested of it in the candidate. Where it undertakes no separate performance action, its adopted service-promise list may be empty; the act of adoption still requires capability and authority. The candidate alone issues neither party's new promises. Selection may contain one or several compatible options under the declared constraints. Both agents still adopt the same complete terms.

Policies define how long an adoption or candidate remains valid. Unknown state remains unknown; the contract imposes no timeout that automatically accepts or rejects it. An explicit withdrawal or revision must be reconciled before relying on the affected adoption.

## 8. Finalization and accepted offer

After verifying the exact adoptions, qualifications, current policies and selection constraints, the originator coordinates one durable finalization for that formation operation. It serializes conflicting option/selection operations according to the declared mechanism and emits an immutable `accepted_offer` naming the candidate and both adoptions. Retries retrieve the same result; they cannot create a second acceptance or silently select another alternative.

The accepted object records agent agreement with initial status `pending_refusal_windows`. It MUST NOT be represented as cleared principal review or native execution/payment authority. The [accepted-offer contract](accepted-offer.md) defines notice, principal review, status and replacement in detail.

The coordinator can record a counterparty adoption only with attributable evidence. Coordination grants no control over that party's behavior. Guarantees hold within conforming participants and their declared selection/ordering scope; the protocol cannot physically prevent a dishonest actor from issuing conflicting promises elsewhere.

## 9. Principal refusal after the agent handshake

Each relevant principal retains the right of refusal for the positive period fixed by its policy in the adopted terms. Neither agent can erase or shorten that period during finalization. It is separate from policy-defined offer or negotiation validity.

Each window starts no earlier than finalization and authenticated delivery/availability of the final terms and usable refusal mechanism at the principal's designated channel. A queued message or unsupported agent assertion is insufficient. The default derivation is the later of finalization and verified notice, plus the adopted duration. Missing required notice leaves the window pending/unresolved.

A principal or its explicitly authorized representative can refuse the exact accepted object. The declared authority's clock and durable ordering determine admission. A valid refusal admitted at or before the deadline prevails; closure is recorded strictly afterward, once relevant events are reconciled. Both principals' requirements must be satisfied before status can report `refusal_windows_closed`.

An authenticated status snapshot binds object digest, monotonic status, evidence, times and freshness. `pending_refusal_windows`, `refused`, `refusal_windows_closed` and `unresolved` are object interpretation states, not commerce/payment states. Unknown or stale evidence cannot establish clearance. Expiry of the refusal period is operation under prior principal delegation, not a fabricated human signature.

Refusal preserves history and prevents reliance on that accepted object. It does not perform a downstream refund or reverse an external effect. A refused object cannot be revived by deleting its refusal; a new agreement needs a linked replacement and fresh adoptions.

## 10. Withdrawal and immutable replacement

Issuers may withdraw their own intent, action promise or offer option according to its validity/policy. Events retain target identity, authority and ordering. Withdrawing one alternative does not withdraw another. Closing contact is not automatically the same act as withdrawing all promises or refusing accepted terms.

Accepted bytes do not change. A material change creates a linked replacement with fresh adoption, explicit handling of outstanding commitments and new principal-window evidence. No replacement silently erases a prior native effect or reuses authority for altered terms. Effects outside Bazaar remain subject to their own systems.

## 11. A2A binding and downstream boundary

The [architecture](protocol-architecture.md) specifies extension advertisement/activation, native message/artifact carriage and portable proof. Native A2A task states remain task states. They cannot substitute for offer issuance, exact adoption, finalization or principal-window status.

Bazaar's output supplies immutable terms, their provenance/proofs, policy references and sufficiently fresh accepted-object status. It contains no AP2 mandate, payment instruction, paid receipt, delivery assessment or settlement state. A downstream consumer must perform its own native validation and obtain its own authority. The [AP2 compatibility note](downstream-boundary.md) identifies how native commerce can preserve the accepted-object digest without importing payment machinery into this contract.

## 12. Failure and extensibility

Unknown required action/policy/proof semantics block the dependent transition. Conflicting content, option lineage or status evidence is retained and resolved explicitly. Remote unavailability never implies consent, refusal-window completion or failure of an already-issued promise. Any policy-based disposition must be attributable and must not fabricate an actor's adoption.

An adapter MUST reject a translation that would change a qualified offer into an unissued proposal, attribute a counterpart request as its promise, lose a principal refusal right, or transform accepted terms into native authority. Breaking semantic changes require a distinct version and renewed understanding/adoption.

The schema and illustrative records are authoring aids. Structural validity alone does not prove capability, authority, current consent, cryptographic authenticity, principal notification or an effective agreement. The testing regime is deferred by the user.
