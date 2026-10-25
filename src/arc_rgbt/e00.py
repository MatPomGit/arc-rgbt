"""E00: sensor-native thermal resolution sweep on seeded synthetic labelled scenes."""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
from pathlib import Path

import cv2
import numpy as np

from arc_rgbt.bench import evaluate
from arc_rgbt.common import exact_keys, load_yaml, positive_integer, provenance, save_json
from arc_rgbt.degradesim import degrade

NATIVE_SIZES = [(8, 8), (16, 12), (32, 24), (80, 60), (160, 120), (256, 192), (320, 240)]


def scenes(count: int, seed: int) -> list[tuple[np.ndarray, list[dict]]]:
    """Synthetic rectangles with known labels; not representative thermal sensor data."""
    rng = np.random.default_rng(seed)
    frames = []
    for _ in range(count):
        source = rng.normal(0.1, 0.015, size=(240, 320)).astype(np.float32)
        labelled = []
        for label, w, h in (("person", 9, 24), ("vehicle", 44, 18)):
            x = int(rng.integers(0, 320 - w))
            y = int(rng.integers(0, 240 - h))
            source[y:y + h, x:x + w] = 0.86
            labelled.append({"label": label, "bbox": [x, y, w, h]})
        frames.append((np.clip(source, 0, 1), labelled))
    return frames


def _ground_truth_native(boxes: list[dict], w: int, h: int) -> list[dict]:
    converted = []
    for entry in boxes:
        x, y, bw, bh = entry["bbox"]
        x1, y1 = int(np.floor(x * w / 320)), int(np.floor(y * h / 240))
        x2, y2 = int(np.ceil((x + bw) * w / 320)), int(np.ceil((y + bh) * h / 240))
        converted.append({"label": entry["label"], "bbox": [x1, y1, x2 - x1, y2 - y1]})
    return converted


def _detect(image: np.ndarray, threshold: float, min_area: int) -> list[dict]:
    mask = (image >= threshold).astype(np.uint8)
    num, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    predictions = []
    for idx in range(1, num):
        x, y, w, h, area = map(int, stats[idx])
        if area >= min_area:
            # Deliberately class-agnostic. This baseline only tests object localization;
            # assigning a class would claim recognition not implemented here.
            predictions.append({"label": "object", "bbox": [x, y, w, h], "score": 1.0})
    return predictions


def run(config: dict, destination: str | Path, config_path: str | Path | None = None) -> dict:
    exact_keys(config, {"seed", "frames", "optical_sigma_px", "noise_sigma", "threshold",
                        "min_area_px", "interpolated_preview_px"})
    seed, count = config["seed"], config["frames"]
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    positive_integer(count, "frames")
    if count > 128:
        raise ValueError("frames must be at most 128 for bounded offline E00 execution")
    positive_integer(config["min_area_px"], "min_area_px")
    threshold = config["threshold"]
    if (isinstance(threshold, bool) or not isinstance(threshold, (int, float))
            or not math.isfinite(threshold) or not 0 < threshold < 1):
        raise ValueError("threshold must be finite and strictly between 0 and 1")
    for name in ("optical_sigma_px", "noise_sigma"):
        value = config[name]
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0):
            raise ValueError(f"{name} must be non-negative and finite")
    preview = config["interpolated_preview_px"]
    if not isinstance(preview, list) or len(preview) != 2 or any(
        not isinstance(v, int) or isinstance(v, bool) or v <= 0 for v in preview
    ):
        raise ValueError("interpolated_preview_px must contain two positive integers")
    if preview[0] * preview[1] > 4_000_000:
        raise ValueError("interpolated_preview_px exceeds four million pixels")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    samples = scenes(count, seed)
    rows = []
    per_resolution = []
    for w, h in NATIVE_SIZES:
        frames = []
        representation = []
        unrounded_areas = []
        subpixel_count = 0
        object_count = 0
        for index, (image, boxes) in enumerate(samples):
            native, record = degrade(image, width_px=w, height_px=h,
                                     optical_sigma_px=config["optical_sigma_px"],
                                     noise_sigma=config["noise_sigma"], seed=seed + index)
            record["interpolated_resolution_px"] = preview
            truth = _ground_truth_native(boxes, w, h)
            # Evaluation is class-agnostic by design. This is NOT a class detector.
            anon_truth = [{**entry, "label": "object"} for entry in truth]
            pred = _detect(native, config["threshold"], config["min_area_px"])
            frames.append({"id": f"scene-{index:03d}", "ground_truth": anon_truth,
                           "predictions": pred})
            representation.extend([entry["bbox"][2] * entry["bbox"][3] for entry in truth])
            for entry in boxes:
                _, _, bw, bh = entry["bbox"]
                exact_width, exact_height = bw * w / 320, bh * h / 240
                unrounded_areas.append(exact_width * exact_height)
                subpixel_count += int(min(exact_width, exact_height) < 1)
                object_count += 1
            if index == 0:
                # Visualization only; cannot improve native sensor information.
                up = cv2.resize(native, tuple(preview), interpolation=cv2.INTER_NEAREST)
                cv2.imwrite(str(destination / f"preview_{w}x{h}.png"), (up * 255).astype(np.uint8))
        metrics = evaluate(frames)
        row = {"native_width_px": w, "native_height_px": h,
               "interpolated_width_px": preview[0], "interpolated_height_px": preview[1],
               "median_annotation_bbox_area_native_px2": float(np.median(representation)),
               "median_unrounded_bbox_area_native_px2": float(np.median(unrounded_areas)),
               "fraction_objects_subpixel_axis": subpixel_count / object_count,
               **metrics}
        rows.append(row)
        per_resolution.append({"native_resolution_px": [w, h],
                               "data_origin": "simulated", "label_origin": "synthetic_geometry",
                               "detector": "class_agnostic_threshold_connected_components",
                               "metrics": metrics,
                               "observability": {
                                   "median_unrounded_bbox_area_native_px2":
                                       float(np.median(unrounded_areas)),
                                   "fraction_objects_subpixel_axis": subpixel_count / object_count,
                                   "definition": "source_bbox_scaled_without_integer_cell_rounding",
                               },
                               "degradation": {**record,
                                               "seed": "per_frame_seed_plus_index",
                                               "first_noise_seed": seed,
                                               "last_noise_seed": seed + count - 1}})
    manifest = {"experiment": "E00", "data_origin": "simulated",
                "physical_measurements": False, "seed": seed, "configuration": config,
                "provenance": provenance([config_path] if config_path else []),
                "resolutions": per_resolution,
                "limitations": ["Synthetic rectangular objects, not radiometric thermograms",
                                "Class-agnostic localization only; not person/vehicle recognition",
                                "Annotation rounding can inflate boxes at extremely low resolution",
                                "Subpixel-axis fractions are geometric, not empirically measured "
                                "detectability",
                                "Interpolation affects visualization only, not detection metrics",
                                "No calibration, temporal effects or hardware measurements"]}
    save_json(destination / "manifest.json", manifest)
    with (destination / "metrics.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    table = "".join("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>"
                                         for v in row.values()) + "</tr>" for row in rows)
    headers = "".join(f"<th>{html.escape(key)}</th>" for key in rows[0])
    document = ("<!doctype html><html lang='en'><meta charset='utf-8'>"
                "<title>E00 synthetic resolution sweep</title>"
                "<h1>E00 native thermal resolution</h1>"
                "<p>SIMULATED labelled rectangles. No physical camera data, no class recognition. "
                "Preview interpolation does not increase sensor resolution.</p>"
                f"<table border='1'><thead><tr>{headers}</tr></thead><tbody>{table}</tbody></table>"
                "<h2>Configuration and provenance</h2><pre>"
                + html.escape(json.dumps(manifest, indent=2)) + "</pre></html>\n")
    (destination / "report.html").write_text(document, encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", default="experiments/E00/config.yaml")
    p.add_argument("--output", default="reports/E00")
    a = p.parse_args(argv)
    record = run(load_yaml(a.config), a.output, a.config)
    print(json.dumps({"experiment": record["experiment"], "origin": record["data_origin"],
                      "output": a.output, "variants": len(record["resolutions"])}, sort_keys=True))


if __name__ == "__main__":
    main()
