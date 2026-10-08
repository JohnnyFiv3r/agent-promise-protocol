# Publication and discovery contract

This is the shared business-rule surface used by existing discovery, subscription, marketplace and agent services. The schema standardizes consent and commercial eligibility at a high level. Services own matching, sales qualification, subscription delivery, routing and admission implementations.

## Publication fields

| Field | Contract meaning |
|---|---|
| Issuer agent/principal | Authenticated author expressing its own consent; no service can broaden it |
| `contract_id`, `revision`, `previous_digest` | Immutable policy revision chain; intent and offers name exact record IDs/digests |
| `valid_from`, `expires_at`, `status_ref` | Validity plus authenticated current withdrawal/revision status; the status API belongs to the service |
| `consent.discovery.audiences` | Audience within which the permitted uses apply |
| `consent.discovery.permitted_uses` | Permitted indexing, matching, subscription delivery or redistribution; omitted uses are not authorized |
| `redistribution_policy_ref` | Immutable details for onward use; cannot expand the declared audience/uses |
| `consent.contact.mode` | Closed or governed by the selected policy; public visibility alone permits no contact |
| `eligible_topics` | Topics eligible for the contact policy |
| `admission_profile`, `admission_policy_ref` | Understood mechanism and immutable service rules for recipient consent and bounded interaction |
| `iterative_offers` | Whether iterative proposals can be admitted within that policy; not an unlimited reply license |
| `eligible_commercial_routes` | Complete combinations the issuer supports; an empty list permits discovery but no agreement formation |

A subscription is consent for its declared delivery scope. Receiving an intent does not imply consent to receive a sales offer, execute work or pay. The recipient's contact policy answers those contact questions separately. Either party can publish demand, supply or collaborative intent under these rules.

A service may implement richer business rules or its own admission profile, provided it preserves the [core guarantees](contract.md#5-invitation-and-negotiation-admission). The [reference permit profile](reference-negotiation-profile.md) is one option.

## Complete commercial routes

An external route contains:

| Field | Meaning |
|---|---|
| `route_id`, `mode` | Shared route identity; mode is `external`, `none` or `simulated` |
| `order_validation` | Exact AP2 version/profile for order validation and commitment |
| `paid_exchange` | Exact x402, Machine Payments Protocol or other selected exchange version/profile |
| `processor_ref` | Immutable native processor/provider configuration; no credentials |
| `settlement.scheme_profile`, `asset`, `network` | Native scheme and settlement denomination/network; use an explicit native value when no blockchain network applies |
| `native_route_policy_ref` | Immutable native compatibility and commercial restrictions; native protocols retain their own configuration semantics |

Each route is one complete combination. Supporting two processors and two networks does not imply support for all four pairings. Services must match complete objects, including their native compatibility policies. Route digests cover the entire canonical route object, including `route_id`.

Both counterparties' current applicable publication contracts must contain the selected route. An offer and candidate terms identify both publication records and select `{route_id, route_digest}`. Native commercial terms supply the exact payee, amount basis, currency/asset, caps and trigger; these must fit the route. The agreement freezes that selection. The processor and settlement choice is therefore constrained at discovery and fixed by acceptance.

Native incompatibility means the route is ineligible even if JSON validates. The paid profile needs an implemented, verified AP2-to-exchange binding; a diagram or synthetic route does not establish one. Additional exchanges can be supported by publishing a compatible versioned route, without changing consent or promise primitives.

## Changes and withdrawal

New revisions cannot mutate existing offers or accepted terms. Formation checks current policy status and route eligibility; a stale required revision or unknown status blocks formation. A service may narrow its own routing choices but cannot silently select a different route for the parties.

Withdrawal stops new publication delivery/contact and formation under that permission. Already admitted negotiations retain a bounded reconciliation/closure path. Accepted agreements keep their terms. Agreement cancellation, execution revocation and downstream mandate revocation use their own native mechanisms.

### Current-status observation

The selected admission or formation profile MUST define the authenticated status authority, evidence format, policy epoch or ordering token, finite maximum evidence age, authoritative clock and allowed clock skew for each required publication/policy status check. The verifier retains the exact evidence, subject revision, observation time and local decision order. Future-dated, expired, too-old, conflicting or unavailable required status evidence blocks the dependent transition. Later observations cannot replace a known newer withdrawal with an older active status.

At reference-profile finalization, the coordinator checks that the retained status evidence for both publication pins is valid under those declared freshness rules. Known withdrawals and the finalization decision serialize in its durable local order: withdrawal known before finalization blocks it; a later observation is retained without silently rewriting a finalized agreement. Native execution and payment authority still require their own subsequent checks.

Independent status services do not provide an instantaneous global snapshot merely because each response is authenticated. This profile's guarantee is eligibility under its specified observation and freshness rule. A deployment requiring withdrawal to take effect atomically across services MUST select a native conditional authorization, reservation or shared ordering mechanism that supplies that guarantee and bind its evidence; it cannot claim the stronger guarantee from timestamps alone.

## Synthetic examples

The [buyer publication](examples/buyer-publication.json) and [provider publication](examples/provider-publication.json) advertise the same simulated route and reference the same demonstration admission policy. Their [intents](examples/buyer-intent.json) reference their respective publication records. The [candidate agreement](examples/research-terms.json) pins both publication digests and that exact route. Status URLs are documentation placeholders; these records demonstrate structure, not live consent.
