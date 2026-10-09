# Publishing a reference release

APP is published as a reference draft with an independently implemented MIT runtime. The release does not certify a provider's deployment, independent interoperability or downstream native integrations.

## Release identity and review

`release.json` records the protocol, RP1 and runtime versions separately. Keep it consistent with `pyproject.toml`, the authoritative schemas, the extension identifiers and `CHANGELOG.md`. The first APP tag is `app-v0.4-draft.1`; its Python runtime is `0.1.0`. APP's [namespace transition](docs/namespace-transition.md) is explicit and does not migrate old signed records.

Maintainers accept changes through an open pull request. Run the reference-verification workflow, address review findings and merge the reviewed revision. Use a new tag for each release; never move a published tag or replace assets to disguise different source bytes. Breaking semantics require new identifiers and participant understanding. Documentation or implementation corrections cannot change an already adopted agreement.

## Verify the exact release commit

Start from the clean merged commit. Install Python 3.11 or newer and uv, then run `uv sync --locked --extra dev`. The separately installed `.tools/opa` must be the official OPA 1.21.1 executable; the [CI workflow](.github/workflows/ci.yml) contains the pinned Linux asset/checksum and [policy notes](policies/README.md) identify the Darwin build used locally.

```sh
uv run --locked --extra dev python checks/release_check.py --output-dir .runtime/release-verification
uv run --locked --extra dev python checks/build_release_bundle.py \
  --verification .runtime/release-verification/report.json \
  --output-dir .runtime/release-assets
```

Both output directories must be fresh. The verifier requires real OPA/mTLS integration and zero skipped runtime tests, verifies source stability, builds the wheel and source distribution, checks their bytes against the checkout, and tests the installed wheel outside the checkout with hash-locked dependencies. It runs release-gate tests separately from protocol runtime tests. A missing integration is a failure, not a successful skipped run.

The bundle builder requires a passed report for the exact clean commit, verifies its source/artifact hashes and copies only its checked distributions. It produces:

- A complete committed reference-source ZIP, including normative sources, schemas, fictional examples, documentation, tests and runtime source.
- The tested Python wheel and source distribution.
- `verification-report.json`, identifying the executed checks and exact source state.
- `release-manifest.json`, identifying versions, source commit, normative-source hashes and artifact hashes.
- `SHA256SUMS`, covering the preceding assets.

The report contains sanitized paths. Diagnostic command logs are retained in the verification directory/CI artifact for inspection, but are not automatically included as public release assets. The example/demonstration evidence limits remain attached to the source and report.

## Publish and verify

Check that the merged commit's GitHub workflow is green and its reviews are addressed. Create and push an annotated tag from that exact commit, then create a GitHub prerelease titled **APP 0.4 Reference Draft** with the generated assets and concrete release notes. The prerelease label describes the protocol's reference-draft status.

After publication, verify that the remote tag resolves to the intended commit, the release is public, every asset is present and downloaded asset hashes match `SHA256SUMS`. The GitHub source/tag URLs provide immutable retrieval; `main` remains a moving development branch. A GitHub release is sufficient for this distribution; publication to PyPI is a separate decision.

Keep historical manifests under `validation/` unchanged. They describe their original commits and namespaces. Fresh release evidence is generated and attached to the corresponding release instead of relabeling an old run.
