# Evidence and limitations

Always distinguish **implemented software**, **simulated examples** and
**independently measured sensor/hardware results**.

| Component | Supported claim | Not demonstrated |
| --- | --- | --- |
| SensorLab / E00 | Pinhole geometry and deterministic native-pixel simulation | Real optical sensitivity or trained detection |
| DegradeSim | Software blur, sampling and noise | Thermal radiometry or measured PSF/NETD |
| FusionLab / E01 | Reference pixel/box fusion and stipulated quality weights | Calibrated scores or field accuracy |
| Pairing / registration / E02 | Declared-clock matching and analytical overlap | Exposure synchrony, calibrated extrinsics or detector IoU |
| Bench | Annotated one-to-one IoU, precision/recall/F1 | AP/mAP or multi-object tracking |
| EdgeLab | Host OpenCV operator timing/allocations | Device inference, MCU RAM/flash or energy |

Every empirical claim needs traceable capture metadata, independent labels
and splits, genuine calibration and uncertainty measured over independent
scenes or acquisitions. Upsampling never restores native information.
Treat missing labels, skewed clocks, invalid overlap masks and model
confidence calibration as **separate error sources**.

Methods and acceptance metadata: [evaluation requirements](../guides/evaluation-requirements.md)
and [reproducibility](../reproducibility.md). Specific algorithms and their
limits: [E00](../experiments/e00.md), [E01](../experiments/e01.md),
[E02](../experiments/e02.md). Imported claims must pass
[literature screening](../experiments/literature-screening.md).
