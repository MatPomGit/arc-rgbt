# P08: Propagation of RGB-Thermal Calibration and Timing Uncertainty into Detection-Risk Bounds

**Editorial status:** OPTIONAL HOLD - CONCEPT ONLY; prospective manuscript content, version 0.1.0 (2026-10-31). **No accepted empirical results, submitted manuscript or journal acceptance.** No empirical work or paper activation is authorized while G07/G08 remain HOLD.

**Related task:** [issue #28](https://github.com/MatPomGit/arc-rgbt/issues/28). **Canonical research controls:** [hypotheses](hypotheses/README.md), [protocol](protocol/README.md), [portfolio](../../RESEARCH.md), [state](../../PROJECT_STATE.yaml), [measurement rules](../../docs/guides/evaluation-requirements.md). Additional context: [P02 physical registration prerequisite](../P02/protocol/README.md) and [G08 gate](protocol/README.md).

## Proposed manuscript abstract (prospective, not a results abstract)

Registration and timing uncertainty can influence the validity of cross-modal detections, yet low mean reprojection error does not establish calibrated predictive reliability. This optional study would evaluate whether uncertainty measured from independent physical calibration and exposure-timing sessions can produce detection-risk or localization-error bounds with valid coverage on untouched acquisitions. Camera coordinate systems, transform uncertainty, clock offset and drift, interpolation support and invalid image overlap would be documented before uncertainty propagation. The primary endpoint would be observed out-of-sample coverage and calibration error relative to a preregistered nominal level, with interval width and perception quality as secondary criteria. Deterministic registration and deliberately misspecified uncertainty would serve as reference baselines. The assessment would include uncertainty versus coverage diagrams, group-wise intervals, shifts in target motion and failure to meet predicted error bounds. The project currently lacks independent physical spatiotemporal uncertainty estimates; E02 simulated skew and geometric rectangle intersection are insufficient. P08 remains OPTIONAL HOLD until G08 physical evidence, risk-bound validity and independent novelty are confirmed. If those prerequisites are not met, uncertainty reporting should remain within P02.

## Introduction: draft opening argument

An estimated RGB-to-LWIR transform can register two images while concealing uncertainty about the camera calibration, target position and time difference. Propagating such uncertainty into a meaningful **predictive risk statement** is harder than reporting mean reprojection residual. This manuscript concept would test calibration of risk bounds out of sample, not merely fit a more complicated registration model.

The paper's research question and falsifiable null and alternative hypotheses are defined in the [hypothesis register](hypotheses/README.md). A protocol freeze and a literature novelty audit must precede any confirmatory claim. Do not cite references until their bibliographic metadata and relevance have been checked.

## Methods: planned manuscript content

1. Do not initiate physical experiments while G08 remains HOLD. Independently review P02 clock and geometric calibration evidence before considering a new study.
2. If promoted, establish genuine capture-exposure clock uncertainty, coordinate conventions, valid masks and calibration target observations from disjoint acquisition sessions.
3. Predeclare a nominal coverage level, bounded error/risk quantity, estimator and validation sessions. Reserve a final untouched dataset for observed coverage checks.
4. Compare deterministic P02 registration with uncertainty propagation and negative controls that deliberately omit or misstate time/geometric uncertainty.
5. Quantify observed interval/risk coverage, calibration gap, width, conditional failures under motion/occlusion and uncertainty by session. Do not treat synthetic E02 as physical calibration.

Methods and stopping criteria are governed by the [canonical protocol](protocol/README.md), not by this editorial outline. All measurements require provenance, code/data hashes, independent group definitions and explicitly recorded deviations.

## Results: required content, not yet available

**RESULTS PENDING.** Do not insert estimated or example numbers as observations. Once the study's gate passes, report the following, including negative results and uncertainty:

- Conditional figure: nominal versus observed held-out bound coverage, with session-group uncertainty.
- Conditional figure: bound width versus error/risk and target-motion strata, including invalid overlap.
- Conditional table: independent calibration sessions, actual clock measurements and reference comparison.

## Discussion: interpretive boundaries

Predictive coverage can appear acceptable on average while failing under motion or a shifted sensor configuration; conditional failures must be reported. If the contribution is only improved mean registration error or synthetic jitter sensitivity, it overlaps with P02 and does not justify a separate article.

The final discussion must state external-validity limits, threats to identification and what the null result would imply. Reconcile the manuscript with sister projects to prevent duplicate claims or artificial splitting of one result across papers.

## Scientific gate and next editorial step

**Current block:** G08 is currently HOLD. Requires independent measured space/time calibration, physical held-out predictive coverage, novelty review and explicit state promotion (#28, #25).

**HOLD rule:** This section is a *contingent concept only*. Do not schedule experiments, select a submission journal, edit `PROJECT_STATE.yaml` to promote the study or claim a separate article without reviewed gate PASS.

**Completion criterion for this page:** the manuscript's proposed question, introduction, prospective abstract, methods, reporting plan and boundary conditions are written. This page does **not** satisfy the empirical research gate or authorize submission.
