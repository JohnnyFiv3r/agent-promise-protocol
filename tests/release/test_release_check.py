"""Protect the release gate against skipped integrations and altered packages."""

import importlib.util
import io
from pathlib import Path
import tarfile
import xml.etree.ElementTree as ET
import zipfile

import pytest


spec = importlib.util.spec_from_file_location(
    "release_check", Path(__file__).resolve().parents[2] / "checks/release_check.py"
)
release_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_check)


def junit(tmp_path, *, outcome=None, missing=False):
    root = ET.Element("testsuites")
    suite = ET.SubElement(root, "testsuite")
    names = sorted(release_check.REQUIRED_INTEGRATIONS)
    for name in names[1:] if missing else names:
        case = ET.SubElement(suite, "testcase", name=name)
        if outcome:
            ET.SubElement(case, outcome)
    path = tmp_path / "tests.xml"
    ET.ElementTree(root).write(path)
    return path


def test_release_requires_all_real_integrations(tmp_path):
    summary = release_check.test_summary(junit(tmp_path))
    assert summary["passed"] == len(release_check.REQUIRED_INTEGRATIONS)
    assert summary["skipped"] == 0
    with pytest.raises(RuntimeError, match="Incomplete test qualification"):
        release_check.test_summary(junit(tmp_path, missing=True))


@pytest.mark.parametrize("outcome", ["skipped", "failure", "error"])
def test_release_rejects_incomplete_pytest_results(tmp_path, outcome):
    with pytest.raises(RuntimeError, match="Incomplete test qualification"):
        release_check.test_summary(junit(tmp_path, outcome=outcome))


def test_release_detects_wheel_and_sdist_schema_drift(tmp_path, monkeypatch):
    monkeypatch.setattr(release_check, "ROOT", tmp_path)
    package = tmp_path / "src/agent_promise_protocol/schemas"
    package.mkdir(parents=True)
    authoritative = tmp_path / "schemas"
    authoritative.mkdir()
    (package / "contract.schema.json").write_bytes(b'{"version":1}')
    (authoritative / "contract.schema.json").write_bytes(b'{"version":1}')
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="agent-promise-protocol"\nversion="0.1.0"\n'
    )
    wheel, sdist = tmp_path / "package.whl", tmp_path / "package.tar.gz"

    def distributions(*, wheel_bytes=b'{"version":1}', sdist_bytes=b'{"version":1}'):
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr(
                "agent_promise_protocol/schemas/contract.schema.json", wheel_bytes
            )
            for name in ("METADATA", "WHEEL", "RECORD"):
                archive.writestr("agent_promise_protocol-0.1.0.dist-info/" + name, b"")
        with tarfile.open(sdist, "w:gz") as archive:
            for name in (
                "src/agent_promise_protocol/schemas/contract.schema.json",
                "schemas/contract.schema.json",
            ):
                member = tarfile.TarInfo(f"package/{name}")
                member.size = len(sdist_bytes)
                archive.addfile(member, io.BytesIO(sdist_bytes))

    distributions()
    assert len(release_check.check_distributions(wheel, sdist)) == 1
    distributions(wheel_bytes=b'{"version":2}')
    with pytest.raises(RuntimeError, match="Wheel source mismatch"):
        release_check.check_distributions(wheel, sdist)
    distributions(sdist_bytes=b'{"version":2}')
    with pytest.raises(RuntimeError, match="Source distribution mismatch"):
        release_check.check_distributions(wheel, sdist)
    distributions()
    with zipfile.ZipFile(wheel, "a") as archive:
        archive.writestr("agent_bazaar/__init__.py", b"# stale pre-rename build")
    with pytest.raises(RuntimeError, match="Unexpected or duplicated wheel members"):
        release_check.check_distributions(wheel, sdist)


def test_build_snapshot_omits_ignored_build_state_and_detects_source_drift(
    tmp_path, monkeypatch
):
    source = tmp_path / "source"
    source.mkdir()
    monkeypatch.setattr(release_check, "ROOT", source)
    (source / "module.py").write_bytes(b"SOURCE = True\n")
    stale = source / "build/lib/agent_bazaar/__init__.py"
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"STALE = True\n")
    snapshot = tmp_path / "snapshot"
    manifest = {"module.py": release_check.sha256((source / "module.py").read_bytes())}
    release_check.snapshot_sources(manifest, snapshot)
    assert list(snapshot.iterdir()) == [snapshot / "module.py"]
    assert (snapshot / "module.py").read_bytes() == b"SOURCE = True\n"
    assert stale.exists()
    (source / "module.py").write_bytes(b"SOURCE = 'changed'\n")
    with pytest.raises(RuntimeError, match="Source changed before snapshot"):
        release_check.snapshot_sources(manifest, tmp_path / "changed-snapshot")
