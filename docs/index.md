# arc-rgbt

Offline, hardware-independent RGB–thermal research software for native
resolution, simulated degradation, fusion and reference diagnostics.
E00–E02 are synthetic/analytical **software experiments**, not measured
camera or embedded-device performance.

## Start here

- [Install and run a synthetic example](getting-started.md)
- [Commands and input/output contracts](reference/cli.md) · [data schemas](reference/data-contracts.md)
- [Processing architecture](concepts/architecture.md) · [scientific evidence boundaries](concepts/evidence.md)
- [Research programme P01–P08](experiments/publications.md) · [reproducibility](reproducibility.md)
- [Candidate datasets and licences](experiments/datasets.md) · [literature screening](experiments/literature-screening.md) · [evaluation requirements](guides/evaluation-requirements.md)

## Experiment reference

| Experiment | Purpose | Limits |
| --- | --- | --- |
| [E00](experiments/e00.md) | Resolution and geometric observability | Simulated rectangles |
| [E01](experiments/e01.md) | Four-method quality-weighted fusion | Hand-authored detections |
| [E02](experiments/e02.md) | Frame skew and idealized geometry | Not detector accuracy |

See the [source repository](https://github.com/MatPomGit/arc-rgbt),
[development guide](development.md) and [project state](https://github.com/MatPomGit/arc-rgbt/blob/main/PROJECT_STATE.yaml).
