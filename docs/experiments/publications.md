# Research programme: P01–P03

The project structures three publication lines without claiming results not established by independently measured data.

| Workstream | Question | Present maturity |
| --- | --- | --- |
| **P01**: detection limits | How do resolution and target footprint constrain object localization? | E00 executable synthetic baseline and audit-ready summary; empirical validation pending |
| **P02**: adaptive and temporal fusion | What is the effect of synchronization errors, calibration and modality fusion? | Timestamp-pairing and projective-registration **reference primitives only** |
| **P03**: embedded efficiency | What are latency, memory, energy and accuracy trade-offs on constrained targets? | Host-only OpenCV reference profiler; **no MCU measurements** |

## P01 analysis pathway

1. Predeclare source image generation and output resolutions.
2. Execute [E00](e00.md) and preserve the generated configuration/provenance.
3. Recompute P01 summary from the machine-readable experiment artifacts.
4. Acquire independently labelled **real** data and define a statistical plan before a generalization claim.

## P02 acquisition pathway

The research protocol calls for verified shared-clock exposure instants, independently calibrated RGB→thermal mapping, valid overlap masks, split-by-sequence evaluation, and uncertainty quantified at the acquisition/scene level.

The existing CLI tools intentionally lack physical clock calibration, tracking, global sequence assignment and learned adaptive fusion. See [synchronization and registration](../guides/synchronization-registration.md).

## P03 measurement pathway

A defensible embedded comparison must specify device model and software stack, target clocks, flash/RAM or peak activation memory, inference latency, workload, power instrumentation, conditions and confidence intervals. `edgelab` **does not** measure these quantities; it profiles a host-side OpenCV operator.

All three publication folders in `publications/` are research workspaces, not accepted or submitted papers. Consult [evidence limitations](../concepts/evidence.md).
