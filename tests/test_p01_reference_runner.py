"""Focused checks for the real-output P01 COCO reference benchmark adapter."""

import importlib.util
import json
from pathlib import Path

import pytest

from arc_rgbt.p01_metrics import native_footprint_recall

SCRIPT = Path(__file__).resolve().parents[1] / "publications/P01/analyses/run_coco_reference.py"
SPEC = importlib.util.spec_from_file_location("run_coco_reference", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def sources(tmp_path, *, leaked=False, short_validation=False):
    val_n = 2 if short_validation else 200
    images = [
        {"id": index, "extra_info": {"video_id": f"v-{index // 20}"}}
        for index in range(val_n)
    ]
    labels = [{"id": 1, "name": "car"}, {"id": 2, "name": "person"}]
    gt = {"images": images, "categories": labels, "annotations": [
        {"image_id": 0, "category_id": 1, "bbox": [0, 0, 4, 4]},
    ]}
    pred = [{"image_id": 0, "category_id": 1,
             "bbox": [0, 0, 4, 4], "score": 0.9}]
    test_group = "v-0" if leaked else "holdout-group"
    test_gt = {"images": [
        {"id": 400, "extra_info": {"video_id": test_group}},
    ], "categories": labels, "annotations": [
        {"image_id": 400, "category_id": 1, "bbox": [0, 0, 4, 4]},
        {"image_id": 400, "category_id": 1, "bbox": [100, 0, 20, 20]},
    ]}
    test_pred = [
        {"image_id": 400, "category_id": 1, "bbox": [0, 0, 4, 4], "score": 0.9},
        {"image_id": 400, "category_id": 1, "bbox": [100, 0, 20, 20], "score": 0.9},
    ]
    return (
        write_json(tmp_path / "val-gt.json", gt),
        write_json(tmp_path / "val-det.json", pred),
        write_json(tmp_path / "test-gt.json", test_gt),
        write_json(tmp_path / "test-det.json", test_pred),
    )


def test_true_predictions_are_only_dataset_reference_descriptive(tmp_path):
    paths = sources(tmp_path)
    result = runner.evaluate_reference(*paths, "car")
    assert result["status"] == "DESCRIPTIVE_ONLY"
    assert result["validation_threshold"]["threshold"] == 0.0
    assert result["validation_threshold"]["group_basis"] == "source_video_proxy"
    assert result["validation_threshold"]["validation_fp_bootstrap_ci_95"] is None
    assert result["holdout_counts"]["reference_targets"] == 2
    assert result["holdout_footprint"]["per_bin"]["small"]["recall"] == 1.0
    assert result["holdout_footprint"]["per_bin"]["reference"]["recall"] == 1.0
    assert result["holdout_footprint"]["candidate_percentile_ci_95"] is None
    assert result["holdout_ap"]["per_class_ap"]["car"] == 1.0
    assert result["physical_sensor_limits_supported"] is False
    assert set(result["input_sha256"]) == {
        "validation_annotations", "validation_predictions",
        "holdout_annotations", "holdout_predictions",
    }


def test_invalid_validation_does_not_touch_holdout(tmp_path):
    val_gt, val_det, _, _ = sources(tmp_path, short_validation=True)
    report = runner.evaluate_reference(
        val_gt, val_det, tmp_path / "missing-gt", tmp_path / "missing-det", "car",
    )
    assert report["status"] == "BLOCKED_VALIDATION"
    assert "holdout_annotations" not in report["input_sha256"]


def test_shared_video_proxy_detected_between_splits(tmp_path):
    with pytest.raises(ValueError, match="group leakage"):
        runner.evaluate_reference(*sources(tmp_path, leaked=True), "car")


def test_source_export_does_not_get_physical_ci():
    frames = [{
        "id": "x",
        "ground_truth": [{"label": "car", "bbox": [0, 0, 4, 4]}],
        "predictions": [{"label": "car", "bbox": [0, 0, 4, 4], "score": 0.8}],
    }]
    report = native_footprint_recall(
        frames, acquisition_ids=["video-1"],
        annotation_status="source_reference_unverified",
        grid_origin="source_export", group_basis="source_video_proxy",
    )
    assert report["status"] == "DESCRIPTIVE_ONLY"
    assert report["physical_sensor_claims_supported"] is False
    assert report["candidate_percentile_ci_95"] is None


def test_adapter_rejects_unknown_predictions(tmp_path):
    paths = sources(tmp_path)
    bad = [{"image_id": 999, "category_id": 1,
            "bbox": [0, 0, 4, 4], "score": 0.8}]
    write_json(paths[1], bad)
    with pytest.raises(ValueError, match="unknown image_id"):
        runner.evaluate_reference(*paths, "car")
