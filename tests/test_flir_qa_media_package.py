"""Synthetic end-to-end tests for local two-assessor FLIR image review packets."""

import importlib
import io
import json
import zipfile
from pathlib import Path

import cv2
import numpy as np
import pytest

SCRIPTS = (Path(__file__).resolve().parents[1] / "publications/P01/analyses")


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    return (
        importlib.import_module("build_flir_qa_inventory"),
        importlib.import_module("select_blinded_qa"),
        importlib.import_module("reconcile_blinded_qa"),
        importlib.import_module("render_flir_qa_package"),
    )


def _fixture_source(root, mods, *, tamper=False):
    build, selector, reviewer, _ = mods
    vid = "Synthetic2026"
    source_frames = []
    coco_images = []
    coco_anns = []
    images = {}
    for i in range(1, 4):
        box = [20, 25, 50, 35]
        labels = [{"labels": ["car"], "boundingBox": dict(zip("xywh", box, strict=True))}]
        if i == 3:
            labels = []
        source_frames.append({
            "width": 640, "height": 512, "videoMetadata": {
                "videoId": vid, "frameIndex": i
            }, "isFlagged": i == 1, "isEmpty": not labels,
            "qaStatus": "approved", "annotations": labels
        })
        name = f"data/video-{vid}-frame-{i:06d}-id.jpg"
        coco_images.append({
            "id": i, "file_name": name, "width": 640, "height": 512,
            "extra_info": {"video_id": vid},
        })
        if i != 3:
            coco_anns.append({
                "id": i, "image_id": i, "category_id": 3,
                "bbox": ([50, 25, 50, 35] if i == 2 else box),
            })
        grey = np.full((512, 640), 25 * i, dtype=np.uint8)
        ok, jpg = cv2.imencode(".jpg", grey)
        assert ok
        images[name] = jpg.tobytes()
    idx = {"frames": source_frames}
    coco = {"categories": [{"id": 3, "name": "car"}],
            "images": coco_images, "annotations": coco_anns}
    raw_index = json.dumps(idx).encode()
    raw_coco = json.dumps(coco).encode()
    import hashlib

    inventory, _ = build.build_inventory(
        idx, coco, split="val", target="car",
        index_sha=hashlib.sha256(raw_index).hexdigest(),
        coco_sha=hashlib.sha256(raw_coco).hexdigest()
    )
    plan = selector.plan_sample(
        inventory, quotas={"A": 1, "B": 1, "C": 1, "D": 0},
        seed=42, max_per_group=3
    )
    assert plan["status"] == "SAMPLE_PLAN_ONLY"
    if tamper:
        plan["inventory_sha256"] = "f" * 64
    source = root / "src"
    source.mkdir()
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("images_thermal_val/index.json", raw_index)
        z.writestr("images_thermal_val/coco.json", raw_coco)
        z.writestr("images_thermal_test/SECRET.txt", b"DO-NOT-READ")
        for name, raw in images.items():
            z.writestr("images_thermal_val/" + name, raw)
    raw = archive.getvalue()
    step = len(raw) // 12
    for i in range(12):
        chunk = raw[i * step:(i + 1) * step] if i < 11 else raw[i * step:]
        (source / f"FLIR_ADAS_v2.zip.{i:02d}").write_bytes(chunk)
    plan_path = root / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    a = root / "a.csv"
    b = root / "b.csv"
    reviewer.prepare(plan_path, a, b)
    return source, plan_path, a, b


def test_render_two_separate_offline_blinded_image_packets(tmp_path, modules):
    _, _, _, renderer = modules
    source, plan, a, b = _fixture_source(tmp_path, modules)
    output = tmp_path / "qa-output"
    report = renderer.render(
        source, plan, a, b, output, split="val", target="car"
    )
    assert report["selected_frames"] == 3
    assert report["status"] == "REVIEW_MEDIA_PREPARED_ONLY"
    assert not report["human_reviews_completed"]
    for folder_name, csv_src in (("reviewer_A", a), ("reviewer_B", b)):
        folder = output / folder_name
        assert (folder / "review.csv").read_bytes() == csv_src.read_bytes()
        page = (folder / "index.html").read_text(encoding="utf-8")
        assert page.count("<section>") == 3
        assert page.count("<details>") == 6
        assert "qa_missing" not in page
        assert "DO-NOT-READ" not in page
        assert len(list((folder / "images").glob("*_raw.png"))) == 3
        assert len(list((folder / "images").glob("*_target.png"))) == 3
        assert len(list((folder / "images").glob("*_all.png"))) == 3
        assert cv2.imread(str(folder / "images/001_raw.png")).shape[:2] == (512, 640)
    manifest = json.loads((output / "package_manifest.json").read_text())
    assert manifest["selected_frames"] == 3
    assert len(manifest["source_image_sha256"]) == 3
    assert manifest["test_labels_inspected"] is False
    assert manifest["source_rights_verified"] is False
    with pytest.raises(FileExistsError):
        renderer.render(source, plan, a, b, output, split="val", target="car")


def test_rejects_source_plan_hash_mismatch(tmp_path, modules):
    _, _, _, renderer = modules
    source, plan, a, b = _fixture_source(tmp_path, modules, tamper=True)
    with pytest.raises(ValueError, match="does not match source"):
        renderer.render(source, plan, a, b, tmp_path / "no-kit",
                        split="val", target="car")
    assert not (tmp_path / "no-kit").exists()


def test_rejects_already_filled_reviewer_sheet(tmp_path, modules):
    _, _, _, renderer = modules
    source, plan, a, b = _fixture_source(tmp_path, modules)
    a.write_text(a.read_text().replace(",\\n", ",complete\\n", 1), encoding="utf-8")
    with pytest.raises(ValueError):
        renderer.render(source, plan, a, b, tmp_path / "no-kit",
                        split="val", target="car")
    assert not (tmp_path / "no-kit").exists()


def test_rejects_test_split_or_wrong_class(tmp_path, modules):
    _, _, _, renderer = modules
    source, plan, a, b = _fixture_source(tmp_path, modules)
    with pytest.raises(ValueError, match="Only train/val"):
        renderer.render(source, plan, a, b, tmp_path / "test-kit",
                        split="test", target="car")
    with pytest.raises(ValueError, match="does not match source"):
        renderer.render(source, plan, a, b, tmp_path / "person-kit",
                        split="val", target="person")
