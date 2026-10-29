"""Strict optional adapter to an independently supplied, pinned TrackEval checkout.

The default mode builds an audit contract only and returns HOTA/IDF1 = null.
Executing third-party code requires an explicit opt-in and a clean checkout.
No source checkout, dataset or model is downloaded by this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

from arc_rgbt.admission import _unique_pairs
from arc_rgbt.evaluation_contracts import tracking_reference_contract
from arc_rgbt.fusionlab import _iou

PINNED_REPO = "https://github.com/JonathonLuiten/TrackEval"
PINNED_SHA = "12c8791b303e0a0b50f753af204249e622d0281a"
MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_TIMESTEPS = 20_000
MAX_DETECTIONS = 400_000

# The pinned TrackEval source still uses np.float and np.int.
# These obsolete aliases are installed ONLY inside the opt-in child process.
_REFERENCE_SCRIPT = r"""
import json
import sys
import numpy as np

if "float" not in np.__dict__:
    np.float = float
if "int" not in np.__dict__:
    np.int = int
sys.path.insert(0, sys.argv[1])
import trackeval

src = json.load(sys.stdin)
result = {}
for label, case in src.items():
    data = {}
    for field in ("gt_ids", "tracker_ids"):
        data[field] = [np.asarray(v, dtype=np.int64) for v in case[field]]
    data["similarity_scores"] = [
        np.asarray(v, dtype=np.float64).reshape(
            (len(data["gt_ids"][i]), len(data["tracker_ids"][i]))
        ) for i, v in enumerate(case["similarity_scores"])
    ]
    for field in (
        "num_timesteps", "num_gt_ids", "num_tracker_ids",
        "num_gt_dets", "num_tracker_dets",
    ):
        data[field] = int(case[field])
    h = trackeval.metrics.HOTA().eval_sequence(data)
    identity = trackeval.metrics.Identity({"PRINT_CONFIG": False}).eval_sequence(data)
    result[label] = {
        "hota": float(np.mean(h["HOTA"])),
        "hota_alphas": [float(x) for x in h["HOTA"]],
        "idf1": float(identity["IDF1"]),
        "idtp": int(identity["IDTP"]),
        "idfp": int(identity["IDFP"]),
        "idfn": int(identity["IDFN"]),
    }

# Sanity checks from the official pinned TrackEval tests and analytic perfect tracking.
perfect = {
    "num_timesteps": 2, "num_gt_ids": 1, "num_tracker_ids": 1,
    "num_gt_dets": 2, "num_tracker_dets": 2,
    "gt_ids": [np.asarray([0]), np.asarray([0])],
    "tracker_ids": [np.asarray([0]), np.asarray([0])],
    "similarity_scores": [np.asarray([[1.]]), np.asarray([[1.]])],
}
h = trackeval.metrics.HOTA().eval_sequence(perfect)
ident = trackeval.metrics.Identity({"PRINT_CONFIG": False}).eval_sequence(perfect)
if abs(float(np.mean(h["HOTA"])) - 1) > 1e-12 or abs(float(ident["IDF1"]) - 1) > 1e-12:
    raise RuntimeError("Perfect-track HOTA/IDF1 sanity check failed")

# Official upstream tests/test_metrics.py no_confusion:
# IDTP=4, IDFN=4, IDFP=5, IDF1 = 8/17.
no_confusion = {
    "num_timesteps": 5, "num_gt_ids": 2, "num_tracker_ids": 2,
    "num_gt_dets": 8, "num_tracker_dets": 9,
    "gt_ids": [np.asarray(v, dtype=int) for v in [[0,1],[0,1],[0,1],[0],[0]]],
    "tracker_ids": [np.asarray(v, dtype=int) for v in [
        [0,1],[0,1],[0,1],[0,1],[1]
    ]],
    "similarity_scores": [np.asarray(v, dtype=float) for v in [
        [[0,0],[1,0]], [[0,0],[1,0]], [[0,0],[0,0]], [[0,1]], [[1]],
    ]],
}
test_identity = trackeval.metrics.Identity({"PRINT_CONFIG": False}).eval_sequence(
    no_confusion
)
if (int(test_identity["IDTP"]), int(test_identity["IDFN"]),
        int(test_identity["IDFP"])) != (4, 4, 5):
    raise RuntimeError("Official Identity ID counts sanity check failed")
if abs(float(test_identity["IDF1"]) - 8 / 17) > 1e-12:
    raise RuntimeError("Official Identity IDF1 sanity check failed")
print(json.dumps(result, allow_nan=False, sort_keys=True))
"""


def _case(frames: list[dict], label: str) -> dict:
    ground_ids = sorted({
        item["track_id"] for frame in frames for item in frame["ground_truth"]
        if item["label"] == label
    })
    predicted_ids = sorted({
        item["track_id"] for frame in frames for item in frame["predictions"]
        if item["label"] == label
    })
    gt_lookup = {value: i for i, value in enumerate(ground_ids)}
    pred_lookup = {value: i for i, value in enumerate(predicted_ids)}
    result: dict = {
        "num_timesteps": len(frames), "num_gt_ids": len(ground_ids),
        "num_tracker_ids": len(predicted_ids),
        "num_gt_dets": 0, "num_tracker_dets": 0,
        "gt_ids": [], "tracker_ids": [], "similarity_scores": [],
    }
    for frame in frames:
        gt = [item for item in frame["ground_truth"] if item["label"] == label]
        pred = [item for item in frame["predictions"] if item["label"] == label]
        result["gt_ids"].append([gt_lookup[item["track_id"]] for item in gt])
        result["tracker_ids"].append([pred_lookup[item["track_id"]] for item in pred])
        result["similarity_scores"].append([
            [_iou(g["bbox_xywh"], p["bbox_xywh"]) for p in pred] for g in gt
        ])
        result["num_gt_dets"] += len(gt)
        result["num_tracker_dets"] += len(pred)
    return result


def prepare(frames: list[dict]) -> dict:
    """Build unambiguous per-class TrackEval arrays, without executing it."""
    tracking_reference_contract(frames)
    if len(frames) > MAX_TIMESTEPS:
        raise ValueError("Tracking input exceeds 20,000 frames")
    if frames[0]["frame_index"] != 0 or any(
        frame["frame_index"] != i for i, frame in enumerate(frames)
    ):
        raise ValueError("TrackEval input needs contiguous zero-based, complete frames")
    total = sum(len(frame["ground_truth"]) + len(frame["predictions"])
                for frame in frames)
    if total > MAX_DETECTIONS:
        raise ValueError("Tracking input exceeds 400,000 objects")
    labels = sorted({
        item["label"] for frame in frames
        for role in ("ground_truth", "predictions") for item in frame[role]
    })
    if not labels:
        raise ValueError("No labelled objects in sequence; scores are undefined")
    return {label: _case(frames, label) for label in labels}


def verify_reference_checkout(folder: str | Path) -> Path:
    """Reject modified or wrong-revision source before opt-in code execution."""
    root = Path(folder).expanduser().resolve()
    if not root.is_dir() or not (root / "trackeval" / "metrics" / "hota.py").is_file():
        raise ValueError("Reference root must contain the TrackEval source checkout")

    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True,
            text=True, check=True, timeout=10,
        )
        return completed.stdout.strip()

    try:
        if Path(git("rev-parse", "--show-toplevel")).resolve() != root:
            raise ValueError("Reference root must equal the Git checkout root")
        revision = git("rev-parse", "HEAD")
        if revision != PINNED_SHA:
            raise ValueError(f"TrackEval HEAD mismatch: {revision}; requires {PINNED_SHA}")
        if git("status", "--porcelain"):
            raise ValueError("TrackEval checkout is modified or contains untracked files")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        raise ValueError("Cannot verify pinned TrackEval checkout") from exc
    return root


def audit(
    frames: list[dict], *, reference_root: str | Path | None = None,
    run_reference: bool = False,
) -> dict:
    """Default is dry-run; explicit opt-in calls the exact upstream HOTA/Identity."""
    cases = prepare(frames)
    if type(run_reference) is not bool:
        raise ValueError("run_reference must be boolean")
    if run_reference and reference_root is None:
        raise ValueError("Reference execution requires --reference-root")
    if not run_reference and reference_root is not None:
        raise ValueError("Reference root supplied without explicit --run-reference")

    result = {
        "tool": "arc-rgbt-trackeval-adapter", "schema_version": 1,
        "data_origin": "user_declared_unverified",
        "reference_repository": PINNED_REPO, "reference_sha": PINNED_SHA,
        "reference_execution": False, "empirical_admission": False,
        "licence_verified": False, "ground_truth_verified": False,
        "classes": sorted(cases), "frames": len(frames),
        "results": {label: {"hota": None, "idf1": None} for label in cases},
        "limitations": [
            "Data rights, tracking identities and source frames are not independently verified",
            "Classwise bbox IoU; no ignore regions, crowd policy or class remapping",
            "Frames must be complete and contiguous; no inferred missing frames",
            "One sequence only: do not pool identities or claim flight-level uncertainty",
        ],
    }
    if not run_reference:
        result["evaluation_status"] = "DRY_RUN_REFERENCE_NOT_EXECUTED"
        return result
    root = verify_reference_checkout(reference_root)
    safe_env = {key: value for key, value in os.environ.items()
                if key in {"PATH", "SYSTEMROOT", "WINDIR", "TMP", "TEMP", "TMPDIR"}}
    try:
        process = subprocess.run(
            [sys.executable, "-I", "-c", _REFERENCE_SCRIPT, str(root)],
            input=json.dumps(cases, allow_nan=False), text=True, capture_output=True,
            cwd=str(root), env=safe_env, timeout=120, check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ValueError(
            "Pinned TrackEval could not run in isolated Python process; "
            "check optional dependencies and NumPy compatibility"
        ) from exc
    try:
        values = json.loads(process.stdout, object_pairs_hook=_unique_pairs)
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("TrackEval output is not valid JSON") from exc
    if not isinstance(values, dict) or set(values) != set(cases):
        raise ValueError("TrackEval returned unexpected class set")
    for metrics in values.values():
        if not isinstance(metrics, dict) or set(metrics) != {
            "hota", "hota_alphas", "idf1", "idtp", "idfp", "idfn",
        }:
            raise ValueError("TrackEval returned unexpected metric fields")
        for name in ("hota", "idf1"):
            v = metrics[name]
            if type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1:
                raise ValueError("TrackEval reported invalid normalized score")
        if (not isinstance(metrics["hota_alphas"], list)
                or len(metrics["hota_alphas"]) != 19
                or any(type(v) not in (int, float) or not math.isfinite(v)
                       or not 0 <= v <= 1 for v in metrics["hota_alphas"])):
            raise ValueError("TrackEval returned invalid HOTA alpha series")
    result["reference_execution"] = True
    result["reference_self_check"] = "PASS"
    result["evaluation_status"] = "PINNED_REFERENCE_EXECUTED_ON_DECLARED_INPUT"
    result["results"] = values
    return result


def run(source: str | Path, *, reference_root: str | Path | None = None,
        run_reference: bool = False) -> dict:
    path = Path(source)
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Track input exceeds 8 MiB")
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    if not isinstance(obj, dict) or set(obj) != {
        "schema_version", "sequence_id", "frames", "data_origin",
    }:
        raise ValueError("Track input requires schema_version, sequence_id, frames, data_origin")
    if type(obj["schema_version"]) is not int or obj["schema_version"] != 1:
        raise ValueError("Unsupported tracking input schema")
    if not isinstance(obj["sequence_id"], str) or not obj["sequence_id"].strip():
        raise ValueError("sequence_id must be a nonempty string")
    if (not isinstance(obj["data_origin"], str)
            or obj["data_origin"] not in {"synthetic", "external_unverified"}):
        raise ValueError("data_origin must be synthetic or external_unverified")
    report = audit(obj["frames"], reference_root=reference_root,
                   run_reference=run_reference)
    report["sequence_id"] = obj["sequence_id"]
    report["data_origin"] = obj["data_origin"]
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Local JSON with complete tracking frames")
    parser.add_argument("--reference-root", help="Locally reviewed clean TrackEval checkout")
    parser.add_argument("--run-reference", action="store_true",
                        help="Explicitly execute pinned third-party TrackEval; never automatic")
    parser.add_argument("--output", help="Exclusive new report JSON file")
    args = parser.parse_args(argv)
    try:
        result = run(args.input, reference_root=args.reference_root,
                     run_reference=args.run_reference)
        payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(payload)
        print(payload, end="")
    except (OSError, TypeError, ValueError, UnicodeError) as exc:
        parser.exit(1, f"trackeval: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
