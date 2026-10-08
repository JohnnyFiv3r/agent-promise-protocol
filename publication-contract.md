# Publication and policy contract

**Draft 0.2.** Existing discovery/subscription services and service sources use the same publication contract to connect to their agent harnesses. Each principal controls its own policy. The service retains matching, ranking, subscriptions and implementation of business rules.

## Publication surface

| Element | Required meaning |
|---|---|
| Issuer and principal | Authenticated author of the consent and its authority basis |
| Record identity and revision | Immutable content, prior revision reference and current-status location |
| Subject and audience | What may be published and who may receive it |
| Permitted uses | Explicit discovery, matching, subscription delivery and onward-use permissions |
| Contact mode | Closed, invitation required, or policy-permitted bounded first offer |
| Admission policy | Eligible senders/topics, allowed message purposes, budgets and shared enforcement authority |
| Validity | Explicit deadline, until withdrawn, or another understood referenced rule |
| Principal policy references | Delegation for publication, offers and acceptance; review/refusal requirements; privacy and other commercial constraints |
| Commercial eligibility | Permitted arrangements or versioned rules for evaluating a negotiated arrangement |
| Status/freshness policy | Authenticated source, ordering, clocks, evidence age and handling of unknown status |

Absence of a required rule is not permission. Publication consent, receiving a first offer, issuing a promise, adopting exact terms and downstream transaction authority are distinct. An existing subscription authorizes only its specified deliveries and uses.

## Service duties and private negotiation

A conforming service MUST preserve issuer, content and policy provenance. It may narrow distribution under its own rules; it cannot broaden audience, permitted uses or contact permission. A publication's visibility does not authorize unsolicited offers unless its contact policy explicitly does so.

Negotiation and terms are private by default. Disclosure to a broker, evaluator or auditor requires the relevant parties' permission. An intent's publication grant does not extend automatically to later offers or an accepted object. Policy may permit a minimal discovery summary while keeping exact terms and evidence accessible only to named recipients.

Service compliance is its own undertaking. A policy issued by Agent A does not prove a discovery service has honored it, and a discovery service cannot issue Agent A's promises merely by carrying its records.

## Qualified declarations

An emitted intent includes the agent's qualified act of declaring/seeking and an exact publication reference. Capability and authority for that act are distinct from the ability or authority to supply or purchase the desired outcome. Relays preserve the action's scope; matching it to a supplier does not issue an offer on either agent's behalf.

## Flexible commercial negotiation

Publication exposes the owners' commercial constraints, not a mandatory exhaustive catalog of identical route objects. An offer may propose any complete arrangement that both policies permit, including a previously unlisted compatible arrangement. The agents may negotiate price, scope, provider, payment preference and other commercial conditions within their authority.

The selected arrangement must have enough structure under its declared semantic profile to check it as a whole. Independent allowed components do not imply that every combination is permitted. Exact candidate terms pin the negotiated arrangement, the applicable policy revisions and the evidence that each policy admits it. An unknown required policy predicate blocks automated adoption.

Commercial terms may name AP2/UCP/ACP, an exchange protocol, processor or settlement preference. Those are agreement data and downstream references, not proof of native compatibility or authority. Bazaar does not construct a Checkout, validate a mandate or invoke a payment contract.

## Validity and budgets

The policy explicitly declares whether permission ends at a deadline, remains until withdrawn, or follows another named rule. The core does not force an expiry timestamp or resolve an inactive conversation. Message/work budgets are independent from validity: a still-valid negotiation can be quota-exhausted.

A replenishment or extension must follow an explicit principal/recipient policy and remain attributable. New message IDs, alternate discovery services, duplicated content or changed option names cannot replenish a budget. Admission occurs before model processing. Status and refusal channels must remain available under their own bounded policies even when proposal capacity is exhausted.

## Changes, freshness and refusal

Policy revisions and withdrawal are immutable attributable events. New permissions cannot silently rewrite an existing offer or accepted terms. Before dependent issuance/adoption/finalization, participants check current applicable status and preserve the evidence used.

The selected profile identifies authenticated status authority, policy epoch/order, authoritative clock, permitted skew and finite evidence freshness. The verifier records exact evidence and local decision order. Known newer withdrawal cannot be displaced by older active status. Missing, too-old, conflicting or unavailable required evidence blocks that transition. This is a bounded observation guarantee, not an instantaneous global snapshot across independent services.

Before agent agreement, the candidate MUST include each principal's positive post-handshake refusal period, notification destination and rule, refusal authority, status authority and clock/freshness policy. Neither agent can shorten these rights while finalizing. See [accepted-offer semantics](accepted-offer.md).

Publication withdrawal stops new activity under that permission. It does not erase existing records, prove reversal of downstream effects or substitute for a principal refusal directed at an accepted object. A principal refusal within the agreed window has the separate effect specified in that object's lifecycle.
