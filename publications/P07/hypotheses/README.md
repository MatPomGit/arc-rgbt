# P07: falsifiable hypothesis

**Status:** OPTIONAL HOLD. Draft hypothesis, not preregistered.

**H1.** On named, instrumented hardware, an adaptive RGB/LWIR capture and inference policy lowers measured joules per scene versus the best fixed P03 pipeline at matched recall, FP/frame and end-to-end latency limits.

**H0.** No measured energy saving under the same perception and service constraints.

## Outcomes

- **Primary:** Measured joules per independently evaluated scene/sequence, including sensing, preprocessing, fusion, control and idle-reference accounting.
- **Secondary:** Per-frame p50/p95/p99 latency, memory, thermal throttling, switch counts, model AP and worst-stratum recall.
- **Independent unit:** held-out physical device, independent capture scene/session or sequence according to the study; adjacent frames are never independent statistical replications.
- **Statistical plan:** freeze contrast, baseline, quality/false-alarm operating point, uncertainty method and minimum meaningful effect before testing. Report paired scene/sequence/device-cluster intervals and negative/null results; no post-hoc threshold selection.

## Distinctness

P07 adds a dynamic control policy and measured energy saving. Static quantization/Pareto comparisons remain in P03, not a new paper.

The [protocol](../protocol/README.md) contains admissibility and STOP/GO conditions. Common [evidence limits](../../../docs/concepts/evidence.md) apply.
