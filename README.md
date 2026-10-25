# arc-rgbt

**Low-Cost RGB–Thermal Fusion Research Platform** | v0.1.0

An open, device-independent Python research toolkit for low- and medium-resolution RGB, NIR and LWIR imaging, native-resolution effects, early/late fusion, labelled detection evaluation, and host profiling. No cloud service, API key, model download or dataset download is required. Apache-2.0 license.

## What works in v0.1.0

| Component | Status | Scope |
|---|---|---|
| SensorLab | Reference implementation | Pinhole FOV, frontal-plane GSD, native object footprint and clipped frame fraction |
| DegradeSim | Reference simulation | Source-domain Gaussian/motion blur, native downsampling, seeded additive noise |
| FusionLab | Reference/experimental | Translation registration, intensity-weighted and gradient-guided image fusion; separate late box fusion |
| Bench | Reference implementation | Labelled box-level greedy IoU matching; precision, recall and F1; CSV/JSON/HTML |
| EdgeLab | Host reference only | CPU GaussianBlur latency, Python allocation peak and optional local model file size |
| E00 | Synthetic experiment | Seven native sensor resolutions, deterministic annotated scenes, class-agnostic localization, manifest and reports |
| E01 (experimental) | Simulated proposal evaluation | Four controlled detection-fusion strategies with externally specified modality quality; deterministic labelled results |
| Synchronization | Reference method | Nearest-frame RGB/LWIR timestamp pairing in a shared clock domain, with missing-frame and skew statistics |
| Calibrated registration | Reference method | Align unequal-resolution RGB/thermal arrays using externally supplied planar homographies and valid-support masks |
| MCU drivers, radiometry, physical calibration, temporal fusion, energy metering | **Planned** | Not implemented or validated |

This baseline does **not** recognize people or vehicles. Its E00 synthetic annotations and algorithm-derived metrics do **not** constitute camera measurements, hardware benchmarks or generalization evidence.

## Installation

Requires Python >=3.12. Install from locally provisioned dependencies (use a wheelhouse if offline):

```bash
python -m pip install -e '.[dev]'
pytest -q
ruff check src tests tools
```

## Searchable research documentation (MkDocs)

The full research guide is in [docs/](docs/index.md), with
[getting started](docs/getting-started.md), [CLI reference](docs/reference/cli.md),
[E00](docs/experiments/e00.md), [E01](docs/experiments/e01.md),
[E02](docs/experiments/e02.md) and
[evidence limits](docs/concepts/evidence.md).

```bash
python -m pip install -e '.[dev,docs]'
python -m tools.check_docs
python -m mkdocs build --strict --clean
python -m mkdocs serve
```

The documentation site is built **locally** and not automatically
deployed to GitHub Pages. Installation uses free Python dependencies;
for an air-gapped machine use an approved, local wheelhouse.

## Scientific raw thermal frames: 16-bit and NumPy (new)

A native thermal frame should remain numeric throughout the research pipeline.
Use this new standalone converter **only for visual inspection**:

```bash
arc-rgbt thermal --input local_thermal_uint16.npy --output reports/thermal-preview-001
# Explicit, shared display bounds for comparisons across frames:
arc-rgbt thermal --input local_thermal_uint16.npy \
  --range 1000 16000 --output reports/thermal-preview-002
```

The command accepts finite 2D NumPy arrays with up to four million samples;
8/16/32-bit signed or unsigned integers and real floating-point arrays
(up to float64). It writes `preview.png` plus `metadata.json` containing
the original dtype, dimensions, raw min/max, display limits, clip counts and
the input SHA-256. The original `.npy` is not modified and no raw thermal
values are replaced. The default 2–98 percentile stretch is image-relative.
Use explicit `--range LOW HIGH` for comparable display scales across frames.
Existing output directories are not overwritten. No camera or network required.

The Studio image pickers additionally accept little- or big-endian 2D
`.npy` of dtype `uint8`, `uint16`, `int16`, `uint32`, `int32`,
`float32` or `float64`, at up to 16 MiB per file. The browser retains
numeric values while rendering a separate min–max-normalized 8-bit preview.
The exported metadata records raw dtype, min/max and normalization, but the
exported PNG is always a display image rather than radiometric output.

Neither mode calibrates temperatures, corrects nonlinear response,
aligns geometries, recovers lost native resolution or validates
people/vehicle detection.

## Interactive RGB–Thermal Studio (fully offline)

```bash
arc-rgbt studio
# On a headless machine, print the local HTML file path:
arc-rgbt studio --no-open
```

To try it without a camera or external dataset, first run
`arc-rgbt demo --output reports/demo`, then select
`reports/demo/rgb_native.png` and `reports/demo/thermal_native.png`
inside Studio.

Studio opens a **local, self-contained HTML file**. Select two pre-aligned,
same-size PNG/JPEG/WebP images using file pickers. A thermal contribution slider
controls weighted grayscale intensity fusion; the difference view shows absolute
intensity differences. Export the current 8-bit grayscale visualization to PNG
and its configuration to JSON. Files never leave the browser tab: there is no
server, upload API, JavaScript CDN or cloud dependency. Each file is limited to
16 MiB, each image to 4 million pixels. Unequal grids are explicitly rejected
without automatic resizing.

**Scope:** browser-decoded sRGB grayscale intensities are not calibrated
radiometry, temperature measurements or geometric calibration. This is an
exploratory visualization, not an RGB–LWIR detector or scientific benchmark.
For numerical pipelines on `.npy` data, continue using `fusionlab` and the
existing reference algorithms.

## Unified entry point and synthetic preview

After installation, run the local diagnostic and a complete, self-contained example:

```bash
arc-rgbt --help
arc-rgbt doctor
arc-rgbt demo --output reports/demo
```

Open `reports/demo/index.html` in a browser for side-by-side native-resolution RGB-like, thermal-like and fused previews, the labelled evaluation report and CPU timing. The demo generates all arrays locally and never contacts a service. The target directory must not already exist, preventing accidental overwrites; select a new `--output` for another run.

The `arc-rgbt` command also forwards the original tool options: `sensor`, `degrade`, `fuse`, `bench`, `edge`, `e00`, `e01`, `e02`, `sync` and `register`. For example: `arc-rgbt fuse --help`.

**Scientific limitation:** the demo contains one synthetic rectangle and a fixed-threshold localization heuristic. Its placeholder prediction score is not a calibrated probability. The resulting benchmark metrics do not establish detector, camera or embedded-hardware performance. Host CPU timings are environment-dependent.

## Quick start (no external data)

```bash
sensorlab --camera configs/sensors/thermal_80x60.yaml --range-m 20 --object-width-m 0.6 --object-height-m 1.7
python -c 'import numpy as np; a=np.zeros((240,320),np.float32); a[50:80,80:95]=.9; np.save("sample.npy",a)'
degradesim --config configs/scenarios/degradation.yaml --input sample.npy --output reports/native.npy
fusionlab --config configs/scenarios/fusion.yaml --rgb reports/native.npy --thermal reports/native.npy --output reports/fused.npy
bench-rgbt --dataset datasets/manifests/example-labelled.json --output reports/bench
edgelab --config configs/processors/reference_cpu.yaml --input reports/native.npy --output reports/edge.json
arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00
```

`sample.npy` is intentionally ignored by Git. `reports/` contains generated outputs, never precomputed evidence. Every CLI supports `--help`. Running modules directly via `PYTHONPATH=src python -m arc_rgbt.<module>` is also supported.

See [ARCHITECTURE.md](ARCHITECTURE.md), [RESEARCH.md](RESEARCH.md), [REPRODUCIBILITY.md](REPRODUCIBILITY.md) and [ROADMAP.md](ROADMAP.md). The research programme has dedicated publication workspaces in `publications/P01` through `P03`.


## Experimental P02 foundations: asynchronous acquisition and unequal image grids

The five principal research tools now have two additional supporting CLI modules.
They are **not** full cross-modal calibration, physical clock synchronization,
motion compensation, tracking, or person/vehicle recognition systems.

```bash
arc-rgbt-sync --input configs/scenarios/synchronization-example.json \
  --output reports/synchronization.json
# The next command requires local .npy images whose dimensions match the
# independently established RGB -> thermal pixel transform.
arc-rgbt-register --rgb local_rgb.npy --thermal local_thermal.npy \
  --homography configs/scenarios/homography-simulated-example.json \
  --calibration-origin simulated --reference thermal \
  --output reports/registered_pair.npz
```

The homography example is **synthetic** and must not be used as real camera
calibration. A smaller thermal grid is not equivalent to an interpolated larger
image. Consult [P02 acquisition protocol](research/protocols/P02-pairing-registration.md).

## Experimental E01: quality-weighted late fusion

The E01 baseline compares RGB-only, thermal-only, equal-quality fixed fusion
and externally quality-weighted late fusion on **identical labelled proposals**.

```bash
arc-rgbt-e01 --dataset datasets/manifests/e01-synthetic-quality.json \
  --output reports/E01
```

E01 does **not** infer per-frame quality, estimate object probabilities,
train a detector or validate physical RGB/LWIR sensing. The small example is
purposefully constructed synthetic data demonstrating method differences,
**not a performance benchmark**. See [E01 protocol](experiments/E01/README.md).
