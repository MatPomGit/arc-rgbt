# P08: experimental protocol and evidence gate

**Status:** OPTIONAL HOLD; empirical work must not start before GATE PASS. Version 0.1.0, 2026-10-28.

## Question and scientific boundary

Can independently measured space/time calibration uncertainty yield valid out-of-sample detection-risk bounds?

**Non-overlap:** P08 tests calibrated predictive risk bounds; simple synthetic jitter, mean reprojection error or E02 overlap remain P02 methods.

## Data prerequisites

Physical RGB/LWIR paired measurements with independent calibration targets/ground-truth point correspondences, exposure clock evidence, valid masks and detection labels.

**Source screening:** A paired image directory is not evidence of physical exposure synchronization or registration uncertainty.

Record original source/version, licences and ethics/privacy conditions, native spectral bands and image grids, annotations, calibration/timing status, independent session splits and SHA-256 for inputs before acquisition or reuse. Do not commit licensed image archives, personal data or weights.

## Design and controls

Calibrate camera intrinsics/extrinsics and time-offset uncertainty on independent sessions. Propagate uncertainty to detection association; compare point-registration, naive perturbation and uncertainty-aware methods on untouched sessions.

**Primary outcome:** Observed coverage and calibration error of preregistered detection-risk/error bounds on held-out physical calibration and scene sessions.

**Secondary outcomes:** Prediction-bound width, risk–coverage AURC, recall at fixed FP/frame, reprojection-error distribution and latency.

## Before confirmatory analysis

- [ ] Measure independent physical reprojection residuals and exposure-time skew/drift.
- [ ] Freeze predicted coverage target, error model and out-of-sample acquisition split.
- [ ] Audit observed bound coverage, uncalibrated cases, negative controls and overlap with P02.
- [ ] Freeze full hypotheses, null, decision rules, baselines, independent split and exclusion policy.
- [ ] Verify reproducibility with code SHA, data/annotation release hashes and test leakage audit.
- [ ] Report physical measurements separately from synthetic E00–E02 or host benchmarks.
- [ ] Document negative and null results, scene-level confidence intervals and independent novelty review.

## GO/NO-GO

**G08 OPTIONAL HOLD: measured P02 geometry/clock uncertainty PASS; independent held-out error-bound coverage PASS; distinct risk-prediction novelty review PASS.**

Until all conditions pass and PROJECT_STATE.yaml is explicitly reviewed and updated, this publication must remain OPTIONAL HOLD. Planning text is not authorization to activate acquisition, benchmarking or manuscript submission.

**If the independent claim cannot be supported:** P08 tests calibrated predictive risk bounds; simple synthetic jitter, mean reprojection error or E02 overlap remain P02 methods.

See [hypothesis](../hypotheses/README.md), [dataset admissions](../../../docs/experiments/datasets.md), [measurement standards](../../../docs/guides/evaluation-requirements.md) and [portfolio controls](../../../AUTOPILOT_PLAN.md).
