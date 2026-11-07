"""Synthetic fixtures for FLIR metadata-only annotation QA inventory generation."""

import importlib.util
import io
import json
import zipfile
from pathlib import Path

import pytest

SCRIPT = (Path(__file__).resolve().parents[1] /
          "publications/P01/analyses/build_flir_qa_inventory.py")
spec = importlib.util.spec_from_file_location("flir_qa_inventory", SCRIPT)
flir = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(flir)


def original_frame(vid, number, annotations, *, state="approved", flagged=False):
    row = {"videoMetadata": {"videoId": vid, "frameIndex": number},
           "annotations": annotations, "isFlagged": flagged,
           "width": 640, "height": 512}
    if state is not None:
        row["qaStatus"] = state
    return row


def original_annotation(label, box):
    return {"labels": [label], "boundingBox": dict(zip("xywh", box, strict=True))}


def image(vid, number):
    return {"id": number, "width": 640, "height": 512,
            "file_name": f"data/video-{vid}-frame-{number:06d}-id.jpg",
            "extra_info": {"video_id": vid}}


def annotation(aid, image_id, category, box):
    return {"id": aid, "image_id": image_id, "category_id": category, "bbox": box}


def documents():
    vid = "synthetic-video"
    index = {"frames": [
        original_frame(vid, 1, [original_annotation("rider", [10, 20, 30, 40])]),
        original_frame(vid, 2, [], state=None),
        original_frame(vid, 3, [original_annotation("car", [610, 20, 40, 30])],
                       flagged=True),
        original_frame(vid, 4, [original_annotation("person", [10, 20, 25, 30])]),
        original_frame(vid, 5, [original_annotation("person", [10, 20, 25, 30])]),
        original_frame(vid, 6, [original_annotation("person", [10, 20, 25, 30])]),
    ]}
    coco = {
        "images": [image(vid, n) for n in range(1, 7)],
        "categories": [{"id": 1, "name": "person"}, {"id": 3, "name": "car"}],
        "annotations": [
            annotation(1, 1, 1, [10, 20, 30, 40]),
            annotation(2, 3, 3, [610, 20, 30, 30]),
            annotation(3, 4, 1, [10, 20, 25, 30]),
            annotation(4, 5, 1, [10.3, 20, 25, 30]),
            annotation(5, 6, 1, [90, 20, 25, 30]),
        ],
    }
    return index, coco


def produce(target="person"):
    idx, co = documents()
    return flir.build_inventory(idx, co, split="val", target=target,
                                index_sha="a" * 64, coco_sha="b" * 64)


def by_number(inventory):
    return {row["frame_id"].split(":")[-1]: row for row in inventory["frames"]}


def test_rider_mapping_negative_candidates_and_geometry_risk():
    inventory, audit = produce()
    rows = by_number(inventory)
    assert rows["1"]["rider_only"] is True
    assert rows["1"]["target_positive"] is True
    assert rows["1"]["class_conflict"] is False
    assert rows["2"]["qa_state"] == "missing"
    assert rows["2"]["candidate_negative"] is True
    assert rows["3"]["qa_state"] == "flagged"
    assert rows["3"]["clipped_box"] is True
    assert rows["3"]["candidate_negative"] is True
    assert rows["4"]["geometry_conflict"] is False
    assert rows["5"]["geometry_conflict"] is False
    assert rows["6"]["geometry_conflict"] is True
    assert audit["annotation_completeness"] == "UNKNOWN"
    assert audit["empirical_admission"] is False
    assert inventory["group_basis"] == "video_id_proxy"


def test_car_does_not_include_riders():
    inventory, audit = produce("car")
    rows = by_number(inventory)
    assert rows["1"]["candidate_negative"] is True
    assert rows["3"]["target_positive"] is True
    assert rows["3"]["clipped_box"] is True
    assert rows["3"]["geometry_conflict"] is True
    assert audit["risk_counts"]["target_positive"] == 1


def test_source_disagreement_never_promotes_negative():
    idx, coco = documents()
    coco["annotations"] = [a for a in coco["annotations"] if a["id"] != 1]
    inventory, _ = flir.build_inventory(
        idx, coco, split="val", target="person",
        index_sha="a" * 64, coco_sha="b" * 64
    )
    first = inventory["frames"][0]
    assert first["class_conflict"] is True
    assert first["target_positive"] is True
    assert first["candidate_negative"] is False


def test_duplicate_and_test_split_rejected():
    idx, coco = documents()
    with pytest.raises(ValueError, match="Only train/val"):
        flir.build_inventory(idx, coco, split="test", target="person",
                             index_sha="x", coco_sha="y")
    coco["images"].append(coco["images"][0].copy())
    with pytest.raises(ValueError, match="Duplicate frame key"):
        flir.build_inventory(idx, coco, split="val", target="person",
                             index_sha="x", coco_sha="y")


def test_orphan_annotation_rejected():
    idx, coco = documents()
    coco["annotations"].append(annotation(99, 999, 1, [1, 1, 5, 5]))
    with pytest.raises(ValueError, match="Orphaned"):
        flir.build_inventory(idx, coco, split="val", target="person",
                             index_sha="x", coco_sha="y")


def test_selector_schema_and_inventory_provenance():
    inventory, _ = produce()
    assert set(inventory) == {"schema_version", "source_release", "group_basis", "frames"}
    assert len(inventory["frames"]) == 6
    assert "index=" + "a" * 64 in inventory["source_release"]
    assert all(set(frame) == {
        "frame_id", "group_id", "qa_state", "class_conflict", "geometry_conflict",
        "clipped_box", "rider_only", "candidate_negative", "target_positive"
    } for frame in inventory["frames"])


def test_member_crc_and_json_sha_are_checked():
    idx, coco = documents()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("images_thermal_val/index.json", json.dumps(idx))
        z.writestr("images_thermal_val/coco.json", json.dumps(coco))
    stream.seek(0)
    with zipfile.ZipFile(stream) as z:
        parsed_i, hash_i = flir._json_entry(z, "images_thermal_val/index.json")
        parsed_c, hash_c = flir._json_entry(z, "images_thermal_val/coco.json")
    assert parsed_i == idx and parsed_c == coco
    assert len(hash_i) == len(hash_c) == 64
    assert hash_i != hash_c
