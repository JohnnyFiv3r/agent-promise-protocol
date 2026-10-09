"""Do not publish artifacts that changed after the verification check."""

import hashlib
import importlib.util
from pathlib import Path
import sys

import pytest


spec = importlib.util.spec_from_file_location(
    "build_release_bundle",
    Path(__file__).resolve().parents[2] / "checks/build_release_bundle.py",
)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def test_bundle_rechecks_copied_artifact_against_verified_digest(tmp_path, monkeypatch):
    wheel = tmp_path / "package.whl"
    expected = hashlib.sha256(b"verified bytes").hexdigest()
    wheel.write_bytes(b"replacement after input verification")
    output = tmp_path / "assets"
    monkeypatch.setattr(
        bundle,
        "checked_inputs",
        lambda path: (
            "commit",
            {},
            {"tag": "app-test", "normative_sources": []},
            [{"path": wheel, "sha256": expected}],
            b'{"result":"passed"}',
        ),
    )

    def archive(command, **kwargs):
        target = next(
            part.removeprefix("--output=")
            for part in command
            if part.startswith("--output=")
        )
        Path(target).write_bytes(b"source archive")

    monkeypatch.setattr(bundle.subprocess, "run", archive)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_release_bundle.py",
            "--verification",
            str(tmp_path / "report.json"),
            "--output-dir",
            str(output),
        ],
    )
    with pytest.raises(ValueError, match="Distribution changed while packaging"):
        bundle.main()
    assert not (output / "release-manifest.json").exists()
    assert not (output / "SHA256SUMS").exists()
