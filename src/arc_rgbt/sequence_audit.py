"""Offline audit of timestamped RGB/LWIR NumPy sequences.

Checks capture files and temporal pairing, not geometric/radiometric calibration.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import shutil
import tempfile
from pathlib import Path, PurePosixPath

import numpy as np

from arc_rgbt.synchronization import pair_frames

MAX_FRAMES = 512
MAX_PIXELS = 4_000_000
MAX_BYTES = 64 * 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_path(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise ValueError("Frame paths must be nonempty relative POSIX paths")
    relative = PurePosixPath(name)
    if (relative.is_absolute() or any(part in (".", "..") for part in name.split("/"))
            or relative.suffix.lower() != ".npy"):
        raise ValueError(f"Unsafe or unsupported frame path: {name!r}")
    path = (root / str(relative)).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Frame path escapes dataset directory: {name!r}")
    if not path.is_file():
        raise FileNotFoundError(f"Missing NumPy frame: {name}")
    return path


def _check_frame(root: Path, entry: dict, modality: str) -> dict:
    path = _relative_path(root, entry["path"])
    size = path.stat().st_size
    if size <= 0 or size > MAX_BYTES:
        raise ValueError(f"Invalid frame file size for {entry['id']!r} (limit 64 MiB)")
    array = np.load(path, mmap_mode="r", allow_pickle=False)
    if not isinstance(array, np.ndarray):
        array.close()
        raise ValueError(f"Expected an uncompressed .npy array for frame {entry['id']!r}")
    if (array.size == 0 or array.ndim not in (2, 3)
            or array.shape[0] * array.shape[1] > MAX_PIXELS
            or modality == "thermal" and array.ndim != 2
            or array.ndim == 3 and array.shape[2] not in (1, 3)
            or array.dtype.kind not in "uif" or array.dtype.itemsize > 8
            or array.dtype.kind in "ui" and array.dtype.itemsize > 4):
        raise ValueError(f"Unsupported shape or dtype in frame {entry['id']!r}")
    if not np.isfinite(array).all():
        raise ValueError(f"Non-finite raw values in frame {entry['id']!r}")
    return {
        "id": entry["id"], "timestamp_ns": entry["timestamp_ns"],
        "path": entry["path"], "sha256": _sha256(path),
        "dtype": array.dtype.str, "shape": list(array.shape),
        "native_grid_wh": [int(array.shape[1]), int(array.shape[0])],
        "min_raw": float(array.min()), "max_raw": float(array.max()),
    }


def analyze(manifest: dict, root: Path, *, manifest_sha256: str | None = None) -> dict:
    """Audit a manifest against existing local frames without changing inputs."""
    expected = {"schema_version", "data_origin", "clock_domain", "tolerance_ms",
                "rgb_frames", "thermal_frames"}
    if not isinstance(manifest, dict) or set(manifest) != expected:
        raise ValueError("Manifest requires exactly the sequence-audit v1 fields")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValueError("Unsupported schema_version (expected 1)")
    if manifest["data_origin"] not in ("simulated", "reference", "measured"):
        raise ValueError("data_origin must be simulated, reference or measured")
    tol = manifest["tolerance_ms"]
    if (isinstance(tol, bool) or not isinstance(tol, (int, float))
            or not math.isfinite(tol) or not 0 <= tol <= 1000):
        raise ValueError("tolerance_ms must be finite within [0, 1000]")
    streams = (manifest["rgb_frames"], manifest["thermal_frames"])
    if (any(not isinstance(items, list) for items in streams)
            or sum(len(items) for items in streams) > MAX_FRAMES):
        raise ValueError("Sequence requires bounded lists of at most 512 total frames")
    for role, entries in zip(("rgb", "thermal"), streams, strict=True):
        for item in entries:
            if not isinstance(item, dict) or set(item) != {"id", "timestamp_ns", "path"}:
                raise ValueError(f"{role} frames require id, timestamp_ns and path")
            if (type(item["timestamp_ns"]) is not int
                    or not 0 <= item["timestamp_ns"] <= 2**63 - 1):
                raise ValueError("timestamp_ns must be a nonnegative signed-64-bit integer")
    # Timestamp schema and uniqueness are validated before reading any arrays.
    result = pair_frames(
        [{k: e[k] for k in ("id", "timestamp_ns")} for e in streams[0]],
        [{k: e[k] for k in ("id", "timestamp_ns")} for e in streams[1]],
        tolerance_ms=tol, clock_domain=manifest["clock_domain"],
    )
    base = root.resolve()
    rgb = [_check_frame(base, frame, "rgb") for frame in streams[0]]
    thermal = [_check_frame(base, frame, "thermal") for frame in streams[1]]
    rgb_by_id = {f["id"]: f for f in rgb}
    thermal_by_id = {f["id"]: f for f in thermal}
    pairs = []
    for pair in result["pairs"]:
        first = rgb_by_id[pair["rgb_id"]]
        second = thermal_by_id[pair["thermal_id"]]
        equal_grid = first["native_grid_wh"] == second["native_grid_wh"]
        pairs.append({
            **pair, "rgb_path": first["path"], "thermal_path": second["path"],
            "rgb_grid_wh": first["native_grid_wh"],
            "thermal_grid_wh": second["native_grid_wh"],
            "equal_native_grids": equal_grid,
        })
    shape_changes = {
        role: len({tuple(frame["shape"]) for frame in values}) > 1
        for role, values in (("rgb", rgb), ("thermal", thermal))
    }
    dtype_changes = {
        role: len({frame["dtype"] for frame in values}) > 1
        for role, values in (("rgb", rgb), ("thermal", thermal))
    }
    return {
        "tool": "arc-rgbt-sequence-audit", "schema_version": 1,
        "data_origin": manifest["data_origin"],
        "manifest_sha256": manifest_sha256, "clock_domain": result["clock_domain"],
        "matching_method": result["method"],
        "summary": {**result["summary"],
                    "equal_native_grid_pairs": sum(p["equal_native_grids"] for p in pairs),
                    "different_native_grid_pairs": sum(not p["equal_native_grids"] for p in pairs),
                    "shape_changed_within_stream": shape_changes,
                    "dtype_changed_within_stream": dtype_changes},
        "pairs": pairs, "rgb_frames": rgb, "thermal_frames": thermal,
        "unmatched_thermal_ids": result["unmatched_thermal_ids"],
        "limitations": [
            "Matching uses declared shared clock; no independent clock calibration is performed",
            "Greedy nearest frame pairing is not globally optimal and does not interpolate frames",
            "Equal native grids do not imply spatial registration or mutual field-of-view",
            "Raw range/dtype/shape checks do not establish sensor radiometry or detector accuracy",
            "No automatic resizing, image fusion, energy metering, "
            "or object recognition is performed",
        ],
    }


def _publish(report: dict, target: Path, stage: Path) -> None:
    (stage / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    columns = ("rgb_id", "thermal_id", "delta_ms", "rgb_path", "thermal_path",
               "rgb_grid_wh", "thermal_grid_wh", "equal_native_grids")
    with (stage / "pairs.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for pair in report["pairs"]:
            row = {name: pair[name] for name in columns}
            for field in ("rgb_id", "thermal_id", "rgb_path", "thermal_path"):
                value = str(row[field])
                if (value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@"))
                        or value.startswith(("\t", "\r", "\n"))):
                    row[field] = "'" + value
            writer.writerow(row)
    rows = "".join(
        "<tr>" + "".join("<td>" + html.escape(str(pair[name])) + "</td>" for name in columns)
        + "</tr>" for pair in report["pairs"]
    )
    summary = html.escape(json.dumps(report["summary"], indent=2, sort_keys=True))
    headers = "".join(f"<th scope='col'>{html.escape(name)}</th>" for name in columns)
    (stage / "index.html").write_text(
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>RGB–LWIR sequence audit</title>"
        "<style>body{font:16px system-ui,sans-serif;max-width:1200px;margin:2em auto;"
        "padding:0 1em}table{border-collapse:collapse;display:block;overflow-x:auto}"
        "td,th{border:1px solid #888;padding:.4em;text-align:left}"
        "pre{white-space:pre-wrap}caption{text-align:left;font-weight:600}</style>"
        "<h1>RGB–LWIR sequence audit</h1>"
        "<p>Reference timestamp matching and data-integrity checks only. "
        "No clock, geometry or radiometry calibration.</p>"
        f"<h2>Summary</h2><pre>{summary}</pre><table>"
        f"<caption>{len(report['pairs'])} paired frames</caption>"
        f"<thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"
        "<p><a href='report.json'>Complete JSON report</a> · "
        "<a href='pairs.csv'>Pair CSV</a></p></html>\n",
        encoding="utf-8",
    )
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Output directory already exists: {target}")
    stage.rename(target)


def run(manifest_path: str | Path, output: str | Path) -> dict:
    source = Path(manifest_path).resolve()
    target = Path(output).expanduser().resolve()
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Output directory already exists: {target}")
    if source.stat().st_size > 1024 * 1024:
        raise ValueError("Manifest exceeds 1 MiB")
    manifest = json.loads(source.read_text(encoding="utf-8"))
    report = analyze(manifest, source.parent, manifest_sha256=_sha256(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".rgbt-sequence-", dir=target.parent))
    try:
        _publish(report, target, staging)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return report


def demo(output: str | Path) -> dict:
    target = Path(output).expanduser().resolve()
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Output directory already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".rgbt-sequence-demo-", dir=target.parent))
    try:
        (staging / "frames").mkdir()
        rgb = []
        thermal = []
        for role, stamp_list, shape, dtype in (
            ("rgb", [0, 33_000_000, 66_000_000], (12, 16), np.float32),
            ("thermal", [4_000_000, 39_000_000, 160_000_000], (6, 8), np.uint16),
        ):
            for index, stamp in enumerate(stamp_list):
                name = f"frames/{role}-{index}.npy"
                frame = np.full(shape, index + 1, dtype=dtype)
                np.save(staging / name, frame, allow_pickle=False)
                (rgb if role == "rgb" else thermal).append({
                    "id": f"{role}-{index}", "timestamp_ns": stamp, "path": name,
                })
        manifest = {
            "schema_version": 1, "data_origin": "simulated",
            "clock_domain": "shared_monotonic_ns", "tolerance_ms": 10,
            "rgb_frames": rgb, "thermal_frames": thermal,
        }
        source = staging / "manifest.json"
        source.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        report = analyze(manifest, staging, manifest_sha256=_sha256(source))
        _publish(report, target, staging)
        return report
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", help="JSON manifest with relative local .npy frame paths")
    mode.add_argument("--demo", action="store_true", help="Generate synthetic streams and report")
    parser.add_argument("--output", default="reports/sequence-audit",
                        help="New, non-existing directory")
    args = parser.parse_args(argv)
    try:
        report = demo(args.output) if args.demo else run(args.input, args.output)
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(1, f"sequence-audit: {type(exc).__name__}: {exc}\n")
    print(json.dumps({"output": args.output, "summary": report["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
