# P06: experimental protocol and evidence gate

**Status:** CORE PLANNED; data and methods not yet empirically validated. Version 0.1.0, 2026-10-28.

## Question and scientific boundary

Does modality-aware temporal association preserve multi-object identity better than single-modality and fixed-fusion trackers during occlusion and intermittent sensing?

**Non-overlap:** Temporal association is separate from P01–P05 frame detection. No tracking claims from synthetic rectangle-overlap E02.

## Data prerequisites

Legally available paired RGB/LWIR video with annotated identities, explicit timestamps or documented unknown clock domains and independent sequence splits; still images are insufficient.

**Source screening:** Investigate owner-published temporal datasets including M3OT only after licensing, annotation and capture-viewpoint verification.

Record original source/version, licences and ethics/privacy conditions, native spectral bands and image grids, annotations, calibration/timing status, independent session splits and SHA-256 for inputs before acquisition or reuse. Do not commit licensed image archives, personal data or weights.

## M3OT first-candidate review (metadata only, 2026-10-29)

[Nie et al., Scientific Data (2025)](https://www.nature.com/articles/s41597-025-06204-0) describe multi-UAV aerial RGB/thermal vehicle tracking, paired modalities, ~10,790 pairs and ~220k bounding boxes. The [institutional dataset entry](https://rgu-repository.worktribe.com/output/3195645/m3ot-a-multi-drone-multi-modality-dataset-for-multi-object-tracking-dataset) lists a CC BY 4.0 licence; the exact hosted archive and tracking GT have **not been inspected**. The dataset documentation reports *manual* sequence-time alignment and affine image registration/cropping, not calibrated physical exposure timestamps or native grids.

Before G06 can pass:

- [ ] Check rights attached to the exact Figshare archive and annotations, plus stable version and checksums; no data mirroring.
- [ ] Audit original paired RGB/IR frame keys, consistent track identities per sequence, occlusion labels, missing tracks and processed/native geometry.
- [ ] Freeze train/validation/test by acquisition flight and scene, check cross-drone views and adjacent-frame/near-duplicate leakage; do not assume the author's image split is sequence-independent.
- [ ] Establish HOTA/IDF1 implementation with independently documented expected values. Verify whether scene/viewpoint label mapping supports the preregistered experiment.
- [ ] Treat manual pair alignment as a preprocessing step with unknown residual clock/skew; keep P02 exposure-synchronization claims blocked unless independently measured.

**Decision:** high-priority metadata candidate for P06, **not an admitted experimental dataset and not a passed G06 gate**.

## Reference tracking evaluator candidate (2026-10-29)

Official upstream: [JonathonLuiten/TrackEval](https://github.com/JonathonLuiten/TrackEval). For reproducible P06 planning, the **candidate revision** is `12c8791b303e0a0b50f753af204249e622d0281a` ([tree](https://github.com/JonathonLuiten/TrackEval/tree/12c8791b303e0a0b50f753af204249e622d0281a), [MIT licence](https://github.com/JonathonLuiten/TrackEval/blob/12c8791b303e0a0b50f753af204249e622d0281a/LICENSE)). The [opt-in TrackEval adapter](../../../docs/reference/data-contracts.md) now maps complete tracking frames to per-class metrics inputs and requires official sanity fixtures on optional trusted execution. **The third-party reference has not been executed in repository CI**, and source-specific GT mapping, ignore regions, data rights and independent flight splits remain unverified; G06 is blocked. Do not fetch untrusted code onto persistent runners or imply the external software licence grants rights to M3OT image/annotation archives.
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

## Association-specific evaluation checks (draft, not frozen)

- HOTA is not association-only: report its detection and association components (**DetA and AssA**) and IDF1, and identify the reference metric's aggregation and localisation thresholds.
- For the association comparison, freeze all input candidate boxes, scores, timestamps and permissible pair keys across tracker variants. Mark any upstream detector or postprocessing changes as a separate full-pipeline experiment, not an isolated association effect.
- Validate ignore regions, empty frames, duplicate track IDs, identity continuation, temporal gaps and class mapping on independently checked reference fixtures. Record the pinned evaluator revision and executable environment.
- Cluster uncertainty by genuinely independent sequence/flight groups; adjacent frames are not independent replicates. The M3OT publication is useful metadata, but cannot replace examination of the actual released tracking archive, rights and source partitions.

## GO/NO-GO

**G06: licensed, real identity-labelled sequences with correct RGB/LWIR pairing and verified HOTA evaluator; vehicle-mounted results must not be claimed as aerial results.**

**If the independent claim cannot be supported:** Temporal association is separate from P01–P05 frame detection. No tracking claims from synthetic rectangle-overlap E02.

See [hypothesis](../hypotheses/README.md), [dataset admissions](../../../docs/experiments/datasets.md), [measurement standards](../../../docs/guides/evaluation-requirements.md) and [portfolio controls](../../../AUTOPILOT_PLAN.md).
