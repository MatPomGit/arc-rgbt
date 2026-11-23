"""Upload bounded, privacy-safe experiment diagnostics to one GitHub results PR.

The full console log stays local. An open non-results PR blocks upload; the
run remains queued locally for a later retry. Never write to main directly.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = "MatPomGit/arc-rgbt"
BRANCH = "p01-validation-results"
STATES = {"PASS", "FAIL", "BLOCKED", "RUNNING"}
ACTIONS = {"install", "configure_data", "diagnostics", "experiment", "publication"}
STAGE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
RUN_ID = re.compile(r"^\d{8}T\d{6}Z_[0-9a-f]{8}$")


def github(*args: str) -> str:
    result = subprocess.run(
        ["gh", "api", *args], check=True, text=True, capture_output=True,
        cwd=ROOT,
    )
    return result.stdout.strip()


def snapshot(folder: Path) -> dict:
    """Whitelist only structured telemetry, never copy console or traceback."""
    if not RUN_ID.fullmatch(folder.name):
        raise ValueError("Malformed run identifier")
    events_file = folder / "events.jsonl"
    if not events_file.is_file() or events_file.stat().st_size > 1024 * 1024:
        raise ValueError("Missing or oversized event log")
    rows = [json.loads(line) for line in events_file.read_text(encoding="utf-8").splitlines()]
    if not 1 <= len(rows) <= 5000:
        raise ValueError("Invalid event count")
    last = rows[-1]
    if last["status"] not in {"PASS", "FAIL", "BLOCKED"}:
        raise ValueError("Do not publish incomplete runs")
    action = last["action"]
    if action not in ACTIONS:
        raise ValueError("Invalid action")
    sanitized = []
    for row in rows:
        if (row.get("action") != action or row.get("run_id") != folder.name
                or row.get("status") not in STATES
                or not isinstance(row.get("stage"), str)
                or not STAGE.fullmatch(row["stage"])):
            raise ValueError("Untrusted event field")
        point = datetime.fromisoformat(row["time_utc"])
        if point.tzinfo is None:
            raise ValueError("UTC offset required")
        sanitized.append({
            "time_utc": point.isoformat(), "stage": row["stage"],
            "status": row["status"],
            **({"elapsed_seconds": row["elapsed_seconds"]}
               if type(row.get("elapsed_seconds")) in (int, float)
               and 0 <= row["elapsed_seconds"] <= 30 * 86400 else {}),
            **({"progress_percent": row["progress_percent"]}
               if type(row.get("progress_percent")) in (int, float)
               and 0 <= row["progress_percent"] <= 100 else {}),
            **({"eta_seconds": row["eta_seconds"]}
               if type(row.get("eta_seconds")) is int
               and 0 <= row["eta_seconds"] <= 30 * 86400 else {}),
            **({"returncode": row["returncode"]}
               if type(row.get("returncode")) is int else {}),
            **({"substage": row["substage"]}
               if isinstance(row.get("substage"), str)
               and STAGE.fullmatch(row["substage"]) else {}),
            **({"error_type": row["error_type"]}
               if row.get("error_type") in
               {"RuntimeError", "ValueError", "OSError", "KeyError", "CalledProcessError"} else {}),
        })
    # Event timestamps are UTC ISO-8601. Exact epoch timings remain locally
    # in the full log; published spans use monotonic-independent UTC timestamps.
    durations = []
    for prev, nxt in zip(sanitized, sanitized[1:], strict=False):
        delta = (datetime.fromisoformat(nxt["time_utc"]) -
                 datetime.fromisoformat(prev["time_utc"])).total_seconds()
        durations.append(max(0.0, round(delta, 3)))
    console_file = folder / "console.log"
    report = {
        "schema_version": 1, "kind": "diagnostic_only",
        "run_id": folder.name, "action": action,
        "started_utc": sanitized[0]["time_utc"],
        "finished_utc": sanitized[-1]["time_utc"],
        "elapsed_seconds": sanitized[-1].get("elapsed_seconds", round((
            datetime.fromisoformat(sanitized[-1]["time_utc"]) -
            datetime.fromisoformat(sanitized[0]["time_utc"])
        ).total_seconds(), 3)),
        "outcome": last["status"],
        "events": sanitized,
        "between_event_seconds": durations,
        "local_console_bytes": console_file.stat().st_size if console_file.exists() else 0,
        "local_console_sha256": (
            hashlib.sha256(console_file.read_bytes()).hexdigest()
            if console_file.exists() and console_file.stat().st_size <= 32 * 1024 * 1024
            else None
        ),
        "console_uploaded": False,
        "raw_dataset_uploaded": False,
        "weights_uploaded": False,
    }
    data = json.dumps(report, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if len(data) > 96 * 1024:
        raise ValueError("Diagnostic report exceeds 96 KiB")
    return report


def sync(folder: Path) -> str:
    """Return UPLOADED, ALREADY_UPLOADED or BLOCKED; no hidden retry loop."""
    if not shutil.which("gh"):
        raise RuntimeError("gh CLI is unavailable; local diagnostic queued")
    report = snapshot(folder)
    raw = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    relative = f"publications/P01/results/diagnostics/{report['run_id']}.json"
    prs = json.loads(github(f"repos/{REPO}/pulls?state=open&per_page=100"))
    if any(pr["head"]["ref"] != BRANCH for pr in prs):
        raise RuntimeError("Another PR is open; local diagnostic queued")
    try:
        github(f"repos/{REPO}/git/ref/heads/{BRANCH}")
    except subprocess.CalledProcessError:
        head = json.loads(github(f"repos/{REPO}/git/ref/heads/main"))["object"]["sha"]
        github("-X", "POST", f"repos/{REPO}/git/refs",
               "-f", f"ref=refs/heads/{BRANCH}", "-f", f"sha={head}")
    try:
        existing = json.loads(github(f"repos/{REPO}/contents/{relative}?ref={BRANCH}"))
    except subprocess.CalledProcessError:
        existing = None
    if existing is not None:
        result = "ALREADY_UPLOADED"
    else:
        import base64
        payload = {
            "message": f"chore(P01): anonymized diagnostic {report['run_id']}",
            "branch": BRANCH, "content": base64.b64encode(raw).decode("ascii"),
        }
        with tempfile.TemporaryDirectory(prefix="p01-logs-") as temp:
            body = Path(temp) / "request.json"
            body.write_text(json.dumps(payload), encoding="utf-8")
            github("-X", "PUT", f"repos/{REPO}/contents/{relative}",
                   "--input", str(body))
        result = "UPLOADED"
    if not any(pr["head"]["ref"] == BRANCH for pr in prs):
        subprocess.run([
            "gh", "pr", "create", "--repo", REPO, "--base", "main",
            "--head", BRANCH, "--title", "P01: validation results and diagnostics",
            "--body", "Sanitized run telemetry only. No console traces, local paths, "
            "images, predictions or model weights. Not scientific GO.",
        ], cwd=ROOT, check=True, capture_output=True, text=True)
    return result


def sync_pending(logs: Path) -> tuple[int, int]:
    uploaded, blocked = 0, 0
    for folder in sorted(logs.iterdir()) if logs.exists() else []:
        if not folder.is_dir() or (folder / "sync_success.json").exists():
            continue
        try:
            result = sync(folder)
            (folder / "sync_success.json").write_text(
                json.dumps({"status": result}) + "\n", encoding="utf-8",
            )
            uploaded += 1
        except (OSError, RuntimeError, ValueError, KeyError,
                json.JSONDecodeError, subprocess.CalledProcessError) as exc:
            (folder / "sync_pending.txt").write_text(
                type(exc).__name__ + ": " + ("GitHub unavailable or one-PR lock" if
                isinstance(exc, (RuntimeError, subprocess.CalledProcessError))
                else "Diagnostic export rejected") + "\n", encoding="utf-8",
            )
            blocked += 1
            # Stop if repository/credentials are unavailable; avoid repeated API calls.
            if isinstance(exc, (RuntimeError, subprocess.CalledProcessError)):
                break
    return uploaded, blocked
