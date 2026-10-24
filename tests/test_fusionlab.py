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
