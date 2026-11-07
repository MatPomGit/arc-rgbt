# P01: LWIR detection performance by source-annotated target footprint

**Decision sheet v0.3.0 · 2026-11-07 · CONDITIONAL_DESIGN / UNFROZEN.**
Author approval of an eventual frozen analysis and claim tier remains pending.
This study uses supplied labels; it does not conduct an annotation-quality
experiment or assert that missing labels prove real negative scenes.

## Current Tier A research question and estimand (#50)

**Question:** Among source-labelled LWIR targets, is recall lower for
smaller annotated image-plane footprints when a fixed detector is evaluated
at a validation-selected false-positive budget, *relative to supplied GT*?

- Candidate primary target class: **car**, without reclassifying `rider` as
  `person`. Other source classes require separately specified mappings.
- Per-GT proxy: `s = sqrt(width_xywh * height_xywh)` on the declared **COCO
  export grid**. Candidate bins: small `s < 8`, intermediate
  `8 <= s < 16`, reference `s >= 16` pixels. This proxy is not a proven
  native focal-plane footprint or physical detection-range estimate.
- Matching: one-to-one same-class boxes, IoU >= 0.50, descending score,
  deterministic tie order. IoU=0.25 is a sensitivity analysis only.
- Reference-relative `FP/frame` uses unmatched detections divided by
  all selected source-labelled frames, including frames with no source GT.
  These are *reference-negative*, not certified object-free.
- Candidate operating budget: 0.10 reference FP/frame. Choose the lowest
  feasible confidence score from **validation only**, preserving tied scores
  and at least one TP; lock it before any holdout reading. If infeasible,
  report `BLOCKED_VALIDATION`, not a tuned holdout result.
- If independently verified acquisitions with both bins exist, candidate
  group contrast `d_g = TP_small,g / GT_small,g - TP_ref,g / GT_ref,g`;
  `Delta = mean_g(d_g)`, equally weighting true acquisitions. All-negative
  groups remain in the FP/frame denominator but not this paired contrast.
  Currently, source `video_id` is a **proxy**, so no confirmatory
  acquisition-independent hypothesis test or cluster CI is authorized.

## H0/H1 conditional on source-independent group evidence

If a prospective author decision establishes authentic acquisition units,
adequate group support, control of relevant confounding and calibrated
inference before held-out outcomes, the directional candidates are
`H0: Delta >= 0`, `H1: Delta < 0` with one-sided alpha 0.05. A two-sided
95% CI is descriptive and cannot substitute for that directional test.
The one-sided group-t test and its finite-group calibration remain
**unapproved candidates** under #49/#50/#53. No p-value is currently
prespecified for unverified source-video proxies.

Without this evidence, report source-GT-relative per-bin recall and
FP/frame, group counts, pooled sensitivity and failures as
`DESCRIPTIVE_ONLY`. Do not imply camera optics causality: small and large
targets can differ in contrast, class, viewpoint, obstruction, blur and
acquisition conditions. Provide class/scene distributions when available,
but no post-hoc inference promotion.

## Distinct outcomes and scientific gates

- **Tier A:** reproducible detector output compared with the existing
  lawful dataset labels. The exact annotation/release version, data split,
  model checkpoint provenance, scores and input/result hashes are required.
  Label incompleteness and training-data overlap remain explicit limitations.
- **Tier B:** any claim about physical **native LWIR sensor** limits needs
  separately verified original-grid optics, annotation coordinate mapping,
  lawful source identity and true independent acquisitions; otherwise
  **BLOCKED**. Descriptive Tier A results cannot validate Tier B.
- RGB is a secondary comparator; RGB-LWIR fusion is primarily P02.
  Artificial resizing E00 is a separately labelled **simulation**.
- No manual reannotation/two-reviewer QA is required. Independent numerical
  reproduction and final manuscript review do not imply new source labelling.
- No test-set optimisation, automatic science GO, editorial contact,
  payments or journal submission.

[Operational protocol](../protocol/README.md) ·
[Source-GT evaluation runner](../analyses/README.md) ·
[Milestone #35](https://github.com/MatPomGit/arc-rgbt/issues/35) ·
[Decision #50](https://github.com/MatPomGit/arc-rgbt/issues/50) ·
[Operating point #51](https://github.com/MatPomGit/arc-rgbt/issues/51).
