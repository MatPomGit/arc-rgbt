# Architecture

The toolkit separates **calculation**, **data and configuration**, **experiments**, and **publication preparation**. Every implemented module is runnable without connecting physical sensors.

| Location | Responsibility |
| --- | --- |
| `src/arc_rgbt/` | Main Python algorithms and CLI entry points |
| `configs/sensors/` | Sensor geometry with explicit physical units |
| `configs/scenarios/` | Degradation, fusion, synchronization and synthetic homography examples |
| `configs/processors/` | Host-CPU assumptions |
| `datasets/manifests/` | Metadata and small synthetic labelled fixtures, not downloaded datasets |
| `experiments/E00/` | Committed experiment configuration and protocol |
| `research/` | Hypotheses, literature references and acquisition protocol |
| `publications/P01–P03/` | Publication workspaces; no pre-claimed results |
| `tests/` | Offline regression and CLI checks |
| `reports/` | Generated, Git-ignored execution artifacts |

## Processing topology

```text
Camera / geometry metadata (SensorLab)
                |
Synthetic source -> DegradeSim -> native-resolution arrays
                                         |
           calibration + timing metadata (optional)
                   |                     |
              pair_frames            align_pair
                   |                     |
                   +--------> FusionLab <-+
                                 |
                    labelled predictions + ground truth
                                 |
                               Bench
                                 |
                       JSON / CSV / HTML reports

Independent tracks: E00 -> P01 summary; EdgeLab -> host CPU profile
```

**Interface units:** widths and heights in pixels; focal length in millimetres; pitch in micrometres; distance in metres; capture times in monotonic nanoseconds within a verified common clock. Images for DegradeSim must be normalized to `[0, 1]`.

## Design constraints

- **Native resolution first.** Upscaling creates additional array samples, not new sensor information.
- **Modality-specific evidence.** Reference RGB and thermal images must not be treated as physical samples without calibration provenance.
- **Explicit provenance.** Reports identify simulation/reference/host origin as appropriate; file hashes and available source SHA support traceability.
- **Strict inputs.** Unknown fields and nonfinite parameters are rejected by many core configuration paths.
- **Separation of research claims.** One-to-one IoU evaluation is not mAP; CPU time is not MCU energy; planar registration does not remove parallax.

For the detailed research boundaries see [Evidence and limitations](evidence.md) and [data contracts](../reference/data-contracts.md).
