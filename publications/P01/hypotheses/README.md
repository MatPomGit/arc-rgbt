# P01: low-cost native-resolution detection limits

**Status:** CORE PLANNED; hypothesis proposed, not preregistered. No independent empirical result.

## H1 and H0

**H1:** Under fixed and preregistered detection/false-alarm operating points, lower **physically acquired native target pixel footprint** is associated with worse held-out human/vehicle recall after stratification by capture geometry, contrast, modality and scene source.

**H0:** No association between measured native target footprint and held-out recall within the preregistered acquisition strata.

## Outcomes and controls

- **Primary:** Change in real-sensor recall at a predeclared FP/frame budget between defined native-pixel-footprint strata, with sequence/scene as independent unit.
- **Secondary:** AP at specified IoU, box localization error, modality dependence, occlusion and viewing-angle strata, and confidence intervals clustered by acquisition.
- **Controls:** original native images, same checkpoint and test labels, consistent thresholds/FP budgets, independent sensor/projection metadata; report simulated E00 degradation separately from actual low-resolution acquisitions.
- **Stopping / negative evidence:** if native source geometry, complete labels or independent holdout cannot be verified, do not publish claims about physical distance or sensor resolution limits.

See the [P01 protocol](../protocol/README.md) and [common measurement rules](../../../docs/guides/evaluation-requirements.md).
