"""Privacy boundary and timing tests for automatic GitHub diagnostics."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import diagnostic_sync
import research_console


def test_snapshot_strips_local_paths_and_console_content(tmp_path: Path) -> None:
    log = research_console.RunLog(tmp_path, "experiment")
    log.progress(20, 100, 72)
    secret = "C:\\Users\\Private\\token-secret.txt"
    log.console.write_text(f"FAILED: {secret}", encoding="utf-8")
    log.emit("FAIL", "training_and_validation",
             returncode=2, message=f"Failure: {secret}")
    report = diagnostic_sync.snapshot(log.path)
    encoded = json.dumps(report)
    assert "token-secret" not in encoded
    assert "C:\\Users" not in encoded
    assert report["console_uploaded"] is False
    assert report["outcome"] == "FAIL"
    assert report["events"][1]["progress_percent"] == 20
    assert isinstance(report["elapsed_seconds"], float)
    assert report["local_console_sha256"]


def test_sync_refuses_incomplete_action(tmp_path: Path) -> None:
    log = research_console.RunLog(tmp_path, "experiment")
    with pytest.raises(ValueError, match="incomplete"):
        diagnostic_sync.snapshot(log.path)


def test_snapshot_rejects_unknown_event_fields(tmp_path: Path) -> None:
    log = research_console.RunLog(tmp_path, "experiment")
    log.emit("PASS", "complete")
    rows = log.events.read_text(encoding="utf-8").splitlines()
    row = json.loads(rows[0])
    row["stage"] = "../escape"
    rows[0] = json.dumps(row)
    log.events.write_text("\n".join(rows) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Untrusted event"):
        diagnostic_sync.snapshot(log.path)
