# Research programme

## P01: Detection Limits of Low-Cost RGB–Thermal Sensors

Hypothesis: Object pixel footprint and degradation conditions constrain localization sensitivity. Primary work package: E00 synthetic resolution sensitivity; external labelled real sensor data are needed before drawing empirical conclusions. See `publications/P01`.

## P02: Adaptive and Temporal RGB–Thermal Fusion

Hypothesis: Registration-aware modality weighting may outperform fixed fusion under asynchronous sensing or camera motion. v0.1.0 includes reference static early/late fusion and supporting timestamp-pairing/externally calibrated planar registration. Adaptive/temporal detection models remain planned. See `publications/P02`.

## P03: Resource-Efficient Embedded RGB–Thermal Detection

Hypothesis: Quantized multi-modal inference can offer a favorable accuracy/latency/memory tradeoff under MCU constraints. v0.1.0 provides host profiling and an MCU adapter interface only. Device-level measurements are mandatory for empirical conclusions. See `publications/P03`.

## Controls

Use openly licensed datasets with explicit ground truth and split-by-sequence/device where appropriate; report mean and uncertainty over predeclared random seeds; stratify by optical geometry and motion. Distinguish synthetic, host-reference and physical device data. Maintain literature references in `research/literature` and pre-register any hypothesis-changing protocol revision.
