# P02 study protocol

Specify inclusion/exclusion criteria, sensor calibration, datasets, controls, splits, uncertainty, statistical design and experimental stopping conditions before empirical data acquisition. No approved empirical protocol is claimed.

## Review-derived preregistration checks

- Establish capture **exposure** timestamps with a verified shared-clock
  transform; arrival times and synthetic E02 offsets are not physical
  synchronization evidence.
- Separate calibration residuals, geometric validity masks and thermal
  sampling limitations from detector confidence and modality quality
  estimation. Do not optimize quality weights on held-out ground truth.
- Compare RGB-only, thermal-only, fixed fusion and any adaptive method
  on the same predeclared scene holdout. Distinguish equal confidence
  thresholds from comparison at a matched false-alarm operating point.
- **Exit gate:** observed detector/association metrics, alignment error
  and time-skew distribution must come from independently labelled,
  calibrated acquisitions, not analytical rectangle IoU or hand-built
  proposal examples.

See [experimental evaluation requirements](../../../docs/guides/evaluation-requirements.md)
and [screened literature](../../../docs/experiments/literature-screening.md).
