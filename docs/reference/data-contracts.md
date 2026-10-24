# Data contracts

Public examples live under `configs/` and `datasets/manifests/`. Values below describe currently implemented input contracts, not generalized camera standards.

## Detection benchmark JSON

```json
{
  "data_origin": "simulated",
  "config": {"purpose": "example"},
  "frames": [{
    "id": "frame-001",
    "ground_truth": [{"label": "object", "bbox": [10, 10, 20, 20]}],
    "predictions": [{"label": "object", "bbox": [10, 10, 20, 20], "score": 0.9}]
  }]
}
```

- Each box is `[x, y, width, height]` with finite numbers and strictly positive width/height.
- Prediction `score` must be finite and in `[0, 1]`. Box fusion uses strictly positive scores.
- Labels are nonempty strings; prediction classes must match ground truth to count as TP.
- Frame IDs are unique nonempty strings or integers; booleans are not valid frame IDs.
- The optional top-level `"annotation_status": "complete"` permits verified fully negative ground truth. A totally empty frame array is still rejected.
- Allowed Bench data origins: `simulated`, `measured`, `reference`.

## Timestamp pairing JSON

```json
{
  "data_origin": "simulated",
  "clock_domain": "shared_monotonic_ns",
  "tolerance_ms": 20,
  "rgb_frames": [{"id": "rgb-001", "timestamp_ns": 0}],
  "thermal_frames": [{"id": "ir-001", "timestamp_ns": 6000000}]
}
```

Per-stream timestamps must be **strictly increasing**, nonnegative integers representing nanoseconds in the same verified capture-time clock domain. Frame IDs are unique nonempty strings *within each stream*. `tolerance_ms` must be a finite nonnegative real value.

The result includes `pairs` (IDs, timestamps and signed `delta_ms = (RGB - thermal)/1e6`), `summary` and explicit limitations. It does not correct clock drift or timing offsets.

## Homography registration

The input matrix is a JSON 3×3 **RGB-to-thermal** homogeneous pixel transform:

```json
[[0.5, 0, 0], [0, 0.5, 0], [0, 0, 1]]
```

Finite, nonsingular, well-conditioned matrices only. The explicit `--calibration-origin` describes its source. By default, output is on the **thermal** grid; `--reference rgb` inversely warps thermal data for analysis. The `valid` mask identifies full bilinear interpolation support, excluding partially padded boundaries.

## Image arrays and geometry

- DegradeSim: grayscale or RGB/RGBA numeric finite arrays, intensity in `[0,1]`, with positive target width/height.
- FusionLab image fusion: two finite, aligned grayscale 2-D arrays of identical shape.
- SensorLab: `width_px`, `height_px` (positive integers), `pixel_pitch_um` and `focal_length_mm` (finite positive numbers).
- E00 configuration: `seed`, `frames`, `optical_sigma_px`, `noise_sigma`, `threshold`, `min_area_px`, `interpolated_preview_px`; all fields required.

See [CLI reference](cli.md), [E00](../experiments/e00.md), and [evidence boundaries](../concepts/evidence.md).
