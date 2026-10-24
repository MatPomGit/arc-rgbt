# E01: Quality-aware late fusion benchmark

This is an offline reference protocol supporting P02, with four methods:
`rgb_only`, `thermal_only`, `fixed_fusion` and `quality_aware_fusion`.
All methods use the same image/scene annotations, class labels and IoU.

## Input contract

Input is JSON containing `experiment: E01`, `data_origin`,
`quality_origin`, `annotation_status: complete`, `config` and `frames`.
Each frame has `id`, `ground_truth`, `rgb_predictions`,
`thermal_predictions` and `quality: {rgb,thermal}`. BBoxes are
`[x,y,width,height]` in one externally aligned common coordinate frame.
Modality quality factors and detection scores must be finite in [0,1].
All predictions must have strictly positive score, nonempty class label
and valid positive-size bounding box.

The quality method multiplies detector scores by externally provided
reliability factors, discards proposals below a **shared** effective-score
threshold and invokes the existing greedy class-aware late box-fusion method.
Fixed fusion applies the same threshold with qualities both set to one.
This is a score heuristic and is NOT probability calibration.

## Run

```bash
arc-rgbt-e01 --dataset datasets/manifests/e01-synthetic-quality.json \
  --output reports/E01
python -m pytest -q tests/test_quality_fusion.py tests/test_e01.py
```

Reports: `reports/E01/manifest.json` and `metrics.csv` with provenance
and source input hash. Generated results must not be committed as evidence.

## Research quality boundaries

The committed synthetic scenario was **hand-designed to show behavior**;
its comparative metrics are not a publication finding, empirical sensor
benchmark, proof of human/vehicle recognition or evidence of improvement.
For a real P02 study use independently calibrated, held-out data and
non-oracle sensor-quality estimates, stratified by resolution, motion,
thermal contrast and time offset. Lock thresholds and split by scene/flight;
evaluate at predeclared false-alarm budgets and include uncertainty intervals.
Do not interpret absent positives as measured sensitivity. More complete AP
and confidence calibration remain planned.
