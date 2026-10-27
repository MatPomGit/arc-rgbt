# Measurement and evaluation requirements

This guide translates an internal aerial imaging literature review into
**vendor-independent scientific evaluation rules**. It is not a UAV flight,
autonomous pursuit, geolocation, or target-control specification.
The cited source review supplied candidate research questions, not validated
performance guarantees.

## Optical geometry before range claims

- Record physical target extent **in the image plane**, view direction,
  calibrated focal length, sensor pitch, optical FOV, native frame size
  and imaging distance. An approximate pixel footprint is useful only
  when projection assumptions are stated.
- **Nadir and oblique imagery must not be conflated.** For a top-down view,
  a vertical object's standing height is not its projected height in
  the sensor image. Use the appropriate visible footprint or calibrated
  3D projection. For oblique views, account for pose and perspective.
- Annotate blur, camera motion, occlusion, contrast, thermal response and
  detector input resizing separately. Upsampling cannot restore spatial
  information removed by the physical sensor.
- Do not publish an unconditional detection range. A distance is an
  experimental condition and must be paired with optical and task
  specifications, not asserted as a universal capability.

## Minimum per-run metadata

| Domain | Record with every experimental result |
| --- | --- |
| Images | Modality (RGB, NIR or LWIR), native width/height, bit depth, radiometric or normalized input |
| Geometry | FOV, calibrated intrinsics/extrinsics, reference coordinate grid, valid support mask, view angle and object footprint |
| Timing | Exposure-time timestamps, clock domain, synchronization method, signed skew distribution, dropped/unpaired frames |
| Detector | Model and checkpoint ID, training/validation/test split, input resolution, confidence threshold, IoU policy |
| Evaluation | Class labels, annotation completeness, scene/sequence identity, independent test units and uncertainty intervals |
| Compute | Hardware, processor/accelerator, precision, warm-up, batch size, thermal conditions, runtime stack |
| Throughput | Capture, preprocessing, inference, fusion and full-pipeline latency distributions; throughput in frames/s |
| Energy | Measurement instrument, measurement boundary, units (W and J/frame), idle reference and workload |

A frame rate reported without the image size, model, processor,
numeric precision and loaded pipeline is **not a reproducible benchmark**.
A host-only timing or memory estimate is not an on-device MCU result.

## Reporting metrics without category errors

- Report **precision, recall, F1 and AP/mAP** separately as applicable.
  Specify IoU threshold(s), confidence threshold, classes, datasets and
  matching policy. Never substitute a single ambiguous “accuracy”.
- A fixed confidence threshold across methods does **not** guarantee
  a common false-positive budget. State whether the comparison is at
  matched thresholds or matched operating points.
- Evaluate low-pixel-footprint regimes by predeclared strata and
  supply uncertainty over independent scenes/sequences, not adjacent
  frames treated as independent replicates.
- Include failures: annotation gaps, unpaired frames, invalid geometric
  overlap, occlusion, nonrepresentative illumination and uncalibrated
  thermal contrast. Negative frames require documented complete labels.
- Treat literature performance numbers as **study-specific**, until
  the original paper's metric definition, test data and implementation
  are verified.

## Correspondence with the current software

| Research question | Current implementation | Evidence boundary |
| --- | --- | --- |
| Native optical footprint | SensorLab, E00 | Pinhole model and synthetic images, not sensor calibration |
| Spatial degradation | DegradeSim | Deterministic software transformation, not measured PSF/NETD |
| Relative fusion behaviour | FusionLab, E01 | E01 quality factors are externally set, not inferred confidence |
| Capture-time mismatch | Synchronization, E02 | E02 timestamps and overlap are simulated analytical quantities |
| Projective valid area | Registration | An externally supplied homography, not a calibration solver |
| Resource limits | EdgeLab | Host operator profiling, not device inference/energy |

This guide does not alter the existing module contracts. For method details
see [sensor geometry](sensors-degradation.md),
[quality-aware fusion](quality-fusion.md),
[E01](../experiments/e01.md), [E02](../experiments/e02.md)
and [evidence limitations](../concepts/evidence.md).

## Questions to resolve before physical studies

1. Is the RGB/thermal pair actually synchronized by **exposure**, and
   how is clock offset/drift quantified?
2. Are camera intrinsics, extrinsics and valid overlap independently measured?
3. How were native-grid pixel footprint, object orientation and image
   preprocessing defined?
4. Can the release/licensing of datasets and annotations be documented?
5. Are accuracy, latency, memory and energy **measured on the stated target**
   with replicable logs, or estimated from simulation/host code?
6. Do the published primary sources support their quoted metrics under
   comparable conditions?

Source triage and selected public references:
[literature screening](../experiments/literature-screening.md).
