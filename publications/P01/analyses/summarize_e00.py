"""Summarize E00 synthetic localization rows without introducing new claims."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def summarize(experiment_dir: Path, output: Path) -> dict:
    """Read generated E00 manifest and CSV, validating provenance and row alignment."""
    manifest_file = experiment_dir / "manifest.json"
    csv_file = experiment_dir / "metrics.csv"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if (manifest.get("experiment") != "E00" or manifest.get("data_origin") != "simulated"
            or manifest.get("physical_measurements") is not False):
        raise ValueError("Expected a simulated E00 manifest, not physical evidence")
    with csv_file.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 7 or len(manifest.get("resolutions", [])) != 7:
        raise ValueError("Expected seven E00 resolution variants")
    table = []
    for row, entry in zip(rows, manifest["resolutions"], strict=True):
        native = [int(row["native_width_px"]), int(row["native_height_px"])]
        if native != entry["native_resolution_px"]:
            raise ValueError("CSV and manifest native resolution mismatch")
        if int(row["tp"]) != entry["metrics"]["tp"]:
            raise ValueError("CSV and manifest localization counts mismatch")
        table.append({"native_resolution_px": native, "recall": float(row["recall"]),
                      "precision": float(row["precision"]), "f1": float(row["f1"])})
    summary = {
        "publication": "P01", "experiment": "E00", "data_origin": "simulated",
        "physical_measurements": False, "code_version": manifest["provenance"]["code_version"],
        "manifest_sha256": hashlib.sha256(manifest_file.read_bytes()).hexdigest(),
        "metrics_sha256": hashlib.sha256(csv_file.read_bytes()).hexdigest(),
        "localization_metrics_by_native_resolution": table,
        "limitations": "Synthetic rectangles and class-agnostic threshold localization; "
                       "no person/vehicle classification, physical calibration or hardware results",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment-dir", type=Path, default=Path("reports/E00"))
    parser.add_argument("--output", type=Path, default=Path("reports/P01/e00_summary.json"))
    args = parser.parse_args()
    print(summarize(args.experiment_dir, args.output)["publication"])


if __name__ == "__main__":
    main()
