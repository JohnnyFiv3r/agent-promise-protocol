# Default harness: integration contract

**APP 0.4 / RP1 · application integration contract.** Reference runtime **0.1.0** supplies the Python mechanics described in the [runtime guide](../docs/runtime.md). The high-level facade below remains a proposed SDK interface, not the package's callable API.

The harness packages the [reference profile](reference-profile.md) so the ordinary application does not implement C1–C6 itself. The universal contract remains the interoperability authority; a convenient facade cannot redefine its semantics.

## Three responsibility layers

| Layer | Responsibility |
|---|---|
| Universal contract | Self-authored qualified promises, exact adoption, bilateral authority, mandatory recovery, dependency and evidence semantics |
| Default profile/harness | Fixed verification/retrieval/policy plumbing, admission, replay, durable formation, key handling, current status, principal notice/refusal and supported handoff gates |
| Application | Truthful capability/constraints, actual principal authority and policy, action vocabulary and real native integrations |

One deployment configuration selects the RP1 preset and its trust/authority bindings. Per-capability registration supplies the application's facts and callbacks. The application is not asked to implement JCS, signatures, a policy interpreter or an operation journal. A deployment claiming the preset must still operate those mechanisms correctly; the spec does not make them disappear.

## Hosting and connector boundary

The same participant semantics apply to an embedded assistant and to a hosted runtime reached through one optional connector. A seller exposes a compatible A2A APP endpoint. The participant's provider maintains its delegated keys, durable journal, inbound interactions and principal channels; an individual tool call or chat session is not the agreement lifetime. Hosting several principals does not merge their identities, disclosure permissions, admission pools or resource authority.

Discovery, filtered intent distribution, offer comparison and the model-facing connector are application functions. They may be supplied by different providers and are not required harness algorithms or new wire methods. The [deployment model](../deployment-model.md) defines the role/custody separation, and the [independent-participant slice](../design/independent-participant-slice.md) states what remains beyond the shared-store runtime.

## Registration surface

A registration identifies `capability_semantics_ref`, `principal_policy_ref`, `capacity_provider`, `principal_channel`, and optionally an `adapter` implementing C8. It declares the features it needs. `bilateral` is always supported by RP1; `composition`, `adapter-handoff` and `lifecycle-evidence` are optional additional capabilities; adapter-handoff requires lifecycle-evidence.

The harness MUST verify that principal delegation covers registration and later acts, the semantics are understood, required qualification facts can be obtained and the protected refusal mechanism is usable. It MUST NOT advertise capabilities that exist only as an unchecked function name. Application callbacks may return unknown; the dependent automatic transition then remains blocked.

## Proposed application facade

Names below specify the intended facade and obligations, not a published library API or copy-paste code.

| Call | Application supplies | Harness responsibility and result |
|---|---|---|
| `emitIntent` | Outcome/preferences and permitted publication scope | Qualify/sign the declaration, enforce publication policy, return its immutable reference |
| `offer` | Exact own action descriptions, requested counteractions and agreement terms | Verify capability/authority, apply option lineage/admission policy, issue the author's qualified promise and return its reference |
| `selectCandidate` | Selected exact option references and any explicit own counteractions | Verify the caller is the coordinator, create one exact candidate including mandatory recovery/default handoff rules, distribute its full reference |
| `adopt` | The exact selected candidate reference and delegated decision | Revalidate the author's authority/own actions, issue exact adoption and recover formation under C4 |
| `observeAgreement` | Accepted reference or candidate reference awaiting formation | Return separate agreement, recovery and optional handoff observations with original evidence; never infer assent from silence |
| `requestHandoff` | Exact accepted action occurrence and selected registered adapter | When feature-enabled, prepare, guard dispatch and recover through C8; return disposition/evidence, not an unsupported success claim |

The negotiating model sees typed application intent, proposed terms and scoped decisions. It does not manufacture keys, credentials, proof references, receipt revisions, deadlines or native payment authority. The harness constructs mechanical records from verified sources. Human approval required by policy remains a separate prerequisite; it does not remove the later protected recovery period.

## Application observations

The facade returns an immutable accepted reference once formed and separates:

- `agreement`: `not_formed`, `formed`, or `unresolved`, backed by the relevant exact records.
- `recovery`: `pending`, `cleared`, `refused`, or `unresolved`. These map to `pending_refusal_windows`, `refusal_windows_closed`, `refused`, `unresolved`; they never create a new protocol state or shorten a period.
- `handoff`, when enabled: the exact C8 phase/outcome and relevant evidence. Absence of this field means no handoff conclusion.

A consumer must preserve evidence freshness and known newer conflicts. An application-friendly observation is a projection of signed records, not an alternative unsigned source of truth.

## Adapter callbacks and limits

A registered adapter exposes the selected C8 `Prepare`, `Dispatch` and `Reconcile` behavior plus a native-authority check. Prepare is side-effect-free. Dispatch uses the exact frozen plan and stable key only after the gate. Reconcile observes that same operation without initiating it. Native action authority and the truth of external outcomes belong to the native integration; the harness verifies their attributable evidence under the selected semantics.

A capacity callback supplies real availability and exclusivity facts; the harness enforces the declared shared constraints. A notification callback connects the principal's designated channel; it cannot report a queued send as qualifying notice. A native adapter cannot label an irreversible action as preparation to evade recovery. The harness MUST block an integration whose required guarantee cannot be established.

## Default and advanced paths

A baseline deployment need not enable C7 or create transaction plans. It can negotiate and observe one agreement using C1–C6 and the RP1 preset. Optional composition repeats that same primitive with explicit plan/binding rules. Optional handoff/evidence uses C8 with the agreed native integrations. Required features are negotiated before adoption; unsupported features fail explicitly.

The [runtime tests and validation record](../validation.md) exercise the implemented mechanics. The broader [proposed tests](../tests/PROPOSED.md) assess correctness and adoption separately; passing implementation tests does not by itself establish independent interoperability or builder ease of adoption. Use the [implementer guide](../docs/implementer-guide.md) for the current entry path.
