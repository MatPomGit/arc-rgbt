# Sensor geometry and image degradation

## SensorLab: frontal-plane geometry

`sensorlab` estimates pinhole field of view and ground sampling distance (GSD). The camera profile needs `width_px`, `height_px`, `pixel_pitch_um` and `focal_length_mm`.

```bash
sensorlab --camera configs/sensors/thermal_80x60.yaml \
  --range-m 10 --object-width-m 0.5 --object-height-m 1.7 \
  --output reports/sensor-10m.json
```

For range `D` (metres), pixel pitch `p` (metres) and focal length `f` (metres), the approximation is **GSD = D × p / f**. Object width in native pixels is object width divided by GSD. This assumes square pixels, a pinhole model and a frontal planar target; occlusions and real lens distortion are outside scope.

## DegradeSim: controlled transformations

`degradesim` takes a NumPy `.npy` image with finite intensities **already normalized to [0, 1]**. It applies Gaussian optical blur, horizontal uniform motion blur, native-resolution resizing and optional seeded additive noise.

```bash
degradesim --config configs/scenarios/degradation.yaml \
  --input reports/sample.npy --output reports/native.npy
```

The configuration uses:

| Key | Unit | Meaning |
| --- | --- | --- |
| `width_px` / `height_px` | pixels | Simulated native output grid |
| `optical_sigma_px` | source pixels | Gaussian standard deviation |
| `motion_length_px` | source pixels | Horizontal one-dimensional blur length |
| `noise_sigma` | normalized intensity | Additive Gaussian noise standard deviation |
| `seed` | integer | Reproducible RNG seed |

Output is the native `.npy` plus JSON metadata at `reports/native.npy.json`. Input beyond the unit interval is **rejected**, not silently scaled. Noise may be clipped to [0, 1]. None of these operations replaces measured optics, sampling response or thermal radiometry.

Next: [image and detection fusion](fusion-benchmark.md) or [data formats](../reference/data-contracts.md).
