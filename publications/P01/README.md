# P01: low-resolution detection limits

Status: **planned study; no empirical results or manuscript submitted**.
[Hypotheses](hypotheses/README.md) · [preregistration gates](protocol/README.md) ·
[E00 reference method](../../docs/experiments/e00.md) ·
[implemented P01 analysis](analyses/README.md).

Project-wide work packages and blockers:
[AUTOPILOT_PLAN.md](../../AUTOPILOT_PLAN.md).

## Current execution policy (2026-11-07)

The agent owns scientific code, local-execution preparation, labelled-dataset benchmark, analysis, figures and manuscript. No obligatory two-reviewer source reannotation, manual CSV forms or new dataset QA workstreams. Where actual files/GPU are local-only, use one short offline command and small hash-backed results. Dataset-relative performance does **not** itself prove physical sensor detection limits. See the [current plan](../../AUTOPILOT_PLAN.md) and [P01 evidence tiers](protocol/README.md) for the authoritative contract.

## Target journal and fit assessment (2026-10-31)

**Selected target:** *Sensors* (MDPI), Special Issue
[Intelligent Mobile Robotics: Object Recognition, Human–Robot Interaction and Autonomous Navigation](https://www.mdpi.com/journal/sensors/special_issues/XR7I5HPX5P),
section *Navigation and Positioning*, Guest Editor Dr. Tomasz Krzeszowski.
The publisher lists a **31 March 2027** submission deadline and **2600 CHF**
APC before discounts/taxes (checked 2026-10-31; recheck before submission).
The call explicitly includes object detection and multi-sensor analysis.
The journal invites a proposed title and approximately 250-word abstract
for an editorial scope assessment.

**Funding planning assumption (owner decision 2026-11-02):** The university will cover the *Sensors* article processing charge for P01. Treat the APC as **institutionally funded in the project plan**, not an unfunded research blocker. This statement is **not proof of payment, a signed funding agreement or authority for an agent to purchase or submit**. The corresponding author must verify the final payable rate, current university payment procedure, invoice recipient and administrative requirements before any authorized submission. No agency/editor outreach or invoice request has been sent by this update. [Current agent execution plan](../../AUTOPILOT_PLAN.md).


**Scope argument:** P01's Tier A studies LWIR detector failures relative to
source-labelled target footprint and a validation-locked false-alert budget,
motivated by perception for mobile robots. It does not yet measure
original native LWIR sensor limits. The contribution must be framed as a
*source-reference detection evaluation*, not demonstrated robot deployment,
navigation improvement or physical detection-range guarantee. The planned
study is distinct from P02 (pairing and fusion performance) and P03
(on-device resource measurement). Fit is **provisional** until the
editorial office responds; no inquiry has been sent.

## Provisional title and scope-check abstract (draft, not sent)

**Source-Annotated LWIR Target Footprint and Localization-Qualified
Detection Reliability for Mobile Robotic Perception**

Thermal object detection is relevant to mobile-robot perception, but image-plane target footprint reported by an annotated dataset should not be conflated with native sensor sampling or physical range. This prospective study will examine the relationship between source-annotated thermal target footprint and localization-qualified detection recall for a fixed long-wave infrared detector on a lawfully usable, versioned image release. The Tier A analysis will use existing dataset labels as its declared reference, with candidate car targets stratified by the square root of annotated bounding-box area on the COCO export grid. At an operating point selected exclusively from group-separated validation data using a prespecified budget of source-label-relative false detections per frame, we will report fixed-threshold recall by footprint bin, missed targets, reference-relative false positives, localization sensitivity and sample denominators. Holdout thresholds and exclusion rules will not be retuned after outcomes are inspected. Within-acquisition contrasts and clustered uncertainty will be calculated only where provenance supports independent acquisitions; otherwise results will remain descriptive. Source annotations do not establish exhaustive labelling, and small and large targets may differ in thermal contrast, viewpoint, obstruction and acquisition conditions. Physical native LWIR footprint or detection-range conclusions would require separately verified optics, image transforms and acquisition metadata, and are not default claims of this benchmark. RGB-only evaluation will be secondary; fusion belongs to a separate study. No empirical outcomes, mobile-robot deployment gains or causal sensor-resolution effects are asserted before analysis.

**Status of this abstract:** prospective **Tier A source-reference**
design only, not a summary of completed experiments. It is an unsent
scope-check abstract (the journal's published guidance is about 250
words), **not** the approximately 200-word results-bearing abstract
required for a submitted research article. The source-export footprint
is not the camera's proven original-grid footprint. All numerical
results and Tier B physical claims remain withheld until the
[P01 prospective decision packet](protocol/README.md#p01-s09-author-decision-packet-v040-2026-11-09-unfrozen)
and evidence gates pass.

## Literature-grounded gap and novelty boundary (2026-11-01)

Poster, Hu and Nasrabadi (2023),
[doi:10.3390/s23187806](https://doi.org/10.3390/s23187806),
studied long-range small-target detection and restricted receptive fields.
Their DSIAC example uses **MWIR**, not LWIR; it is a useful pixels-on-target
methodological precedent but cannot validate LWIR sensor-specific limits.
Ying et al., [RGBT-Tiny (arXiv:2406.14482)](https://arxiv.org/abs/2406.14482),
present a visible-thermal tiny-object benchmark with paired annotations;
the cited preprint does **not** establish original-archive image/label
licences, native optical geometry or independent sensor exposure timing for
P01. Recent [RAPT-Net (2026)](https://www.mdpi.com/2072-4292/18/3/449)
also studies multimodal tiny-target detection with scale-specific evaluation;
novelty cannot rest on tiny-object bins or RGB/thermal combination alone.

The proposed Tier A contribution is a **source-reference operating-envelope
analysis**: a fixed validation-selected false-alert budget, target footprint
measured on the declared COCO export grid, and independent
acquisition-group uncertainty **only when authentic groups exist**.
Otherwise the analysis is descriptive. Any original-native-grid
physical extension remains separately blocked. This is a proposed
distinction, **not a completed novelty or reproducibility review**.
Exact eligible data and applicability still require #10/#36 admission
and #29 independent review.

### Candidate novelty matrix (no originality claim yet)

| Prior work | Established precedent | Evidence required for P01 distinction |
| --- | --- | --- |
| Poster et al. (Sensors 2023) | Long-range small targets, including **MWIR** | Actual native **LWIR** geometry and sensor-specific applicability |
| Ying et al. (RGBT-Tiny) | Tiny visible-thermal benchmark and annotations | Independently confirmed original-grid labels, rights and acquisition IDs |
| RAPT-Net (Remote Sensing 2026) | Multimodal detection with tiny-target evaluation | A distinct, source-audited within-acquisition fixed-FP operating analysis |
| P01 Tier A candidate | Source-annotation LWIR export-grid footprint / validation-fixed FP/frame / eligible acquisition contrast only when supported | Exact source release, lawful labels, detector provenance, group support, reproducible results and novelty audit |

The table is prospective, not a systematic review or demonstrated
novelty. Comparator definitions, spectral bands, licences and native
acquisition metadata remain subject to direct verification.

## Unsent editorial scope-check package (2026-11-04)

**Editorial fit: PROVISIONAL; no inquiry sent.** The [official Special Issue
call](https://www.mdpi.com/journal/sensors/special_issues/XR7I5HPX5P)
was checked on 2026-11-04. It lists a **2027-03-31** deadline, welcomes
object detection and multi-sensor analysis for mobile robotics, and permits
a proposed title with an **approximately 250-word abstract** for an
initial editorial scope check. The title and prospective abstract above
are the proposed package; they do not contain experimental findings.

The [Sensors author instructions](https://www.mdpi.com/journal/sensors/instructions)
were also checked on 2026-11-04. A *submitted manuscript* is expected to
have an abstract of **about 200 words maximum**, which must summarize
actual supported results and conclusions. The longer prospective
scope-check abstract above is **not** a submission abstract. A compliant
results-bearing abstract can be finalized only after eligible experiments.
Submission materials must address source and code availability, ethics,
author contributions, funding and conflicts of interest. No results, real
sensor performance, manuscript acceptance or author approval are inferred
from this screening.

**Scope questions for a future authorized editorial inquiry** (not sent):

1. Is a source-label-relative LWIR target-footprint analysis of
   localization-qualified detection at a validation-fixed false-alert
   operating point within this Special Issue's object-detection scope
   **without** physical mobile-robot field trials?
2. Would a LWIR-only primary analysis with RGB-only *secondary* comparisons
   be considered in scope, provided that RGB–LWIR fusion is addressed in a
   separate manuscript and no multi-sensor deployment benefit is claimed?
3. Which novelty and original-data documentation would the Editorial
   Office expect for this observational, acquisition-grouped evaluation
   relative to existing small-target and RGBT benchmarks?

**Financial/administrative check, separate from editorial suitability.**
The [publisher's current Sensors APC](https://www.mdpi.com/journal/sensors/apc)
is **2600 CHF** before applicable taxes and discounts. The
[MDPI discount guidance](https://www.mdpi.com/about/apc_faq) describes
institutional IOAP/affiliation reductions and eligible reviewer vouchers;
eligibility and stacking must be verified with the institution and
publisher before acceptance. The university-coverage statement above is a
planning assumption; neither a discount nor any charge is approved here.
A future inquiry must not request preferential peer review or editorial
treatment in exchange for funding, affiliation or reviewer status.

**Precheck release conditions:** verify source rights and original thermal
geometry (#45-#47), authentic independent acquisition groups and non-test
precision (#48), independent interval-method review (#49), the numerical
decision sheet (#50-#51), and author decision (#53). The prospective
abstract and questions may be circulated for internal review while these
conditions are pending. Contact with editors, payment and submission each
require separate explicit authorization. The protocol remains **UNFROZEN /
DATA BLOCKED**; see the [canonical decision record](protocol/README.md).

## Planned manuscript outline

1. Introduction: small-target detectability and relevance to mobile-robot perception.
2. Related work: LWIR target-footprint evaluation, detection and limitations of sensor-specific claims.
3. Materials: lawful, versioned source images and supplied labels; geometry provenance and rights.
4. Methods: COCO export-grid footprint strata, validation-only calibration,
   verified grouping where available, baselines and descriptive uncertainty.
5. Results: source-GT-relative recall, FP/frame, AP and secondary RGB comparisons (pending evidence).
6. Discussion: confounding, limitations, reproducibility and applicability.
7. Conclusions: evidence-bounded findings only (pending evidence).

**Work tracking:** [P01 evidence #24](https://github.com/MatPomGit/arc-rgbt/issues/24),
[study design and journal fit #35](https://github.com/MatPomGit/arc-rgbt/issues/35),
[data admission #36](https://github.com/MatPomGit/arc-rgbt/issues/36).
Internal package target: **2027-03-19**; publisher deadline: **2027-03-31**.
No editorial contact, submission, APC commitment or author sign-off is implied.
