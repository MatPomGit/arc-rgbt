"""P01 offline benchmark of supplied COCO labels and detector predictions.

Only validation selects the threshold. Source-video grouping is a proxy,
not a claim of independent camera acquisitions or physical sensor limits.
The script does not run model inference or download images/weights.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

from arc_rgbt.evaluation_contracts import detection_contract
from arc_rgbt.p01_metrics import choose_validation_threshold, native_footprint_recall

ANNOTATION_STATUS = "source_reference_unverified"
GROUP_BASIS = "source_video_proxy"
GRID_ORIGIN = "source_export"


def digest(path: Path) -> str:
    """Fingerprint original input bytes without changing them."""
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def source_group(image: dict) -> str:
    """Read a source video identifier; do not infer flight independence."""
    extra = image.get("extra_info", {})
    value = extra.get("video_id") if isinstance(extra, dict) else None
    if value is None:
        value = image.get("video_id")
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or unicodedata.normalize("NFKC", value) != value
        or any(
            char.isspace() or unicodedata.category(char) in ("Cc", "Cf")
            for char in value
        )
    ):
        raise ValueError("Each COCO image needs a canonical nonempty source video_id")
    return value


def load_coco(
    annotations_path: Path, predictions_path: Path, selected_class: str,
) -> tuple[list[dict], list[str], dict]:
    """Translate existing COCO boxes into the shared Bench contract."""
    annotations = json.loads(annotations_path.read_text(encoding="utf-8"))
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    if not isinstance(annotations, dict) or not isinstance(predictions, list):
        raise ValueError("Expected COCO annotation object and detection array")
    cats = annotations.get("categories")
    images = annotations.get("images")
    objects = annotations.get("annotations")
    if not all(isinstance(item, list) for item in (cats, images, objects)):
        raise ValueError("Missing COCO images/categories/annotations arrays")
    names = {cat["id"]: cat["name"] for cat in cats}
    chosen = {cid for cid, name in names.items() if name == selected_class}
    if len(chosen) != 1:
        raise ValueError("Selected class must appear exactly once in COCO categories")
    category_id = next(iter(chosen))
    frames = {}
    groups = {}
    for item in images:
        image_id = item["id"]
        if type(image_id) is not int or image_id in frames:
            raise ValueError("Duplicate or invalid COCO image id")
        frames[image_id] = {
            "id": str(image_id), "ground_truth": [], "predictions": [],
        }
        groups[image_id] = source_group(item)

    for item in objects:
        image_id = item["image_id"]
        if image_id not in frames:
            raise ValueError("Orphan COCO ground truth")
        if item["category_id"] == category_id:
            # Do not silently score unsupported crowd/ignore annotations.
            if item.get("iscrowd", 0) or item.get("ignore", 0):
                raise ValueError("Selected source crowd/ignore GT needs a frozen policy")
            frames[image_id]["ground_truth"].append({
                "label": selected_class, "bbox": item["bbox"],
            })

    for item in predictions:
        image_id = item["image_id"]
        if image_id not in frames:
            raise ValueError("Prediction for unknown image_id")
        if item["category_id"] == category_id:
            frames[image_id]["predictions"].append({
                "label": selected_class, "bbox": item["bbox"],
                "score": item["score"],
            })

    if not frames:
        raise ValueError("COCO split has no images")
    ids = sorted(frames)
    return (
        [frames[i] for i in ids],
        [groups[i] for i in ids],
        {
            "images": len(ids),
            "source_video_groups": len(set(groups.values())),
            "reference_positive_frames": sum(
                bool(frames[i]["ground_truth"]) for i in ids
            ),
            "reference_negative_frames": sum(
                not frames[i]["ground_truth"] for i in ids
            ),
            "reference_targets": sum(len(frames[i]["ground_truth"]) for i in ids),
        },
    )


def validation_candidate(
    validation_annotations: Path, validation_predictions: Path, selected_class: str,
) -> tuple[dict, list[str]]:
    """Compute source-GT-relative validation cutoff without any held-out input."""
    val, val_groups, val_counts = load_coco(
        validation_annotations, validation_predictions, selected_class,
    )
    cutoff = choose_validation_threshold(
        val, acquisition_ids=val_groups, split_role="validation",
        annotation_status=ANNOTATION_STATUS, group_basis=GROUP_BASIS,
    )
    result = {
        "schema_version": 1,
        "status": "BLOCKED_VALIDATION",
        "scientific_claim": "dataset_reference_descriptive_only",
        "source_annotation_completeness_verified": False,
        "native_sensor_geometry_verified": False,
        "independent_acquisitions_verified": False,
        "model_training_independence_verified": False,
        "physical_sensor_limits_supported": False,
        "selected_class": selected_class,
        "validation_counts": val_counts,
        "validation_threshold": cutoff,
        "input_sha256": {
            "validation_annotations": digest(validation_annotations),
            "validation_predictions": digest(validation_predictions),
        },
        "implementation_sha256": {
            "runner": digest(Path(__file__)),
            "p01_metrics": digest(Path(__import__(
                "arc_rgbt.p01_metrics", fromlist=["__file__"]
            ).__file__)),
        },
    }
    if cutoff["status"] == "CANDIDATE_ONLY":
        result["status"] = "VALIDATION_CANDIDATE_ONLY"
    return result, val_groups


def evaluate_reference(
    validation_annotations: Path, validation_predictions: Path,
    holdout_annotations: Path, holdout_predictions: Path,
    selected_class: str, *, freeze_record: Path | None = None,
) -> dict:
    """Hold-out evaluator. Its CLI requires a prior author-FROZEN record."""
    result, val_groups = validation_candidate(
        validation_annotations, validation_predictions, selected_class,
    )
    cutoff = result["validation_threshold"]
    if cutoff["status"] != "CANDIDATE_ONLY":
        result["status"] = "BLOCKED_VALIDATION"
        return result
    if freeze_record is None:
        raise ValueError("An author-FROZEN protocol record is required for held-out access")
    frozen = verify_freeze_record(
        freeze_record, validation_annotations, validation_predictions,
        holdout_annotations,
    )
    result["author_freeze_record_sha256"] = digest(freeze_record)
    result["author_freeze_record_self_declared"] = True
    result["author_protocol_sha256"] = frozen["protocol_sha256"]

    # Do not even open held-out files until after validation selection.
    result["input_sha256"].update({
        "holdout_annotations": digest(holdout_annotations),
        "holdout_predictions": digest(holdout_predictions),
    })
    test, test_groups, test_counts = load_coco(
        holdout_annotations, holdout_predictions, selected_class,
    )
    overlap = set(val_groups) & set(test_groups)
    if overlap:
        raise ValueError(
            f"Validation/holdout video group leakage: {len(overlap)} group(s)"
        )
    if not test_counts["reference_targets"]:
        raise ValueError("No selected GT targets in holdout")
    cutoff_score = cutoff["threshold"]
    footprint = native_footprint_recall(
        test, acquisition_ids=test_groups,
        annotation_status=ANNOTATION_STATUS, group_basis=GROUP_BASIS,
        grid_origin=GRID_ORIGIN, operating_score=cutoff_score,
    )
    ap = detection_contract(
        test, annotation_status=ANNOTATION_STATUS,
        iou_threshold=0.5, operating_score=cutoff_score,
    )
    result.update(
        status="DESCRIPTIVE_ONLY",
        holdout_counts=test_counts,
        holdout_footprint=footprint,
        holdout_ap=ap,
        operating_threshold_locked_from="validation",
        limitations=[
            "Only supplied source labels are reference ground truth",
            "Missing annotations may inflate apparent FP/frame",
            "video_id is a grouping proxy, not independently verified acquisition",
            "Source export boxes are not proof of original optical grid",
            "Checkpoint training-split independence is not verified here",
            "No physical camera limits, causal attribution, or scientific GO",
        ],
    )
    return result


def verify_freeze_record(
    path: Path, validation_annotations: Path, validation_predictions: Path,
    holdout_annotations: Path,
) -> dict:
    """Require an explicit prospective Tier A author decision before test access.

    Records are author-declared; this function checks byte bindings but does
    not cryptographically verify the approver's identity.
    """
    if not 0 < path.stat().st_size <= 16 * 1024:
        raise ValueError("Author freeze record must be a small JSON document")
    record = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(record, dict)
            or record.get("schema_version") != 1
            or record.get("author_decision") != "FROZEN"
            or record.get("claim_tier") != "A"):
        raise ValueError("An author-FROZEN Tier A protocol record is required")
    for name in ("protocol_sha256", "checkpoint_sha256", "split_manifest_sha256"):
        value = record.get(name)
        if (not isinstance(value, str) or len(value) != 64
                or any(char not in "0123456789abcdef" for char in value)):
            raise ValueError(f"Missing immutable {name} in author freeze record")
    for name, source in (
        ("validation_annotations_sha256", validation_annotations),
        ("validation_predictions_sha256", validation_predictions),
        ("holdout_annotations_sha256", holdout_annotations),
    ):
        expected = record.get(name)
        if expected != digest(source):
            raise ValueError(f"Frozen input does not match {name}")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-annotations", type=Path, required=True)
    parser.add_argument("--validation-predictions", type=Path, required=True)
    parser.add_argument("--mode", choices=("validation", "holdout"), default="validation")
    parser.add_argument("--holdout-annotations", type=Path)
    parser.add_argument("--holdout-predictions", type=Path)
    parser.add_argument("--freeze-record", type=Path)
    parser.add_argument("--class-name", default="car")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    repository_root = Path(__file__).resolve().parents[3]
    output = args.output.resolve()
    if output.is_relative_to(repository_root):
        parser.error("Output must be outside the source repository")
    inputs = (args.validation_annotations, args.validation_predictions)
    if args.mode == "validation":
        if any(value is not None for value in (
            args.holdout_annotations, args.holdout_predictions, args.freeze_record
        )):
            parser.error("Validation-only mode prohibits any holdout or freeze-record paths")
    elif any(value is None for value in (
        args.holdout_annotations, args.holdout_predictions, args.freeze_record
    )):
        parser.error("Holdout mode requires both held-out inputs and author freeze record")
    all_inputs = (
        *inputs, args.holdout_annotations, args.holdout_predictions, args.freeze_record,
    )
    if output in {path.resolve() for path in all_inputs if path is not None}:
        parser.error("Output cannot overwrite an input")
    if output.exists():
        parser.error("Output already exists; preserving immutable evidence")

    try:
        if args.mode == "validation":
            report, _ = validation_candidate(*inputs, args.class_name)
        else:
            preliminary, _ = validation_candidate(*inputs, args.class_name)
            if preliminary["validation_threshold"]["status"] != "CANDIDATE_ONLY":
                report = preliminary
                report["status"] = "BLOCKED_VALIDATION"
            else:
                report = evaluate_reference(
                    *inputs, args.holdout_annotations,
                    args.holdout_predictions, args.class_name,
                    freeze_record=args.freeze_record,
                )
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, allow_nan=False, sort_keys=True)
            handle.write("\n")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"P01 benchmark: {type(exc).__name__}: {exc}\n")
    print(json.dumps({
        "status": report["status"],
        "output": str(output),
        "threshold": report["validation_threshold"].get("threshold"),
        "model_inference_performed_by_this_script": False,
        "processed_holdout": args.mode == "holdout" and "holdout_counts" in report,
        "metrics_computed_from": "provided_COCO_detections_and_source_labels",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
