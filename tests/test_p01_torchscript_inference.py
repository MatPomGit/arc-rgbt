"""Targeted tests for P01 validation-only TorchScript prediction adapter."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

SCRIPT = (Path(__file__).resolve().parents[1]
          / "publications/P01/analyses/predict_torchscript_coco.py")
SPEC = importlib.util.spec_from_file_location("p01_predict_torchscript_coco", SCRIPT)
sys.path.insert(0, str(SCRIPT.parent))
predictor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(predictor)


def write_manifest(path, value):
    """Write canonical manifest fingerprint used by the P01 pre-test tool."""
    canonical = json.dumps(
        value["frame_manifest"], ensure_ascii=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    value["frame_manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    path.write_text(json.dumps(value), encoding="utf-8")


def test_letterbox_round_trip_xyxy_to_source_coco():
    source = np.full((20, 40), 128, dtype=np.uint8)
    model_input, mapping = predictor.letterbox(source, 64, 64, 3)
    assert model_input.shape == (1, 3, 64, 64)
    assert model_input.dtype == np.float32
    assert np.array_equal(model_input[0, 0], model_input[0, 2])
    # Source box x=5..15, y=2..12 maps with 1.6x and pad top=16.
    raw = np.array([[8, 19.2, 24, 35.2, 0.8, 2]], dtype=np.float32)
    detections = predictor.decode_predictions(raw, 17, (40, 20), mapping, 2, 3)
    assert detections[0]["image_id"] == 17
    assert detections[0]["category_id"] == 3
    assert detections[0]["bbox"] == pytest.approx([5, 2, 10, 10], abs=1e-5)
    assert detections[0]["score"] == pytest.approx(0.8)


@pytest.mark.parametrize("rows", [
    np.array([[1, 1, 5, 5, 1.1, 0]]),
    np.array([[1, 1, 5, 5, float("nan"), 0]]),
    np.array([[1, 1, 5, 5, 0.2, -1]]),
    np.array([[1, 1, 5, 5, 0.2, 0.5]]),
    np.array([[1, 1, 50, 50, 0.2, 0]]),
    np.array([[5, 1, 1, 5, 0.2, 0]]),
    np.zeros((1, 7)),
])
def test_invalid_model_detections_fail_closed(rows):
    with pytest.raises(ValueError):
        predictor.decode_predictions(rows, 1, (10, 10), (0, 0, 1, 1), 0, 3)


@pytest.mark.parametrize("name", [
    "../outside.jpg", "/etc/passwd", "C:/windows/temp.jpg", "a\\b.jpg",
    "file.tiff", "source/./image.jpg",
])
def test_reject_unsafe_or_unsupported_image_paths(tmp_path, name):
    with pytest.raises(ValueError):
        predictor.safe_image(tmp_path.resolve(), name)


def test_manifest_validation_rejects_unbound_or_unfrozen_sources(tmp_path):
    annotations = tmp_path / "validation.json"
    annotations.write_text(
        json.dumps({"images": [{"id": 1, "video_id": "g-1",
                               "file_name": "image.jpg", "width": 10, "height": 10}],
                    "categories": [{"id": 3, "name": "car"}],
                    "annotations": []}), encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    write_manifest(manifest, {
        "status": "PROVISIONAL_VIDEO_PROXY_SPLIT", "split_mode": "propose",
        "selected_class": "car", "heldout_opened": False,
        "source_annotation_sha256": {"validation": predictor.digest(annotations)},
        "validation_threshold_exposure_meets_software_floor": True,
        "frame_manifest": [{
            "split": "validation", "frame_id": "validation:1", "source_video_id": "g-1"
        }],
    })
    with pytest.raises(ValueError, match="Manifest not eligible"):
        predictor.load_validation(annotations, manifest, "car")


def test_manifest_rejects_nonmatching_group(tmp_path):
    source = {
        "images": [{"id": 1, "video_id": "actual-g",
                    "file_name": "image.jpg", "width": 10, "height": 10}],
        "categories": [{"id": 3, "name": "car"}], "annotations": [],
    }
    annotations = tmp_path / "validation.json"
    annotations.write_text(json.dumps(source), encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    write_manifest(manifest, {
        "status": "PROVISIONAL_VIDEO_PROXY_SPLIT", "split_mode": "preserve",
        "selected_class": "car", "heldout_opened": False,
        "source_annotation_sha256": {"validation": predictor.digest(annotations)},
        "validation_threshold_exposure_meets_software_floor": True,
        "frame_manifest": [{
            "split": "validation", "frame_id": "validation:1",
            "source_video_id": "fake-g",
        }],
    })
    with pytest.raises(ValueError, match="group mismatch"):
        predictor.load_validation(annotations, manifest, "car")


def test_manifest_hash_and_actual_exposure_verified_before_inference(tmp_path):
    """Forged flags cannot make one validation frame satisfy scientific exposure."""
    annotations = tmp_path / "validation.json"
    annotations.write_text(json.dumps({
        "images": [{"id": 1, "video_id": "g-1", "file_name": "frame.png",
                    "width": 16, "height": 16}],
        "categories": [{"id": 3, "name": "car"}], "annotations": [],
    }), encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    plan = {
        "status": "PROVISIONAL_VIDEO_PROXY_SPLIT",
        "split_mode": "preserve", "selected_class": "car",
        "heldout_opened": False,
        "source_annotation_sha256": {"validation": predictor.digest(annotations)},
        "validation_threshold_exposure_meets_software_floor": True,
        "frame_manifest": [{
            "split": "validation", "frame_id": "validation:1",
            "source_video_id": "g-1",
        }],
    }
    write_manifest(manifest, plan)
    with pytest.raises(ValueError, match="Actual source validation exposure"):
        predictor.load_validation(annotations, manifest, "car")
    plan["frame_manifest"][0]["source_video_id"] = "g-2"
    manifest.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(ValueError, match="manifest content SHA-256 mismatch"):
        predictor.load_validation(annotations, manifest, "car")


def test_source_manifest_cannot_hide_train_validation_leakage(tmp_path):
    """A rehashed, internally contradictory manifest must not enable inference."""
    annotations = tmp_path / "validation.json"
    annotations.write_text(json.dumps({
        "images": [{"id": 1, "video_id": "session-A", "file_name": "image.png",
                    "width": 16, "height": 16}],
        "categories": [{"id": 3, "name": "car"}], "annotations": [],
    }), encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    base = {
        "status": "PROVISIONAL_VIDEO_PROXY_SPLIT",
        "split_mode": "preserve", "selected_class": "car",
        "heldout_opened": False,
        "source_annotation_sha256": {"validation": predictor.digest(annotations)},
        "validation_threshold_exposure_meets_software_floor": True,
        "frame_manifest": [
            {"split": "train", "frame_id": "train:7", "source_video_id": "session-A"},
            {"split": "validation", "frame_id": "validation:1",
             "source_video_id": "session-A"},
        ],
    }
    write_manifest(manifest, base)
    with pytest.raises(ValueError, match="Train/validation source video group leakage"):
        predictor.load_validation(annotations, manifest, "car")


def test_source_manifest_rejects_duplicate_frame_entries(tmp_path):
    annotations = tmp_path / "validation.json"
    annotations.write_text(json.dumps({
        "images": [{"id": 1, "video_id": "session-B", "file_name": "image.png",
                    "width": 16, "height": 16}],
        "categories": [{"id": 3, "name": "car"}], "annotations": [],
    }), encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    row = {"split": "validation", "frame_id": "validation:1",
           "source_video_id": "session-B"}
    write_manifest(manifest, {
        "status": "PROVISIONAL_VIDEO_PROXY_SPLIT",
        "split_mode": "preserve", "selected_class": "car",
        "heldout_opened": False,
        "source_annotation_sha256": {"validation": predictor.digest(annotations)},
        "validation_threshold_exposure_meets_software_floor": True,
        "frame_manifest": [row, row.copy()],
    })
    with pytest.raises(ValueError, match="Invalid or duplicate pre-test frame split"):
        predictor.load_validation(annotations, manifest, "car")


def test_checkpoint_hash_fails_before_optional_torch_or_image_io(tmp_path):
    checkpoint = tmp_path / "model.pt"
    checkpoint.write_bytes(b"not a checkpoint")
    with pytest.raises(ValueError, match="Checkpoint SHA-256 mismatch"):
        predictor.predict(
            tmp_path / "unread-annotations.json", tmp_path / "unread-manifest.json",
            tmp_path, checkpoint, "0" * 64, "car", 0,
            16, 16, 1, "cpu", tmp_path / "result",
        )


def test_torchscript_validation_integration_if_torch_is_installed(tmp_path):
    torch = pytest.importorskip("torch")
    import cv2

    class ConstantDetector(torch.nn.Module):
        def forward(self, data):
            return torch.tensor([[[2.0, 2.0, 10.0, 10.0, 0.8, 0.0]]])

    checkpoint = tmp_path / "trusted.pt"
    traced = torch.jit.trace(ConstantDetector(), torch.zeros(1, 1, 16, 16))
    traced.save(str(checkpoint))
    image_root = tmp_path / "images"
    image_root.mkdir()
    assert cv2.imwrite(str(image_root / "frame.png"),
                       np.zeros((16, 16), dtype=np.uint8))
    frames = [{
        "id": i, "video_id": f"scene-{i // 20}", "file_name": "frame.png",
        "width": 16, "height": 16,
    } for i in range(200)]
    annotations = tmp_path / "validation.json"
    annotations.write_text(json.dumps({
        "categories": [{"id": 3, "name": "car"}],
        "images": frames, "annotations": [],
    }), encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    write_manifest(manifest, {
        "status": "PROVISIONAL_VIDEO_PROXY_SPLIT",
        "split_mode": "preserve", "selected_class": "car",
        "heldout_opened": False,
        "source_annotation_sha256": {"validation": predictor.digest(annotations)},
        "validation_threshold_exposure_meets_software_floor": True,
        "frame_manifest": [
            {"split": "validation", "frame_id": f"validation:{i}",
             "source_video_id": f"scene-{i // 20}"}
            for i in range(200)
        ],
    })
    output = tmp_path / "output"
    report = predictor.predict(
        annotations, manifest, image_root, checkpoint,
        predictor.digest(checkpoint), "car", 0, 16, 16, 1, "cpu", output,
    )
    result = json.loads((output / "predictions.json").read_text(encoding="utf-8"))
    assert len(result) == 200
    assert len({row["image_id"] for row in result}) == 200
    assert result[0]["bbox"] == pytest.approx([2, 2, 8, 8])
    assert report["status"] == "VALIDATION_PREDICTIONS_ONLY_UNADMITTED"
    assert report["heldout_opened"] is False
    assert report["predictions_sha256"] == predictor.digest(output / "predictions.json")
    assert not (tmp_path / "holdout.json").exists()
