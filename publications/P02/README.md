# P02: Quality-Aware RGB-Thermal Fusion Under Measured Temporal and Geometric Misalignment

**Editorial status:** CORE PLANNED; prospective manuscript content, version 0.1.0 (2026-10-31). **No accepted empirical results, submitted manuscript or journal acceptance.** Scientific hypotheses and results remain unverified; the protocol has not been frozen.

**Related task:** [issue #25](https://github.com/MatPomGit/arc-rgbt/issues/25). **Canonical research controls:** [hypotheses](hypotheses/README.md), [protocol](protocol/README.md), [portfolio](../../RESEARCH.md), [state](../../PROJECT_STATE.yaml), [measurement rules](../../docs/guides/evaluation-requirements.md). Additional context: [E01 fusion reference](../../docs/experiments/e01.md) and [E02 timing reference](../../docs/experiments/e02.md); [pairing method](../../research/protocols/P02-pairing-registration.md).

## Proposed manuscript abstract (prospective, not a results abstract)

RGB and long-wave infrared (LWIR) sensors offer complementary observations but are affected by unequal signal quality, spatial registration errors and capture-time offsets. This proposed study asks whether independently estimated modality reliability can improve object-detection recall compared with fixed late fusion when false alarms are controlled. We plan to characterize real exposure timestamps, sensor clock relationships, geometric alignment and invalid image regions before comparing unimodal, equal-weight and non-oracle adaptive fusion pipelines on held-out acquisition groups. Reliability estimators and operating thresholds will be fitted on training or validation data only. The primary contrast will be paired recall at a predeclared false-positive-per-frame ceiling; average precision, calibration, failure strata and computational cost will be secondary outcomes. Artificially injected skew or degradation will be reported separately from physically measured capture discrepancies. Results will be interpreted with cluster-aware uncertainty and complete negative scenes. If original acquisition metadata cannot substantiate physical synchronization, the study will explicitly restrict its claims to observed pairing quality rather than exposure-level timing. No empirical performance or fusion benefit is claimed at this planning stage.

## Introduction: draft opening argument

Mobile perception stacks can receive RGB and LWIR observations whose quality varies independently across illumination, thermal contrast and viewing geometry. Combining detector scores is attractive, yet fixed weights can propagate erroneous detections from a degraded modality. A separate obstacle is that aligned image files need not correspond to the same exposure instant. This manuscript will distinguish the **quality-estimation problem** from the **physical pairing and registration problem**, then test whether reliability-aware fusion yields an operational improvement under a common false-alarm budget.

The paper's research question and falsifiable null and alternative hypotheses are defined in the [hypothesis register](hypotheses/README.md). A protocol freeze and a literature novelty audit must precede any confirmatory claim. Do not cite references until their bibliographic metadata and relevance have been checked.

## Related work and testable contribution

Hwang et al., *Multispectral Pedestrian Detection: Benchmark Dataset and Baseline* ([CVPR 2015](https://openaccess.thecvf.com/content_cvpr_2015/html/Hwang_Multispectral_Pedestrian_Detection_2015_CVPR_paper.html)), demonstrated the importance of paired visible and thermal pedestrian imagery and multispectral detection baselines. Their benchmark does not, by itself, establish that arbitrary subsequently used paired files have physically verified common exposure times. The distinctive question here is whether a **non-oracle**, development-trained reliability estimate produces a held-out gain over fixed fusion at a common false-alarm budget, while measured timing/registration residuals are treated as separate explanatory variables.

The review must distinguish improvements arising from detector tuning, registration, and modality weights. A gain from privileged ground-truth-derived weights is not an independent adaptive fusion result. If physical exposure timestamps are absent, restrict the temporal analysis to available pairing quality and identify exposure skew as unmeasured. A prospective novelty claim is not a verified priority claim.

## Methods: planned manuscript content

1. Register the acquisition unit (session/scene/flight), complete positive and negative labels, native spectral band, image geometry, clock domain and availability of capture-exposure timestamps. Treat missing clock provenance explicitly as unknown.
2. Estimate real temporal offset/drift and spatial residuals on calibration sessions, independently of detection test labels. Do not confuse E02 synthetic jitter or image-arrival timestamps with exposure synchronization.
3. Lock shared detector checkpoints, class mapping, proposal rules, image validity masks and inference budgets. Fit quality estimates without privileged information from held-out labels.
4. Compare RGB-only, LWIR-only, equal-weight late fusion and independently estimated reliability-weighted fusion; include preregistered quality/registration/skew sensitivity strata.
5. Select operating thresholds using development sequences only. Analyze paired recall at identical FP/frame ceiling with acquisition-clustered uncertainty; also report AP, calibration, invalid-overlap rates and elapsed end-to-end time when legitimately measured.

Methods and stopping criteria are governed by the [canonical protocol](protocol/README.md), not by this editorial outline. All measurements require provenance, code/data hashes, independent group definitions and explicitly recorded deviations.

## Results: required content, not yet available

**RESULTS PENDING.** Do not insert estimated or example numbers as observations. Once the study's gate passes, report the following, including negative results and uncertainty:

- Table: acquisition/sensor metadata, clock-provenance completeness, label counts and scene-disjoint partition audit.
- Figure: held-out recall against FP/frame for each fusion baseline, with uncertainty estimated by acquisition group.
- Figure: subgroup effect for low LWIR quality, registration residual bins and measurable exposure-skew bins; list bins that are not physically identifiable.
- Table: complete ablation and negative-result registry, computational budget and failure modes.

## Discussion: interpretive boundaries

Interpret any improvement specifically as evidence for **non-oracle quality-aware fusion**, not for generic fusion or validated clock synchronization unless independently measured. Describe robustness to incomplete calibration, distribution shift and uncertainty in reliability scores. Keep P04's fault-selective risk and P08's calibrated predictive uncertainty outside this paper unless their independent novelty gates fail.

The final discussion must state external-validity limits, threats to identification and what the null result would imply. Reconcile the manuscript with sister projects to prevent duplicate claims or artificial splitting of one result across papers.

## Scientific gate and next editorial step

**Current block:** B01 data rights, real paired labels and B02 physical pairing/calibration evidence; #10, #23 and #25. Confirm independence against P04/P08.

**Next step:** complete the protocol preregistration and rights/provenance audit; develop the literature and methods sections while real-data evidence remains blocked. Select a journal and submission deadline only after independent scientific GO and owner authorization.

**Completion criterion for this page:** the manuscript's proposed question, introduction, prospective abstract, methods, reporting plan and boundary conditions are written. This page does **not** satisfy the empirical research gate or authorize submission.
