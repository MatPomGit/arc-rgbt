"""Calibrated planar RGB–thermal warping without inventing native resolution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def _image(value: np.ndarray, label: str) -> np.ndarray:
    if (not isinstance(value, np.ndarray) or value.ndim not in (2, 3)
            or value.size == 0 or (value.ndim == 3 and value.shape[2] not in (1, 3, 4))
            or not np.issubdtype(value.dtype, np.number)
            or np.issubdtype(value.dtype, np.complexfloating)
            or not np.isfinite(value).all()):
        raise ValueError(f"{label} must be a finite real grayscale/RGB/RGBA image")
    return value.astype(np.float32)


def align_pair(
    rgb: np.ndarray, thermal: np.ndarray, rgb_to_thermal: np.ndarray, *,
    reference: str = "thermal", calibration_origin: str = "measured",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Align two images using an externally supplied calibrated planar homography.

    In thermal mode RGB is interpolated onto thermal's native sensor grid.
    In RGB mode thermal is interpolated for analysis/display; its resolution
    is not increased. Mask marks pixels with valid source image support.
    """
    a, b = _image(rgb, "RGB"), _image(thermal, "thermal")
    if reference not in ("rgb", "thermal"):
        raise ValueError("reference must be 'rgb' or 'thermal'")
    if calibration_origin not in ("measured", "simulated", "estimated"):
        raise ValueError("calibration_origin must identify provenance")
    try:
        h = np.asarray(rgb_to_thermal, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("Homography must contain real numeric values") from exc
    if h.shape != (3, 3) or not np.isfinite(h).all():
        raise ValueError("Homography must be a finite 3x3 matrix")
    if abs(np.linalg.det(h)) < 1e-12 or np.linalg.cond(h) > 1e10:
        raise ValueError("Homography must be nonsingular and well-conditioned")
    matrix = h if reference == "thermal" else np.linalg.inv(h)
    source = a if reference == "thermal" else b
    target = b if reference == "thermal" else a
    height, width = target.shape[:2]
    aligned = cv2.warpPerspective(source, matrix, (width, height),
                                  flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    # A nearest-neighbour mask can mark partially padded bilinear pixels as valid.
    # Warp unit coverage with the SAME interpolation kernel as the image.
    source_valid = np.ones(source.shape[:2], dtype=np.float32)
    coverage = cv2.warpPerspective(source_valid, matrix, (width, height),
                                   flags=cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_CONSTANT)
    valid = coverage >= 1.0 - 1e-6
    if reference == "thermal":
        rgb_aligned, thermal_aligned = aligned, b.copy()
    else:
        rgb_aligned, thermal_aligned = a.copy(), aligned
    record = {
        "method": "external_planar_homography",
        "calibration_origin": calibration_origin,
        "reference_grid": reference,
        "rgb_native_resolution_px": [int(a.shape[1]), int(a.shape[0])],
        "thermal_native_resolution_px": [int(b.shape[1]), int(b.shape[0])],
        "aligned_resolution_px": [width, height],
        "valid_overlap_fraction": float(valid.mean()),
        "thermal_upsampled_for_analysis": reference == "rgb",
        "limitations": [
            "requires independently established extrinsic calibration",
            "single homography assumes a planar scene or negligible parallax",
            "interpolation does not recover missing native thermal detail",
            "valid_overlap_mask requires full bilinear interpolation support",
        ],
    }
    return rgb_aligned, thermal_aligned, valid, record


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rgb", required=True, help="RGB image as NumPy .npy")
    parser.add_argument("--thermal", required=True, help="Thermal image as NumPy .npy")
    parser.add_argument("--homography", required=True, help="JSON 3x3 RGB-to-thermal matrix")
    parser.add_argument("--reference", choices=["rgb", "thermal"], default="thermal")
    parser.add_argument("--calibration-origin", choices=["measured", "estimated", "simulated"],
                        required=True)
    parser.add_argument("--output", default="reports/registered_pair.npz")
    args = parser.parse_args(argv)
    h = json.loads(Path(args.homography).read_text(encoding="utf-8"))
    ra, ta, mask, metadata = align_pair(
        np.load(args.rgb, allow_pickle=False), np.load(args.thermal, allow_pickle=False),
        np.asarray(h), reference=args.reference, calibration_origin=args.calibration_origin,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, rgb=ra, thermal=ta, valid=mask)
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(metadata, sort_keys=True))


if __name__ == "__main__":
    main()
