"""Quality-aware late fusion reference for paired RGB and thermal detections.

Quality weights are externally specified reliability proxies, NOT calibrated
probabilities. Fusion does not estimate image quality or recognize objects.
"""

from __future__ import annotations

import math
from typing import Any

from arc_rgbt.fusionlab import fuse_detections


def _unit(value: Any, name: str) -> float:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not 0 <= value <= 1):
        raise ValueError(f"{name} must be a finite numeric value in [0,1]")
    return float(value)


def quality_fuse_detections(
    rgb_boxes: list[dict], thermal_boxes: list[dict], *,
    rgb_quality: float, thermal_quality: float,
    min_effective_score: float = 0.25, match_iou: float = 0.5,
) -> list[dict]:
    """Apply modality reliability to scored proposals, then perform box fusion.

    Input boxes use native common-coordinate [x,y,w,h] geometry, the same
    class labels and uncalibrated detector scores in (0,1]. Effective scores
    are score*quality and must not be interpreted as posterior probabilities.
    Output drops proposals below a common gate and leaves inputs unchanged.
    With unit qualities and zero gate this reproduces existing late fusion.
    """
    rq = _unit(rgb_quality, "rgb_quality")
    tq = _unit(thermal_quality, "thermal_quality")
    gate = _unit(min_effective_score, "min_effective_score")
    # Shared validator rejects malformed boxes and IoU before any multiplication.
    fuse_detections(rgb_boxes, thermal_boxes, threshold=match_iou)

    def adjust(boxes: list[dict], quality: float) -> list[dict]:
        result = []
        for item in boxes:
            effective = float(item["score"]) * quality
            if effective > 0 and effective >= gate:
                result.append({
                    "label": item["label"],
                    "bbox": list(item["bbox"]),
                    "score": effective,
                })
        return result

    return fuse_detections(adjust(rgb_boxes, rq), adjust(thermal_boxes, tq),
                           threshold=match_iou)
