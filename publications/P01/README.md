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

**Scope argument:** P01 studies native RGB/LWIR observability and detection
failure under documented imaging conditions relevant to perception on
mobile robots. The contribution must be framed as a *sensor-aware detection
evaluation*, not as an experimentally demonstrated robot deployment,
navigation improvement or physical detection-range guarantee. The planned
study is distinct from P02 (pairing and fusion performance) and P03
(on-device resource measurement). Fit is **provisional** until the
editorial office responds; no inquiry has been sent.

## Provisional title and scope-check abstract (draft, not sent)

**Native-Pixel Footprint and Detection Reliability in RGB–Thermal
Perception for Mobile Robotics**

Low-cost RGB and long-wave infrared (LWIR) cameras are candidates for object detection in mobile-robot perception, yet the influence of physically acquired native target size on detection reliability remains difficult to isolate. Image resizing alone cannot reproduce changes in optics, sensor noise, thermal contrast, or acquisition geometry. This planned study will quantify the association between native target pixel footprint and held-out object-detection recall at a prespecified false-positive-per-frame operating point. Subject to verification of suitable original acquisitions and annotation rights, we will evaluate RGB-only and LWIR-only baselines, and a matched-budget fusion baseline where valid pairing is available. Target footprint will be measured in each sensor's original image grid and interpreted alongside view angle, occlusion, optical parameters, thermal contrast, and object class. Training, validation, and testing will be separated by independent acquisition or scene groups; thresholds and footprint strata will be fixed before inspecting the held-out test outcomes. We will report detection failures, false alarms, localization error, average precision, and uncertainty estimated over independent acquisition groups rather than treating adjacent frames as independent observations. Software downsampling will be analyzed only as a separate controlled ablation and will not support physical range-limit claims. The intended contribution is a reproducible, sensor-aware evaluation of where RGB and thermal detection becomes unreliable under documented acquisition conditions, with implications for the design and operating envelopes of mobile robotic perception systems. Empirical results, numerical limits, and deployment claims remain contingent on real-data admission and independent validation.

**Status of this abstract:** prospective research design only, not a
summary of completed experiments. All numerical results and claims of
physical detection limits are withheld until the [P01 protocol](protocol/README.md)
and independent data/evidence gates pass.

## Planned manuscript outline

1. Introduction: physical target observability and robot perception relevance.
2. Related work: native sensor resolution, RGB/LWIR detection and evaluation gaps.
3. Materials: admitted original datasets, sensor geometry, rights and labels.
4. Methods: native-footprint strata, operating-point calibration, independent
   splits, baselines, uncertainty and software-only ablations.
5. Results: per-modality detection and failure distributions (pending evidence).
6. Discussion: confounding, limitations, reproducibility and applicability.
7. Conclusions: evidence-bounded findings only (pending evidence).

**Work tracking:** [P01 evidence #24](https://github.com/MatPomGit/arc-rgbt/issues/24),
[study design and journal fit #35](https://github.com/MatPomGit/arc-rgbt/issues/35),
[data admission #36](https://github.com/MatPomGit/arc-rgbt/issues/36).
Internal package target: **2027-03-19**; publisher deadline: **2027-03-31**.
No editorial contact, submission, APC commitment or author sign-off is implied.
