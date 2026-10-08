# Reference negotiation profile: reception permits

**Profile URI:** `https://example.org/extensions/agent-bazaar/profiles/reception-permits/v0.1` (documentation URI).

This profile implements the core [consent and bounded-negotiation requirements](contract.md#5-invitation-and-negotiation-admission). It is selected explicitly by the publication contract's `consent.contact.admission_profile`. Existing discovery, subscription, and admission services may supply another versioned profile that preserves the core guarantees. They do not have to implement this permit format, opener coordinator, or these numerical defaults.

The policy document supplies deployment-specific identity, topic, aggregate-capacity, retention, and overload rules. The `reception_permit` schema belongs to this reference profile. Formation and research assessment are separate profiles; admission does not grant commitment, execution, or payment authority.

## Admission mechanism

A recipient publishes one of three policies: `closed`, `invitation_only`, or `bounded_contact`. The absence of a policy means closed. A policy specifies eligible topics and identities/classes, payload limit, request frequency, retention horizon, and capacity behavior. The first research profile uses allowlisted identities, one initial contact per peer and intent revision, a 2 KiB contact limit, and no attachments.

Recipients MUST also configure finite total ingress-message/byte budgets per time window and finite active-channel limits across all identities and intent revisions. Unbounded or missing aggregate limits are invalid. Reject or queue under a stated finite queue policy before model inference; new intent IDs, sender IDs, carriers, or episodes do not reset those local totals.

An initial contact is only a request to discuss an identified intent. It MUST NOT carry a hidden full offer, executable instructions, or an automatic follow-up sequence. The recipient may decline or remain silent. A retry must use the same operation identity. Automated rejection/acknowledgment loops are forbidden; implementations use bounded machine receipts or silence under overload.

A consenting recipient issues a **directional reception permit**: issuer/recipient, authorized sender, channel ID, topic, exact intent digest, allowed message kinds, sequence range, aggregate byte budget, message-size limit, minimum interval, absolute expiry, and policy epoch. Only the recipient can enlarge permission to its own inbox. Reciprocal communication requires the other party's permit too.

The negotiation episode key is the digest of the profile, sorted peer identities, sorted triggering intent digests, and topic. The lexically first agent is the local reference profile's opener coordinator and may register only one episode number as active for that key. Simultaneous open requests using that identical trigger set resolve to that active episode. Requests referring to different demand/supply intents may create different keys; aggregate per-peer limits still apply and no semantic deduplication is claimed. If the coordinator cannot be reached, opening stays pending. A new episode needs fresh reciprocal consent and does not reset per-peer or principal-wide quotas.

Bootstrap messages (initial contact, channel-open request/response, and reception-permit exchange) use a separate recipient-local admission budget under the published contact policy: one open request and at most two setup responses per peer/episode, each at most 2 KiB. The contact includes an authenticated capability for those bounded setup replies to its author. They carry no offer or attached work and expire after sixty seconds. No response starts a retry loop. A missing policy or exhausted bootstrap allowance stops setup. Reopening consumes the same aggregate per-peer budget. An already invited peer may return its reciprocal permit in a setup response without first receiving a negotiation permit.

Every substantive inbound negotiation message MUST pass deterministic admission **before model inference**:

1. Check authenticated sender, audience, topic, profile, permit, expiry, policy epoch and size.
2. Atomically reserve one unused permit sequence and the canonical record's UTF-8 byte count against all applicable recipient-local limits.
3. Record `(permit_id, sequence, digest)` and admission outcome durably before acknowledgment.
4. Same sequence and digest returns the earlier receipt without consuming another allowance. Same sequence and different digest is rejected.

All carriers serving one recipient MUST share that admission authority. Separate per-carrier counters are nonconforming. If shared admission is unavailable, messages remain unadmitted. Transport, cryptographic, and denial-of-service costs still exist; this profile bounds admitted negotiation and model work, not arbitrary hostile network traffic or Sybil identities.

## Reference negotiation budget

For each direction: at most eight substantive messages, at most four offer versions, at most 16 KiB per message, at most 64 KiB total, at least five seconds between newly admitted substantive messages, and a thirty-minute absolute episode lifetime. These are configurable demo defaults, not theory-derived constants. Clarification questions and answers consume the same substantive-message budget.

Receipts are fixed-size and do not trigger further receipts. Each direction has separate control allowances: at most eight formation/status messages, each at most 4 KiB and at most 32 KiB total, plus one close signal and one close acknowledgment of at most 1 KiB each. Control messages contain only typed formation/status references, never another proposal. They use the same identity, replay and atomic admission rules. Exhausting proposal quota cannot prevent bounded closure or resolution of an already-pending award.

Replacing a permit requires explicit recipient action within principal-wide quotas and MUST NOT raise the episode's original caps or absolute expiry. Additional negotiation requires a new consensual episode; agents MUST NOT auto-reopen or auto-renew solely because another offer arrived. Retrieving existing durable outcomes is a separately rate-limited read operation, not a way to submit fresh formation messages.

Each counterparty gets a separate channel. Negotiating with one provider does not reserve all demand or prevent competing proposals. Aggregate quotas are still local policy; the protocol makes no global fairness guarantee.
