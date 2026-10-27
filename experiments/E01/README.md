# E01: quality-weighted box fusion

Synthetic four-arm comparison using externally supplied modality
qualities and existing labelled box proposals, **not** calibrated
reliability or real-world detector superiority.

```bash
arc-rgbt-e01 --dataset datasets/manifests/e01-synthetic-quality.json --output reports/E01
```

Canonical protocol, schemas, metrics and evidence limits:
[E01 guide](https://github.com/MatPomGit/arc-rgbt/blob/main/docs/experiments/e01.md).
