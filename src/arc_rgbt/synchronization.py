"""Reproducible cross-sensor timestamp pairing in a shared clock domain.

This tool does not synchronize physical clocks or interpolate missing frames.
"""

from __future__ import annotations

import argparse
import bisect
import json
import math
import statistics
from pathlib import Path
from typing import Any


def _validate_frames(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list of frame records")
    result: list[dict[str, Any]] = []
    ids: set[str] = set()
    last_time = -1
    for raw in value:
        if not isinstance(raw, dict) or set(raw) != {"id", "timestamp_ns"}:
            raise ValueError(f"{label} requires id and timestamp_ns per frame")
        name, stamp = raw["id"], raw["timestamp_ns"]
        if not isinstance(name, str) or not name or name in ids:
            raise ValueError(f"{label} IDs must be nonempty and unique strings")
        if (isinstance(stamp, bool) or not isinstance(stamp, int)
                or not 0 <= stamp <= 2**63 - 1):
            raise ValueError(f"{label} timestamps must be signed-64-bit nonnegative nanoseconds")
        if stamp <= last_time:
            raise ValueError(f"{label} timestamps must be strictly increasing")
        ids.add(name)
        last_time = stamp
        result.append({"id": name, "timestamp_ns": stamp})
    return result


def _percentile(sorted_values: list[float], percent: float) -> float | None:
    if not sorted_values:
        return None
    position = (len(sorted_values) - 1) * percent
    lo = math.floor(position)
    hi = math.ceil(position)
    return (sorted_values[lo] * (hi - position)
            + sorted_values[hi] * (position - lo)) if lo != hi else sorted_values[lo]


def pair_frames(
    rgb_frames: list[dict], thermal_frames: list[dict], *,
    tolerance_ms: float, clock_domain: str,
) -> dict[str, Any]:
    """Greedily pair each thermal frame with its nearest unused RGB frame.

    The inputs must already use the same measured clock domain. Result is a
    baseline alignment for analysis, not a globally optimal assignment.
    """
    if clock_domain != "shared_monotonic_ns":
        raise ValueError("clock_domain must be shared_monotonic_ns; calibrate clocks first")
    if (isinstance(tolerance_ms, bool) or not isinstance(tolerance_ms, (int, float))
            or not math.isfinite(tolerance_ms) or tolerance_ms < 0):
        raise ValueError("tolerance_ms must be nonnegative and finite")
    rgb = _validate_frames(rgb_frames, "rgb_frames")
    thermal = _validate_frames(thermal_frames, "thermal_frames")
    max_delta_ns = tolerance_ms * 1_000_000
    if not math.isfinite(max_delta_ns):
        raise ValueError("tolerance_ms overflows when converted to nanoseconds")
    rgb_stamps = [f["timestamp_ns"] for f in rgb]
    used: set[int] = set()
    pairs: list[dict[str, Any]] = []
    unmatched_thermal: list[str] = []

    for tf in thermal:
        target = tf["timestamp_ns"]
        i = bisect.bisect_left(rgb_stamps, target)
        left, right = i - 1, i
        chosen: int | None = None
        while left >= 0 or right < len(rgb):
            left_dist = abs(rgb_stamps[left] - target) if left >= 0 else math.inf
            right_dist = abs(rgb_stamps[right] - target) if right < len(rgb) else math.inf
            if min(left_dist, right_dist) > max_delta_ns:
                break
            if left_dist <= right_dist:  # tie: earlier RGB frame
                candidate, left = left, left - 1
            else:
                candidate, right = right, right + 1
            if candidate not in used:
                chosen = candidate
                break
        if chosen is None:
            unmatched_thermal.append(tf["id"])
            continue
        used.add(chosen)
        pairs.append({
            "rgb_id": rgb[chosen]["id"], "thermal_id": tf["id"],
            "rgb_timestamp_ns": rgb_stamps[chosen],
            "thermal_timestamp_ns": target,
            "delta_ms": (rgb_stamps[chosen] - target) / 1_000_000,
        })

    deltas = sorted(abs(p["delta_ms"]) for p in pairs)
    return {
        "method": "greedy_nearest_unique_rgb_per_thermal",
        "clock_domain": clock_domain,
        "tolerance_ms": float(tolerance_ms),
        "pairs": pairs,
        "summary": {
            "rgb_frames": len(rgb), "thermal_frames": len(thermal),
            "matched": len(pairs),
            "unmatched_rgb": len(rgb) - len(used),
            "unmatched_thermal": len(unmatched_thermal),
            "matched_thermal_fraction": len(pairs) / len(thermal) if thermal else None,
            "absolute_delta_median_ms": statistics.median(deltas) if deltas else None,
            "absolute_delta_p95_ms": _percentile(deltas, 0.95),
        },
        "unmatched_thermal_ids": unmatched_thermal,
        "limitations": [
            "timestamps must denote comparable capture instants in a shared clock domain",
            "greedy matching is not a global optimal time assignment",
            "temporal proximity does not correct motion, rolling shutter, or parallax",
            "no artificial frame interpolation or clock drift correction is performed",
        ],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON timestamp manifest")
    parser.add_argument("--output", default="reports/synchronization.json")
    args = parser.parse_args(argv)
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {
        "rgb_frames", "thermal_frames", "tolerance_ms", "clock_domain", "data_origin"
    } or data["data_origin"] not in ("simulated", "reference", "measured"):
        raise ValueError("Invalid timing manifest schema or data_origin")
    result = pair_frames(
        data["rgb_frames"], data["thermal_frames"],
        tolerance_ms=data["tolerance_ms"], clock_domain=data["clock_domain"],
    )
    result["data_origin"] = data["data_origin"]
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
                      encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
