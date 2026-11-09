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


def frozen_synthetic_record(tmp_path, paths):
    """Synthetic FROZEN fixture only; never a real author decision."""
    val_gt, val_pred, test_gt, _ = paths
    data = {
        "schema_version": 1, "author_decision": "FROZEN", "claim_tier": "A",
        "validation_annotations_sha256": runner.digest(val_gt),
        "validation_predictions_sha256": runner.digest(val_pred),
        "holdout_annotations_sha256": runner.digest(test_gt),
    }
    for kind in ("protocol", "checkpoint", "split_manifest"):
        artifact = tmp_path / f"fixture-{kind}.bin"
        artifact.write_bytes(f"synthetic-{kind}".encode())
        data[f"{kind}_path"] = str(artifact)
        data[f"{kind}_sha256"] = runner.digest(artifact)
    return write_json(tmp_path / "synthetic-freeze.json", data)


def test_true_predictions_are_only_dataset_reference_descriptive(tmp_path):
    paths = sources(tmp_path)
    result = runner.evaluate_reference(
        *paths, "car", freeze_record=frozen_synthetic_record(tmp_path, paths),
    )
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
    paths = sources(tmp_path, leaked=True)
    with pytest.raises(ValueError, match="group leakage"):
        runner.evaluate_reference(
            *paths, "car", freeze_record=frozen_synthetic_record(tmp_path, paths),
        )


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


def test_crowd_gt_is_not_silently_treated_as_ordinary_target(tmp_path):
    val_gt, val_pred, _, _ = sources(tmp_path)
    annotations = json.loads(val_gt.read_text(encoding="utf-8"))
    annotations["annotations"][0]["iscrowd"] = 1
    write_json(val_gt, annotations)
    with pytest.raises(ValueError, match="crowd/ignore"):
        runner.load_coco(val_gt, val_pred, "car")


@pytest.mark.parametrize("bad_group", [
    "v-0 ", " v-0", "v-\u200b0", "\uff56-0", "v-0\n",
])
def test_noncanonical_group_cannot_bypass_split_guard(tmp_path, bad_group):
    val_gt, val_pred, test_gt, test_pred = sources(tmp_path)
    payload = json.loads(test_gt.read_text(encoding="utf-8"))
    payload["images"][0]["extra_info"]["video_id"] = bad_group
    write_json(test_gt, payload)
    with pytest.raises(ValueError, match="canonical nonempty source video_id"):
        runner.evaluate_reference(
            val_gt, val_pred, test_gt, test_pred, "car",
            freeze_record=frozen_synthetic_record(
                tmp_path, (val_gt, val_pred, test_gt, test_pred),
            ),
        )


def test_direct_api_requires_author_freeze_before_reading_heldout(tmp_path):
    paths = sources(tmp_path)
    with pytest.raises(ValueError, match="author-FROZEN"):
        runner.evaluate_reference(*paths, "car")


def test_cli_validation_only_never_requires_or_reads_holdout(tmp_path):
    val_gt, val_pred, _, _ = sources(tmp_path)
    out = tmp_path / "validation-only.json"
    assert runner.main([
        "--mode", "validation",
        "--validation-annotations", str(val_gt),
        "--validation-predictions", str(val_pred),
        "--output", str(out),
    ]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["status"] == "VALIDATION_CANDIDATE_ONLY"
    assert report["validation_threshold"]["status"] == "CANDIDATE_ONLY"
    assert "holdout_annotations" not in report["input_sha256"]
    assert "holdout_counts" not in report


def test_cli_refuses_test_inputs_in_default_validation_mode(tmp_path):
    val_gt, val_pred, _, _ = sources(tmp_path)
    with pytest.raises(SystemExit) as err:
        runner.main([
            "--validation-annotations", str(val_gt),
            "--validation-predictions", str(val_pred),
            "--holdout-annotations", str(tmp_path / "missing-test-gt.json"),
            "--output", str(tmp_path / "not-created.json"),
        ])
    assert err.value.code == 2
    assert not (tmp_path / "not-created.json").exists()


def test_cli_blocks_holdout_without_author_freeze(tmp_path):
    val_gt, val_pred, _, _ = sources(tmp_path)
    with pytest.raises(SystemExit) as err:
        runner.main([
            "--mode", "holdout",
            "--validation-annotations", str(val_gt),
            "--validation-predictions", str(val_pred),
            "--holdout-annotations", str(tmp_path / "missing-test-gt.json"),
            "--holdout-predictions", str(tmp_path / "missing-test-det.json"),
            "--output", str(tmp_path / "not-created.json"),
        ])
    assert err.value.code == 2


def test_cli_author_not_frozen_does_not_open_holdout(tmp_path):
    val_gt, val_pred, _, _ = sources(tmp_path)
    frozen = tmp_path / "unapproved-freeze.json"
    write_json(frozen, {
        "schema_version": 1, "author_decision": "CONDITIONAL_DESIGN",
        "claim_tier": "A",
    })
    with pytest.raises(SystemExit) as err:
        runner.main([
            "--mode", "holdout",
            "--validation-annotations", str(val_gt),
            "--validation-predictions", str(val_pred),
            "--holdout-annotations", str(tmp_path / "missing-test-gt.json"),
            "--holdout-predictions", str(tmp_path / "missing-test-det.json"),
            "--freeze-record", str(frozen),
            "--output", str(tmp_path / "not-created.json"),
        ])
    assert err.value.code == 1
    assert not (tmp_path / "not-created.json").exists()


def test_cli_synthetic_frozen_record_binds_inputs_and_remains_descriptive(tmp_path):
    val_gt, val_pred, test_gt, test_pred = sources(tmp_path)
    frozen = frozen_synthetic_record(tmp_path, (val_gt, val_pred, test_gt, test_pred))
    out = tmp_path / "test-report.json"
    assert runner.main([
        "--mode", "holdout",
        "--validation-annotations", str(val_gt),
        "--validation-predictions", str(val_pred),
        "--holdout-annotations", str(test_gt),
        "--holdout-predictions", str(test_pred),
        "--freeze-record", str(frozen),
        "--output", str(out),
    ]) == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["status"] == "DESCRIPTIVE_ONLY"
    assert result["physical_sensor_limits_supported"] is False
    assert result["author_freeze_record_sha256"] == runner.digest(frozen)
    assert result["author_freeze_record_self_declared"] is True
    assert result["frozen_protocol_checkpoint_split_hashes_verified"] is True
