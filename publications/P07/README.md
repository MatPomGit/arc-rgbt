# P07: Dynamic Energy-Aware RGB-Thermal Sensing and Inference under Perception Constraints

**Editorial status:** OPTIONAL HOLD - CONCEPT ONLY; prospective manuscript content, version 0.1.0 (2026-10-31). **No accepted empirical results, submitted manuscript or journal acceptance.** No empirical work or paper activation is authorized while G07/G08 remain HOLD.

**Related task:** [issue #27](https://github.com/MatPomGit/arc-rgbt/issues/27). **Canonical research controls:** [hypotheses](hypotheses/README.md), [protocol](protocol/README.md), [portfolio](../../RESEARCH.md), [state](../../PROJECT_STATE.yaml), [measurement rules](../../docs/guides/evaluation-requirements.md). Additional context: [P03 measured fixed baseline](../P03/protocol/README.md) and [G07 gate](protocol/README.md).

## Proposed manuscript abstract (prospective, not a results abstract)

Dynamic switching between sensing and inference configurations could reduce the energy required by multimodal perception, but such a claim is distinct from comparing fixed embedded models. This optional study would investigate a causal, implementable policy that selects RGB, LWIR or combined processing modes based solely on information available at decision time. The primary estimand would be measured joules per independently evaluated scene or sequence relative to the best feasible fixed P03 pipeline, subject to prespecified detection recall, false-alarm and latency constraints. A credible experiment would require a physically metered target with genuinely switchable camera and computation states, measured transition costs, idle power and reproducible scene workloads. Candidate policies, baselines and prediction thresholds would be frozen before final testing, and energy benefits would be interpreted jointly with any failure to satisfy perception service levels. The project has no admitted device power baseline or switching measurements. It remains OPTIONAL HOLD: this conceptual outline neither authorizes acquisition or implementation nor guarantees a separate paper. If a distinct dynamic-control benefit is absent, the findings belong with P03.

## Introduction: draft opening argument

A static comparison of quantization levels and fixed modality choices can define a resource frontier without requiring a new control algorithm. A separate adaptive-sensing contribution is justified only when the system **actively changes** capture or compute modes on the device and when complete physical energy accounting demonstrates a gain at matched detection quality.

The paper's research question and falsifiable null and alternative hypotheses are defined in the [hypothesis register](hypotheses/README.md). A protocol freeze and a literature novelty audit must precede any confirmatory claim. Do not cite references until their bibliographic metadata and relevance have been checked.

## Methods: planned manuscript content

1. Do not start empirical work while G07 is HOLD. Review physical P03 measurement logs, target-state controllability, switch/boot latency and scientific distinctness before any activation proposal.
2. If independently promoted, define the policy action space and inputs observable at run time; avoid oracle quality labels, future frames and target-test tuning.
3. Compare best feasible fixed P03 baseline with dynamic policies over repeatable independent scenes, including all sensor, control, compute and transition energy.
4. Freeze recall, FP/frame, latency and coverage constraints; report the proportion of workloads that violate any constraint rather than averaging away failures.
5. Estimate joules per scene, switch frequency, thermal state, tail latency, confidence intervals and generalization by scene type.

Methods and stopping criteria are governed by the [canonical protocol](protocol/README.md), not by this editorial outline. All measurements require provenance, code/data hashes, independent group definitions and explicitly recorded deviations.

## Results: required content, not yet available

**RESULTS PENDING.** Do not insert estimated or example numbers as observations. Once the study's gate passes, report the following, including negative results and uncertainty:

- Conditional figure: energy versus matched perception constraint and uncertainty over repeated scenes.
- Conditional table: actual switching actions, physical transition costs, latency and infeasible states.
- Conditional negative-result table: policy violations, no-saving cases and off-policy limitations.

## Discussion: interpretive boundaries

Do not relabel P03 static pipeline data as dynamic savings. A policy that uses test-time ground truth or fails service constraints does not establish a usable control benefit. Publication remains conditional on G07 PASS and an explicit change of status in PROJECT_STATE.yaml.

The final discussion must state external-validity limits, threats to identification and what the null result would imply. Reconcile the manuscript with sister projects to prevent duplicate claims or artificial splitting of one result across papers.

## Scientific gate and next editorial step

**Current block:** G07 is currently HOLD. Requires physically verified P03 baseline, controllable adaptive hardware, independently metered savings and distinct novelty (#27, #26).

**HOLD rule:** This section is a *contingent concept only*. Do not schedule experiments, select a submission journal, edit `PROJECT_STATE.yaml` to promote the study or claim a separate article without reviewed gate PASS.

**Completion criterion for this page:** the manuscript's proposed question, introduction, prospective abstract, methods, reporting plan and boundary conditions are written. This page does **not** satisfy the empirical research gate or authorize submission.
