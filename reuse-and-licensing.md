# Agent Bazaar: licensing and independent implementation

**User-directed decision · October 8, 2026:** Bazaar's original specification, schemas, examples and implementation use the [MIT license](LICENSE). Comparison frameworks supply inspiration where permitted. Their implementation code, schemas, normative prose and test suites are not copied, translated or adapted into Bazaar.

This supersedes the earlier recommendation to adopt components from A202, AMP/ASA or other comparators. No comparison code or fixture suite was imported into the project. The research was not a clean-room exercise: selected public source was inspected. Future work must be independently authored from the Bazaar requirements and cited conceptual sources, without claiming an isolated provenance process that did not occur.

Existing A2A, MCP, AP2, checkout and payment protocols remain integration targets under their own specifications. That interoperability boundary does not require incorporating a comparison marketplace's implementation. Third-party materials linked for research retain their own licenses; Bazaar's MIT license does not relicense them.

The [required contract map](contract-map.md) now drives authoring. The findings below remain a source-availability record, not a dependency-selection plan.

## Verified licenses and availability

| Project | License and available material | Use as related work |
|---|---|---|
| **A202** | **Apache-2.0** at `8473b0421fdc2a0d9e4bcd299cf9937ee68bf556`: specification, schemas, Python reference code and conformance suite. Documentation fonts have separate SIL OFL 1.1 licenses. [License](https://github.com/a202-protocol/a202/blob/8473b0421fdc2a0d9e4bcd299cf9937ee68bf556/LICENSE), [reference implementation](https://github.com/a202-protocol/a202/blob/8473b0421fdc2a0d9e4bcd299cf9937ee68bf556/reference/README.md)  | Conceptual comparison for exact acceptance and conformance design; no code, schemas or fixtures adopted. |
| **AMP** | **Apache-2.0**, confirmed in root license and Python/TypeScript metadata at `40a55ca3804fc806dee6e96a942b69ef5af53018`. [License](https://github.com/alexfleetcommander/agent-matchmaking/blob/40a55ca3804fc806dee6e96a942b69ef5af53018/LICENSE)  | Conceptual comparison for discovery and RFQ boundaries. |
| **Agent Service Agreements (ASA)** | **Apache-2.0**, confirmed in root license and both language manifests at `d86945286402a298a7262e297c2d9bade38e48ea`. [License](https://github.com/alexfleetcommander/agent-service-agreements/blob/d86945286402a298a7262e297c2d9bade38e48ea/LICENSE)  | Conceptual comparison for negotiated performance terms and failure handling. |
| **TOS implementation** | **GPL v3** at `a70ee803611dcd51a584b42015154b0f443d4d55`. [License](https://github.com/tosnetwork/tos-service-protocol/blob/a70ee803611dcd51a584b42015154b0f443d4d55/LICENSE)  | Conceptual comparison for own-obligor authority, revisions and replay. |
| **TOS specification** | Publicly readable; no general license grant found in the inspected tree at `80739a8f670e335e581e5b99eef54ad032d5cf3d`. [Repository](https://github.com/tosnetwork/tos-service-spec/tree/80739a8f670e335e581e5b99eef54ad032d5cf3d)  | Public reference; no copied prose, schemas or scripts and no assumption of a general reuse grant. |
| **BotVibes** | **Apache-2.0** for public SDK, specification, examples and docs at `2c7b5474534afd369d219155c23fe03002a07884`. Its README explicitly says the **engine source is not yet public**. [License](https://github.com/Axsar/botvibes/blob/2c7b5474534afd369d219155c23fe03002a07884/LICENSE), [availability](https://github.com/Axsar/botvibes/blob/2c7b5474534afd369d219155c23fe03002a07884/README.md)  | Compare discovery, firm-quote and acceptance semantics; no SDK or engine adoption. |
| **ERABI** | **Apache-2.0** public monorepo at `07505e37936afd573b7688c0dfd9b98a8aee1938`, including SDKs, schemas and exchange components. [License](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/LICENSE), [NOTICE](https://github.com/HMAKT99/Erabi/blob/07505e37936afd573b7688c0dfd9b98a8aee1938/NOTICE)  | Compare disclosure and marketplace boundaries; preserve the distinction between sponsorship bids and service promises. |
| **Duami** | Public service documentation and API; **no verified OSS implementation or license**. The repository linked by a third-party registry returned Not Found. [Official manual](https://duami.ai/llms.txt), [API](https://duami.ai/openapi.json), [terms](https://duami.ai/terms)  | Compare the symmetric intent and counterproposal journey; no implementation adoption. |
| **CSNP** | **MIT** at `f2c0502de6674a5667b72f12e081d30e9d696847`; Python library, CLI, consent guard and tests. Package identifies itself as 0.1.0 Alpha. [License](https://github.com/molanocortes/consent-scoped-agent-negotiation/blob/f2c0502de6674a5667b72f12e081d30e9d696847/LICENSE), [ScopeGuard](https://github.com/molanocortes/consent-scoped-agent-negotiation/blob/f2c0502de6674a5667b72f12e081d30e9d696847/src/csnp/scope.py)  | Conceptual comparison for consent to discuss versus commit and finite interaction. |
| **Beckn v2 specification** | The inspected repository's LICENSE is **CC BY-NC-SA 4.0**, including a noncommercial restriction. [License](https://github.com/beckn/protocol-specifications-v2/blob/main/LICENSE)  | Public comparison only; do not copy or adapt its restricted specification material. |


## Independent authoring rule

Derive the contracts from the agreed diagram, the user's product thesis and the Promise Theory primitives: emitted intent, recipient autonomy, proposed own behavior, requested counterpart behavior and each promiser's own adoption. Use related work to challenge omissions and identify interoperability differences. Write Bazaar's schemas, transition rules, examples and adversarial cases from those requirements.

Draft 0.2 treats a Bazaar offer as the issuer's qualified conditional promise. Any adapter must preserve its conditions, principal refusal rights and authorship; neither the offer nor accepted terms can become a native purchase instruction without that consumer's required authority. Any eventual adapter must preserve those semantics and its native system's evidence. This is an interface requirement, not a code-reuse decision.

The original material in this artifact directory is covered by [LICENSE](LICENSE). The copyright notice uses John Inniger, the recorded project owner. The [standard MIT text](https://opensource.org/license/mit) grants reuse of our work subject to its notice requirement; it does not grant rights in separately referenced materials.

## Research coverage

The license checks above inspected exact repository licenses and selected package metadata. They establish the stated source availability, not production readiness or permission to copy material outside each grant. A202's source included a manifest with 148 fixtures, but none were executed. Its README's release assertion conflicted with public tag/release retrieval; the commit pin records the inspected source. No native integrations were executed.

The earlier [recursive overlap audit](novel-angle-audit.md) remains useful for evaluating the design's scope. Its component-adoption suggestions are superseded by the user's independent-implementation decision.
