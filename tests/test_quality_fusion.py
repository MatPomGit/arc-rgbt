import copy

import pytest

from arc_rgbt.fusionlab import fuse_detections
from arc_rgbt.quality_fusion import quality_fuse_detections


def proposal(x, score=0.9, label="person"):
    return {"label": label, "bbox": [x, 0, 10, 10], "score": score}


def test_unit_quality_matches_existing_baseline():
    rgb, thermal = [proposal(0)], [proposal(1, 0.8)]
    result = quality_fuse_detections(
        rgb, thermal, rgb_quality=1, thermal_quality=1, min_effective_score=0)
    assert result == fuse_detections(rgb, thermal)


def test_lower_quality_modality_has_less_coordinate_influence():
    rgb, thermal = [proposal(0)], [proposal(2)]
    fixed = quality_fuse_detections(
        rgb, thermal, rgb_quality=1, thermal_quality=1, min_effective_score=0)
    adaptive = quality_fuse_detections(
        rgb, thermal, rgb_quality=1, thermal_quality=0.1, min_effective_score=0)
    assert 0 < adaptive[0]["bbox"][0] < fixed[0]["bbox"][0]


def test_reliability_suppresses_false_proposals_without_mutation():
    rgb = [proposal(0, 0.9)]
    thermal = [proposal(100, 0.95)]
    original = copy.deepcopy((rgb, thermal))
    fused = quality_fuse_detections(
        rgb, thermal, rgb_quality=1, thermal_quality=0.1, min_effective_score=0.25)
    assert len(fused) == 1
    assert fused[0]["bbox"] == rgb[0]["bbox"]
    assert (rgb, thermal) == original


def test_zero_reliability_removes_all_candidates():
    assert quality_fuse_detections(
        [proposal(0)], [proposal(1)], rgb_quality=0, thermal_quality=0,
        min_effective_score=0,
    ) == []


@pytest.mark.parametrize("invalid", [True, False, None, -0.1, 1.1, float("nan"),
                                      float("inf"), "0.5"])
def test_quality_parameters_must_be_finite_numeric(invalid):
    with pytest.raises(ValueError):
        quality_fuse_detections(
            [], [], rgb_quality=invalid, thermal_quality=0.5,
        )


@pytest.mark.parametrize("invalid", [True, -0.01, 1.01, float("nan")])
def test_gate_validation(invalid):
    with pytest.raises(ValueError):
        quality_fuse_detections(
            [], [], rgb_quality=0.4, thermal_quality=0.5,
            min_effective_score=invalid,
        )


def test_invalid_detection_schema_is_rejected():
    with pytest.raises(ValueError):
        quality_fuse_detections(
            [{"bbox": [0, 0, 2, 2], "label": "person", "score": True}], [],
            rgb_quality=1, thermal_quality=1,
        )


def test_early_quality_validation_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        quality_fuse_detections(
            [], [], rgb_quality=1, thermal_quality=1, match_iou=0,
        )
