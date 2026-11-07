"""Build a candidate annotation-QA inventory from FLIR ADAS v2 metadata.

Only thermal train or validation COCO and Conservator JSON are read.
No test annotations, images, detector outputs or G01 admission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import zipfile
from bisect import bisect_right
from collections import Counter, defaultdict
from itertools import accumulate
from pathlib import Path

MAX_JSON_BYTES = 200 * 1024 * 1024
TARGET_CLASS_MAP = {"person": frozenset({"person", "rider"}),
                    "car": frozenset({"car"})}


class JoinedParts:
    """Seekable read-only ZIP stream over the official twelve archive chunks."""

    def __init__(self, parts: list[Path]) -> None:
        if len(parts) != 12:
            raise ValueError("Exactly twelve FLIR ADAS v2 parts are required")
        for i, part in enumerate(parts):
            if part.name != f"FLIR_ADAS_v2.zip.{i:02d}" or not part.is_file():
                raise ValueError(f"Missing archive part {i:02d}")
        self.parts = parts
        self.ends = list(accumulate(part.stat().st_size for part in parts))
        if any(self.ends[i] == (self.ends[i - 1] if i else 0)
               for i in range(len(parts))):
            raise ValueError("Empty ZIP archive part")
        self.pos = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence not in (0, 1, 2):
            raise ValueError("Invalid seek mode")
        self.pos = (0, self.pos, self.ends[-1])[whence] + offset
        if not 0 <= self.pos <= self.ends[-1]:
            raise ValueError("Archive offset out of range")
        return self.pos

    def read(self, size: int = -1) -> bytes:
        size = self.ends[-1] - self.pos if size < 0 else size
        chunks = []
        while size > 0 and self.pos < self.ends[-1]:
            i = bisect_right(self.ends, self.pos)
            start = self.ends[i - 1] if i else 0
            count = min(size, self.ends[i] - self.pos)
            with self.parts[i].open("rb") as part:
                part.seek(self.pos - start)
                block = part.read(count)
            if len(block) != count:
                raise OSError("Unexpected truncated archive part")
            chunks.append(block)
            self.pos += count
            size -= count
        return b"".join(chunks)


def _unique_json_keys(pairs: list[tuple[str, object]]) -> dict:
    """Refuse JSON with ambiguous repeated keys in source annotations."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _json_entry(z: zipfile.ZipFile, name: str) -> tuple[dict, str]:
    if sum(item.filename == name for item in z.infolist()) != 1:
        raise ValueError(f"Missing or duplicate ZIP metadata entry: {name}")
    info = z.getinfo(name)
    if info.file_size > MAX_JSON_BYTES:
        raise ValueError("Annotation JSON exceeds the 200 MiB limit")
    raw = z.read(name)  # CRC checked by zipfile for selected JSON entry
    doc = json.loads(raw, object_pairs_hook=_unique_json_keys)
    if not isinstance(doc, dict):
        raise ValueError("Expected JSON annotation object")
    return doc, hashlib.sha256(raw).hexdigest()


def _rect(box: object) -> tuple[float, float, float, float]:
    if isinstance(box, dict):
        try:
            coords = (box["x"], box["y"], box["w"], box["h"])
        except KeyError as exc:
            raise ValueError("Missing original bbox coordinate") from exc
    elif isinstance(box, list) and len(box) == 4:
        coords = tuple(box)
    else:
        raise ValueError("Invalid bounding box structure")
    if any(type(value) not in (int, float) or not math.isfinite(value)
           for value in coords):
        raise ValueError("Nonfinite or nonnumeric bbox")
    x, y, w, h = map(float, coords)
    if w <= 0 or h <= 0:
        raise ValueError("Nonpositive bbox dimensions")
    return x, y, w, h


def _iou(a: tuple, b: tuple) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    overlap = max(0, min(ax + aw, bx + bw) - max(ax, bx)) * max(
        0, min(ay + ah, by + bh) - max(ay, by)
    )
    union = aw * ah + bw * bh - overlap
    return overlap / union if union else 0.0


def _same_boxes(original: list[tuple], exported: list[tuple]) -> bool:
    """Conservative IoU >= .95 matching, for a risk flag only."""
    if len(original) != len(exported):
        return False
    pairs = sorted(
        ((_iou(a, b), i, j) for i, a in enumerate(original)
         for j, b in enumerate(exported)), reverse=True
    )
    matched_a: set[int] = set()
    matched_b: set[int] = set()
    for overlap, i, j in pairs:
        if overlap < 0.95:
            break
        if i not in matched_a and j not in matched_b:
            matched_a.add(i)
            matched_b.add(j)
    return len(matched_a) == len(original)


def _coco_key(image: dict) -> tuple[str, int]:
    extra = image.get("extra_info")
    if not isinstance(extra, dict) or not isinstance(extra.get("video_id"), str):
        raise ValueError("Missing COCO video_id")
    match = re.search(r"(?:^|/)video-(.+?)-frame-(\d+)-",
                      str(image.get("file_name", "")))
    if match is None or match.group(1) != extra["video_id"]:
        raise ValueError("COCO filename/video_id mismatch")
    return extra["video_id"], int(match.group(2))


def _index_key(frame: dict) -> tuple[str, int]:
    meta = frame.get("videoMetadata")
    if not isinstance(meta, dict) or not isinstance(meta.get("videoId"), str):
        raise ValueError("Missing original videoMetadata")
    number = meta.get("frameIndex")
    if type(number) is not int:
        raise ValueError("Invalid original frame index")
    return meta["videoId"], number


def _unique(items: list[dict], key_fn) -> dict:
    result = {}
    for item in items:
        key = key_fn(item)
        if key in result:
            raise ValueError(f"Duplicate frame key: {key}")
        result[key] = item
    return result


def build_inventory(index: dict, coco: dict, *, split: str, target: str,
                    index_sha: str, coco_sha: str) -> tuple[dict, dict]:
    """Prepare risk flags and candidate negatives; never verify completeness."""
    if split not in ("train", "val") or target not in TARGET_CLASS_MAP:
        raise ValueError("Only train/val and person/car supported")
    if not isinstance(index.get("frames"), list) or not isinstance(coco.get("images"), list):
        raise ValueError("Missing frame/image arrays")
    categories = {c.get("id"): c.get("name") for c in coco.get("categories", [])}
    ids = [cid for cid, name in categories.items() if name == target]
    if len(ids) != 1:
        raise ValueError(f"Exactly one COCO category required for {target}")
    cid = ids[0]
    original = _unique(index["frames"], _index_key)
    exported = _unique(coco["images"], _coco_key)
    if set(original) != set(exported):
        raise ValueError("Unmatched train/validation frame identities")
    image_ids = [image.get("id") for image in coco["images"]]
    if len(set(image_ids)) != len(image_ids):
        raise ValueError("Duplicate COCO image ID")
    image_set = set(image_ids)
    by_image: dict[object, list[dict]] = defaultdict(list)
    seen_annotations = set()
    for annotation in coco.get("annotations", []):
        annotation_id = annotation.get("id")
        if annotation_id in seen_annotations:
            raise ValueError("Duplicate COCO annotation ID")
        seen_annotations.add(annotation_id)
        image_id = annotation.get("image_id")
        if image_id not in image_set:
            raise ValueError("Orphaned COCO annotation")
        by_image[image_id].append(annotation)

    records = []
    counters: Counter = Counter()
    classes = TARGET_CLASS_MAP[target]
    for (vid, number), image in sorted(exported.items()):
        frame = original[(vid, number)]
        if image.get("width") != frame.get("width") or image.get("height") != frame.get("height"):
            raise ValueError("COCO and original image dimensions differ")
        width, height = image["width"], image["height"]
        if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
            raise ValueError("Invalid image dimensions")
        raw_annotations = frame.get("annotations")
        if not isinstance(raw_annotations, list):
            raise ValueError("Missing original annotations")
        if type(frame.get("isEmpty")) is not bool or frame["isEmpty"] != (len(raw_annotations) == 0):
            raise ValueError("Original isEmpty conflicts with annotations or is missing")
        if type(frame.get("isFlagged")) is not bool:
            raise ValueError("Original isFlagged is not boolean")
        boxes_original = []
        original_labels = Counter()
        clipped = False
        for annotation in raw_annotations:
            if not isinstance(annotation, dict):
                raise ValueError("Invalid original annotation")
            box = _rect(annotation.get("boundingBox"))
            if (box[0] < 0 or box[1] < 0 or box[0] + box[2] > width
                    or box[1] + box[3] > height):
                clipped = True
            labels = annotation.get("labels")
            if not isinstance(labels, list) or any(not isinstance(label, str)
                                                    for label in labels):
                raise ValueError("Invalid original labels")
            original_labels.update(labels)
            if classes.intersection(labels):
                boxes_original.append(box)

        boxes_coco = []
        for annotation in by_image.get(image["id"], []):
            box = _rect(annotation.get("bbox"))
            if (box[0] < 0 or box[1] < 0 or box[0] + box[2] > width
                    or box[1] + box[3] > height):
                clipped = True
            if annotation.get("category_id") == cid:
                boxes_coco.append(box)

        state = frame.get("qaStatus")
        if state not in (None, "approved"):
            raise ValueError("Unexpected original QA status; inspect source manually")
        qa_state = ("flagged" if frame.get("isFlagged") is True else
                    "approved" if state == "approved" else "missing")
        class_conflict = len(boxes_original) != len(boxes_coco)
        candidate_negative = not boxes_original and not boxes_coco
        record = {
            "frame_id": f"{split}:{vid}:{number}", "group_id": vid,
            "qa_state": qa_state, "class_conflict": class_conflict,
            "geometry_conflict": not class_conflict and not _same_boxes(
                boxes_original, boxes_coco
            ),
            "clipped_box": clipped,
            "rider_only": (target == "person" and original_labels["rider"] > 0
                           and original_labels["person"] == 0),
            "candidate_negative": candidate_negative,
            "target_positive": not candidate_negative,
        }
        records.append(record)
        for field in ("class_conflict", "geometry_conflict", "clipped_box", "rider_only",
                      "candidate_negative", "target_positive"):
            counters[field] += int(record[field])
        counters["qa_" + qa_state] += 1

    release = f"FLIR_ADAS_v2:{split}:{target}:index={index_sha}:coco={coco_sha}"
    inventory = {"schema_version": 1, "source_release": release,
                 "group_basis": "video_id_proxy", "frames": records}
    summary = {"split": split, "target": target, "population_frames": len(records),
               "video_id_groups_proxy": len({record["group_id"] for record in records}),
               "risk_counts": dict(counters), "annotation_completeness": "UNKNOWN",
               "source_rights_verified": False, "native_grid_verified": False,
               "empirical_admission": False, "test_annotations_inspected": False}
    return inventory, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive_dir", type=Path)
    parser.add_argument("--split", choices=("train", "val"), default="val")
    parser.add_argument("--target", choices=("person", "car"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan-output", type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--max-per-group", type=int)
    parser.add_argument("--quotas", help="A=5,B=5,C=5,D=5; example only")
    args = parser.parse_args(argv)
    if args.output.exists() or (args.plan_output and args.plan_output.exists()):
        parser.error("Output exists; refusing overwrite")
    if args.plan_output and args.output.resolve() == args.plan_output.resolve():
        parser.error("Inventory and plan output paths must differ")
    if args.plan_output and (args.seed is None or args.max_per_group is None
                             or args.quotas is None):
        parser.error("Plan requires seed, group cap and all four quotas")
    if not args.plan_output and (args.seed is not None or args.max_per_group is not None
                                 or args.quotas is not None):
        parser.error("Sampling options require --plan-output")

    parts = [args.archive_dir / f"FLIR_ADAS_v2.zip.{i:02d}" for i in range(12)]
    with zipfile.ZipFile(JoinedParts(parts)) as z:
        member_names = z.namelist()
        if len(member_names) != len(set(member_names)):
            raise ValueError("ZIP archive has duplicate member names")
        prefix = f"images_thermal_{args.split}"
        index, index_sha = _json_entry(z, f"{prefix}/index.json")
        coco, coco_sha = _json_entry(z, f"{prefix}/coco.json")
    inventory, audit = build_inventory(index, coco, split=args.split,
                                       target=args.target,
                                       index_sha=index_sha, coco_sha=coco_sha)
    plan = None
    if args.plan_output:
        from select_blinded_qa import plan_sample

        try:
            pairs = [part.split("=", 1) for part in args.quotas.split(",")]
            quotas = {key: int(value) for key, value in pairs}
            if len(pairs) != 4:
                raise ValueError("Four explicit quotas required")
        except ValueError as exc:
            parser.error(f"Invalid quotas: {exc}")
        plan = plan_sample(inventory, quotas=quotas, seed=args.seed,
                           max_per_group=args.max_per_group)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(inventory, stream, indent=2)
        stream.write("\n")
    if plan is not None:
        with args.plan_output.open("x", encoding="utf-8") as stream:
            json.dump(plan, stream, indent=2)
            stream.write("\n")
    print(json.dumps(audit, indent=2))
    if plan is not None:
        print("QA plan:", plan["status"], "shortfalls:", plan["shortfalls"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
