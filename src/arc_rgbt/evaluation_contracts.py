"""Evaluation contracts on declared labels; not physical or licence verification."""

from __future__ import annotations

import math
from collections import Counter

from arc_rgbt.bench import evaluate
from arc_rgbt.fusionlab import _iou


def _unit(value: object, field: str, *, positive: bool = False) -> float:
    if (type(value) not in (int, float) or not math.isfinite(value)
            or not (0 < value <= 1 if positive else 0 <= value <= 1)):
        raise ValueError(f"{field} must be a finite number within [0,1]")
    return float(value)


def _interpolated_ap(recalls: list[float], precisions: list[float]) -> float:
    if not recalls:
        return 0.0
    envelope = precisions[:]
    for i in range(len(envelope) - 2, -1, -1):
        envelope[i] = max(envelope[i], envelope[i + 1])
    total = previous = 0.0
    for recall, precision in zip(recalls, envelope, strict=True):
        total += (recall - previous) * precision
        previous = recall
    return total


def detection_contract(
    frames: list[dict], *, annotation_status: str,
    iou_threshold: float = 0.5, operating_score: float = 0.0,
) -> dict:
    """Class-wise all-points AP and held-out-score FP/frame, using existing Bench boxes."""
    if annotation_status != "complete":
        raise ValueError("Complete positive and negative frame annotation required")
    threshold = _unit(iou_threshold, "iou_threshold", positive=True)
    cutoff = _unit(operating_score, "operating_score")
    if not isinstance(frames, list) or not frames:
        raise ValueError("Nonempty labelled frames required")
    evaluate(frames, iou_threshold=threshold)  # existing full-box schema validation
    working = [
        {**frame, "predictions": [
            p for p in frame["predictions"] if p["score"] >= cutoff
        ]}
        for frame in frames
    ]
    counts = evaluate(working, iou_threshold=threshold)
    targets: Counter[str] = Counter(
        gt["label"] for frame in frames for gt in frame["ground_truth"]
    )
    per_class = {}
    for label in sorted(targets):
        # Stable tie breaking by declared frame and prediction order.
        proposals = [
            (fi, pi, item) for fi, frame in enumerate(frames)
            for pi, item in enumerate(frame["predictions"]) if item["label"] == label
        ]
        proposals.sort(key=lambda pair: (-pair[2]["score"], pair[0], pair[1]))
        matched: set[tuple[int, int]] = set()
        tp = fp = 0
        recalls, precisions = [], []
        for fi, _, item in proposals:
            best = max((
                (j, _iou(item["bbox"], gt["bbox"]))
                for j, gt in enumerate(frames[fi]["ground_truth"])
                if gt["label"] == label and (fi, j) not in matched
            ), key=lambda pair: pair[1], default=(-1, -1))
            if best[1] >= threshold:
                matched.add((fi, best[0]))
                tp += 1
            else:
                fp += 1
            recalls.append(tp / targets[label])
            precisions.append(tp / (tp + fp))
        per_class[label] = _interpolated_ap(recalls, precisions)
    return {
        "metric_origin": "declared_labelled_boxes_unverified",
        "ap_definition": "all_points_interpolated_per_class_single_IoU",
        "annotation_status": annotation_status,
        "iou_threshold": threshold, "operating_score": cutoff,
        "per_class_ap": per_class,
        "mean_ap": sum(per_class.values()) / len(per_class) if per_class else None,
        "recall_at_operating_score": counts["recall"] if targets else None,
        "precision_at_operating_score": (
            counts["precision"] if counts["tp"] + counts["fp"] else None
        ),
        "fp_per_frame": counts["fp"] / len(frames),
        "tp": counts["tp"], "fp": counts["fp"], "fn": counts["fn"],
        "frames": len(frames), "empirical_admission": False,
        "zero_denominator_policy": (
            "no_GT: AP/recall null; no_predictions: precision null; "
            "complete-negative frames count in FP/frame"
        ),
        "limitations": [
            "Not COCO AP@[.50:.95]; only the declared fixed IoU threshold",
            "Annotation completeness, geometry and source rights not independently audited",
        ],
    }


def tracking_reference_contract(frames: list[dict]) -> dict:
    """Fail-closed ID-track schema; do not invent HOTA or IDF1 scores."""
    if not isinstance(frames, list) or not frames:
        raise ValueError("Nonempty tracking frames required")
    ids = set()
    last_index = -1
    known_labels: dict[tuple[str, str], str] = {}
    counts = Counter()
    for frame in frames:
        if not isinstance(frame, dict) or set(frame) != {
            "frame_id", "frame_index", "annotation_status", "ground_truth", "predictions",
        }:
            raise ValueError("Invalid tracking frame schema")
        fid = frame["frame_id"]
        if not isinstance(fid, str) or not fid or fid in ids:
            raise ValueError("Duplicate or invalid tracking frame ID")
        ids.add(fid)
        index = frame["frame_index"]
        if type(index) is not int or index < 0 or index <= last_index:
            raise ValueError("Tracking frame_index must strictly increase")
        last_index = index
        if frame["annotation_status"] != "complete":
            raise ValueError("Tracking labels must be complete, including negatives")
        for role in ("ground_truth", "predictions"):
            objects = frame[role]
            if not isinstance(objects, list):
                raise ValueError(f"{role} must be a list")
            local_ids = set()
            for obj in objects:
                if not isinstance(obj, dict) or set(obj) != {
                    "track_id", "label", "bbox_xywh",
                }:
                    raise ValueError("Invalid tracking object schema")
                track_id, label = obj["track_id"], obj["label"]
                if (not isinstance(track_id, str) or not track_id
                        or not isinstance(label, str) or not label):
                    raise ValueError("Track ID and label must be nonempty strings")
                if track_id in local_ids:
                    raise ValueError("Duplicate track ID within sequence frame")
                local_ids.add(track_id)
                box = obj["bbox_xywh"]
                if (not isinstance(box, list) or len(box) != 4
                        or any(type(v) not in (int, float) or not math.isfinite(v)
                               for v in box) or min(box[2:]) <= 0):
                    raise ValueError("Invalid track bounding box")
                identity = (role, track_id)
                if identity in known_labels and known_labels[identity] != label:
                    raise ValueError("Tracking identity class changes within sequence")
                known_labels[identity] = label
                counts[role] += 1
    return {
        "schema_validation": "PASS", "frames": len(frames),
        "ground_truth_boxes": counts["ground_truth"],
        "prediction_boxes": counts["predictions"],
        "hota": None, "idf1": None, "empirical_admission": False,
        "evaluation_status": "requires_independently_verified_TrackEval",
        "limitations": [
            "No identity metric is computed by this structural contract",
            "Requires independent GT/identity provenance and reference evaluator tests",
        ],
    }
