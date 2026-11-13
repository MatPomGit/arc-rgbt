# P01 study protocol

## P01 S09 author decision packet v0.4.1 (2026-11-13; UNFROZEN)

**Purpose:** one prospective choice for [#35](https://github.com/MatPomGit/arc-rgbt/issues/35)
and [#53](https://github.com/MatPomGit/arc-rgbt/issues/53), due 2026-11-13.
**Current author decision:** `CONDITIONAL_DESIGN` (2026-11-04); no frozen
preregistration, source admission, confirmatory test, or experimental result.
This packet summarizes existing decisions without changing their scientific
authority. Its Git revision records the *candidate*, not author approval.

| Decision | Single Tier A candidate for author review | Status / blocking evidence |
| --- | --- | --- |
| Claim and population | Fixed LWIR detector on a lawfully used, versioned source release; `car` against supplied COCO reference labels | **CANDIDATE**; original archive image/annotation terms, release hashes and checkpoint training provenance not verified (#45/#47) |
| Size proxy | `s=sqrt(w*h)` from COCO **export-grid** bbox; small `s<8`, intermediate `8<=s<16`, reference `s>=16` pixels | **CANDIDATE**, never automatically described as native detector pixels or physical range (#46) |
| Matching and alerts | Same-class one-to-one IoU `>=0.50`; unmatched car detections per **all** source-labelled frames. Zero-car-GT frames are reference-negative, not proven empty | **CANDIDATE** ignore/crowd boxes rejected until source convention specified (#47) |
| Threshold | Lowest nontrivial feasible validation-only score meeting candidate `0.10` source-reference FP/frame; no test retuning; holdout violation `OPERATING_CONDITION_NOT_MET` | **CANDIDATE**; final ceiling and rule need author approval, real validation frames and fixed checkpoint (#51/#58) |
| Data partitions | No overlap of true acquisition groups in train/validation/holdout or checkpoint training; `video_id` is **only a proxy** | **BLOCKED**; lawful source-provided independent acquisition IDs and split/checkpoint lineage unavailable (#48/#55) |
| Primary contrast | If genuine independent acquisitions exist, equally weighted `Delta = mean_g(recall_small,g - recall_reference,g)` among groups with targets in both bins | **CANDIDATE**; number/heterogeneity of true groups and paired-bin support unavailable (#48/#50) |
| Statistical inference | One-sided `H1: Delta < 0`, alpha 0.05 acquisition-level t procedure only after empirical validity/calibration and independent methodological review | **BLOCKED** (#49/#53); if prerequisites fail, `DESCRIPTIVE_ONLY`, with per-bin recall, FP/frame, AP@IoU 0.50, group/target/frame denominators |
| Scope | Tier A observational source-GT-relative benchmark; RGB-only secondary, RGB/LWIR fusion P02; software resizing E00 simulated | **CANDIDATE**; no causal optics, physical range, native-sensor or deployment claim |
| Tier B | Separately verified original sensor grid/optics, transform from native to labels, physical provenance and authentic acquisitions | **BLOCKED** (#46); never promoted by Tier A metrics |
| Editorial fit | Object detection and sensor perception are within the *Sensors* Special Issue's subject list; whether this particular Tier A benchmark is sufficiently novel remains unproven | **PROVISIONAL** (#52); unsent scope abstract in [P01 overview](../README.md) |

**Software readiness, not scientific approval.** [PR #72](https://github.com/MatPomGit/arc-rgbt/pull/72)
was merged as `e1161ea2d0a8e7821d5934018966dc380b54fa0b`;
[exact-head CI](https://github.com/MatPomGit/arc-rgbt/actions/runs/42664280237)
passed 447 tests with 8 skips, Ruff and MkDocs. The code computes
pre-test COCO denominators and guarded validation predictions from an
existing compatible local checkpoint, but no actual source archive,
checkpoint or inference result was observed in this review. The
held-out evaluator requires an author-declared `FROZEN` record with
actual file SHA-256s; **an editable record does not authenticate its
author or prove legal/scientific admission**.

**2026-11-13 decision criterion:** choose `FROZEN` only after eligible
source release/rights, exact data/model/split lineage, complete numerical
choices, acquisition-feasibility and applicable independent method review
are documented and the corresponding author expressly approves the
specific prospective protocol revision. Otherwise preserve
`CONDITIONAL_DESIGN / UNFROZEN / G01 BLOCKED`; choose `NO-GO` if
the original data or statistical requirements are demonstrably
incompatible. An unfinished source admission is not cured by manual
reannotation or by a green unit-test suite.

**Next automatic evidence:** permitted local source files -> group and
source-GT denominator manifest -> fixed-checkpoint validation-only
predictions and candidate FP/frame threshold -> artifact hashes. Untouched
holdout remains closed until the actual prospective freeze. No
publisher outreach, paid tools, new human label QA or implicit manuscript
submission is authorized.

Specify inclusion/exclusion criteria, sensor calibration, datasets, controls, splits, uncertainty, statistical design and experimental stopping conditions before empirical data acquisition. No approved empirical protocol is claimed.

## Current protocol interpretation: automation-first (2026-11-07)

**Tier A, existing-data benchmark:** use the dataset's existing reference annotations, with predeclared target/class/ignore rules and group-disjoint train/validation/test partitions where authentic grouping exists. Detection recall, AP and FP/frame are **relative to supplied labels**. Unlabelled real targets could be apparent FPs. Annotations are not guaranteed complete. If independent acquisition identifiers cannot be verified, limit group-based inference to `DESCRIPTIVE_ONLY`. Lack of native optics evidence blocks Tier B physical claims but does not itself preclude a properly documented Tier A source-GT-relative analysis.

**Tier B, physical native-sensor interpretation:** requires independent already-available original LWIR sensor/grid/optical and acquisition evidence, source terms and a frozen prospective protocol. If unavailable, physical sensor-range and causal/native-optical claims stay BLOCKED while a legal Tier A experiment may proceed in its narrower claim class. A change of confirmatory claims requires explicit author decision before viewing untouched test outcomes.

**No agent-created manual annotation gate:** no two source-image reviewers, assessor CSVs, blind image galleries, adjudication or independent relabelling; no standalone database/dataset QA program without permission. Reuse minimal necessary source-format checks, split/leakage controls and validated metric code as integral parts of real experiments. If data/GPU reside on local Fedora, a single short offline command and hash-backed machine outputs suffice as a handoff. Distinguish independent reproduction of results from human relabelling. Source rights, no test tuning, no spending and final author approval remain mandatory.

## Review-derived preregistration checks

- Define object appearance in **native pixels**, optical geometry, target
  orientation and projection plane. For near-nadir imagery, standing body
  height is **not** the projected target height; do not infer universal
  distance limits from an assumed 1.7 m visual extent.
- Predefine strata for native grid, optical blur, noise, thermal contrast,
  image orientation and occlusion, and distinguish simulated versus
  independently measured optical degradation.
- Report precision, recall, F1 and AP separately as applicable, including
  IoU/confidence policies, annotation completeness limitations and
  uncertainty over independent scenes/acquisitions.
- **Exit gate:** no real-sensor generalization claim until original
  source images, labels, scene-separated test split and provenance are verified.

See [experimental evaluation requirements](../../../docs/guides/evaluation-requirements.md)
and [screened literature](../../../docs/experiments/literature-screening.md).

## Planned confirmatory study (not yet preregistered)

The legacy native-sensor planning items in this section concern possible Tier B extensions. For the currently proposed Tier A endpoint, use the source-export footprint and dataset-relative claim conventions of the S09 v0.4.1 decision table above. No physical native-pixel claim is authorized.

- **Primary candidate:** equal-weight mean of within-acquisition LWIR small-minus-reference IoU-0.50 recall differences at a validation-locked FP/frame operating point. This is an observational association, not a causal effect of image resolution. Class, contrast, geometry and viewpoint balance must be assessed.
- **Baselines:** LWIR-only fixed checkpoint for the single primary analysis, RGB-only as secondary; RGB/LWIR fusion belongs to P02. Artificial downsampling remains a separate software ablation, not measured physical low-resolution performance.
- **Controls:** native focal length/pixel pitch, projection geometry, image-frame orientation, blur, occlusion, thermal contrast and completeness of negative frames.
- **Evaluation:** freeze inclusion/exclusion policy and footprint strata before analyzing held-out data. Use acquisition/sequence-group intervals, report detection failures and avoid frame-wise IID inference.
- **GO:** physically acquired native frames, source/annotation licences, complete independent labels, test splits and uncertainty PASS. Otherwise NO-GO for physical detection-limit claims.

[Hypothesis and estimands](../hypotheses/README.md) · [portfolio boundary](../../../RESEARCH.md).

## D1/D2/D10 decision sheet for author review (2026-11-03; UNFROZEN)

This sheet resolves the *candidate interpretation* of the P01 primary
question, not its scientific approval. No source-verified acquisition
inventory, non-test pilot variance or independent method sign-off is
available. It therefore **must not** be called preregistration.

| ID | Candidate decision | Evidence still needed before freeze |
| --- | --- | --- |
| D1: target population | Lawfully usable LWIR frames with supplied GT for Tier A descriptive/reference-relative analysis; authentic original-grid geometry and independent acquisition IDs are separately required for Tier B physical claims and defensible confirmatory group inference. For the Tier A primary contrast, an acquisition contributes only when it contains at least one eligible target in **each** of the two prespecified COCO export-grid footprint bins; Tier B physical interpretation has separate original-sensor requirements. Frames with zero GT remain in FP/frame assessment. | Original archive, lawful terms, supplied-label convention and group/geometry evidence status (#45-#48); missing source-label completeness restricts the claim, not an automatic demand for new human annotation. |
| D2: contrast | For acquisition `g`, compute `d_g = TP_small,g / N_small,g - TP_reference,g / N_reference,g` at the **same** validation-locked LWIR detector threshold. Primary estimand is `Delta = mean_g(d_g)`, giving each eligible acquisition equal weight, not each target. The population is the eligible paired-bin acquisition cohort, **not** all LWIR scenes. | Counts by acquisition/bin and overlap of class, contrast, viewpoint and occlusion; review potential selection induced by requiring both bins (#48/#50). |
| D10: inference | Directional candidate `H1: Delta < 0`, `H0: Delta >= 0` (calibrate at boundary `Delta = 0`); proposed one-sided alpha `0.05`. A two-sided 95% interval is **descriptive**, not the alpha-0.05 decision. Candidate confirmatory test: one-sided acquisition-level Student t of mean `d_g` against zero with `G-1` degrees of freedom; group-level validity and source-informed calibration remain unresolved. | Independent group count, group heterogeneity, distributional diagnostics, finite-sample type-I error and power simulations informed by non-test data, independent scientific review and author approval (#49/#50/#53). |

**Inferential compatibility and stop rule.** If the t procedure is eventually
approved, use the predeclared one-sided p-value with alpha 0.05 and optionally
the corresponding one-sided 95% upper confidence bound for the same test;
`upper_bound < 0` is the equivalent directional decision when the sample
variance is positive and the test assumptions hold. With zero sample variance,
mark the candidate t decision `UNDEFINED` rather than interpreting a
degenerate interval as calibrated evidence. A symmetric
two-sided 95% t interval corresponds to a stricter directional crossing
criterion and cannot silently replace that test. The current 2000-replicate
percentile cluster bootstrap is a **sensitivity/precision candidate only**,
because synthetic small-group coverage was inadequate; do not label its
two-sided 95% interval as a calibrated confirmatory procedure. No
parametric normality, group exchangeability or independent-acquisition
assumption has yet been established on admitted data.

**Confounding and common support.** Within-acquisition comparison removes
some between-acquisition variation but does not randomize footprint.
Differences in class, occlusion, contrast, viewing geometry, range or
annotation convention may still explain the contrast. Report distributions
of these factors by bin and acquisition *without using held-out detection
outcomes* to choose exclusions or bin edges. If class/geometry overlap is
insufficient, describe the contrast as observational or mark the planned
primary inference `DESCRIPTIVE_ONLY`; any class-standardized estimate is
secondary unless separately prespecified and supported by source counts.
Never interpret a significant `Delta` as a causal pixel-resolution effect,
physical maximum range or demonstrated mobile-robot deployment.

**Selection and multiplicity.** There is one LWIR-only directional primary
test, conditional on valid source admission and the fixed FP/frame operating
condition. RGB, fusion, alternate IoU thresholds, bin edges, weighting and
covariate-adjusted estimates do not supply replacement confirmatory tests.
If the frozen held-out FP/frame condition is violated, preserve the
descriptive contrast and label the confirmatory operating condition unmet,
without retuning or switching to another endpoint. Author signature,
reviewer identity, source SHA and decision date remain **PENDING**.

## Operational preregistration decision register (draft 2026-10-31)

This is a **draft design**, not a frozen preregistration or permission to
make empirical claims. Final numerical choices require a legally admitted
source inventory and author sign-off **before access to held-out outcomes**.
Changes after that point must be logged as deviations, not silently applied.

| Decision | Proposed rule | Freeze status |
| --- | --- | --- |
| Population | Tier A: eligible source-labelled LWIR `car` targets on a documented COCO export grid, with source-GT-relative negatives; independent acquisition verification is necessary for confirmatory inference, not a prerequisite to honest descriptive measurement. RGB only secondary. Tier B has additional native-optics requirements. | PENDING lawful source, class map, split and inferential group proof |
| Primary estimand | Equal-acquisition-weighted mean of within-group small minus reference LWIR GT recall differences, both bins in each contributing acquisition | PENDING eligible groups and author freeze |
| Independent unit | Original acquisition/scene or flight group; adjacent frames from one acquisition are not independent replicates | PENDING source IDs |
| Operating point | Select detector thresholds on validation groups only, targeting the same FP/frame ceiling; never tune on held-out test data | PENDING numerical ceiling |
| Footprint provenance | Tier A: `s = sqrt(w_export * h_export)` on the declared COCO export grid, without calling it native. Tier B: original sensor geometry, coordinate transforms and optics separately verified; detector-input resizing is not native footprint evidence. | PENDING export transform; physical calibration BLOCKED for Tier B |
| Baselines | LWIR-only fixed primary checkpoint; RGB secondary; pairing/fusion belongs to P02 | PENDING admissible data |
| Primary inference candidate | One-sided acquisition-level t test, alpha 0.05, conditional on calibration under source-informed bounded and heterogeneous group differences | PENDING type-I error, power, source-independent groups and approval |
| Descriptive uncertainty | Two-sided 95% whole-acquisition percentile bootstrap and two-sided group t interval; neither serves as the primary directional decision | PENDING coverage and pilot precision audit |
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
| Primary modality | Lawfully obtained **LWIR** source imagery with supplied labels; Tier A may use documented export coordinates without proving the sensor's native pixel geometry. RGB secondary; fusion belongs to P02. | Source modality, release, lawful use and label lineage; physical native geometry reserved for Tier B |
| Independent outcome | Source-GT-relative **IoU-0.50 localization-qualified** recall difference (small minus reference), equally weighted across eligible paired acquisitions; negative sign is a hypothesis, not an assumed finding. | Confirmatory inference needs verified independent acquisitions with both bins and justified finite-group method; otherwise DESCRIPTIVE_ONLY |
| Footprint proxy | Tier A: `s = sqrt(w_export * h_export)` in pixels from the declared COCO export-grid GT box. Small: `s < 8`; intermediate: `8 <= s < 16`; reference: `s >= 16`. Small vs reference is the only primary candidate; neither bins nor physical interpretation are approved. | Exact export grid and box transform documented; Tier B native footprint requires separate evidence |
| Match rule | Class-aware, score-descending one-to-one IoU `>= 0.50`, original prediction order breaks ties. Each GT is counted once and assigned to a bin by its **source-export-grid GT box** before matching. | [P01 metrics tests](../analyses/README.md), plus shared #23 reference contract |
| False-alert budget | Candidate `0.10 source-GT-relative FP/frame` across all eligible source-labelled frames. Choose lowest validation-only score threshold meeting observed ceiling using sorted unique prediction scores plus 0 and 1; no zero-TP solution. Keep fixed on test; this is not a guarantee of future FP/frame or true physical false alarms. | Source-labelled validation frames and documented exposure/groups; label completeness is not presumed |
| Test reporting | Report observed held-out FP/frame over all eligible positive and empty frames. If above `0.10`, label **OPERATING_CONDITION_NOT_MET**; report fixed-threshold recall descriptively, never retune test. | No test-outcome-driven threshold selection |
| Directional inference | Candidate one-sided group Student t test of `Delta < 0` at alpha 0.05; reject `H0: Delta >= 0` only if its one-sided 95% upper t bound is below zero. No test if the sample variance is zero. | Minimum independent groups, empirical type-I calibration and prospective power remain pending |
| Descriptive interval | Candidate 2000-resample whole-paired-acquisition percentile bootstrap, seed `20261101`, two-sided 95% (2.5/97.5%) endpoints. This is **not** the primary hypothesis test. | Provisional >=10 paired groups; source-informed coverage audit still required |
| Sensitivity | IoU `0.25` for tiny-target localization, intermediate bin, RGB, per-class and contrast/occlusion/view strata, AP, group-vs-object weighting all secondary/exploratory. | No post hoc confirmatory promotion |

#### Paired group estimand and causal limits (candidate)

For every independently verified LWIR acquisition group `g` containing at
least one **small** and one **reference** GT, compute
`r_small,g = TP_small,g / GT_small,g` and
`r_ref,g = TP_ref,g / GT_ref,g`. The primary candidate is
`Delta = mean_g(r_small,g - r_ref,g)`, with exactly **one equal weight per
acquisition**, not an object-pooled difference. Matching is assigned to
source-export-grid GT objects, including misses. Acquisitions lacking one bin
contribute only descriptive denominators and must be reported separately.
The current >=10 **paired** groups criterion is a *provisional computational
floor*, not a sufficient-power guarantee. The code permits a group with
one target per bin and reports it explicitly; this is **not** an approved
scientific minimum. Report paired group counts, targets per group and bin,
the fraction of all acquisitions excluded for lacking both bins, and
the count of paired groups with a singleton bin. Choose a justified minimum
within-bin target count and independent-group count from non-test source
inventory, prospective precision/power simulations and reviewer assessment
before freeze. Recalculate the small-minus-reference contrast by pooling
targets **within paired groups only** as an exploratory weighting sensitivity:
the prespecified primary estimand remains equal-acquisition weighted.
The target-pooled sensitivity uses different relative acquisition weights
in the small and reference bins; it can differ even if each acquisition has
`d_g = 0`. The difference is a **change of estimand and bin composition**,
not merely a single alternate set of acquisition weights.
If eligible acquisitions are sparse or common support is inadequate,
mark the study `DESCRIPTIVE_ONLY` irrespective of software-generated
candidate intervals. The implementation requires an explicitly configured
`minimum_targets_per_bin >= 2` before it emits even a descriptive candidate
interval; the default is unset and therefore `DESCRIPTIVE_ONLY`. This is an
engineering floor, **not a validated scientific sample size**. Include wholly negative acquisitions in FP/frame
denominators and total acquisition count, never as pseudo-paired recall units.

The contrast is **observational**. Small targets can have different class,
orientation, thermal contrast, occlusion, distance, motion blur and annotation
quality from larger ones within the same acquisition. This design does
not isolate a causal native-resolution effect. Before freezing, specify
class-/contrast-/viewpoint-specific sensitivity, balance tables and any
covariate-standardized comparison with a demonstrated common-support region.
Without support, report the limitations rather than a purported physical
detection limit. H0: `Delta >= 0`; directional H1: `Delta < 0` is proposed,
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

#### D3/D4 validation threshold and exclusion decision matrix (2026-11-06; UNFROZEN)

This is a **pre-outcome candidate** for #51, not an author-approved
numerical operating-point freeze. The function
`arc_rgbt.p01_metrics.choose_validation_threshold` requires explicit
`split_role="validation"` and rejects all other roles **before** parsing
predictions; the role is only a caller declaration. The source admission
ledger, source-to-P01 class map, original split SHA, independent group
identity, and per-frame complete GT must still be verified outside the
function. A role flag alone cannot prevent a dishonest or mistaken caller
from passing held-out data. Test outcomes must not be inspected during
calibration.

| Candidate condition | Selector / downstream decision |
| --- | --- |
| Split declared `train`, `test`, blank or omitted | Reject before inspecting frame content; no threshold |
| Missing source-verified labels or invalid/unknown groups | Stop at external eligibility gate; do not pass frames to selector |
| Validation sample below provisional frame/group floor | `BLOCKED_VALIDATION_SIZE`; no cutoff |
| Too few candidate complete-negative frames or negative groups | `BLOCKED_NEGATIVE_EXPOSURE`; no cutoff |
| No score threshold with observed FP/frame <= proposed 0.10 and nonzero TP | `BLOCKED_NO_TRUE_POSITIVES` or `BLOCKED_NO_FEASIBLE_THRESHOLD`; no cutoff |
| Confidence ties around the budget boundary | Use `score >= threshold`: all predictions tied at the threshold are included; never partially retain a tie to meet budget |
| First valid lowest cutoff in sorted distinct validation scores plus 0 and 1 | `CANDIDATE_ONLY`, with observed validation FP/frame, TP and acquisition-bootstrap 95% diagnostic |
| Validation bootstrap upper 95% FP/frame bound above 0.10 | Preserve candidate cutoff and set `validation_fp_upper_ci_exceeds_ceiling=true`; review uncertainty, do not claim high-confidence budget control |
| Untouched held-out test FP/frame > frozen budget | `OPERATING_CONDITION_NOT_MET`; retain threshold and descriptive evidence, suppress candidate confirmatory inference; no retuning |

Threshold proposals and this software fixture matrix do **not** authorize
real-data calibration. Before freezing D3/D4, decide the exact FP/frame
budget, any acceptable validation uncertainty criterion, IoU 0.50 primary
and IoU 0.25 sensitivity, duplicate predictions, ignored/crowd/occluded GT,
and exact eligible positive/negative denominators. The prespecified
confidence-grid endpoint `1.0` cannot suppress predictions scored exactly
`1.0`; when no candidate yields both a valid budget and TP, the
operation remains blocked rather than inventing a no-detection cutoff.
The primary IoU and cutoff are shared across eligible small/reference bins
for a given LWIR detector. Candidate **scientific status is unchanged**:
`CONDITIONAL_DESIGN / UNFROZEN / G01 BLOCKED`.

#### Directional inference, bootstrap sensitivity and localization (candidate)

For the proposed directional hypothesis, the candidate one-sided group t
test uses exactly one `d_g` per verified acquisition and `G-1` degrees
of freedom. It compares the mean against the least-favourable null boundary
zero and rejects only if the one-sided 95% upper t bound is below zero.
The group-bootstrap interval below and the ordinary two-sided 95% group t
interval are **descriptive sensitivity outputs**. The simulation now reports
one-sided null-boundary rejection rates and alternative detection frequencies
separately from two-sided CI coverage, including Monte Carlo uncertainty.
The test is not authorized for empirical inference until its type-I error
and power are reviewed across source-informed group sizes, asymmetric
bounded outcomes, unequal target counts and dependence structures.
Zero-variance groups yield an undefined t decision. No test replacement or
post hoc change of alpha is permitted after held-out outcomes are observed.


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

`native_footprint_recall` computes per-GT footprint from supplied bounding boxes on the declared coordinate grid; its historical function name does **not** authenticate native sensor pixels. It also provides match flags,
paired-group target denominators, singleton-bin and excluded-acquisition
counts, an equal-group contrast, a target-pooled contrast restricted to the
same paired groups for exploratory weighting sensitivity, and a deterministic
descriptive bootstrap. Unlike aggregate
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
it cannot support Tier B physical native-sensor conclusions. A Tier A analysis may
still use a documented COCO export grid, but confirmatory group inference
separately requires verified independent acquisitions and a prospectively
justified finite-group decision procedure.

**Denominators and stop rules.** Every eligible source-annotated
target is counted in the recall denominator, including misses. Dataset-relative FP/frame uses
all eligible source-labelled test frames, including reference-negative frames; absence of a label does not prove true object absence.
Record unmatched predictions on both positive and negative frames. Do not
select an operating threshold from the test set. If validation permits only
the no-detection solution, or the required independent groups, native labels
or independently established scene absence is unavailable, report Tier B **BLOCKED** rather
than a physical detection-limit estimate; a limited Tier A descriptive result can still be reported against supplied GT. Only groups containing both
bins can contribute to the proposed paired bootstrap; if there are too
few or pilot precision is insufficient,
report DESCRIPTIVE_ONLY without a confirmatory interval. Author approval
is still required for bin edges, IoU,
FP/frame, group minimum and inference plan before freeze.

#### Synthetic cluster precision audit before freeze (2026-11-02)

A deterministic [acquisition-level precision pilot](../analyses/README.md)
now compares two-sided percentile bootstrap and cluster t interval
coverage with a **separate one-sided alpha-0.05 group t test** across
10/20/40 independent paired groups, 4/20 targets per bin, and generating
contrasts 0 and -0.15. With `--stress`, asymmetric group contrasts and
single-target bins supplement unequal denominators and shared probability
shocks. The pilot reports empirical simulation rates of directional
false positives at the null boundary and directional detection under the
synthetic alternative, with finite Monte Carlo uncertainty. It does not
establish type-I control or power for any real source. The pilot flags possible
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

### Freeze-readiness evidence ledger (2026-11-04)

**Author's interim design decision (2026-11-04): CONDITIONAL_DESIGN / UNFROZEN / DATA BLOCKED.**
This ledger is a dated preparatory review for [Issue #35](https://github.com/MatPomGit/arc-rgbt/issues/35),
not an author-approved preregistration. The final protocol revision SHA
must be recorded after external review and final approval, not copied from
an earlier software CI run.

| Freeze gate | Evidence as of 2026-11-04 | Required exit evidence |
| --- | --- | --- |
| Research question and primary estimand | Candidate D1/D2/D10 above and [hypotheses](../hypotheses/README.md) are written; independent methodological sign-off missing. | Author approves cohort, observational interpretation, primary directional test and compatible alpha/CI rule; #49/#50/#53. |
| Original LWIR source, rights and sensor geometry | Preliminary source shortlist only in [datasets](../../../docs/experiments/datasets.md); no original release admitted. | Exact original release and annotation rights, LWIR spectral band, native grid/transform and independent group IDs verified; #45/#46/#36. |
| Annotation and negative exposure | Proposed GT matching and all-frame FP rules exist, but original labels and complete negative frames remain unverified. | Source-specific class map, visible/amodal and ignore policy, supplied-reference negative-frame definition, exclusion log and explicit label-completeness limitations; no human QA requirement; #47. |
| Pairing, representativeness and precision | The estimator now reports singleton bins, excluded acquisitions and paired-only pooled weighting sensitivity; synthetic directional testing is available. Authentic group counts, common support and source-informed type-I/power calibration remain absent. | Counts-only independent acquisition inventory, within-bin target minimum, effect-size justification, group heterogeneity, directional type-I/power and descriptive CI coverage decision; #48/#49/#50. |
| Threshold and multiplicity | Numerical FP/frame, IoU and footprint values are **candidates**, not approved choices. | Author-approved D3/D4 and inference/multiplicity rules before test access; #51/#53. |
| Publication fit and novelty | Prospective ~250-word scope text and [unsent editorial package](../README.md); fit provisional. | External originality/scope appraisal and approved inquiry if desired; #52. |
| Independent review and author sign-off | No independent post-fix scientific approval; no signed decision or final commit SHA. | Dated reviewer identity and disposition, author identity/decision, exact reviewed protocol commit SHA recorded in #35 and #53. |

**Permitted outcomes at the 2026-11-13 decision:**

- `FROZEN`: only after real source eligibility, reviewable
  feasibility/precision, all numerical and exclusion decisions, independent
  scientific review and explicit author approval are documented **before**
  accessing held-out detection outcomes.
- `CONDITIONAL_DESIGN`: the proposed methods are reviewable but actual
  source admission and/or precision remain unresolved. This is **not** a
  completed preregistration and does not permit confirmatory held-out access.
- `NO-GO`: the proposed question has no defensible data/source trajectory
  or the methodological prerequisites cannot be met; physical LWIR limits
  are not to be claimed. Any simulation-only alternative requires a new
  novelty and journal-fit appraisal.

**Decision record:** status = `CONDITIONAL_DESIGN`; decision date =
`2026-11-04`; decision source = **author's explicit chat acceptance of the
conditional design status**, documented in [Issue #35](https://github.com/MatPomGit/arc-rgbt/issues/35).
This decision authorizes continuing design/source screening only. It does
**not** approve the proposed numeric FP/frame, footprint, IoU, group-size or
alpha settings; it is not a signature approving a frozen preregistration.
Independent scientific reviewer = `PENDING`; frozen-protocol approval =
`PENDING`; final frozen protocol commit SHA = `PENDING`; admitted original
LWIR data release and rights = `NONE`; source-informed precision evidence =
`NONE`; outstanding issues = #10, #36, #45-#51, #53.
Do not access untouched test outcomes or mark Issue #35 completed while
mandatory freeze gates remain open.

### Decisions still required before freeze

- [ ] Identify lawful original dataset release(s), sensor calibration,
      complete labels and independent acquisition identifiers (#10, #36).
- [ ] Fix the numerical FP/frame ceiling, IoU, footprint bins, minimum
      within-bin target counts and independent-group power/precision criteria
      *without looking at held-out outcomes*.
- [ ] Freeze the paired-group estimand, overlap policy, class/contrast balance,
      validation exposure and threshold candidate grid.
- [ ] Audit one-sided t-test null-boundary calibration and synthetic power,
      two-sided CI coverage, paired-bin support/weighting, missingness and
      ignore-region rules; freeze the sole primary test and multiplicity.
- [ ] Obtain explicit author approval of the frozen protocol and store
      its commit SHA and date in [issue #35](https://github.com/MatPomGit/arc-rgbt/issues/35).
- [ ] Obtain independent evidence GO before reporting physical limits
      or claiming a submission-ready manuscript (#24, #29).

**Current evidence status: BLOCKED for confirmatory physical detection-limit
claims.** This draft can guide dataset screening and analysis implementation
without pre-empting the required preregistration.

## Source-annotation evaluation convention (#47; 2026-11-07)

1. **GT:** supplied versioned annotations are the declared reference. Freeze car/person/rider interpretation, ignore/crowd/occlusion rules, source box convention and class-aware one-to-one IoU BEFORE held-out outcomes. Use source documentation, not new handwritten labels.
2. **Negative frames:** absence of a reference box is a **reference-negative**, not independently verified object absence. FP/frame = unmatched detections divided by eligible frames, relative to source GT, with this limitation stated in manuscript and figures.
3. **Samples and splits:** track source/release/config SHA, source-provided acquisition IDs where available, deterministic group-disjoint split mapping and duplicate leakage constraints. Video IDs are not by themselves proof of independently acquired physical scenes. No new human image-adjudication gate.
4. **Results:** record bins, GT and frame denominators, exclusions, TP/FN/FP, threshold selection on validation only, source-relative outcomes, supported uncertainty, null/negative findings. If data or group assumptions cannot support a confirmatory estimate, output DESCRIPTIVE_ONLY. Never fabricate measurements.
5. **Claim boundary:** physical native optics, thermal calibration, range or robot deployment require Tier B evidence and separate author decision. E00 remains simulated. Source annotation integrity is never inferred from passing synthetic regression tests.

The former 2026-11-06 reviewer plans and optional FLIR two-reviewer toolchain are **retired from mandatory P01 execution**. Historical code and source-inventory findings remain recoverable in Git history and issues #46/#47 but are not prerequisites. Independent scientific review means calculation/method/manuscript verification, not re-annotation.

