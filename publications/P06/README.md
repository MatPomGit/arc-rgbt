# P06: Modality-Aware Temporal Association for Identity-Preserving RGB-Thermal Multi-Object Tracking

**Editorial status:** CORE PLANNED; prospective manuscript content, version 0.1.0 (2026-10-31). **No accepted empirical results, submitted manuscript or journal acceptance.** Scientific hypotheses and results remain unverified; the protocol has not been frozen.

**Related task:** [issue #19](https://github.com/MatPomGit/arc-rgbt/issues/19). **Canonical research controls:** [hypotheses](hypotheses/README.md), [protocol](protocol/README.md), [portfolio](../../RESEARCH.md), [state](../../PROJECT_STATE.yaml), [measurement rules](../../docs/guides/evaluation-requirements.md). Additional context: [tracking protocol](protocol/README.md) and [dataset admission task #22](https://github.com/MatPomGit/arc-rgbt/issues/22).

## Proposed manuscript abstract (prospective, not a results abstract)

Framewise RGB-thermal object detection cannot by itself establish stable target identity over time. This proposed study will test whether modality-aware temporal association preserves multi-object identity during occlusion and intermittent sensor degradation more effectively than unimodal or fixed-fusion association. The experiment requires lawful, paired real video sequences with persistent ground-truth track identifiers and a validated sequence-level evaluation protocol. To isolate association from detection quality, the primary comparison will use identical frozen candidate detections across association methods; complete detection-and-tracking pipelines will be analyzed separately. HOTA on held-out source-independent sequences will be the primary endpoint, with IDF1, identity switches, fragmentation and association accuracy as secondary measures. Occlusion and missing-modality strata will be defined before testing. We will audit dataset frame keys, identity consistency, flight/scene partitions, manual registration limits and annotation rights, and validate the metric implementation against published reference fixtures. Sequence-clustered uncertainty and explicitly documented failed tracks will accompany all comparisons. The intended contribution is temporal identity continuity, not improved per-frame mAP or physical exposure synchronization. No verified tracking dataset or empirical HOTA improvement is claimed.

## Introduction: draft opening argument

A detection pipeline can report high average precision while repeatedly swapping object identities between frames. Maintaining track identity across occlusion, viewpoint changes and intermittent modality loss is a distinct temporal inference task. This manuscript will evaluate whether modality-aware association improves **identity continuity**, rather than conflating tracking quality with more accurate object proposals.

The paper's research question and falsifiable null and alternative hypotheses are defined in the [hypothesis register](hypotheses/README.md). A protocol freeze and a literature novelty audit must precede any confirmatory claim. Do not cite references until their bibliographic metadata and relevance have been checked.

## Methods: planned manuscript content

1. Audit exact paired RGB/LWIR sequence releases, rights, frame keys, track-ID conventions, ignored regions, gaps and native-versus-registered geometry before dataset admission. M3OT is a metadata candidate, not yet an approved source.
2. Freeze acquisition/flight-disjoint partitions and predeclare occlusion, temporary modality loss and viewpoint strata. State whether views are aerial or ground-based; manual alignment is not exposure synchronization.
3. Validate the chosen HOTA/IDF1 reference implementation on known deterministic fixtures, including ignore and missing-frame semantics; avoid executing untrusted third-party packages on persistent runners.
4. Hold detection proposals and timestamps identical across baseline association strategies: RGB-only, LWIR-only, fixed-fusion and modality-aware temporal association. Test full pipelines separately.
5. Report per-sequence HOTA, IDF1, identity switches, fragmentation, association/detection components and cluster-level uncertainty, including failed and untracked targets.

Methods and stopping criteria are governed by the [canonical protocol](protocol/README.md), not by this editorial outline. All measurements require provenance, code/data hashes, independent group definitions and explicitly recorded deviations.

## Results: required content, not yet available

**RESULTS PENDING.** Do not insert estimated or example numbers as observations. Once the study's gate passes, report the following, including negative results and uncertainty:

- Table: real sequence admission, identity-label coverage, independent flight grouping and viewpoint descriptions.
- Figure: HOTA per independent sequence and occlusion/missing-modality stratum with paired effects.
- Figure: separate detection and association components; identity-switch timelines on documented test cases.
- Table: evaluation version/fixture verification, source hashes and reproducibility status.

## Discussion: interpretive boundaries

Distinguish genuine temporal identity association from detector improvements, short track fragments and alignment artefacts. Discuss whether the acquired dataset supports claims specifically about UAV imagery; do not generalize ground vehicle sequences to aerial sensing. If identity labels or reference metric verification fail, tracking remains blocked rather than inferred from bounding-box overlap.

The final discussion must state external-validity limits, threats to identification and what the null result would imply. Reconcile the manuscript with sister projects to prevent duplicate claims or artificial splitting of one result across papers.

## Scientific gate and next editorial step

**Current block:** G06 real licensed track-ID-labelled paired sequences, correct temporal pairing and independently validated HOTA, #19, #22, #23.

**Next step:** complete the protocol preregistration and rights/provenance audit; develop the literature and methods sections while real-data evidence remains blocked. Select a journal and submission deadline only after independent scientific GO and owner authorization.

**Completion criterion for this page:** the manuscript's proposed question, introduction, prospective abstract, methods, reporting plan and boundary conditions are written. This page does **not** satisfy the empirical research gate or authorize submission.
