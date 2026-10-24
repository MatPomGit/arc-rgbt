# P01 reproducible analyses

Implemented: `summarize_e00.py` consumes generated E00 manifest/CSV and writes a SHA-256-linked JSON summary, explicitly marked `simulated`.

```bash
arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00
python publications/P01/analyses/summarize_e00.py --experiment-dir reports/E00 --output reports/P01/e00_summary.json
```

For real camera studies, new scripts and preregistered analyses will be required. These E00 point estimates are not empirical detection performance.
