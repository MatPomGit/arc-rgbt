# arc-rgbt

**Low-Cost RGB–Thermal Fusion Research Platform** · Version 0.1.0

`arc-rgbt` is an open, hardware-independent Python toolkit for studying spatial resolution, controlled image degradation, RGB–thermal fusion, labelled object-localization metrics and computational constraints. It targets reproducible research with low- and medium-resolution sensors.

[Start with a reproducible example](getting-started.md) · [Explore the architecture](concepts/architecture.md) · [Read the evidence policy](concepts/evidence.md)

## Implemented software

| Area | Implementation | Scientific boundary |
| --- | --- | --- |
| SensorLab | Pinhole FOV, GSD and object footprint | Analytical frontal-plane approximation |
| DegradeSim | Seeded blur, downsampling and noise | Simulated normalized intensity, not sensor radiometry |
| FusionLab | Translation-only alignment, image and box fusion | Reference algorithms; no physical cross-modal calibration |
| Bench | Greedy labelled IoU matching and P/R/F1 reports | Not mAP, tracking or a real-world detection benchmark |
| EdgeLab | Host OpenCV latency and Python allocation statistics | **Not** MCU RAM, flash, power or model inference |
| E00 / P01 | Seeded synthetic resolution sweep and auditable summary | **Not** person/vehicle recognition |
| E01 | Four-arm labelled detection fusion comparison | Synthetic quality weights, not real-world detection evidence |
| E02 | Timing and lateral-shift analytical geometry on native grids | Geometric overlap is not detector IoU or pixel-resolution performance |
| P02 groundwork | Timestamp matching and projective registration | Requires shared clocks and external homography |

## Research integrity

!!! warning "Simulation is not measurement"
    Synthetic geometric labels and threshold-based localization do **not** establish the accuracy of physical thermal imagers, detection of people or vehicles, or embedded-device performance.

The code runs locally, without cloud APIs or pretrained-model downloads. Python 3.12 or later is required. Documentation itself is a static MkDocs site with local search; hosting is optional.

## Find your next step

- [Installation and first experiment](getting-started.md)
- [E00 methodology and outputs](experiments/e00.md)
- [E01 labelled quality fusion](experiments/e01.md)
- [E02 timing/skew geometry](experiments/e02.md)
- [Frame pairing and planar registration](guides/synchronization-registration.md)
- [CLI and JSON contracts](reference/cli.md)
- [Publication readiness and traceability](reproducibility.md)

Source code and licence: [arc-rgbt repository](https://github.com/MatPomGit/arc-rgbt).

## Research review intake

A selective screening of historical RGB–thermal/aerial-imaging literature
is available in [literature screening](experiments/literature-screening.md).
Its methodology is distilled into
[experimental evaluation requirements](guides/evaluation-requirements.md).
These pages do not add verified physical performance claims.
