"""Deterministic, metadata-preserving native-resolution image degradation."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

from arc_rgbt.common import exact_keys, load_yaml, positive_integer, save_json


def degrade(
    image: np.ndarray, *, width_px: int, height_px: int, optical_sigma_px: float = 0,
    noise_sigma: float = 0, motion_length_px: int = 1, seed: int = 0,
) -> tuple[np.ndarray, dict]:
    if (not isinstance(image, np.ndarray) or image.ndim not in (2, 3)
            or image.size == 0 or not np.issubdtype(image.dtype, np.number)
            or np.issubdtype(image.dtype, np.complexfloating)
            or (image.ndim == 3 and image.shape[2] not in (1, 3, 4))):
        raise ValueError("Image must be a nonempty real grayscale/RGB/RGBA array")
    for name, value in (("width_px", width_px), ("height_px", height_px),
                        ("motion_length_px", motion_length_px)):
        positive_integer(value, name)
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    for name, value in (("optical_sigma_px", optical_sigma_px), ("noise_sigma", noise_sigma)):
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not np.isfinite(value) or value < 0):
            raise ValueError(f"{name} must be non-negative and finite")
    if not np.isfinite(image).all():
        raise ValueError("Image must contain only finite intensities")
    if np.any(image < 0) or np.any(image > 1):
        raise ValueError("Input intensities must be normalized to [0, 1]; no implicit clipping")
    work = image.astype(np.float32).copy()
    if optical_sigma_px:
        sigma = (optical_sigma_px, optical_sigma_px) + ((0,) if work.ndim == 3 else ())
        work = gaussian_filter(work, sigma=sigma, mode="reflect")
    if motion_length_px > 1:
        kernel = np.full((1, motion_length_px), 1 / motion_length_px, dtype=np.float32)
        work = cv2.filter2D(work, -1, kernel, borderType=cv2.BORDER_REFLECT)
    native = cv2.resize(work, (width_px, height_px), interpolation=cv2.INTER_AREA)
    if noise_sigma:
        native += (
            np.random.default_rng(seed).normal(0, noise_sigma, native.shape).astype(np.float32)
        )
    native = np.clip(native, 0, 1).astype(np.float32)
    return native, {"data_origin": "simulated", "native_resolution_px": [width_px, height_px],
                    "source_resolution_px": [image.shape[1], image.shape[0]],
                    "optical_sigma_source_px": optical_sigma_px,
                    "noise_sigma_normalized": noise_sigma,
                    "motion_length_source_px": motion_length_px,
                    "motion_kernel": "horizontal_uniform_1d", "seed": seed,
                    "input_intensity_range": "normalized_0_1",
                    "noise_output_clipping": "unit_interval",
                    "interpolated_resolution_px": None}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--input", required=True, help="NumPy .npy array normalized to [0, 1]")
    p.add_argument("--output", default="reports/degradesim.npy")
    a = p.parse_args(argv)
    params = load_yaml(a.config)
    exact_keys(params, {"width_px", "height_px"},
               {"optical_sigma_px", "noise_sigma", "motion_length_px", "seed"})
    native, record = degrade(np.load(a.input, allow_pickle=False), **params)
    out = Path(a.output)
    if out.suffix not in ("", ".npy"):
        p.error("--output must be a .npy path or have no extension")
    if not out.suffix:
        out = out.with_suffix(".npy")
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(out, native, allow_pickle=False)
    print(save_json(str(out) + ".json", record))


if __name__ == "__main__":
    main()
