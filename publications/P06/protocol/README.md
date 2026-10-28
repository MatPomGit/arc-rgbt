# P06: experimental protocol and evidence gate

**Status:** CORE PLANNED; data and methods not yet empirically validated. Version 0.1.0, 2026-10-28.

## Question and scientific boundary

Does modality-aware temporal association preserve multi-object identity better than single-modality and fixed-fusion trackers during occlusion and intermittent sensing?

**Non-overlap:** Temporal association is separate from P01–P05 frame detection. No tracking claims from synthetic rectangle-overlap E02.

## Data prerequisites

Legally available paired RGB/LWIR video with annotated identities, explicit timestamps or documented unknown clock domains and independent sequence splits; still images are insufficient.

**Source screening:** Investigate owner-published temporal datasets including M3OT only after licensing, annotation and capture-viewpoint verification.

Record original source/version, licences and ethics/privacy conditions, native spectral bands and image grids, annotations, calibration/timing status, independent session splits and SHA-256 for inputs before acquisition or reuse. Do not commit licensed image archives, personal data or weights.

## Design and controls

First compare association methods with fixed detector proposals; then separately compare full detector+tracker pipelines. Include RGB-only, LWIR-only, fixed fusion+tracker and modality-aware association. Disallow shared tracks across development and test.

**Primary outcome:** HOTA on independent annotated sequences, including predeclared occlusion and temporary modality-loss strata.

**Secondary outcomes:** IDF1, identity switches, fragmentation, association accuracy, recall, FP/frame and full-pipeline latency.

## Before confirmatory analysis

- [ ] Verify identity-labelled full sequences, rights and viewpoint (aerial vs vehicle-mounted).
- [ ] Freeze track-ID conventions, HOTA evaluator, temporal pairing and independent source splits.
- [ ] Measure sequence-group confidence intervals, missing modalities, occlusion and detector-versus-association contributions.
- [ ] Freeze full hypotheses, null, decision rules, baselines, independent split and exclusion policy.
- [ ] Verify reproducibility with code SHA, data/annotation release hashes and test leakage audit.
- [ ] Report physical measurements separately from synthetic E00–E02 or host benchmarks.
- [ ] Document negative and null results, scene-level confidence intervals and independent novelty review.

## GO/NO-GO

**G06: licensed, real identity-labelled sequences with correct RGB/LWIR pairing and verified HOTA evaluator; vehicle-mounted results must not be claimed as aerial results.**

**If the independent claim cannot be supported:** Temporal association is separate from P01–P05 frame detection. No tracking claims from synthetic rectangle-overlap E02.

See [hypothesis](../hypotheses/README.md), [dataset admissions](../../../docs/experiments/datasets.md), [measurement standards](../../../docs/guides/evaluation-requirements.md) and [portfolio controls](../../../AUTOPILOT_PLAN.md).
