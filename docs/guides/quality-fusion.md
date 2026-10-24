# Quality-weighted late detection fusion

The P02 quality baseline is a *Python API* for fusing already-labelled,
already-aligned detection proposals, used by the E01 command-line runner.

```python
from arc_rgbt.quality_fusion import quality_fuse_detections

rgb = [{"label": "person", "bbox": [10, 10, 20, 20], "score": 0.9}]
thermal = [{"label": "person", "bbox": [11, 10, 20, 20], "score": 0.8}]

result = quality_fuse_detections(
    rgb, thermal,
    rgb_quality=0.9,
    thermal_quality=0.4,
    min_effective_score=0.25,
    match_iou=0.5,
)
```

The `quality_fuse_detections` arguments are:

| Argument | Contract |
| --- | --- |
| `rgb_boxes`, `thermal_boxes` | Lists of `{label, bbox, score}` detections in one coordinate system |
| `rgb_quality`, `thermal_quality` | Finite numeric, not boolean, in [0,1] |
| `min_effective_score` | Common gate in [0,1], default 0.25 |
| `match_iou` | Matching IoU in (0,1], default 0.5 |

Bounding boxes use `[x, y, width, height]` with positive dimensions
and positive finite detector scores. Qualities of zero suppress
one modality completely, regardless of incoming score.

The algorithm validates inputs through the existing late-fusion
baseline, scales input scores by the externally supplied quality,
discards low-effective-score proposals and performs greedy class-matched
weighted box fusion. It does **not** alter the caller's lists.

!!! warning "Quality is not confidence calibration"
    The quality factors are externally supplied *reliability proxies*
    and can be heuristic or synthetic. Multiplying them by detector scores
    does not create calibrated posterior probabilities. The implementation
    cannot derive quality from RGB or thermal pixels, perform temporal
    association or correct misregistration.

Run the reproducible four-arm study with
[E01](../experiments/e01.md). Review the [data contract](../reference/data-contracts.md)
before importing measured proposals.
