# E02: Temporal skew and native angular-sampling geometry

## Purpose

Isolate *one* consequence of asynchronous frame acquisition: the expected
horizontal overlap of identical axis-aligned bounding boxes for a target
moving laterally relative to the camera. Simulated 30-fps RGB and 9-fps
thermal timestamps are paired using the existing nearest-unique-frame
algorithm under a selectable temporal tolerance. The offset, tolerance,
target width, target range, horizontal field of view, lateral velocity and
native thermal resolutions are explicit experimental controls.

## Analytical model

For a native image width W and horizontal field of view alpha:

- focal_px = W / (2 tan(alpha / 2))
- object_width_px = physical_target_width_m * focal_px / range_m
- horizontal_shift_px = lateral_speed_m_s * abs(skew_ms) / 1000 *
  focal_px / range_m
- geometric_bbox_IoU = (object_width_px - shift_px) /
  (object_width_px + shift_px), if shift_px is below object width, else zero.

Assumptions: pinhole camera, horizontal motion, identical upright,
frontal planar rectangular targets, unchanged width/range and no lens
distortion or scene parallax. Pairing is greedy; timestamps are generated
on a shared monotonic reference clock rather than obtained from sensors.

**Key limitation:** At fixed horizontal FOV, normalized overlap IoU is
independent of native pixel resolution in this continuous analytical
model. The experiment *does not* model lower-resolution loss of detection
ability, quantization, sensor PSF, NETD, image noise, thermal contrast,
classification or MCU latency. Any claim that one sensor resolution
improves detector performance from these scores is invalid.

## Reproduce offline

```bash
python -m arc_rgbt.e02 --config experiments/E02/config.json --output reports/E02
python -m pytest -q tests/test_e02.py
```

The configured synthetic sweep produces 84 rows: four thermal
start offsets, seven native thermal sizes and three lateral speeds.

Outputs are `reports/E02/manifest.json` and
`reports/E02/geometry.csv`, marked as simulated data with
analytical geometry metrics, a package version, git SHA when available
and a SHA-256 digest of the input configuration.

## Next empirical steps

Estimate thermal/RGB clock offsets from genuine exposure timestamps.
Use calibrated FOV and range, frame-level ground truth, radiometric
normalization, PSF/MTF and measured detector outputs. Compare quality
fusion using held-out scenes, report camera-motion stratification and
scene/flight-level uncertainty, and explicitly distinguish temporal
registration from detector inference.
