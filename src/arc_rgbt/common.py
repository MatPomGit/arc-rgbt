"""Shared strict config handling and reproducible report helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from arc_rgbt import __version__


def load_yaml(path: str | Path) -> dict[str, Any]:
    obj = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("YAML root must be a mapping")
    return obj


def exact_keys(data: dict, required: set[str], optional: set[str] | None = None) -> None:
    optional = optional or set()
    unknown = set(data) - required - optional
    missing = required - set(data)
    if unknown or missing:
        raise ValueError(f"Missing keys: {sorted(missing)}; unknown keys: {sorted(unknown)}")


def positive_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name} must be a positive number")
    import math

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")
    return float(value)


def positive_integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def provenance(input_paths: list[str | Path] | None = None) -> dict[str, Any]:
    package_root = Path(__file__).resolve().parents[2]
    try:
        sha = subprocess.run(
            ["git", "-C", str(package_root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=3,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        sha = None
    files = {}
    for path in input_paths or []:
        p = Path(path)
        files[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return {"code_version": __version__, "git_sha": sha, "input_sha256": files}


def save_json(path: str | Path, data: Any) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return p
