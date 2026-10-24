"""Reference host CPU profiling; embedded measurements require an external adapter."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Protocol

import cv2
import numpy as np

from arc_rgbt.common import exact_keys, load_yaml, positive_integer, provenance, save_json


class DeviceProfiler(Protocol):
    """Future MCU instrumentation adapter. Implementations must identify hardware."""

    def profile(self, payload: bytes) -> dict: ...


def profile_cpu(image: np.ndarray, repeats: int = 10, model: str | Path | None = None) -> dict:
    positive_integer(repeats, "repeats")
    if image.ndim != 2 or not image.size or not np.isfinite(image).all():
        raise ValueError("Provide a finite two-dimensional test image")
    work = image.astype(np.float32)
    cv2.GaussianBlur(work, (5, 5), 1.0)  # warm-up
    tracemalloc.start()
    times = []
    try:
        for _ in range(repeats):
            before = time.perf_counter_ns()
            cv2.GaussianBlur(work, (5, 5), 1.0)
            times.append((time.perf_counter_ns() - before) / 1e6)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return {"data_origin": "measured_host_reference", "device_class": "host_cpu",
            "host": platform.platform(), "kernel": "opencv GaussianBlur (5x5, sigma=1)",
            "input_shape_px": list(work.shape), "repetitions": repeats,
            "latency_median_ms": statistics.median(times), "latency_min_ms": min(times),
            "python_alloc_peak_bytes": peak,
            "input_array_bytes": work.nbytes,
            "model_file_bytes": Path(model).stat().st_size if model else None,
            "limitations": "Python allocation peak excludes native OpenCV/C allocations and RSS; "
                           "not a device power or MCU memory measurement",
            "provenance": provenance([model] if model else [])}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="Grayscale .npy test image")
    p.add_argument("--config", help="Optional host processor YAML profile")
    p.add_argument("--repeats", type=int, default=None)
    p.add_argument("--model", help="Optional local model file, used for file-size measurement only")
    p.add_argument("--output", default="reports/edgelab.json")
    a = p.parse_args(argv)
    config = load_yaml(a.config) if a.config else {}
    exact_keys(config, set(), {"name", "class", "note", "repeats"})
    if config.get("class", "host_cpu") != "host_cpu":
        raise ValueError("Only host_cpu profiling is implemented")
    repeats = a.repeats if a.repeats is not None else config.get("repeats", 10)
    result = profile_cpu(np.load(a.input, allow_pickle=False), repeats, a.model)
    print(json.dumps(result, indent=2))
    save_json(a.output, result)


if __name__ == "__main__":
    main()
