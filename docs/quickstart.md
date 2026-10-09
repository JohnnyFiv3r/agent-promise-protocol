# One capability, one agreement

**ABP 0.4 / RP1 · integration design, not installation instructions for an existing SDK.**

The normal interaction is: express an outcome, receive qualified offers, select exact terms, adopt the same candidate, and honor each principal's protected refusal period. A conforming reference harness handles the protocol mechanics. This guide defines the intended adoption path to implement after contract/profile lock.

## Who integrates and who authorizes

The buyer enables a connector to a delegated participant or uses an assistant with that participant embedded. The seller or its software provider exposes an A2A ABP endpoint backed by its business logic. Humans authorize policies and keep a usable notice/refusal interface; their providers handle durable protocol state. One connector can reach multiple compatible sellers, and direct peers need no discovery service. The [deployment model](../deployment-model.md) separates these product entry points from scoped protocol authorities; the [runtime guide](runtime.md) describes the implementation available today.

## What the application supplies

| Input | The application's responsibility |
|---|---|
| Capability | The understood action vocabulary, inputs/outputs, what it can actually do and evidence appropriate to that claim |
| Principal policy | Who may act for whom, permitted actions/limits, any required human approval, and a positive recovery duration |
| Real constraints | Available capacity, exclusivity, privacy restrictions, service conditions and current facts; the harness cannot invent these |
| Principal channel | A designated channel and authenticated refusal route that the principal can actually use |
| Performance connection, when needed | An adapter implementing the agreed preparation, native authorization, dispatch and reconciliation boundary for the application |

The default harness profile supplies proof formatting, key lookup, policy decision plumbing, content retrieval, message admission, operation identity, durable ordering, candidate references, notices and refusal/status processing. The deployer configures the profile's trust and authority assignments once. Application builders do not choose a cryptographic suite, policy language or ledger topology for each offer.

## The ordinary flow

1. **Register the capability and principal configuration.** Use the default profile. The harness checks that authority and the principal refusal channel are usable. Unsupported required action semantics or missing truthful capacity evidence prevent autonomous commitments.
2. **Publish an intent under the principal's audience/contact rules.** It communicates what the agent seeks. It does not offer payment, promise fulfillment or permit unrestricted unsolicited contact.
3. **Issue qualified offers.** Each offer names only its author's own promises and any requested counterpart actions. Several options may coexist within policy-selected budgets and validity. The harness admits traffic and maintains option histories.
4. **Select one exact candidate.** The originator/coordinator selects and distributes its full reference. Both agents inspect and adopt that reference. A recipient can accept directly without inventing a reciprocal service promise.
5. **Observe agreement and recovery separately.** Agent formation creates an accepted object. The harness delivers qualifying notice and exposes recovery as `pending`, `cleared`, `refused` or `unresolved`. The applicable positive durations are adopted policy values, not an optional mode.
6. **Handoff only when requested and eligible.** If the application enables an adapter, the harness evaluates relevant clearance and the adapter independently establishes native action authority before dispatch. An application that only negotiates can stop at the accepted object and its current recovery status.

No transaction plan or composition binding is needed for this path. The normal A2A invocation surface stays `submit_record`, `finalize_candidate`, `query_status`; domain-facing helper names in the [harness interface](../profiles/harness-interface.md) are a proposed SDK facade, not additional transport methods.

## When something does not proceed

- **Offer quota exhausted:** additional negotiation work waits for explicitly permitted replenishment; no agreement or expiry is invented.
- **Unknown meaning or authority:** the dependent act is blocked and explains the missing requirement within disclosure policy.
- **Principal refuses:** the accepted object remains refused. New agreement needs new exact terms/adoptions and a new protected period.
- **Lost response:** the harness recovers the same operation; the application does not resend it as a fresh purchase or action.
- **Uncertain native effect:** reconciliation preserves the original key and possible effect. An unknown result does not authorize another dispatch.

The application must not reduce these facts to a single `success` flag. A formed agreement may still be pending recovery; cleared recovery may still lack native authority; a dispatched request may still have an unknown outcome.

## Add capabilities only when needed

| Feature | When to enable | What stays unchanged |
|---|---|---|
| `composition` | Several bilateral contributions or subcontract agreements have declared dependencies | Each agreement has its own exact candidate, authorship, adoptions and recovery rights |
| `adapter-handoff` | Connect an agreed action to separately authorized native performance | Agent agreement and principal clearance are still not execution authority |
| `lifecycle-evidence` | Exchange typed fulfillment, assessment or native settlement observations | Reports retain their own issuer, native evidence and interpretation limits |

Advanced features are advertised and understood before a dependent act. A peer that lacks a required feature rejects it; no silent approximation. The default bilateral path does not require atomic bundles, auctions or cross-market coordination.

## How simplicity will be assessed

After contract lock and harness implementation, give an independent builder this guide, RP1 and the SDK. They should connect one existing capability and principal policy, form an agreement and honor refusal without writing protocol machinery or obtaining unwritten rules from the authors. Separately, another implementation should interoperate from the specification without using the SDK. These are [proposed adoption tests](../tests/PROPOSED.md), not results already obtained.
