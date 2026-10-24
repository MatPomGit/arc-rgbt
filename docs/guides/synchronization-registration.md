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
