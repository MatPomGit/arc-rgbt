import numpy as np
import pytest

from arc_rgbt.degradesim import degrade


def test_seed_and_native_resolution():
    image = np.random.default_rng(1).random((240, 320), dtype=np.float32)
    a, record = degrade(image, width_px=8, height_px=8, noise_sigma=0.05, seed=21)
    b, _ = degrade(image, width_px=8, height_px=8, noise_sigma=0.05, seed=21)
    assert a.shape == (8, 8)
    assert np.array_equal(a, b)
    assert record["interpolated_resolution_px"] is None


def test_invalid_shape_and_param():
    with pytest.raises(ValueError):
        degrade(np.array([]), width_px=8, height_px=8)
    with pytest.raises(ValueError):
        degrade(np.ones((8, 8)), width_px=0, height_px=8)


def test_intensities_outside_unit_range_are_not_silently_clipped():
    with pytest.raises(ValueError, match="normalized"):
        degrade(np.full((8, 8), 255, dtype=np.uint8), width_px=8, height_px=8)
    with pytest.raises(ValueError, match="normalized"):
        degrade(np.full((8, 8), -0.01), width_px=8, height_px=8)


@pytest.mark.parametrize("kwargs", [
    {"width_px": 8.5}, {"height_px": True}, {"motion_length_px": 2.5},
    {"noise_sigma": float("nan")}, {"optical_sigma_px": float("inf")},
    {"seed": -1}, {"seed": True},
])
def test_invalid_degradation_controls(kwargs):
    params = {"width_px": 8, "height_px": 8, **kwargs}
    with pytest.raises(ValueError):
        degrade(np.ones((8, 8)), **params)


def test_motion_blur_is_horizontal_and_preserves_constant_signal():
    src = np.zeros((9, 9), dtype=np.float32)
    src[4, 4] = 1.0
    blurred, meta = degrade(src, width_px=9, height_px=9, motion_length_px=3)
    assert np.allclose(blurred[4, 3:6], 1 / 3)
    assert meta["motion_kernel"] == "horizontal_uniform_1d"
    const, _ = degrade(np.full((9, 9), 0.4), width_px=9,
                       height_px=9, motion_length_px=5)
    assert np.allclose(const, 0.4)
