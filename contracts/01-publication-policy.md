# C1 — Publication, consent, and principal policy

**Normative contract · ABP 0.4-draft**

This contract governs permission to publish, discover, contact, and negotiate. `MUST`, `MUST NOT`, and `MAY` prescribe participant behavior. It implements the controlling [decisions](../decisions-v0.2.md); the [publication guide](../publication-contract.md) explains the surface and the [record schema](../schemas/contract.schema.json) defines its structure.

## Actors and required inputs

### C1-01

Only the controlling principal or an agent currently delegated the relevant act MAY authorize, revise, or withdraw that principal's publication policy. An issuer MUST authenticate its agent identity, principal identity, and the delegation covering the specific subject and act. A service's ability to store or route a record grants none of those acts.

### C1-02

A publication decision MUST identify the exact publication record; `principal_policy_ref`; `discovery.distribution_policy_ref`; `contact.admission_policy_ref`; `transaction_policy_ref`; and `validity.policy_ref` with its authenticated `status_ref`. Each content reference MUST resolve to the referenced bytes and understood semantics. A locator, descriptive title, or unattested permission claim is insufficient.

### C1-03

`discovery.distribution_policy_ref` MUST specify the publication subject, permitted fields or representations, permitted audience, allowed uses, and onward-disclosure restrictions. `principal_policy_ref` MUST specify delegated acts and limits, human approval requirements, negotiation privacy, and principal refusal requirements. These references MUST contain evaluable declarations under named semantics; unconstrained prose MUST NOT supply an automatic permission decision.

### C1-04

`validity.policy_ref` MUST identify the authenticated status authority, authoritative ordering and clock, permitted skew, finite maximum evidence age, and conflict/unavailability behavior. `status_ref` MUST resolve through that authority's declared mechanism. A reference's own digest establishes its policy content, not the current status of the permission it describes.

## Publication and reception guards

### C1-05

Before publication or onward delivery, the acting agent or service MUST establish that the exact subject, representation, audience, use, and current authority are permitted together. It MUST apply the intersection of all applicable restrictions. Independent permission for two fields, audiences, or uses MUST NOT be combined into an unapproved disclosure.

### C1-06

A discovery service MAY narrow distribution, reject publication, rank matches, or apply additional business rules. It MUST preserve original authorship, record content, and policy provenance. A redacted summary MUST remain an attributed derivative with its own permitted scope; it MUST NOT be represented as the complete signed original or as another agent's promise.

### C1-07

Each delivery through a subscription MUST be covered by that subscription's subject, audience, and use permissions. Subscription membership, public visibility, a match, or receipt of an intent MUST NOT be interpreted as permission to receive offers, disclose private terms, issue promises, or accept an agreement.

### C1-08

For `contact.admission_kind = closed`, no new contact is admitted under that policy. For `invitation`, the sender MUST possess the required current invitation. For `first_offer`, the sender MAY issue a bounded first offer without an extra invitation round only when the admission policy admits that sender, subject, purpose, content, and resource use. Missing required permission is closed.

### C1-09

The recipient or its delegated admission authority MUST decide admission before negotiation model processing. The decision MUST bind the authenticated sender, recipient, exact message, applicable policy revision, and allowance consumed. Receipt, successful transport, admission, and commercial adoption MUST remain separate observations.

### C1-10

The admission policy MUST name allowed purposes, applicable message/work budgets, aggregation scope, and the authority enforcing those limits across applicable channels and services. An implementation MAY choose its mechanism; it MUST preserve those declared limits under concurrent admissions and duplicate delivery. No particular permit format, counters, default values, or discovery service is required.

### C1-11

Budget exhaustion MUST restrict the messages or work governed by that budget. It MUST NOT imply refusal, agreement, abandonment, breach, or closure of an otherwise valid negotiation. Status and principal-refusal access MUST remain available under their separately bounded policies; unused control capacity MUST NOT carry hidden proposals.

### C1-12

Replenishment, renewal, or extension MUST follow an explicit current recipient/principal rule and retain an attributable decision. A new message ID, option name, sender alias, service, or repeated payload MUST NOT reset an applicable aggregate budget. Silence or continuing activity MUST NOT supply consent to replenish it.

## Validity, changes, and evidence

### C1-13

Permission MUST use an understood validity rule: `expires_at`, `until_withdrawn`, or `policy_defined`. A conforming participant MUST NOT impose a universal expiry or infer an outcome from inactivity. Policy-defined deadlines and fresh-status requirements remain enforceable independently of negotiation lifetime and available budget.

### C1-14

Before dependent publication, contact, promise issuance, terms adoption, or finalization, the responsible participant MUST verify the current applicable policy and authority evidence within their freshness rules. It MUST retain references to the exact evidence used and the decision's authoritative ordering. A previous successful check MUST NOT substitute for a required current check.

### C1-15

Missing, too-old, conflicting, unauthenticated, or unavailable required evidence MUST leave the dependent act unauthorized or unresolved; it MUST NOT be treated as permission. Known newer withdrawal or restriction MUST NOT be displaced by older active evidence. Evidence freshness establishes the declared bounded observation, never an instantaneous global snapshot.

### C1-16

A revision MUST preserve `contract_id`, identify the exact prior digest, advance that chain's revision, and authenticate authority over the same subject. Repeated identical bytes are one observation. Conflicting bytes for the same identity/revision MUST be quarantined until the declared status authority resolves their relationship; arrival order alone MUST NOT select permission.

### C1-17

Supersession and withdrawal MUST be attributable events identifying the affected exact record and their authority basis. They stop new acts dependent on the withdrawn permission according to its status ordering. They MUST NOT erase prior issuance or acceptance, manufacture rollback, or substitute for a principal refusal addressed to an accepted-offer object.

### C1-18

A newly permissive policy MUST NOT silently widen an existing promise, offer, candidate, or accepted object. Where a pending act depends on changed policy or scope, the participant MUST obtain the required new record and adoption. Previously admitted negotiations MAY retain their explicitly authorized status/refusal access without acquiring permission for further proposals.

## Privacy and commercial constraints

### C1-19

Negotiation records, offers, candidate terms, capability evidence, and accepted terms MUST be private by default. Additional recipients, including brokers or auditors, require permission covering the relevant parties' information. Publishing an intent MUST NOT grant disclosure rights over later negotiation or its participants' evidence.

### C1-20

An acting party MUST check permission separately for disclosing a record, disclosing its referenced evidence, and granting access to a locator. A promisee is not automatically authorized to redistribute a promise; a permitted observer is not automatically a promisee. Proof metadata or content references MUST NOT be used to bypass applicable confidentiality restrictions.

### C1-21

Withdrawal of disclosure permission MUST stop future disclosures covered by that withdrawal. Historical content MUST NOT be silently rewritten to conceal prior acts. Record retention and access MUST follow the agreed privacy and evidence policies; historical retention alone MUST NOT grant onward disclosure. If required evidence cannot lawfully be shared or verified, the dependent automatic decision MUST remain blocked.

### C1-22

Agents MAY negotiate a previously unlisted complete commercial arrangement when both principals' current policies permit it. They MUST check the arrangement as a whole under its named semantics and record the applicable policy revisions and decision evidence. A catalog of identical prepublished routes is not required; independently permitted components do not establish a permitted combination.

### C1-23

Commercial protocol, provider, processor, or settlement preferences MAY appear as agreement data. Their presence MUST NOT be interpreted as native compatibility, transaction authority, or a completed downstream act. [C8](08-adapter-boundary.md) governs handoff and interpretation of returned evidence; native payment and fulfillment procedures remain beyond that boundary.

### C1-24

Unknown required policy predicates, extension semantics, subject interpretations, or delegation conditions MUST prevent the dependent automated act. Optional explanation MAY inform a human decision but MUST NOT silently extend typed permissions. An adapter MUST NOT drop a restriction to obtain a compatible decision.

### C1-25

Candidate terms MUST preserve each distinct principal's policy-required positive refusal period, notice destination and delivery rule, refusal authority/path, and status/clock rules. Agents MUST NOT waive or shorten these rights through issuance, adoption, or finalization. The [accepted-offer contract](../accepted-offer.md) determines their effect after the agent handshake.

### C1-26

Permission to emit a declaration covers only the qualified emission it actually identifies. Neither discovery, matching, service compliance, nor reception consent issues another actor's promise. Principal policy provides continuing permission; it MUST NOT be promoted into a standing promise to negotiate, accept future work, or perform unspecified actions.
