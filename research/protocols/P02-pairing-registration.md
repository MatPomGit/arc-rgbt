# P02: Acquisition synchrony and asymmetric RGB–LWIR registration

## Research questions

1. For a specified RGB/LWIR frame-rate asymmetry, what proportion of LWIR
   frames can be paired with a distinct RGB observation under tolerance
   windows of 10, 30, 50 and 100 milliseconds?
2. How do geometric coverage and synchronization tolerance affect **measured**
   downstream detection quality when independently annotated real sequences
   become available?
3. How does registration to the native thermal grid compare with interpolation
   onto the RGB grid in compute cost and observable input information?

## Protocol

- Record RGB and thermal **exposure reference instants**, not arrival instants.
  Ensure a shared clock or independently estimate and document the clock
  transform; refuse uncalibrated heterogeneous clock domains.
- Record per-sensor serial/FOV, lens state, resolution, calibration matrix,
  mounting orientation, calibration target/depth and uncertainty.
- Use the provided pairing baseline with a predeclared tolerance. Report
  counts, thermal pairing fraction, median/p95 absolute time skew and the
  number of unmatched observations; report the greedy matching limitation.
- Calibrate the geometric transform **outside** this reference module,
  retaining residual reprojection errors and an independent validation scene.
- Export masks of valid overlap. Run native thermal-grid and RGB-grid alignment
  variants without claiming interpolated pixels carry new thermal detail.
- For flight data, stratify by speed, range, roll and observation angle.
  Maintain split-by-sequence/flight to prevent train/test leakage.
- Use confidence intervals across **independent flights or scenes**, not
  adjacent frames treated as independent replicates.

## Evidence boundary and acceptance

In this draft, unit tests and synthetic examples establish software behavior
only. Physical timing calibration, extrinsic calibration error, object
recognition, real-world performance and efficiency on microcontrollers are
unverified. Empirical P02 claims require annotated real camera recordings
and independently verified camera clock domains.

## Reproduction

\`\`\`bash
arc-rgbt-sync --input configs/scenarios/synchronization-example.json \
  --output reports/synchronization.json
python -m pytest -q tests/test_synchronization.py tests/test_registration.py
\`\`\`
