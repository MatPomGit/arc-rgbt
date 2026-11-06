"""Select a deterministic, blinded P01 annotation QA sample from local metadata only.

No images, predictions, source rights or scientific admission are inspected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

STRATA = ("A", "B", "C", "D")
FRAME_KEYS = {
    "frame_id", "group_id", "qa_state", "class_conflict",
    "geometry_conflict", "clipped_box", "rider_only",
    "candidate_negative", "target_positive",
}
MAX_INPUT_BYTES = 8 * 1024 * 1024


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"Duplicate JSON key: {key}")
        out[key] = value
    return out


def _frame_stratum(frame: dict) -> str:
    if frame["qa_state"] in {"missing", "flagged"}:
        return "A"
    if any(frame[key] for key in (
        "class_conflict", "geometry_conflict", "clipped_box", "rider_only"
    )):
        return "B"
    if frame["candidate_negative"]:
        return "C"
    if frame["target_positive"]:
        return "D"
    raise ValueError(f"Unclassified frame: {frame['frame_id']}")


def _check(data: dict, quotas: dict[str, int], seed: int,
           max_per_group: int) -> None:
    if not isinstance(data, dict) or set(data) != {
        "schema_version", "source_release", "group_basis", "frames"
    }:
        raise ValueError("Invalid inventory fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unsupported inventory schema_version")
    if not isinstance(data["source_release"], str) or not data["source_release"].strip():
        raise ValueError("source_release required")
    if data["group_basis"] not in ("video_id_proxy", "declared_acquisition"):
        raise ValueError("group_basis must identify a provisional grouping")
    if not isinstance(data["frames"], list) or not data["frames"]:
        raise ValueError("Nonempty frames required")
    if set(quotas) != set(STRATA) or any(
        type(n) is not int or n < 0 for n in quotas.values()
    ) or not any(quotas.values()):
        raise ValueError("Explicit nonnegative A/B/C/D quotas required")
    if type(seed) is not int or type(max_per_group) is not int or max_per_group < 1:
        raise ValueError("Invalid explicit seed or max_per_group")
    seen = set()
    for frame in data["frames"]:
        if not isinstance(frame, dict) or set(frame) != FRAME_KEYS:
            raise ValueError("Invalid frame fields; predictions must not be included")
        for key in ("frame_id", "group_id"):
            if not isinstance(frame[key], str) or not frame[key].strip():
                raise ValueError(f"Nonempty {key} required")
        if frame["frame_id"] in seen:
            raise ValueError("Duplicate frame_id")
        seen.add(frame["frame_id"])
        if frame["qa_state"] not in ("approved", "missing", "flagged"):
            raise ValueError("Invalid qa_state")
        for key in FRAME_KEYS - {"frame_id", "group_id", "qa_state"}:
            if type(frame[key]) is not bool:
                raise ValueError(f"Invalid boolean: {key}")
        if frame["candidate_negative"] and frame["target_positive"]:
            raise ValueError("Candidate negative and positive conflict")
        _frame_stratum(frame)


def plan_sample(data: dict, *, quotas: dict[str, int], seed: int,
                max_per_group: int) -> dict:
    """Return a reproducible sample *plan*, never annotation admission."""
    _check(data, quotas, seed, max_per_group)
    buckets: dict[str, list[dict]] = {key: [] for key in STRATA}
    for frame in data["frames"]:
        buckets[_frame_stratum(frame)].append(frame)
    group_usage: Counter = Counter()
    selected: list[dict] = []
    for stratum in STRATA:
        candidates = sorted(
            buckets[stratum],
            key=lambda frame: (
                hashlib.sha256(
                    f"{seed}\0{data['source_release']}\0{stratum}\0"
                    f"{frame['frame_id']}".encode("utf-8")
                ).hexdigest(), frame["frame_id"]
            ),
        )
        chosen = 0
        for frame in candidates:
            if chosen == quotas[stratum]:
                break
            group_id = frame["group_id"]
            if group_usage[group_id] >= max_per_group:
                continue
            group_usage[group_id] += 1
            chosen += 1
            selected.append({
                "frame_id": frame["frame_id"],
                "group_id": group_id,
                "stratum": stratum,
                "risk_flags": [
                    key for key in ("class_conflict", "geometry_conflict",
                                    "clipped_box", "rider_only", "candidate_negative")
                    if frame[key]
                ] + (["qa_" + frame["qa_state"]]
                     if frame["qa_state"] != "approved" else []),
                "reviewer_a": None,
                "reviewer_b": None,
                "adjudication": None,
            })
    counts = Counter(row["stratum"] for row in selected)
    shortfalls = {key: quotas[key] - counts[key] for key in STRATA}
    canonical = json.dumps(
        sorted(data["frames"], key=lambda row: row["frame_id"]),
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return {
        "schema_version": 1,
        "status": ("SAMPLE_PLAN_INCOMPLETE" if any(shortfalls.values())
                   else "SAMPLE_PLAN_ONLY"),
        "empirical_admission": False,
        "blinded_source_qa_executed": False,
        "source_release": data["source_release"],
        "group_basis": data["group_basis"],
        "group_basis_verified": False,
        "frame_inventory_sha256": hashlib.sha256(canonical).hexdigest(),
        "seed": seed,
        "max_per_group": max_per_group,
        "population_frames": len(data["frames"]),
        "population_groups_declared": len({f["group_id"] for f in data["frames"]}),
        "population_strata": {s: len(buckets[s]) for s in STRATA},
        "quotas": {s: quotas[s] for s in STRATA},
        "selected_strata": {s: counts[s] for s in STRATA},
        "shortfalls": shortfalls,
        "selected_frames": selected,
        "limitations": (
            "Operator-supplied metadata; overlapping risks assigned only once "
            "by A>B>C>D; groups and candidate negatives unverified; "
            "oversampling is not a population prevalence estimator; "
            "two blinded human reviews, adjudication and author-approved "
            "numeric QA criteria are still required."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--max-per-group", type=int, required=True)
    parser.add_argument("--quotas", required=True, help="A=5,B=5,C=5,D=5")
    args = parser.parse_args(argv)
    parts = args.quotas.split(",")
    try:
        quotas = dict(part.split("=") for part in parts)
        if len(parts) != 4:
            raise ValueError("Four explicit quotas required")
        quotas = {key: int(value) for key, value in quotas.items()}
    except (ValueError, TypeError) as exc:
        parser.error(f"Invalid quotas: {exc}")
    raw = args.input.read_bytes()
    if len(raw) > MAX_INPUT_BYTES:
        parser.error("Inventory exceeds 8 MiB")
    data = json.loads(raw, object_pairs_hook=_unique_pairs)
    report = plan_sample(
        data, quotas=quotas, seed=args.seed, max_per_group=args.max_per_group
    )
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
