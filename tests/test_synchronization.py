import json

import pytest

from arc_rgbt.synchronization import main, pair_frames


def frame(i, stamp):
    return {"id": f"f-{i}", "timestamp_ns": stamp}


def test_nearest_unique_and_motion_skew_statistics():
    rgb = [frame(i, t) for i, t in enumerate([0, 33_000_000, 66_000_000, 99_000_000])]
    thermal = [frame(i, t) for i, t in enumerate([4_000_000, 100_000_000])]
    res = pair_frames(rgb, thermal, tolerance_ms=10, clock_domain="shared_monotonic_ns")
    assert [p["delta_ms"] for p in res["pairs"]] == [-4.0, -1.0]
    assert res["summary"]["matched"] == 2
    assert res["summary"]["absolute_delta_median_ms"] == 2.5
    assert res["summary"]["absolute_delta_p95_ms"] == pytest.approx(3.85)
    assert res["summary"]["unmatched_rgb"] == 2


def test_tolerance_inclusive_and_zero_match():
    result = pair_frames([frame("x", 1_000_000)], [frame("z", 0)],
                         tolerance_ms=1, clock_domain="shared_monotonic_ns")
    assert result["summary"]["matched"] == 1
    result = pair_frames([frame("x", 1_000_001)], [frame("z", 0)],
                         tolerance_ms=1, clock_domain="shared_monotonic_ns")
    assert result["summary"]["matched"] == 0
    assert result["summary"]["absolute_delta_p95_ms"] is None


def test_frame_never_reused():
    result = pair_frames([frame("a", 10)], [frame("a", 9), frame("b", 11)],
                         tolerance_ms=0.00001, clock_domain="shared_monotonic_ns")
    assert len(result["pairs"]) == 1
    assert result["summary"]["unmatched_thermal"] == 1


@pytest.mark.parametrize("rgb,thermal", [
    ([frame("a", 1), frame("b", 1)], []),
    ([frame("a", 2), frame("b", 1)], []),
    ([frame("a", -1)], []),
    ([{"id": "a", "timestamp_ns": True}], []),
    ([{"id": "a", "timestamp_ns": 1.4}], []),
    ([{"id": "a", "timestamp_ns": 1, "extra": 4}], []),
    ([], "not a list"),
])
def test_malformed_frame_stream_rejected(rgb, thermal):
    with pytest.raises(ValueError):
        pair_frames(rgb, thermal, tolerance_ms=10, clock_domain="shared_monotonic_ns")


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf"), True, "40"])
def test_invalid_tolerance_rejected(bad):
    with pytest.raises(ValueError):
        pair_frames([], [], tolerance_ms=bad, clock_domain="shared_monotonic_ns")


def test_shared_clock_is_mandatory():
    with pytest.raises(ValueError, match="calibrate clocks"):
        pair_frames([], [], tolerance_ms=1, clock_domain="unknown")


def test_cli_reports_exact_origin(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({
        "data_origin": "simulated", "clock_domain": "shared_monotonic_ns",
        "tolerance_ms": 5,
        "rgb_frames": [frame("a", 0)], "thermal_frames": [frame("t", 1_000_000)],
    }))
    dest = tmp_path / "summary.json"
    main(["--input", str(path), "--output", str(dest)])
    stored = json.loads(dest.read_text())
    assert stored["data_origin"] == "simulated"
    assert stored["summary"]["matched"] == 1
