"""Regression suite for bounded offline RGB/thermal sequence ingestion."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from arc_rgbt.sequence_audit import analyze, demo, main, run


def fixture(tmp_path, *, rgb_shape=(6, 8), thermal_shape=(3, 4),
            rgb_count=2, thermal_count=2):
    frames = tmp_path / "frames"
    frames.mkdir()
    rgb = []
    thermal = []
    for role, count, shape, dtype, offset in (
        ("rgb", rgb_count, rgb_shape, np.float32, 0),
        ("thermal", thermal_count, thermal_shape, np.uint16, 4_000_000),
    ):
        for i in range(count):
            path = f"frames/{role}-{i}.npy"
            np.save(tmp_path / path, np.full(shape, i + 1, dtype=dtype), allow_pickle=False)
            (rgb if role == "rgb" else thermal).append(
                {"id": f"{role}-{i}", "timestamp_ns": 33_000_000 * i + offset,
                 "path": path}
            )
    manifest = {
        "schema_version": 1, "data_origin": "simulated",
        "clock_domain": "shared_monotonic_ns", "tolerance_ms": 10,
        "rgb_frames": rgb, "thermal_frames": thermal,
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path, manifest


def test_demo_end_to_end_nonmatching_grids_and_unmatched_frame(tmp_path):
    folder = tmp_path / "demo"
    report = demo(folder)
    assert report["summary"]["matched"] == 2
    assert report["summary"]["unmatched_thermal"] == 1
    assert report["summary"]["different_native_grid_pairs"] == 2
    assert report["summary"]["equal_native_grid_pairs"] == 0
    assert report["data_origin"] == "simulated"
    assert sorted(p["delta_ms"] for p in report["pairs"]) == [-6.0, -4.0]
    assert {p["thermal_id"] for p in report["pairs"]} == {"thermal-0", "thermal-1"}
    for name in ("manifest.json", "report.json", "pairs.csv", "index.html",
                 "frames/rgb-0.npy", "frames/thermal-2.npy"):
        assert (folder / name).is_file()
    assert json.loads((folder / "report.json").read_text()) == report
    with pytest.raises(FileExistsError):
        demo(folder)


def test_real_manifest_timing_and_per_frame_sha_are_reproducible(tmp_path):
    path, manifest = fixture(tmp_path)
    output = tmp_path / "results"
    report = run(path, output)
    assert report["summary"]["matched"] == 2
    assert report["summary"]["absolute_delta_median_ms"] == 4
    assert report["manifest_sha256"] and len(report["manifest_sha256"]) == 64
    assert all(len(frame["sha256"]) == 64 for frame in report["thermal_frames"])
    assert report["thermal_frames"][0]["dtype"].endswith("u2")
    assert np.array_equal(np.load(tmp_path / manifest["thermal_frames"][0]["path"]),
                          np.ones((3, 4), dtype=np.uint16))
    with (output / "pairs.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2 and rows[0]["equal_native_grids"] == "False"
    assert "No clock" in (output / "index.html").read_text()
    with pytest.raises(FileExistsError):
        run(path, output)


def test_schema_and_timestamp_validation_precede_file_access(tmp_path):
    path, manifest = fixture(tmp_path)
    manifest["rgb_frames"][0]["timestamp_ns"] = 2**90
    with pytest.raises(ValueError, match="64-bit"):
        analyze(manifest, tmp_path)
    manifest["rgb_frames"][0]["timestamp_ns"] = 0
    manifest["rgb_frames"][0]["extra"] = "oops"
    with pytest.raises(ValueError, match="require"):
        analyze(manifest, tmp_path)
    manifest["rgb_frames"][0].pop("extra")
    manifest["schema_version"] = True
    with pytest.raises(ValueError, match="schema_version"):
        analyze(manifest, tmp_path)


@pytest.mark.parametrize("candidate", [
    "../escape.npy", "/etc/passwd.npy", "sub/../frame.npy",
    ".\\other.npy", "", "missing.json",
])
def test_path_traversal_or_non_numpy_suffix_rejected(tmp_path, candidate):
    _, manifest = fixture(tmp_path)
    manifest["rgb_frames"][0]["path"] = candidate
    with pytest.raises(ValueError):
        analyze(manifest, tmp_path)


def test_symlink_outside_source_directory_is_rejected(tmp_path):
    root = tmp_path / "data"
    root.mkdir()
    _, manifest = fixture(root)
    escape = tmp_path / "outside.npy"
    np.save(escape, np.zeros((6, 8), np.float32), allow_pickle=False)
    inside = root / "frames" / "escape.npy"
    try:
        inside.symlink_to(escape)
    except (NotImplementedError, OSError):
        pytest.skip("No symlink creation permission")
    manifest["rgb_frames"][0]["path"] = "frames/escape.npy"
    with pytest.raises(ValueError, match="escapes"):
        analyze(manifest, root)


@pytest.mark.parametrize("bad", [
    np.ones((4, 4), dtype=bool),
    np.ones((4, 4), dtype=np.complex64),
    np.ones((4, 4), dtype=np.uint64),
    np.ones((4, 4, 3), dtype=np.float32),
    np.full((4, 4), np.nan, dtype=np.float32),
])
def test_reject_non_numeric_or_invalid_thermal_data(tmp_path, bad):
    _, manifest = fixture(tmp_path)
    np.save(tmp_path / manifest["thermal_frames"][0]["path"], bad, allow_pickle=False)
    with pytest.raises(ValueError, match="Unsupported|Non-finite"):
        analyze(manifest, tmp_path)


def test_detect_shape_and_dtype_changes_without_upsampling(tmp_path):
    _, manifest = fixture(tmp_path)
    np.save(tmp_path / manifest["rgb_frames"][1]["path"], np.ones((7, 9), np.uint16),
            allow_pickle=False)
    report = analyze(manifest, tmp_path)
    assert report["summary"]["shape_changed_within_stream"]["rgb"]
    assert report["summary"]["dtype_changed_within_stream"]["rgb"]
    assert report["summary"]["different_native_grid_pairs"] == 2


def test_no_timing_match_still_produces_explicit_audit(tmp_path):
    _, manifest = fixture(tmp_path)
    manifest["tolerance_ms"] = 0
    report = analyze(manifest, tmp_path)
    assert report["summary"]["matched"] == 0
    assert report["summary"]["absolute_delta_p95_ms"] is None
    assert not report["pairs"]
    assert report["summary"]["unmatched_thermal"] == 2


def test_html_escaped_and_csv_formula_disarmed(tmp_path):
    _, manifest = fixture(tmp_path)
    manifest["rgb_frames"][0]["id"] = "=2+2<img src=x>"
    manifest["rgb_frames"][1]["id"] = "@SUM(1)"
    result = run_manifest_direct(manifest, tmp_path)
    assert "=2+2&lt;img" in (result / "index.html").read_text()
    assert "<img src=x>" not in (result / "index.html").read_text()
    with (result / "pairs.csv").open(encoding="utf-8", newline="") as stream:
        data = list(csv.DictReader(stream))
    assert data[0]["rgb_id"].startswith("'=") and data[1]["rgb_id"].startswith("'@")


def run_manifest_direct(manifest, tmp_path):
    file = tmp_path / "edited.json"
    file.write_text(json.dumps(manifest), encoding="utf-8")
    output = tmp_path / "result-1"
    run(file, output)
    return output


def test_cli_demo_and_argument_errors(tmp_path, capsys):
    main(["--demo", "--output", str(tmp_path / "cli-demo")])
    assert (tmp_path / "cli-demo" / "pairs.csv").is_file()
    assert "matched" in capsys.readouterr().out
    with pytest.raises(SystemExit) as raised:
        main(["--demo", "--input", "something.json"])
    assert raised.value.code == 2
