"""Push sanitized run telemetry directly to the dedicated GitHub branch.

Small reports sync after every local action. Detailed logs are opt-in only.
Do not commit to main or upload raw, unreviewed console output.
"""
from __future__ import annotations

import base64
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
BRANCH = "research-telemetry"
STATES = {"PASS", "FAIL", "BLOCKED", "RUNNING"}
ACTIONS = {"install", "configure_data", "diagnostics", "experiment", "publication",
           "extended_upload"}
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



def _missing(exc: subprocess.CalledProcessError) -> bool:
    """Do not confuse HTTP 404 with authorization or network failures."""
    return "HTTP 404" in (exc.stderr or "")


def _ensure_branch() -> None:
    try:
        github(f"repos/{REPO}/git/ref/heads/{BRANCH}")
    except subprocess.CalledProcessError as exc:
        if not _missing(exc):
            raise
        main = json.loads(github(f"repos/{REPO}/git/ref/heads/main"))["object"]["sha"]
        github("-X", "POST", f"repos/{REPO}/git/refs",
               "-f", f"ref=refs/heads/{BRANCH}", "-f", f"sha={main}")


def _upload(relative: str, raw: bytes, message: str) -> str:
    """Idempotent single-file GitHub commit on telemetry branch, no PR."""
    if not shutil.which("gh"):
        raise RuntimeError("GitHub CLI is unavailable or not authenticated")
    _ensure_branch()
    try:
        existing = json.loads(github(f"repos/{REPO}/contents/{relative}?ref={BRANCH}"))
    except subprocess.CalledProcessError as exc:
        if not _missing(exc):
            raise
        existing = None
    if existing is not None:
        previous = base64.b64decode(existing.get("content", "").replace("\n", ""))
        if previous != raw:
            raise ValueError("Telemetry run ID already exists with different bytes")
        return "ALREADY_UPLOADED"
    request = {
        "message": message, "branch": BRANCH,
        "content": base64.b64encode(raw).decode("ascii"),
    }
    with tempfile.TemporaryDirectory(prefix="arc-rgbt-sync-") as folder:
        body = Path(folder) / "request.json"
        body.write_text(json.dumps(request), encoding="utf-8")
        github("-X", "PUT", f"repos/{REPO}/contents/{relative}",
               "--input", str(body))
    return "UPLOADED"


def sync(folder: Path) -> str:
    """Push a small report after each completed/failed operation."""
    report = snapshot(folder)
    raw = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    if len(raw) > 96 * 1024:
        raise ValueError("Diagnostic report exceeds 96 KiB")
    path = f"publications/P01/results/diagnostics/{report['run_id']}.json"
    return _upload(path, raw, f"chore(P01): diagnostic {report['run_id']}")


# Sanitization is deliberately conservative. The user previews every extended
# export before uploading; these are still not suitable for arbitrary secrets.
SENSITIVE = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9_]{12,}|github_pat_[A-Za-z0-9_]{12,}"
    r"|sk-[A-Za-z0-9_-]{16,}|(?i:bearer)\s+[A-Za-z0-9._-]+)"
)
KEY_VALUE = re.compile(
    r"(?i)\b(?:authorization|access[_-]?token|password|api[_-]?key|secret)"
    r"\s*[=:]\s*[^\s,;]+"
)
URL = re.compile(r"https?://[^\s\x22\x27]+")
WINDOWS_PATH = re.compile(r"(?i)(?:[A-Z]:[\\/]|\\\\)[^\s\x22\x27]+")
UNIX_PATH = re.compile(r"/(?:home|Users|mnt|tmp|var|opt)/[^\s\x22\x27]+")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

def redact_line(line: str) -> str:
    line = ANSI.sub("", line)
    for pattern, replacement in (
        (SENSITIVE, "[SECRET]"), (KEY_VALUE, "[SECRET_FIELD]"),
        (URL, "[URL]"), (WINDOWS_PATH, "[LOCAL_PATH]"),
        (UNIX_PATH, "[LOCAL_PATH]"), (EMAIL, "[EMAIL]"),
    ):
        line = pattern.sub(replacement, line)
    return line[:2048]


def extended_report(folder: Path) -> dict:
    """Create a bounded redacted excerpt only for explicit menu upload."""
    basic = snapshot(folder)
    source = folder / "console.log"
    raw_size = source.stat().st_size if source.exists() else 0
    tail = b""
    if source.is_file():
        with source.open("rb") as inp:
            inp.seek(max(0, raw_size - 256 * 1024))
            tail = inp.read(256 * 1024)
    lines = tail.decode("utf-8", errors="replace").splitlines()
    clean = [redact_line(line) for line in lines][-1500:]
    report = {
        "schema_version": 1, "kind": "redacted_extended_diagnostic",
        "run_id": basic["run_id"], "basic": basic,
        "console_source_bytes": raw_size,
        "excerpt_truncated": raw_size > 256 * 1024,
        "redacted_console_excerpt": clean,
        "contains_raw_training_data": False,
    }
    raw = json.dumps(report, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if len(raw) > 512 * 1024:
        raise ValueError("Extended diagnostic exceeds 512 KiB")
    return report


def sync_extended(folder: Path) -> str:
    """Manual, pre-confirmed upload. Never invoked in automatic sync."""
    report = extended_report(folder)
    raw = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    if len(raw) > 512 * 1024:
        raise ValueError("Extended diagnostic exceeds 512 KiB")
    path = f"publications/P01/results/diagnostics/extended/{report['run_id']}.json"
    return _upload(path, raw, f"chore(P01): extended diagnostic {report['run_id']}")


def sync_pending(logs: Path) -> tuple[int, int]:
    """Retry local reports next time GitHub is available, without a new PR."""
    uploaded, blocked = 0, 0
    for folder in sorted(logs.iterdir()) if logs.exists() else []:
        if not folder.is_dir() or (folder / "sync_success.json").exists():
            continue
        try:
            result = sync(folder)
            (folder / "sync_success.json").write_text(
                json.dumps({"status": result, "branch": BRANCH}) + "\n",
                encoding="utf-8",
            )
            (folder / "sync_pending.txt").unlink(missing_ok=True)
            uploaded += 1
        except (OSError, RuntimeError, ValueError, KeyError,
                json.JSONDecodeError, subprocess.CalledProcessError) as exc:
            (folder / "sync_pending.txt").write_text(
                f"{type(exc).__name__}: push unavailable; retry after resolving GitHub access"
                "\n", encoding="utf-8",
            )
            blocked += 1
            if isinstance(exc, (RuntimeError, subprocess.CalledProcessError)):
                break
    return uploaded, blocked
