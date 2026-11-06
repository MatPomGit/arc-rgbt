"""Count P01 candidate acquisition support from local, non-test metadata only.

This tool never opens images, annotations, predictions or held-out outcomes.
Counts and declarations must not be promoted to empirical source admission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import median

MAX_INPUT_BYTES = 8 * 1024 * 1024
SPLITS = ("train", "validation")
COUNTS = ("small", "intermediate", "reference")
STATES = ("candidate_positive", "candidate_negative", "unknown")
FRAME_KEYS = {
    "frame_id", "group_id", "split", "target_state", "small",
    "intermediate", "reference", "viewpoint", "contrast",
}
TOP_KEYS = {"schema_version", "source_release", "group_basis", "grid_basis", "frames"}


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _validate(inventory: dict) -> None:
    if not isinstance(inventory, dict) or set(inventory) != TOP_KEYS:
        raise ValueError("Invalid inventory fields")
    if type(inventory["schema_version"]) is not int or inventory["schema_version"] != 1:
        raise ValueError("Unsupported schema_version")
    source = inventory["source_release"]
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Nonempty source_release required")
    if inventory["group_basis"] not in ("video_id_proxy", "declared_acquisition"):
        raise ValueError("Invalid group_basis")
    if inventory["grid_basis"] not in ("export_grid_proxy", "declared_native", "unknown"):
        raise ValueError("Invalid grid_basis")
    frames = inventory["frames"]
    if not isinstance(frames, list) or not frames:
        raise ValueError("Nonempty frames required")
    seen = set()
    for frame in frames:
        if not isinstance(frame, dict) or set(frame) != FRAME_KEYS:
            raise ValueError("Invalid frame fields: no predictions or outcomes allowed")
        for key in ("frame_id", "group_id", "viewpoint", "contrast"):
            value = frame[key]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Nonempty {key} required")
        if frame["frame_id"] in seen:
            raise ValueError("Duplicate frame_id")
        seen.add(frame["frame_id"])
        if frame["split"] not in SPLITS:
            raise ValueError("Only train and validation metadata permitted; no test split")
        if frame["target_state"] not in STATES:
            raise ValueError("Invalid target_state")
        counts = [frame[key] for key in COUNTS]
        if frame["target_state"] == "unknown":
            if any(value is not None for value in counts):
                raise ValueError("Unknown target_state requires null bin counts")
        else:
            if any(type(value) is not int or value < 0 for value in counts):
                raise ValueError("Candidate bin counts must be nonnegative integers")
            if frame["target_state"] == "candidate_negative" and any(counts):
                raise ValueError("Candidate negative cannot contain candidate targets")
            if frame["target_state"] == "candidate_positive" and not any(counts):
                raise ValueError("Candidate positive needs at least one target")
            if inventory["grid_basis"] == "unknown" and any(counts):
                raise ValueError("Unknown grid_basis cannot support footprint bins")


def _range(values: list[int]) -> dict | None:
    return ({"min": min(values), "median": median(values), "max": max(values)}
            if values else None)


def assess(inventory: dict) -> dict:
    """Summarize operator-declared candidate support; always scientifically blocked."""
    _validate(inventory)
    frames = inventory["frames"]
    by_split = defaultdict(list)
    group_splits = defaultdict(set)
    for frame in frames:
        by_split[frame["split"]].append(frame)
        group_splits[frame["group_id"]].add(frame["split"])
    crossing = {group for group, splits in group_splits.items() if len(splits) > 1}
    per_split = {}
    for split in SPLITS:
        rows = by_split[split]
        groups = defaultdict(list)
        for frame in rows:
            groups[frame["group_id"]].append(frame)
        paired = []
        pure_negatives = 0
        negative_groups = 0
        unknown_groups = 0
        viewpoint_unknown = 0
        contrast_unknown = 0
        joint_condition_support = 0
        for group_rows in groups.values():
            small = sum(row["small"] or 0 for row in group_rows)
            reference = sum(row["reference"] or 0 for row in group_rows)
            if small > 0 and reference > 0:
                paired.append((small, reference))
                # Candidate overlap, not standardized confounder control.
                # Skip missing categories rather than treating "unknown"
                # as an eligible shared condition.
                cells = defaultdict(lambda: [0, 0])
                for row in group_rows:
                    if "unknown" in (row["viewpoint"], row["contrast"]):
                        continue
                    cell = cells[(row["viewpoint"], row["contrast"])]
                    cell[0] += row["small"] or 0
                    cell[1] += row["reference"] or 0
                if any(min(cell) > 0 for cell in cells.values()):
                    joint_condition_support += 1
            if all(row["target_state"] == "candidate_negative" for row in group_rows):
                pure_negatives += 1
            if any(row["target_state"] == "candidate_negative" for row in group_rows):
                negative_groups += 1
            if any(row["target_state"] == "unknown" for row in group_rows):
                unknown_groups += 1
            if any(row["viewpoint"] == "unknown" for row in group_rows):
                viewpoint_unknown += 1
            if any(row["contrast"] == "unknown" for row in group_rows):
                contrast_unknown += 1
        per_split[split] = {
            "frames": len(rows),
            "groups_declared": len(groups),
            "target_state_counts": dict(
                (state, sum(row["target_state"] == state for row in rows))
                for state in STATES
            ),
            "candidate_bin_counts": {
                bin_name: sum(row[bin_name] or 0 for row in rows)
                for bin_name in COUNTS
            },
            "groups_with_both_candidate_bins": len(paired),
            "paired_groups_with_known_joint_viewpoint_contrast_support": (
                joint_condition_support
            ),
            "groups_with_at_least_two_per_primary_bin": sum(
                min(small, reference) >= 2 for small, reference in paired
            ),
            "paired_small_targets_per_group": _range([v[0] for v in paired]),
            "paired_reference_targets_per_group": _range([v[1] for v in paired]),
            "groups_with_candidate_negatives": negative_groups,
            "groups_only_candidate_negative": pure_negatives,
            "groups_with_unknown_frames": unknown_groups,
            "groups_missing_viewpoint": viewpoint_unknown,
            "groups_missing_contrast": contrast_unknown,
        }
    canonical = json.dumps(
        {**inventory, "frames": sorted(frames, key=lambda row: row["frame_id"])},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return {
        "schema_version": 1,
        "status": ("BLOCKED_SPLIT_GROUP_OVERLAP" if crossing
                   else "PROVISIONAL_METADATA_ONLY"),
        "empirical_admission": False,
        "independent_acquisitions_verified": False,
        "native_footprint_verified": False,
        "scientific_sample_size_approved": False,
        "heldout_outcomes_processed_by_tool": False,
        "source_release": inventory["source_release"],
        "group_basis": inventory["group_basis"],
        "grid_basis": inventory["grid_basis"],
        "input_inventory_sha256": hashlib.sha256(canonical).hexdigest(),
        "frames_total": len(frames),
        "groups_declared_total": len(group_splits),
        "groups_declared_in_multiple_splits": len(crossing),
        "per_split": per_split,
        "limitations": (
            "All counts derive from an operator-supplied pre-test inventory. "
            "Candidate negatives do not prove exhaustive annotations; "
            "declared native grids and group IDs are unverified. "
            "Group overlaps prevent split-disjointness even on declared IDs. "
            "No sample-size sufficiency, inference, independent acquisitions "
            "or source-admission GO is established."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.input.stat().st_size > MAX_INPUT_BYTES:
        parser.error("Metadata inventory exceeds 8 MiB")
    data = json.loads(args.input.read_text(encoding="utf-8"),
                      object_pairs_hook=_unique_pairs)
    report = assess(data)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
