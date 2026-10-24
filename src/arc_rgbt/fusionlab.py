"""Reference translational registration, early image fusion and late box fusion."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from arc_rgbt.common import exact_keys, load_yaml, save_json


def _pair(rgb: np.ndarray, thermal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if (not isinstance(rgb, np.ndarray) or not isinstance(thermal, np.ndarray)
            or rgb.ndim != 2 or thermal.ndim != 2 or rgb.shape != thermal.shape
            or not all(np.issubdtype(x.dtype, np.number)
                       and not np.issubdtype(x.dtype, np.complexfloating)
                       for x in (rgb, thermal))):
        raise ValueError("Provide two real aligned grayscale arrays of identical shape")
    if not (np.isfinite(rgb).all() and np.isfinite(thermal).all()):
        raise ValueError("Images must be finite")
    return rgb.astype(np.float32), thermal.astype(np.float32)


def register_translation(reference: np.ndarray, moving: np.ndarray) -> tuple[np.ndarray, dict]:
    a, b = _pair(reference, moving)
    (dx, dy), response = cv2.phaseCorrelate(a, b)
    matrix = np.float32([[1, 0, -dx], [0, 1, -dy]])
    aligned = cv2.warpAffine(b, matrix, (a.shape[1], a.shape[0]))
    return aligned, {"translation_applied_px": [-dx, -dy], "phase_response": response,
                     "model": "translation_only", "data_origin": "reference_algorithm"}


def fuse_images(rgb: np.ndarray, thermal: np.ndarray, method: str = "weighted",
                thermal_weight: float = 0.5) -> np.ndarray:
    a, b = _pair(rgb, thermal)
    if (isinstance(thermal_weight, bool) or not isinstance(thermal_weight, (int, float))
            or not np.isfinite(thermal_weight) or not 0 <= thermal_weight <= 1):
        raise ValueError("thermal_weight must be a finite number within [0,1]")
    if method == "weighted":
        return ((1 - thermal_weight) * a + thermal_weight * b).astype(np.float32)
    if method == "gradient":
        # Local gradient energy chooses the higher-contrast modality per pixel.
        energy_a = cv2.GaussianBlur(np.abs(cv2.Laplacian(a, cv2.CV_32F)), (5, 5), 0)
        energy_b = cv2.GaussianBlur(np.abs(cv2.Laplacian(b, cv2.CV_32F)), (5, 5), 0)
        return np.where(energy_b > energy_a, b, a).astype(np.float32)
    raise ValueError("Unknown early fusion method")


def _iou(a: list[float], b: list[float]) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[0] + a[2], b[0] + b[2]), min(a[1] + a[3], b[1] + b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = a[2] * a[3] + b[2] * b[3] - inter
    return inter / union if union > 0 else 0.0


def fuse_detections(rgb_boxes: list[dict], thermal_boxes: list[dict],
                    threshold: float = 0.5) -> list[dict]:
    """Greedy class-matched confidence-weighted box fusion; inputs not mutated."""
    if (isinstance(threshold, bool) or not isinstance(threshold, (int, float))
            or not np.isfinite(threshold) or not 0 < threshold <= 1):
        raise ValueError("Invalid IoU threshold")
    if not isinstance(rgb_boxes, list) or not isinstance(thermal_boxes, list):
        raise ValueError("Detections must be lists")
    for box in [*rgb_boxes, *thermal_boxes]:
        if not isinstance(box, dict) or set(box) != {"bbox", "label", "score"}:
            raise ValueError("Detection must contain bbox, label and score")
        coords, score, label = box["bbox"], box["score"], box["label"]
        if (not isinstance(coords, list) or len(coords) != 4
                or any(isinstance(v, bool) or not isinstance(v, (int, float))
                       or not np.isfinite(v) for v in coords)
                or min(coords[2:]) <= 0
                or not isinstance(label, str) or not label
                or isinstance(score, bool) or not isinstance(score, (int, float))
                or not np.isfinite(score) or not 0 < score <= 1):
            raise ValueError("Invalid detection bbox, label or score")
    used: set[int] = set()
    output: list[dict] = []
    for a in sorted(rgb_boxes, key=lambda box: -box["score"]):
        candidates = [(i, _iou(a["bbox"], b["bbox"]))
                      for i, b in enumerate(thermal_boxes)
                      if i not in used and a["label"] == b["label"]]
        i, overlap = max(candidates, key=lambda pair: pair[1], default=(-1, -1))
        if overlap >= threshold:
            b = thermal_boxes[i]
            used.add(i)
            wa, wb = float(a["score"]), float(b["score"])
            if wa + wb <= 0:
                raise ValueError("Box scores must be positive for weighted fusion")
            bbox = [(wa * x + wb * y) / (wa + wb)
                    for x, y in zip(a["bbox"], b["bbox"], strict=True)]
            output.append({"bbox": bbox, "score": max(wa, wb), "label": a["label"]})
        else:
            output.append(dict(a))
    output.extend(dict(box) for i, box in enumerate(thermal_boxes) if i not in used)
    return output


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rgb", required=True, help="Grayscale .npy")
    p.add_argument("--thermal", required=True, help="Grayscale .npy")
    p.add_argument("--config", help="Optional image-fusion YAML profile")
    p.add_argument("--method", choices=["weighted", "gradient"], default=None)
    p.add_argument("--register", action="store_true")
    p.add_argument("--output", default="reports/fusionlab.npy")
    a = p.parse_args(argv)
    config = load_yaml(a.config) if a.config else {}
    exact_keys(config, set(), {"method", "thermal_weight", "register"})
    method = a.method or config.get("method", "weighted")
    weight = config.get("thermal_weight", 0.5)
    do_register = a.register or config.get("register", False)
    if not isinstance(do_register, bool):
        raise ValueError("register must be a boolean")
    rgb, thermal = np.load(a.rgb, allow_pickle=False), np.load(a.thermal, allow_pickle=False)
    reg = None
    if do_register:
        thermal, reg = register_translation(rgb, thermal)
    fused = fuse_images(rgb, thermal, method, weight)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(out, fused, allow_pickle=False)
    save_json(str(out) + ".json", {"method": method, "thermal_weight": weight,
                                   "registration": reg,
                                   "fusion_level": "image", "data_origin": "reference_algorithm"})
    print(out)


if __name__ == "__main__":
    main()
