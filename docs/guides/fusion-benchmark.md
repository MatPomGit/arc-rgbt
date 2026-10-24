# Image fusion and labelled benchmarking

## FusionLab

Input image fusion expects **two finite, aligned, equally sized, two-dimensional grayscale arrays**.

```bash
fusionlab --config configs/scenarios/fusion.yaml \
  --rgb reports/native.npy --thermal reports/native.npy \
  --output reports/fused.npy
```

- `weighted` calculates a convex combination of intensities using `thermal_weight` in [0, 1].
- `gradient` selects between modalities using smoothed local Laplacian magnitudes.
- `register: true` enables **translation-only** phase-correlation registration, not camera extrinsic calibration.
- `fuse_detections` provides a separate Python-level class-matched greedy IoU box-fusion baseline, with strict score/bbox validation.

These are reference operations. Comparable RGB/LWIR intensity scales and cross-modal correspondences need their own justification; registering a thermal array does not automatically calibrate the imaging geometry.

## Bench: annotation-dependent evaluation

```bash
bench-rgbt --dataset datasets/manifests/example-labelled.json \
  --output reports/bench
```

Bench greedily matches prediction boxes to *unused* ground-truth boxes of the same class at IoU ≥ 0.5 by default. It reports **TP**, **FP**, **FN**, precision, recall and F1, then writes JSON, CSV and escaped HTML.

For `TP + FP > 0`, precision = `TP / (TP + FP)`. For `TP + FN > 0`, recall = `TP / (TP + FN)`. A zero denominator returns 0 by the current numerical convention, **not** a scientifically estimated sensitivity or precision.

Annotation completeness matters: all-negative datasets require `"annotation_status": "complete"`; the absence of positive labels alone is not proof that a dataset is fully annotated. Predictions must have finite confidence scores in [0, 1]. Bench is **not** a mean average precision (mAP) implementation.

For the E01 externally weighted detector-proposal baseline see [quality fusion](quality-fusion.md) and [E01](../experiments/e01.md).

For schema details consult [data contracts](../reference/data-contracts.md) and for interpretation consult [evidence boundaries](../concepts/evidence.md).
