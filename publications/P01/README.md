# P01: low-resolution detection limits

Status: **planned study; no empirical results or manuscript submitted**.
[Hypotheses](hypotheses/README.md) · [preregistration gates](protocol/README.md) ·
[E00 reference method](../../docs/experiments/e00.md) ·
[implemented P01 analysis](analyses/README.md).

Project-wide work packages and blockers:
[AUTOPILOT_PLAN.md](../../AUTOPILOT_PLAN.md).

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


**Scope argument:** P01 studies native RGB/LWIR observability and detection
failure under documented imaging conditions relevant to perception on
mobile robots. The contribution must be framed as a *sensor-aware detection
evaluation*, not as an experimentally demonstrated robot deployment,
navigation improvement or physical detection-range guarantee. The planned
study is distinct from P02 (pairing and fusion performance) and P03
(on-device resource measurement). Fit is **provisional** until the
editorial office responds; no inquiry has been sent.

## Provisional title and scope-check abstract (draft, not sent)

**Native LWIR Target Footprint and Localization-Qualified Detection
Reliability for Mobile Robotic Perception**

Long-wave infrared (LWIR) cameras are considered for mobile-robot perception, but physically acquired target size must not be confused with resized detector inputs. This prospective study will investigate the association between native-grid LWIR object footprint and held-out localization-qualified detection recall, comparing small and reference target strata. The candidate primary contrast is an equally weighted mean of within-acquisition recall differences, restricted to independently verified acquisitions containing both bins. A fixed LWIR model will be evaluated at a confidence threshold selected exclusively on fully labelled validation frames using a prespecified false-positive-per-frame criterion. Held-out detection thresholds will not be retuned, including when the false-alert condition is missed. Detection outcomes will be allocated to independently annotated original-grid objects; we will report missed targets, false alarms, localization-tolerance sensitivity, and variation by class, thermal contrast, viewpoint and occlusion. Uncertainty will be estimated by resampling independent acquisitions, not adjacent video frames. RGB-only evaluation will be secondary; RGB–thermal fusion is treated in a separate study. Source permissions, native optics, spectral band, annotations and acquisition identities must pass independent verification before physical data are admitted. The measured image-plane footprint is not a calibrated range or a causal sensor-resolution effect. All numerical analysis choices remain pending author approval. No observed performance results, physical distance limits or robot deployment claims are asserted.

**Status of this abstract:** prospective research design only, not a
summary of completed experiments. All numerical results and claims of
physical detection limits are withheld until the [P01 protocol](protocol/README.md)
and independent data/evidence gates pass.

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

The proposed contribution is an **acquisition-aware operating-envelope
analysis**: a fixed, validation-selected false-alert budget, target footprint
measured on verified original sensor grids, independent acquisition-group
uncertainty, and explicit separation of physical imaging evidence from
software downsampling. This is a proposed distinction, **not a completed
novelty or reproducibility review**. The exact eligible data and the
applicability of these comparisons still require #10/#36 admission and #29
independent review.

### Candidate novelty matrix (no originality claim yet)

| Prior work | Established precedent | Evidence required for P01 distinction |
| --- | --- | --- |
| Poster et al. (Sensors 2023) | Long-range small targets, including **MWIR** | Actual native **LWIR** geometry and sensor-specific applicability |
| Ying et al. (RGBT-Tiny) | Tiny visible-thermal benchmark and annotations | Independently confirmed original-grid labels, rights and acquisition IDs |
| RAPT-Net (Remote Sensing 2026) | Multimodal detection with tiny-target evaluation | A distinct, source-audited within-acquisition fixed-FP operating analysis |
| P01 candidate | Proposed combined LWIR native-footprint / fixed FP/frame / group-based uncertainty contract | Reproducible real-data admission, matching, comparisons and methodological novelty audit |

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

1. Is an original-source native-LWIR target-footprint analysis of
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

1. Introduction: physical target observability and robot perception relevance.
2. Related work: native sensor resolution, RGB/LWIR detection and evaluation gaps.
3. Materials: admitted original datasets, sensor geometry, rights and labels.
4. Methods: native-footprint strata, operating-point calibration, independent
   splits, baselines, uncertainty and software-only ablations.
5. Results: LWIR within-acquisition recall, false alerts and secondary RGB comparisons (pending evidence).
6. Discussion: confounding, limitations, reproducibility and applicability.
7. Conclusions: evidence-bounded findings only (pending evidence).

**Work tracking:** [P01 evidence #24](https://github.com/MatPomGit/arc-rgbt/issues/24),
[study design and journal fit #35](https://github.com/MatPomGit/arc-rgbt/issues/35),
[data admission #36](https://github.com/MatPomGit/arc-rgbt/issues/36).
Internal package target: **2027-03-19**; publisher deadline: **2027-03-31**.
No editorial contact, submission, APC commitment or author sign-off is implied.
