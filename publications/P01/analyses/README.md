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
exploratory **paired-only target-pooled contrast** to diagnose group
weighting. With fewer than the provisional 10 paired groups, the
difference is retained descriptively but its candidate 2000-replicate
bootstrap interval is suppressed. A computed interval is descriptive,
not a calibrated directional test. `choose_validation_threshold` chooses a validation-only
candidate cutoff with a 0.10 FP/frame point ceiling, provisional >=10
groups and >=200 fully labelled frames, **including >=20 fully negative
frames in >=2 groups**, and no trivial zero-TP solution. It also reports
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
a per-acquisition difference; this is a **computational definition**, not a
scientific sample-size minimum. The report exposes
`paired_group_target_counts`, `paired_groups_with_singleton_bin`,
`acquisitions_excluded_from_paired_contrast` and the exploratory
`paired_object_pooled_delta_sensitivity`. The pooled sensitivity is
restricted to the **same paired acquisitions**, preserving the cohort
when comparing weighting conventions.

Before any confirmatory analysis, #48/#49/#50 must document an authentic,
**non-test** acquisition inventory, per-bin count distributions, class and
viewpoint common support, group-level variance/effect assumptions, and a
source-informed minimum count and group-size decision with evaluated type-I
error, power and interval coverage. A small software-sufficient group count
cannot authorize empirical inference; if feasibility or overlap is inadequate,
report `DESCRIPTIVE_ONLY`. No frozen sample-size or alpha approval is
implied by the synthetic pilot.
