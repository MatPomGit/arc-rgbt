# P04: Selective RGB-Thermal Detection Under Missing and Degraded Modalities: A Risk-Coverage Study

**Editorial status:** CORE PLANNED; prospective manuscript content, version 0.1.0 (2026-10-31). **No accepted empirical results, submitted manuscript or journal acceptance.** Scientific hypotheses and results remain unverified; the protocol has not been frozen.

**Related task:** [issue #17](https://github.com/MatPomGit/arc-rgbt/issues/17). **Canonical research controls:** [hypotheses](hypotheses/README.md), [protocol](protocol/README.md), [portfolio](../../RESEARCH.md), [state](../../PROJECT_STATE.yaml), [measurement rules](../../docs/guides/evaluation-requirements.md). Additional context: [failure-aware protocol](protocol/README.md).

## Proposed manuscript abstract (prospective, not a results abstract)

Object detectors that combine visible and thermal imagery may fail when one stream becomes unavailable, stale or severely degraded. This proposed investigation will assess whether explicit failure monitoring and selective prediction can reduce missed detections under such conditions without hiding errors behind abstention. A predeclared fault catalogue will include RGB and LWIR loss, delayed observations, blur and diminished modality contrast, together with unaffected controls. A reliability monitor will be trained on development data only and compared on independent scenes against unimodal detection, fixed late fusion and an appropriate quality-aware fusion baseline. The primary endpoint will be the highest missed-detection rate across predefined fault strata at a common false-positive-per-frame ceiling and a minimum prediction-coverage requirement. Secondary analyses will describe risk-coverage behavior, abstentions, calibration, monitor discrimination and overhead. Physical sensor failures will be distinguished from injected software perturbations. Grouped uncertainty and complete negative-scene annotation will prevent artificial gains from selective omission of difficult examples. The study's safety or operational reliability interpretation will remain conditional on real independently labelled degradations and separate scientific review; no improvement has yet been demonstrated.

## Introduction: draft opening argument

Modality redundancy does not automatically produce graceful degradation. A detector may issue confident false alarms or silently miss objects when one sensor freezes, disappears or delivers uninformative data. An abstaining policy can appear accurate merely by refusing hard cases, so the operational constraint must include **minimum prediction coverage**. This manuscript will address failure-conditioned miss risk rather than average fusion accuracy.

The paper's research question and falsifiable null and alternative hypotheses are defined in the [hypothesis register](hypotheses/README.md). A protocol freeze and a literature novelty audit must precede any confirmatory claim. Do not cite references until their bibliographic metadata and relevance have been checked.

## Methods: planned manuscript content

1. Predeclare physically observed versus synthetically injected failure categories, severity thresholds, minimum coverage and FP/frame ceiling. Define treatment of missing frames and unscored predictions.
2. Require complete positive and negative labels at the scene/session level and source-disjoint partitions. Freeze fault strata and severity definitions before the final test.
3. Use the same base detectors and matched inference budgets for RGB-only, LWIR-only, fixed fusion, P02 non-oracle fusion and selective failure-aware decision policy.
4. Train the reliability monitor and choose abstention/score thresholds on development data only. Do not condition operating points on held-out failure labels.
5. Compute worst-stratum miss rate subject to coverage and FP/frame constraints; report infeasible thresholds, AURC, abstention rate and paired cluster intervals, including negative outcomes.

Methods and stopping criteria are governed by the [canonical protocol](protocol/README.md), not by this editorial outline. All measurements require provenance, code/data hashes, independent group definitions and explicitly recorded deviations.

## Results: required content, not yet available

**RESULTS PENDING.** Do not insert estimated or example numbers as observations. Once the study's gate passes, report the following, including negative results and uncertainty:

- Table: fault taxonomy, real-versus-injected origin, severity, class balance and split completeness.
- Figure: worst-condition miss rate against minimum achieved coverage, with the matched FP/frame ceiling displayed.
- Figure: risk-coverage curves and subgroup intervals; explicitly show abstained cases and false alarms.
- Table: monitoring overhead, failure AUROC/calibration, and all infeasible or failed operating points.

## Discussion: interpretive boundaries

Emphasize that a failure monitor does not guarantee safety. Discuss open-set sensor failures, coverage constraints and deployment conditions not represented in the evaluation. If the primary worst-stratum claim cannot be distinguished from P02's fusion benefit, integrate the findings into P02 instead of treating P04 as an independent publication.

The final discussion must state external-validity limits, threats to identification and what the null result would imply. Reconcile the manuscript with sister projects to prevent duplicate claims or artificial splitting of one result across papers.

## Scientific gate and next editorial step

**Current block:** G04 lawful real labelled fault strata, no-fault controls, independent scenes and an honest coverage denominator, #17, #10, #23.

**Next step:** complete the protocol preregistration and rights/provenance audit; develop the literature and methods sections while real-data evidence remains blocked. Select a journal and submission deadline only after independent scientific GO and owner authorization.

**Completion criterion for this page:** the manuscript's proposed question, introduction, prospective abstract, methods, reporting plan and boundary conditions are written. This page does **not** satisfy the empirical research gate or authorize submission.
