"""Read-only image-subset audit for duplicate and near-duplicate leakage.

A reported perceptual-hash match is a review candidate, not evidence that
two source scenes are identical. This tool cannot approve data rights or G06.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

import cv2
import numpy as np

from arc_rgbt.admission import _unique_pairs, analyze

MAX_ITEMS = 512
MAX_MANIFEST_BYTES = 8 * 1024 * 1024
MAX_IMAGE_BYTES = 16 * 1024 * 1024
MAX_DECODED_PIXELS = 4_000_000
MAX_CANDIDATES = 200
SUFFIXES = {".png", ".jpg", ".jpeg"}


def _load_json(path: str | Path, limit: int) -> dict:
    source = Path(path)
    if source.stat().st_size > limit:
        raise ValueError("JSON input exceeds configured size limit")
    return json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)


def _local_image(root: Path, name: object) -> Path:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise ValueError("Image path must be a nonempty relative POSIX path")
    candidate = PurePosixPath(name)
    if (candidate.is_absolute() or any(part in {".", "..", ""} for part in name.split("/"))
            or candidate.suffix.lower() not in SUFFIXES):
        raise ValueError(f"Unsafe or unsupported image path: {name!r}")
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Image path escapes declared local image root")
    if not path.is_file():
        raise FileNotFoundError(f"Image absent from local subset: {name}")
    return path


def _fingerprint(path: Path, expected_hash: str) -> str:
    if not 0 < path.stat().st_size <= MAX_IMAGE_BYTES:
        raise ValueError("Image file exceeds 16 MiB or is empty")
    raw = path.read_bytes()
    if path.suffix.lower() == ".png":
        valid_header = raw.startswith(b"\x89PNG\r\n\x1a\n")
    else:
        valid_header = raw.startswith(b"\xff\xd8")
    if not valid_header:
        raise ValueError("Image bytes do not match PNG/JPEG signature")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_hash:
        raise ValueError("Local image SHA-256 does not match admission manifest")
    reduced = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8),
                           cv2.IMREAD_REDUCED_GRAYSCALE_8)
    if reduced is None or reduced.size == 0 or reduced.size > MAX_DECODED_PIXELS:
        raise ValueError("Image cannot be decoded within bounded reduced dimensions")
    # 9*8 is the canonical width/height of a 64-bit horizontal dHash.
    small = cv2.resize(reduced, (9, 8), interpolation=cv2.INTER_AREA)
    bits = small[:, 1:] > small[:, :-1]
    value = 0
    for bit in bits.ravel():
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def analyze_subset(manifest: dict, mapping: dict, root: str | Path,
                   *, max_hamming: int = 4) -> dict:
    """Audit the *local supplied subset* against existing strict source metadata."""
    if type(max_hamming) is not int or not 0 <= max_hamming <= 64:
        raise ValueError("max_hamming must be an integer from 0 to 64")
    analyze(manifest)  # reuse strict schema, source split and duplicate-hash guards
    if not isinstance(mapping, dict) or set(mapping) != {"schema_version", "items"}:
        raise ValueError("Map must contain exactly schema_version and items")
    if type(mapping["schema_version"]) is not int or mapping["schema_version"] != 1:
        raise ValueError("Unsupported image map version")
    items = mapping["items"]
    if not isinstance(items, list) or not 2 <= len(items) <= MAX_ITEMS:
        raise ValueError("Image map must contain 2..512 local images")
    available = {}
    for seq in manifest["sequences"]:
        for frame in seq["frames"]:
            for kind, field in (("rgb", "rgb"), ("thermal", "thermal")):
                key = (seq["id"], kind, frame[f"{field}_id"])
                available[key] = {
                    "sha256": frame[f"{field}_sha256"], "split": seq["split"],
                    "flight_group": seq["flight_group"],
                    "scene_group": seq["scene_group"],
                    "band": seq[kind]["band"],
                }
    records = []
    visited = set()
    file_ids = set()
    root_dir = Path(root).resolve()
    if not root_dir.is_dir():
        raise ValueError("Local image root must be an existing directory")
    for item in items:
        if not isinstance(item, dict) or set(item) != {
            "sequence_id", "modality", "frame_id", "path",
        }:
            raise ValueError("Invalid mapping item fields")
        key = (item["sequence_id"], item["modality"], item["frame_id"])
        if key in visited:
            raise ValueError("Duplicate sequence/modality/frame mapping")
        visited.add(key)
        try:
            evidence = available[key]
        except (KeyError, TypeError) as exc:
            raise ValueError("Mapped frame does not exist in admission manifest") from exc
        image = _local_image(root_dir, item["path"])
        stat = image.stat()
        inode = (stat.st_dev, stat.st_ino)
        if inode in file_ids:
            raise ValueError("Reused local image file or hardlink in mapping")
        file_ids.add(inode)
        records.append({
            "sequence_id": key[0], "frame_id": key[2], "modality": key[1],
            "split": evidence["split"], "flight_group": evidence["flight_group"],
            "scene_group": evidence["scene_group"], "band": evidence["band"],
            "sha256": evidence["sha256"],
            "dhash64": _fingerprint(image, evidence["sha256"]),
        })
    candidates = []
    comparisons = 0
    for i, first in enumerate(records):
        for second in records[i + 1:]:
            if first["split"] == second["split"] or first["band"] != second["band"]:
                continue
            comparisons += 1
            distance = (int(first["dhash64"], 16) ^ int(second["dhash64"], 16)).bit_count()
            if distance <= max_hamming:
                if len(candidates) >= MAX_CANDIDATES:
                    raise ValueError("Too many near-duplicate candidates; reduce the subset")
                candidates.append({
                    "first": {"sequence_id": first["sequence_id"],
                              "frame_id": first["frame_id"], "split": first["split"]},
                    "second": {"sequence_id": second["sequence_id"],
                               "frame_id": second["frame_id"], "split": second["split"]},
                    "band": first["band"], "hamming_distance": distance,
                    "manual_review_required": True,
                })
    return {
        "tool": "arc-rgbt-near-duplicate-audit", "schema_version": 1,
        "data_origin": "local_image_subset_not_approved",
        "images_hashed_and_decoded": len(records),
        "cross_split_same_band_comparisons": comparisons,
        "near_duplicate_candidates": candidates,
        "max_hamming": max_hamming,
        "result": ("REVIEW_REQUIRED" if candidates else "NO_CANDIDATES_IN_SUBSET"),
        "empirical_admission": False, "licence_verified": False,
        "tracking_metric_verified": False,
        "limitations": [
            "Local image bytes were SHA-256 matched to investigator-declared manifest hashes",
            "No independent verification of original archive rights or source identities",
            "dHash is a lossy heuristic; same hash or small distance is NOT proof of same scene",
            "dHash may miss rotations, crops, relighting or temporal near-duplicates",
            "Only local mapped images and cross-split same-band pairs are compared",
            "Potential cross-UAV overlap and source sessions require human review",
            "This check does not establish real-dataset admission or G06 readiness",
        ],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Local admission inventory JSON")
    parser.add_argument("--map", required=True, help="Frame IDs to local image paths JSON")
    parser.add_argument("--root", required=True, help="Root for local read-only image subset")
    parser.add_argument("--max-hamming", type=int, default=4)
    parser.add_argument("--output", help="New JSON report path; no overwrite")
    args = parser.parse_args(argv)
    try:
        manifest = _load_json(args.input, MAX_MANIFEST_BYTES)
        mapping = _load_json(args.map, 1024 * 1024)
        report = analyze_subset(manifest, mapping, args.root,
                                max_hamming=args.max_hamming)
        payload = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(payload)
        print(payload, end="")
    except (ValueError, TypeError, OSError, UnicodeError) as exc:
        parser.exit(1, f"near-duplicates: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
