"""Detection evaluation on explicitly labelled input, with provenance-bearing reports."""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
from pathlib import Path

from arc_rgbt.common import exact_keys, provenance, save_json
from arc_rgbt.fusionlab import _iou


def evaluate(frames: list[dict], iou_threshold: float = 0.5) -> dict:
    if not 0 < iou_threshold <= 1:
        raise ValueError("Invalid IoU threshold")
    tp = fp = fn = 0
    if not isinstance(frames, list):
        raise ValueError("frames must be a list")
    for frame in frames:
        if not isinstance(frame, dict):
            raise ValueError("Each frame must be a mapping")
        exact_keys(frame, {"id", "ground_truth", "predictions"})
        truth, predictions = frame["ground_truth"], frame["predictions"]
        if not isinstance(truth, list) or not isinstance(predictions, list):
            raise ValueError("Ground truth and predictions must be lists")
        for box in [*truth, *predictions]:
            if not isinstance(box, dict) or set(box) - {"label", "bbox", "score"}:
                raise ValueError("Invalid annotation schema")
            coords = box.get("bbox")
            if (not isinstance(box.get("label"), str) or not box["label"]
                    or not isinstance(coords, list) or len(coords) != 4
                    or any(isinstance(v, bool) or not isinstance(v, (int, float))
                           or not math.isfinite(v) for v in coords)
                    or min(coords[2:]) <= 0):
                raise ValueError("Invalid labelled bounding box")
        used: set[int] = set()
        for pred in sorted(predictions, key=lambda box: -box["score"]):
            if not 0 <= pred["score"] <= 1:
                raise ValueError("Prediction confidence out of bounds")
            if len(pred["bbox"]) != 4 or min(pred["bbox"][2:]) <= 0:
                raise ValueError("Invalid prediction bounding box")
            matches = [(j, _iou(pred["bbox"], box["bbox"])) for j, box in enumerate(truth)
                       if j not in used and box["label"] == pred["label"]]
            j, overlap = max(matches, key=lambda item: item[1], default=(-1, -1))
            if overlap >= iou_threshold:
                tp += 1
                used.add(j)
            else:
                fp += 1
        fn += len(truth) - len(used)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            "iou_threshold": iou_threshold, "frames": len(frames)}


def report(dataset: dict, dest: str | Path, source_path: str | Path | None = None) -> dict:
    exact_keys(dataset, {"data_origin", "frames", "config"})
    if dataset["data_origin"] not in ("simulated", "measured", "reference"):
        raise ValueError("Explicit data_origin required")
    if not dataset["frames"]:
        raise ValueError("Cannot compute detection metrics without labelled frames")
    result = {"metrics": evaluate(dataset["frames"]), "config": dataset["config"],
              "data_origin": dataset["data_origin"],
              "provenance": provenance([source_path] if source_path else [])}
    root = Path(dest)
    root.mkdir(parents=True, exist_ok=True)
    save_json(root / "bench.json", result)
    with (root / "bench.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(result["metrics"]))
        writer.writeheader()
        writer.writerow(result["metrics"])
    escaped = html.escape(json.dumps(result, indent=2))
    (root / "bench.html").write_text(
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<title>RGBT benchmark</title><h1>Detection benchmark</h1><pre>"
        + escaped + "</pre></html>\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", required=True, help="JSON containing labelled frames")
    p.add_argument("--output", default="reports/bench")
    a = p.parse_args(argv)
    dataset = json.loads(Path(a.dataset).read_text(encoding="utf-8"))
    print(json.dumps(report(dataset, a.output, a.dataset)["metrics"], sort_keys=True))


if __name__ == "__main__":
    main()
