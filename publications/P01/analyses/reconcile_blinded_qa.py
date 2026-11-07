"""Prepare blinded independent QA sheets and reconcile signed-off decisions.

No images or predictions are read. Agreement is not empirical source admission.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024
FIELDS = (
    "frame_id", "coverage", "target_present", "labels", "boxes",
    "missing_targets", "reason_code",
)
OPTIONS = {
    "coverage": {"complete", "incomplete", "uncertain"},
    "target_present": {"yes", "no", "uncertain"},
    "labels": {"correct", "incorrect", "uncertain"},
    "boxes": {"correct", "incorrect", "uncertain"},
}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
REASON = re.compile(r"[A-Za-z0-9_-]{0,48}\Z")


def _unique_json_pairs(pairs: list[tuple[str, object]]) -> dict:
    record = {}
    for key, value in pairs:
        if key in record:
            raise ValueError(f"Duplicate JSON key: {key}")
        record[key] = value
    return record


def _read_limited(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError("Input exceeds 8 MiB")
    return path.read_bytes()


def _plan(path: Path) -> tuple[dict, str, list[str]]:
    raw = _read_limited(path)
    data = json.loads(raw, object_pairs_hook=_unique_json_pairs)
    if (not isinstance(data, dict) or data.get("schema_version") != 1
            or data.get("status") != "SAMPLE_PLAN_ONLY"
            or data.get("empirical_admission") is not False
            or data.get("blinded_source_qa_executed") is not False
            or not isinstance(data.get("selected_frames"), list)
            or not data["selected_frames"]):
        raise ValueError("Require complete provisional QA sample plan, not admission")
    for field in ("inventory_sha256", "frame_inventory_sha256"):
        if not isinstance(data.get(field), str) or not SHA256.fullmatch(data[field]):
            raise ValueError(f"Invalid {field}")
    selected = data["selected_frames"]
    frame_ids = []
    for item in selected:
        if (not isinstance(item, dict) or not isinstance(item.get("frame_id"), str)
                or not item["frame_id"].strip()
                or item.get("stratum") not in ("A", "B", "C", "D")
                or not isinstance(item.get("risk_flags"), list)):
            raise ValueError("Malformed QA plan frame")
        frame_ids.append(item["frame_id"])
    if len(set(frame_ids)) != len(frame_ids):
        raise ValueError("Duplicate sampled frame IDs")
    return data, hashlib.sha256(raw).hexdigest(), frame_ids


def _order(ids: list[str], digest: str, reviewer: str) -> list[str]:
    return sorted(ids, key=lambda fid: hashlib.sha256(
        json.dumps([digest, reviewer, fid], separators=(",", ":")).encode()
    ).hexdigest())


def prepare(plan_path: Path, reviewer_a: Path, reviewer_b: Path) -> dict:
    """Generate *separate*, annotation-risk-blinded reviewer CSV templates."""
    _, digest, frames = _plan(plan_path)
    paths = (plan_path.resolve(), reviewer_a.resolve(), reviewer_b.resolve())
    if len(set(paths)) != 3:
        raise ValueError("Plan and reviewer paths must differ")
    if reviewer_a.exists() or reviewer_b.exists():
        raise FileExistsError("Reviewer template exists; refusing overwrite")
    # Do not include source labels, QA strata, group IDs or risk flags.
    for name, path in (("A", reviewer_a), ("B", reviewer_b)):
        with path.open("x", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            for frame_id in _order(frames, digest, name):
                writer.writerow({"frame_id": frame_id})
    return {
        "status": "BLINDED_REVIEW_TEMPLATES_ONLY",
        "plan_sha256": digest,
        "sample_frames": len(frames),
        "human_reviews_completed": False,
        "source_admitted": False,
    }


def _read_review(path: Path, expected: set[str]) -> dict[str, dict]:
    raw = _read_limited(path)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Reviewer sheet must be UTF-8") from exc
    from io import StringIO

    reader = csv.DictReader(StringIO(text))
    if reader.fieldnames is None or tuple(reader.fieldnames) != FIELDS:
        raise ValueError("Review sheet columns do not match template")
    result = {}
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Malformed review CSV column count")
        fid = row["frame_id"]
        if fid not in expected or fid in result:
            raise ValueError("Unknown or duplicate reviewer frame ID")
        for field, allowed in OPTIONS.items():
            if row[field] not in allowed:
                raise ValueError(f"Uncompleted or invalid {field} for {fid}")
        if not re.fullmatch(r"(0|[1-9][0-9]{0,4})", row["missing_targets"]):
            raise ValueError(f"Invalid missing_targets for {fid}")
        if REASON.fullmatch(row["reason_code"]) is None:
            raise ValueError("reason_code must be short ASCII code")
        missing = int(row["missing_targets"])
        if row["coverage"] == "complete" and missing:
            raise ValueError("Claim of complete coverage conflicts with missing targets")
        if row["target_present"] == "no" and missing:
            raise ValueError("No-target decision conflicts with missing targets")
        result[fid] = {**row, "missing_targets": missing}
    if set(result) != expected:
        raise ValueError("Reviewer sheets must cover all sampled frames")
    return result


def _verdict(row: dict) -> str:
    if (row["coverage"] == "incomplete" or row["labels"] == "incorrect"
            or row["boxes"] == "incorrect" or row["missing_targets"] > 0):
        return "defect"
    if (row["coverage"] == "complete" and row["target_present"] != "uncertain"
            and row["labels"] == "correct" and row["boxes"] == "correct"):
        return "no_defect_reported"
    return "uncertain"


def reconcile(plan_path: Path, reviewer_a: Path, reviewer_b: Path) -> dict:
    """Check two recorded reviews without granting admission or adjudication."""
    _, digest, ids = _plan(plan_path)
    paths = (plan_path.resolve(), reviewer_a.resolve(), reviewer_b.resolve())
    if len(set(paths)) != 3:
        raise ValueError("Independent reviewers require distinct source files")
    a = _read_review(reviewer_a, set(ids))
    b = _read_review(reviewer_b, set(ids))
    counts = Counter()
    pending = []
    for frame_id in ids:
        first, second = a[frame_id], b[frame_id]
        va, vb = _verdict(first), _verdict(second)
        counts["reviewer_a_" + va] += 1
        counts["reviewer_b_" + vb] += 1
        if va == vb:
            counts["verdict_agreement"] += 1
        else:
            counts["verdict_disagreement"] += 1
        if first["target_present"] == second["target_present"]:
            counts["target_presence_agreement"] += 1
        if any(first[field] != second[field] for field in FIELDS[1:-1]):
            counts["raw_decision_disagreement"] += 1
            pending.append({"frame_id": frame_id, "reason": "reviewer_disagreement"})
        elif va == "uncertain" or vb == "uncertain":
            counts["uncertain_consensus"] += 1
            pending.append({"frame_id": frame_id, "reason": "uncertain_unresolved"})
        elif va == "defect":
            counts["concordant_defects"] += 1
            pending.append({"frame_id": frame_id, "reason": "defect_adjudication_required"})
    return {
        "schema_version": 1,
        "status": "MANUAL_ADJUDICATION_REQUIRED" if pending
                  else "REVIEW_RECORDS_COLLECTED_NOT_ADMITTED",
        "plan_sha256": digest,
        "reviewer_a_sha256": hashlib.sha256(_read_limited(reviewer_a)).hexdigest(),
        "reviewer_b_sha256": hashlib.sha256(_read_limited(reviewer_b)).hexdigest(),
        "sample_frames": len(ids),
        "verdict_agreement_rate": counts["verdict_agreement"] / len(ids),
        "counts": dict(counts),
        "pending_adjudication": pending,
        "independence_of_reviewers_verified": False,
        "blinded_review_provenance_verified": False,
        "numeric_quality_gate_frozen": False,
        "source_admitted": False,
        "confirmatory_fp_frame_status": "BLOCKED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "reconcile"))
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.action == "prepare":
        if args.output is not None:
            parser.error("prepare does not use --output")
        report = prepare(args.plan, args.reviewer_a, args.reviewer_b)
    else:
        if args.output is None:
            parser.error("reconcile requires --output")
        if args.output.resolve() in {args.plan.resolve(),
                                     args.reviewer_a.resolve(),
                                     args.reviewer_b.resolve()}:
            parser.error("Output must differ from input files")
        if args.output.exists():
            parser.error("Output exists; refusing overwrite")
        report = reconcile(args.plan, args.reviewer_a, args.reviewer_b)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print(json.dumps({k: report[k] for k in ("status", "sample_frames",
                                              "source_admitted")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
