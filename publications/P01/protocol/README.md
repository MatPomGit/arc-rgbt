# P01 study protocol

Specify inclusion/exclusion criteria, sensor calibration, datasets, controls, splits, uncertainty, statistical design and experimental stopping conditions before empirical data acquisition. No approved empirical protocol is claimed.

## Review-derived preregistration checks

- Define object appearance in **native pixels**, optical geometry, target
  orientation and projection plane. For near-nadir imagery, standing body
  height is **not** the projected target height; do not infer universal
  distance limits from an assumed 1.7 m visual extent.
- Predefine strata for native grid, optical blur, noise, thermal contrast,
  image orientation and occlusion, and distinguish simulated versus
  independently measured optical degradation.
- Report precision, recall, F1 and AP separately as applicable, including
  IoU/confidence policies, negative-frame annotation completeness and
  uncertainty over independent scenes/acquisitions.
- **Exit gate:** no real-sensor generalization claim until original
  source images, labels, scene-separated test split and provenance are verified.

See [experimental evaluation requirements](../../../docs/guides/evaluation-requirements.md)
and [screened literature](../../../docs/experiments/literature-screening.md).

## Planned confirmatory study (not yet preregistered)

- **Primary endpoint:** recall at the same preregistered FP/frame ceiling across native pixel-footprint bins, stratified by physical viewpoint, object class, modality and independent scene/acquisition.
- **Baselines:** RGB-only and LWIR-only with fixed checkpoints and documented pre-processing. Artificial downsampling is a separate controlled software ablation and must not be confused with measured physical low-resolution performance.
- **Controls:** native focal length/pixel pitch, projection geometry, image-frame orientation, blur, occlusion, thermal contrast and completeness of negative frames.
- **Evaluation:** freeze inclusion/exclusion policy and footprint strata before analyzing held-out data. Use acquisition/sequence-group intervals, report detection failures and avoid frame-wise IID inference.
- **GO:** physically acquired native frames, source/annotation licences, complete independent labels, test splits and uncertainty PASS. Otherwise NO-GO for physical detection-limit claims.

[Hypothesis and estimands](../hypotheses/README.md) · [portfolio boundary](../../../RESEARCH.md).

## Operational preregistration decision register (draft 2026-10-31)

This is a **draft design**, not a frozen preregistration or permission to
make empirical claims. Final numerical choices require a legally admitted
source inventory and author sign-off **before access to held-out outcomes**.
Changes after that point must be logged as deviations, not silently applied.

| Decision | Proposed rule | Freeze status |
| --- | --- | --- |
| Population | Objects with verified class labels in physically acquired original RGB or LWIR frames, including fully labelled negative frames | PENDING source and class mapping |
| Primary estimand | Difference in per-object held-out recall between preregistered smaller and reference *native projected pixel-footprint* strata, evaluated at a common FP/frame ceiling, separately by modality | PENDING strata, FP ceiling and IoU |
| Independent unit | Original acquisition/scene or flight group; adjacent frames from one acquisition are not independent replicates | PENDING source IDs |
| Operating point | Select detector thresholds on validation groups only, targeting the same FP/frame ceiling; never tune on held-out test data | PENDING numerical ceiling |
| Native footprint | Derive visible annotated target width/height/area on each modality's **original** grid; retain calibrated geometry and visibility metadata; do not use resized detector input as native footprint | PENDING native grid and optics |
| Baselines | Fixed RGB-only and LWIR-only checkpoints; include paired fusion only where alignment and pairing are independently verified | PENDING admissible data |
| Primary uncertainty | Resample independent acquisition groups (not individual frames) and report interval and group count; no precision claim if independent groups are insufficient | PENDING sample-size/interval specification |
| Secondary analyses | Class, view, occlusion, contrast, localization error, AP at named IoU and software degradation; explicitly exploratory unless prespecified and multiplicity handled | PENDING prespecification |

### Admission, selection and measurement rules

1. Admit a dataset only after original source/version, legal use, sensor
   modality (LWIR is not NIR), native-versus-cropped grid, optics/geometry,
   annotation completeness, frame keys and source IDs have been audited
   under [the shared evidence gate](../../../docs/experiments/datasets.md).
   Unverified metadata are **unknown**, never assumed valid.
2. Before running any confirmatory detector evaluation, lock class mapping,
   inclusion/exclusion criteria, target-footprint bin edges, minimum group
   counts, primary IoU and FP/frame ceiling using **non-test information**.
   Do not select bins, thresholds or test scenes to maximize a result.
3. Assign train/validation/test by source acquisition groups using the
   [shared data contracts](../../../docs/reference/data-contracts.md).
   Check exact and near-duplicate overlap, shared scenes across sensors,
   adjacent frames and source/device leakage. Record split hashes and
   reasons for exclusions before outcome analysis.
4. Use all independently labelled negatives in FP/frame denominators.
   Define the frame count, IoU matching, class policy, ignored regions,
   missing detections and zero-denominator behavior in the frozen protocol.
   If a method cannot meet the target FP/frame ceiling, report that
   limitation rather than comparing at unmatched operating points.
5. Compare native RGB and LWIR strata **within their own grids**; do not
   equate an RGB pixel to an LWIR pixel without measured projection
   geometry. Report capture distance only when independently measured,
   with view direction, optics and target orientation; no universal range.
6. Summarize the primary effect with acquisition-group uncertainty and
   report failure cases and group counts. If there are too few independent
   groups, missing negative labels, unknown rights or unreliable native
   geometry, stop confirmatory physical-limit analysis and mark **BLOCKED**.
7. Keep E00 synthetic downsampling and any image-resize ablation in a
   separate analysis. Neither validates optical point-spread, thermal
   noise, calibration, actual target range nor robot deployment.

### Candidate primary analysis contract (author review required)

These are **prospective numerical defaults**, not a frozen protocol or a claim
that any eligible real data exist. They are recorded before test-data access
to make the pending author decision concrete. If the author rejects a default,
record the replacement and rationale in #35 before unblinding test outcomes.

| Item | Proposed prespecification | Gate |
| --- | --- | --- |
| Primary modality | Physically acquired native **LWIR** only. RGB is a prespecified secondary comparison; fusion belongs to P02 unless a separate P01 ablation is justified. | Native LWIR and original labels verified |
| Independent outcome | Held-out difference in **per-object recall**: small minus reference footprint at the same frozen LWIR checkpoint and confidence threshold; expected sign negative. | Eligible groups and full target labels |
| Footprint proxy | `s = sqrt(w_native * h_native)` in pixels from the original-grid target bounding box. Small: `s < 8`; intermediate: `8 <= s < 16`; reference: `s >= 16`. Only small vs reference is confirmatory. | Original grid and annotation conventions independently checked |
| Match rule | Class-aware, one-to-one IoU `>= 0.50` with deterministic score-ordered greedy matching. A target can contribute at most one true positive. | Shared metric contract #23 reference tests |
| False-alert budget | Candidate ceiling `0.10 FP/frame`. On independent **validation** frames, select the lowest confidence threshold satisfying the ceiling (ties resolved by higher threshold). Keep it unchanged on test. | Fully labelled negative and positive frames; fixed checkpoint |
| Test reporting | Report observed test FP/frame even if above `0.10`, plus all target and frame denominators. Exceeding the ceiling means the target operating condition was **not met**, not that the test threshold may be retuned. | No test-outcome-driven threshold selection |
| Uncertainty | Two-sided 95% percentile interval from 2000 bootstrap replicates of **whole independent acquisition groups**, fixed seed `20261101`, preserving all frames and targets within each sampled group. | At least 10 distinct groups contributing targets to each compared bin; otherwise descriptive only |
| Sensitivity | Intermediate footprint bin, RGB modality, IoU `0.25` for localization sensitivity, AP and contrast/occlusion strata are secondary/exploratory unless separately prespecified. | No post hoc confirmatory promotion |

**Interpretation safeguards.** The annotated bounding box is an observable
*image-plane footprint proxy*, not an independent optical point-spread
measurement or a calibrated physical object extent. For occluded or clipped
objects, the annotation may describe the visible region or the inferred full
extent; record that convention and predefine exclusion/sensitivity handling
before freeze. No physical distance threshold follows from `s` alone.
If a source offers only resized/cropped images with unknown native geometry,
it cannot enter the confirmatory population.

**Denominators and stop rules.** Every eligible, independently annotated
target is counted in the recall denominator, including misses. FP/frame uses
all eligible and completely annotated test frames, including empty frames.
Record unmatched predictions on both positive and negative frames. Do not
select an operating threshold from the test set. If validation permits only
the no-detection solution, or the required independent groups, native labels
or negative-frame completeness are unavailable, report **BLOCKED** rather
than a physical detection-limit estimate. If bootstrap replicates omit a
comparison bin, report the invalid count and do not silently replace them
with frame-wise resampling. The author must still approve bin edges, IoU,
FP/frame, group minimum and inference plan before freeze.

### Decisions still required before freeze

- [ ] Identify lawful original dataset release(s), sensor calibration,
      complete labels and independent acquisition identifiers (#10, #36).
- [ ] Fix the numerical FP/frame ceiling, IoU, footprint bins and sample
      adequacy criteria *without looking at held-out outcomes*.
- [ ] Fix the group-resampling method, interval level, missingness rules
      and any multiplicity adjustment for confirmatory secondary tests.
- [ ] Obtain explicit author approval of the frozen protocol and store
      its commit SHA and date in [issue #35](https://github.com/MatPomGit/arc-rgbt/issues/35).
- [ ] Obtain independent evidence GO before reporting physical limits
      or claiming a submission-ready manuscript (#24, #29).

**Current evidence status: BLOCKED for confirmatory physical detection-limit
claims.** This draft can guide dataset screening and analysis implementation
without pre-empting the required preregistration.
