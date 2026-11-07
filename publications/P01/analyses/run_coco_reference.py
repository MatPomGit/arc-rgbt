"""P01 offline benchmark of supplied COCO labels and detector predictions.

Only validation selects the threshold. Source-video grouping is a proxy,
not a claim of independent camera acquisitions or physical sensor limits.
The script does not run model inference or download images/weights.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
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
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Each COCO image needs a nonempty source video_id")
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


def evaluate_reference(
    validation_annotations: Path, validation_predictions: Path,
    holdout_annotations: Path, holdout_predictions: Path,
    selected_class: str,
) -> dict:
    """Lock validation threshold before loading held-out outcome data."""
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
            "holdout_annotations": digest(holdout_annotations),
            "holdout_predictions": digest(holdout_predictions),
        },
        "implementation_sha256": {
            "runner": digest(Path(__file__)),
            "p01_metrics": digest(Path(__import__(
                "arc_rgbt.p01_metrics", fromlist=["__file__"]
            ).__file__)),
        },
    }
    if cutoff["status"] != "CANDIDATE_ONLY":
        return result

    # Deliberately delay reading holdout GT and predictions until after
    # the validation-only operating point has been selected.
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-annotations", type=Path, required=True)
    parser.add_argument("--validation-predictions", type=Path, required=True)
    parser.add_argument("--holdout-annotations", type=Path, required=True)
    parser.add_argument("--holdout-predictions", type=Path, required=True)
    parser.add_argument("--class-name", default="car")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    repository_root = Path(__file__).resolve().parents[3]
    output = args.output.resolve()
    if output.is_relative_to(repository_root):
        parser.error("Output must be outside the source repository")
    inputs = (
        args.validation_annotations, args.validation_predictions,
        args.holdout_annotations, args.holdout_predictions,
    )
    if output in {path.resolve() for path in inputs}:
        parser.error("Output cannot overwrite an input")
    if output.exists():
        parser.error("Output already exists; preserving immutable evidence")

    try:
        report = evaluate_reference(*inputs, args.class_name)
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
        "real_measurements_performed_by_this_script": False,
        "metrics_computed_from": "provided_COCO_detections_and_source_labels",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
