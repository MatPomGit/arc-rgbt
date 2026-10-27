# Getting started

Requires Python 3.12+ and a local repository checkout. From the root:

```bash
python -m pip install -e '.[dev]'
arc-rgbt studio
```

Select **Try an example**. The local, browser-based viewer displays a
clearly labelled synthetic image pair; use the blend slider or
**Highlight intensity differences** and save a PNG/JSON if needed.
Use **Clear images** before loading new data. No server or account is
needed. Real files must already be aligned and the same size.
Studio visualization is not radiometry or measured detection.

On a headless system: `arc-rgbt studio --no-open`.
To inspect *native numeric* thermal data, use:

```bash
arc-rgbt thermal --input thermal_uint16.npy --output reports/thermal-preview
```

Raw arrays remain unchanged; `preview.png` is an 8-bit display view
and `metadata.json` documents the original values and SHA-256.
For comparisons across recordings use fixed `--range LOW HIGH`
rather than independent percentiles. See [CLI reference](reference/cli.md).

## Reproduce reference experiments

```bash
arc-rgbt demo --output reports/demo
arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00
arc-rgbt-e01 --dataset datasets/manifests/e01-synthetic-quality.json --output reports/E01
arc-rgbt-e02 --config experiments/E02/config.json --output reports/E02
```

The demo output directory must not exist before execution. Results are
placed under ignored `reports/`. None of these runs measures physical
camera detection or MCU efficiency.

Read the methods before interpreting results:
[E00](experiments/e00.md) · [E01](experiments/e01.md) ·
[E02](experiments/e02.md). For other tools and examples see the
[CLI reference](reference/cli.md),
[sensor guide](guides/sensors-degradation.md),
[fusion guide](guides/fusion-benchmark.md) and
[timing/registration guide](guides/synchronization-registration.md).

## Validate and extend

```bash
python -m pytest -q
python -m ruff check src tests tools
python -m tools.check_docs
```

Use local wheels for offline dependency installation. See
[reproducibility](reproducibility.md), [development](development.md) and
[evidence standards](concepts/evidence.md).
