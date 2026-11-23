"""Offline FLIR P01 train/validation pipeline for Windows and Fedora.

Uses the existing local multipart reader, group manifest, detector and COCO
evaluation. No held-out access; nothing is published without --publish.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ANALYSES = Path(__file__).resolve().parent
REPO = "MatPomGit/arc-rgbt"
PARTS = tuple(f"FLIR_ADAS_v2.zip.{i:02d}" for i in range(12))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def command(args: list[str], *, capture: bool = False) -> str:
    """Show training logs in real time; capture only GitHub API responses."""
    completed = subprocess.run(
        args, cwd=ROOT, check=True, text=True, capture_output=capture,
    )
    return completed.stdout or ""


def acquire(parts_dir: Path, manifest_path: Path | None) -> None:
    """Optional download only from explicitly supplied HTTPS URLs and pinned SHA."""
    missing = [name for name in PARTS if not (parts_dir / name).is_file()]
    if not missing and manifest_path is None:
        return
    if manifest_path is None:
        raise ValueError(
            "FLIR archive absent. Supply official 12-part archive locally, or "
            "--download-manifest with independently verified HTTPS URL/SHA-256 per part."
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if set(manifest) != set(PARTS):
        raise ValueError("Download manifest must name exactly 12 canonical ZIP parts")
    for name in PARTS:
        record = manifest[name]
        url, expected = record["url"], record["sha256"]
        parsed = urllib.parse.urlparse(url)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username
                or parsed.password or len(expected) != 64
                or any(c not in "0123456789abcdef" for c in expected)):
            raise ValueError(f"Unsafe or unpinned archive part: {name}")
        target = parts_dir / name
        if target.exists():
            if sha256(target) != expected:
                raise ValueError(f"Existing archive part SHA mismatch: {name}")
            continue
        tmp = target.with_suffix(target.suffix + ".partial")
        if tmp.exists():
            raise ValueError(f"Partial download exists; inspect before retry: {name}")
        parts_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        try:
            with urllib.request.urlopen(url, timeout=60) as response, tmp.open("xb") as output:
                final = urllib.parse.urlparse(response.url)
                if final.scheme != "https" or final.hostname != parsed.hostname:
                    raise ValueError("Unsafe archive redirect")
                received = 0
                while chunk := response.read(1024 * 1024):
                    received += len(chunk)
                    if received > 8 * 1024**3:
                        raise ValueError("Archive part exceeds 8 GiB")
                    digest.update(chunk)
                    output.write(chunk)
            if digest.hexdigest() != expected:
                raise ValueError(f"Downloaded archive SHA mismatch: {name}")
            tmp.replace(target)
        finally:
            tmp.unlink(missing_ok=True)
    if any(sha256(parts_dir / name) != manifest[name]["sha256"] for name in PARTS):
        raise ValueError("Archive fingerprint verification failed")


def publish(summary: Path) -> None:
    """Open/update one results PR, never push raw assets or directly to main."""
    branch = "p01-validation-results"
    raw = summary.read_bytes()
    if len(raw) > 128 * 1024:
        raise ValueError("Summary exceeds the 128 KiB publication limit")
    record = json.loads(raw)
    if (not isinstance(record, dict) or record.get("schema_version") != 1
            or record.get("heldout_opened") is not False
            or record.get("test_tuned") is not False
            or record.get("physical_sensor_limit_claim") is not False
            or record.get("research_tier") != "A_SOURCE_GT_RELATIVE_DESCRIPTIVE_CANDIDATE"):
        raise ValueError("Not a validated P01 source-relative summary")
    # Never publish arbitrary user-edited keys, paths or raw predictions.
    allowed = {
        "schema_version", "generated_utc", "research_tier", "status",
        "heldout_opened", "test_tuned", "physical_sensor_limit_claim",
        "rights_verified_independently", "native_optics_verified",
        "independent_acquisitions_verified", "checkpoint_sha256",
        "train_annotation_sha256", "validation_annotation_sha256",
        "split_manifest_sha256", "validation_predictions_sha256",
        "source_part_sha256", "training", "validation", "limitations",
    }
    if set(record) != allowed:
        raise ValueError("Unexpected summary fields; refusing public upload")
    run_id = hashlib.sha256(raw).hexdigest()[:20]
    relative = f"publications/P01/results/runs/{run_id}.json"
    payload = base64.b64encode(raw).decode("ascii")
    def gh(*args: str) -> str:
        return command(["gh", "api", *args], capture=True).strip()

    # Preserve the repository-wide limit of one active pull request.
    opened = json.loads(gh(f"repos/{REPO}/pulls?state=open&per_page=100"))
    if any(pr["head"]["ref"] != branch for pr in opened):
        raise ValueError("Another PR is active; finish it before publishing results")
    # A results branch is only created after code changes have been merged.
    try:
        gh(f"repos/{REPO}/git/ref/heads/{branch}")
    except subprocess.CalledProcessError:
        sha = json.loads(gh(f"repos/{REPO}/git/ref/heads/main"))["object"]["sha"]
        gh("-X", "POST", f"repos/{REPO}/git/refs",
           "-f", f"ref=refs/heads/{branch}", "-f", f"sha={sha}")
    existing = None
    try:
        existing = json.loads(gh(f"repos/{REPO}/contents/{relative}?ref={branch}"))
    except subprocess.CalledProcessError:
        pass
    if existing is not None:
        encoded = existing.get("content", "").replace("\\n", "")
        if base64.b64decode(encoded) != raw:
            raise ValueError("Existing run identifier conflicts with different bytes")
    else:
        # Windows has a limited command-line length: use a temporary JSON body.
        request = {
            "message": f"P01: record validation-only run {run_id}",
            "branch": branch, "content": payload,
        }
        with tempfile.TemporaryDirectory(prefix="p01-gh-") as temp:
            body = Path(temp) / "request.json"
            body.write_text(json.dumps(request), encoding="utf-8")
            gh("-X", "PUT", f"repos/{REPO}/contents/{relative}",
               "--input", str(body))
    prs = json.loads(gh(f"repos/{REPO}/pulls?state=open&head=MatPomGit:{branch}"))
    if not prs:
        command([
            "gh", "pr", "create", "--repo", REPO, "--base", "main",
            "--head", branch, "--title", "P01: recorded validation-only runs",
            "--body", "Machine-generated sanitized source-GT-relative validation evidence. "
            "Not held-out results, protocol freeze, Tier B evidence or scientific GO.",
        ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parts-dir", type=Path)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--download-manifest", type=Path)
    parser.add_argument("--rights-acknowledged", action="store_true")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--acquire-only", action="store_true",
                        help="Acquire and hash-check source parts; do not train")
    parser.add_argument("--publish-summary", type=Path,
                        help="Publish a completed local summary without retraining")
    args = parser.parse_args(argv)
    if args.acquire_only:
        if not args.parts_dir or not args.download_manifest or args.work_dir or args.publish:
            parser.error("--acquire-only requires --parts-dir and --download-manifest only")
        parts = args.parts_dir.expanduser().resolve()
        if parts.is_relative_to(ROOT):
            parser.error("Dataset directory must be outside the repository")
        try:
            acquire(parts, args.download_manifest)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            parser.exit(1, f"P01 download BLOCKED/FAIL: {type(exc).__name__}: {exc}\n")
        print(json.dumps({"status": "SOURCE_PARTS_VERIFIED", "count": len(PARTS)}))
        return 0
    if args.publish_summary is not None:
        if args.publish or args.download_manifest or args.rights_acknowledged:
            parser.error("--publish-summary must be used by itself")
        summary = args.publish_summary.expanduser().resolve()
        if not summary.is_file() or summary.is_relative_to(ROOT):
            parser.error("Summary must exist outside the repository")
        try:
            publish(summary)
        except (OSError, ValueError, KeyError, subprocess.CalledProcessError,
                json.JSONDecodeError) as exc:
            parser.exit(1, f"P01 publish BLOCKED/FAIL: {type(exc).__name__}: {exc}\n")
        print(json.dumps({"published": True, "summary_sha256": sha256(summary)}))
        return 0
    if args.parts_dir is None or args.work_dir is None:
        parser.error("--parts-dir and --work-dir are required for training")
    if not args.rights_acknowledged:
        parser.error("Review source licence and specify --rights-acknowledged")
    if args.epochs < 1 or args.epochs > 100 or args.batch_size < 1 or args.batch_size > 8:
        parser.error("Training budget out of range")
    parts_dir = args.parts_dir.expanduser().resolve()
    work = args.work_dir.expanduser().resolve()
    if work.is_relative_to(ROOT) or parts_dir.is_relative_to(ROOT):
        parser.error("Source archive and work directory must be outside the repository")
    if work.exists():
        parser.error("Work directory already exists; use a new run directory")
    try:
        work.mkdir(parents=True)
        stage_file = work / "pipeline_stage.json"

        def stage(name: str) -> None:
            stage_file.write_text(
                json.dumps({"stage": name, "time_utc": datetime.now(timezone.utc).isoformat()})
                + "\n", encoding="utf-8"
            )
            print(f"[P01 STAGE] {name}", flush=True)

        stage("download_and_verify_archive")
        acquire(parts_dir, args.download_manifest)
        evidence = work / "preflight"
        output = work / "training"
        stage("extract_source_annotations_and_split_manifest")
        command([
            sys.executable, str(ANALYSES / "read_flir_multipart_coco.py"),
            "--parts-dir", str(parts_dir), "--output-dir", str(evidence),
        ])
        stage("train_and_validate_model")
        command([
            sys.executable, str(ANALYSES / "train_torchvision_baseline.py"),
            "--parts-dir", str(parts_dir), "--preflight-dir", str(evidence),
            "--output-dir", str(output), "--rights-acknowledged",
            "--epochs", str(args.epochs), "--batch-size", str(args.batch_size),
            "--device", args.device,
        ])
        stage("evaluate_source_reference_metrics")
        command([
            sys.executable, str(ANALYSES / "run_coco_reference.py"),
            "--validation-annotations", str(evidence / "val_coco.json"),
            "--validation-predictions", str(output / "validation_predictions" / "predictions.json"),
            "--mode", "validation", "--output", str(work / "validation_metrics.json"),
        ])
        stage("assemble_reproducible_results")
        provenance = json.loads((output / "training_provenance.json").read_text())
        metrics = json.loads((work / "validation_metrics.json").read_text())
        source = json.loads((evidence / "source_manifest.json").read_text())
        summary = {
            "schema_version": 1,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "research_tier": "A_SOURCE_GT_RELATIVE_DESCRIPTIVE_CANDIDATE",
            "status": provenance["status"],
            "heldout_opened": False,
            "test_tuned": False,
            "physical_sensor_limit_claim": False,
            "rights_verified_independently": False,
            "native_optics_verified": False,
            "independent_acquisitions_verified": False,
            "checkpoint_sha256": provenance["checkpoint_sha256"],
            "train_annotation_sha256": provenance["input_annotation_sha256"]["train"],
            "validation_annotation_sha256": provenance["input_annotation_sha256"]["validation"],
            "split_manifest_sha256": provenance["input_preflight_manifest_sha256"],
            "validation_predictions_sha256": provenance["validation_predictions_sha256"],
            "source_part_sha256": {p["filename"]: p["sha256"] for p in source["parts"]},
            "training": {
                "model": provenance["model"], "seed": provenance["seed"],
                "epochs": provenance["epochs"], "batch_size": provenance["batch_size"],
                "device": provenance["device"], "torch": provenance["torch"],
                "torchvision": provenance["torchvision"],
                "loss_by_epoch": provenance["training_loss_by_epoch"],
            },
            "validation": {
                "status": metrics["status"],
                "threshold_candidate": metrics["validation_threshold"],
            },
            "limitations": [
                "Reference labels may be incomplete; FP/frame is source-label-relative.",
                "Video ID is not proof of independently acquired scenes.",
                "No test results, physical optical limits or scientific GO.",
            ],
        }
        summary_path = work / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8")
        if args.publish:
            stage("publish_results")
            publish(summary_path)
        stage("complete")
        print(json.dumps({"status": summary["status"], "summary": str(summary_path),
                          "published": args.publish}))
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"P01 pipeline BLOCKED/FAIL: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
