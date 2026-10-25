import copy
import csv
import json

import pytest

from arc_rgbt.e01 import METHODS, main, run


def _box(x, score=None):
    obj = {"label": "person", "bbox": [x, 2, 10, 10]}
    if score is not None:
        obj["score"] = score
    return obj


def example():
    return {
        "experiment": "E01", "data_origin": "simulated",
        "quality_origin": "synthetic_scenario", "annotation_status": "complete",
        "config": {"iou_threshold": 0.5, "min_effective_score": 0.25},
        "frames": [
            {"id": "positive", "ground_truth": [_box(2)],
             "rgb_predictions": [_box(2, 0.9)],
             "thermal_predictions": [_box(80, 0.95)],
             "quality": {"rgb": 1.0, "thermal": 0.1}},
            {"id": "negative", "ground_truth": [],
             "rgb_predictions": [],
             "thermal_predictions": [_box(80, 0.9)],
             "quality": {"rgb": 0.8, "thermal": 0.1}},
        ],
    }


def test_quality_weighted_fusion_improves_synthetic_sanity_case(tmp_path):
    sample = example()
    unchanged = copy.deepcopy(sample)
    result = run(sample, tmp_path)
    assert sample == unchanged
    assert result["data_origin"] == "simulated"
    assert result["quality_origin"] == "synthetic_scenario"
    assert list(result["metrics"]) == list(METHODS)
    fixed = result["metrics"]["fixed_fusion"]
    adaptive = result["metrics"]["quality_aware_fusion"]
    assert adaptive["fp"] < fixed["fp"]
    assert adaptive["tp"] == fixed["tp"] == 1
    assert adaptive["f1"] > fixed["f1"]
    assert (tmp_path / "manifest.json").exists()
    with (tmp_path / "metrics.csv").open(newline="") as stream:
        assert len(list(csv.DictReader(stream))) == 4


def test_deterministic_outputs(tmp_path):
    sample = example()
    a = run(sample, tmp_path / "a")
    b = run(sample, tmp_path / "b")
    assert a["metrics"] == b["metrics"]
    assert (tmp_path / "a" / "metrics.csv").read_bytes() == (
        tmp_path / "b" / "metrics.csv").read_bytes()


@pytest.mark.parametrize("change", [
    {"data_origin": "unknown"},
    {"quality_origin": "oracle_measured"},
    {"annotation_status": "partial"},
    {"frames": []},
    {"experiment": "bad"},
    {"config": {"iou_threshold": 0, "min_effective_score": 0.25}},
])
def test_invalid_manifest_rejected_without_artifacts(tmp_path, change):
    dest = tmp_path / "denied"
    with pytest.raises(ValueError):
        run({**example(), **change}, dest)
    assert not dest.exists()


def test_duplicate_frames_and_malformed_quality_rejected(tmp_path):
    sample = example()
    sample["frames"].append(copy.deepcopy(sample["frames"][0]))
    with pytest.raises(ValueError, match="unique"):
        run(sample, tmp_path / "dup")
    sample = example()
    sample["frames"][0]["quality"]["rgb"] = float("nan")
    with pytest.raises(ValueError, match="quality"):
        run(sample, tmp_path / "nan")


def test_reject_invalid_detector_score(tmp_path):
    sample = example()
    sample["frames"][0]["rgb_predictions"][0]["score"] = True
    with pytest.raises(ValueError, match="score"):
        run(sample, tmp_path / "invalid")


def test_e01_cli_and_sha256_provenance(tmp_path):
    dataset = tmp_path / "scenario.json"
    dataset.write_text(json.dumps(example()))
    output = tmp_path / "result"
    main(["--dataset", str(dataset), "--output", str(output)])
    result = json.loads((output / "manifest.json").read_text())
    assert result["provenance"]["input_sha256"][str(dataset)]
    assert result["quality_origin"] == "synthetic_scenario"


def test_integer_zero_frame_id_matches_benchmark_schema(tmp_path):
    dataset = example()
    dataset["frames"][0]["id"] = 0
    result = run(dataset, tmp_path / "zero-id")
    assert result["metrics"]["rgb_only"]["frames"] == 2
