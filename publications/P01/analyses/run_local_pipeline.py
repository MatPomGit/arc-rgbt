"""Offline FLIR P01 train/validation pipeline for Windows and Fedora.

Uses the existing local multipart reader, group manifest, detector and COCO
evaluation. No held-out access; nothing is published without --publish.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import UTC, datetime
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
        print(f"[P01 DATA] verify {name}", flush=True)
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
        print(f"[P01 DATA] downloading {name} from approved source", flush=True)
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
            print(f"[P01 DATA] SHA-256 PASS {name}", flush=True)
        finally:
            tmp.unlink(missing_ok=True)
    if any(sha256(parts_dir / name) != manifest[name]["sha256"] for name in PARTS):
        raise ValueError("Archive fingerprint verification failed")



def validate_public_summary(record: object) -> None:
    """Fail closed on every public summary field, including nested values."""
    def fields(value: object, required: set[str], optional: set[str] | None = None) -> dict:
        if not isinstance(value, dict):
            raise ValueError("Expected a structured summary object")
        keys = set(value)
        if not required <= keys or keys - required - (optional or set()):
            raise ValueError("Unrecognized or missing public summary field")
        return value

    def integer(value: object, minimum: int, maximum: int) -> bool:
        return type(value) is int and minimum <= value <= maximum

    def number(value: object, minimum: float, maximum: float) -> bool:
        return (type(value) in (int, float) and math.isfinite(value)
                and minimum <= value <= maximum)

    def digest(value: object) -> bool:
        return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None

    top = {
        "schema_version", "generated_utc", "research_tier", "status",
        "heldout_opened", "test_tuned", "physical_sensor_limit_claim",
        "rights_verified_independently", "native_optics_verified",
        "independent_acquisitions_verified", "checkpoint_sha256",
        "train_annotation_sha256", "validation_annotation_sha256",
        "split_manifest_sha256", "validation_predictions_sha256",
        "source_part_sha256", "training", "validation", "limitations",
    }
    record = fields(record, top)
    if (record["schema_version"] != 1
            or record["research_tier"] != "A_SOURCE_GT_RELATIVE_DESCRIPTIVE_CANDIDATE"
            or record["status"] != "VALIDATION_CANDIDATE_ONLY_UNFROZEN"
            or any(record[key] is not False for key in (
                "heldout_opened", "test_tuned", "physical_sensor_limit_claim",
                "rights_verified_independently", "native_optics_verified",
                "independent_acquisitions_verified",
            ))):
        raise ValueError("No eligible validation-only evidence for public upload")
    date = record["generated_utc"]
    if not isinstance(date, str) or len(date) > 40:
        raise ValueError("Invalid evidence timestamp")
    try:
        instant = datetime.fromisoformat(date)
    except ValueError as exc:
        raise ValueError("Invalid evidence timestamp") from exc
    if instant.utcoffset() is None or instant.utcoffset().total_seconds() != 0:
        raise ValueError("Evidence timestamp must be in UTC")
    for key in ("checkpoint_sha256", "train_annotation_sha256",
                "validation_annotation_sha256", "split_manifest_sha256",
                "validation_predictions_sha256"):
        if not digest(record[key]):
            raise ValueError(f"Invalid {key}")
    source = fields(record["source_part_sha256"], set(PARTS))
    if any(not digest(sha) for sha in source.values()):
        raise ValueError("Invalid source-part digest")
    training = fields(record["training"], {
        "model", "seed", "epochs", "batch_size", "device", "torch",
        "torchvision", "loss_by_epoch",
    })
    if (training["model"] != "scratch_torchvision_frcnn_mobilenetv3_single_car"
            or training["device"] not in ("cpu", "cuda")
            or not integer(training["seed"], 0, 2**32 - 1)
            or not integer(training["epochs"], 1, 100)
            or not integer(training["batch_size"], 1, 8)):
        raise ValueError("Invalid training configuration")
    for key in ("torch", "torchvision"):
        version = training[key]
        if not isinstance(version, str) or not re.fullmatch(
            r"[0-9][0-9A-Za-z.+_-]{0,39}", version
        ):
            raise ValueError("Unsafe training dependency version")
    losses = training["loss_by_epoch"]
    if not isinstance(losses, list) or len(losses) != training["epochs"]:
        raise ValueError("Incomplete or invalid training loss series")
    for epoch, item in enumerate(losses, 1):
        item = fields(item, {"epoch", "train_mean_loss"})
        if item["epoch"] != epoch or not number(item["train_mean_loss"], 0, 1e12):
            raise ValueError("Invalid training loss")
    validation = fields(record["validation"], {"status", "threshold_candidate"})
    if validation["status"] != "VALIDATION_CANDIDATE_ONLY":
        raise ValueError("Blocked validation cannot be published as a result")
    threshold = fields(validation["threshold_candidate"], {
        "status", "threshold", "empirical_admission", "split_role",
        "annotation_reference", "group_basis", "threshold_selection",
        "score_inclusion_rule", "frames", "groups", "limitations",
        "negative_frames", "negative_groups", "validation_fp_per_frame",
        "validation_tp", "validation_fp_bootstrap_ci_95",
        "validation_fp_upper_ci_exceeds_ceiling", "bootstrap_replicates",
        "uncertainty_status",
    })
    expected = {
        "status": "CANDIDATE_ONLY",
        "empirical_admission": False,
        "split_role": "declared_validation_unverified",
        "annotation_reference": "source_reference_unverified",
        "group_basis": "source_video_proxy",
        "threshold_selection": "lowest_feasible_sorted_unique_score",
        "score_inclusion_rule": "score >= threshold; ties indivisible",
        "limitations": "Observed validation FP/frame is not a future upper bound",
        "uncertainty_status": "SUPPRESSED_UNVERIFIED_GROUP_INDEPENDENCE",
        "validation_fp_bootstrap_ci_95": None,
        "validation_fp_upper_ci_exceeds_ceiling": None,
        "bootstrap_replicates": 0,
    }
    if any(threshold[key] != value for key, value in expected.items()):
        raise ValueError("Invalid validation status or scientific gate")
    if (not number(threshold["threshold"], 0, 1)
            or not number(threshold["validation_fp_per_frame"], 0, 0.1)
            or not integer(threshold["validation_tp"], 1, 10**9)
            or not integer(threshold["frames"], 1, 10**9)
            or not integer(threshold["groups"], 1, 10**8)
            or not integer(threshold["negative_frames"], 0, 10**9)
            or not integer(threshold["negative_groups"], 0, 10**8)):
        raise ValueError("Invalid validation metrics")
    if record["limitations"] != [
        "Reference labels may be incomplete; FP/frame is source-label-relative.",
        "Video ID is not proof of independently acquired scenes.",
        "No test results, physical optical limits or scientific GO.",
    ]:
        raise ValueError("Unrecognized scientific limitations")



def publish(summary: Path) -> None:
    """Open/update one results PR, never push raw assets or directly to main."""
    branch = "p01-validation-results"
    raw = summary.read_bytes()
    if len(raw) > 128 * 1024:
        raise ValueError("Summary exceeds the 128 KiB publication limit")
    record = json.loads(raw)
    validate_public_summary(record)
    run_id = hashlib.sha256(raw).hexdigest()[:20]
    relative = f"publications/P01/results/runs/{run_id}.json"
    payload = base64.b64encode(raw).decode("ascii")
    def gh(*args: str) -> str:
        return command(["gh", "api", *args], capture=True).strip()

    # Only the shared controller may authorize a new portfolio PR. Reuse an
    # existing results PR; otherwise stop before creating or exposing a branch.
    prs = json.loads(gh(f"repos/{REPO}/pulls?state=open&head=MatPomGit:{branch}"))
    if not isinstance(prs, list) or not prs:
        raise ValueError(
            "Results PR not authorized by portfolio controller; "
            "ask controller to reserve a slot within the global four-PR cap"
        )
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
                json.dumps({"stage": name, "time_utc": datetime.now(UTC).isoformat()})
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
            "generated_utc": datetime.now(UTC).isoformat(),
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
        if summary["status"] == "BLOCKED_VALIDATION_NO_OPERATING_POINT":
            stage("blocked_validation_no_operating_point")
            print(json.dumps({"status": summary["status"], "summary": str(summary_path),
                              "published": False}))
            return 2
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
