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
