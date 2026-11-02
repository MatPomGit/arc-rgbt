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

- **Primary candidate:** equal-weight mean of within-acquisition LWIR small-minus-reference IoU-0.50 recall differences at a validation-locked FP/frame operating point. This is an observational association, not a causal effect of image resolution. Class, contrast, geometry and viewpoint balance must be assessed.
- **Baselines:** LWIR-only fixed checkpoint for the single primary analysis, RGB-only as secondary; RGB/LWIR fusion belongs to P02. Artificial downsampling remains a separate software ablation, not measured physical low-resolution performance.
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
| Population | Verified native LWIR objects from independent acquisition groups with fully labelled positive and negative frames; RGB only secondary | PENDING source and class mapping |
| Primary estimand | Equal-acquisition-weighted mean of within-group small minus reference LWIR GT recall differences, both bins in each contributing acquisition | PENDING eligible groups and author freeze |
| Independent unit | Original acquisition/scene or flight group; adjacent frames from one acquisition are not independent replicates | PENDING source IDs |
| Operating point | Select detector thresholds on validation groups only, targeting the same FP/frame ceiling; never tune on held-out test data | PENDING numerical ceiling |
| Native footprint | Derive visible annotated target width/height/area on each modality's **original** grid; retain calibrated geometry and visibility metadata; do not use resized detector input as native footprint | PENDING native grid and optics |
| Baselines | LWIR-only fixed primary checkpoint; RGB secondary; pairing/fusion belongs to P02 | PENDING admissible data |
| Primary uncertainty | Bootstrap independent **paired acquisition** differences, equal group weights, not objects/frames; report effective group count | PENDING support and pilot precision audit |
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
| Independent outcome | Within-acquisition **IoU-0.50 localization-qualified** GT recall difference (small minus reference), averaged equally across acquisitions. Expected sign negative, no causal interpretation. | Source-verified acquisitions with both bins and complete labels |
| Footprint proxy | `s = sqrt(w_native * h_native)` in pixels from the original-grid target bounding box. Small: `s < 8`; intermediate: `8 <= s < 16`; reference: `s >= 16`. Only small vs reference is confirmatory. | Original grid and annotation conventions independently checked |
| Match rule | Class-aware, score-descending one-to-one IoU `>= 0.50`, original prediction order breaks ties. Each GT is counted once and assigned to a bin by its **original-grid GT box** before matching. | [P01 metrics tests](../analyses/README.md), plus shared #23 reference audit |
| False-alert budget | Candidate `0.10 FP/frame`. Choose lowest validation-only score threshold meeting observed ceiling using sorted unique prediction scores plus 0 and 1; no zero-TP solution. Keep fixed on test; this is not a guarantee of future FP/frame. | Complete validation frames and adequate exposure/groups |
| Test reporting | Report observed held-out FP/frame over all eligible positive and empty frames. If above `0.10`, label **OPERATING_CONDITION_NOT_MET**; report fixed-threshold recall descriptively, never retune test. | No test-outcome-driven threshold selection |
| Uncertainty | Candidate 2000 resamples of paired **whole acquisition differences**, seed `20261101`, 2.5/97.5% linearly interpolated percentiles, equal group weights. | Provisional >=10 *same* independent groups with both bins; pilot precision and coverage audit still required |
| Sensitivity | IoU `0.25` for tiny-target localization, intermediate bin, RGB, per-class and contrast/occlusion/view strata, AP, group-vs-object weighting all secondary/exploratory. | No post hoc confirmatory promotion |

#### Paired group estimand and causal limits (candidate)

For every independently verified LWIR acquisition group `g` containing at
least one **small** and one **reference** GT, compute
`r_small,g = TP_small,g / GT_small,g` and
`r_ref,g = TP_ref,g / GT_ref,g`. The primary candidate is
`Delta = mean_g(r_small,g - r_ref,g)`, with exactly **one equal weight per
acquisition**, not an object-pooled difference. Matching is assigned to
original-grid GT objects, including misses. Acquisitions lacking one bin
contribute only descriptive denominators and must be reported separately.
The current >=10 **paired** groups criterion is a *provisional minimum*,
not a sufficient-power guarantee; report effective group counts, counts
of objects per group/bin and exclusion frequencies. Include acquisition
groups consisting solely of fully labelled negative frames in the
FP/frame denominator and total acquisition count, but **not** as
pseudo-paired units in the primary recall contrast.

The contrast is **observational**. Small targets can have different class,
orientation, thermal contrast, occlusion, distance, motion blur and annotation
quality from larger ones within the same acquisition. This design does
not isolate a causal native-resolution effect. Before freezing, specify
class-/contrast-/viewpoint-specific sensitivity, balance tables and any
covariate-standardized comparison with a demonstrated common-support region.
Without support, report the limitations rather than a purported physical
detection limit. H0: `Delta = 0`; directional H1: `Delta < 0` is proposed,
not preregistered.

#### FP/frame calibration on validation only (candidate)

The engineering selector in `arc_rgbt.p01_metrics.choose_validation_threshold`
takes fully annotated validation frames and a declared group ID per frame.
Its **provisional** minimum is >=10 declared acquisition groups and >=200
frames, **including >=20 negative frames from >=2 acquisition groups**.
If negative-frame exposure is insufficient, return
`BLOCKED_NEGATIVE_EXPOSURE`, never a nominal 0-FP success. These floors
alone do not establish a reliable validation false-alert rate. Candidate confidence
thresholds are the sorted unique observed validation prediction scores
and 0/1 bounds, with inclusion rule `score >= threshold`. Select the lowest
threshold yielding observed `FP / all_validation_frames <= 0.10`.
Reject no-feasible and zero-TP solutions, including a trivial no-detection
threshold. The selector now reports a candidate 2000-replicate **acquisition-cluster
bootstrap percentile interval** for validation FP/frame (seed `20261101`).
Each replicate samples groups with replacement and computes
`sum(FP_g) / sum(frames_g)`, preserving the all-frame denominator.
If its upper 95% bound exceeds 0.10, flag
`validation_fp_upper_ci_exceeds_ceiling=true` and require review of
false-alert uncertainty before protocol freeze. This bound is a
descriptive validation uncertainty diagnostic, **not** a guarantee of
test performance. Review positive/negative-frame prevalence, unequal
acquisition sizes and negative-frame exposure. The held-out threshold
and checkpoint cannot be adjusted after seeing test results.

#### Group bootstrap and localization sensitivity (candidate)

Resample **whole eligible paired acquisition IDs** with replacement and
compute the mean of their entire per-group recall differences. Candidate
settings are 2000 replicates, fixed seed `20261101`, 95% percentile
limits at 0.025/0.975 with linear interpolation. Paired sampling avoids
empty-bin resamples; malformed or insufficient group support leads to
`DESCRIPTIVE_ONLY`, never frame-wise IID substitution. Ten acquisitions
may still yield poor interval coverage. Before held-out access, run a
pilot/simulation-based precision and coverage check and freeze any
small-cluster alternative interval. Report group variation, bin counts,
interval width and null findings. At `s < 8` pixels, a 1-pixel box
localization discrepancy can dramatically change IoU-0.50 recall:
interpret the primary endpoint as *localization-qualified detection*,
and prespecify IoU-0.25 and visible/amodal annotation sensitivity.
If ignore/crowd regions, ambiguous boxes or native vs processed geometry
cannot be resolved, exclude by a frozen policy or mark **BLOCKED**.
On a fixed-threshold held-out sample exceeding `0.10 FP/frame`, mark
`OPERATING_CONDITION_NOT_MET` and retain the point contrast only as
descriptive; do not present a confirmatory candidate CI or retune test.

#### Implementation and evidence boundary

`native_footprint_recall` provides per-GT native footprint, match flags,
group-paired differences and deterministic bootstrap. Unlike aggregate
`detection_contract` it retains original GT indices. It does **not**
independently verify image pixels, original grid, source identities,
licences, calibration or annotation completeness; its outputs always mark
`empirical_admission=false`. The metric helper retains per-acquisition
FP and frame counts even for fully negative groups; a test budget
violation suppresses the proposed CI while preserving descriptive
counts. The validation helper provides a source-group bootstrap
uncertainty *diagnostic*, not guaranteed false-alarm control. Both code
helpers and all numeric choices remain *prospective and unfrozen*. Reference tests using only synthetic
boxes provide engineering evidence, not real LWIR scientific GO.

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
than a physical detection-limit estimate. Only groups containing both
bins can contribute to the proposed paired bootstrap; if there are too
few or pilot precision is insufficient,
report DESCRIPTIVE_ONLY without a confirmatory interval. Author approval
is still required for bin edges, IoU,
FP/frame, group minimum and inference plan before freeze.

#### Synthetic cluster precision audit before freeze (2026-11-02)

A deterministic [acquisition-level precision pilot](../analyses/README.md)
now compares the candidate percentile bootstrap with a cluster-level
Student t interval across 10/20/40 independent paired groups, 4/20
targets per bin, and true mean contrasts 0 and -0.15. It assesses nominal
coverage, interval width and directional decision frequency under a
**specified synthetic generating model**. The pilot flags possible
undercoverage of the percentile interval when the provisional minimum of
ten groups is used. Thus **>=10 paired groups is not validated as a
confirmatory sample-size rule**. Neither interval is frozen or approved by
this audit. Before seeing held-out outcomes, the author must specify
source-informed group heterogeneity, bin counts, clinically/robotically
meaningful effect size, target precision, and an independently reviewed
inferential method. The simulation does not include the validation FP/frame
selector or real optical evidence; its coverage is not a guarantee for the
eventual study. Optional stress cases assess imbalanced bin denominators and
extra acquisition-shared probability variation. Finite-trial simulation
uncertainty is reported using Wilson bounds. These sensitivity checks cannot
replace a preregistered source-informed precision target, independent
acquisition audit, author sign-off or a separately reviewed statistical rule.

### Decisions still required before freeze

- [ ] Identify lawful original dataset release(s), sensor calibration,
      complete labels and independent acquisition identifiers (#10, #36).
- [ ] Fix the numerical FP/frame ceiling, IoU, footprint bins and sample
      adequacy criteria *without looking at held-out outcomes*.
- [ ] Freeze the paired-group estimand, overlap policy, class/contrast balance,
      validation exposure and threshold candidate grid.
- [ ] Audit pilot-based group-bootstrap precision, missingness and ignore-region
      rules; freeze multiplicity handling for any confirmatory extension.
- [ ] Obtain explicit author approval of the frozen protocol and store
      its commit SHA and date in [issue #35](https://github.com/MatPomGit/arc-rgbt/issues/35).
- [ ] Obtain independent evidence GO before reporting physical limits
      or claiming a submission-ready manuscript (#24, #29).

**Current evidence status: BLOCKED for confirmatory physical detection-limit
claims.** This draft can guide dataset screening and analysis implementation
without pre-empting the required preregistration.
