"""Offline admission *metadata* validator (no images, GT archive or models are opened).

A structural PASS does not approve dataset rights, exposure calibration or empirical research.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

MAX_MANIFEST_BYTES = 8 * 1024 * 1024
MAX_SEQUENCES = 2000
MAX_FRAMES = 50000
MAX_OBJECTS_PER_FRAME = 256
MAX_DIMENSION = 16384
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _exact(value: object, names: set[str], where: str) -> dict:
    if not isinstance(value, dict) or set(value) != names:
        raise ValueError(f"{where}: required fields {sorted(names)}")
    return value


def _ident(value: object, where: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 128 or not value.strip():
        raise ValueError(f"{where}: expected nonempty string (max 128 characters)")
    if any(ord(c) < 32 for c in value):
        raise ValueError(f"{where}: control characters are not allowed")
    return value


def _hash(value: object, where: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        raise ValueError(f"{where}: expected lowercase SHA-256 hex")
    return value


def _grid(value: object, where: str) -> tuple[int, int]:
    if (not isinstance(value, list) or len(value) != 2
            or any(type(x) is not int or not 1 <= x <= MAX_DIMENSION for x in value)):
        raise ValueError(f"{where}: expected integer [width,height] in 1..16384")
    return value[0], value[1]


def _url(value: object, where: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{where}: expected HTTPS URL")
    u = urlsplit(value)
    if u.scheme != "https" or not u.hostname or u.username or u.password:
        raise ValueError(f"{where}: expected HTTPS source without credentials")


def _modality(value: object, kind: str) -> tuple[int, int]:
    item = _exact(
        value, {"band", "native_grid_wh", "processed_grid_wh", "grid_origin"},
        kind,
    )
    bands = {"rgb"} if kind == "rgb" else {"lwir", "nir", "unverified_ir"}
    if item["band"] not in bands:
        raise ValueError(f"{kind}.band: invalid spectral band")
    _grid(item["native_grid_wh"], f"{kind}.native_grid_wh")
    grid = _grid(item["processed_grid_wh"], f"{kind}.processed_grid_wh")
    if item["grid_origin"] not in {"original_native", "aligned_crop", "unknown"}:
        raise ValueError(f"{kind}.grid_origin: invalid source provenance")
    if (item["grid_origin"] == "original_native"
            and item["native_grid_wh"] != item["processed_grid_wh"]):
        raise ValueError(f"{kind}: original_native cannot change image grid")
    return grid


def _bbox(value: object, grid: tuple[int, int], where: str) -> None:
    if (not isinstance(value, list) or len(value) != 4
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in value)):
        raise ValueError(f"{where}: bbox must be four finite [x,y,width,height] values")
    x, y, w, h = value
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > grid[0] or y + h > grid[1]:
        raise ValueError(f"{where}: bbox outside declared processed modality grid")


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def analyze(manifest: dict, *, manifest_sha256: str | None = None) -> dict:
    """Validate a bounded inventory; never access the declared image/annotation files."""
    _exact(manifest, {"schema_version", "data_origin", "dataset", "sequences"}, "root")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    if manifest["data_origin"] != "metadata_only":
        raise ValueError("data_origin must be metadata_only (not measured evidence)")

    info = _exact(manifest["dataset"], {
        "id", "release", "owner_url", "licence_url", "rights_status", "archive_sha256",
    }, "dataset")
    dataset_id = _ident(info["id"], "dataset.id")
    _ident(info["release"], "dataset.release")
    _url(info["owner_url"], "dataset.owner_url")
    if info["licence_url"] is not None:
        _url(info["licence_url"], "dataset.licence_url")
    if info["rights_status"] not in {
        "needs_review", "owner_terms_identified", "independently_reviewed",
    }:
        raise ValueError("dataset.rights_status: unsupported review category")
    _hash(info["archive_sha256"], "dataset.archive_sha256", nullable=True)

    sequences = manifest["sequences"]
    if not isinstance(sequences, list) or not 1 <= len(sequences) <= MAX_SEQUENCES:
        raise ValueError("sequences: expected 1..2000 entries")
    seen_sequences: set[str] = set()
    groups: dict[tuple[str, str], str] = {}
    image_hashes: set[str] = set()
    counts = Counter()
    bands = set()
    track_gaps = 0
    for seq in sequences:
        _exact(seq, {
            "id", "flight_group", "scene_group", "device_id", "split",
            "rgb", "thermal", "pairing_origin", "exposure_clock", "frames",
        }, "sequence")
        seq_id = _ident(seq["id"], "sequence.id")
        if seq_id in seen_sequences:
            raise ValueError(f"Duplicate sequence ID: {seq_id}")
        seen_sequences.add(seq_id)
        if seq["split"] not in {"train", "validation", "test"}:
            raise ValueError(f"{seq_id}: unsupported split")
        for field in ("flight_group", "scene_group"):
            name = _ident(seq[field], f"{seq_id}.{field}")
            key = (field, name)
            prior = groups.setdefault(key, seq["split"])
            if prior != seq["split"]:
                raise ValueError(f"Split leakage: {field}={name} spans {prior} and "
                                 f"{seq['split']}")
        _ident(seq["device_id"], f"{seq_id}.device_id")
        rgb_grid = _modality(seq["rgb"], "rgb")
        thermal_grid = _modality(seq["thermal"], "thermal")
        bands.add(seq["thermal"]["band"])
        if seq["pairing_origin"] not in {"manual", "declared_clock", "unknown"}:
            raise ValueError(f"{seq_id}: pairing_origin invalid")
        if seq["exposure_clock"] not in {"unknown", "declared_only"}:
            raise ValueError(f"{seq_id}: clock verification is external, not automatic")
        frames = seq["frames"]
        if not isinstance(frames, list) or not frames:
            raise ValueError(f"{seq_id}: nonempty frames required")
        counts["frames"] += len(frames)
        if counts["frames"] > MAX_FRAMES:
            raise ValueError(f"Manifest exceeds {MAX_FRAMES} frame pairs")
        frame_ids: set[str] = set()
        rgb_ids: set[str] = set()
        thermal_ids: set[str] = set()
        last_index = -1
        last_tracks: dict[tuple[str, str], int] = {}
        for frame in frames:
            _exact(frame, {
                "pair_id", "frame_index", "rgb_id", "thermal_id", "rgb_sha256",
                "thermal_sha256", "annotation_status", "objects",
            }, f"{seq_id}.frame")
            pair_id = _ident(frame["pair_id"], "frame.pair_id")
            rgb_id = _ident(frame["rgb_id"], "frame.rgb_id")
            thermal_id = _ident(frame["thermal_id"], "frame.thermal_id")
            if pair_id in frame_ids or rgb_id in rgb_ids or thermal_id in thermal_ids:
                raise ValueError(f"{seq_id}: duplicate paired or modality frame ID")
            frame_ids.add(pair_id)
            rgb_ids.add(rgb_id)
            thermal_ids.add(thermal_id)
            index = frame["frame_index"]
            if type(index) is not int or not 0 <= index <= 2**63 - 1 or index <= last_index:
                raise ValueError(f"{seq_id}: frame_index must strictly increase")
            last_index = index
            for name in ("rgb_sha256", "thermal_sha256"):
                digest = _hash(frame[name], name)
                if digest in image_hashes:
                    raise ValueError(f"Duplicate image SHA-256: {digest}")
                image_hashes.add(digest)
            if frame["annotation_status"] not in {"complete", "partial", "unknown"}:
                raise ValueError(f"{seq_id}: annotation_status invalid")
            if frame["annotation_status"] != "complete":
                counts["incomplete_or_unknown_labels"] += 1
            objects = frame["objects"]
            if not isinstance(objects, list) or len(objects) > MAX_OBJECTS_PER_FRAME:
                raise ValueError(f"{seq_id}: too many or malformed objects")
            this_tracks: set[tuple[str, str]] = set()
            for obj in objects:
                _exact(obj, {"modality", "track_id", "label", "bbox_xywh"},
                       f"{seq_id}.object")
                modality = obj["modality"]
                if modality not in {"rgb", "thermal"}:
                    raise ValueError(f"{seq_id}: object modality must be rgb or thermal")
                identity = (modality, _ident(obj["track_id"], "object.track_id"))
                if identity in this_tracks:
                    raise ValueError(f"{seq_id}: duplicate track ID in the same frame")
                this_tracks.add(identity)
                _ident(obj["label"], "object.label")
                _bbox(obj["bbox_xywh"], rgb_grid if modality == "rgb" else thermal_grid,
                      f"{seq_id}.{pair_id}.{modality}")
                if identity in last_tracks and index - last_tracks[identity] > 1:
                    track_gaps += 1
                last_tracks[identity] = index
                counts["objects"] += 1
            counts["pairs_with_annotations"] += bool(objects)
            counts[f"{seq['split']}_pairs"] += 1
        counts["sequences"] += 1

    return {
        "tool": "arc-rgbt-admission", "schema_version": 1,
        "data_origin": "metadata_only",
        "manifest_sha256": manifest_sha256,
        "dataset_id": dataset_id,
        "rights_status_declared": info["rights_status"],
        "structural_validation": "PASS",
        "empirical_admission": False,
        "source_image_accessed": False,
        "source_annotations_independently_verified": False,
        "exposure_clock_verified": False,
        "counts": {
            "sequences": counts["sequences"],
            "paired_frames": counts["frames"],
            "objects": counts["objects"],
            "pairs_with_annotations": counts["pairs_with_annotations"],
            "incomplete_or_unknown_labels": counts["incomplete_or_unknown_labels"],
            "train_pairs": counts["train_pairs"],
            "validation_pairs": counts["validation_pairs"],
            "test_pairs": counts["test_pairs"],
            "track_gaps_to_review": track_gaps,
            "unique_image_hashes": len(image_hashes),
        },
        "thermal_bands_declared": sorted(bands),
        "limitations": [
            "Inventory assertions and hashes are declarations, not checked source files",
            "Image hashes are deduplicated but never independently recomputed",
            "Manual pairing is not hardware exposure-clock synchronization",
            "Track gaps can be legitimate occlusions, not proven ID errors",
            "Frame track IDs are modality-local; cross-modal identity is not established",
            "Structural PASS never proves rights, labels, native optics, or admission",
            "HOTA, AP, detector accuracy, and physical measurements are not computed",
        ],
    }


def run(input_path: str | Path) -> dict:
    source = Path(input_path)
    if source.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("Metadata inventory exceeds 8 MiB")
    raw = source.read_bytes()
    manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    return analyze(manifest, manifest_sha256=hashlib.sha256(raw).hexdigest())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Existing local JSON metadata inventory")
    parser.add_argument("--output", help="Optional *new* JSON report path (never overwrite)")
    args = parser.parse_args(argv)
    try:
        report = run(args.input)
        payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(payload)
        print(payload, end="")
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(1, f"admission: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
