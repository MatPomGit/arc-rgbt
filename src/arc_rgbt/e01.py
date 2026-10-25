"""E01: deterministic, labelled quality-aware detection-fusion benchmark.

This does not measure real sensors, calibrate scores or infer image quality.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from arc_rgbt.bench import evaluate
from arc_rgbt.common import exact_keys, provenance, save_json
from arc_rgbt.quality_fusion import _unit, quality_fuse_detections

METHODS = ("rgb_only", "thermal_only", "fixed_fusion", "quality_aware_fusion")


def run(dataset: dict, output: str | Path, source_path: str | Path | None = None) -> dict:
    if not isinstance(dataset, dict):
        raise ValueError("E01 input must be a JSON mapping")
    exact_keys(dataset, {"experiment", "data_origin", "quality_origin",
                         "annotation_status", "config", "frames"})
    if dataset["experiment"] != "E01":
        raise ValueError("E01 experiment identifier required")
    if dataset["data_origin"] not in {"simulated", "reference", "measured"}:
        raise ValueError("Unknown data_origin")
    if dataset["quality_origin"] not in {
        "synthetic_scenario", "heuristic", "measured_independent"
    }:
        raise ValueError("Unknown quality_origin")
    if dataset["annotation_status"] != "complete":
        raise ValueError("Complete annotation declaration required")
    config = dataset["config"]
    if not isinstance(config, dict):
        raise ValueError("config must be a mapping")
    exact_keys(config, {"iou_threshold", "min_effective_score"})
    threshold = config["iou_threshold"]
    gate = _unit(config["min_effective_score"], "min_effective_score")
    if (isinstance(threshold, bool) or not isinstance(threshold, (float, int))
            or not 0 < threshold <= 1):
        raise ValueError("iou_threshold must be in (0,1]")
    _unit(threshold, "iou_threshold")

    frames = dataset["frames"]
    if not isinstance(frames, list) or not frames:
        raise ValueError("At least one annotated frame required")
    predictions = {key: [] for key in METHODS}
    seen: set[str | int] = set()
    for sample in frames:
        if not isinstance(sample, dict):
            raise ValueError("Each frame must be a mapping")
        exact_keys(sample, {"id", "ground_truth", "rgb_predictions",
                            "thermal_predictions", "quality"})
        frame_id = sample["id"]
        if (isinstance(frame_id, bool) or not isinstance(frame_id, (str, int))
                or frame_id == "" or frame_id in seen):
            raise ValueError("Frame identifiers must be unique and nonempty")
        seen.add(frame_id)
        q = sample["quality"]
        if not isinstance(q, dict):
            raise ValueError("quality must be a mapping")
        exact_keys(q, {"rgb", "thermal"})
        qr, qt = _unit(q["rgb"], "quality.rgb"), _unit(q["thermal"], "quality.thermal")
        rgb, thermal = sample["rgb_predictions"], sample["thermal_predictions"]
        fixed = quality_fuse_detections(
            rgb, thermal, rgb_quality=1, thermal_quality=1,
            min_effective_score=gate, match_iou=threshold,
        )
        adjusted = quality_fuse_detections(
            rgb, thermal, rgb_quality=qr, thermal_quality=qt,
            min_effective_score=gate, match_iou=threshold,
        )
        # The evaluation layer validates ground-truth geometry/class labels.
        candidates = {
            "rgb_only": [box for box in rgb if box["score"] >= gate],
            "thermal_only": [box for box in thermal if box["score"] >= gate],
            "fixed_fusion": fixed,
            "quality_aware_fusion": adjusted,
        }
        for method, boxes in candidates.items():
            predictions[method].append({
                "id": frame_id,
                "ground_truth": sample["ground_truth"],
                "predictions": boxes,
            })
    scores = {
        method: evaluate(predictions[method], iou_threshold=threshold)
        for method in METHODS
    }
    report = {
        "experiment": "E01",
        "data_origin": dataset["data_origin"],
        "quality_origin": dataset["quality_origin"],
        "annotation_status": dataset["annotation_status"],
        "configuration": config,
        "metrics": scores,
        "provenance": provenance([source_path] if source_path else []),
        "limitations": [
            "quality is externally supplied; it is not a learned or calibrated estimate",
            "all detector predictions, scores and annotations come from the input manifest",
            "quality multiplication is a heuristic, not probability calibration",
            "frame-level matching is not tracking or temporal filtering",
            "E01 does not establish sensor, flight, MCU or field detection performance",
        ],
    }
    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    save_json(target / "manifest.json", report)
    with (target / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["method", *next(iter(scores.values()))])
        writer.writeheader()
        for method, metric in scores.items():
            writer.writerow({"method": method, **metric})
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="E01 labelled input JSON")
    parser.add_argument("--output", default="reports/E01")
    args = parser.parse_args(argv)
    dataset = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    report = run(dataset, args.output, args.dataset)
    print(json.dumps({"experiment": report["experiment"],
                      "methods": list(report["metrics"]), "output": args.output},
                     sort_keys=True))


if __name__ == "__main__":
    main()
