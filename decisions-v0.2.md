# User decisions incorporated in draft 0.2

The user's fifteen answers govern this revision. These decisions supersede contradictory language in draft 0.1 and the earlier component-reuse recommendation.

| # | Decision | Contract effect |
|---|---|---|
| 1 | Autonomous action within delegated limits | Principal policy determines when an agent may negotiate/adopt and when human approval is required. |
| 2 | Promise means qualified action; an offer is a promise; no standing promises | Offer issuance adopts the author's conditional action promises. Capability and authority are separate qualifications. Continuing permission lives in policy. |
| 3 | Promises can exist outside an agreement, subject to #2 | Explicit scoped action promises are supported without a transaction; policy is not itself a standing promise. |
| 4 | Small universal structure with extensions; proposal to refine | Common action shape specifies actor, semantics, polarity, parameters, qualifications and evidence references. No universal product ontology is imposed. |
| 5 | Recipient policy may allow a bounded first offer | No mandatory invitation round when current contact policy already admits that offer. Missing permission is closed. |
| 6 | Several competing options may coexist | Each named option has its own revision chain. Selection identifies an exact option/revision; shared capacity or exclusivity must be explicit. |
| 7 | Budgets apply; validity is policy-defined; no forced expiry or resolution | Validity supports explicit deadlines, until-withdrawn and referenced rules. Exhaustion restricts traffic rather than inventing an agreement outcome. |
| 8 | Private negotiation by default | Additional disclosure needs explicit permission; intent publication does not publish offers or terms. |
| 9 | Author of initiating promise/intent is coordinator | Origin reference and coordinator are pinned, independent of buyer/provider role or message arrival time. |
| 10 | Commercial route as flexible as owner policies allow | Parties may negotiate a new complete arrangement satisfying both policies; no requirement for identical prepublished route objects. |
| 11 | Fresh policy-status checks plus principal refusal after agent handshake | Accepted terms include policy-defined positive refusal windows, notification rules and status authority. Agent agreement does not erase human refusal. |
| 12 | Immutable terms with linked replacement | Replacements require fresh adoption and explicit disposition of prior obligations; historical records remain. |
| 13 | Portable proof compatible with downstream AP2 | Native proof suites authenticate exact Bazaar bytes. A downstream adapter maps the accepted terms into native commerce/Checkout; Bazaar issues no AP2 mandate. |
| 14 | Contract ends at accepted-offer object | Remove payment, settlement, delivery and assessment objects/state machines from Bazaar. Simulated payments belong only in a later internal toy consumer. |
| 15 | Testing regime later | No selected human reviewer, correction count, evaluation procedure or live payment qualification is a current requirement. |

## Concrete authoring proposals within those decisions

The following details make the selected behavior precise and remain reviewable:

- Finalization creates the accepted-offer object after both agent adoptions. Its status starts `pending_refusal_windows`; it is not cleared for downstream reliance until all required windows have closed without refusal and current evidence verifies that fact.
- Each principal's agreed window starts no earlier than finalization and authenticated delivery of the finalization notice to its designated channel. The notice includes exact terms and a usable refusal path. Delivery does not assert that a human has read it. A policy can demand stronger acknowledgment.
- An authenticated refusal admitted at or before the deadline prevails over closure. Closure requires the status authority's durable ordering and a time strictly after the deadline. Missing evidence remains pending or unresolved.
- Coordinator identity follows the author of the declared initiating record, never an inferred earliest timestamp. Crossed independent openings remain distinct until the parties explicitly select an origin for a common negotiation.
- A shared action shape standardizes qualification and authorship; extensions define the meaning of domain parameters. Unknown required semantics prevent automated issuance or adoption.

No universal refusal duration is selected. Each principal's policy supplies a positive duration; the parties adopt those rules before finalization. This specific review period does not impose a lifetime on the negotiation itself.
