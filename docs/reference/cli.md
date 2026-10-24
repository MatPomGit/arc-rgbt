# Command-line reference

All entry points are defined by `[project.scripts]` in `pyproject.toml`. Run any tool with `--help` for the authoritative flag list. Execute commands from the repository root; generated results belong in the ignored `reports/` directory.

## Unified launcher (recommended)

After `pip install -e .`, `arc-rgbt --help` lists all available tools.

| Command | Purpose |
| --- | --- |
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
