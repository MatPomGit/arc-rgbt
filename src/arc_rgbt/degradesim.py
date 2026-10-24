"""Deterministic, metadata-preserving native-resolution image degradation."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from arc_rgbt.common import exact_keys, load_yaml, save_json


def degrade(image: np.ndarray, *, width_px: int, height_px: int, optical_sigma_px: float = 0,
            noise_sigma: float = 0, motion_length_px: int = 1, seed: int = 0) -> tuple[np.ndarray, dict]:
    if image.ndim not in (2, 3) or image.size == 0 or not np.issubdtype(image.dtype, np.number):
        raise ValueError("Image must be a nonempty numeric grayscale or multi-channel array")
    if min(width_px, height_px, motion_length_px) <= 0 or min(optical_sigma_px, noise_sigma) < 0:
        raise ValueError("Invalid resolution or degradation parameters")
    if not np.isfinite(image).all() or not np.isfinite([optical_sigma_px, noise_sigma]).all():
        raise ValueError("Image and parameters must be finite")
    work = image.astype(np.float32).copy()
    if optical_sigma_px:
        work = cv2.GaussianBlur(work, (0, 0), optical_sigma_px)
    if motion_length_px > 1:
        kernel = np.zeros((motion_length_px, motion_length_px), dtype=np.float32)
        kernel[motion_length_px // 2, :] = 1 / motion_length_px
        work = cv2.filter2D(work, -1, kernel, borderType=cv2.BORDER_REFLECT)
    native = cv2.resize(work, (width_px, height_px), interpolation=cv2.INTER_AREA)
    if noise_sigma:
        native += np.random.default_rng(seed).normal(0, noise_sigma, native.shape).astype(np.float32)
    native = np.clip(native, 0, 1).astype(np.float32)
    return native, {"data_origin": "simulated", "native_resolution_px": [width_px, height_px],
                    "source_resolution_px": [image.shape[1], image.shape[0]],
                    "optical_sigma_source_px": optical_sigma_px, "noise_sigma_normalized": noise_sigma,
                    "motion_length_source_px": motion_length_px, "seed": seed,
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
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(out, native, allow_pickle=False)
    print(save_json(str(out) + ".json", record))


if __name__ == "__main__":
    main()
