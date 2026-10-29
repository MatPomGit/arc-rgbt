# arc-rgbt research work plan

**Version 1.2.0 · updated 2026-10-28.** Six CORE planned studies P01–P06 and two OPTIONAL HOLD studies P07–P08. This file owns work packages, not a second copy of research methods: use [RESEARCH.md](RESEARCH.md), the individual protocols and machine-readable [PROJECT_STATE.yaml](PROJECT_STATE.yaml).

## Current execution queue and issue milestones

**Execution ownership:** [Issue #21, M0–M6](https://github.com/MatPomGit/arc-rgbt/issues/21) is the current checklist and dependency index; linked issues #10, #17–#19, #22–#29 specify atomic agent runs, acceptance evidence and blocked tasks. Use this tracker before selecting the next run. This Markdown file owns work-package definitions; `PROJECT_STATE.yaml` remains the machine-readable scientific gate authority. An issue marked complete must not automatically promote a dataset or optional publication.

**Unblocked first actions:** source/rights and metadata-only M3OT review [#22](https://github.com/MatPomGit/arc-rgbt/issues/22) and reusable validation contracts [#23](https://github.com/MatPomGit/arc-rgbt/issues/23), subject to the one-active-PR rule. Empirical M2–M4 work still depends on independently admitted actual data/hardware; P07/P08 remain M6 OPTIONAL HOLD.

## Work packages

| ID | Work | Acceptance gate | Stream |
| --- | --- | --- | --- |
| RGBT-01 | Freeze P01/P02 outcomes, negative controls and independent splits | Versioned, reviewable P01/P02 protocols | P01/P02 |
| RGBT-02 | Audit RGB/LWIR/NIR candidate datasets, licences, labels and provenance | Accepted lawful release with verified native modality and scene grouping | P01/P02/P04/P05/P06 |
| RGBT-03 | Measure exposure-clock alignment and RGB/LWIR registration | Independent time skew, residuals and valid overlap | P02; prerequisite P08 |
| RGBT-04 | Evaluate native resolution/degradation against real data | Independent low-resolution labelled scenes; uncertainty separate from synthetic E00 | P01 |
| RGBT-05 | Compare RGB, thermal, fixed and adaptive fusion | Held-out measured calibration, fair operating points and independent reliability weights | P02 |
| RGBT-06 | Instrument a named constrained target | Physical device RAM/flash/latency/energy logs and perception metrics | P03; prerequisite P07 |
| RGBT-07 | Independent evidence and non-overlap publication GO/NO-GO | Paper-specific auditable evidence and scientific novelty review, no automatic submission | P01–P08 |
| RGBT-08 | Predeclare modality failures and selective risk policy | [G04](publications/P04/protocol/README.md): held-out fault-stratified labels and risk/coverage baselines | P04 |
| RGBT-09 | Verify and test genuine cross-sensor transfer | [G05](publications/P05/protocol/README.md): two independent labelled sensor domains and leakage-free holdout | P05 |
| RGBT-10 | Test multi-object temporal identity consistency | [G06](publications/P06/protocol/README.md): real paired sequences, ground-truth track IDs and HOTA audit | P06 |
| RGBT-11 | **OPTIONAL HOLD:** adaptive sensing/compute and measured policy energy | [G07](publications/P07/protocol/README.md): P03 physical benchmark + adaptive hardware measurements + non-overlap PASS | P07 |
| RGBT-12 | **OPTIONAL HOLD:** propagated calibration uncertainty risk bounds | [G08](publications/P08/protocol/README.md): real geometric/clock uncertainty + coverage + non-overlap PASS | P08 |

## Priorities and dependencies

1. RGBT-01/02 data rights, versioned protocol and labels precede external-dataset performance claims. Documentation-only planning P04–P06 can proceed without empirical claims.
2. RGBT-03 underpins P02 and any later P08. RGBT-04/05/08/09 require genuinely labelled, independent scenes. RGBT-10 requires real identity-labelled, correctly paired sequences; still imagery is inadequate.
3. RGBT-06 must precede P03 physical efficiency claims. **RGBT-11/P07 is blocked** until all G07 conditions pass and are reviewed.
4. **RGBT-12/P08 is blocked** until all G08 conditions pass and are reviewed. Synthetic E02 skew/overlap does not satisfy measured uncertainty or risk-bound coverage.
5. RGBT-07 enforces independent manuscript-level claims; integrate any overlapping or unsupported findings into parent articles instead of salami slicing.

## Evidence, costs and autonomy

Use no paid APIs. Do not auto-download datasets/weights, run untrusted PR code on persistent self-hosted runners, or infer physical effects from synthetic E00–E02 or host EdgeLab. Check dataset rights/privacy, annotate negative-frame completeness, isolate scenes/devices, record acquisition/calibration evidence, code SHA and measurement uncertainty. Human/physical studies or manuscript submission require their own authorization and scientific GO.

An OPTIONAL HOLD entry is a **blocked candidate**, not queued execution, and must not be automatically promoted based on a documentation change. Scope is [RESEARCH.md](RESEARCH.md); methods are in [publication protocols](publications/P07/protocol/README.md), [measurement rules](docs/guides/evaluation-requirements.md) and [evidence policy](docs/concepts/evidence.md).
