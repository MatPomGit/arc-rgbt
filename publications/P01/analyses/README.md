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
small-minus-reference differences. A candidate 2000-replicate group
bootstrap interval is produced only for >=10 *declared* groups containing
both bins. `choose_validation_threshold` chooses a validation-only
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

The script compares the **candidate whole-acquisition percentile bootstrap**
against a **whole-acquisition Student t interval**. These are methodological
stress tests, not a preregistration decision or a data-derived sample-size
justification. Under some simulated ten-group settings, nominal 95% percentile
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
