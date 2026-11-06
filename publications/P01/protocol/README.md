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

## D1/D2/D10 decision sheet for author review (2026-11-03; UNFROZEN)

This sheet resolves the *candidate interpretation* of the P01 primary
question, not its scientific approval. No source-verified acquisition
inventory, non-test pilot variance or independent method sign-off is
available. It therefore **must not** be called preregistration.

| ID | Candidate decision | Evidence still needed before freeze |
| --- | --- | --- |
| D1: target population | Lawfully usable original-grid LWIR acquisitions with complete eligible GT and verified acquisition identifiers. For the primary contrast, an acquisition contributes only when it contains at least one eligible target in **each** of the two prespecified native-footprint bins. Frames with zero GT remain in FP/frame assessment. | Original archive, spectral band, annotation/negative completeness, independent group keys and class mapping (#45-#48). |
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
| Population | Verified native LWIR objects from independent acquisition groups with fully labelled positive and negative frames; RGB only secondary | PENDING source and class mapping |
| Primary estimand | Equal-acquisition-weighted mean of within-group small minus reference LWIR GT recall differences, both bins in each contributing acquisition | PENDING eligible groups and author freeze |
| Independent unit | Original acquisition/scene or flight group; adjacent frames from one acquisition are not independent replicates | PENDING source IDs |
| Operating point | Select detector thresholds on validation groups only, targeting the same FP/frame ceiling; never tune on held-out test data | PENDING numerical ceiling |
| Native footprint | Derive visible annotated target width/height/area on each modality's **original** grid; retain calibrated geometry and visibility metadata; do not use resized detector input as native footprint | PENDING native grid and optics |
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
| Primary modality | Physically acquired native **LWIR** only. RGB is a prespecified secondary comparison; fusion belongs to P02 unless a separate P01 ablation is justified. | Native LWIR and original labels verified |
| Independent outcome | Within-acquisition **IoU-0.50 localization-qualified** GT recall difference (small minus reference), averaged equally across acquisitions. Expected sign negative, no causal interpretation. | Source-verified acquisitions with both bins and complete labels |
| Footprint proxy | `s = sqrt(w_native * h_native)` in pixels from the original-grid target bounding box. Small: `s < 8`; intermediate: `8 <= s < 16`; reference: `s >= 16`. Only small vs reference is confirmatory. | Original grid and annotation conventions independently checked |
| Match rule | Class-aware, score-descending one-to-one IoU `>= 0.50`, original prediction order breaks ties. Each GT is counted once and assigned to a bin by its **original-grid GT box** before matching. | [P01 metrics tests](../analyses/README.md), plus shared #23 reference audit |
| False-alert budget | Candidate `0.10 FP/frame`. Choose lowest validation-only score threshold meeting observed ceiling using sorted unique prediction scores plus 0 and 1; no zero-TP solution. Keep fixed on test; this is not a guarantee of future FP/frame. | Complete validation frames and adequate exposure/groups |
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
original-grid GT objects, including misses. Acquisitions lacking one bin
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

`native_footprint_recall` provides per-GT native footprint, match flags,
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
| Annotation and negative exposure | Proposed GT matching and all-frame FP rules exist, but original labels and complete negative frames remain unverified. | Source-specific class map, visible/amodal policy, blinded QA, ignore/exclusion log, complete negative-frame audit; #47. |
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

## Annotation eligibility and negative-frame contract (#47; proposal v0.2.0, 2026-11-06)

This is a **pre-outcome decision proposal**, not verified annotation
completeness, an accepted source, or a frozen preregistration. The original
release, exact annotation version, rights and independent acquisition keys
are still unavailable. The rules below must be signed off before accessing
held-out detection outcomes.

### Reference population and matching

1. Record the owner-defined class taxonomy, source label identifiers and
   explicit mapping to the prespecified P01 target class. Unmapped classes
   are **UNKNOWN**, not negatives; never silently collapse classes or infer
   missing labels from detector output.
2. Preserve the original box coordinate convention, visible versus amodal
   extent, image orientation, truncation and occlusion attributes. Native
   footprint bins require independently verified original-detector geometry;
   aligned/export boxes alone are insufficient (#46).
3. Freeze an IoU threshold and a deterministic confidence-ranked one-to-one
   match rule on non-test material. A ground-truth object can match at most
   one prediction. Duplicate predictions are FP unless an independently validated, frozen
   ignore-region policy explicitly exempts them; they are never additional TP.
4. Decide *before test* whether crowd/ignore regions, uncertain boxes,
   heavily occluded and cut-off objects are evaluable, ignored or excluded.
   Record each reason and its effect on the GT denominator. An ignore
   region is not evidence that all other image regions are fully annotated.

### Complete-frame audit and FP/frame denominator

For each original frame record exact source/annotation release hashes,
acquisition and frame ID, original dimensions, target-class mapping and
affirmative evidence of annotation coverage. The three *proposed*
evidence-backed frame states are:

| State | Required evidence | Eligible outcome |
| --- | --- | --- |
| `complete_positive` | Exhaustive target-class annotation independently verified, at least one eligible P01 target | FP/frame and target recall |
| `complete_negative` | Exhaustive target-class annotation independently verified, zero eligible P01 targets under the frozen policy | FP/frame only |
| `unknown` | Missing, partial, ambiguous or unverified annotation | Neither confirmatory FP/frame nor recall |

`complete_negative` means target-class negative, not necessarily
object-free. An empty annotation file, missing label record or zero mapped
objects alone is **not** evidence of exhaustive target coverage. A frame
containing only ignored/ambiguous targets is not automatically negative.
Classify independently of detector predictions; store unknown counts and
acquisition IDs separately. A positive frame contributes to FP/frame only
if its coverage is verified complete.

Prospective FP/frame equals unmatched **in-scope P01 target-class**
predictions (including duplicates, subject to the frozen ignore policy)
divided by **all completely annotated eligible original frames**,
positive and verified negative. Define the class-scoping rule before
testing; do not silently include unrelated class predictions in FP or
delete unmatched P01 predictions. Fully annotated frames from groups
excluded from the paired-bin recall estimand still contribute to FP/frame.
Recall denominators contain eligible target GT only. Report FP counts,
frame counts and ratios by source, split and acquisition. Choose the score
threshold using verified *validation* frames only; freeze it before
untouched test evaluation. If completeness or negative-frame evidence
cannot be verified, mark the confirmatory FP/frame operating point
**BLOCKED**; never claim that 0.10 FP/frame was achieved.

### Blinded QA and adjudication before outcomes

- Before model predictions or held-out performance are viewed, freeze a
  reproducible, acquisition-stratified random audit seed and sample size
  based on the actual non-test frame inventory. Include both owner-labelled
  positives and candidate empty frames; preserve independent source groups.
- Two reviewers independently inspect sampled frames using the original
  annotation convention, blinded to model outputs and to one another's
  decisions. Record missing objects, class mismatch, box extent, duplicates,
  ignore/crowd ambiguity and apparent incomplete negatives.
- Reconcile disagreements against source documentation; unresolved cases
  remain `unknown`. Record raw decisions, reviewer roles, adjudication
  date and exact release/manifest hashes in an external rights-compliant
  evidence record, not personal data or images in Git.
- Fix an allowable uncertainty/disagreement criterion **before** the audit
  results are known; none is currently justified by source evidence.
  A small QA sample cannot establish zero missing annotations. If the
  prespecified criterion fails, stop admission and correct/re-audit the
  source without inspecting held-out detector outcomes.

### Required pre-test exclusion and denominator ledger

For each candidate release record counts of total frames, verified
positive frames, verified fully negative frames, unknown/partial frames,
eligible GT by native-footprint bin, ignored/ambiguous objects, duplicate
annotation IDs, and acquisition groups with both target bins. Report
mutually exclusive exclusion reasons and source/acquisition IDs, plus
whether excluded groups' frames remain eligible for FP/frame (only when
fully annotated). Freeze the source-specific ledger, class map, matching
rule, QA plan, split hashes and reviewer decision before held-out analysis.
Do not infer any counts from the current metadata-only screening.

### Executable-contract boundary (not implemented by this PR)

`arc_rgbt.p01_metrics.native_footprint_recall` and
`choose_validation_threshold` accept the caller's global declaration
`annotation_status="complete"` but do **not** independently verify
per-frame annotation coverage, source rights, class mapping, acquisition
independence or original geometry. In particular,
`choose_validation_threshold` counts empty `ground_truth` lists as
negative frames; the declaration is not evidence. The shared
`arc_rgbt.bench.evaluate` counts all supplied classes and has no
crowd/ignore-region semantics. Existing box matching is confidence-ranked,
class-aware and one-to-one, with input order breaking score ties.

**Fail closed:** never pass unchecked source frames to either metric.
Verify the external eligibility ledger *before* preparing its input, and
restrict it to the frozen target class under a reviewed mapping. Where
ignores, crowd regions, uncertain GT or occlusions cannot be represented
without changing FP/GT semantics, mark
`BLOCKED_UNSUPPORTED_ANNOTATION_POLICY` rather than silently removing
boxes or relabelling frames. A source-specific adapter requires separate
implementation, tests and scientific approval. This PR only documents
the future admission contract.

### Pre-outcome eligibility checklist (v0.2.0; pending)

- [ ] Document lawful image **and annotation** rights, exact original
      release, annotation version, hashes and independently verifiable links.
- [ ] Verify LWIR band, original sensor grid, image transforms,
      visible/amodal annotation convention and acquisition keys (#46).
- [ ] Freeze source-to-P01 class map, non-target handling, IoU/score
      matching, duplicates and ambiguous/ignored GT rules (#51).
- [ ] Verify complete target-class annotation on **every** included
      original frame, including candidate empty frames; assign one of
      the three states above from evidence, not detector output.
- [ ] Confirm unique frame and GT IDs, group-disjoint train/validation/test
      partitions and split manifest hashes. Flag adjacent-frame leakage.
- [ ] Freeze a reproducible, acquisition-stratified QA seed and sample
      size for positive and candidate-negative frames, two independent
      blinded reviewers, adjudication procedure and *numerical*
      discrepancy/uncertainty acceptance criterion **before QA results**.
- [ ] Retain both original QA decisions and adjudications in a
      rights-compliant evidence record; unresolved labels stay
      `unknown`, and a failed QA gate blocks admission.
- [ ] Reconcile by source, split and acquisition:
      `total_frames = complete_positive + complete_negative + unknown`;
      eligible GT by footprint bin; frames and GT excluded by reason;
      paired-bin acquisitions; fully annotated FP/frame exposure.
- [ ] Record author approval, independent reviewer decision, protocol
      SHA and dates **before held-out outcomes**; open #35/#36/#47/#53
      until their own required evidence is available.

### Independently reviewable exclusion and rejection log (v0.2.0)

Maintain one append-only, source-specific decision log, with one row per
source release, acquisition, frame or GT decision. Store its redacted
version and SHA in a rights-compliant evidence location, linked from
#47/#36; do not put restricted images or personal information in Git.
Required row fields:

| Fields | Contract |
| --- | --- |
| `source_sha`, `annotation_sha`, `split_sha`, `evidence_ref` | Immutable release/labels/split and completeness evidence; missing values block admission |
| `unit_type`, `unit_id`, `acquisition_id`, `split` | Stable non-identifying decision key and train/validation/test membership |
| `frame_state`, `decision`, `primary_reason`, `secondary_reasons` | One state; `INCLUDE`/`EXCLUDE`/`HOLD`; exactly one exclusion reason counted |
| `eligible_gt_small`, `eligible_gt_intermediate`, `eligible_gt_reference` | Independently audited GT counts, not model-derived counts |
| `fp_frame_eligible`, `paired_recall_eligible` | Separate flags; no paired GT does not itself disqualify fully annotated FP exposure |
| `reviewer_a_ref`, `reviewer_b_ref`, `adjudication_ref` | Blinded QA decisions and resolution records |
| `rule_version`, `protocol_sha`, `decision_date` | Audit trail fixed before test-outcome inspection |

For mutually exclusive **frame** rejection counts choose the first
applicable primary reason in this fixed order:
`RIGHTS_OR_RELEASE`, `NATIVE_GRID_OR_GROUP_UNVERIFIED`,
`CLASS_OR_IGNORE_UNRESOLVED`, `ANNOTATION_INCOMPLETE`,
`SPLIT_LEAKAGE`. Preserve other applicable reasons in
`secondary_reasons`, without counting one excluded frame twice.
`NO_PAIRED_BINS` is *acquisition-level recall exclusion only*, never a
reason to remove otherwise fully annotated frames from FP/frame.
Reconcile source/split/acquisition totals and independent review
decisions before use.

**Log state on 2026-11-06: `SOURCE_QA_NOT_EXECUTED`.** No independently
admitted source release, two-reviewer blind audit, numerical QA acceptance
criterion or author sign-off exists. Metadata screening below does not
replace source-specific acceptance records.

### FLIR ADAS v2 local metadata preflight (2026-11-06; operator-reported, not verified admission)
### FLIR ADAS v2 local metadata and export reconciliation (2026-11-06; source not admitted)

This is a read-only **operator-executed** FLIR ADAS v2 12-part archive
screening of thermal training and validation metadata, subsequently
cross-checked for aggregate arithmetic using the two provided JSON audit
reports (v1 SHA-256 `916180554efa19058872e5457d83ff20caacbf26561d258771cf31242fdd8360`;
v2 SHA-256 `277475abaca08f634c09a1268593a38a28836f15caa0810c3556fd042319bde9`).
The reports and raw dataset remain outside Git. These descriptive counts
are **not** independently repeated source inspection, blinded source QA
or physical detection results. The held-out test annotations were not
opened.

| Metadata check | Thermal train | Thermal validation |
| --- | ---: | ---: |
| Frames with paired index/COCO identities | 10,742 | 1,144 |
| Conservator `index.json` GT | 176,063 | 16,786 |
| COCO `coco.json` GT | 175,040 | 16,696 |
| Net original minus COCO | 1,023 | 90 |
| Frames with unequal GT counts | 645 | 50 |
| Frames missing QA status | 1,992 | 183 |
| Frames flagged | 52 | 1 |
| All-class COCO empty (not verified negative) | 264 | 16 |
| COCO no-`person` / no-`car` candidates | 2,537 / 918 | 325 / 97 |
| Original index boxes exceeding image bounds (needs policy) | 196 | 18 |

**Aggregate class mapping fully reconciles the count difference:**

| Original label operation inferred from totals | Train | Validation |
| --- | ---: | ---: |
| `face` absent in COCO | 752 | 73 |
| `license plate` absent in COCO | 270 | 17 |
| `bird` absent in COCO | 1 | 0 |
| **Net omitted count** | **1,023** | **90** |
| `rider` counted in COCO `person` | 5,951 | 161 |
| `animal` counted in COCO `deer` | 8 | 0 |

After applying these operations, **every aggregate category tally
matches exactly** between the Conservator original and COCO in both
partitions. In particular, original `person` + `rider` =
50,478/4,470 COCO `person`; original `car` = COCO `car`
73,623/7,133. These are **strong count-level export explanations**,
not proof that each individual annotation was mapped correctly.
The user-reported COCO-`person`-positive but original
literal-`person`-absent frame counts (773 train / 28 val) are compatible
with `rider` remapping. A P01 endpoint defined as *pedestrian* is
not interchangeable with an endpoint defined as all COCO `person`
(including riders). An explicit owner-approved target definition and
per-instance class policy must be frozen before metrics.

**Geometry reconciliation, separate from omitted-class arithmetic.**
Exact bbox matching left original-only 6,002/466 and COCO-only
4,979/376 records. A *diagnostic-only*, unvalidated greedy
IoU-tolerant matching of the previously unmatched pairs produced:

| IoU status among non-exact boxes | Train | Validation |
| --- | ---: | ---: |
| Matched with IoU >= 0.95 | 4,416 | 307 |
| Matched with 0.50 <= IoU < 0.95 | 484 | 61 |
| Original unmatched after IoU >= 0.50 | 1,102 | 98 |
| COCO unmatched after IoU >= 0.50 | 79 | 8 |

Remaining original-minus-COCO records equal 1,113, consistent with
the class mapping above, but **1,200 original and 87 COCO boxes
remain unresolved by the diagnostic geometry matcher**. No per-object
missing-label count, class-disagreement verdict, annotation
uncertainty bound or rejection ledger may be inferred from this
greedy pairing. Differences may include altered box extents,
truncation, duplicate/overlapping annotations, category filtering
and sub-0.5 overlaps. Original out-of-bounds bbox entries might
encode intentional truncation; they are not automatically erroneous
without source-specific annotation conventions. Freeze explicit
`rider` and `animal` mappings and bbox clip/ignore semantics
**before** an independent per-frame review.

All 11,886 original train/validation frame keys aligned between
index and COCO; no `video_id` is shared across these two partitions.
That does not establish independence of physical acquisitions or
exclude neighboring-scene leakage. Metadata-only within-video
small/reference paired candidates: `person` 91/12 and `car`
122/17 (train/validation), not independent acquisition counts.
No COCO target-absent frame was contradicted by original target-label
presence under the **audit script's proposed raw label comparison**;
this is not verified exhaustive negative-frame annotation. Owner QA
status `approved` also does not prove completeness.

The archive contained 46,447 unique ZIP members. The **v2 full-member
ZIP CRC passed**, consistent with readable uncorrupted archive contents.
The earlier v1 report computed SHA-256 for the 12 local ZIP parts,
but neither their digests nor the original source release/version
were authenticated against owner-supplied checksums. Six sampled
thermal TIFF headers reported 640x512, single-channel, 16-bit
storage with lossless LZW. Teledyne FLIR publicly specifies Tau 2
640x512 and pre-AGC 14-bit thermal TIFF in this dataset
(<https://oem.flir.com/solutions/automotive/adas-dataset-form/>).
This supports plausible sensor format, **not** a proven
raw-sensor-coordinate correspondence for every COCO bbox.
Owner image/annotation terms for the exact release remain
unverified; `coco.json` had no declared licence entries in the
reported screening. Free download does not itself grant unrestricted
reuse.

**Unresolved STOP/GO evidence:** prove source image and annotation
licences/owner release; verify native TIFF values, image coordinate
transforms and original box conventions; independently inspect a
predeclared stratified set of QA-missing, flagged, filtered/
geometry-discordant, and potential negative frames with two blinded
reviewers and numeric acceptance criteria; adjudicate
`person` vs `rider` and cutoff/occlusion policy; verify physically
independent acquisitions and near-duplicate split separation.
Do not access held-out detector outcomes to adjust these rules.
No frame may be promoted to `complete_positive` or
`complete_negative` solely by `approved`, `isEmpty`,
a complete CRC, or category count identity.

**Current scientific status: `METADATA_REVIEW_REQUIRED /
CONDITIONAL_DESIGN / UNFROZEN / G01 BLOCKED`.**
No empirical FP/frame denominator or model-detection-limit claim
is yet admitted.


**Gate:** #47 is only a prepared convention until a lawful exact release,
independent QA and the author-approved source-specific rules exist. #36
and #57 own dataset admission; #35/#53 own protocol freeze. Current
status: `CONDITIONAL_DESIGN / UNFROZEN / G01 BLOCKED`.

