"""Offline, provenance-bearing preview of a raw 2D thermal/intensity NumPy frame.

A visualization does not convert raw sensor counts into degrees or radiance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import tempfile
from pathlib import Path

import cv2
import numpy as np

MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_PIXELS = 4_000_000


def preview(image: np.ndarray, *, percentiles: tuple[float, float] = (2.0, 98.0),
            display_range: tuple[float, float] | None = None) -> tuple[np.ndarray, dict]:
    """Produce an 8-bit *display only* image without modifying the source array."""
    if (not isinstance(image, np.ndarray) or image.ndim != 2 or not image.size
            or image.size > MAX_PIXELS or image.dtype.kind not in "uif"
            or image.dtype.itemsize > 8 or (image.dtype.kind in "ui" and image.dtype.itemsize > 4)
            or not np.isfinite(image).all()):
        raise ValueError("Expected finite, real 2D numeric array (1..4 million pixels)")
    if (not isinstance(percentiles, tuple) or len(percentiles) != 2
            or any(isinstance(v, bool) or not isinstance(v, (int, float))
                   or not math.isfinite(v) for v in percentiles)
            or not 0 <= percentiles[0] < percentiles[1] <= 100):
        raise ValueError("percentiles must satisfy 0 <= lower < upper <= 100")
    if display_range is not None and (
        not isinstance(display_range, tuple) or len(display_range) != 2
        or any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(v) for v in display_range)
        or display_range[0] >= display_range[1]
    ):
        raise ValueError("display_range must contain two finite increasing numbers")
    raw = image.astype(np.float64)
    low, high = (np.percentile(raw, percentiles) if display_range is None
                 else display_range)
    minimum, maximum = float(raw.min()), float(raw.max())
    if not math.isfinite(low) or not math.isfinite(high):
        raise ValueError("Computed display bounds are non-finite")
    constant = high <= low
    if constant:
        view = np.full(image.shape, 127, dtype=np.uint8)
    else:
        scale = max(abs(low), abs(high), 1.0)
        denominator = high / scale - low / scale
        if denominator <= 0:
            raise ValueError("Display range too narrow for stable float64 rendering")
        scaled = np.clip((raw / scale - low / scale) / denominator, 0, 1)
        view = np.rint(scaled * 255).astype(np.uint8)
    metadata = {
        "data_origin": "user_supplied_unverified", "raw_dtype": image.dtype.str,
        "raw_shape_yx": list(image.shape), "raw_min": minimum, "raw_max": maximum,
        "display_low": float(low), "display_high": float(high),
        "display_method": "explicit_range" if display_range is not None else "percentile",
        "requested_percentiles": list(percentiles) if display_range is None else None,
        "display_constant": bool(constant),
        "pixels_below_display_range": int(np.count_nonzero(raw < low)),
        "pixels_above_display_range": int(np.count_nonzero(raw > high)),
        "output_dtype": "uint8", "raw_values_preserved_in_source": True,
        "calibration": "not_provided", "physical_units": "unknown",
        "limitations": [
            "PNG is a lossy visualization of input sample values, not quantitative thermal data",
            "No conversion to temperature or radiance without independently supplied calibration",
            "Percentile normalization is image-relative and not comparable across frames",
        ],
    }
    return view, metadata


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(source: str | Path, output: str | Path, *,
        percentiles: tuple[float, float] = (2.0, 98.0),
        display_range: tuple[float, float] | None = None) -> dict:
    """Publish preview PNG and audit metadata only when both are complete."""
    source = Path(source)
    target = Path(output).expanduser().resolve()
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Output directory exists: {target}")
    if source.suffix.lower() != ".npy":
        raise ValueError("--input must be a NumPy .npy file")
    if not 0 < source.stat().st_size <= MAX_FILE_BYTES:
        raise ValueError("Input must be a nonempty .npy file <= 64 MiB")
    raw = np.load(source, mmap_mode="r", allow_pickle=False)
    picture, metadata = preview(raw, percentiles=percentiles, display_range=display_range)
    metadata["source_name"] = source.name
    metadata["source_sha256"] = _sha256(source)
    ok, encoded = cv2.imencode(".png", picture)
    if not ok:
        raise OSError("Cannot encode thermal preview PNG")
    target.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".rgbt-thermal-preview-", dir=target.parent))
    try:
        (staged / "preview.png").write_bytes(encoded.tobytes())
        (staged / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"Output directory exists: {target}")
        staged.rename(target)
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    return metadata


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Original 2D NumPy .npy, e.g. uint16")
    parser.add_argument("--output", default="reports/thermal-preview",
                        help="New, non-existing output directory")
    bounds = parser.add_mutually_exclusive_group()
    bounds.add_argument("--range", dest="display_range", nargs=2, type=float,
                        metavar=("LOW", "HIGH"), help="Explicit display range in raw units")
    bounds.add_argument("--percentiles", nargs=2, type=float, default=(2.0, 98.0),
                        metavar=("LOW", "HIGH"), help="Image-relative display stretch")
    args = parser.parse_args(argv)
    try:
        meta = run(args.input, args.output, percentiles=tuple(args.percentiles),
                   display_range=tuple(args.display_range) if args.display_range else None)
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(1, f"thermal-preview: {exc}\n")
    print(json.dumps({"output": str(args.output), "raw_dtype": meta["raw_dtype"],
                      "display_range": [meta["display_low"], meta["display_high"]]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
