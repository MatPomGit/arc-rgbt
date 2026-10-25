# Changelog

## 0.1.0 (initial research baseline)

- Modular installable package and five command-line tools.
- Camera geometry and strict units; seeded degradations with parameter provenance.
- Translational registration, two early fusion algorithms and separate late box fusion.
- Label-dependent detection benchmarking and host-only computational profiling.
- E00 native-resolution sweep with synthetic labels, deterministic seed, CSV/HTML/JSON manifests.
- Dedicated P01/P02/P03 publication workspaces and offline test suite.

This changelog records implemented features only; it is not a validation certificate or a Git tag.

## Unreleased (experimental P02 branch)

- Add quality-scaled late box fusion with explicit finite reliability weights.
- Add E01 labelled four-arm comparison with input-provenance manifests and CSV metrics.
- Add synthetic example, focused tests and a study protocol; no field-performance claim.

## Unreleased documentation

- Searchable MkDocs Material guide with explicit CLI/data contracts and
  step-by-step E00, E01 and E02 reproduction.
- Verifiable documentation navigation, local links, executable metadata
  and negative regression tests for the documentation contract.
- Manual self-hosted strict MkDocs build; no automatic public deployment.
- This is documentation of reference/simulated methods, not new field evidence.

## Unreleased (sequence integrity, under review)

- Add vendor-independent offline audit for timestamped RGB/LWIR NumPy frame
  sequences with strict relative paths and bounded frame/file sizes.
- Add synthetic sequence demo and HTML/CSV/JSON pairing reports with SHA-256,
  native grids, dtype changes, timing skew and unmatched-frame counts.
- Explicitly distinguish time pairing from real clock synchronization,
  spatial registration, detector accuracy and radiometric validity.

## Unreleased (KISS usability pass, under review)

- Studio starts with a one-click synthetic example, a clear/reset action
  and a simpler two-step interface, without requiring a local image dataset.
- Selecting real data automatically discards the example's other modality
  instead of silently combining simulated and measured inputs.
- Mark synthetic example provenance in exported JSON, retain an explicit
  note about non-radiometric preview-only results and make CLI help
  recommend the simplest local workflow.
- Test blending behavior, source labels, reset, and sample-to-real transition
  without adding dependencies to the runtime.

## Unreleased (user experience, under review)

- Add unified `arc-rgbt` CLI with diagnostics and synthetic self-contained demo.
- Add offline browser Studio with pre-aligned raster and numeric 2D NumPy
  inputs, selectable grayscale blending, PNG export and metadata.
- Add bounded native uint16/float thermal preview with SHA-256,
  original intensity ranges and explicit display normalization.
- Add guardrails for invalid frames, extensionless output paths and
  regressions for overflow-prone float64 ranges.
- Changes remain research visualization tools; they are not thermal
  calibration, detector validation or MCU benchmark evidence.
