"""Focused pre-test FLIR COCO grouping and denominator regression checks."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (Path(__file__).resolve().parents[1]
          / "publications/P01/analyses/build_coco_group_manifest.py")


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def dataset(tmp_path, *, duplicate_group=False, missing_group=False, ignored=False):
    categories = [{"id": 3, "name": "car"}, {"id": 1, "name": "person"}]
    train = {
        "images": [
            {"id": 1, "video_id": "video-A"},
            {"id": 2, "video_id": "video-A"},
            {"id": 3, "extra_info": {"video_id": "video-B"}},
        ],
        "categories": categories,
        "annotations": [
            {"image_id": 1, "category_id": 3, "bbox": [0, 0, 4, 4]},
            {"image_id": 1, "category_id": 3, "bbox": [0, 0, 20, 20]},
            {"image_id": 2, "category_id": 1, "bbox": [0, 0, 2, 2]},
        ],
    }
    validation = {
        "images": [
            {"id": 10, "video_id": "video-A" if duplicate_group else "video-C"},
            {"id": 11, "video_id": "video-D"},
        ],
        "categories": categories,
        "annotations": [
            {"image_id": 10, "category_id": 3, "bbox": [0, 0, 8, 8]},
        ],
    }
    if missing_group:
        validation["images"][0]["video_id"] = "video-\\u200bC"
    if ignored:
        validation["annotations"][0]["iscrowd"] = 1
    return (
        write_json(tmp_path / "train.json", train),
        write_json(tmp_path / "validation.json", validation),
    )


def run(tmp_path, train, validation, *, mode="preserve", name="out.json"):
    output = tmp_path / name
    proc = subprocess.run([
        sys.executable, str(SCRIPT),
        "--train-annotations", str(train),
        "--validation-annotations", str(validation),
        "--release-id", "FLIR-archive-UNVERIFIED",
        "--mode", mode,
        "--output", str(output),
    ], capture_output=True, text=True, check=False)
    return proc, output


def test_preserve_source_coco_counts_and_input_hashes(tmp_path):
    train, validation = dataset(tmp_path)
    result, output = run(tmp_path, train, validation)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "PROVISIONAL_VIDEO_PROXY_SPLIT"
    assert report["heldout_opened"] is False
    assert report["rights_verified"] is False
    assert report["independent_acquisitions_verified"] is False
    assert report["per_split"]["train"]["frames"] == 3
    assert report["per_split"]["train"]["source_reference_negative_frames"] == 2
    assert report["per_split"]["train"]["source_gt_targets_by_footprint_bin"] == {
        "small": 1, "intermediate": 0, "reference": 1,
    }
    assert report["per_split"]["validation"]["source_gt_targets_by_footprint_bin"] == {
        "small": 0, "intermediate": 1, "reference": 0,
    }
    assert len(report["source_annotation_sha256"]["train"]) == 64
    assert len(report["frame_manifest_sha256"]) == 64


def test_original_overlap_blocks_without_corrupting_source_denominators(tmp_path):
    train, validation = dataset(tmp_path, duplicate_group=True)
    result, output = run(tmp_path, train, validation)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "BLOCKED_SOURCE_GROUP_OVERLAP"
    assert report["source_video_groups_in_both_original_splits"] == 1
    assert report["per_split"]["train"]["frames"] == 3
    assert report["per_split"]["validation"]["frames"] == 2


def test_proposal_is_deterministic_and_video_disjoint(tmp_path):
    train, validation = dataset(tmp_path, duplicate_group=True)
    first, output_one = run(tmp_path, train, validation, mode="propose", name="one.json")
    second, output_two = run(tmp_path, train, validation, mode="propose", name="two.json")
    assert first.returncode == second.returncode == 0
    a = json.loads(output_one.read_text(encoding="utf-8"))
    b = json.loads(output_two.read_text(encoding="utf-8"))
    assert a["frame_manifest_sha256"] == b["frame_manifest_sha256"]
    assert a["status"] == "PROVISIONAL_VIDEO_PROXY_SPLIT"
    grouped = {}
    for frame in a["frame_manifest"]:
        key = frame["source_video_id"]
        grouped.setdefault(key, frame["split"])
        assert grouped[key] == frame["split"]
    assert set(grouped.values()) == {"train", "validation"}
    assert a["source_video_groups_in_both_original_splits"] == 1


def test_unknown_group_blocks_not_silently_approved(tmp_path):
    train, validation = dataset(tmp_path, missing_group=True)
    result, output = run(tmp_path, train, validation, mode="propose")
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "BLOCKED_MISSING_OR_NONCANONICAL_GROUPS"
    assert report["source_group_ids_missing_or_noncanonical"] == 1


def test_unfrozen_crowd_rule_fails_closed(tmp_path):
    train, validation = dataset(tmp_path, ignored=True)
    result, output = run(tmp_path, train, validation)
    assert result.returncode != 0
    assert "crowd/ignore" in result.stderr
    assert not output.exists()


def test_evidence_files_are_immutable(tmp_path):
    train, validation = dataset(tmp_path)
    first, _ = run(tmp_path, train, validation)
    second, _ = run(tmp_path, train, validation)
    assert first.returncode == 0
    assert second.returncode != 0
    assert "already" in second.stderr or "must be new" in second.stderr
