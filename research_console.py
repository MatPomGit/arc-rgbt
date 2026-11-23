"""Local research console: datasets, environments, experiments, and audit logs.

Standard library only, so it can bootstrap an isolated virtual environment.
Dataset archives and complete logs never enter the source repository.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
import uuid
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = Path(os.getenv("LOCALAPPDATA") or Path.home() / ".local" / "share") / "arc-rgbt"
SETTINGS = STATE / "settings.json"
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PIPELINE = ROOT / "publications/P01/analyses/run_local_pipeline.py"
OFFICIAL_FLIR = "https://oem.flir.com/solutions/automotive/adas-dataset-form/"
# Future algorithms register here; experiment lifecycle and logs remain shared.
EXPERIMENTS = {
    "p01_frcnn_lwir": {
        "description": "P01: scratch Faster R-CNN / LWIR, validation only",
        "script": PIPELINE,
        "dataset": "flir_adas_v2",
    },
}
DEFAULTS = {
    "dataset_dirs": {"flir_adas_v2": str(Path.home() / "FLIR_ADAS_v2")},
    "runs_dir": str(Path.home() / "ArcRGBT_runs"),
    "download_manifest": "",
}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_settings() -> dict:
    if not SETTINGS.exists():
        return json.loads(json.dumps(DEFAULTS))
    saved = json.loads(SETTINGS.read_text(encoding="utf-8"))
    if not isinstance(saved, dict) or not isinstance(saved.get("dataset_dirs"), dict):
        raise ValueError("Invalid local settings; rename settings.json to recover")
    settings = json.loads(json.dumps(DEFAULTS))
    settings.update(saved)
    return settings


def save_settings(settings: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    temp = SETTINGS.with_suffix(".tmp")
    temp.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    temp.replace(SETTINGS)


def directory(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if path == ROOT or path.is_relative_to(ROOT):
        raise ValueError("Data and logs must stay outside the Git repository")
    return path


class RunLog:
    """Every action has an independent, diagnosable and persistent audit trail."""

    def __init__(self, runs_dir: Path, action: str) -> None:
        self.id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        self.path = runs_dir / "logs" / self.id
        self.path.mkdir(parents=True, exist_ok=False)
        self.events = self.path / "events.jsonl"
        self.console = self.path / "console.log"
        self.status = self.path / "status.json"
        self.action = action
        self.stage = "start"
        self.emit("RUNNING", "start")

    def emit(self, status: str, stage: str, **details: object) -> None:
        self.stage = stage
        row = {"time_utc": timestamp(), "run_id": self.id,
               "action": self.action, "stage": stage, "status": status, **details}
        with self.events.open("a", encoding="utf-8") as out:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.status.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
        message = details.get("message")
        print(f"[{status}] {stage}" + (f": {message}" if message else ""))

    def execute(self, stage: str, args: list[str]) -> None:
        self.emit("RUNNING", stage)
        with self.console.open("a", encoding="utf-8") as output:
            output.write(f"\n[{timestamp()}] START stage={stage}\n")
            output.flush()
            process = subprocess.Popen(
                args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
            )
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="", flush=True)
                output.write(line)
                output.flush()
            rc = process.wait()
            output.write(f"\n[{timestamp()}] END stage={stage} returncode={rc}\n")
        if rc != 0:
            detail = ""
            if stage == "training_and_validation":
                substage = self.path / "artifacts" / "pipeline_stage.json"
                if substage.is_file():
                    detail = json.loads(substage.read_text(encoding="utf-8")).get(
                        "stage", "unknown"
                    )
            self.emit("FAIL", stage, returncode=rc, substage=detail,
                      message=f"Exit code {rc}; substage={detail}; read {self.console}")
            raise RuntimeError(f"{stage}/{detail} failed (exit code {rc})")
        self.emit("PASS", stage)


def run_action(action: str, callback) -> None:
    try:
        settings = read_settings()
        log = RunLog(directory(settings["runs_dir"]), action)
    except (OSError, ValueError) as exc:
        print(f"[BLOCKED] Cannot initialise logs: {exc}")
        return
    try:
        outcome = callback(settings, log)
        if outcome is False:
            log.emit("BLOCKED", "cancelled")
        else:
            log.emit("PASS", "complete")
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        log.emit("FAIL", log.stage, error_type=type(exc).__name__, message=str(exc))
        with log.console.open("a", encoding="utf-8") as out:
            traceback.print_exc(file=out)
    finally:
        print(f"Diagnostics: {log.path}")


def install(settings: dict, log: RunLog) -> None:
    if sys.version_info[:2] != (3, 12):
        raise ValueError("Use Python 3.12 to launch the BAT file")
    if not PYTHON.exists():
        log.execute("create_venv", [sys.executable, "-m", "venv", str(ROOT / ".venv")])
    log.execute("install_dependencies",
                [str(PYTHON), "-m", "pip", "install", "-e", ".[torch]"])
    log.execute("verify_imports", [
        str(PYTHON), "-c",
        "import torch, torchvision, arc_rgbt; "
        "print('torch', torch.__version__, 'CUDA', torch.cuda.is_available())",
    ])


def configure_data(settings: dict, log: RunLog) -> None:
    current = settings["dataset_dirs"]["flir_adas_v2"]
    print("Official FLIR data access:", OFFICIAL_FLIR)
    print("Registration/terms may be required. No bypass or guessed URLs.")
    answer = input(f"Local archive folder [{current}]: ").strip()
    if answer:
        settings["dataset_dirs"]["flir_adas_v2"] = str(directory(answer))
    manifest = input(
        "Verified 12-part HTTPS/SHA-256 JSON manifest (Enter to keep current): "
    ).strip()
    if manifest:
        path = Path(manifest).expanduser().resolve()
        if not path.is_file():
            raise ValueError("Download manifest does not exist")
        settings["download_manifest"] = str(path)
    save_settings(settings)
    log.emit("PASS", "save_data_settings")
    print("Saved dataset directory:", settings["dataset_dirs"]["flir_adas_v2"])
    choice = input("Fetch missing archive parts with verified manifest? [y/N]: ").lower()
    if choice != "y":
        return
    if not PYTHON.is_file():
        raise ValueError("Install dependencies first (option 1)")
    if not settings["download_manifest"]:
        raise ValueError("Verified download manifest not configured. Use official FLIR portal.")
    if input("I accepted the source terms and am allowed to download [y/N]: "
             ).strip().lower() != "y":
        log.emit("BLOCKED", "source_terms")
        return False
    log.execute("download_verify", [
        str(PYTHON), str(PIPELINE), "--acquire-only",
        "--parts-dir", settings["dataset_dirs"]["flir_adas_v2"],
        "--download-manifest", settings["download_manifest"],
    ])


def diagnostics(settings: dict, log: RunLog) -> None:
    data = directory(settings["dataset_dirs"]["flir_adas_v2"])
    existing = [f"FLIR_ADAS_v2.zip.{n:02}" for n in range(12)
                if (data / f"FLIR_ADAS_v2.zip.{n:02}").is_file()]
    log.emit("PASS", "check_archive_names", found=len(existing), required=12)
    if not PYTHON.is_file():
        log.emit("BLOCKED", "check_environment", message="Install .venv first")
        return False
    log.execute("check_torch_cuda", [
        str(PYTHON), "-c",
        "import torch,torchvision; print('torch:',torch.__version__);"
        "print('torchvision:',torchvision.__version__);"
        "print('CUDA:',torch.cuda.is_available());"
        "print('GPU:',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')",
    ])


def train(settings: dict, log: RunLog) -> None:
    if not PYTHON.is_file():
        raise ValueError("Install .venv first (option 1)")
    print("Algorithms:")
    names = list(EXPERIMENTS)
    for index, name in enumerate(names, 1):
        print(f"  {index}. {EXPERIMENTS[name]['description']}")
    selected = input("Algorithm [1]: ").strip() or "1"
    if not selected.isdigit() or not 1 <= int(selected) <= len(names):
        raise ValueError("Invalid algorithm selection")
    profile_id = names[int(selected) - 1]
    profile = EXPERIMENTS[profile_id]
    data = directory(settings["dataset_dirs"][profile["dataset"]])
    device = (input("Device [cuda/cpu] (default cuda): ").strip() or "cuda").lower()
    if device not in ("cuda", "cpu"):
        raise ValueError("Device must be cuda or cpu")
    if input("I have checked FLIR access terms and permit this local research use [y/N]: "
             ).strip().lower() != "y":
        log.emit("BLOCKED", "licence_acknowledgement")
        return False
    if input("Start training and validation? [y/N]: ").strip().lower() != "y":
        log.emit("BLOCKED", "user_cancelled")
        return False
    work = log.path / "artifacts"
    args = [
        str(PYTHON), str(profile["script"]),
        "--parts-dir", str(data), "--work-dir", str(work),
        "--rights-acknowledged", "--device", device,
    ]
    if settings.get("download_manifest"):
        # Missing parts can only be obtained with pinned, approved inputs.
        args.extend(["--download-manifest", settings["download_manifest"]])
    log.emit("RUNNING", "experiment", experiment=profile_id, device=device)
    log.execute("training_and_validation", args)
    summary = work / "summary.json"
    if not summary.is_file():
        raise ValueError("Training ended without summary.json")
    (log.path / "result.json").write_text(json.dumps({
        "experiment": profile_id, "summary_sha256": file_hash(summary),
        "status": "VALIDATION_ONLY", "summary_file": str(summary),
    }, indent=2) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def recent_runs(settings: dict) -> list[Path]:
    root = directory(settings["runs_dir"]) / "logs"
    return sorted((p for p in root.iterdir() if p.is_dir()), reverse=True) if root.exists() else []


def show_logs() -> None:
    settings = read_settings()
    rows = recent_runs(settings)[:15]
    if not rows:
        print("No runs recorded yet")
        return
    for index, folder in enumerate(rows, 1):
        status = folder / "status.json"
        event = json.loads(status.read_text(encoding="utf-8")) if status.is_file() else {}
        print(f"{index:2d}. {folder.name} {event.get('action','?')} "
              f"{event.get('status','?')} at {event.get('stage','?')}")
    selected = input("Open run folder [1, Enter=back]: ").strip()
    if not selected:
        return
    if not selected.isdigit() or not 1 <= int(selected) <= len(rows):
        print("Invalid selection")
        return
    path = rows[int(selected) - 1]
    print("Log folder:", path)
    if os.name == "nt":
        os.startfile(str(path))
    else:
        print("Read:", path / "console.log", "and", path / "events.jsonl")


def publish_run(settings: dict, log: RunLog) -> None:
    if not PYTHON.is_file():
        raise ValueError("Install .venv first")
    candidates = [p / "artifacts" / "summary.json" for p in recent_runs(settings)
                  if (p / "artifacts" / "summary.json").is_file()]
    if not candidates:
        raise ValueError("No completed local validation summary found")
    for index, path in enumerate(candidates[:15], 1):
        print(f"{index}. {path.parent.parent.name}")
    selected = input("Which result to publish [1]: ").strip() or "1"
    if not selected.isdigit() or not 1 <= int(selected) <= min(15, len(candidates)):
        raise ValueError("Invalid result selection")
    summary = candidates[int(selected) - 1]
    if input("Publish sanitised summary to GitHub PR (not weights/images)? [y/N]: "
             ).strip().lower() != "y":
        log.emit("BLOCKED", "user_cancelled")
        return False
    log.execute("publish_results", [
        str(PYTHON), str(PIPELINE), "--publish-summary", str(summary),
    ])


def main() -> int:
    while True:
        try:
            settings = read_settings()
            print("\nARC-RGBT | Research console | Windows / Fedora")
            print(" 1. Install/update .venv and PyTorch")
            print(" 2. Configure FLIR path / approved download")
            print(" 3. Diagnose environment and dataset")
            print(" 4. Start training and validation")
            print(" 5. Publish an existing summary to GitHub PR")
            print(" 6. Show run history, logs and error stages")
            print(" 7. Open official FLIR access page")
            print(" 0. Exit")
            print("Data:", settings["dataset_dirs"]["flir_adas_v2"])
            print("Run logs:", str(directory(settings["runs_dir"]) / "logs"))
            choice = input("Choice: ").strip()
            if choice == "0":
                return 0
            if choice == "1":
                run_action("install", install)
            elif choice == "2":
                run_action("configure_data", configure_data)
            elif choice == "3":
                run_action("diagnostics", diagnostics)
            elif choice == "4":
                run_action("experiment", train)
            elif choice == "5":
                run_action("publication", publish_run)
            elif choice == "6":
                show_logs()
            elif choice == "7":
                webbrowser.open(OFFICIAL_FLIR)
            else:
                print("Unknown menu choice")
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            print(f"[BLOCKED] {type(exc).__name__}: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled")
            return 130


if __name__ == "__main__":
    raise SystemExit(main())
