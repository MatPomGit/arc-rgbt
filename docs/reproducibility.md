# Reproducibility and quality assurance

Reproducible research requires more than passing tests. Record software identity, input provenance, detector protocol, experimental unit and any physical measurement uncertainty.

## Local executable verification

From the repository root:

```bash
python -m pytest -q
python -m ruff check src tests tools
python -m tools.check_docs
arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00
arc-rgbt-e01 --dataset datasets/manifests/e01-synthetic-quality.json --output reports/E01
arc-rgbt-e02 --config experiments/E02/config.json --output reports/E02
python publications/P01/analyses/summarize_e00.py \
  --experiment-dir reports/E00 --output reports/P01/e00_summary.json
```

The MkDocs site requires the separate `docs` extra:

```bash
python -m pip install -e '.[docs]'
python -m mkdocs build --strict
python -m mkdocs serve
```

`mkdocs build --strict` checks site assembly, navigation and resolvable Markdown links. `tools.check_docs` offers a fast offline structural check with standard Python + the project's declared PyYAML dependency. When installing offline, supply the documentation dependencies from a local wheelhouse; the validation itself uses no external API.

## Minimum evidence record

| Field | Record |
| --- | --- |
| Code | Full commit SHA, package version and dirty/clean working-tree state |
| Runtime | Python, NumPy, SciPy, OpenCV, OS and relevant build parameters |
| Input | Original hashes, licences, annotation completeness, source identity and permitted use |
| Geometry | Sensor-native array shape, pixel conventions and calibration provenance |
| Time | Clock domain, exposure reference instant, tolerance, mismatch and pairing method |
| Randomization | Fixed seeds and data partitioning policy |
| Outcomes | Numerators/denominators, uncertainty, experimental unit and baseline limitations |

`provenance()` records the package version, available Git SHA and SHA-256 for explicitly passed file inputs. When run from an installed distribution outside a checkout, Git SHA can be null. It does not automatically snapshot the complete dependency lock or every dataset file.

## Interpretation rules

- Simulated E00 output is a *software verification artifact*, not field performance.
- E01 uses hand-authored scored proposals and uncalibrated quality multipliers; F1 is not a real-world performance claim.
- E02 calculates continuous idealized rectangle overlap, not measured detector IoU or any actual resolution-dependent detection limit.
- Report zero-denominator metric conventions and missing labels explicitly.
- Use all-negative ground truth only when completeness is verified and declared.
- Keep only pixels under the valid interpolation support mask after projective registration.
- Do not infer MCU power consumption from host Python allocations or OpenCV timing.
- Do not commit generated reports, model weights, secrets or unreleased datasets.

See [evidence policy](concepts/evidence.md) and [development workflow](development.md).
