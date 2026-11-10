"""Create P01 pre-test source-GT denominators and disjoint group proposals.

Reads existing train/validation COCO labels ONLY. Never reads held-out test,
model predictions or images. All groups are source video-ID proxies; passing
structural checks cannot prove true independent acquisitions or lawful use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from run_coco_reference import digest, source_group

MAX_COCO_BYTES = 256 * 1024 * 1024
BINS = ("small", "intermediate", "reference")


def _load(path: Path, class_name: str, source_split: str) -> tuple[list[dict], dict]:
    if not 0 < path.stat().st_size <= MAX_COCO_BYTES:
        raise ValueError("COCO annotations are empty or exceed 256 MiB")
    coco = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(coco, dict):
        raise ValueError("COCO root must be an object")
    images = coco.get("images")
    objects = coco.get("annotations")
    categories = coco.get("categories")
    if not all(isinstance(x, list) for x in (images, objects, categories)):
        raise ValueError("Expected COCO images, annotations, categories arrays")
    chosen = [cat["id"] for cat in categories
              if isinstance(cat, dict) and cat.get("name") == class_name]
    if len(chosen) != 1:
        raise ValueError("Exactly one source category must match the target class")
    category_id = chosen[0]
    frames = {}
    for image in images:
        image_id = image.get("id")
        if type(image_id) is not int or image_id in frames:
            raise ValueError("Invalid or repeated image ID within source split")
        try:
            group = source_group(image)
        except ValueError:
            group = None
        frames[image_id] = {
            "frame_id": f"{source_split}:{image_id}",
            "group_id": group,
            "original_split": source_split,
            "bins": Counter(),
        }
    seen_annotation_ids = set()
    for ann in objects:
        if not isinstance(ann, dict) or ann.get("image_id") not in frames:
            raise ValueError("Malformed or orphan annotation")
        # COCO annotation IDs identify GT records across every category.
        # Missing, null, non-integer or repeated IDs make the source count
        # ambiguous, even if the selected target class appears unaffected.
        annotation_id = ann.get("id")
        if type(annotation_id) is not int or annotation_id in seen_annotation_ids:
            raise ValueError("Missing, invalid or repeated COCO annotation ID")
        seen_annotation_ids.add(annotation_id)
        if ann.get("category_id") != category_id:
            continue
        if ann.get("iscrowd", 0) or ann.get("ignore", 0):
            raise ValueError("Target class crowd/ignore needs a frozen rule")
        bbox = ann.get("bbox")
        if (not isinstance(bbox, list) or len(bbox) != 4
                or any(type(x) not in (int, float) or not math.isfinite(x)
                       for x in bbox)
                or bbox[2] <= 0 or bbox[3] <= 0):
            raise ValueError("Malformed selected source bbox")
        footprint = math.sqrt(bbox[2] * bbox[3])
        name = ("small" if footprint < 8 else
                "intermediate" if footprint < 16 else "reference")
        frames[ann["image_id"]]["bins"][name] += 1
    return list(frames.values()), {
        "sha256": digest(path),
        "image_count": len(images),
        "selected_target_count": sum(sum(f["bins"].values())
                                     for f in frames.values()),
    }


def prepare(train: Path, validation: Path, class_name: str,
            mode: str, seed: int, validation_fraction: float,
            release_id: str) -> dict:
    """Build manifest with explicit barriers, never an empirical admission."""
    if mode not in ("preserve", "propose"):
        raise ValueError("Unsupported split mode")
    if not 0 < validation_fraction < 1 or type(seed) is not int:
        raise ValueError("Invalid split parameters")
    if not release_id.strip():
        raise ValueError("A source release identifier is required")
    if train.resolve() == validation.resolve():
        raise ValueError("Train and validation COCO inputs must differ")
    first, train_source = _load(train, class_name, "train")
    second, validation_source = _load(validation, class_name, "validation")
    frames = first + second
    known_groups = sorted({f["group_id"] for f in frames if f["group_id"] is not None})
    missing = sum(f["group_id"] is None for f in frames)
    existing_overlap = sorted(
        {f["group_id"] for f in first if f["group_id"] is not None}
        & {f["group_id"] for f in second if f["group_id"] is not None}
    )
    if mode == "propose" and not missing and len(known_groups) >= 2:
        ranking = sorted(
            known_groups,
            key=lambda group: (
                hashlib.sha256(f"{seed}:{group}".encode()).hexdigest(), group
            ),
        )
        n_validation = max(1, min(len(ranking) - 1,
                                  round(len(ranking) * validation_fraction)))
        validation_groups = set(ranking[:n_validation])
        assignments = {
            group: ("validation" if group in validation_groups else "train")
            for group in known_groups
        }
    else:
        assignments = {}
    per_split = {}
    for name in ("train", "validation"):
        selected = [
            f for f in frames
            if (assignments[f["group_id"]] if mode == "propose" and
                f["group_id"] in assignments else f["original_split"]) == name
        ]
        per_split[name] = {
            "frames": len(selected),
            "source_reference_negative_frames": sum(
                not f["bins"] for f in selected
            ),
            "source_reference_negative_groups": len({
                f["group_id"] for f in selected
                if not f["bins"] and f["group_id"] is not None
            }),
            "source_reference_positive_frames": sum(
                bool(f["bins"]) for f in selected
            ),
            "source_gt_targets_by_footprint_bin": {
                bin_name: sum(f["bins"][bin_name] for f in selected)
                for bin_name in BINS
            },
            "source_video_proxy_groups": len({
                f["group_id"] for f in selected if f["group_id"] is not None
            }),
        }
    validation_counts = per_split["validation"]
    validation_threshold_exposure = {
        "at_least_200_frames": validation_counts["frames"] >= 200,
        "at_least_10_source_video_groups": (
            validation_counts["source_video_proxy_groups"] >= 10
        ),
        "at_least_20_reference_negative_frames": (
            validation_counts["source_reference_negative_frames"] >= 20
        ),
        "at_least_2_reference_negative_groups": (
            validation_counts["source_reference_negative_groups"] >= 2
        ),
    }
    if missing:
        status = "BLOCKED_MISSING_OR_NONCANONICAL_GROUPS"
    elif len(known_groups) < 2:
        status = "BLOCKED_INSUFFICIENT_GROUPS"
    elif mode == "preserve" and existing_overlap:
        status = "BLOCKED_SOURCE_GROUP_OVERLAP"
    elif min(per_split[name]["frames"] for name in per_split) == 0:
        status = "BLOCKED_EMPTY_SPLIT"
    else:
        status = "PROVISIONAL_VIDEO_PROXY_SPLIT"
    manifest = [{
        "frame_id": f["frame_id"],
        "source_video_id": f["group_id"],
        "split": (assignments.get(f["group_id"]) if mode == "propose" and
                  f["group_id"] in assignments else f["original_split"]),
        "selected_gt_bins": {name: f["bins"][name] for name in BINS},
    } for f in sorted(frames, key=lambda row: row["frame_id"])]
    manifest_sha = hashlib.sha256(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": 1,
        "status": status,
        "research_tier": "A_source_reference_candidate_only",
        "empirical_admission": False,
        "rights_verified": False,
        "native_sensor_geometry_verified": False,
        "independent_acquisitions_verified": False,
        "model_training_independence_verified": False,
        "heldout_opened": False,
        "release_id_claim": release_id,
        "selected_class": class_name,
        "source_grid": "source_coco_export_unverified",
        "group_basis": "source_video_proxy_unverified",
        "split_mode": mode,
        "seed": seed if mode == "propose" else None,
        "validation_fraction_candidate": validation_fraction if mode == "propose" else None,
        "source_annotation_sha256": {
            "train": train_source["sha256"],
            "validation": validation_source["sha256"],
        },
        "source_group_ids_missing_or_noncanonical": missing,
        "source_video_groups_in_both_original_splits": len(existing_overlap),
        "per_split": per_split,
        "validation_threshold_candidate_exposure": validation_threshold_exposure,
        "validation_threshold_exposure_meets_software_floor": all(
            validation_threshold_exposure.values()
        ),
        "implementation_sha256": {
            "manifest_builder": digest(Path(__file__)),
            "reference_runner": digest(Path(__file__).with_name("run_coco_reference.py")),
        },
        "frame_manifest_sha256": manifest_sha,
        "frame_manifest": manifest,
        "limitations": [
            "COCO supplied GT is not certified physically complete.",
            "Video IDs and archive names are not independently verified acquisitions.",
            "Only train and validation source annotation files were opened.",
            "A proposed reassignment is not safe for an already trained checkpoint.",
            "No lawful-use, native-optics or scientific G01 approval is implied.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-annotations", type=Path, required=True)
    parser.add_argument("--validation-annotations", type=Path, required=True)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--class-name", default="car")
    parser.add_argument("--mode", choices=("preserve", "propose"), default="preserve")
    parser.add_argument("--seed", type=int, default=20261109)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    output = args.output.resolve()
    if output.is_relative_to(root):
        parser.error("Output must be outside the source repository")
    if output in {
        args.train_annotations.resolve(), args.validation_annotations.resolve()
    } or output.exists():
        parser.error("Output must be new and must not overwrite an input")
    try:
        result = prepare(
            args.train_annotations, args.validation_annotations, args.class_name,
            args.mode, args.seed, args.validation_fraction, args.release_id,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2,
                      allow_nan=False)
            stream.write("\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"P01 metadata: {type(exc).__name__}: {exc}\n")
    print(json.dumps({
        "status": result["status"], "output": str(output),
        "group_missing": result["source_group_ids_missing_or_noncanonical"],
        "heldout_opened": False,
        "real_detector_measurement": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
