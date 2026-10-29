# Data contracts

Public examples live under `configs/` and `datasets/manifests/`. Values below describe currently implemented input contracts, not generalized camera standards.
External dataset vetting is a separate [admission process](../experiments/datasets.md); its screening metadata example is **not** a supported Bench or E01 import format.

## Candidate metadata admission inventory (implemented v1)

Separate from the existing `.npy` sequence audit, `arc-rgbt admission` validates **JSON metadata only**. It does not inspect or hash original image files, labels, licence text or capture clocks. Its structural PASS always reports `empirical_admission: false` and cannot satisfy B01, B02 or G06.

The [synthetic example](https://github.com/MatPomGit/arc-rgbt/blob/main/datasets/manifests/admission-synthetic.json) uses illustrative, **not actual image** SHA-256 values:

```bash
arc-rgbt admission --input datasets/manifests/admission-synthetic.json
arc-rgbt-admission --input datasets/manifests/admission-synthetic.json --output reports/admission.json
```

Strict root fields: `schema_version: 1`, `data_origin: metadata_only`, `dataset` and `sequences`.

- Dataset fields: `id`, `release`, `owner_url` (HTTPS), `licence_url` (HTTPS or null), `rights_status` (`needs_review`, `owner_terms_identified`, `independently_reviewed`, **declared only**) and `archive_sha256` (lowercase 64-hex or null).
- Each sequence: `id`, `flight_group`, `scene_group`, `device_id`, `split` (`train`, `validation`, `test`), `rgb`, `thermal`, `pairing_origin` (`manual`, `declared_clock`, `unknown`), `exposure_clock` (`unknown`, `declared_only`), and `frames`.
- Modality descriptors: `band` is `rgb` for RGB, one of `lwir`, `nir`, `unverified_ir` for thermal/IR. Declare `native_grid_wh`, `processed_grid_wh` as `[width,height]`, and `grid_origin` (`original_native`, `aligned_crop`, `unknown`). Original-native geometry cannot declare a different processed grid.
- Each paired frame: unique `pair_id`, `rgb_id`, `thermal_id`, increasing `frame_index`, lowercase `rgb_sha256`, `thermal_sha256`, `annotation_status` (`complete`, `partial`, `unknown`), and `objects`.
- Object fields: `modality` (`rgb`/`thermal`), `track_id`, `label`, `bbox_xywh` (finite positive box fully inside **processed** modality grid). Track IDs are modality-local; equal names do not prove cross-sensor identity.

Global duplicate image hashes, duplicate per-stream IDs, duplicate track IDs within a frame/modality, and assigning the same flight or scene group to multiple train/validation/test splits fail validation. Gaps in track IDs are **reported** as possible occlusions, not necessarily errors. Input bounds: 8 MiB, 2000 sequences, 50,000 paired frames, 256 objects per pair. Unknown schema fields and duplicate JSON keys are rejected.

The optional output is created exclusively and never overwrites existing files. This tool cannot establish actual frame-to-frame identity correctness, measured exposure synchronization, annotation completeness or dataset permission. It does not calculate AP/HOTA/IDF1 or automatically allocate splits. See [dataset admission policy](../experiments/datasets.md).

## Proposed split and metric contracts (M1, implemented)

The `arc-rgbt split` (also `arc-rgbt-split`) command takes the **same** metadata-only admission inventory, checks it through the existing `admission.analyze`, then groups sequences into connected components by shared `flight_group` or `scene_group`. With `--device-disjoint`, shared `device_id` also joins components. A seeded SHA-256 ordering assigns entire components to train/validation/test. Minimum three independent groups required; a complete 3-way split is **impossible** with fewer. This is a **proposal only**, not an automatic update of the original manifest or empirical approval.

```bash
arc-rgbt split --input datasets/manifests/split-synthetic.json --seed 17
# For an actual 3-way proposal, provide at least three independently declared flight/scene groups.
arc-rgbt split --input local-metadata.json --seed 17 --device-disjoint --output reports/split-proposal.json
```

Requested `--proportions TRAIN VAL TEST` are positive and must sum to 1; assignment quotas count **connected groups**, not frame or class proportions. Actual flight/device identities, near-duplicate imagery and cross-UAV scene overlap still demand independent manual or image-based provenance checks. The report is never equivalent to a licence or native-dataset admission.

Python evaluators in `arc_rgbt.evaluation_contracts` extend existing `bench.evaluate` without replacing its TP/FP/FN matching. `detection_contract(frames, annotation_status='complete', iou_threshold=0.5, operating_score=0.0)` computes per-class **all-points interpolated AP at the specified single IoU threshold**, mean across GT-present classes, recall and FP/frame at the declared score threshold. It is **not** COCO AP@[.50:.95]. With no GT, AP/recall are null; with no predictions, precision is null; complete-negative frames remain in the FP/frame denominator. Annotation completeness remains a declaration.

`tracking_reference_contract(frames)` verifies monotonically increasing frame indices, complete GT, nonduplicate identities per frame and valid per-sequence tracking boxes. It returns `hota: null` and `idf1: null`: **neither HOTA nor IDF1 is implemented**. Scientific tracking evaluation requires a separately pinned and independently validated TrackEval reference implementation with real sequence IDs, original annotations and accepted access terms.

These tools do not open external archives, measure physical clocks, or promote B01/G06. Full AP/HOTA claims still require source evidence and benchmark protocol review.

## Local image near-duplicate audit (R3.1, implemented)

`arc-rgbt near-duplicates` is separate from metadata-only `arc-rgbt admission` and the `.npy` `arc-rgbt sequence` audit. Use it **only on a local subset whose licence permits access and analysis**. It does not download source images or upload images, derived thumbnails, or model weights. The input admission inventory must already pass the strict metadata schema and split guard. A second small JSON mapping identifies local images without modifying source manifests.

Mapping format:

```json
{"schema_version": 1, "items": [
  {"sequence_id": "flightA", "modality": "rgb", "frame_id": "rgb-001", "path": "frame-001.jpg"},
  {"sequence_id": "flightB", "modality": "rgb", "frame_id": "rgb-002", "path": "frame-002.jpg"}
]}
```

```bash
arc-rgbt near-duplicates --input local-inventory.json --map local-frame-map.json --root /path/to/permitted/images --max-hamming 4 --output reports/near-duplicate-review.json
```

- `--input`: existing strict admission JSON with declared per-frame SHA-256, split, sequence ID and modality-specific frame ID. `--map`: exactly `schema_version` and 2–512 `items`. Each item has `sequence_id`, `modality` (`rgb` or `thermal`), `frame_id` and relative `.jpg`, `.jpeg` or `.png` `path`. `--root` identifies read-only source images. Local paths cannot escape the root, including symlinks; hardlinks and reused mapped image files are rejected.
- The tool recomputes the **actual SHA-256 of each local PNG/JPEG** and requires an exact match to the admission manifest. It then decodes a reduced grayscale image and computes the 64-bit horizontal **difference hash (dHash)**. Images are compared only when they are in different train/validation/test splits and share the **same declared spectral band**. The default Hamming-distance threshold is four bits; configurable from 0 to 64.
- A flagged pair means `REVIEW_REQUIRED`, **not** an independently established duplicate. dHash has false positives on flat/textureless scenes and false negatives after cropping, rotation, shifts and thermal remapping. An unflagged subset is `NO_CANDIDATES_IN_SUBSET`, **never** proof of split independence or absence of leakage. For M3OT, a reviewer must also inspect overlapping UAV flights and original capture provenance.
- Bounds: local mapping up to 1 MiB; images up to 16 MiB each; maximum 4 million pixels after reduced decoding; maximum 512 mapped images and 200 candidate pairs per run. Reports contain IDs, splits, modality, hash distances and limitations, not image pixels. Output uses exclusive file creation and cannot overwrite existing results.
- Results always report `empirical_admission: false`, `licence_verified: false`, and `tracking_metric_verified: false`, even when every input hash matches. Do not commit local image archives, restricted labels or review output.

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
