# P04: falsifiable hypothesis

**Status:** CORE PLANNED. Draft hypothesis, not preregistered.

**H1.** A separately trained failure-aware decision policy lowers worst-condition missed detection rate compared with fixed late fusion at a predeclared FP/frame ceiling and minimum coverage on held-out corrupted and physically degraded scenes.

**H0.** No improvement in worst-condition missed-detection rate at matched FP/frame and coverage.

## Outcomes

- **Primary:** Worst-condition miss rate at a locked false-positive-per-frame ceiling and minimum prediction coverage, grouped by independent scene or sequence.
- **Secondary:** Risk–coverage AURC, detection AP, ECE, abstention rate, measured inference overhead and failure-detection AUROC.
- **Independent unit:** held-out physical device, independent capture scene/session or sequence according to the study; adjacent frames are never independent statistical replications.
- **Statistical plan:** freeze contrast, baseline, quality/false-alarm operating point, uncertainty method and minimum meaningful effect before testing. Report paired scene/sequence/device-cluster intervals and negative/null results; no post-hoc threshold selection.

## Distinctness

P04 measures risk under failure, not average P02 fusion mAP. Merge into P02 if no defensible independent risk outcome is demonstrated.

The [protocol](../protocol/README.md) contains admissibility and STOP/GO conditions. Common [evidence limits](../../../docs/concepts/evidence.md) apply.
