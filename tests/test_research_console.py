"""Offline lifecycle checks for the Windows/Fedora research console."""

from __future__ import annotations

import json
from pathlib import Path

import research_console as console


def test_profiles_share_one_lifecycle() -> None:
    assert console.EXPERIMENTS["p01_frcnn_lwir"]["dataset"] == "flir_adas_v2"
    assert console.EXPERIMENTS["p01_frcnn_lwir"]["script"].is_file()


def test_settings_live_outside_source_tree(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "settings.json"
    monkeypatch.setattr(console, "SETTINGS", target)
    monkeypatch.setattr(console, "STATE", tmp_path)
    settings = console.read_settings()
    settings["dataset_dirs"]["flir_adas_v2"] = str(tmp_path / "flir")
    console.save_settings(settings)
    assert console.read_settings()["dataset_dirs"]["flir_adas_v2"] == str(
        tmp_path / "flir"
    )
    assert json.loads(target.read_text())["runs_dir"]


def test_stage_failure_produces_diagnostics_without_gpu(tmp_path: Path) -> None:
    run = console.RunLog(tmp_path, "test")
    try:
        run.execute("intentional_failure", [
            console.sys.executable, "-c", "raise SystemExit(7)",
        ])
    except RuntimeError:
        pass
    else:
        raise AssertionError("Subprocess failure should propagate")
    event = json.loads(run.status.read_text(encoding="utf-8"))
    assert event["stage"] == "intentional_failure"
    assert event["status"] == "FAIL"
    assert event["returncode"] == 7
    assert "returncode=7" in run.console.read_text(encoding="utf-8")
    assert run.events.read_text(encoding="utf-8").count("\n") >= 2


def test_data_and_log_paths_cannot_be_inside_repository() -> None:
    try:
        console.directory(str(console.ROOT / "datasets"))
    except ValueError:
        pass
    else:
        raise AssertionError("Data paths under Git must be rejected")
