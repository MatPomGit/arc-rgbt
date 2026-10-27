# Data contracts

Public examples live under `configs/` and `datasets/manifests/`. Values below describe currently implemented input contracts, not generalized camera standards.
External dataset vetting is a separate [admission process](../experiments/datasets.md); its screening metadata example is **not** a supported Bench or E01 import format.

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

## E01 labelled quality-fusion input

E01 requires top-level `experiment: E01`, `data_origin`
(`simulated`, `reference` or `measured`), `quality_origin`
(`synthetic_scenario`, `heuristic` or `measured_independent`),
`annotation_status: complete`, `config`, and nonempty `frames`.

- `config`: `iou_threshold` in (0, 1] and
  `min_effective_score` in [0, 1].
- Each frame: unique `id`, `ground_truth`, `rgb_predictions`,
  `thermal_predictions`, and `quality: {rgb, thermal}`.
- Each prediction: a nonempty `label`, positive-size
  `bbox: [x,y,width,height]` and a finite score in (0, 1].
  Both modalities must use a **common coordinate grid**.
- `quality.rgb` and `quality.thermal`: externally declared finite
  values in [0, 1], not calibrated detection probabilities.
- The output contains `manifest.json` and four-method `metrics.csv`.

See [E01](../experiments/e01.md).

## E02 timing and geometry scenario

The strict JSON schema requires `rgb_fps`, `thermal_fps` (positive,
at most 240); `frames` (integer 1 to 500); `tolerance_ms` (0 to
1000); nonempty `thermal_start_offsets_ms` (0 to 1000);
`native_thermal_sizes_px` (unique integer width/height pairs,
1 to 8192); `horizontal_fov_deg` (greater than 0, at most 179);
positive `target_range_m`, `target_width_m`; and nonnegative
`lateral_speeds_m_s` (at most 100).

Each configuration list is bounded, with a maximum 10,000 combinations.
`geometry.csv` contains per-grid overlap summaries. `manifest.json`
declares `data_origin: simulated`,
`metric_origin: analytical_geometry`, and
`physical_measurements: false`. Missing pairs yield `null` overlap
statistics rather than a measured-zero detection score.

See [E02](../experiments/e02.md).

## Image arrays and geometry

- DegradeSim: grayscale or RGB/RGBA numeric finite arrays, intensity in `[0,1]`, with positive target width/height.
- FusionLab image fusion: two finite, aligned grayscale 2-D arrays of identical shape.
- SensorLab: `width_px`, `height_px` (positive integers), `pixel_pitch_um` and `focal_length_mm` (finite positive numbers).
- E00 configuration: `seed`, `frames`, `optical_sigma_px`, `noise_sigma`, `threshold`, `min_area_px`, `interpolated_preview_px`; all fields required.

See [CLI reference](cli.md), [E00](../experiments/e00.md), and [evidence boundaries](../concepts/evidence.md).
