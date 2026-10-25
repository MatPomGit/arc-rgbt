# Five command-line tools

All commands work with an editable installation (`pip install -e .`) and local inputs.

1. **SensorLab**: `sensorlab --camera configs/sensors/thermal_80x60.yaml --range-m 20 --object-width-m 0.6 --object-height-m 1.7 --output reports/sensorlab.json`
2. **DegradeSim**: `degradesim --config configs/scenarios/degradation.yaml --input sample.npy --output reports/native.npy` (normalized, 2-D NumPy input)
3. **FusionLab**: `fusionlab --config configs/scenarios/fusion.yaml --rgb reports/native.npy --thermal reports/native.npy --output reports/fused.npy` (same-size, grayscale arrays)
4. **Bench**: `bench-rgbt --dataset datasets/manifests/example-labelled.json --output reports/bench` (explicit labelled JSON)
5. **EdgeLab**: `edgelab --config configs/processors/reference_cpu.yaml --input reports/native.npy --output reports/edgelab.json` (reference host CPU only)

`arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00` runs the standalone synthetic experiment. Run `--help` on each CLI for all options. Configurations and generated reports are intentionally separate. None of these tools downloads models or datasets.


## P02 support CLIs (outside the five principal tools)

- `arc-rgbt-sync --input configs/scenarios/synchronization-example.json`
  computes per-frame time offset and unmatched-frame statistics from an
  explicitly common monotonic nanosecond clock.
- `arc-rgbt-register --rgb rgb.npy --thermal thermal.npy
  --homography configs/scenarios/homography-simulated-example.json
  --calibration-origin simulated --reference thermal` aligns different
  native image shapes using an **externally supplied** planar transform.
  Inputs must be compatible with the calibration; the example matrix is
  strictly synthetic.

## Sequence audit (experimental)

```bash
arc-rgbt sequence --demo --output reports/seq-demo
arc-rgbt sequence --input recordings/manifest.json --output reports/seq-run
```

Timestamped NumPy datasets are checked offline for input safety, shape/dtype
consistency, source hashes and paired-frame temporal skew. Output is JSON,
CSV and HTML. No sensor connection, calibration, upsampling or inference.

## New UX commands (unreleased)

```bash
arc-rgbt --help
arc-rgbt doctor
arc-rgbt demo --output reports/demo
arc-rgbt studio
arc-rgbt thermal --input thermal_uint16.npy --output reports/thermal-preview
```

`thermal` accepts original 2D finite NumPy frames and writes a separate
8-bit display PNG plus audit metadata. It does **not** overwrite the input
nor infer physical temperature. Use `--range LOW HIGH` for consistent
display scaling between frames; percentile scaling is frame-dependent.
Studio can inspect native `.npy` arrays but exports visualization images,
not calibrated radiometry.
