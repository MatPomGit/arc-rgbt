# Evidence and limitations

This project distinguishes **software correctness**, **simulation behaviour**, **reference algorithm output** and **experimental measurement**.

| Output | What it establishes | What it does not establish |
| --- | --- | --- |
| SensorLab geometry | A pinhole-model projection under the declared assumptions | Actual optical resolution or calibration uncertainty |
| DegradeSim images | Deterministic effects of the specified image transformation | LWIR radiometric accuracy |
| E00 detection metrics | Class-agnostic threshold localization on seeded synthetic rectangles | Classification accuracy for persons or vehicles |
| P01 summary | Consistency of manifest and metrics CSV and hashed artifacts | Statistical generalization to real sensors |
| E01 comparison | Four methods on the same hand-authored detection proposals | Calibrated scores or real detector performance |
| E02 geometry | Timestamp pairing and idealized lateral overlap of rectangles | Measured detector IoU or native-resolution detection sensitivity |
| Sync statistics | Timestamp-nearest pairing under a user-declared shared clock | Physical clock synchronization or exposure simultaneity |
| Registration masks | Full interpolation support after a supplied homography | Extrinsic calibration accuracy or parallax correction |
| EdgeLab reports | Latency of host OpenCV GaussianBlur and Python allocation peak | MCU inference, flash/RAM budget, device power |

## Core methodological safeguards

1. Record whether data are `simulated`, `measured` or `reference`. An origin label is metadata, **not** independent verification.
2. Keep sensor-native shape and optical/noise parameters. Specify interpolation policy and source-image pixel units.
3. Keep original capture-time timestamps in a shared monotonic clock; arrival timestamps are not interchangeable.
4. Exclude invalid projective pixels using the returned support mask before quantitative comparison.
5. Use independently annotated datasets, independent acquisition sequences and calibration uncertainties before reporting empirical detection performance.
6. Treat adjacent frames within one recording as correlated; compute uncertainty across independent scenes or acquisitions.

## Current non-goals

The software does not supply a trained person/vehicle detector, NIR/LWIR sensor drivers, an end-to-end calibrated RGB–thermal device, physical energy instrumentation, globally optimal time assignment or learned adaptive/temporal fusion. E01 is an externally weighted heuristic and E02 computes ideal analytical geometry.

See [E00](../experiments/e00.md), [research programme](../experiments/publications.md) and [reproducibility](../reproducibility.md).

## Evidence imported from external literature surveys

Historical review documents may be used to **identify research questions
and candidate citations**, but must not be copied as verified device
specifications, fixed detection ranges, universal accuracy percentages
or measured runtime results. When a source uses the word “accuracy”,
identify the exact metric, input images, operating point and split
before importing the claim.

For the protocol safeguards, see
[experimental evaluation requirements](../guides/evaluation-requirements.md).
For screened DOI candidates and citation-check status, see
[literature screening](../experiments/literature-screening.md).
