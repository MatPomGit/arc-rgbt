# Architecture (v0.1.0)

`src/arc_rgbt/` is the implementation layer; `tools/` contains thin executable entry-point wrappers. `configs/` separates camera geometry, processor assumptions and scenario parameters. `research/` stores hypotheses, protocols and literature tracking. `experiments/E00/` holds a committed experiment configuration, not outcomes. `datasets/manifests/` contains descriptions/miniature labelled examples, not downloaded datasets. `reports/` is git-ignored except its placeholder. `applications/` and `embedded/` are forward-looking integration boundaries. `publications/P01-P03/` hold protocols and reproduction plans.

## Interfaces and fidelity boundaries

- `Camera` validates explicit `*_px`, `*_um`, `*_mm`; `geometry` is an ideal pinhole projection onto a frontal plane. Object coverage ignores occlusion and clipping near image edges.
- `degrade()` is a normalized image simulation with deterministic RNG. Blur parameters are specified in **source image pixels**, noise standard deviation in [0,1] intensity units, output size in **native simulated sensor pixels**. Interpolation is never treated as a native resolution increase.
- `register_translation()` uses grayscale phase correlation. Not physically calibrated across RGB/LWIR and not robust against arbitrary parallax or severe modality changes.
- `fuse_images()` offers early fusion methods `weighted` and `gradient`. `fuse_detections()` implements late-stage class-matched weighted box fusion, not pixel fusion.
- `bench.evaluate()` consumes actual box annotations and prediction records. Greedy one-to-one class-matched IoU at threshold 0.5 is **not** mAP or MOT evaluation. Empty datasets are refused by the reporting layer.
- `DeviceProfiler` is the forward-compatible MCU adapter protocol; `profile_cpu()` benchmarks an explicitly named OpenCV operator on the executing host. Python `tracemalloc` does not account for native OpenCV allocations.

## Data provenance

Every report includes `data_origin` and/or `physical_measurements`. Values distinguish `simulated`, `reference_algorithm`, `analytical_estimate` and `measured_host_reference`; only physical-device adapters may claim hardware measurements. JSON manifests include package version, available git HEAD and SHA-256 of file inputs. Re-running from an installed package outside a Git checkout may result in `git_sha=null`; that absence is deliberate, not fabricated.

## Dependency and trust policy

Required: Python 3.12+, NumPy, SciPy, OpenCV headless and PyYAML. PyTorch is optional. Tests use no model weights or network calls. Self-hosted CI requires a manual trusted dispatch; running arbitrary third-party PR code on a privileged runner is disallowed. CI does not create releases or auto-merge branches.
