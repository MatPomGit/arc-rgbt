import math

import pytest

from arc_rgbt.sensorlab import Camera, geometry


def test_geometry_and_units():
    camera = Camera(80, 60, 17, 3.1)
    actual = geometry(camera, 10, 0.5, 1.7)
    assert math.isclose(actual["gsd_m_per_pixel"], 10 * 17e-6 / 3.1e-3)
    assert actual["object_width_native_px"] > 1
    assert 0 < actual["object_frame_coverage_fraction"] <= 1


def test_invalid_profile(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("width_px: 80\nheight_px: 60\npixel_pitch_mm: 17\nfocal_length_mm: 3")
    with pytest.raises(ValueError, match="Missing keys"):
        Camera.from_yaml(path)
    with pytest.raises(ValueError):
        geometry(Camera(80, 60, 17, 3.1), -1, 1, 1)
