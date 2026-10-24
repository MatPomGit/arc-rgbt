import importlib.util
from pathlib import Path

import pytest

from arc_rgbt.e00 import run

SCRIPT = Path(__file__).resolve().parents[1] / "publications/P01/analyses/summarize_e00.py"


def test_p01_reproducible_analysis_and_source_guard(tmp_path):
    spec = importlib.util.spec_from_file_location("p01_analysis", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    config = {"seed": 2, "frames": 2, "optical_sigma_px": 0.8,
              "noise_sigma": 0.02, "threshold": 0.45, "min_area_px": 1,
              "interpolated_preview_px": [64, 48]}
    root = tmp_path / "e00"
    run(config, root)
    result = module.summarize(root, tmp_path / "analysis.json")
    assert result["data_origin"] == "simulated"
    assert result["physical_measurements"] is False
    assert len(result["localization_metrics_by_native_resolution"]) == 7
    bad = root / "manifest.json"
    bad.write_text(bad.read_text().replace('"data_origin": "simulated"',
                                           '"data_origin": "measured"', 1))
    with pytest.raises(ValueError, match="simulated"):
        module.summarize(root, tmp_path / "rejected.json")
