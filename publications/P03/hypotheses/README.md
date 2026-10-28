# P03: fixed embedded inference efficiency

**Status:** CORE PLANNED; hypothesis proposed, not preregistered. No physical target measurements.

## H1 and H0

**H1:** On a named, physically instrumented constrained target, at least one preregistered fixed RGB/LWIR model and precision configuration reduces measured end-to-end energy and memory demand relative to a feasible reference while remaining inside an independently frozen detection-quality and latency budget.

**H0:** No fixed configuration meets the combined energy, memory, detection-quality and latency criteria against the feasible reference.

## Outcomes and controls

- **Primary:** End-to-end joules per fully processed frame at matched held-out recall and FP/frame limits, together with peak measured device memory and flash usage.
- **Secondary:** Inference/fusion/acquisition latency distribution p50/p95/p99, AP, boot/idle baseline, device temperature, precision and native input resolution.
- **Baselines:** fixed RGB-only, fixed LWIR-only and fixed dual-sensor inference where device memory allows; distinguish infeasible configurations explicitly rather than fabricating a baseline.
- **Experimental unit:** independently repeated workloads and acquisition sequences, with code/model/input hashes, target revision, power instrument and operational clock/thermal conditions recorded.
- **Stopping:** if no target supports valid power and memory instrumentation, remain host reference only; host OpenCV timing is not embedded performance.

P07 will require separate adaptive-policy switching and measured energy improvements; these fixed-P03 results alone do not establish P07. See [P03 protocol](../protocol/README.md).
