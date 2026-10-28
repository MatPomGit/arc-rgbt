# P05: falsifiable hypothesis

**Status:** CORE PLANNED. Draft hypothesis, not preregistered.

**H1.** A predeclared lightweight modality/sensor normalization or unsupervised adaptation rule reduces out-of-domain AP loss against an otherwise identical source-only model on held-out sensor-domain cohorts.

**H0.** No improvement in out-of-domain AP loss on independent source/device groups.

## Outcomes

- **Primary:** Out-of-domain AP drop relative to in-domain source performance, with independent device/domain as the test group.
- **Secondary:** Recall at matched FP/frame, ECE, per-device effect and inference overhead; source-group bootstrap intervals.
- **Independent unit:** held-out physical device, independent capture scene/session or sequence according to the study; adjacent frames are never independent statistical replications.
- **Statistical plan:** freeze contrast, baseline, quality/false-alarm operating point, uncertainty method and minimum meaningful effect before testing. Report paired scene/sequence/device-cluster intervals and negative/null results; no post-hoc threshold selection.

## Distinctness

Resizing frames from one device does not establish cross-sensor transfer. P05 studies external validity, not P01 pixel-footprint or P02 fusion gain.

The [protocol](../protocol/README.md) contains admissibility and STOP/GO conditions. Common [evidence limits](../../../docs/concepts/evidence.md) apply.
