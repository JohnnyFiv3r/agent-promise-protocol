# Foundational prior-art audit

**Baseline note:** this comparison was authored against draft 0.1. Statements about Bazaar’s former proposal-only offers, fixed validity or payment scope are historical. The [draft 0.2 decisions](../decisions-v0.2.md) govern the current contract; external findings remain source-review observations.

Checked October 8, 2026 against the current local Agent Bazaar product spec and contract. This is a bounded recursive review of Contract Net/FIPA, Beckn/ONDC, Agent Bounties and crypto intent/solver protocols. It follows their directly relevant specifications, types and implementation references; it does not establish internet-wide novelty, deployment status or independent adoption. Branch URLs below are mutable observations, not release pins.

## Finding

**Keep the product thesis and narrow the novelty claim to the semantic boundary.** Intent-driven discovery, iterative negotiation, voluntary participation, explicit commitment and outcome-contingent payment all have substantial prior art. The strongest proposed contribution is a portable A2A contract that preserves the difference between an interest declaration, permission to engage, a proposed promise, an agent's adoption of its own promise, and authority to execute or pay, even when independent discovery services and payment adapters compose the interaction.

This is a product and interoperability distinction. Promise Theory supplies the meaning; naming existing negotiation fields after Promise Theory would not itself establish a new system. A useful demonstration must exercise transitions that a plain solicitation–bid–award marketplace cannot represent without additional rules.

## Contract Net and FIPA

The original FIPA 1997 publication already distinguishes `inform`, `cfp`, `request`, `propose`, `agree`, `refuse`, `accept-proposal` and `reject-proposal`. Its iterated Contract Net permits revised CFPs and repeated bidding. A proposal describes the sender's conditional action; the Contract Net profile treats that proposal as binding when the manager accepts it. This is conditional self-commitment, not the manager inventing another party's promise. See printed pages 23–26, 34, 37–39 and 46–47 of the [original FIPA publication preserved by the USPTO](https://ptacts.uspto.gov/ptacts/public-informations/petitions/1524581/download-documents?artifactId=mAFcp83DjfjSWipt5FGgyfLcg-iSu5gdYeGK2kap9GUGdJFhtFcO6SI).

**Implication:** neither separated speech acts nor iterative proposals is new. Bazaar's chosen distinction is that its draft offers remain nonbinding promise descriptions until explicit self-adoption/finalization; its consent and bounded-iteration guarantees also apply before and across bilateral negotiation. A FIPA mapping must preserve proposal firmness. It must not map a Bazaar draft straight to a binding `propose` and thereby advance commitment without the author.

The official 2002 [Contract Net](http://www.fipa.org/specs/fipa00029/SC00029H.pdf), [Iterated Contract Net](http://www.fipa.org/specs/fipa00030/SC00030H.pdf), and [Communicative Act Library](http://www.fipa.org/specs/fipa00037/SC00037J.pdf) endpoints were inaccessible in this check. The primary document inspected is FIPA's own 1997 text, not a claim to have verified the full 2002 revisions.

## Beckn and ONDC: substantial conceptual overlap

Beckn v2 is the strongest comparator in this group. Its current OpenAPI describes cross-domain value exchange, intent-based discovery, price/terms negotiation and contracts. `Offer` contains commercial conditions, value and validity; `Commitment` binds resources and offer terms with a lifecycle status; `Contract` gathers commitments, consideration, participants, performance and settlement. `/select`, `/init` and `/confirm` separate quote, final terms and confirmation. The file also specifies policy-based refusal and capacity/rate responses. Its fabric requires namespace and registry services. This is already a broad commerce contract model, not just a retail catalog. [Canonical OpenAPI, including `Offer`, `Commitment`, `Contract`, `NackDiscretionary`, and `NackTooManyRequests`](https://github.com/beckn/protocol-specifications-v2/blob/main/api/v2.0.0/beckn.yaml).

Its communication draft goes further: a message declares the sender's state without directing the receiver to adopt it; transport acknowledgements are separate from business responses; nodes can reject engagement; downstream layers do not inherit confirmation automatically. Those concepts directly overlap the autonomy motivation. The document identifies itself as a draft, with implementation and stress-test reports unavailable. [NFH-013 communication model, sections 3–4 and 11](https://github.com/beckn/protocol-specifications-v2/blob/main/docs/Communication_Protocol.md).

Recursive checks found an [independent-workflows document](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Independent_Workflows.md), but its substantive normative sections remain placeholders in the inspected version. The referenced NFH-008 error document could not be retrieved; refusal/capacity claims above are grounded in the accessible API and communication draft. Do not treat an inaccessible dependency as proof that a feature is absent.

ONDC's own [base-layer repository](https://github.com/ONDC-Official/protocol-base) names Beckn as its base, and its [network extension repository](https://github.com/ONDC-Official/protocol-network-extension) describes the additional network layer. The inspected [ONDC core YAML](https://github.com/ONDC-Official/ONDC-Protocol-Specs/blob/master/protocol-specifications/core/v0/api/core.yaml) is labeled 1.0.1/adapted from Beckn 0.9.3 and includes intent search. This establishes lineage; it does not establish that current ONDC networks implement the Beckn v2 features above.

**Residual for Bazaar:** a thin A2A extension usable across existing discovery/admission systems, symmetric interest declarations distinct from service catalogs, explicit per-agent provide/receive polarity and adoption, and consent/iteration limits that survive relays and carrier changes. Those are more precise differences than “autonomous commerce,” “negotiated commitments,” or “consent.” The inspected Beckn commitment type does not establish those complete Bazaar semantics. It also has extension points, so the comparison is against documented native behavior, not a claim that Beckn could never support them.

**Design pressure:** do not build a second full commerce ontology, catalog network, registry, quote system or fulfillment engine. A Beckn adapter should be a useful test: it can reuse Beckn's catalog and contract records, while explicitly recording where an interest declaration, promise adoption or admission budget has no lossless native mapping.

## Agent Bounties: exact terms and verifiable completion already exist

The current autonomous protocol publishes committed terms before bounty creation, including reward, bond, windows, verification policy and evidence commitments. It distinguishes transaction preparation and signatures from canonical settlement evidence, and includes optional bounded delegation. [Autonomous protocol](https://github.com/NSPG13/agent-bounties/blob/main/docs/autonomous-protocol.md).

The implementation is concrete: `AgentBounty.sol` binds a solver claim to the bounty, solver, round, `termsHash`, `policyHash` and deadline; configuration stores acceptance-criteria, benchmark and evidence-schema hashes; `claim` activates a claim and collects the bond. [Contract source](https://github.com/NSPG13/agent-bounties/blob/main/contracts/base-escrow/src/AgentBounty.sol).

Its A2A 1.0 interface is expressly a read-only discovery/orientation surface. It does not claim work, authorize funds, verify submissions or prove payment through A2A. [A2A interface contract](https://github.com/NSPG13/agent-bounties/blob/main/docs/a2a.md).

**Overlap:** autonomous agents discovering paid digital work, exact accepted terms, bounded authority, artifact evidence and verified outcome/payment. A research-report bounty with a rubric is not a differentiated demo by itself.

**Residual:** Bazaar standardizes an earlier, symmetric conversation and commitment boundary; the inspected bounty protocol standardizes participation in already funded, committed work under its own settlement system. Treat Agent Bounties as a potential discovery/fulfillment venue. Do not reimplement its escrow, claim bond, verification network or payout machinery. A provider's advertised interest in research work must remain representable without constructing a funded bounty or signing a claim.

## Crypto intent and solver systems

### ERC-7683: distinguish interest from executable payment orders

The currently published ERC-7683 standard differs substantially from its older draft. It defines a solver-facing resolver: opaque protocol payloads resolve into steps, variables, payments and named assumptions. It expressly defines an order as a payment offer for satisfying requirements, leaving order creation, authorization and settlement flexibility to underlying protocols. The document explains why it replaced the earlier `OnchainCrossChainOrder`/`GaslessCrossChainOrder`, `open`/`openFor` and `fill` lifecycle model. [Current ERC-7683, especially “Orders,” “Resolvers,” and “Previous Draft”](https://ercs.ethereum.org/ERCS/erc-7683).

**Implication:** portable solver execution is established prior art. A Bazaar interest declaration is deliberately earlier than an ERC-7683 order. An adapter must never produce such an order merely from publication or discovery. If a selected commercial route uses an intent protocol, the authorization-bearing order belongs after accepted terms and the required order-commitment gate. The useful difference is who is permitted to advance each transition, not the word “intent.”

### CoW: competitive execution and immutable signed limits

CoW accepts off-chain signed orders and lets solvers compete to settle them. Its documented guarantees protect user funds behind order authorization and constrain execution to the order's limit. [Core architecture](https://docs.cow.fi/cow-protocol/reference/contracts/core). The `GPv2Order.Data` type binds tokens, receiver, amounts, expiry, app-data hash, fee and partial-fill settings into the signed order. [Order-library source](https://github.com/cowprotocol/contracts/blob/main/src/contracts/libraries/GPv2Order.sol).

**Implication:** competitive selection, exact signed constraints and fill evidence are not Bazaar innovations. CoW's domain and execution object differ from open-ended service negotiation, but that difference must be demonstrated rather than asserted from “AI agent” labeling.

### Anoma: preference and counterparty-discovery overlap

Anoma's intent-machine specification describes preference over future states, counterparty discovery, and solvers aggregating intents into executable transactions. Concretely, an intent is a potentially unbalanced transaction describing resources offered for consumption and desired resources; solvers return balanced transactions. The inspected page labels specification v0.1.1 and carries 2024 update metadata. [Intent-machine definition and data format](https://specs.anoma.net/main/system_architecture/state/intent_machine/index.html).

**Implication:** expressing desired outcomes without prescribing the execution path, discovering counterparties and compositional solving are prior art. Bazaar's narrower target is pre-commitment interaction consent and self-owned behavioral promises across off-chain products/services and existing agent protocols. Do not pitch broad “intent-centric economy” as a new mechanism.

## Requirements that keep the proposal distinct

These are design recommendations based on this comparison, not claims about deployed Bazaar behavior:

1. **Show both directions.** A provider's “I seek research work” and a buyer's “I seek a report” must each be publishable without a quote, payment offer, mandated action or counterparty promise.
2. **Make authorship executable.** Reject an offer that purports to issue another agent's promise. A requested reciprocal remains a request until its named promiser adopts it.
3. **Test commitment semantics in adapters.** A conversion to a FIPA conditional bid, funded bounty claim, Beckn confirmation or crypto payment order must declare that semantic transition and require its authority; lexical field matching is insufficient.
4. **Prove consent portability.** Deliver the same intent through two independent discovery services, then revise an offer through A2A. Duplicate delivery or a new transport ID must not renew the recipient's permission, budget or channel lifetime.
5. **Show useful negotiation that terminates without trade.** A recipient can permit one clarification, decline further contact and owe no purchase, service or payment. Ordinary rate limiting is insufficient evidence for this property.
6. **Keep payment mechanics delegated.** Bind the selected route and exact accepted terms to native AP2/payment records; demonstrate that discovery, a payment challenge and transport acknowledgement cannot initiate payment.
7. **Avoid demo false positives.** “Three research agents bid and one gets paid” proves a contract-net marketplace. Add self-authorship rejection, symmetric emission, cross-service replay/consent behavior and refusal to perform a lossy commitment mapping to prove this thesis.

The non-duplication test is therefore behavioral: can an independent participant preserve these distinctions and reject the invalid transitions without sharing Bazaar's reference runtime? If the answer requires replacing discovery, identity, authorization or settlement, the design has expanded beyond its strongest angle.
