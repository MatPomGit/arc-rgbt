"""E02: deterministic temporal-skew geometry for moving frontal planar targets.

This is an analytical overlap diagnostic, not a detection or sensor benchmark.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any

from arc_rgbt.common import exact_keys, provenance, save_json
from arc_rgbt.synchronization import pair_frames


def _number(value: Any, name: str, *, lower: float = 0,
            upper: float = 1e6, lower_open: bool = False) -> float:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value > upper
            or (value <= lower if lower_open else value < lower)):
        raise ValueError(f"{name} must be finite and in the configured range")
    return float(value)


def _integer(value: Any, name: str, limit: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= limit:
        raise ValueError(f"{name} must be an integer in [1,{limit}]")
    return value


def _sequence(values: Any, name: str, limit: int,
              validator: Any) -> list:
    if not isinstance(values, list) or not 1 <= len(values) <= limit:
        raise ValueError(f"{name} must be a nonempty bounded list")
    return [validator(value) for value in values]


def _median_or_none(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _horizontal_geometric_iou(width_px: float, shift_px: float) -> float:
    """Exact IoU for two identical axis-aligned rectangles shifted only in x."""
    if shift_px >= width_px:
        return 0.0
    return (width_px - shift_px) / (width_px + shift_px)


def simulate(config: dict) -> dict:
    if not isinstance(config, dict):
        raise ValueError("E02 config must be a mapping")
    exact_keys(config, {"rgb_fps", "thermal_fps", "frames", "tolerance_ms",
                        "thermal_start_offsets_ms", "native_thermal_sizes_px",
                        "horizontal_fov_deg", "target_range_m", "target_width_m",
                        "lateral_speeds_m_s"})
    rgb_fps = _number(config["rgb_fps"], "rgb_fps", lower=0, upper=240,
                      lower_open=True)
    thermal_fps = _number(config["thermal_fps"], "thermal_fps", lower=0, upper=240,
                          lower_open=True)
    frames = _integer(config["frames"], "frames", 500)
    tolerance = _number(config["tolerance_ms"], "tolerance_ms", upper=1000)
    offsets = _sequence(config["thermal_start_offsets_ms"], "offsets", 30,
                        lambda x: _number(x, "offset_ms", upper=1000))
    speeds = _sequence(config["lateral_speeds_m_s"], "speeds", 30,
                       lambda x: _number(x, "speed_m_s", upper=100))
    fov_deg = _number(config["horizontal_fov_deg"], "horizontal_fov_deg",
                      lower=0, upper=179, lower_open=True)
    target_range = _number(config["target_range_m"], "target_range_m",
                           lower=0, upper=100000, lower_open=True)
    target_width = _number(config["target_width_m"], "target_width_m",
                           lower=0, upper=1000, lower_open=True)
    sizes = _sequence(config["native_thermal_sizes_px"], "resolutions", 30,
                      lambda x: x)
    validated_sizes = []
    for pair in sizes:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("Each native resolution must be [width,height]")
        validated_sizes.append([_integer(pair[0], "width_px", 8192),
                                _integer(pair[1], "height_px", 8192)])
    if len(set(map(tuple, validated_sizes))) != len(validated_sizes):
        raise ValueError("Native sensor sizes must be unique")
    if len(offsets) * len(speeds) * len(sizes) > 10000:
        raise ValueError("Maximum 10000 E02 geometry configurations")

    # Every timestamp is from a single *simulated* monotonic capture clock.
    # Reject FPS that cannot produce a signed-64-bit nanosecond period.
    min_fps = 1e9 / (2**63 - 1)
    if rgb_fps < min_fps or thermal_fps < min_fps:
        raise ValueError("FPS is too small for bounded nanosecond timestamps")
    rgb_period_ns = round(1e9 / rgb_fps)
    thermal_period_ns = round(1e9 / thermal_fps)
    max_time_ns = (frames - 1) * thermal_period_ns + round(max(offsets) * 1e6)
    if max_time_ns > 2**63 - 1:
        raise ValueError("Simulated timestamps exceed signed-64-bit range")
    rgb_count = math.ceil(max_time_ns / rgb_period_ns) + 2
    if rgb_count > 120000:
        raise ValueError("Simulated frame count too large")
    rgb_stream = [{"id": f"rgb-{i:06d}", "timestamp_ns": i * rgb_period_ns}
                  for i in range(rgb_count)]
    rows: list[dict] = []
    timing: list[dict] = []
    for offset in offsets:
        t0 = round(offset * 1e6)
        thermal_stream = [
            {"id": f"thermal-{i:06d}", "timestamp_ns": t0 + i * thermal_period_ns}
            for i in range(frames)
        ]
        synced = pair_frames(rgb_stream, thermal_stream, tolerance_ms=tolerance,
                             clock_domain="shared_monotonic_ns")
        timing.append({"thermal_start_offset_ms": offset,
                       "summary": synced["summary"]})
        skews = [abs(p["delta_ms"]) for p in synced["pairs"]]
        for w, h in validated_sizes:
            focal_px = w / (2 * math.tan(math.radians(fov_deg) / 2))
            target_px = target_width * focal_px / target_range
            for speed in speeds:
                shifts = [speed * (skew / 1000) * focal_px / target_range
                          for skew in skews]
                overlaps = [_horizontal_geometric_iou(target_px, shift)
                            for shift in shifts]
                rows.append({
                    "native_width_px": w, "native_height_px": h,
                    "thermal_start_offset_ms": offset,
                    "lateral_speed_m_s": speed,
                    "target_width_native_px": target_px,
                    "matched_pairs": len(skews),
                    "thermal_pair_fraction": synced["summary"]["matched_thermal_fraction"],
                    "median_abs_skew_ms": _median_or_none(skews),
                    "median_geometric_shift_px": _median_or_none(shifts),
                    "median_geometric_bbox_iou": _median_or_none(overlaps),
                    "min_geometric_bbox_iou": min(overlaps) if overlaps else None,
                })
    return {
        "experiment": "E02", "data_origin": "simulated",
        "metric_origin": "analytical_geometry",
        "physical_measurements": False,
        "model": "pinhole_fixed_fov_lateral_translation_equal_rectangles",
        "config": config, "rows": rows, "synchronization": timing,
        "limitations": [
            "timestamps are generated, not physical camera exposures",
            "motion is lateral and target range/FOV remain fixed",
            "equal-size frontal rectangles ignore parallax, occlusion and lens distortion",
            "bbox IoU is analytical geometric overlap, not detection precision or recall",
            "same FOV makes normalized overlap independent of native resolution",
            "no detector, image quality estimator or thermal radiometry is modeled",
        ],
    }


def run(config: dict, destination: str | Path,
        config_path: str | Path | None = None) -> dict:
    report = simulate(config)
    report["provenance"] = provenance([config_path] if config_path else [])
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    save_json(root / "manifest.json", report)
    with (root / "geometry.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(report["rows"][0]))
        writer.writeheader()
        writer.writerows(report["rows"])
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="E02 JSON scenario")
    parser.add_argument("--output", default="reports/E02")
    args = parser.parse_args(argv)
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    result = run(config, args.output, args.config)
    print(json.dumps({"experiment": result["experiment"],
                      "data_origin": result["data_origin"],
                      "cases": len(result["rows"]), "output": args.output},
                     sort_keys=True))


if __name__ == "__main__":
    main()
