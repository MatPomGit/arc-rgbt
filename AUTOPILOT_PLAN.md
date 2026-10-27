# arc-rgbt research work plan

**Version 1.1.0 · updated 2026-10-27.** This is the actionable work
plan, not a second implementation manual. Machine-readable truth:
[PROJECT_STATE.yaml](PROJECT_STATE.yaml). Hypotheses:
[RESEARCH.md](RESEARCH.md). Current work: [Issue #10](https://github.com/MatPomGit/arc-rgbt/issues/10).

## Work packages

| ID | Work | Acceptance gate |
| --- | --- | --- |
| RGBT-01 | Freeze P01/P02 primary endpoints and negative controls | Reviewed [P01](publications/P01/protocol/README.md) / [P02](publications/P02/protocol/README.md) protocols and sequence splits |
| RGBT-02 | Screen RGB/LWIR/NIR datasets, licences and annotations | Independent scenes, modality and native-grid provenance recorded |
| RGBT-03 | Calibrate exposure-time alignment and RGB–LWIR geometry | Measured time skew, reprojection residuals and valid masks |
| RGBT-04 | Evaluate P01 resolution and degradation effects | Real, labelled holdout and uncertainty distinct from [E00](docs/experiments/e00.md) |
| RGBT-05 | Compare P02 RGB/thermal/fixed/adaptive fusion | Independent quality estimates, matched operating points; [E01](docs/experiments/e01.md)/[E02](docs/experiments/e02.md) only reference baselines |
| RGBT-06 | Profile P03 constrained target | Named device, measured RAM/flash/latency/energy, [P03 protocol](publications/P03/protocol/README.md) |
| RGBT-07 | Decide publication GO/NO-GO per stream | Frozen evidence, separate independent review, no automatic submission |

Dependencies: RGBT-01 precedes 02; verified acquisition/calibration
(RGBT-02–03) precedes real P01/P02 comparisons (04–05).
Physical-device measurement (06) must precede P03 claims.
Only evidence-complete streams enter 07; **no deadline or manuscript
completion is implied**.

## Evidence and cost policy

The implemented E00–E02 demonstrations are simulated or analytical;
EdgeLab is a host profiler. Do not convert their output into sensor,
human/vehicle detection or MCU claims. Follow the
[evidence rules](docs/concepts/evidence.md) and
[measurement contract](docs/guides/evaluation-requirements.md).
Data licences and ethics are assessed before acquisition. Use no paid
APIs or self-hosted execution of untrusted PR code.

Journal fit, current scores and possible APC support are evaluated only
after a stream meets its gates; no budget or journal is committed.
Research Autopilot indexes this plan, while scientific status and
reproducibility originate in this repository.
