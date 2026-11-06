# P01 reproducible analyses

Implemented: `summarize_e00.py` consumes generated E00 manifest/CSV and writes a SHA-256-linked JSON summary, explicitly marked `simulated`.

```bash
arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00
python publications/P01/analyses/summarize_e00.py --experiment-dir reports/E00 --output reports/P01/e00_summary.json
```

For real camera studies, new scripts and preregistered analyses will be required. These E00 point estimates are not empirical detection performance.

## Native LWIR footprint analysis contract (prospective, UNFROZEN)

`arc_rgbt.p01_metrics.native_footprint_recall` accepts existing Bench-style
GT/prediction frames, a parallel list of acquisition IDs,
`annotation_status="complete"` and `grid_origin="original_native"`.
It returns per-GT IoU-matched flags and original-grid footprint bins,
including misses, all-frame FP/frame, and equal-acquisition-weighted
small-minus-reference differences. It also returns per-paired-acquisition
target counts, singleton-bin and excluded-acquisition counts, and an
exploratory **paired-only target-pooled contrast**. Bin-specific pooling
weights can change acquisition composition, even when all per-group
contrasts are zero: this is an alternate estimand, not only reweighting.
The primary difference is descriptive by default. A 2000-replicate
candidate bootstrap interval requires >=10 paired groups **and** an
explicit `minimum_targets_per_bin >= 2` satisfied in every paired
acquisition. This computational floor is not a scientific sample-size
approval; without it the interval is suppressed. An interval is also suppressed
if all observed paired-acquisition contrasts are identical: a zero-width
bootstrap distribution is not evidence of known population precision.
Reports expose `candidate_interval_degenerate` and
`candidate_interval_suppression_reason` separately from the numerical
paired-bin support gate. A computed interval is descriptive,
not a calibrated directional test. `choose_validation_threshold` now requires
an explicit `split_role="validation"` keyword before inspecting frame data:
`train`, `test`, omitted or unknown roles are rejected. This is a
**caller-declared guard**, not proof that the frames were actually allocated
to the validation split; independent split-manifest and leakage verification
remain mandatory. The function selects a validation-only candidate cutoff
with a 0.10 FP/frame point ceiling, provisional >=10 groups and >=200 fully
labelled frames, **including >=20 fully negative frames in >=2 groups**, and
no trivial zero-TP solution. Its confidence threshold rule includes **all**
predictions tied at the cutoff (`score >= threshold`). Reports retain
`split_role="declared_validation_unverified"` and the candidate selection policy. It also reports
an acquisition-bootstrap CI for observed validation FP/frame; its upper
bound can exceed the candidate budget even if the point estimate meets
it. The held-out metric helper retains negative-only acquisitions in
FP/frame counts and marks `OPERATING_CONDITION_NOT_MET` if the test rate
is excessive, suppressing any candidate confirmatory CI.
Neither function verifies real original images, group independence,
annotation completeness, optical calibration, permissions or test quality;
both explicitly mark `empirical_admission=false`. The executable
synthetic regression cases are in `tests/test_p01_metrics.py`.
The [study protocol](../protocol/README.md) retains all scientific gates.

## Pre-freeze acquisition-cluster precision pilot (synthetic)

Run the dependency-free [precision pilot](pilot_cluster_precision.py) before
author approval of the candidate minimum of ten paired acquisitions:

```bash
python publications/P01/analyses/pilot_cluster_precision.py --trials 250 --bootstrap 2000 --seed 20261102
```

The JSON printed to standard output is explicitly
`synthetic_precision_audit_only`. It evaluates 10, 20 and 40 independent
paired acquisition groups, with 4 or 20 labelled targets per footprint bin
per group, under population group-mean recall contrasts 0 and -0.15.
Reference detection probabilities vary uniformly between 0.35 and 0.75
across groups; small-target probabilities have the specified mean contrast
and a uniform acquisition perturbation of +/-0.08. Each trial draws new
Bernoulli outcomes. The true mean contrast is known from the generating
model, so repeated trials estimate interval coverage, mean width and the
frequency of an upper interval limit below zero.

The script compares **two-sided 95%** whole-acquisition percentile
bootstrap and acquisition-level Student t intervals. Independently, it
evaluates the **proposed one-sided alpha-0.05 acquisition-level t decision**
against the boundary of `H0: Delta >= 0`. The decision rejects only
when its one-sided 95% upper confidence bound lies below zero; zero
sample variance yields an undefined test rather than a positive finding.
For `Delta=0` scenarios the rejection fraction estimates synthetic
type-I error at the null boundary; for `Delta=-0.15` it estimates
directional detection frequency. Both include Wilson Monte Carlo
uncertainty. These are methodological stress tests, not preregistration
or data-derived sample-size justification. Under some simulated ten-group settings, nominal 95% percentile
coverage falls below 95%; ten groups cannot be treated as a sufficient
confirmatory minimum merely because the software can compute an interval.
The t comparison is not automatically a validated replacement.

Neither model includes detector score selection, FP/frame constraints,
imaging physics, correlated targets beyond group probability heterogeneity,
missing annotations, source rights or real sensor measurements. The
[canonical P01 protocol](../protocol/README.md) requires source-informed
precision assumptions and author sign-off before a confidence-interval
method, effect threshold or minimum group count is frozen. No generated
JSON, images or results are committed.

### Methodological sensitivity and Monte Carlo precision

The script accepts `--directional-only` to skip both descriptive
confidence-interval families and rapidly estimate directional rejection.
For example, use `--trials 5000 --stress --directional-only` to reduce
Monte Carlo uncertainty without performing bootstrap draws; the JSON
reports `directional_only=true`, no descriptive methods, and zero
bootstrap draws. For CI coverage, omit this flag and run the full
`--trials 250 --bootstrap 2000 --stress` study. The full run is not part
of default PR CI and must have separate exact-SHA execution evidence.
The script reports `nominal_targets_per_bin` and actual per-bin group
count minima, medians and maxima.

The same script accepts `--stress` to append 24 additional
**synthetic-only** scenarios: 12 with unequal group/bin denominators and
a shared acquisition probability shock, and 12 with asymmetric zero-mean
contrast shocks plus groups containing only one GT per bin. These stress
both interval coverage and one-sided test calibration when paired-group
differences are skewed or denominators highly unbalanced. The generating
population mean contrast remains fixed. The original 12 balanced scenarios
remain available when the flag is absent.

```bash
python publications/P01/analyses/pilot_cluster_precision.py --trials 250 --bootstrap 2000 --seed 20261102 --stress
```

Two-sided CI coverage, two-sided negative upper bounds and **one-sided
directional rejection** each include 95% Wilson Monte Carlo intervals and
MCSE. These intervals describe uncertainty of simulation-based rates,
**not** confidence in physical LWIR performance. With only 250 trials they are
relatively wide; no interval family or group count is approved by this pilot.
The stress model remains intentionally simplified and does not evaluate
FP/frame threshold selection, real labels, optics or scene dependence. It may
guide a source-informed, pre-unblinding follow-up under #49/#48, not a
confirmatory preregistration or empirical GO.


## Minimum paired-bin support before a scientific freeze

The estimator currently accepts at least one GT in each bin to calculate
a per-acquisition difference. Candidate intervals are suppressed by default
until an explicit computational count floor (at least two targets in each
bin of every paired acquisition) is provided; this is **not** a validated
scientific sample-size minimum. The report exposes
`paired_group_target_counts`, `paired_groups_with_singleton_bin`,
`acquisitions_excluded_from_paired_contrast` and the exploratory
`paired_object_pooled_delta_sensitivity`. The pooled sensitivity is
restricted to the **same paired acquisitions**, preserving the cohort
but changing the relative contributions of acquisitions separately in
each bin. This sensitivity measures an estimand/composition shift, not
purely a single set of alternative acquisition weights. The
`acquisitions_excluded_by_reason` field lists acquisition IDs separately
for groups with no targets, a small bin without reference, a reference
bin without small, and intermediate-only GT. These are primary-contrast
exclusions, not exclusions from FP/frame exposure.

Before any confirmatory analysis, #48/#49/#50 must document an authentic,
**non-test** acquisition inventory, per-bin count distributions, class and
viewpoint common support, group-level variance/effect assumptions, and a
source-informed minimum count and group-size decision with evaluated type-I
error, power and interval coverage. A small software-sufficient group count
cannot authorize empirical inference; if feasibility or overlap is inadequate,
report `DESCRIPTIVE_ONLY`. No frozen sample-size or alpha approval is
implied by the synthetic pilot.


## Pre-test acquisition-group feasibility from metadata (#48)

Run the offline `audit_group_feasibility.py` after independently preparing a
**local, non-test** frame-count inventory. It never opens source images,
model predictions or held-out test outcomes. This audit is a
**count-only planning aid**; even an overlap-free report cannot prove true
independent physical acquisitions, source rights, complete annotations,
native geometry, sample-size sufficiency or scientific GO.

Input schema v1 has `schema_version: 1`, nonempty `source_release`,
`group_basis` (`video_id_proxy` or `declared_acquisition`),
`grid_basis` (`export_grid_proxy`, `declared_native` or `unknown`),
required `target_class_spec_sha256` and `footprint_bin_spec_sha256`
(two lowercase, 64-character SHA-256 hex digests of locally versioned
**target-class mapping** and **footprint-bin definition** contracts),
and a nonempty `frames` array. A target-class contract must state
the selected source label IDs, remaps (including rider handling),
exclusions and target definition. A bin contract must state native/export
grid, formula and units for the footprint, exact cutoff values and
strict/inclusive interval boundaries. Record the exact bytes of both
contracts and hash them locally before producing counts; hashes supplied
by the operator are not independently checked by this tool.

Each frame row must contain exactly:

- `frame_id`, `group_id` (nonempty unique frame IDs; groups may recur).
  IDs are opaque and **case-sensitive**, but must already be in Unicode
  NFKC form and must not contain whitespace or invisible control/format
  characters; noncanonical variants are rejected rather than silently
  treated as different groups;
- `split`: `train` or `validation` only. `test` is rejected;
- `target_state`: `candidate_positive`, `candidate_negative` or
  `unknown` (all provisional; no state implies audited label coverage);
- candidate `small`, `intermediate`, `reference` GT-bin counts (three
  nonnegative integers for positive/negative candidates, three `null`
  values for `unknown`). Bins reflect the declared grid basis **only**;
- `viewpoint` and `contrast` (nonempty operator-declared category
  strings, or **exactly lowercase `unknown`** when unavailable).
  Leading/trailing whitespace, Unicode compatibility aliases and
  `Unknown` / `UNKNOWN` are rejected, not counted as known categories.

The count labels describe the proposed P01 target class **only** under an
operator-supplied taxonomy, which is still subject to #47/#51 approval.
Use `candidate_negative` only for records with zero candidate GT:
this is **not** an independently verified complete negative frame.
With `grid_basis: unknown`, nonzero footprint counts are rejected.
Never derive candidate counts from held-out detector outcomes.

Minimal synthetic input example:

```json
{
  "schema_version": 1,
  "source_release": "synthetic-only",
  "group_basis": "video_id_proxy",
  "grid_basis": "export_grid_proxy",
  "target_class_spec_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "footprint_bin_spec_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "frames": [
    {
      "frame_id": "f1", "group_id": "v1", "split": "train",
      "target_state": "candidate_positive",
      "small": 2, "intermediate": 0, "reference": 1,
      "viewpoint": "front", "contrast": "unknown"
    },
    {
      "frame_id": "f2", "group_id": "v2", "split": "validation",
      "target_state": "candidate_negative",
      "small": 0, "intermediate": 0, "reference": 0,
      "viewpoint": "unknown", "contrast": "unknown"
    }
  ]
}
```

The repeated-`a` and repeated-`b` digests above are **synthetic
placeholders only**. Real inventories must use the SHA-256 values of
actual, versioned local contract files. Changing the class mapping or
a bin cutoff must change its spec digest and therefore the full
`input_inventory_sha256`, even when the numeric rows happen to match.
Neither fingerprint certifies correctness or source eligibility.

```bash
python publications/P01/analyses/audit_group_feasibility.py \
  --input LOCAL_NONTEST_COUNTS.json --output LOCAL_GROUP_AUDIT.json
```

The tool refuses to overwrite existing output, hashes the entire canonical
inventory **including both operator-declared spec digests**, rejects duplicate
JSON keys/frame IDs, noncanonical group identifiers and missing-value
sentinels, contradictory target states, incomplete bin counts,
unsupported fields and test-split access.
It reports, **separately for train/validation**, declared groups, candidate
negative/positive/unknown frames, provisional GT-bin totals, paired-bin
groups, per-group counts (minimum/median/maximum), computational
`>=2` bin support, candidate negative-only groups, missing
viewpoint/contrast metadata and **candidate paired-bin overlap within the
same known viewpoint-and-contrast category in each declared group**.
Groups whose two bins appear only under different or unknown conditions
do not count as joint-condition support. The categories remain
operator-declared proxies, not validated measurement comparability.
A declared group appearing in both splits
produces `BLOCKED_SPLIT_GROUP_OVERLAP`; otherwise the result is
`PROVISIONAL_METADATA_ONLY`, never empirical PASS. The output contains
aggregates, not frame/group identifiers or physical data.

**Not provided by this tool:** genuinely independent acquisition proof,
near-duplicate checks, verification of native-pixel transforms, class/
viewpoint/contrast *comparability* between bins, annotation completeness,
source-informed type-I/power/CI calibration or author approval.
These remain the independent #46-#51 and G01 gates. Keep source inventories
and output reports outside Git; include only admissible checksums and a
reviewed summary in the research issue.

## Blind annotation-QA sampling from local metadata (metadata-only)

`select_blinded_qa.py` creates a **deterministic, group-capped sampling
manifest** for source-image/label inspection. It reads JSON *metadata only*,
never imagery or model outcomes, and will not overwrite an existing output.
The tool is a convenience for #47/#48, **not** dataset admission or proof
of independent acquisitions. An operator must prepare a local inventory
from the lawful exact source release; no source is downloaded automatically.

The input JSON object has `schema_version: 1`, a
`source_release` string, `group_basis` equal to `video_id_proxy`
or `declared_acquisition`, and nonempty `frames`. Each frame has
`frame_id`, `group_id`, `qa_state` (`approved`, `missing`, `flagged`)
and **boolean** `class_conflict`, `geometry_conflict`,
`clipped_box`, `rider_only`, `candidate_negative` and
`target_positive`. This is an explicit **operator-generated inventory
contract**; the JSON does not establish source/label rights or QA truth.
A candidate negative means a frame potentially contains no instances
of the source-specific target class, **not** a verified complete negative.

Example (synthetic metadata only):

```json
{
  "schema_version": 1,
  "source_release": "synthetic-example",
  "group_basis": "video_id_proxy",
  "frames": [{
    "frame_id": "example-1", "group_id": "video-proxy-1",
    "qa_state": "missing", "class_conflict": false,
    "geometry_conflict": false, "clipped_box": false,
    "rider_only": false, "candidate_negative": true,
    "target_positive": false
  }]
}
```

Run after reviewing and explicitly choosing the sample seed, **four
stratum quotas**, and a per-group cap:

```bash
python publications/P01/analyses/select_blinded_qa.py \
  --input LOCAL_METADATA.json --output LOCAL_QA_PLAN.json \
  --seed 20261106 --max-per-group 1 --quotas A=5,B=5,C=5,D=5
```

These values illustrate CLI syntax, **not approved sample sizes**.
The mutually exclusive priority is A (QA missing/flagged), B (class or
geometry conflict, clipped or rider-only), C (candidate negative), D
(ordinary positive). Overlap is retained in risk flags; quotas that
cannot be filled under the group cap produce `SAMPLE_PLAN_INCOMPLETE`.
A group labelled `video_id_proxy` is **never** promoted to an independent
physical acquisition. Sample enrichment cannot estimate source-wide
annotation error prevalence without a separate sampling/weighting design.

Selection uses a deterministic, **group-first order** for each stratum:
one eligible frame from each group is drawn per pass before another frame
from that group is considered, subject to the cap shared across strata.
This avoids selection probability being mechanically proportional to
the number of frames in a long video during the first pass; it does
**not** prove the declared groups are physically independent or create
a frame-representative probability sample. Higher-priority strata can
exhaust the per-group cap and cause lower-priority quota shortfalls.

The manifest records both `frame_inventory_sha256` (canonical sorted
frame records only) and `inventory_sha256` (all inventory fields,
including source release and grouping basis). It separately reports
selected candidate-negative and target-positive counts and whether
both target states are represented; **this is diagnostic, not a QA
acceptance criterion**. All hashes are of operator-supplied declarations,
not owner-verified archive bytes. Keep seed, source identity, grouping
definition, quotas and code revision with the external audit record.

The output lists selected frame/group keys, review/adjudication placeholders,
population counts, quotas and explicit shortfalls. Two truly independent
blinded reviewers must examine lawful original images/annotations, adjudicate
disagreements and apply an author-approved **numeric acceptance criterion**
before any annotation-completeness claim. Keep the full input and review
manifest outside Git and link only rights-permitted checksums/evidence to #47.
