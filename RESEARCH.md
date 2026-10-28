# Research programme: eight publication candidates

**Planning baseline: 2026-10-28. Six core streams P01–P06; two optional streams P07–P08 remain HOLD.** All eight are concepts; none has a confirmed manuscript submission or independently validated field result.

| Paper | Main question and independent outcome | Role | Protocol |
| --- | --- | --- | --- |
| P01 | Native resolution/optical footprint vs. object localization and detection | CORE | [P01](publications/P01/protocol/README.md) |
| P02 | Exposure pairing, registration and modality-quality fusion; recall at matched false-alert budget | CORE | [P02](publications/P02/protocol/README.md) |
| P03 | Fixed embedded inference pipeline: measured accuracy vs. RAM/flash/latency/energy | CORE | [P03](publications/P03/protocol/README.md) |
| P04 | Reliability under missing/degraded modalities: worst-stratum miss rate with alert/coverage constraints | CORE | [P04](publications/P04/protocol/README.md) |
| P05 | Cross-device/domain transfer: out-of-domain detection AP decline | CORE | [P05](publications/P05/protocol/README.md) |
| P06 | Identity-preserving multi-object association: HOTA on real labelled sequences | CORE | [P06](publications/P06/protocol/README.md) |
| P07 | Adaptive modality/inference policy: measured joules per scene at matched perception | **OPTIONAL HOLD** | [P07](publications/P07/protocol/README.md) |
| P08 | Calibration/timing uncertainty propagation: observed risk-bound coverage | **OPTIONAL HOLD** | [P08](publications/P08/protocol/README.md) |

## Independence rule

P01: physical spatial observability; P02: ordinary fusion and frame alignment; P03: fixed embedded device benchmarking; P04: fault handling and selective risk; P05: independent cross-sensor generalization; P06: temporal identity association; P07: policy-dependent energy saving, **not** static P03 profiling; P08: validated risk-bound calibration, **not** mean P02 registration error. A paper without a distinct falsifiable primary endpoint, adequate independent evidence or a defensible novelty contribution is **not** submitted as a separate manuscript; its results are merged into the relevant parent study instead.

## Activation and evidence policy

- P01–P06 are planned research tasks, not completed studies. Independent legal data and real labels remain unverified.
- P04 requires fault-stratified risk/coverage evidence; P05 requires genuinely independent sensor-domain cohorts; P06 needs track-ID annotations on real sequences.
- P07 remains HOLD until measured P03 physical baseline, actual adaptive sensing/compute switching, metered energy data, matched-quality performance and independent non-overlap review are all PASS.
- P08 remains HOLD until independently measured P02 calibration and exposure timing uncertainty, out-of-sample uncertainty/risk-bound coverage and non-overlap review are all PASS.
- E00/E01/E02 are synthetic/analytical reference baselines only. Host EdgeLab cannot substantiate MCU or physical energy claims.
- No automatic submission or publication authorization follows from any GO review.

Scientific constraints and detailed hypotheses are in the respective protocols. [Publication overview](docs/experiments/publications.md), [datasets](docs/experiments/datasets.md), [work packages](AUTOPILOT_PLAN.md), [evidence status](PROJECT_STATE.yaml) and [reproducibility](REPRODUCIBILITY.md) are authoritative in their respective domains.
