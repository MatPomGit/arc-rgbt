# P06: falsifiable hypothesis

**Status:** CORE PLANNED. Draft hypothesis, not preregistered.

**H1.** On independent paired RGB/LWIR sequences with track-ID labels, modality-aware association improves HOTA against frozen-detection single-modality and fixed-fusion association baselines in predeclared occlusion/dropout strata.

**H0.** No HOTA improvement when detections, sequences and association budget are matched.

## Outcomes

- **Primary:** HOTA on independent annotated sequences, including predeclared occlusion and temporary modality-loss strata.
- **Secondary:** IDF1, identity switches, fragmentation, association accuracy, recall, FP/frame and full-pipeline latency.
- **Independent unit:** held-out physical device, independent capture scene/session or sequence according to the study; adjacent frames are never independent statistical replications.
- **Statistical plan:** freeze contrast, baseline, quality/false-alarm operating point, uncertainty method and minimum meaningful effect before testing. Report paired scene/sequence/device-cluster intervals and negative/null results; no post-hoc threshold selection.

## Distinctness

Temporal association is separate from P01–P05 frame detection. No tracking claims from synthetic rectangle-overlap E02.

The [protocol](../protocol/README.md) contains admissibility and STOP/GO conditions. Common [evidence limits](../../../docs/concepts/evidence.md) apply.
