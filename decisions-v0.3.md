# Governing-contract authoring decisions

**ABP 0.3-draft.** These choices make the [fifteen controlling decisions](decisions-v0.2.md) concrete. Draft 0.2 is preserved in Git history at `0011b504b706970c54a780d700be3efe444d4898`; [draft 0.1](archive/0.1/README.md) remains a historical archive.

| Choice | Definition in 0.3 | Reason |
|---|---|---|
| Six normative interfaces | [C1–C6](contracts/README.md) name actors, guards, permitted effects and failures | An independent harness needs enforceable requirements, not only product semantics. |
| Separate semantic record and interaction envelope | Requests bind exact record/status subject, recipient, permission basis and stable operation identity | A replay or transport acknowledgment cannot be mistaken for a new promise or an adoption. |
| Recipient-issued invitation | `admission_grant` exposes scoped permission under principal policy | Supports invitation-required policy without imposing it on permitted first offers. |
| Finite disclosed admission pools | Machine-readable admission declaration maps to an existing authenticated policy system | Iterative offers remain possible while carriers share accounting and control rights remain usable. |
| Explicit promise provenance | Candidate `promise_bindings` identifies an issued source or issuance by its own author at adoption | A coordinator cannot manufacture another agent's promise by copying an action into terms. |
| Exact revision and withdrawal rules | Strict lineage; candidate/adoption/grant withdrawal is representable | Retries, offer alternatives and a finalization race require attributable outcomes. |
| Explicit formation invocation | `finalize_candidate` asks the originator to form or recover one exact candidate outcome | A peer can recover a lost finalization without already knowing the accepted-object reference. |
| Attributable receipts | Pending, applied, declined, blocked and conflict report only the requested operation | No receipt creates broader consent or a forced negotiation outcome. |
| Owner-controlled capacity ordering | Native selection/reservation mechanisms govern shared resources across coordinators | Each originator cannot independently spend the same provider capacity. |
| Explicit principal-refusal transitions | First qualifying notice, durable refusal admission, closure evidence and absorbing refusal | Agent agreement preserves the agreed period of human refusal. |
| Concrete A2A binding | Typed data parts carry the signed request/receipt and referenced records | Uses native A2A instead of defining a new transport or task lifecycle. |

0.3 is a distinct semantic profile. Added required candidate provenance and governing interaction semantics are not silently imposed on 0.2 peers. Participants must activate and understand the selected profile. Existing illustrative records are migrated to 0.3 with regenerated local fixture digests; this does not turn their fictional proof references into signatures.

No universal quota, negotiation expiry, refusal duration, product ontology, principal policy engine, cryptographic suite, payment route, runtime or test regime is selected. The required profile hooks have explicit outputs and rejection behavior; a deployment must select and authenticate their concrete mechanisms before claiming interoperability.
