# Changelog

This file records changes integrated in the source tree, **not Git tags**.
The package version declared by `pyproject.toml` is authoritative.

## 2026-10-27 — research documentation

- Screened RGB/LWIR literature with DOI provenance and method-specific
  claims; added native-pixel measurement standards and P01–P03 protocol gates.
- Consolidated overlapping guides and linked stable source-of-truth files.

## 2026-10 — reference software and documentation

- E00 resolution sweep, P01 summary; E01 four-arm quality heuristic;
  E02 simulated time-skew geometry, with explicit provenance.
- Pairing and planar registration with native grids and valid-support mask;
  offline sequence integrity audit.
- Browser Studio, native numeric thermal preview, unified `arc-rgbt`
  launcher, bounded synthetic demo and optional local browser tests.
- MkDocs guide, CLI/data contracts and strict offline documentation checks.

## Initial 0.1.0 baseline

- Installable Python package, SensorLab, DegradeSim, FusionLab, Bench,
  EdgeLab and deterministic synthetic fixtures.
- Unit/CLI tests, publication workspaces and host-only profiling.

These features are **not** empirical sensor, calibrated detector or
physical MCU validation. See [state](PROJECT_STATE.yaml) and
[study evidence rules](docs/concepts/evidence.md).
