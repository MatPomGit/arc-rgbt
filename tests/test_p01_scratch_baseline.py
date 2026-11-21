"""Focused checks for source-only P01 scratch-LWIR integration."""

import importlib
import json
import sys
import zipfile
from pathlib import Path

import cv2
import numpy as np
import pytest

ANALYSES = Path(__file__).resolve().parents[1] / "publications/P01/analyses"


def baseline():
    if str(ANALYSES) not in sys.path:
        sys.path.insert(0, str(ANALYSES))
    return importlib.import_module("train_torchvision_baseline")


def source(tmp_path):
    sample = np.full((512, 640), 120, dtype=np.uint8)
    encoded = cv2.imencode(".jpg", sample)[1].tobytes()
    archive_path = tmp_path / "FLIR_ADAS_v2.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("FLIR_ADAS_v2/images_thermal_train/data/a.jpg", encoded)
        z.writestr("FLIR_ADAS_v2/images_thermal_val/data/b.jpg", encoded)
        z.writestr("FLIR_ADAS_v2/video_thermal_test/data/untouched.jpg", b"test")
    payload = archive_path.read_bytes()
    for index in range(12):
        start = index * len(payload) // 12
        end = (index + 1) * len(payload) // 12
        (tmp_path / f"FLIR_ADAS_v2.zip.{index:02d}").write_bytes(payload[start:end])
    categories = [{"id": 3, "name": "car"}, {"id": 1, "name": "person"}]
    train = {
        "categories": categories,
        "images": [{"id": 7, "width": 640, "height": 512,
                    "file_name": "data/a.jpg", "video_id": "one"}],
        "annotations": [{"id": 1, "image_id": 7, "category_id": 3,
                         "bbox": [4, 5, 8, 11]}],
    }
    validation = {
        "categories": categories,
        "images": [{"id": 8, "width": 640, "height": 512,
                    "file_name": "data/b.jpg", "video_id": "two"}],
        "annotations": [],
    }
    train_json = tmp_path / "train_coco.json"
    val_json = tmp_path / "val_coco.json"
    train_json.write_text(json.dumps(train), encoding="utf-8")
    val_json.write_text(json.dumps(validation), encoding="utf-8")
    return train_json, val_json


def test_multipart_source_train_validation_only(tmp_path):
    mod = baseline()
    train, val = source(tmp_path)
    t = mod.coco_records(train, role="train")
    v = mod.coco_records(val, role="validation")
    assert t[0]["boxes"] == [[4, 5, 12, 16]]
    assert v[0]["boxes"] == []
    with mod.FlirImages(tmp_path) as archive:
        assert archive.member("train", "data/a.jpg").endswith("data/a.jpg")
        assert archive.member("validation", "data/b.jpg").endswith("data/b.jpg")
        assert mod.decode_thermal(archive.read("train", "data/a.jpg"), 512, 640).shape == (
            512, 640,
        )
        assert not any("test" in k for role in archive.members for k in archive.members[role])
        with pytest.raises(ValueError, match="No unique"):
            archive.member("validation", "data/a.jpg")


def test_source_paths_and_box_fail_closed(tmp_path):
    mod = baseline()
    train, _ = source(tmp_path)
    for path in ("../evil.jpg", "/test.jpg", "a\\b.jpg", "C:/file.jpg", "data/file.tiff"):
        with pytest.raises(ValueError):
            mod.archive_relative_name(path)
    payload = json.loads(train.read_text())
    payload["annotations"][0]["bbox"] = [639, 510, 2, 3]
    train.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="outside"):
        mod.coco_records(train, role="train")


def test_training_cannot_bypass_rights_acknowledgement(tmp_path):
    mod = baseline()
    with pytest.raises(ValueError, match="terms acknowledgment"):
        mod.train_and_validate(
            tmp_path, tmp_path, tmp_path / "out", epochs=1, batch_size=1,
            seed=0, device="cpu", rights_acknowledged=False,
        )
    assert not (tmp_path / "out").exists()


def test_optional_torchscript_output_is_existing_post_nms_contract():
    torch = pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    mod = baseline()
    detector = mod.make_detector().eval()
    scripted = torch.jit.script(mod.make_post_nms_wrapper(detector).eval())
    rows = scripted(torch.zeros(1, 3, 512, 640))
    assert rows.ndim == 2 and rows.shape[1] == 6
    assert rows.shape[0] <= 1000
    assert torch.isfinite(rows).all()
    assert (rows[:, 5] == 0).all()
