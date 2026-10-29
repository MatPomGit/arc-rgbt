# P05: experimental protocol and evidence gate

**Status:** CORE PLANNED; data and methods not yet empirically validated. Version 0.1.0, 2026-10-28.

## Question and scientific boundary

Can a bounded training-only adaptation reduce detection degradation on unseen physical RGB/LWIR sensors and acquisition environments?

**Non-overlap:** Resizing frames from one device does not establish cross-sensor transfer. P05 studies external validity, not P01 pixel-footprint or P02 fusion gain.

## Data prerequisites

At least two truly independent legal RGB/LWIR sensor/domain cohorts with compatible labels, documented optics, native resolution and preprocessing; NIR is separate, not a substitute for LWIR.

**Source screening:** LLVIP, KAIST, DroneVehicle and FLIR ADAS are only candidate sources, not automatically compatible or rights-cleared.

Record original source/version, licences and ethics/privacy conditions, native spectral bands and image grids, annotations, calibration/timing status, independent session splits and SHA-256 for inputs before acquisition or reuse. Do not commit licensed image archives, personal data or weights.

## Cross-domain identification caution (2026-10-29)

Owner-backed candidates include [KAIST](https://github.com/SoonminHwang/rgbt-ped-detection) (vehicle-mounted, default CC BY-NC-SA 4.0), [LLVIP](https://github.com/bupt-ai-cz/LLVIP) (low-light pedestrian, non-commercial licence), and [M3OT](https://www.nature.com/articles/s41597-025-06204-0) (aerial vehicle tracking; institutional record lists CC BY 4.0). **These are not automatically comparable domains.** Differences in class labels (pedestrian vs vehicle), viewpoint, night/day, native sensor pitch, aligned crops and thermal processing can confound any inference that a change is caused by sensor identity. Declare a class-compatible, independent source/device comparison before any cross-sensor claim; otherwise report a broader multi-domain generalization study or NO-GO for P05.

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
