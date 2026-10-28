# P04: experimental protocol and evidence gate

**Status:** CORE PLANNED; data and methods not yet empirically validated. Version 0.1.0, 2026-10-28.

## Question and scientific boundary

Does explicit modality-failure monitoring and selective prediction lower missed detections under missing/degraded RGB or LWIR at matched false-positive and minimum-coverage budgets?

**Non-overlap:** P04 measures risk under failure, not average P02 fusion mAP. Merge into P02 if no defensible independent risk outcome is demonstrated.

## Data prerequisites

Licensed, fully labelled RGB/LWIR positive and negative scenes with documented native grids, acquisition sources and corruption definitions; simulated corruption must be distinguished from measured sensor failure.

**Source screening:** Use documented RGB/LWIR candidates after licences and annotations are independently verified.

Record original source/version, licences and ethics/privacy conditions, native spectral bands and image grids, annotations, calibration/timing status, independent session splits and SHA-256 for inputs before acquisition or reuse. Do not commit licensed image archives, personal data or weights.

## Design and controls

Lock RGB-only, LWIR-only, fixed fusion, adaptive P02 fusion and failure-aware selection baselines. Test RGB dropout, LWIR dropout, stale frames, blur, low contrast and unchanged control frames at equal detector, scene and alert conditions; hold out independent scenes.

**Primary outcome:** Worst-condition miss rate at a locked false-positive-per-frame ceiling and minimum prediction coverage, grouped by independent scene or sequence.

**Secondary outcomes:** Risk–coverage AURC, detection AP, ECE, abstention rate, measured inference overhead and failure-detection AUROC.

## Before confirmatory analysis

- [ ] Predeclare fault categories and severity levels, FP/frame threshold and minimum prediction coverage.
- [ ] Train reliability estimators on development data only; freeze all thresholds before test.
- [ ] Audit negative-frame completeness, report paired scene-clustered uncertainty and all failed operating points.
- [ ] Freeze full hypotheses, null, decision rules, baselines, independent split and exclusion policy.
- [ ] Verify reproducibility with code SHA, data/annotation release hashes and test leakage audit.
- [ ] Report physical measurements separately from synthetic E00–E02 or host benchmarks.
- [ ] Document negative and null results, scene-level confidence intervals and independent novelty review.

## GO/NO-GO

**G04: independent scene-level detection labels, frozen fault strata, held-out reliability estimator and matched operational baselines; synthetic failures alone do not support field-safety claims.**

**If the independent claim cannot be supported:** P04 measures risk under failure, not average P02 fusion mAP. Merge into P02 if no defensible independent risk outcome is demonstrated.

See [hypothesis](../hypotheses/README.md), [dataset admissions](../../../docs/experiments/datasets.md), [measurement standards](../../../docs/guides/evaluation-requirements.md) and [portfolio controls](../../../AUTOPILOT_PLAN.md).
