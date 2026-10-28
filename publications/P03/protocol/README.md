# P03 study protocol

Specify inclusion/exclusion criteria, sensor calibration, datasets, controls, splits, uncertainty, statistical design and experimental stopping conditions before empirical data acquisition. No approved empirical protocol is claimed.

## Review-derived preregistration checks

- Specify device and numeric precision, model/input resolution, memory
  accounting boundary, batch size, warm-up and clock/thermal conditions.
- Decompose end-to-end latency into acquisition, preprocessing, inference,
  multimodal alignment/fusion and output reporting. Record distribution
  and throughput, not only mean device-model inference time.
- Measure energy on the **actual target device** with a named instrument,
  idle-power reference and workload duration. Never equate a host OpenCV
  benchmark or claimed TOPS with target-device Joules per processed frame.
- **Exit gate:** publish embedded efficiency comparisons only with
  logged physical power, latency and RAM/flash measurements plus
  independently assessed perception quality.

See [experimental evaluation requirements](../../../docs/guides/evaluation-requirements.md)
and [screened literature](../../../docs/experiments/literature-screening.md).

## Planned fixed-pipeline study (not yet preregistered)

- **Primary endpoint:** physically instrumented joules per complete frame under preregistered held-out detection recall/FP-frame and latency requirements; peak on-device memory and flash are co-constraints.
- **Feasible controls:** RGB-only, LWIR-only and dual-modality fixed configurations, with identical sensor/image workloads; record configurations that cannot execute on the target as infeasible.
- **Experimental design:** predeclare target board, numeric precision, warm-up, idle reference, power-meter uncertainty, capture/fusion/IO timing boundaries and cold/hot clock regimes. Repeated scene workloads and deterministic model hashes required.
- **Acceptance:** independent labels, code/model/source revisions and separately metered acquisition through output pipeline available. P03 remains blocked until real target RAM, flash, latency and energy traces are independently verified.
- **Separation from P07:** P03 compares fixed configurations; P07 would require a separately novel adaptive modality/compute switching policy with independently measured real energy saving and matched perception.

[Hypothesis and estimands](../hypotheses/README.md) · [hardware prerequisites](../../../embedded/README.md).
