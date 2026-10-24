# Roadmap

- **v0.1.0 implemented:** Five callable/CLI tools; explicit sensor units; seeded degradations; two early fusion operators; separate detection fusion; labelled evaluation; synthetic E00; reference-host profiler; offline tests; experiment manifests.
- **P02 groundwork implemented in v0.1.0 draft:** Shared-clock greedy frame matching; externally provided planar RGB-to-LWIR homography with unequal native image sizes and overlap mask. No clock offset estimation, calibration solver or temporal detector.
- **v0.2.0 planned:** Camera extrinsics and uncertainty; RGB-to-LWIR cross-modal landmarks and robust registration; synchronization perturbation; realistic thermal point-spread functions; multi-class dataset import with licence checks; confidence calibration.
- **v0.3.0 planned:** Adaptive/temporal fusion with ablations (P02); target-depth/sensor-motion models; AP across IoU thresholds; prediction data interchange.
- **v0.4.0 planned:** Quantization/pruning baselines and explicit RAM/flash/timing budgets, MCU adapter implementations and physical energy/latency instrumentation (P03).
- **Pre-publication gates:** Document calibrated physical validation, independent datasets, test leakage controls, confidence intervals and independent replication. No publication claim is made by this scaffold.

- **E01 / P02 quality baseline (new experimental PR):** Quality-scaled late
  fusion on already co-registered scored boxes; deterministic four-method
  labelled benchmarking; quality must be independently measured or declared.
  This is a heuristic baseline, not probabilistic uncertainty calibration.
- **Publication readiness gate for E01:** Locked real-data sequence splits,
  independently derived quality proxies, calibrated detector scores,
  independent scene-level confidence intervals and measured MCU costs.
