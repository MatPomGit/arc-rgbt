import numpy as np
import pytest

from arc_rgbt.registration import align_pair


def test_identity_different_native_resolutions_and_masks():
    rgb = np.ones((4, 6), dtype=np.float32)
    thermal = np.ones((2, 3), dtype=np.float32) * 0.5
    matrix = np.diag([0.5, 0.5, 1.0])
    ra, ta, mask, meta = align_pair(rgb, thermal, matrix, calibration_origin="simulated")
    assert ra.shape == (2, 3) == ta.shape == mask.shape
    assert mask.all()
    assert meta["rgb_native_resolution_px"] == [6, 4]
    assert meta["thermal_native_resolution_px"] == [3, 2]
    assert not meta["thermal_upsampled_for_analysis"]
    ra2, ta2, mask2, meta2 = align_pair(
        rgb, thermal, matrix, reference="rgb", calibration_origin="simulated")
    assert ra2.shape == (4, 6) == ta2.shape == mask2.shape
    assert meta2["thermal_upsampled_for_analysis"]


def test_known_planar_translation_produces_valid_mask():
    rgb = np.zeros((8, 8), np.float32)
    rgb[3, 3] = 0.9
    therm = np.zeros((8, 8), np.float32)
    therm[3, 4] = 0.9
    h = np.array([[1, 0, 1], [0, 1, 0], [0, 0, 1]], dtype=np.float64)
    result, other, mask, meta = align_pair(rgb, therm, h, calibration_origin="simulated")
    assert result[3, 4] == pytest.approx(other[3, 4])
    assert not mask[:, 0].any()
    assert meta["valid_overlap_fraction"] == pytest.approx(7 / 8)


@pytest.mark.parametrize("matrix", [
    np.zeros((3, 3)), np.ones((2, 2)),
    [[1, 0, 0], [0, float("nan"), 0], [0, 0, 1]],
])
def test_invalid_homography_is_rejected(matrix):
    with pytest.raises(ValueError):
        align_pair(np.ones((8, 8)), np.ones((8, 8)), matrix)


def test_unknown_provenance_rejected():
    with pytest.raises(ValueError):
        align_pair(np.ones((8, 8)), np.ones((8, 8)), np.eye(3),
                   calibration_origin="unknown")


def test_nan_in_image_rejected():
    rgb = np.ones((8, 8))
    rgb[2, 1] = np.nan
    with pytest.raises(ValueError):
        align_pair(rgb, np.ones((8, 8)), np.eye(3))


def test_fractional_translation_rejects_partial_interpolation_support():
    rgb = np.ones((5, 5), dtype=np.float32)
    thermal = np.ones((5, 5), dtype=np.float32)
    h = np.array([[1, 0, 0.3], [0, 1, 0], [0, 0, 1]], dtype=np.float64)

    shifted, _, mask, meta = align_pair(rgb, thermal, h, calibration_origin="simulated")
    assert np.all(shifted[:, 0] < 1.0)
    assert not mask[:, 0].any()
    assert mask[:, 1:].all()
    assert meta["valid_overlap_fraction"] == pytest.approx(0.8)

    _, shifted_back, inverse_mask, _ = align_pair(
        rgb, thermal, h, reference="rgb", calibration_origin="simulated")
    assert np.all(shifted_back[:, -1] < 1.0)
    assert not inverse_mask[:, -1].any()
    assert inverse_mask[:, :-1].all()
