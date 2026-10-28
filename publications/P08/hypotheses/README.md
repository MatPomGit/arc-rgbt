# P08: falsifiable hypothesis

**Status:** OPTIONAL HOLD. Draft hypothesis, not preregistered.

**H1.** Propagating measured calibration and exposure-clock uncertainty improves held-out coverage/calibration of predicted detection-failure risk relative to deterministic P02 registration at a locked operating point.

**H0.** No improvement in measured risk-bound coverage/calibration against deterministic registration.

## Outcomes

- **Primary:** Observed coverage and calibration error of preregistered detection-risk/error bounds on held-out physical calibration and scene sessions.
- **Secondary:** Prediction-bound width, risk–coverage AURC, recall at fixed FP/frame, reprojection-error distribution and latency.
- **Independent unit:** held-out physical device, independent capture scene/session or sequence according to the study; adjacent frames are never independent statistical replications.
- **Statistical plan:** freeze contrast, baseline, quality/false-alarm operating point, uncertainty method and minimum meaningful effect before testing. Report paired scene/sequence/device-cluster intervals and negative/null results; no post-hoc threshold selection.

## Distinctness

P08 tests calibrated predictive risk bounds; simple synthetic jitter, mean reprojection error or E02 overlap remain P02 methods.

The [protocol](../protocol/README.md) contains admissibility and STOP/GO conditions. Common [evidence limits](../../../docs/concepts/evidence.md) apply.
