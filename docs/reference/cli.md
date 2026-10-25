# Command-line reference

All entry points are defined by `[project.scripts]` in `pyproject.toml`. Run any tool with `--help` for the authoritative flag list. Execute commands from the repository root; generated results belong in the ignored `reports/` directory.

## RGB/LWIR sequence quality audit

`arc-rgbt sequence --demo --output reports/sequence-demo` creates a
self-contained, labelled-as-synthetic timestamp/data-integrity example.
`arc-rgbt sequence --input PATH/manifest.json --output NEW_DIRECTORY` checks
preexisting local frames. The manifest schema and output format are described
in [synchronization guide](../guides/synchronization-registration.md).
Use `arc-rgbt-sequence` for the dedicated executable. All outputs are offline
and the destination must not already exist.

## Raw NumPy thermal preview (new)

`arc-rgbt thermal` (or `arc-rgbt-thermal`) takes a 2D numeric `.npy`:

```bash
arc-rgbt thermal --input thermal_u16.npy --output reports/thermal-001
arc-rgbt thermal --input thermal_u16.npy --range 1000 16000 \
  --output reports/thermal-fixed-001
arc-rgbt thermal --input thermal_u16.npy --percentiles 2 98 \
  --output reports/thermal-relative-001
```

The `--range` and `--percentiles` controls are mutually exclusive.
Accepted types: 8/16/32-bit signed/unsigned integers and real float arrays;
2D, finite, ≤4 million samples and ≤64 MiB on disk. Raw units are not
interpreted as temperatures without a separately documented calibration.
Output is a new directory containing `preview.png` (8-bit visualization)
and `metadata.json` (original dtype, shape, min/max, SHA-256, clipping,
display bounds and explicit limitations). The input file is not changed.

Studio also parses a safe subset of v1/v2/v3 uncompressed NumPy headers in
the browser (2D C-order and supported real numeric dtypes). It validates
header, file length, shape, endianness, finite values and the 16 MiB limit.
The browser preserves raw samples separately from its normalized preview.

## Interactive local studio

`arc-rgbt studio` opens a packaged, standalone browser UI via a `file://`
URL. Use `arc-rgbt studio --no-open` to print the absolute HTML path without
launching a browser. It has no HTTP server and requires no added dependencies.
Click **Try an example** to load built-in, clearly labelled synthetic images
without preparing any files. Use **Clear images** to start over. Alternatively,
select pre-aligned same-size PNG/JPEG/WebP or supported 2D NumPy files, move
the thermal slider, inspect differences, and save PNG/JSON. Exported metadata
identifies a synthetic or user-supplied source. Choosing your own image
removes any remaining built-in example to avoid mixing both origins. The UI does not
perform spatial registration or radiometric calibration; outputs are
exploratory rather than validated detector/MCU measurements.

## Studio acceptance test (optional)

The ordinary offline test suite does not require a browser. For an extra
end-to-end check with locally installed Chromium and Playwright:

```bash
ARC_RGBT_BROWSER_TEST=1 ARC_RGBT_CHROMIUM_EXECUTABLE=/usr/bin/chromium \
  python -m pytest -q tests/test_studio_browser.py
```

Leave `ARC_RGBT_CHROMIUM_EXECUTABLE` unset when Playwright already has its
own local Chromium installation. This optional test exercises file selection,
mismatched grids, pixel values after blending, the intensity difference view,
both download buttons and rejection of invalid MIME types. It does not download
a browser automatically.

On Windows PowerShell, opt in explicitly before the browser test:
`$env:ARC_RGBT_BROWSER_TEST = "1"`. The CMD syntax `set VARIABLE=1`
does not update PowerShell's environment, so the browser tests will skip.
See [Playwright offline validation](../guides/playwright-offline.md).

For extensionless output paths, `arc-rgbt register` also normalizes
`--output registered` into `registered.npz` with
`registered.npz.json` metadata. Other explicit suffixes are rejected.

## Unified launcher (recommended)

The installed unified entry point is `arc-rgbt`.
After `pip install -e .`, `arc-rgbt --help` lists all available tools.

| Command | Purpose |
| --- | --- |
| `arc-rgbt thermal [--input] ...` | Raw numeric thermal preview with source SHA-256 and explicit display limits |
| `arc-rgbt sequence --demo` or `--input FILE` | Validate RGB/LWIR frames and inspect timestamp pairing in HTML/CSV/JSON |
| `arc-rgbt studio [--no-open]` | Open local browser-based RGB–thermal viewer with no server |
| `arc-rgbt doctor [--json]` | Validate Python >=3.12 and required local dependencies |
| `arc-rgbt demo [--output NEW_DIR] [--seed N]` | Generate a synthetic run, image previews and a local HTML viewer |
| `arc-rgbt sensor ...` | Forwards to `sensorlab` |
| `arc-rgbt degrade ...` | Forwards to `degradesim` |
| `arc-rgbt fuse ...` | Forwards to `fusionlab` |
| `arc-rgbt bench ...` | Forwards to `bench-rgbt` |
| `arc-rgbt edge ...` | Forwards to `edgelab` |
| `arc-rgbt e00/e01/e02 ...` | Forwards to the corresponding experiment |
| `arc-rgbt sync ...` | Forwards to `arc-rgbt-sync` |
| `arc-rgbt register ...` | Forwards to `arc-rgbt-register` |

Legacy entry points remain compatible. Use `arc-rgbt fuse --help` or the
original executable's `--help` for detailed arguments. Failed local file
reads are reported as short command-specific errors by the launcher.

The demo directory must **not already exist**. The CLI writes to a temporary
directory and publishes it only after all files have been generated. Preview
PNGs, a local `index.html`, NumPy arrays, benchmark CSV/JSON/HTML, a
geometry report and a host CPU profile are included.

For `fusionlab` and `degradesim`, an extensionless `--output` is
normalized to `.npy`; metadata is written as `<actual-file>.json`.
Other explicit extensions are rejected instead of silently appending `.npy`.

| Command | Required inputs | Default output |
| --- | --- | --- |
| `sensorlab` | `--camera`, `--range-m`, `--object-width-m`, `--object-height-m` | `reports/sensorlab.json` |
| `degradesim` | `--config`, `--input` | `reports/degradesim.npy` |
| `fusionlab` | `--rgb`, `--thermal` | `reports/fusionlab.npy` |
| `bench-rgbt` | `--dataset` | `reports/bench/` |
| `edgelab` | `--input` | `reports/edgelab.json` |
| `arc-rgbt-e00` | none; optionally `--config` | `reports/E00/` |
| `arc-rgbt-sync` | `--input` | `reports/synchronization.json` |
| `arc-rgbt-register` | `--rgb`, `--thermal`, `--homography`, `--calibration-origin` | `reports/registered_pair.npz` |
| `arc-rgbt-e01` | `--dataset` | `reports/E01/` |
| `arc-rgbt-e02` | `--config` | `reports/E02/` |

## Optional flags and behaviours

| Tool | Flag | Behaviour |
| --- | --- | --- |
| `fusionlab` | `--config`, `--method weighted/gradient`, `--register` | YAML method/weight and optional phase-correlation translation |
| `edgelab` | `--config`, `--repeats`, `--model` | Host CPU repetitions and optional local model **file-size** measurement |
| `arc-rgbt-sync` | `--output` | Write pairing JSON after schema validation |
| `arc-rgbt-register` | `--reference rgb/thermal` | Choose interpolation target grid |
| `arc-rgbt-register` | `--calibration-origin measured/estimated/simulated` | Mandatory declaration; not independently verified |
| `arc-rgbt-e00` | `--config`, `--output` | Seeded deterministic sweep of native resolutions |
| `arc-rgbt-e01` | `--dataset`, `--output` | Four-method evaluation on labelled scored proposals |
| `arc-rgbt-e02` | `--config`, `--output` | Timing and native-grid analytical overlap sweep |

All `.npy` inputs use `numpy.load(..., allow_pickle=False)` in the CLI. User-controlled input files should still be treated as untrusted data; prefer isolated computation for third-party material.

## Python API entry points

```python
from arc_rgbt.sensorlab import Camera, geometry
from arc_rgbt.degradesim import degrade
from arc_rgbt.fusionlab import fuse_images, fuse_detections, register_translation
from arc_rgbt.bench import evaluate, report
from arc_rgbt.edgelab import profile_cpu
from arc_rgbt.synchronization import pair_frames
from arc_rgbt.registration import align_pair
from arc_rgbt.e00 import run
from arc_rgbt.e01 import run as run_e01
from arc_rgbt.e02 import run as run_e02
from arc_rgbt.quality_fusion import quality_fuse_detections
```

Use [data contracts](data-contracts.md) for schemas, [guides](../getting-started.md) for runnable examples and module docstrings for function parameters.
