"""Safety smoke tests for the local P01 orchestrator, without FLIR or GPU."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "publications/P01/analyses/run_local_pipeline.py"
)
SPEC = importlib.util.spec_from_file_location("p01_local_pipeline", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_missing_archive_never_downloads_without_pinned_manifest(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="FLIR archive absent"):
        MODULE.acquire(tmp_path / "archive", None)
    assert not (tmp_path / "archive").exists()


def test_rights_acknowledgement_required(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as error:
        MODULE.main([
            "--parts-dir", str(tmp_path / "archive"),
            "--work-dir", str(tmp_path / "run"),
        ])
    assert error.value.code == 2
    assert not (tmp_path / "run").exists()


def test_output_inside_repository_rejected() -> None:
    with pytest.raises(SystemExit) as error:
        MODULE.main([
            "--parts-dir", str(MODULE.ROOT / "archive"),
            "--work-dir", str(MODULE.ROOT / "run"),
            "--rights-acknowledged",
        ])
    assert error.value.code == 2
