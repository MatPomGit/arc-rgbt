# P05: Cross-Sensor Generalization of RGB-Thermal Detection with Strict Device and Domain Holdouts

**Editorial status:** CORE PLANNED; prospective manuscript content, version 0.1.0 (2026-10-31). **No accepted empirical results, submitted manuscript or journal acceptance.** Scientific hypotheses and results remain unverified; the protocol has not been frozen.

**Related task:** [issue #18](https://github.com/MatPomGit/arc-rgbt/issues/18). **Canonical research controls:** [hypotheses](hypotheses/README.md), [protocol](protocol/README.md), [portfolio](../../RESEARCH.md), [state](../../PROJECT_STATE.yaml), [measurement rules](../../docs/guides/evaluation-requirements.md). Additional context: [cross-domain protocol](protocol/README.md).

## Proposed manuscript abstract (prospective, not a results abstract)

RGB and thermal detectors are frequently evaluated on images originating from a limited set of sensor devices and acquisition environments. It remains difficult to attribute performance changes to the sensing system when viewpoint, object classes, annotation practice and lighting vary simultaneously. This proposed study will quantify how detection performance transfers to previously unseen physical RGB-LWIR sources and whether a prespecified, training-only normalization or adaptation rule reduces that deterioration relative to source-only training. Admission will require at least two independently documented and legally usable sensor-domain cohorts with compatible annotations. All train, validation and test partitions will be split by source/device or acquisition session, with overlap and near-duplicate checks. The primary outcome will be out-of-domain average-precision degradation relative to the corresponding in-domain benchmark; recall under a fixed false-alarm budget and calibration will be secondary. Adaptation will not use target-test labels, and model/tuning budgets will be balanced. When class or viewpoint confounders prevent a sensor-specific conclusion, we will report only broader cross-domain generalization or a no-go decision. This document proposes the analysis; it does not establish measured transfer robustness.

## Introduction: draft opening argument

Strong in-domain performance does not establish external validity across thermal cameras, optical assemblies and annotation pipelines. A shift in device can coincide with a shift in scene type, object taxonomy or mounting viewpoint, making unqualified 'sensor generalization' claims misleading. The study will separate the **transfer estimate** from the stronger causal interpretation that sensor identity alone caused the observed shift.

The paper's research question and falsifiable null and alternative hypotheses are defined in the [hypothesis register](hypotheses/README.md). A protocol freeze and a literature novelty audit must precede any confirmatory claim. Do not cite references until their bibliographic metadata and relevance have been checked.

## Related work and testable contribution

Seemakurthy et al., *Domain Generalised Faster R-CNN* ([AAAI 2023](https://doi.org/10.1609/aaai.v37i2.25312)), evaluated object detection under domain shift, providing an appropriate conceptual point of comparison rather than direct proof of RGB/LWIR sensor transfer. A physically new camera need not create an identifiable **sensor-only** contrast: a change in object classes, image scale, environment or labels can yield the same apparent AP deterioration.

Define an estimand for each allowed source-to-target transfer and preserve a table of class, viewpoint, optical and annotation comparability. Compare adaptation gain against the source-only model **on the same held-out target cohort**, in addition to reporting the preregistered out-of-domain AP drop. Distinguish source/domain transfer from causal attribution to sensor hardware; if source confounding is uncontrolled, the latter claim is disallowed. Never tune adaptation using target-test ground truth.

## Methods: planned manuscript content

1. Independently verify source identities, native RGB/LWIR band and optics, exact archive rights, annotations, source versions and class harmonization. NIR is not an LWIR replacement.
2. Predeclare which comparisons identify sensor shift and which only identify joint sensor/domain shift. Reject an experiment if class/viewpoint confounding makes its declared estimand uninterpretable.
3. Freeze leave-one-source/device-out and scene-group splits, cross-source duplicates, near-duplicate and adjacent-frame leakage checks; never tune on target-test labels.
4. Compare source-only RGB, LWIR and fixed-fusion baselines with a bounded training-only normalization or unsupervised adaptation method at matched training and inference budgets.
5. Estimate out-of-domain minus in-domain AP loss for every permissible held-out source, with source/session-aware uncertainty; report recall at matched FP/frame, ECE and heterogeneous failure cases.

Methods and stopping criteria are governed by the [canonical protocol](protocol/README.md), not by this editorial outline. All measurements require provenance, code/data hashes, independent group definitions and explicitly recorded deviations.

## Results: required content, not yet available

**RESULTS PENDING.** Do not insert estimated or example numbers as observations. Once the study's gate passes, report the following, including negative results and uncertainty:

- Table: independent device/source provenance, spectral band, native grids, classes, viewpoint and licensing decisions.
- Matrix plot: each train-source to test-source AP transfer, including all tested directions.
- Figure: AP degradation and confidence intervals, separated by source, class and acquisition covariates.
- Table: adaptation cost, test-label non-use audit, and confounding limitations for every experiment.

## Discussion: interpretive boundaries

An apparent improvement may reflect source composition rather than robust modality adaptation. Discuss the limited number of devices, source class imbalance and covariate support. Resized copies of one sensor are not independent domains. If two class-compatible independent cohorts cannot be validated, retain P05 as blocked rather than manufacturing a cross-sensor claim.

The final discussion must state external-validity limits, threats to identification and what the null result would imply. Reconcile the manuscript with sister projects to prevent duplicate claims or artificial splitting of one result across papers.

## Scientific gate and next editorial step

**Current block:** G05 >=2 rights-cleared, physically independent and class-compatible sensor/domain cohorts, with source-disjoint evaluation, #18 and #10.

**Next step:** complete the protocol preregistration and rights/provenance audit; develop the literature and methods sections while real-data evidence remains blocked. Select a journal and submission deadline only after independent scientific GO and owner authorization.

**Completion criterion for this page:** the manuscript's proposed question, introduction, prospective abstract, methods, reporting plan and boundary conditions are written. This page does **not** satisfy the empirical research gate or authorize submission.
