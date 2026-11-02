"""Prospective P01 native-grid GT evaluation. No independent empirical admission."""

from __future__ import annotations

import math
import random
from collections import defaultdict

from arc_rgbt.bench import evaluate
from arc_rgbt.fusionlab import _iou


def _rate(value: float, *, positive: bool = False) -> float:
    if (type(value) not in (int, float) or not math.isfinite(value)
            or not (0 < value <= 1 if positive else 0 <= value <= 1)):
        raise ValueError("Invalid rate or threshold")
    return float(value)


def _validate(frames: list[dict], groups: list[str], labels: str, iou: float) -> None:
    if labels != "complete":
        raise ValueError("Complete annotations required, including negative frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("Nonempty frames required")
    if (not isinstance(groups, list) or len(groups) != len(frames)
            or any(not isinstance(g, str) or not g.strip() for g in groups)):
        raise ValueError("One nonempty acquisition ID per frame required")
    evaluate(frames, iou_threshold=iou)


def _percentile(values: list[float], probability: float) -> float:
    point = (len(values) - 1) * probability
    low, high = math.floor(point), math.ceil(point)
    return values[low] + (values[high] - values[low]) * (point - low)


def native_footprint_recall(
    frames: list[dict], *, acquisition_ids: list[str], annotation_status: str,
    grid_origin: str, operating_score: float = 0.5, iou_threshold: float = 0.5,
    small_limit: float = 8, reference_limit: float = 16,
    minimum_paired_groups: int = 10, replicates: int = 2000, seed: int = 20261101,
) -> dict:
    """Per-GT IoU matching and acquisition-paired recall; declarations unverified."""
    cutoff, iou = _rate(operating_score), _rate(iou_threshold, positive=True)
    _validate(frames, acquisition_ids, annotation_status, iou)
    if grid_origin != "original_native":
        raise ValueError("Original-native GT grid required")
    if (type(small_limit) not in (int, float)
            or type(reference_limit) not in (int, float)
            or not math.isfinite(small_limit) or not math.isfinite(reference_limit)
            or not 0 < small_limit < reference_limit):
        raise ValueError("Invalid native footprint bins")
    if (type(minimum_paired_groups) is not int or minimum_paired_groups < 2
            or type(replicates) is not int or replicates < 100 or type(seed) is not int):
        raise ValueError("Invalid bootstrap parameters")

    grouped = defaultdict(lambda: {"small": [0, 0], "intermediate": [0, 0],
                                   "reference": [0, 0]})
    objects = []
    false_positives = 0
    for frame, group in zip(frames, acquisition_ids, strict=True):
        truth = frame["ground_truth"]
        matched = set()
        proposals = sorted(enumerate(frame["predictions"]),
                           key=lambda pair: (-pair[1]["score"], pair[0]))
        for _, prediction in proposals:
            if prediction["score"] < cutoff:
                continue
            best = max(
                ((idx, _iou(prediction["bbox"], target["bbox"]))
                 for idx, target in enumerate(truth)
                 if idx not in matched and target["label"] == prediction["label"]),
                key=lambda pair: pair[1], default=(-1, -1.0),
            )
            if best[1] >= iou:
                matched.add(best[0])
            else:
                false_positives += 1
        for idx, target in enumerate(truth):
            footprint = math.sqrt(target["bbox"][2] * target["bbox"][3])
            bin_name = ("small" if footprint < small_limit else
                        "intermediate" if footprint < reference_limit else "reference")
            hit = idx in matched
            grouped[group][bin_name][0] += int(hit)
            grouped[group][bin_name][1] += 1
            objects.append({"frame_id": frame["id"], "acquisition_id": group,
                            "gt_index": idx, "label": target["label"],
                            "footprint_px": footprint, "bin": bin_name, "matched": hit})
    per_bin = {}
    for name in ("small", "intermediate", "reference"):
        tp = sum(g[name][0] for g in grouped.values())
        count = sum(g[name][1] for g in grouped.values())
        per_bin[name] = {"tp": tp, "targets": count,
                         "recall": tp / count if count else None}
    paired_groups = sorted(g for g, v in grouped.items()
                           if v["small"][1] and v["reference"][1])
    deltas = {g: (grouped[g]["small"][0] / grouped[g]["small"][1]
                  - grouped[g]["reference"][0] / grouped[g]["reference"][1])
              for g in paired_groups}
    eligible = len(paired_groups) >= minimum_paired_groups
    point, interval = None, None
    if eligible:
        values = list(deltas.values())
        point = sum(values) / len(values)
        rng = random.Random(seed)
        samples = sorted(sum(rng.choices(values, k=len(values))) / len(values)
                         for _ in range(replicates))
        interval = [_percentile(samples, 0.025), _percentile(samples, 0.975)]
    return {
        "status": "PROSPECTIVE_UNFROZEN" if eligible else "DESCRIPTIVE_ONLY",
        "empirical_admission": False,
        "grid_origin": "declared_original_native_unverified",
        "per_object": objects, "per_bin": per_bin,
        "groups_total": len(grouped), "groups_with_both_bins": len(paired_groups),
        "group_differences": deltas, "primary_group_mean_delta": point,
        "candidate_percentile_ci_95": interval, "replicates": replicates if eligible else 0,
        "fp": false_positives, "frames": len(frames),
        "fp_per_frame": false_positives / len(frames),
        "notes": "Within-acquisition association only; no causal resolution attribution.",
    }


def choose_validation_threshold(
    frames: list[dict], *, acquisition_ids: list[str], annotation_status: str,
    max_fp_per_frame: float = 0.1, iou_threshold: float = 0.5,
    minimum_groups: int = 10, minimum_frames: int = 200,
) -> dict:
    """Select observed FP/frame operating point on validation only, never test."""
    ceiling, iou = _rate(max_fp_per_frame), _rate(iou_threshold, positive=True)
    _validate(frames, acquisition_ids, annotation_status, iou)
    if (type(minimum_groups) is not int or minimum_groups < 2
            or type(minimum_frames) is not int or minimum_frames < 1):
        raise ValueError("Invalid validation group/frame minimums")
    result = {"status": "BLOCKED_VALIDATION_SIZE", "threshold": None,
              "empirical_admission": False, "frames": len(frames),
              "groups": len(set(acquisition_ids)),
              "limitations": "Observed validation FP/frame is not a future upper bound"}
    if len(frames) < minimum_frames or len(set(acquisition_ids)) < minimum_groups:
        return result
    candidates = {0.0, 1.0}
    for frame in frames:
        candidates.update(p["score"] for p in frame["predictions"])
    for cutoff in sorted(candidates):
        filtered = [{**frame, "predictions": [p for p in frame["predictions"]
                                             if p["score"] >= cutoff]}
                    for frame in frames]
        counts = evaluate(filtered, iou_threshold=iou)
        rate = counts["fp"] / len(frames)
        if rate <= ceiling:
            if counts["tp"] == 0:
                result["status"] = "BLOCKED_NO_TRUE_POSITIVES"
            else:
                result.update(status="CANDIDATE_ONLY", threshold=cutoff,
                              validation_fp_per_frame=rate, validation_tp=counts["tp"])
            return result
    result["status"] = "BLOCKED_NO_FEASIBLE_THRESHOLD"
    return result
