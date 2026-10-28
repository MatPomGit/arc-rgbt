# P07: experimental protocol and evidence gate

**Status:** OPTIONAL HOLD; empirical work must not start before GATE PASS. Version 0.1.0, 2026-10-28.

## Question and scientific boundary

Can an on-device policy switch modality/resolution and save measured energy while preserving predeclared perception constraints?

**Non-overlap:** P07 adds a dynamic control policy and measured energy saving. Static quantization/Pareto comparisons remain in P03, not a new paper.

## Data prerequisites

Actual target hardware with independently measured power, controllable camera modes and licensed labelled real sequences; host-only estimates do not qualify.

**Source screening:** No hardware selection or device energy measurements have yet passed review.

Record original source/version, licences and ethics/privacy conditions, native spectral bands and image grids, annotations, calibration/timing status, independent session splits and SHA-256 for inputs before acquisition or reuse. Do not commit licensed image archives, personal data or weights.

## Design and controls

Compare fixed RGB, fixed LWIR, fixed dual-sensor and adaptive policy under matched workloads and full end-to-end instrumented power accounting. Predeclare energy budget and minimum quality.

**Primary outcome:** Measured joules per independently evaluated scene/sequence, including sensing, preprocessing, fusion, control and idle-reference accounting.

**Secondary outcomes:** Per-frame p50/p95/p99 latency, memory, thermal throttling, switch counts, model AP and worst-stratum recall.

## Before confirmatory analysis

- [ ] Complete instrumented P03 fixed-pipeline benchmark with validated sensor and power baseline.
- [ ] Demonstrate actual controllable capture/computation modes and quantify switching overhead.
- [ ] Preregister power measurement method, perception thresholds and independently repeated-scene evaluation.
- [ ] Freeze full hypotheses, null, decision rules, baselines, independent split and exclusion policy.
- [ ] Verify reproducibility with code SHA, data/annotation release hashes and test leakage audit.
- [ ] Report physical measurements separately from synthetic E00–E02 or host benchmarks.
- [ ] Document negative and null results, scene-level confidence intervals and independent novelty review.

## GO/NO-GO

**G07 OPTIONAL HOLD: P03 named-device RAM/flash/latency/energy baseline PASS; instrumented adaptive switching and matched-perception comparison PASS; independent non-overlap/novelty review PASS.**

Until all conditions pass and PROJECT_STATE.yaml is explicitly reviewed and updated, this publication must remain OPTIONAL HOLD. Planning text is not authorization to activate acquisition, benchmarking or manuscript submission.

**If the independent claim cannot be supported:** P07 adds a dynamic control policy and measured energy saving. Static quantization/Pareto comparisons remain in P03, not a new paper.

See [hypothesis](../hypotheses/README.md), [dataset admissions](../../../docs/experiments/datasets.md), [measurement standards](../../../docs/guides/evaluation-requirements.md) and [portfolio controls](../../../AUTOPILOT_PLAN.md).
