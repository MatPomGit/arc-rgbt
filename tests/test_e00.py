import json

from arc_rgbt.e00 import NATIVE_SIZES, run


def test_e00_real_generated_reports_and_reproducibility(tmp_path):
    params = {"seed": 2, "frames": 3, "optical_sigma_px": 0.8,
              "noise_sigma": 0.02, "threshold": 0.45, "min_area_px": 1,
              "interpolated_preview_px": [640, 480]}
    a = run(params, tmp_path / "a")
    b = run(params, tmp_path / "b")
    assert len(a["resolutions"]) == len(NATIVE_SIZES) == 7
    assert a["physical_measurements"] is False
    assert [v["metrics"] for v in a["resolutions"]] == [v["metrics"] for v in b["resolutions"]]
    display_only = dict(params, interpolated_preview_px=[320, 240])
    c = run(display_only, tmp_path / "c")
    assert [v["metrics"] for v in a["resolutions"]] == [v["metrics"] for v in c["resolutions"]]
    assert (tmp_path / "a" / "metrics.csv").exists()
    assert (tmp_path / "a" / "report.html").exists()
    assert (tmp_path / "a" / "preview_8x8.png").exists()
    assert json.loads((tmp_path / "a" / "manifest.json").read_text())["data_origin"] == "simulated"
