# P03: End-to-End Energy and Memory Constraints of Fixed Embedded RGB-Thermal Object Detection

**Editorial status:** CORE PLANNED; prospective manuscript content, version 0.1.0 (2026-10-31). **No accepted empirical results, submitted manuscript or journal acceptance.** Scientific hypotheses and results remain unverified; the protocol has not been frozen.

**Related task:** [issue #26](https://github.com/MatPomGit/arc-rgbt/issues/26). **Canonical research controls:** [hypotheses](hypotheses/README.md), [protocol](protocol/README.md), [portfolio](../../RESEARCH.md), [state](../../PROJECT_STATE.yaml), [measurement rules](../../docs/guides/evaluation-requirements.md). Additional context: [embedded measurement prerequisites](../../embedded/README.md).

## Proposed manuscript abstract (prospective, not a results abstract)

Multi-sensor object detection on constrained computing devices requires balancing perception quality against power, memory and timing constraints. This proposed empirical study will quantify that trade-off for fixed RGB-only, LWIR-only and dual-modality configurations on a specifically identified device with measured capture and inference interfaces. Rather than treating model latency or advertised accelerator throughput as system performance, the study will measure the full pipeline from acquisition through preprocessing, fusion and output. An external measurement procedure will estimate workload energy with an explicitly characterized idle reference and measurement uncertainty. Peak memory and flash footprint, latency distributions and independently evaluated detection recall at a locked false-alarm budget will form the feasibility constraints. Comparisons will use versioned model and input hashes, matched scene workloads and declared clock and thermal conditions. Unavailable configurations will be reported as infeasible instead of receiving synthetic benchmark values. The main contribution will be a reproducible end-to-end resource versus detection-quality analysis on the target hardware, contingent on independent measurement and scientific review. No physical device measurements have yet been accepted.

## Introduction: draft opening argument

The feasibility of an embedded RGB-LWIR detector is determined by whole-system behavior, not by model-only inference speed. Sensor readout, buffering, image transformations, inter-modality alignment and output interfaces consume memory, energy and execution time. This manuscript will assess **fixed configurations only** and show which perception targets remain achievable within measured resource constraints. Dynamic policy control belongs to the distinct, currently inactive P07 study.

The paper's research question and falsifiable null and alternative hypotheses are defined in the [hypothesis register](hypotheses/README.md). A protocol freeze and a literature novelty audit must precede any confirmatory claim. Do not cite references until their bibliographic metadata and relevance have been checked.

## Related work and testable contribution

Banbury et al., *MLPerf Tiny Benchmark* ([NeurIPS Datasets and Benchmarks 2021](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/da4fb5c6e93e74d3df8527599fa62642-Abstract-round1.html)), formalized reproducible accuracy, latency and energy comparisons for tiny inference systems. That benchmark provides an important measurement precedent, but **inference energy is not automatically the complete RGB/LWIR capture-to-output energy** claimed by this proposed paper.

Specify every included rail and subsystem, the power integration window, treatment of idle baseline, any non-metered peripherals, and repeatability before comparing devices. If sensor acquisition or fusion runs outside the measured supply boundary, present the reported quantity as partial energy, not system joules per completed frame. Any extension beyond standard TinyML benchmarks must come from measured multi-sensor system overhead and detection-quality constraints, not model specifications.

## Methods: planned manuscript content

1. Identify one reproducible target board and revision, processor/accelerator, operating system, sensors, input resolutions, interfaces, device power rails and allowable precision/quantization settings before benchmarking.
2. Define the measurement boundary, external meter, sample rate and calibration uncertainty; separately measure idle/reference power and include full sensing-to-output workload energy.
3. Freeze a feasible reference pipeline and fixed unimodal or dual-modality alternatives; record compilation/toolchain, clock mode, warm-up, thermal state, batch size, code and model hashes.
4. Run independent repeated workloads, measuring joules per completed frame, latency p50/p95/p99, peak RAM and nonvolatile storage; never replace unavailable physical readings with host timing.
5. Evaluate perception with lawful independent labels, a predeclared recall and FP/frame criterion and scene-grouped uncertainty, then report feasible and infeasible configurations on a Pareto view.

Methods and stopping criteria are governed by the [canonical protocol](protocol/README.md), not by this editorial outline. All measurements require provenance, code/data hashes, independent group definitions and explicitly recorded deviations.

## Results: required content, not yet available

**RESULTS PENDING.** Do not insert estimated or example numbers as observations. Once the study's gate passes, report the following, including negative results and uncertainty:

- Table: hardware identity, metering topology, device constraints and run/repetition traceability.
- Figure: energy per completed frame versus held-out recall with FP/frame and latency feasibility markings.
- Figure: acquisition, preprocessing, inference, registration/fusion and reporting latency components, including tail latency.
- Table: measured RAM/flash, uncertainty bounds, missing/infeasible configurations and run-level conditions.

## Discussion: interpretive boundaries

Separate empirical hardware limits from host reference measurements and architectural projections. Examine thermal throttling, sensor standby draw and the consequences of including capture overhead. A null result (no feasible dual-modality mode) remains publishable evidence if well characterized. P07 cannot be inferred from static Pareto curves; it needs a measured adaptive switching policy.

The final discussion must state external-validity limits, threats to identification and what the null result would imply. Reconcile the manuscript with sister projects to prevent duplicate claims or artificial splitting of one result across papers.

## Scientific gate and next editorial step

**Current block:** Named target, physically instrumented power/latency/RAM/flash and lawful held-out detection evidence, per #26. Hardware currently unverified.

**Next step:** complete the protocol preregistration and rights/provenance audit; develop the literature and methods sections while real-data evidence remains blocked. Select a journal and submission deadline only after independent scientific GO and owner authorization.

**Completion criterion for this page:** the manuscript's proposed question, introduction, prospective abstract, methods, reporting plan and boundary conditions are written. This page does **not** satisfy the empirical research gate or authorize submission.
