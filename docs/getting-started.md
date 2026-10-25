# Getting started

## Prerequisites

- Python **3.12+** on Linux, Windows (PowerShell/WSL) or macOS.
- A local clone of `arc-rgbt`.
- The declared NumPy, SciPy, OpenCV-headless and PyYAML dependencies, supplied by an internal wheelhouse if the computer is offline.

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check src tests tools
```

The installation command may download free Python packages if they are not cached. For isolated offline execution, install from a locally prepared wheelhouse instead. No paid API or cloud runtime is needed.

## Start the interactive image studio

```bash
arc-rgbt studio
```

The local browser UI accepts two images (PNG, JPEG or WebP), lets you change
thermal weighting or inspect the absolute grayscale difference, and exports
a PNG and JSON metadata. No server, network, login or uploaded data is involved.
Inputs must already be aligned and have identical dimensions; resampling is
never performed implicitly. For servers without a GUI, use
`arc-rgbt studio --no-open` to print the packaged HTML file location and open
it later on a desktop that has the package installed.

Studio operates on 8-bit browser-decoded image intensities and is **not**
an interface for physical thermal radiometry, detector evaluation or rigorous
research data processing. Use the Python API or CLI for numerical arrays.

## Fastest start: no input files to prepare

```bash
arc-rgbt doctor
arc-rgbt demo --output reports/demo
```

Open `reports/demo/index.html` locally to inspect the RGB-like, thermal-like and
fused PNGs, a labelled report and the host CPU measurement. The full source
NumPy arrays and metadata are available in the same directory. No datasets,
cameras, accounts or API keys are required.

The demo refuses to overwrite an existing output directory. For another run,
choose `--output reports/demo-2`. Use `arc-rgbt --help` to discover commands
and `arc-rgbt fuse --help` (or another command) to see the original options.

This demonstration contains one synthetic rectangular target and a threshold
heuristic with an uncalibrated placeholder prediction score. Its metrics are
**not physical sensor, detection or MCU performance evidence**.

## Produce your first synthetic data

The following creates a normalized input image **without downloading any dataset**:

```bash
python - <<'PY'
from pathlib import Path
import numpy as np

Path("reports").mkdir(exist_ok=True)
image = np.zeros((240, 320), dtype=np.float32)
image[50:80, 80:95] = 0.9
np.save("reports/sample.npy", image, allow_pickle=False)
PY
```

On Windows PowerShell, run this block inside WSL or put its Python statements into a local `.py` file.

Now run the five principal reference tools:

```bash
sensorlab --camera configs/sensors/thermal_80x60.yaml \
  --range-m 20 --object-width-m 0.6 --object-height-m 1.7 \
  --output reports/sensorlab.json

degradesim --config configs/scenarios/degradation.yaml \
  --input reports/sample.npy --output reports/native.npy

fusionlab --config configs/scenarios/fusion.yaml \
  --rgb reports/native.npy --thermal reports/native.npy \
  --output reports/fused.npy

bench-rgbt --dataset datasets/manifests/example-labelled.json \
  --output reports/bench

edgelab --config configs/processors/reference_cpu.yaml \
  --input reports/native.npy --output reports/edge.json
```

!!! note "Interpretation"
    The fusion example uses the *same* synthetic image for both modalities to demonstrate the interface. It is not an evaluation of physical RGB–thermal fusion. EdgeLab measures host OpenCV operations, not embedded hardware.

## Run E00 and summarize it as P01 material

```bash
arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00
python publications/P01/analyses/summarize_e00.py \
  --experiment-dir reports/E00 --output reports/P01/e00_summary.json
```

Expected generated artifacts include `reports/E00/manifest.json`, `metrics.csv`, `report.html` and preview images. The P01 analysis generates a separate JSON summary after cross-checking the manifest and CSV.

## Explore E01 and E02 without datasets or cameras

```bash
arc-rgbt-e01 --dataset datasets/manifests/e01-synthetic-quality.json \
  --output reports/E01
arc-rgbt-e02 --config experiments/E02/config.json \
  --output reports/E02
```

E01 generates four method comparisons using **hand-authored** labelled
proposals. E02 calculates 84 simulated timing/geometry cases; its overlap
is not measured detector accuracy. Read [E01](experiments/e01.md) and
[E02](experiments/e02.md) before interpreting the generated results.

Continue with [E00](experiments/e00.md), [CLI options](reference/cli.md)
and [reproducibility rules](reproducibility.md).
