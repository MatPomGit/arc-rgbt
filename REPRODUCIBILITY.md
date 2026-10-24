# Reproducibility protocol

1. Record Python, NumPy, SciPy, OpenCV and OS versions together with code SHA. This baseline records the package version and available Git commit SHA; dependency environment capture remains a publication-release responsibility.
2. Check out the exact code SHA and install from pinned wheels on an isolated reference host. Do not expect the same numerical latency across hosts.
3. Run `pytest -q` and `ruff check src tests tools`, followed by all quick-start CLI calls.
4. Run `arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00`. Preserve its `manifest.json`, `metrics.csv`, `report.html` and generated previews separately, with SHA256 digests.
5. Confirm all seven native resolutions are present. `interpolated_preview_px` is visualization only. Ground truth is derived from the source synthetic rectangles and rounded outward to native pixel cells.
6. Interpret `precision`, `recall`, `f1` strictly as localization detection against generated class-agnostic annotations; do not cite as person/vehicle classification or measured thermal-sensor detection performance.
7. For actual publications, provide dataset version/licence, calibrated measurement chain, split policy, model weights with hashes, external independent evaluation and confidence intervals. These steps are not yet implemented.

No pre-generated synthetic performance table or fabricated validation logs are committed to the repository.


## Data integrity and interpretation

DegradeSim rejects inputs outside normalized [0,1] rather than silently turning
raw integer intensities into saturated unit pixels. Record upstream physical
calibration and normalization separately. The horizontal blur is a source-pixel
one-dimensional uniform exposure kernel, not a calibrated physical motion model.

E00 reports both rounded annotation areas and continuous native-pixel footprints.
For P01, compare `fraction_objects_subpixel_axis` across resolutions while
treating threshold-localization scores solely as synthetic sanity checks.
The P01 analysis refuses CSV/manifest metric mismatches, including precision and
recall, to avoid accidentally summarizing inconsistent artifacts.

Negative-only frames are valid evaluation samples when their empty annotations
have been verified. To run a fully negative dataset, set
`annotation_status: complete` in the Bench JSON; otherwise it is rejected to
avoid treating unannotated images as negatives. Mixed positive/negative legacy
datasets remain supported, with completeness the dataset curator's responsibility.
