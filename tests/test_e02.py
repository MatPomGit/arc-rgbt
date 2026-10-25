import csv
import json

import pytest

from arc_rgbt.e02 import _horizontal_geometric_iou, run, simulate


def scenario():
    return {
        "rgb_fps": 30, "thermal_fps": 9, "frames": 10, "tolerance_ms": 25,
        "thermal_start_offsets_ms": [0, 10, 25],
        "native_thermal_sizes_px": [[8, 8], [80, 60], [320, 240]],
        "horizontal_fov_deg": 35,
        "target_range_m": 20,
        "target_width_m": 0.6,
        "lateral_speeds_m_s": [0, 3, 6],
    }


def test_expected_scenario_and_determinism(tmp_path):
    a = simulate(scenario())
    b = simulate(scenario())
    assert a == b
    assert a["data_origin"] == "simulated"
    assert a["metric_origin"] == "analytical_geometry"
    assert a["physical_measurements"] is False
    assert len(a["rows"]) == 27
    assert all(row["matched_pairs"] == 10 for row in a["rows"])
    assert all(row["median_geometric_bbox_iou"] == 1 for row in a["rows"]
               if row["lateral_speed_m_s"] == 0)
    assert all(0 <= row["min_geometric_bbox_iou"] <= 1 for row in a["rows"])
    report = run(scenario(), tmp_path)
    assert report["rows"] == a["rows"]
    assert json.loads((tmp_path / "manifest.json").read_text())["experiment"] == "E02"
    with (tmp_path / "geometry.csv").open(newline="") as fh:
        assert len(list(csv.DictReader(fh))) == 27


def test_normalized_geometric_overlap_not_claimed_as_resolution_benefit():
    output = simulate(scenario())
    low = output["rows"][1]  # 8x8, offset 0, speed 3
    higher = output["rows"][4]  # 80x60, offset 0, speed 3
    assert low["target_width_native_px"] < higher["target_width_native_px"]
    assert low["median_geometric_bbox_iou"] == pytest.approx(
        higher["median_geometric_bbox_iou"])


def test_temporal_shift_lowers_iou_and_zero_pair_avoids_fake_scores():
    zero = simulate({**scenario(), "tolerance_ms": 0,
                     "thermal_start_offsets_ms": [10]})
    for row in zero["rows"]:
        assert row["matched_pairs"] == 0
        assert row["median_geometric_bbox_iou"] is None
    assert _horizontal_geometric_iou(10, 0) == 1
    assert _horizontal_geometric_iou(10, 10) == 0
    assert _horizontal_geometric_iou(10, 2) == pytest.approx(8 / 12)


@pytest.mark.parametrize("change", [
    {"rgb_fps": 0}, {"thermal_fps": float("inf")}, {"frames": True},
    {"frames": 501}, {"tolerance_ms": -1}, {"horizontal_fov_deg": 180},
    {"target_range_m": 0}, {"target_width_m": float("nan")},
    {"native_thermal_sizes_px": [[0, 80]]},
    {"native_thermal_sizes_px": [[8, 8], [8, 8]]},
    {"native_thermal_sizes_px": [[80, True]]},
    {"lateral_speeds_m_s": [False]},
])
def test_invalid_configuration_is_rejected_before_writing(tmp_path, change):
    destination = tmp_path / "denied"
    with pytest.raises(ValueError):
        run({**scenario(), **change}, destination)
    assert not destination.exists()


def test_tolerance_can_reduce_pairs():
    no_pair = simulate({**scenario(), "tolerance_ms": 0,
                        "thermal_start_offsets_ms": [10]})
    loose = simulate({**scenario(), "tolerance_ms": 25,
                      "thermal_start_offsets_ms": [10]})
    assert no_pair["synchronization"][0]["summary"]["matched"] == 0
    assert loose["synchronization"][0]["summary"]["matched"] > 0

@pytest.mark.parametrize("field", ["rgb_fps", "thermal_fps"])
def test_extremely_small_fps_is_rejected_before_period_conversion(field):
    values = {**scenario(), field: 1e-300}
    with pytest.raises(ValueError, match="FPS"):
        simulate(values)
