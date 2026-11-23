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


def test_push_small_report_without_pull_request(monkeypatch, tmp_path: Path) -> None:
    log = research_console.RunLog(tmp_path, "experiment")
    log.emit("FAIL", "train_and_validate_model", returncode=3)
    calls = []

    def fake_github(*args: str) -> str:
        calls.append(args)
        endpoint = args[0] if args else ""
        if "git/ref/heads/research-telemetry" in endpoint:
            return json.dumps({"object": {"sha": "abc123"}})
        if "contents/" in endpoint and "-X" not in args:
            from subprocess import CalledProcessError

            raise CalledProcessError(1, args, stderr="HTTP 404: Not Found")
        return "{}"

    monkeypatch.setattr(diagnostic_sync.shutil, "which", lambda _: "gh")
    monkeypatch.setattr(diagnostic_sync, "github", fake_github)
    assert diagnostic_sync.sync(log.path) == "UPLOADED"
    assert any("research-telemetry" in str(call) for call in calls)
    assert not any("pulls" in str(call) or "pr" in call for call in calls)


def test_extended_report_redacts_credentials_paths_and_urls(tmp_path: Path) -> None:
    log = research_console.RunLog(tmp_path, "experiment")
    log.console.write_text(
        "python C:\\\\Users\\\\Test\\\\project\\\\script.py "
        "token=abc12345678 https://example.org/data "
        "password=secret123 sk-abcdefghijklmnopqrst test@example.com\\n",
        encoding="utf-8",
    )
    log.emit("PASS", "complete")
    detailed = diagnostic_sync.extended_report(log.path)
    public = json.dumps(detailed)
    for private in (
        "abc12345678", "https://example.org", "secret123",
        "sk-abcdefghijklmnopqrst", "test@example.com", "Users",
    ):
        assert private not in public
    assert "[SECRET_FIELD]" in public
    assert "[URL]" in public
    assert detailed["kind"] == "redacted_extended_diagnostic"


def test_failed_git_sync_keeps_local_run_queued(monkeypatch, tmp_path: Path) -> None:
    log = research_console.RunLog(tmp_path, "experiment")
    log.emit("PASS", "complete")

    def unreachable(_folder: Path) -> str:
        raise RuntimeError("Offline")

    monkeypatch.setattr(diagnostic_sync, "sync", unreachable)
    uploaded, pending = diagnostic_sync.sync_pending(tmp_path / "logs")
    assert (uploaded, pending) == (0, 1)
    assert (log.path / "sync_pending.txt").exists()
    assert not (log.path / "sync_success.json").exists()


def test_extended_report_redacts_quoted_json_fields_beyond_preview_tail(
    tmp_path: Path,
) -> None:
    log = research_console.RunLog(tmp_path, "experiment")
    secret = "MyVeryPrivateNonPatternSecret"
    lines = [json.dumps({"password": secret, "step": "start"})]
    lines.extend("training step completed" for _ in range(25))
    log.console.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.emit("PASS", "complete")
    report = diagnostic_sync.extended_report(log.path)
    rendered = json.dumps(report)
    assert secret not in rendered
    assert "[SECRET_FIELD]" in rendered
    assert len(report["redacted_console_excerpt"]) > 12


def test_extended_report_covers_single_quoted_key_values(tmp_path: Path) -> None:
    log = research_console.RunLog(tmp_path, "experiment")
    log.console.write_text(
        "'secret': 'classified value'\\n password='another private value'\\n",
        encoding="utf-8",
    )
    log.emit("PASS", "complete")
    rendered = json.dumps(diagnostic_sync.extended_report(log.path))
    assert "classified value" not in rendered
    assert "another private value" not in rendered
