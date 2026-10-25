import cv2
import numpy as np
import pytest

from arc_rgbt.fusionlab import fuse_detections, fuse_images, register_translation


def test_weighted_and_gradient_fusion():
    x = np.zeros((32, 32), np.float32)
    y = np.ones((32, 32), np.float32)
    assert np.allclose(fuse_images(x, y, "weighted", 0.25), 0.25)
    assert np.array_equal(fuse_images(x, y, "gradient"), x)
    with pytest.raises(ValueError):
        fuse_images(x, y, "missing")


def test_registration_shift():
    y, x = np.mgrid[:96, :96]
    reference = np.exp(-((x - 45) ** 2 + (y - 47) ** 2) / 100).astype(np.float32)
    translated = cv2.warpAffine(reference, np.float32([[1, 0, 4], [0, 1, -3]]), (96, 96))
    registered, record = register_translation(reference, translated)
    assert np.mean(np.abs(registered - reference)) < 0.01
    assert abs(record["translation_applied_px"][0] + 4) < 0.5


def test_late_fusion_class_match_and_unmatched():
    a = [{"label": "person", "bbox": [0, 0, 10, 10], "score": 0.7}]
    b = [{"label": "person", "bbox": [1, 0, 10, 10], "score": 0.9},
         {"label": "vehicle", "bbox": [0, 0, 10, 10], "score": 0.8}]
    result = fuse_detections(a, b)
    assert len(result) == 2
    assert 0 < result[0]["bbox"][0] < 1
    assert result[1]["label"] == "vehicle"


def test_late_fusion_rejects_zero_threshold_and_negative_box():
    with pytest.raises(ValueError):
        fuse_detections([], [], threshold=0)
    with pytest.raises(ValueError):
        fuse_detections([{"label": "object", "bbox": [0, 0, -1, 5], "score": 0.9}], [])


@pytest.mark.parametrize("invalid_score", [True, False, None, "0.8", 0, -0.1,
                                             float("nan"), float("inf")])
def test_late_fusion_rejects_invalid_score_types(invalid_score):
    box = {"label": "person", "bbox": [0, 0, 10, 10], "score": invalid_score}
    with pytest.raises(ValueError, match="Invalid detection"):
        fuse_detections([box], [])


@pytest.mark.parametrize("invalid", [
    {"label": "", "bbox": [0, 0, 4, 4], "score": 0.6},
    {"label": "person", "bbox": [0, 0, True, 4], "score": 0.6},
    {"label": "person", "bbox": [0, 0, 4, 4], "score": 0.6, "extra": 1},
    {"label": "person", "bbox": [0, 0, 4, float("nan")], "score": 0.6},
    {},
])
def test_late_fusion_rejects_invalid_boxes(invalid):
    with pytest.raises(ValueError, match="[Dd]etection"):
        fuse_detections([invalid], [])


@pytest.mark.parametrize("threshold", [True, None, float("nan"), "0.5"])
def test_late_fusion_rejects_invalid_threshold_types(threshold):
    with pytest.raises(ValueError, match="IoU threshold"):
        fuse_detections([], [], threshold=threshold)


@pytest.mark.parametrize("weight", [True, None, "0.5", float("nan")])
def test_image_fusion_rejects_invalid_weights(weight):
    img = np.ones((4, 4), dtype=np.float32)
    with pytest.raises(ValueError, match="thermal_weight"):
        fuse_images(img, img, thermal_weight=weight)


def test_image_fusion_rejects_non_numeric_arrays():
    invalid = np.array([["a", "b"], ["c", "d"]])
    with pytest.raises(ValueError, match="grayscale"):
        fuse_images(invalid, invalid)


def test_finite_float64_values_outside_float32_range_are_rejected():
    extreme = np.full((4, 4), 1e40, dtype=np.float64)
    with pytest.raises(ValueError, match="float32"):
        fuse_images(extreme, extreme)
    with pytest.raises(ValueError, match="float32"):
        register_translation(extreme, extreme)


def test_late_fusion_rejects_overflowed_iou_geometry():
    extreme = {"label": "person", "bbox": [0.0, 0.0, 1e308, 1e308], "score": 0.8}
    with pytest.raises(ValueError, match="geometry"):
        fuse_detections([extreme], [extreme])
