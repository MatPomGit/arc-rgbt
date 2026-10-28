# P05: experimental protocol and evidence gate

**Status:** CORE PLANNED; data and methods not yet empirically validated. Version 0.1.0, 2026-10-28.

## Question and scientific boundary

Can a bounded training-only adaptation reduce detection degradation on unseen physical RGB/LWIR sensors and acquisition environments?

**Non-overlap:** Resizing frames from one device does not establish cross-sensor transfer. P05 studies external validity, not P01 pixel-footprint or P02 fusion gain.

## Data prerequisites

At least two truly independent legal RGB/LWIR sensor/domain cohorts with compatible labels, documented optics, native resolution and preprocessing; NIR is separate, not a substitute for LWIR.

**Source screening:** LLVIP, KAIST, DroneVehicle and FLIR ADAS are only candidate sources, not automatically compatible or rights-cleared.

Record original source/version, licences and ethics/privacy conditions, native spectral bands and image grids, annotations, calibration/timing status, independent session splits and SHA-256 for inputs before acquisition or reuse. Do not commit licensed image archives, personal data or weights.

## Design and controls

Leave-one-device/source-out evaluation; fixed dataset/label mapping and train/validation/test partitions. Compare RGB-only, LWIR-only, fixed fusion, source-only and adaptation baselines with equal model budgets and no target-test label tuning.

**Primary outcome:** Out-of-domain AP drop relative to in-domain source performance, with independent device/domain as the test group.

**Secondary outcomes:** Recall at matched FP/frame, ECE, per-device effect and inference overhead; source-group bootstrap intervals.

## Before confirmatory analysis

- [ ] Audit sensor identities, native bit depth, spectral bands, class harmonization and rights.
- [ ] Freeze unseen device/domain test cohorts and duplicate/near-duplicate exclusions.
- [ ] Report all domain transfers, including failed transfers and scene-group confidence intervals.
- [ ] Freeze full hypotheses, null, decision rules, baselines, independent split and exclusion policy.
- [ ] Verify reproducibility with code SHA, data/annotation release hashes and test leakage audit.
- [ ] Report physical measurements separately from synthetic E00–E02 or host benchmarks.
- [ ] Document negative and null results, scene-level confidence intervals and independent novelty review.

## GO/NO-GO

**G05: two or more licensed, independent sensor/domain cohorts with compatible complete annotations and leakage-free source holdouts.**

**If the independent claim cannot be supported:** Resizing frames from one device does not establish cross-sensor transfer. P05 studies external validity, not P01 pixel-footprint or P02 fusion gain.

See [hypothesis](../hypotheses/README.md), [dataset admissions](../../../docs/experiments/datasets.md), [measurement standards](../../../docs/guides/evaluation-requirements.md) and [portfolio controls](../../../AUTOPILOT_PLAN.md).
