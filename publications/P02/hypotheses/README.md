# P02 hypotheses

Register falsifiable hypotheses, null hypotheses, outcome definitions, preregistration status and any protocol amendments for Adaptive and Temporal RGB–Thermal Fusion. See the programme register in `research/hypotheses`.

## Proposed H1 (not empirically tested)

At a matched fixed false-alarm budget, independently estimated frame-level
modality reliability weighting improves recall over equal-quality late fusion
for degraded low-resolution thermal data, controlling for RGB detector and
identical physical scenes.

- Null: no improvement in recall at matched false-alarm budget.
- Explanatory E01 input currently uses **synthetically stipulated** weights.
  These weights do not constitute an independent estimator.
- Predeclare all quality estimators, confidence calibrations, IoU thresholds,
  and split policies using training data only.
- Hold out complete sequences/scene sources; do not split adjacent frames
  between training and test sets.
- Use sequence/flight-level resampling and paired effect estimates, not
  single-frame IID confidence intervals.
- Explicitly report sensor resolution, bit depth, temporal skew, and
  latency/RAM/energy only when measured on identified hardware.
