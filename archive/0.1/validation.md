# Artifact validation

Checked October 8, 2026. Reproduce with `python3 checks/validate.py` from this artifact directory; Python 3 and `jsonschema` are required.

- JSON Schema is valid under Draft 2020-12, with URI/date-time format checking.
- Ten semantic-record fixtures validate: two publication contracts, two intents, a reception permit, four offers and candidate agreement terms.
- Five additional synthetic shapes validate: external route publication, external settlement terms, AP2 order-validation binding, downstream payment binding and a generic MCP offering using nonresearch performance/formation profiles. These shapes use fictional native references and prove no integration compatibility.
- Eighteen malformed structural cases are rejected, including missing immutable publication/route pins, missing finalization or AP2 references on payment, missing processors, unknown AP2 version, authority injected into intent/binding, missing reference-formation slot and automatic research acceptance on timeout.
- Three content-level route mismatch checks reject wrong digests, a route missing on one side and incompatible processor configurations. Complete objects must match, not independently selected components.
- Publication/policy/specification/performance references, intent-permit linkage, own/peer offer revision chains, selected final offer heads, rubric references and A2A embedding all match fixture content. Offers and candidate terms agree on the offering, settlement and complete selected route. Own-promise authors match performers/promisers.
- The full-book text reader's range union covers PDF pages 1–318 without gaps. Source digest and extraction/figure limits remain in [reading coverage](promise-theory-reading-coverage.json).
- Local document links, code-fence balance and all 63 unique conformance identifiers pass. Mermaid diagrams were reviewed as source; rendered layout was not automatically verified.
- Independent review identified and resolved the generic procurement-slot requirement, ambiguity about synthesizing routes, and reuse of native payment evidence across different accepted obligations. The normative binding now requires authenticated native correlation and no double counting.
- Contract-map review clarified that competing offers may differ, scoped delivery/review clocks to the research performance profile, and specified authenticated publication-status freshness and local decision ordering. These are normative requirements; no runtime status or race test was executed.

These are specification, schema and fixture checks. The 63 behavioral cases are **specified, not executed**. Runtime interoperability, live consent/status services, native authority/payment integration and semantic assessment require implementation. Structural validation does not establish consent, truth, obligation satisfaction or payment execution.

The schema covers publication, intent, reference permits, offers, candidate terms, standalone promises, external bindings and delivery. Formation receipts and assessments remain specified in normative prose; their complete wire schemas and proof/trust profiles remain release work. The examples do not form a live agreement. Current-status and specification URIs use the reserved documentation domain pending publication.
