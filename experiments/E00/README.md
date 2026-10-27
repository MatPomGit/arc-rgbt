# E00: native resolution sweep

Reproducible seeded, **synthetic-only** class-agnostic localization on
20 generated scenes with two labelled rectangles per frame. Native
grids span 8×8 through 320×240; outward-rounded boxes and continuous
subpixel-footprint diagnostics must not be conflated.

```bash
arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00
```

Canonical method, outputs and interpretation:
[E00 guide](https://github.com/MatPomGit/arc-rgbt/blob/main/docs/experiments/e00.md).
No physical sensor performance is inferred.
