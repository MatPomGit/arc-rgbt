# Command-line reference

All entry points are defined by `[project.scripts]` in `pyproject.toml`. Run any tool with `--help` for the authoritative flag list. Execute commands from the repository root; generated results belong in the ignored `reports/` directory.

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

## Optional flags and behaviours

| Tool | Flag | Behaviour |
| --- | --- | --- |
| `fusionlab` | `--config`, `--method weighted/gradient`, `--register` | YAML method/weight and optional phase-correlation translation |
| `edgelab` | `--config`, `--repeats`, `--model` | Host CPU repetitions and optional local model **file-size** measurement |
| `arc-rgbt-sync` | `--output` | Write pairing JSON after schema validation |
| `arc-rgbt-register` | `--reference rgb/thermal` | Choose interpolation target grid |
| `arc-rgbt-register` | `--calibration-origin measured/estimated/simulated` | Mandatory declaration; not independently verified |
| `arc-rgbt-e00` | `--config`, `--output` | Seeded deterministic sweep of native resolutions |

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
```

Use [data contracts](data-contracts.md) for schemas, [guides](../getting-started.md) for runnable examples and module docstrings for function parameters.
