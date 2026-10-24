import json

import pytest

from arc_rgbt.bench import evaluate, report


def test_real_matching_and_reports(tmp_path):
    frames = [{"id": "1", "ground_truth": [{"label": "object", "bbox": [0, 0, 10, 10]}],
               "predictions": [{"label": "object", "bbox": [0, 0, 10, 10], "score": 1.0},
                               {"label": "object", "bbox": [50, 50, 10, 10], "score": 0.7}]}]
    data = {"data_origin": "simulated", "config": {"case": "unit"}, "frames": frames}
    result = report(data, tmp_path)
    assert result["metrics"]["tp"] == 1
    assert result["metrics"]["fp"] == 1
    assert result["metrics"]["fn"] == 0
    assert (tmp_path / "bench.html").is_file()
    assert (tmp_path / "bench.csv").is_file()
    assert json.loads((tmp_path / "bench.json").read_text())["data_origin"] == "simulated"


def test_no_unlabelled_detection_metrics(tmp_path):
    with pytest.raises(ValueError, match="labelled"):
        report({"data_origin": "simulated", "config": {}, "frames": []}, tmp_path)
    with pytest.raises(ValueError):
        evaluate([], 0)
