# P01 manuscript working draft: introduction, methods and limitations

**Version:** 0.1.3, 2026-11-12. **Status:** UNSENT, UNFROZEN, no empirical results.
This is manuscript prose for [#38](https://github.com/MatPomGit/arc-rgbt/issues/38), not a replacement for the [author decision packet](protocol/README.md). Numerical choices below are **candidates**, not an approved preregistration. Do not fill Results from simulations or software CI.

## Working title

Source-Annotated LWIR Target Footprint and Localization-Qualified Detection Reliability for Mobile Robotic Perception

## Introduction

Reliable object detection under limited thermal image detail is relevant to perception systems that must detect objects of different apparent sizes. The number of image pixels covered by a source-annotated bounding box, however, is not equivalent to the physical angular extent of a target at the sensor. Image export, cropping, resizing, optical blur, annotation conventions and detector preprocessing can all change the relationship between source coordinates and physical sampling. Consequently, a benchmark of detector performance against provided bounding boxes must be distinguished from a claim about the intrinsic resolution limit of a thermal camera.

This study proposes a reproducible observational evaluation of a fixed long-wave infrared (LWIR) detector on a lawfully available, versioned dataset with existing source annotations. Its principal contribution is intended to be an operating-point-controlled comparison of localization-qualified detection recall across source-annotated target-footprint strata. The analysis explicitly reports apparent false detections relative to supplied labels, rather than assuming those labels exhaustively describe every object in each image. The proposed experiment is motivated by mobile robotic perception; it does not claim to measure autonomous navigation or robot deployment outcomes.

Small-object detection has previously been investigated with restricted receptive fields by Poster, Hu and Nasrabadi (2023, https://doi.org/10.3390/s23187806), including MWIR material that must not be treated as LWIR evidence. Visible-thermal tiny-object benchmarks such as RGBT-Tiny (https://arxiv.org/abs/2406.14482) provide further context, but their existence alone does not validate the acquisition provenance or native sensor geometry of the dataset selected here. The intended distinction of the present work is the predeclared false-alert operating point and explicit evidence boundary between dataset-relative and physical sensor claims. This novelty proposition requires independent review.

## Materials and methods (prospective)

### Data provenance and eligibility

The primary input will be a permitted original release of FLIR ADAS v2 or a separately approved lawful alternative, with original source annotations converted by the existing repository parser into a documented COCO-compatible representation. Prior to analysis, record the exact release identity, terms of use, annotation version, source hashes, coordinate transforms, and any available original LWIR grid and optics metadata. Do not equate a third-party export with an authenticated original sensor grid. Missing provenance must be marked UNKNOWN, not reconstructed from detector output.

The candidate primary target category is `car`. Source `rider` must not be silently merged with `person`. Any ignored or crowd annotations require a prospective rule compatible with the source convention; the current reference evaluator rejects unsupported conventions. Images without an annotated eligible target remain in the denominator for apparent false positives per frame. They are **reference-negative** and are not independently established to be object-free.

### Partitions and detector provenance

Separate training, validation and untouched holdout by genuine source acquisition/session identifiers whenever these can be verified. Source `video_id` alone is a proxy, not evidence of independent acquisitions. The training lineage of the fixed checkpoint must be checked for source and group overlap before using validation or test data. Deterministic group split manifests, input hashes and any exact or near-duplicate exclusions must be recorded without inspecting held-out detector outcomes.

The detector checkpoint, preprocessing, input grid, class mapping and inference configuration must be fixed before the held-out run. A compatible existing TorchScript checkpoint may be used with the repository's current validation inference adapter; no model download, training on holdout or manual reannotation is part of this design.

### Outcomes and operating point

For each eligible supplied bounding box in COCO export coordinates, define the footprint proxy `s = sqrt(w * h)` pixels. Candidate strata are small (`s < 8`), intermediate (`8 <= s < 16`) and reference (`s >= 16`). These are export-grid measurements, **not verified native sensor pixels**. Use same-class, one-to-one score-ordered matching at IoU >= 0.50. Report true positives, false negatives and recall relative to supplied annotations for each stratum, with denominators. IoU 0.25 may be examined as a declared sensitivity analysis.

The candidate false-alert budget is 0.10 unmatched eligible detections per **all** selected source-labelled frames. Select the confidence threshold exclusively from validation predictions, retaining score ties and requiring at least one validation true positive. If the budget is infeasible, record `BLOCKED_VALIDATION`. A locked threshold must not be changed in response to held-out FP/frame, even if the holdout exceeds the validation budget. Report any such violation as `OPERATING_CONDITION_NOT_MET`, not as a reason to tune the test.

The implemented runner reports all-points interpolated AP at IoU 0.50, **not** COCO mAP averaged over IoU 0.50:0.95. This AP uses the full score ranking rather than the locked FP/frame operating threshold and is secondary to the fixed-operating-point analysis. Apparent false positives can include objects omitted from source annotations; neither FP/frame nor recall is a physical sensor detection bound.

### Estimand and uncertainty

If verified independent acquisitions contain both the small and reference bins, define for each eligible acquisition `g`: `d_g = TP_small,g / N_small,g - TP_reference,g / N_reference,g`. The candidate primary contrast is `Delta = mean_g(d_g)`, weighting acquisitions equally. Report the number of eligible acquisitions and within-group target counts. A one-sided acquisition-level t procedure for `H1: Delta < 0` is **not authorized** without source-informed assumption checks, sufficient independent groups, methodological review and the author's prospective freeze. In particular, a two-sided 95% interval cannot silently substitute for a one-sided alpha 0.05 decision.

If authentic acquisition IDs or inferential support are unavailable, report `DESCRIPTIVE_ONLY` counts, per-bin recall, reference-relative FP/frame and transparent descriptive variability without confirmatory p-values. No frame-wise IID uncertainty estimate is a substitute for independent acquisition-level inference.

### Reproducible execution boundary

The existing [P01 analysis interface](analyses/README.md) provides three separate stages: (1) train/validation-only COCO group and denominator manifest generation; (2) guarded validation-only TorchScript inference with a pre-existing trusted, SHA-pinned checkpoint; and (3) validation-only source-reference threshold selection. These stages must not be conflated with an executed experiment. The manifest can propose new partitions, but applying a proposal to a checkpoint already trained on those validation frames would invalidate the split. The current inference adapter accepts 8-bit grayscale thermal JPEG/PNG and a declared post-NMS tensor layout; it does not support arbitrary original 14/16-bit TIFF or unverified preprocessing. These are substantive eligibility constraints, not implementation details to silently bypass.

The evaluator's held-out mode requires a prospective author-declared freeze record with actual artifact digests and paths; the record is not independent proof of author identity, source rights, checkpoint training isolation or true acquisition independence. Any future manuscript result must link to the exact input/model/config/split/code hashes, validation decision and held-out output. Until then, the outcome remains NOT_RUN.

## Results

**Not available.** No original source release, lawful data admission, compatible checkpoint, validation cutoff or real held-out outcome has been verified in this manuscript revision. Insert only hash-backed, reproducible empirical tables and plots after the applicable author decision and execution gates. Never substitute E00 simulated findings for real LWIR measurements.

## Discussion: prespecified interpretation limits

The principal threat to interpretation is that source labels may be incomplete, so unmatched detections are not necessarily physical false alarms. The exported annotation footprint may differ from original sensor sampling because of cropping, scaling, interpolation and annotation geometry. Apparent target size can covary with class, contrast, occlusion, orientation, range and acquisition environment. Thus an observed association between footprint and recall would not isolate a causal optical mechanism.

A dataset-relative Tier A analysis may be scientifically reportable with a clearly delimited population and transparent descriptive interpretation. A Tier B assertion about native LWIR optics, detection range, causal resolution effects or real robot deployment requires separately verified sensor and acquisition evidence. Tier B remains **BLOCKED**. The study does not make claims about RGB/LWIR fusion, which belongs primarily to P02, or embedded power and latency, which belong to P03.

## Reproducibility and ethics statements (pending verification)

The final paper must name the lawful dataset release, original owner and terms, model checkpoint provenance, code revision, configuration, split manifest, validation threshold and result hashes. Public availability of images or weights must not be asserted before licence review. No new human participants or original acquisitions are claimed by this draft. Ethics applicability, author contributions, conflicts of interest, funding and data/code availability must be verified for the actual study before submission.

## Evidence and decision ledger

| Manuscript element | Current evidence | State |
| --- | --- | --- |
| Candidate estimand, footprint bins, FP/frame conventions | [Hypothesis sheet](hypotheses/README.md), [protocol](protocol/README.md) | UNFROZEN |
| Journal scope and related-work starting points | [P01 overview](README.md), [#52](https://github.com/MatPomGit/arc-rgbt/issues/52) | PROVISIONAL |
| Lawful source identity, rights, original grid and optics | [#45](https://github.com/MatPomGit/arc-rgbt/issues/45), [#46](https://github.com/MatPomGit/arc-rgbt/issues/46), [#54](https://github.com/MatPomGit/arc-rgbt/issues/54) | BLOCKED |
| Authentic group counts, split and checkpoint provenance | [#48](https://github.com/MatPomGit/arc-rgbt/issues/48), [#55](https://github.com/MatPomGit/arc-rgbt/issues/55), [#58](https://github.com/MatPomGit/arc-rgbt/issues/58) | BLOCKED |
| Real validation cutoff and held-out performance | [#58](https://github.com/MatPomGit/arc-rgbt/issues/58), [#59](https://github.com/MatPomGit/arc-rgbt/issues/59), [#60](https://github.com/MatPomGit/arc-rgbt/issues/60) | NOT_RUN |
| Independent numerical and manuscript review | [#29](https://github.com/MatPomGit/arc-rgbt/issues/29), [#62](https://github.com/MatPomGit/arc-rgbt/issues/62) | PENDING |
| Author protocol/claim approval and submission | [#53](https://github.com/MatPomGit/arc-rgbt/issues/53), [#40](https://github.com/MatPomGit/arc-rgbt/issues/40) | NOT_AUTHORIZED |

This draft is intentionally limited to prospective prose. Its Git commit is **not** scientific approval.
