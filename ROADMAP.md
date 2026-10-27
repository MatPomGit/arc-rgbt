# Roadmap

The current software on `main` includes reference sensor geometry and
degradation, early/late fusion, labelled benchmarks, pairing/registration,
E00–E02, offline Studio, safe native thermal preview, sequence audits,
host profiling and tests. See the [CLI reference](docs/reference/cli.md)
rather than repeating the feature list here.

| Planned stage | Engineering focus | Scientific prerequisite |
| --- | --- | --- |
| 0.2.x | Independently calibrated geometry/timing, dataset import and quality estimation | Verified acquisitions, native grids and licensing |
| 0.3.x | Temporal/quality fusion ablations and AP reporting | Frozen P02 outcomes and independent scene splits |
| 0.4.x | Quantization, constrained inference and device measurements | Named target, measured RAM/flash/latency/energy |

Versions above are **plans**, not tagged releases or promises of dates.
Research tasks RGBT-01–07 and their acceptance gates:
[AUTOPILOT_PLAN.md](AUTOPILOT_PLAN.md). Current verified evidence and blockers:
[PROJECT_STATE.yaml](PROJECT_STATE.yaml). Do not infer field performance
from reference simulations.
