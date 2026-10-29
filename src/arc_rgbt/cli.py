"""Discoverable CLI for local RGB/thermal experiments and diagnostics."""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import shutil
import sys
import tempfile
from pathlib import Path

from arc_rgbt import __version__

TOOLS = {
    "sensor": ("sensorlab", "Camera geometry and native pixel footprint"),
    "degrade": ("degradesim", "Synthetic native-resolution degradation"),
    "fuse": ("fusionlab", "Early image fusion on aligned arrays"),
    "bench": ("bench", "Labelled box evaluation and reports"),
    "edge": ("edgelab", "Host CPU profiling (not MCU power)"),
    "e00": ("e00", "Synthetic resolution experiment"),
    "e01": ("e01", "Labelled quality-weighted proposal experiment"),
    "e02": ("e02", "Simulated synchronization/geometry experiment"),
    "sync": ("synchronization", "Pair timestamps on a common clock"),
    "register": ("registration", "Apply an externally calibrated homography"),
    "studio": ("studio", "Offline visual image viewer and fusion controls"),
    "thermal": ("thermal_preview", "Raw 16-bit or float .npy preview with provenance"),
    "sequence": ("sequence_audit", "Audit RGB/LWIR timestamped frames and pairing quality"),
    "admission": ("admission", "Validate offline metadata and scene/flight splits"),
    "near-duplicates": ("near_duplicate_audit", "Audit local image subset leakage (human review)"),
    "trackeval": ("trackeval_adapter", "Tracking input preflight or opt-in pinned TrackEval"),
    "split": ("split_plan", "Propose deterministic independent acquisition-group splits"),
}
DEPENDENCIES = {"numpy": "NumPy", "cv2": "OpenCV", "scipy": "SciPy", "yaml": "PyYAML"}


def _parser() -> argparse.ArgumentParser:
    descriptions = "\n".join(f"  {name:<10} {detail}" for name, (_, detail) in TOOLS.items())
    parser = argparse.ArgumentParser(
        prog="arc-rgbt",
        description="Offline RGB/thermal research toolkit. No camera or dataset download required.",
        epilog=("Start here:\n"
                "  arc-rgbt studio       Open the viewer and click Try an example\n"
                "  arc-rgbt doctor       Check installed dependencies\n"
                "  arc-rgbt demo         Save a reproducible synthetic report\n"
                "  arc-rgbt sequence --demo   Audit synthetic RGB/LWIR timestamps\n\n"
                "Advanced tools (arc-rgbt <name> --help):\n" + descriptions),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_argument_group("commands")
    commands.add_argument("--version", action="version", version=f"arc-rgbt {__version__}")
    commands.add_argument("command", nargs="?", help="doctor, demo, " + ", ".join(TOOLS))
    return parser


def _doctor(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="arc-rgbt doctor", description="Check local runtime")
    parser.add_argument("--json", action="store_true", help="Machine-readable diagnostic")
    args = parser.parse_args(argv)
    dependencies = {}
    for module, label in DEPENDENCIES.items():
        try:
            imported = importlib.import_module(module)
        except (ImportError, OSError) as exc:
            dependencies[label] = {"ok": False, "detail": str(exc)}
        else:
            dependencies[label] = {"ok": True,
                                   "version": str(getattr(imported, "__version__", "unknown"))}
    python_ok = sys.version_info >= (3, 12)
    ok = python_ok and all(item["ok"] for item in dependencies.values())
    result = {"ok": ok, "python": platform.python_version(),
              "python_supported": python_ok, "dependencies": dependencies,
              "note": "Environment check only; no hardware or detector validation"}
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"Python {result['python']}: {'OK' if python_ok else 'requires >=3.12'}")
        for label, status in dependencies.items():
            print(f"{label}: {status.get('version', status.get('detail'))} "
                  f"({'OK' if status['ok'] else 'MISSING/BROKEN'})")
        print("Environment: " + ("READY" if ok else "NOT READY"))
        if not ok:
            print("Install local project dependencies: python -m pip install -e .")
    return 0 if ok else 1


def _demo(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="arc-rgbt demo",
        description="Create synthetic images, fusion, labelled evaluation and a host profile",
    )
    parser.add_argument("--output", default="reports/demo", help="New, non-existing directory")
    parser.add_argument("--seed", type=int, default=7, help="Non-negative NumPy random seed")
    args = parser.parse_args(argv)
    if not 0 <= args.seed <= 2**32 - 1:
        parser.error("--seed must be an integer in [0, 4294967295]")
    destination = Path(args.output).expanduser().resolve()
    if destination.exists() or destination.is_symlink():
        parser.error(f"output already exists: {destination}; choose a new --output")
    destination.parent.mkdir(parents=True, exist_ok=True)

    import cv2
    import numpy as np

    from arc_rgbt.bench import report
    from arc_rgbt.common import save_json
    from arc_rgbt.degradesim import degrade
    from arc_rgbt.edgelab import profile_cpu
    from arc_rgbt.fusionlab import fuse_images
    from arc_rgbt.sensorlab import Camera, geometry

    staging = Path(tempfile.mkdtemp(prefix=".arc-rgbt-demo-", dir=destination.parent))
    try:
        rgb = np.full((192, 256), 0.12, dtype=np.float32)
        thermal = np.full((192, 256), 0.18, dtype=np.float32)
        rgb[64:144, 96:152] = 0.80
        thermal[64:144, 96:152] = 0.92
        np.save(staging / "rgb_source.npy", rgb, allow_pickle=False)
        np.save(staging / "thermal_source.npy", thermal, allow_pickle=False)
        degraded_rgb, rgb_meta = degrade(rgb, width_px=128, height_px=96,
                                         noise_sigma=0.02, seed=args.seed)
        degraded_thermal, thermal_meta = degrade(
            thermal, width_px=128, height_px=96, noise_sigma=0.02, seed=args.seed + 1
        )
        np.save(staging / "rgb_native.npy", degraded_rgb, allow_pickle=False)
        np.save(staging / "thermal_native.npy", degraded_thermal, allow_pickle=False)
        save_json(staging / "degradation.json", {"rgb": rgb_meta, "thermal": thermal_meta})
        fused = fuse_images(degraded_rgb, degraded_thermal, thermal_weight=0.5)
        np.save(staging / "fused.npy", fused, allow_pickle=False)
        for name, image in (("rgb_native", degraded_rgb),
                            ("thermal_native", degraded_thermal), ("fused", fused)):
            preview = (np.clip(image, 0, 1) * 255).astype(np.uint8)
            ok, encoded = cv2.imencode(".png", preview)
            if not ok:
                raise OSError(f"Could not encode preview for {name}")
            (staging / f"{name}.png").write_bytes(encoded.tobytes())
        save_json(staging / "sensor.json", geometry(Camera(80, 60, 17.0, 3.1), 20, 0.6, 1.7))
        ys, xs = np.nonzero(fused >= 0.5)
        if not len(xs):
            raise ValueError("Synthetic target not localized; demonstration aborted")
        estimated_bbox = [int(xs.min()), int(ys.min()),
                          int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]
        dataset = {
            "data_origin": "simulated",
            "annotation_status": "complete",
            "config": {"method": "illustrative_fixed_threshold", "threshold": 0.5,
                       "score_origin": "placeholder_not_calibrated_probability"},
            "frames": [{"id": "synthetic-0001",
                        "ground_truth": [{"label": "synthetic_target",
                                          "bbox": [48, 32, 28, 40]}],
                        "predictions": [{"label": "synthetic_target",
                                         "bbox": estimated_bbox, "score": 1.0}]}],
        }
        save_json(staging / "labels.json", dataset)
        metrics = report(dataset, staging / "bench")["metrics"]
        edge = profile_cpu(degraded_thermal, repeats=3)
        save_json(staging / "edge.json", edge)
        summary = {
            "data_origin": "simulated", "synthetic_demo": True, "seed": args.seed,
            "native_shape_px": [128, 96], "metrics": metrics,
            "files": ["rgb_source.npy", "thermal_source.npy", "rgb_native.npy",
                      "thermal_native.npy", "fused.npy", "rgb_native.png",
                      "thermal_native.png", "fused.png", "index.html", "sensor.json",
                      "degradation.json", "labels.json", "bench/bench.html", "bench/bench.csv",
                      "bench/bench.json", "edge.json"],
            "limitations": [
                "One synthetic rectangle, not person or vehicle recognition",
                "Fixed threshold and placeholder score are not a trained detector",
                "Benchmark results from this demonstration are not scientific evidence",
                "CPU timing depends on host load and is not an MCU or energy measurement",
            ],
        }
        save_json(staging / "summary.json", summary)
        (staging / "index.html").write_text(
            "<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>arc-rgbt synthetic demo</title>"
            "<style>body{font:16px system-ui,sans-serif;max-width:960px;margin:2rem auto;"
            "padding:0 1rem;background:#111827;color:#f9fafb}"
            "a{color:#93c5fd} .gallery{display:grid;grid-template-columns:"
            "repeat(auto-fit,minmax(240px,1fr));gap:1rem}"
            "figure{margin:0;background:#1f2937;padding:1rem;border-radius:8px}"
            "img{width:100%;image-rendering:pixelated}"
            "figcaption{padding-top:.5rem}</style>"
            "<h1>RGB–thermal: synthetic demonstration</h1>"
            "<p>Reference arrays only. No camera, calibrated detector or MCU is tested.</p>"
            "<div class='gallery'>"
            "<figure><img src='rgb_native.png' alt='Synthetic RGB intensity'>"
            "<figcaption>RGB-like intensity</figcaption></figure>"
            "<figure><img src='thermal_native.png' alt='Synthetic thermal intensity'>"
            "<figcaption>Thermal-like intensity</figcaption></figure>"
            "<figure><img src='fused.png' alt='Weighted image fusion'>"
            "<figcaption>Weighted image fusion</figcaption></figure></div>"
            "<p>Threshold-based localization is illustrative; its fixed score is not a "
            "calibrated probability. Metrics do not measure real detection accuracy.</p>"
            "<p><a href='bench/bench.html'>Labelled evaluation report</a> · "
            "<a href='summary.json'>Run summary</a> · "
            "<a href='edge.json'>Host CPU profile</a></p></html>\n",
            encoding="utf-8",
        )
        staging.rename(destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print(f"Demo created: {destination}")
    print(f"Open {destination / 'index.html'} for previews and report links")
    print("Synthetic reference only; not sensor performance or detector accuracy.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    parser = _parser()
    if not args or args[0] in ("-h", "--help", "--version"):
        parser.parse_args(args)
        if not args:
            parser.print_help()
        return 0
    name, *rest = args
    if name == "doctor":
        return _doctor(rest)
    if name == "demo":
        try:
            return _demo(rest)
        except (OSError, ValueError) as exc:
            parser.exit(1, f"arc-rgbt demo: {type(exc).__name__}: {exc}\n")
    if name not in TOOLS:
        parser.error(f"unknown command '{name}'; run 'arc-rgbt --help'")
    try:
        module = importlib.import_module(f"arc_rgbt.{TOOLS[name][0]}")
        module.main(rest)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"arc-rgbt {name}: {type(exc).__name__}: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
