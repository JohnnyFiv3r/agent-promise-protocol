"""Verify a reference release; never publish or modify protocol sources.

Run with locked development dependencies and OPA 1.21.1 at .tools/opa:
    uv run --locked --extra dev python checks/release_check.py --output-dir PATH
PATH must be empty. UV_OFFLINE=1 and UV_CACHE_DIR may be used with a populated
local cache. Builds and an installed-wheel smoke test require uv on PATH.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OPA_VERSION = "1.21.1"
OPA_LINUX_AMD64_SHA256 = (
    "668506eb17a2eaa1fce6cc0d1f42ef85125d4ac5bda5fc74d1152d0c77145031"
)
REQUIRED_INTEGRATIONS = {
    "test_real_opa_1211_over_tls13_mtls",
    "test_real_tls13_mtls_a2a_handler",
    "test_real_tls_evidence_digest_allowlist_and_budget",
    "test_real_mtls_a2a_finalization_and_durable_replay",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_state():
    names = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT,
        )
        .decode()
        .split("\0")
    )
    manifest = {
        name: sha256((ROOT / name).read_bytes())
        for name in sorted(set(names))
        if name and (ROOT / name).is_file()
    }
    return {
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "dirty": bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)
        ),
        "files_sha256": manifest,
        "manifest_sha256": sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ),
    }


def test_summary(path):
    cases = list(ET.parse(path).getroot().iter("testcase"))
    summary = {"total": len(cases), "failures": 0, "errors": 0, "skipped": 0}
    for element, key in (
        ("failure", "failures"),
        ("error", "errors"),
        ("skipped", "skipped"),
    ):
        summary[key] = sum(case.find(element) is not None for case in cases)
    summary["passed"] = summary["total"] - sum(
        summary[key] for key in ("failures", "errors", "skipped")
    )
    seen = {case.attrib["name"] for case in cases}
    missing = REQUIRED_INTEGRATIONS - seen
    summary["required_integrations"] = sorted(REQUIRED_INTEGRATIONS)
    if (
        not cases
        or missing
        or summary["skipped"]
        or summary["failures"]
        or summary["errors"]
    ):
        raise RuntimeError(
            f"Incomplete test qualification: {summary}; missing={sorted(missing)}"
        )
    return summary


def check_distributions(wheel, sdist):
    expected = {
        str(path.relative_to(ROOT / "src")): path.read_bytes()
        for path in (ROOT / "src" / "agent_promise_protocol").rglob("*")
        if path.is_file()
        and (path.suffix == ".py" or path.name.endswith(".schema.json"))
    }
    authoritative = {
        path.name: path.read_bytes()
        for path in (ROOT / "schemas").glob("*.schema.json")
    }
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    metadata_prefix = (
        project["name"].replace("-", "_") + "-" + project["version"] + ".dist-info/"
    )
    with zipfile.ZipFile(wheel) as archive:
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
        unexpected = {
            name
            for name in names
            if name not in expected and not name.startswith(metadata_prefix)
        }
        if unexpected or len(names) != len(set(names)):
            raise RuntimeError(
                f"Unexpected or duplicated wheel members: {sorted(unexpected)}"
            )
        if not {
            metadata_prefix + name for name in ("METADATA", "WHEEL", "RECORD")
        } <= set(names):
            raise RuntimeError("Wheel is missing its own distribution metadata")
        if any(name.startswith("/") or ".." in Path(name).parts for name in names):
            raise RuntimeError("Wheel contains an unsafe member path")
        for name, data in expected.items():
            if archive.read(name) != data:
                raise RuntimeError(f"Wheel source mismatch: {name}")
        for name, data in authoritative.items():
            if archive.read(f"agent_promise_protocol/schemas/{name}") != data:
                raise RuntimeError(f"Wheel schema drift: {name}")
    with tarfile.open(sdist, "r:gz") as archive:
        prefix = archive.getnames()[0].split("/")[0]
        for name, data in expected.items():
            member = archive.extractfile(f"{prefix}/src/{name}")
            if member is None or member.read() != data:
                raise RuntimeError(f"Source distribution mismatch: {name}")
        for name, data in authoritative.items():
            member = archive.extractfile(f"{prefix}/schemas/{name}")
            if member is None or member.read() != data:
                raise RuntimeError(f"Source distribution schema drift: {name}")
    return {name: sha256(data) for name, data in expected.items()}


def snapshot_sources(source_files, destination):
    """Copy only the source manifest, checking bytes again before building."""
    for name, expected_digest in source_files.items():
        data = (ROOT / name).read_bytes()
        if sha256(data) != expected_digest:
            raise RuntimeError(f"Source changed before snapshot: {name}")
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


SMOKE = r"""
import hashlib, importlib.metadata, importlib.resources, json, pathlib, sys
import agent_promise_protocol
from agent_promise_protocol.errors import ProtocolError
from agent_promise_protocol.schema import validate

expected = json.loads(pathlib.Path(sys.argv[1]).read_text())
package = pathlib.Path(agent_promise_protocol.__file__).resolve().parent
assert package.is_relative_to(pathlib.Path(sys.prefix).resolve()), package
assert importlib.metadata.version("agent-promise-protocol") == expected["version"]
for name, digest in expected["files"].items():
    path = package.parent / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
for record in expected["records"]:
    validate(record)
    malformed = {**record, "unknown_release_smoke_field": True}
    try:
        validate(malformed)
    except ProtocolError:
        pass
    else:
        raise AssertionError("Installed schema accepted an unknown required shape")
print(json.dumps({"installed_version": expected["version"],
                  "package_outside_checkout": True,
                  "package_files_verified": len(expected["files"]),
                  "valid_and_invalid_schema_examples": len(expected["records"])}))
"""


def verify(output, report, redactions):
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    # Respect cache/offline options, but never inherit pytest selection or plugins.
    env.pop("PYTEST_ADDOPTS", None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv must be available on PATH")
    redactions[str(Path(uv).resolve())] = "<uv>"
    redactions[uv] = "<uv>"

    def run(name, command, *, cwd=ROOT):
        command = [str(item) for item in command]
        print(f"Verifying {name}", flush=True)
        result = subprocess.run(
            command, cwd=cwd, env=env, text=True, capture_output=True
        )
        (output / f"{name}.stdout.log").write_text(result.stdout)
        (output / f"{name}.stderr.log").write_text(result.stderr)
        report.setdefault("commands", []).append(
            {"name": name, "argv": command, "exit_code": result.returncode}
        )
        if result.returncode:
            raise RuntimeError(
                f"{name} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}"
            )
        return result.stdout

    opa = ROOT / ".tools" / "opa"
    if not opa.is_file():
        raise RuntimeError(
            "Required real OPA1.21.1 missing at .tools/opa; release checks cannot skip it"
        )
    opa_hash = sha256(opa.read_bytes())
    if (
        platform.system() == "Linux"
        and platform.machine() == "x86_64"
        and opa_hash != OPA_LINUX_AMD64_SHA256
    ):
        raise RuntimeError(
            "OPA Linux AMD64 binary does not match the pinned official static build"
        )
    version = run("opa-version", [opa, "version"])
    if f"Version: {OPA_VERSION}\n" not in version:
        raise RuntimeError(f"Expected OPA {OPA_VERSION}, received {version!r}")
    report["opa"] = {
        "version": OPA_VERSION,
        "sha256": opa_hash,
        "version_output": version,
    }
    report["uv"] = run("uv-version", [uv, "--version"]).strip()
    report["authoring"] = json.loads(
        run("authoring", [sys.executable, "checks/validate.py"])
    )
    run(
        "release-check-tests",
        [sys.executable, "-m", "pytest", "tests/release", "-q", "-ra"],
    )
    junit = output / "runtime-tests.xml"
    run(
        "runtime-tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/runtime",
            "-q",
            "-ra",
            f"--junitxml={junit}",
        ],
    )
    report["runtime_tests"] = test_summary(junit)
    dist = output / "dist"
    with tempfile.TemporaryDirectory(prefix="app-release-build-") as directory:
        snapshot = Path(directory).resolve()
        if snapshot.is_relative_to(ROOT):
            raise RuntimeError(
                "Release build snapshot must be outside the checkout; set TMPDIR elsewhere"
            )
        redactions[str(snapshot)] = "<build-snapshot>"
        snapshot_sources(report["source_files_sha256"], snapshot)
        run(
            "build",
            [uv, "build", "--wheel", "--sdist", "--out-dir", dist],
            cwd=snapshot,
        )
    wheels, sdists = list(dist.glob("*.whl")), list(dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise RuntimeError(
            "Expected exactly one fresh wheel and one fresh source distribution"
        )
    wheel, sdist = wheels[0], sdists[0]
    package_files = check_distributions(wheel, sdist)
    report["artifacts"] = [
        {
            "path": str(path.relative_to(output)),
            "sha256": sha256(path.read_bytes()),
            "size": path.stat().st_size,
        }
        for path in (wheel, sdist)
    ]
    report["distribution_source_check"] = {
        "package_files_verified": len(package_files),
        "authoritative_schemas": 3,
    }
    requirements = output / "locked-runtime-requirements.txt"
    run(
        "export-lock",
        [
            uv,
            "export",
            "--locked",
            "--no-dev",
            "--no-emit-project",
            "--output-file",
            requirements,
        ],
    )
    with tempfile.TemporaryDirectory(prefix="app-release-smoke-") as directory:
        outside = Path(directory).resolve()
        if outside.is_relative_to(ROOT):
            raise RuntimeError(
                "Installed-wheel smoke directory must be outside the checkout; set TMPDIR elsewhere"
            )
        redactions[str(outside)] = "<smoke>"
        venv = outside / "venv"
        python = venv / "bin" / "python"
        run("smoke-venv", [uv, "venv", "--python", sys.executable, venv], cwd=outside)
        run(
            "smoke-dependencies",
            [
                uv,
                "pip",
                "install",
                "--python",
                python,
                "--require-hashes",
                "-r",
                requirements,
            ],
            cwd=outside,
        )
        run(
            "smoke-install-wheel",
            [uv, "pip", "install", "--python", python, "--no-deps", wheel],
            cwd=outside,
        )
        expected = outside / "expected.json"
        expected.write_text(
            json.dumps(
                {
                    "version": tomllib.loads((ROOT / "pyproject.toml").read_text())[
                        "project"
                    ]["version"],
                    "files": package_files,
                    "records": [
                        json.loads((ROOT / "examples" / name).read_text())
                        for name in (
                            "candidate-terms.json",
                            "requester-publication.json",
                            "admission-policy.json",
                            "transaction-plan.json",
                            "handoff-request.json",
                        )
                    ],
                }
            )
        )
        report["installed_wheel"] = json.loads(
            run("smoke-schemas", [python, "-I", "-c", SMOKE, expected], cwd=outside)
        )
        demo = json.loads(
            run(
                "smoke-demo",
                [
                    venv / "bin" / "agent-promise-protocol",
                    "demo",
                    "--directory",
                    outside / "demo",
                ],
                cwd=outside,
            )
        )
        scenarios = demo["scenarios"]
        if (
            demo["evidence_scope"]["network_calls"] != 0
            or scenarios["bilateral"]["simulated_native_calls_after_replay"] != 1
            or scenarios["refusal_at_deadline"]["simulated_native_calls"] != 0
            or scenarios["refusal_at_deadline"]["same_receipt_on_replay"] is not True
            or scenarios["three_agent_composition"]["simulated_native_calls"] != 2
        ):
            raise RuntimeError("Installed demo failed its expected controlled outcomes")
        report["installed_demo"] = demo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="fresh/empty evidence directory (prefer outside checkout or .runtime/)",
    )
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error(
            "--output-dir must be empty; preserve prior evidence or choose a fresh path"
        )
    output.mkdir(parents=True, exist_ok=True)
    source = source_state()
    report = {
        "result": "failed",
        "python": sys.version,
        "platform": platform.platform(),
        "source_commit": source["git_sha"],
        "source_dirty": source["dirty"],
        "source_manifest_sha256": source["manifest_sha256"],
        "source_files_sha256": source["files_sha256"],
    }
    redactions = {
        str(ROOT): "<repository>",
        str(output): "<output>",
        sys.executable: "<python>",
    }
    try:
        verify(output, report, redactions)
        if source != source_state():
            raise RuntimeError(
                "Repository source changed during verification; rerun against a stable checkout"
            )
        report["result"] = "passed"
    except Exception as error:
        report["error"] = str(error)
        print(str(error), file=sys.stderr)
    finally:
        serialized = json.dumps(report, indent=2)
        for path in sorted(redactions, key=len, reverse=True):
            serialized = serialized.replace(path, redactions[path])
        (output / "report.json").write_text(serialized + "\n")
    print(f"Release verification {report['result']}: {output / 'report.json'}")
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
