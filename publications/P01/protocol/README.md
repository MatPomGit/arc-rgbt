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
