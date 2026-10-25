# Frame synchronization and geometric registration

This P02 groundwork includes two independent tools. Neither calibrates physical cameras by itself.

## Timestamp pairing

`pair_frames` requires strictly increasing, unique frame identifiers and integer nanosecond timestamps for both streams, recorded in an already comparable `shared_monotonic_ns` clock domain.

```bash
arc-rgbt-sync --input configs/scenarios/synchronization-example.json \
  --output reports/synchronization.json
```

For each thermal frame, it greedily selects the nearest **unused** RGB timestamp within the specified tolerance, preferring the earlier RGB timestamp on an exact tie. Outputs include paired IDs, signed offsets in milliseconds, matched fraction, unmatched counts, median absolute skew and p95 skew.

!!! warning "No clock calibration"
    Declaring `shared_monotonic_ns` does not establish it. A real acquisition must verify exposure timestamps and transform clock domains externally. Pairing is greedy and is not a global optimal assignment.

## Offline sequence integrity and timing audit

Use `arc-rgbt sequence` for a reproducible **batch** audit of previously
captured local `.npy` files. It neither opens live devices nor calibrates clocks.

For a complete synthetic example, with three frames from each modality:

```bash
arc-rgbt sequence --demo --output reports/sequence-example
```

Open `reports/sequence-example/index.html`. The report includes one deliberately
unmatched thermal frame, two matched frames, and unequal native RGB/LWIR grids.

For existing recordings, create a `manifest.json` next to a `frames/` directory:

```json
{
  "schema_version": 1,
  "data_origin": "measured",
  "clock_domain": "shared_monotonic_ns",
  "tolerance_ms": 10,
  "rgb_frames": [
    {"id": "rgb-001", "timestamp_ns": 100000000, "path": "frames/rgb-001.npy"}
  ],
  "thermal_frames": [
    {"id": "lw-001", "timestamp_ns": 104000000, "path": "frames/lw-001.npy"}
  ]
}
```

The `data_origin` field is a *declaration*, not independently verified evidence.
All paths are relative to the manifest and restricted to that directory tree;
external symlinks and path traversal are rejected. Arrays must be finite,
numeric, uncompressed and use compatible 2D or RGB 3D structures. Inputs are
limited to 512 frames total, 4 million native pixels per frame and 64 MiB per
file. Missing/corrupted frames fail the audit instead of silently vanishing.

```bash
arc-rgbt sequence --input captures/manifest.json --output reports/capture-001
```

Outputs: `report.json` (frame SHA-256, native dtype/grid/raw extrema and
paired IDs), `pairs.csv` and `index.html`. The report exposes matched and
unmatched counts, matched thermal fraction, median and p95 absolute skew,
unequal native grids, shape changes and dtype changes within each modality.
CSV cells are protected against spreadsheet formula injection.

These are **data-integrity and timing diagnostics only**. They are not a
precision-recall score, geometric calibration, global-optimal assignment or
clock-drift correction. Native resolution differences are reported rather
than resampled. Choose synchronization tolerances in the study protocol,
not after viewing experimental outcomes.

## Planar registration

`align_pair` takes a supplied 3×3 homography mapping **RGB pixel coordinates to thermal pixel coordinates**. The reference grid defaults to native thermal resolution; `--reference rgb` instead interpolates thermal onto the RGB grid.

Generate a minimal synthetic pair compatible with the supplied **simulated** 0.5-scale example matrix:

```bash
python - <<'PY'
from pathlib import Path
import numpy as np

Path("reports").mkdir(exist_ok=True)
rgb = np.zeros((240, 320), np.float32)
thermal = np.zeros((120, 160), np.float32)
rgb[80:130, 90:140] = 0.8
thermal[40:65, 45:70] = 0.8
np.save("reports/rgb-demo.npy", rgb, allow_pickle=False)
np.save("reports/thermal-demo.npy", thermal, allow_pickle=False)
PY

arc-rgbt-register --rgb reports/rgb-demo.npy \
  --thermal reports/thermal-demo.npy \
  --homography configs/scenarios/homography-simulated-example.json \
  --calibration-origin simulated --reference thermal \
  --output reports/registered_pair.npz
```

The output archive contains `rgb`, `thermal` and `valid` arrays, with metadata saved as `registered_pair.npz.json`. The support mask excludes pixels whose **bilinear interpolation footprint** would include out-of-image padding. Analyse only the valid overlap.

The matrix is an artificial transformation, **not** a measured calibration. One projective transform is valid only for a planar scene or negligible parallax; upsampling does not recover missing thermal information.

See [timing/registration fields](../reference/data-contracts.md), [methodology](../concepts/evidence.md) and the source [P02 acquisition protocol](https://github.com/MatPomGit/arc-rgbt/blob/main/research/protocols/P02-pairing-registration.md).
