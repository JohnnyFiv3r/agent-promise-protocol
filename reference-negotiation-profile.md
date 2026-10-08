# Reference negotiation note: policy-controlled admission

**Draft 0.2.** This note illustrates the admission contract. It does not mandate a permit format, a numerical quota, a fixed negotiation duration or forced closure.

Each recipient's publication references an understood admission policy. That policy declares eligible participants/topics, admitted message kinds, finite message/byte/work budgets, concurrency/capacity limits, accounting authority and validity. It can admit a bounded first offer, require an invitation, or close contact entirely. Receiving a published intent does not independently authorize a response.

A service may use signed grants, subscription entitlements, native gateway admission or another declared mechanism. All carriers serving the same recipient must preserve the same logical accounting; changing transport, option IDs or publication paths cannot manufacture a new allowance.

## Admission behavior

Before invoking the recipient's model, verify sender, policy, current status, topic, message kind, payload size, operation identity and remaining allowance. Reserve admission atomically with durable deduplication. Replaying the same identity/content yields the same outcome; conflicting reuse is rejected. Traffic rejected for duplicate/conflicting content is still subject to native ingress-abuse controls.

A first offer consumes offer admission capacity. A clarification or new alternative cannot be disguised as a control/status message. Each offer option owns its revision chain. A new option consumes the applicable policy budget and capacity even when its text resembles another option.

## Validity and exhaustion

Policy must expose validity explicitly: a deadline, until withdrawn, or another understood rule. An absent rule is not permission. An open-ended conversation may remain idle or quota-exhausted indefinitely; the protocol does not turn it into acceptance, rejection, withdrawal or a new consent grant.

Budgets and validity are distinct. Exhaustion stops additional admitted work under the exhausted allowance. A policy may authorize a finite top-up or replenishment rule, provided it is explicit, attributable and cannot be triggered by an untrusted sender merely sending more traffic. Status retrieval and principal refusal use their declared bounded channels so proposal exhaustion cannot erase an existing right of refusal.

Explicit closure is possible when policy or an actor requests it. It does not silently cancel independently issued qualified actions or an accepted object. Those require the corresponding authorized withdrawal/refusal event.

No fixed four-offer/eight-message/thirty-minute default survives from draft 0.1. Numeric values in illustrative records are example policy choices only; the testing regime remains deferred.
