# P01: low-cost native-resolution detection limits

**Status:** CORE PLANNED; hypothesis proposed, not preregistered. No independent empirical result.

## H1 and H0

**H1 (directional candidate):** With a frozen LWIR detector and validation-only selected operating point, the equal-acquisition-weighted mean of within-acquisition small-minus-reference *IoU-0.50 localization-qualified* GT recall differences is negative (`Delta < 0`). This is an association, not a causal sensor-resolution effect.

**H0 (candidate):** The within-acquisition LWIR contrast averaged equally across eligible paired acquisition groups is zero (`Delta = 0`). Its inferential decision rule remains subject to author freeze before any held-out outcomes.

## Outcomes and controls

- **Primary candidate (pending author freeze):** LWIR-only equal-weight *paired acquisition* contrast for native GT footprint `s < 8` versus `s >= 16` pixels. At least 10 source-verified groups with both bins are provisionally required; the validation-selected cutoff is locked on test, with target 0.10 FP/frame. RGB is secondary; fusion belongs to P02. See the [full protocol](../protocol/README.md).
- **Secondary:** IoU=0.25 tiny-object localization sensitivity, AP at specified IoU, RGB modality, class/contrast/occlusion/viewpoint balance, and alternative weighting. No exploratory result may be promoted into a primary test.
- **Controls:** original native images, same checkpoint and test labels, consistent thresholds/FP budgets, independent sensor/projection metadata; report simulated E00 degradation separately from actual low-resolution acquisitions.
- **Stopping / negative evidence:** if native source geometry, complete labels or independent holdout cannot be verified, do not publish claims about physical distance or sensor resolution limits.

See the [P01 protocol](../protocol/README.md) and [common measurement rules](../../../docs/guides/evaluation-requirements.md).
