"""Deterministic *proposed* scene/flight-disjoint split assignment.

Uses declared metadata only. No source images, near-duplicate fingerprints or
dataset licences are inspected; this never constitutes dataset admission.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from copy import deepcopy

from arc_rgbt.admission import analyze

SPLITS = ("train", "validation", "test")


def propose_splits(
    manifest: dict, *, seed: int = 17,
    proportions: tuple[float, float, float] = (0.7, 0.15, 0.15),
    device_disjoint: bool = False,
) -> dict:
    """Assign connected acquisition groups, without changing the input manifest.

    Components join sequences sharing a flight or scene; device_disjoint=True
    additionally joins all sequences from the same device. An input manifest
    with pre-existing split leakage is rejected by the shared admission audit.
    """
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must be an unsigned 32-bit integer")
    if type(device_disjoint) is not bool:
        raise ValueError("device_disjoint must be boolean")
    if (not isinstance(proportions, (list, tuple)) or len(proportions) != 3
            or any(type(p) not in (int, float) or not math.isfinite(p) or p <= 0
                   for p in proportions)
            or not math.isclose(sum(proportions), 1.0, abs_tol=1e-9, rel_tol=0)):
        raise ValueError("proportions must be three positive numbers summing to 1")
    # Reuse the existing strict schema, duplication and leakage checks.
    analyze(manifest)
    entries = manifest["sequences"]
    count = len(entries)
    parent = list(range(count))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        parent[find(a)] = find(b)

    seen: dict[tuple[str, str], int] = {}
    for i, seq in enumerate(entries):
        fields = ("flight_group", "scene_group", "device_id") if device_disjoint else (
            "flight_group", "scene_group",
        )
        for field in fields:
            key = (field, seq[field])
            if key in seen:
                union(i, seen[key])
            else:
                seen[key] = i

    components: dict[int, list[int]] = {}
    for i in range(count):
        components.setdefault(find(i), []).append(i)
    groups = list(components.values())
    if len(groups) < 3:
        raise ValueError("At least three independent acquisition groups are required")

    # Allocating a minimum of one group to each split is explicit. Remaining
    # quotas favor the largest deficit against the requested group proportions.
    quotas = {split: 1 for split in SPLITS}
    while sum(quotas.values()) < len(groups):
        selected = max(SPLITS, key=lambda s: (
            proportions[SPLITS.index(s)] * len(groups) - quotas[s],
            -SPLITS.index(s),
        ))
        quotas[selected] += 1

    def stable_key(group: list[int]) -> str:
        identifiers = sorted(entries[i]["id"] for i in group)
        material = json.dumps([seed, identifiers], ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    ordered = sorted(groups, key=lambda group: (stable_key(group),
                                               tuple(sorted(entries[i]["id"] for i in group))))
    assignments: dict[str, str] = {}
    split_counts = Counter()
    position = 0
    for name in SPLITS:
        for group in ordered[position:position + quotas[name]]:
            for i in group:
                seq = entries[i]
                assignments[seq["id"]] = name
                split_counts[f"{name}_frames"] += len(seq["frames"])
                split_counts[f"{name}_sequences"] += 1
        position += quotas[name]

    proposed = deepcopy(manifest)
    for seq in proposed["sequences"]:
        seq["split"] = assignments[seq["id"]]
    # Independently reuse the canonical guard on the proposal.
    analyze(proposed)
    return {
        "tool": "arc-rgbt-split-plan", "schema_version": 1,
        "data_origin": "metadata_only", "source_dataset": manifest["dataset"]["id"],
        "seed": seed, "device_disjoint": device_disjoint,
        "requested_group_proportions": dict(zip(SPLITS, proportions, strict=True)),
        "component_count": len(groups), "group_quotas": quotas,
        "split_sequence_counts": {name: split_counts[f"{name}_sequences"] for name in SPLITS},
        "split_frame_counts": {name: split_counts[f"{name}_frames"] for name in SPLITS},
        "assignments": {key: assignments[key] for key in sorted(assignments)},
        "structural_validation": "PASS", "empirical_admission": False,
        "limitations": [
            "Group labels and hashes are source declarations and not independently checked",
            "Split quotas count connected acquisition groups, not frame count or class prevalence",
            "Actual near-duplicates, cross-UAV overlap and device provenance require source inspection",
            "A proposed split is not an empirical benchmark or licensing approval",
        ],
    }


def main(argv: list[str] | None = None) -> None:
    """Produce a proposal report, preserving source manifest bytes."""
    import argparse
    from pathlib import Path

    from arc_rgbt.admission import MAX_MANIFEST_BYTES, _unique_pairs

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Existing metadata-only JSON manifest")
    parser.add_argument("--seed", type=int, default=17, help="Unsigned 32-bit seed")
    parser.add_argument("--proportions", type=float, nargs=3, default=(0.7, 0.15, 0.15),
                        metavar=("TRAIN", "VAL", "TEST"))
    parser.add_argument("--device-disjoint", action="store_true")
    parser.add_argument("--output", help="Optional new JSON report (no overwrite)")
    args = parser.parse_args(argv)
    try:
        path = Path(args.input)
        if path.stat().st_size > MAX_MANIFEST_BYTES:
            raise ValueError("Manifest exceeds 8 MiB")
        manifest = json.loads(path.read_text(encoding="utf-8"),
                              object_pairs_hook=_unique_pairs)
        result = propose_splits(
            manifest, seed=args.seed, proportions=args.proportions,
            device_disjoint=args.device_disjoint,
        )
        output = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as handle:
                handle.write(output)
        print(output, end="")
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(1, f"split: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
