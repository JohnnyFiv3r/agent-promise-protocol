"""Package a clean, verified commit as local APP release assets. Never publish.

python checks/build_release_bundle.py --verification PATH/report.json --output-dir PATH
The verification report must describe this exact clean commit. Output must be fresh.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_inputs(report_path):
    report_bytes = report_path.read_bytes()
    report = json.loads(report_bytes)
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)
    if (
        dirty
        or report.get("result") != "passed"
        or report.get("source_dirty") is not False
        or report.get("source_commit") != head
    ):
        raise ValueError("A passed report for this exact clean commit is required")
    names = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .split("\0")
    )
    sources = {name: sha256(ROOT / name) for name in names if name}
    if report.get("source_files_sha256") != sources:
        raise ValueError("Source bytes differ from the verified manifest")
    metadata = json.loads((ROOT / "release.json").read_text())
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    if metadata["runtime_version"] != project["version"]:
        raise ValueError("Runtime release metadata differs from pyproject.toml")
    schemas = sorted(
        json.loads(path.read_text())["$id"]
        for path in (ROOT / "schemas").glob("*.schema.json")
    )
    if schemas != sorted(metadata["schema_ids"]):
        raise ValueError(
            "Schema release metadata differs from the authoritative schemas"
        )
    artifacts = []
    for item in report.get("artifacts", []):
        path = (report_path.parent / item["path"]).resolve()
        if (
            not path.is_relative_to(report_path.parent)
            or sha256(path) != item["sha256"]
        ):
            raise ValueError(
                "Distribution path or digest differs from verified artifact"
            )
        artifacts.append({"path": path, "sha256": item["sha256"]})
    stem = project["name"].replace("-", "_") + "-" + project["version"]
    expected = {stem + "-py3-none-any.whl", stem + ".tar.gz"}
    if {item["path"].name for item in artifacts} != expected or len(artifacts) != 2:
        raise ValueError("Expected exactly the verified wheel and source distribution")
    return head, sources, metadata, artifacts, report_bytes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verification", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report_path = args.verification.resolve()
    head, sources, metadata, artifacts, report_bytes = checked_inputs(report_path)
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error(
            "--output-dir must be fresh or empty; existing assets are never replaced"
        )
    output.mkdir(parents=True, exist_ok=True)
    tag = metadata["tag"]
    archive = output / (tag + "-reference-bundle.zip")
    subprocess.run(
        [
            "git",
            "archive",
            "--format=zip",
            "--prefix=" + tag + "/",
            "--output=" + str(archive),
            head,
        ],
        cwd=ROOT,
        check=True,
    )
    (output / "verification-report.json").write_bytes(report_bytes)
    for item in artifacts:
        path = item["path"]
        copied = output / path.name
        shutil.copyfile(path, copied)
        if sha256(copied) != item["sha256"]:
            raise ValueError(
                "Distribution changed while packaging; no release manifest produced"
            )
    manifest = {
        "release": metadata,
        "source_commit": head,
        "source_url": "https://github.com/JohnnyFiv3r/agent-promise-protocol/tree/"
        + head,
        "normative_sources_sha256": {
            name: sources[name] for name in metadata["normative_sources"]
        },
        "artifacts": [
            {"name": path.name, "sha256": sha256(path), "size": path.stat().st_size}
            for path in sorted(output.iterdir())
        ],
        "scope": "Reference draft and tested reference runtime; no provider deployment or independent interoperability certification.",
    }
    (output / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    checksum_lines = [
        sha256(path) + "  " + path.name for path in sorted(output.iterdir())
    ]
    (output / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n")
    print(
        json.dumps(
            {
                "tag": tag,
                "source_commit": head,
                "assets": sorted(p.name for p in output.iterdir()),
            }
        )
    )


if __name__ == "__main__":
    main()
