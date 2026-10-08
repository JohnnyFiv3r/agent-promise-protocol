# Draft 0.4 authoring verification

**Authoring checks passed on October 8, 2026 for the local 0.4 draft.** These results are limited to the document checks below.

Follow the [setup instructions](README.md#status-and-checks), then run `python3 checks/validate.py` from the repository root. The checked state is identified below; future edits require a new recorded run before these results can describe that state.

## Current authoring run

| Item | Result for this 0.4 revision |
|---|---|
| Checked revision/working-tree state and run date | Uncommitted 0.4 working tree on `codex/agent-governing-contracts`, based on `0011b504b706970c54a780d700be3efe444d4898`; 2026-10-08 |
| Checker command and exit/result summary | `python3 checks/validate.py` exited 0 |
| Schemas checked as JSON Schema Draft 2020-12 | 3 valid schema documents |
| Semantic records checked against their schema | 29 fictional records across 20 defined semantic kinds |
| Interaction envelopes checked against their schema | 6 fictional request/receipt records |
| Admission declarations checked against their schema | 2 fictional declarations |
| Supporting fictional documents checked only for reference integrity | 27 documents; their policy/evidence contents are not schema validated |
| Local content references and authored payload digests checked | 327 local content references resolve with matching digests; fixture proof-payload digests are consistent |
| A2A construction-template parsing and placeholder checks | 2 JSON templates parse, retain explicit placeholders and use the 0.4 extension identifier; no native validator or server exercised |
| Markdown links, code fences and Git whitespace, if separately checked | 43 active Markdown documents have balanced fences; 251 local link targets exist; `git diff --check` passed. Remote links and fragment anchors not verified by this check. |

These are document-authoring checks. The checker covers its implemented structural/reference constraints; JSON Schema and local consistency checks cannot establish all cross-record authority, ordering, freshness, truthfulness or effect guarantees in C1–C8. Supporting evidence with no adopted structural schema is not made valid authority by being reachable through a matching digest.

A read-only specification review can identify contradictions, missing guards and field mismatches. It is design-review evidence, not proof that a participant implementation enforces the reviewed requirements. Historical draft results remain historical and must not be relabeled as 0.4 verification.

## Proofs, examples and templates

Current fixtures are fictional design-review material. Documentation proof references and unsigned/fictitious native evidence do not establish cryptographic authorship or current delegation. The selected real reference-profile mechanisms remain distinct from nonvalidating examples; selecting a mechanism in prose is not running its verifier.

The fixture digest helper is limited to the authored ASCII/safe-integer values documented by the checker. Its checks do not establish a general RFC 8785 implementation. Construction templates with placeholders may parse as JSON without constituting complete native requests, authenticated records or interoperability evidence.

No authoring check proves actual capability, truthful capacity, human notification, refusal timing, durable runtime behavior, real adapter idempotency, service delivery, assessment quality, native authorization or settlement.

## Proposed tests are not validation results

[tests/PROPOSED.md](tests/PROPOSED.md) contains **27 proposed, unrun scenarios, P01–P27**. The proposal covers behavioral correctness and failure handling, then separately assesses builder adoption through a future SDK, independent implementation without it and the minimal bilateral path. The SDK is not implemented by this specification work. No result is claimed for adoption, runtime conformance or independent interoperability.

After contract/profile lock, executable fixtures and behavioral checks may be implemented within the agreed scope. The proposed adapter probes use controlled fakes and injected evidence only. They stop before real native services, orders, mandates, payments, transfers and settlement; successful fake behavior cannot be reported as verified AP2 or other live integration.

[Conformance status](conformance.md) defines how these evidence categories remain separate. No executable test suite, agent runtime, SDK, live service connector or payment implementation is established by these authoring results.
