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
    max_fp_per_frame: float = 0.1,
) -> dict:
    """Per-GT IoU matching and acquisition-paired recall; declarations unverified."""
    cutoff, iou = _rate(operating_score), _rate(iou_threshold, positive=True)
    fp_ceiling = _rate(max_fp_per_frame)
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
    frame_counts: dict[str, int] = defaultdict(int)
    fp_counts: dict[str, int] = defaultdict(int)
    for frame, group in zip(frames, acquisition_ids, strict=True):
        # Register groups even when all their frames contain no targets.
        group_bins = grouped[group]
        frame_counts[group] += 1
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
                fp_counts[group] += 1
        for idx, target in enumerate(truth):
            footprint = math.sqrt(target["bbox"][2] * target["bbox"][3])
            bin_name = ("small" if footprint < small_limit else
                        "intermediate" if footprint < reference_limit else "reference")
            hit = idx in matched
            group_bins[bin_name][0] += int(hit)
            group_bins[bin_name][1] += 1
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
    paired_group_counts = {
        g: {"small": grouped[g]["small"][1],
            "reference": grouped[g]["reference"][1]}
        for g in paired_groups
    }
    paired_pooled_delta = None
    if paired_groups:
        small_tp = sum(grouped[g]["small"][0] for g in paired_groups)
        small_n = sum(grouped[g]["small"][1] for g in paired_groups)
        ref_tp = sum(grouped[g]["reference"][0] for g in paired_groups)
        ref_n = sum(grouped[g]["reference"][1] for g in paired_groups)
        paired_pooled_delta = small_tp / small_n - ref_tp / ref_n
    # A test sample over budget cannot support the proposed operating condition,
    # even if its acquisition-paired recall difference remains descriptive.
    test_fp_rate = false_positives / len(frames)
    budget_met = test_fp_rate <= fp_ceiling
    eligible = len(paired_groups) >= minimum_paired_groups
    # Retain an explicitly descriptive contrast even when group support
    # is insufficient for an interval. No scientific inference is authorized.
    values = list(deltas.values())
    point = sum(values) / len(values) if values else None
    interval = None
    if eligible and budget_met:
        rng = random.Random(seed)
        samples = sorted(sum(rng.choices(values, k=len(values))) / len(values)
                         for _ in range(replicates))
        interval = [_percentile(samples, 0.025), _percentile(samples, 0.975)]
    report_status = (
        "OPERATING_CONDITION_NOT_MET" if not budget_met else
        "PROSPECTIVE_UNFROZEN" if eligible else "DESCRIPTIVE_ONLY"
    )
    return {
        "status": report_status,
        "operating_condition_met": budget_met,
        "candidate_fp_ceiling": fp_ceiling,
        "empirical_admission": False,
        "grid_origin": "declared_original_native_unverified",
        "per_object": objects, "per_bin": per_bin,
        "per_group": {
            group: {**{name: {"tp": values[name][0], "targets": values[name][1]}
                       for name in ("small", "intermediate", "reference")},
                    "frames": frame_counts[group], "fp": fp_counts[group]}
            for group, values in sorted(grouped.items())
        },
        "groups_total": len(grouped), "groups_with_both_bins": len(paired_groups),
        "groups_without_targets": sum(
            all(counts[name][1] == 0 for name in counts)
            for counts in grouped.values()
        ),
        "group_differences": deltas, "primary_group_mean_delta": point,
        "paired_group_target_counts": paired_group_counts,
        "paired_groups_with_singleton_bin": sum(
            min(counts.values()) == 1 for counts in paired_group_counts.values()
        ),
        "acquisitions_excluded_from_paired_contrast": (
            len(grouped) - len(paired_groups)
        ),
        "paired_object_pooled_delta_sensitivity": paired_pooled_delta,
        "paired_weighting_difference_sensitivity": (
            point - paired_pooled_delta if point is not None else None
        ),
        "candidate_percentile_ci_95": interval,
        "replicates": replicates if interval is not None else 0,
        "fp": false_positives, "frames": len(frames),
        "fp_per_frame": test_fp_rate,
        "notes": "Within-acquisition association only; no causal resolution attribution.",
    }


def choose_validation_threshold(
    frames: list[dict], *, acquisition_ids: list[str], annotation_status: str,
    max_fp_per_frame: float = 0.1, iou_threshold: float = 0.5,
    minimum_groups: int = 10, minimum_frames: int = 200,
    minimum_negative_frames: int = 20, replicates: int = 2000,
    seed: int = 20261101,
) -> dict:
    """Select observed FP/frame operating point on validation only, never test."""
    ceiling, iou = _rate(max_fp_per_frame), _rate(iou_threshold, positive=True)
    _validate(frames, acquisition_ids, annotation_status, iou)
    if (type(minimum_groups) is not int or minimum_groups < 2
            or type(minimum_frames) is not int or minimum_frames < 1
            or type(minimum_negative_frames) is not int
            or minimum_negative_frames < 1
            or type(replicates) is not int or replicates < 100
            or type(seed) is not int):
        raise ValueError("Invalid validation exposure/bootstrap parameters")
    result = {"status": "BLOCKED_VALIDATION_SIZE", "threshold": None,
              "empirical_admission": False, "frames": len(frames),
              "groups": len(set(acquisition_ids)),
              "limitations": "Observed validation FP/frame is not a future upper bound"}
    if len(frames) < minimum_frames or len(set(acquisition_ids)) < minimum_groups:
        return result
    negative_groups = {group for frame, group in zip(frames, acquisition_ids, strict=True)
                       if not frame["ground_truth"]}
    negative_frames = sum(not frame["ground_truth"] for frame in frames)
    result.update(negative_frames=negative_frames, negative_groups=len(negative_groups))
    if negative_frames < minimum_negative_frames or len(negative_groups) < 2:
        result["status"] = "BLOCKED_NEGATIVE_EXPOSURE"
        return result
    # Pre-aggregate original frames by acquisition to retain cluster covariance.
    groups = defaultdict(list)
    for frame, group in zip(frames, acquisition_ids, strict=True):
        groups[group].append(frame)
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
                # FP/frame is a ratio of totals. Resample acquisition groups
                # jointly: never treat neighboring frames as IID observations.
                cluster_rates = []
                for group in sorted(groups):
                    group_frames = [
                        {**f, "predictions": [p for p in f["predictions"]
                                              if p["score"] >= cutoff]}
                        for f in groups[group]
                    ]
                    measured = evaluate(group_frames, iou_threshold=iou)
                    cluster_rates.append((measured["fp"], len(group_frames)))
                rng = random.Random(seed)
                bootstrap_rates = []
                for _ in range(replicates):
                    sampled = rng.choices(cluster_rates, k=len(cluster_rates))
                    bootstrap_rates.append(
                        sum(item[0] for item in sampled) /
                        sum(item[1] for item in sampled)
                    )
                bootstrap_rates.sort()
                interval = [_percentile(bootstrap_rates, 0.025),
                            _percentile(bootstrap_rates, 0.975)]
                result.update(
                    status="CANDIDATE_ONLY", threshold=cutoff,
                    validation_fp_per_frame=rate, validation_tp=counts["tp"],
                    validation_fp_bootstrap_ci_95=interval,
                    validation_fp_upper_ci_exceeds_ceiling=interval[1] > ceiling,
                    bootstrap_replicates=replicates,
                )
            return result
    result["status"] = "BLOCKED_NO_FEASIBLE_THRESHOLD"
    return result
