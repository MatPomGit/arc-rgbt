# Command-line reference

Run `arc-rgbt --help` to discover the unified launcher. Tool-specific
`--help` is authoritative for flags; installed commands are declared in
[`pyproject.toml`](https://github.com/MatPomGit/arc-rgbt/blob/main/pyproject.toml).
All experiments run locally and place outputs in ignored `reports/`.

## Unified launcher

| Command | Purpose |
| --- | --- |
| `arc-rgbt studio` | Open offline same-grid RGB/thermal viewer |
| `arc-rgbt thermal --input FILE --output DIR` | Native 2D numeric preview; preserve input and record source units |
| `arc-rgbt sequence --demo --output DIR` | Synthetic pair-timing/integrity report |
| `arc-rgbt sequence --input FILE --output DIR` | Audit existing local sequence manifests |
| `arc-rgbt doctor` | Inspect local runtime |
| `arc-rgbt demo --output DIR` | Synthetic images and offline HTML example |
| `arc-rgbt sensor/degrade/fuse/bench/edge` | Delegate to named reference tools |
| `arc-rgbt e00/e01/e02` | Run the corresponding synthetic/analytical experiment |
| `arc-rgbt sync/register` | Timestamp pairing or supplied-homography registration |

## Individual installed entry points

| Executable | Primary inputs / reference |
| --- | --- |
| `sensorlab` | `--camera`, `--range-m`, `--object-width-m`, `--object-height-m` |
| `degradesim` | `--config`, `--input` (normalized local `.npy`) |
| `fusionlab` | `--rgb`, `--thermal`, optional fusion configuration |
| `bench-rgbt` | `--dataset` (annotated boxes) |
| `edgelab` | `--input`, optional host CPU configuration |
| `arc-rgbt-e00` | `--config experiments/E00/config.yaml` |
| `arc-rgbt-e01` | `--dataset datasets/manifests/e01-synthetic-quality.json` |
| `arc-rgbt-e02` | `--config experiments/E02/config.json` |
| `arc-rgbt-sync` | `--input` common-clock timestamp JSON |
| `arc-rgbt-register` | `--rgb`, `--thermal`, `--homography`, `--calibration-origin` |
| `arc-rgbt-thermal` | `--input` 2D numeric thermal file, `--output` fresh directory |
| `arc-rgbt-sequence` | `--demo` or `--input` manifest, `--output` fresh directory |

**Python/API launcher:** `arc-rgbt`, listed above; direct module
entry points are in `src/arc_rgbt/`. Supported inputs, outputs and
calibration-origin semantics are in [data contracts](data-contracts.md).
CLI input files are untrusted; NumPy loading disables pickling.

## Specific guides

- [Getting started](../getting-started.md): Studio, thermal preview and first experiments.
- [Sensor degradation](../guides/sensors-degradation.md) and [image/box fusion](../guides/fusion-benchmark.md).
- [Quality-weighted fusion](../guides/quality-fusion.md) and [synchronization/registration](../guides/synchronization-registration.md).
- [E00](../experiments/e00.md), [E01](../experiments/e01.md), [E02](../experiments/e02.md).
- [Offline browser acceptance](../guides/playwright-offline.md) for optional Chromium/Playwright tests.

### Thermal preview and browser constraints

`arc-rgbt thermal` preserves the input `.npy` and generates an 8-bit
display PNG plus original-dtype/intensity/hash metadata. Explicit
`--range LOW HIGH` supports frame-to-frame display comparisons;
per-frame percentiles do not establish absolute thermal intensity.
Studio uses `file://` and does **not** register misaligned images.
Fusion and registration remain separate scientific operations.

For scientific claims, use [evidence rules](../concepts/evidence.md).
