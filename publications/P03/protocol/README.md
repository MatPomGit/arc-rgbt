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
