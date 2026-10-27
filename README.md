# arc-rgbt

**RGB–thermal/IR research toolkit** · Python 3.12+ · Apache-2.0

Reusable offline software for native sensor geometry, degradation,
RGB/LWIR image and detection fusion, frame pairing, labelled evaluation
and host-side profiling. No models, datasets or API keys are downloaded.

## Start

```bash
python -m pip install -e '.[dev]'
arc-rgbt studio
```

In Studio, choose **Try an example** for a fully synthetic RGB–thermal
preview. For CLI discovery run `arc-rgbt --help`. The interface and
examples are not calibrated radiometry or physical detector validation.

## Documentation

| Need | Canonical resource |
| --- | --- |
| Installation and first experiment | [Getting started](docs/getting-started.md) |
| Command syntax and Python API | [CLI reference](docs/reference/cli.md) |
| Architecture and data formats | [Architecture](docs/concepts/architecture.md) · [data contracts](docs/reference/data-contracts.md) |
| E00 resolution, E01 fusion, E02 timing | [E00](docs/experiments/e00.md) · [E01](docs/experiments/e01.md) · [E02](docs/experiments/e02.md) |
| Research methods and candidate literature | [Evidence requirements](docs/guides/evaluation-requirements.md) · [literature](docs/experiments/literature-screening.md) |
| Research portfolio and current gates | [Research plan](AUTOPILOT_PLAN.md) · [state](PROJECT_STATE.yaml) · [Issue #10](https://github.com/MatPomGit/arc-rgbt/issues/10) |
| Development and validation | [Contributing](CONTRIBUTING.md) · [reproducibility](docs/reproducibility.md) |

```bash
python -m tools.check_docs
python -m pytest -q
python -m ruff check src tests tools
```

All generated artifacts belong under the ignored `reports/` directory.
**Synthetic E00/E01/E02 and host profiling are not evidence of sensor,
human/vehicle detection or microcontroller performance.**
