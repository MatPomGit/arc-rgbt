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


def test_invalid_gt_bbox_is_rejected():
    with pytest.raises(ValueError, match="Invalid labelled"):
        evaluate([{"id": "bad", "ground_truth": [{"label": "object", "bbox": [0, 0, -1, 2]}],
                   "predictions": []}])


def test_only_negative_unannotated_frames_do_not_produce_metrics(tmp_path):
    with pytest.raises(ValueError, match="labelled ground truth"):
        report({"data_origin": "simulated", "config": {},
                "frames": [{"id": "empty", "ground_truth": [], "predictions": []}]}, tmp_path)


@pytest.mark.parametrize("bad_score", [None, float("nan"), float("inf"), True, -0.1, 1.1])
def test_prediction_confidence_must_be_validated_before_sorting(bad_score):
    frame = {"id": "1", "ground_truth": [{"label": "object", "bbox": [0, 0, 4, 4]}],
             "predictions": [{"label": "object", "bbox": [0, 0, 4, 4],
                              "score": bad_score}]}
    with pytest.raises(ValueError):
        evaluate([frame])


def test_duplicate_frame_identifier_rejected():
    frame = {"id": "duplicate", "ground_truth": [], "predictions": []}
    with pytest.raises(ValueError, match="unique"):
        evaluate([frame, frame])


def test_missing_score_and_nonfinite_iou_rejected():
    frame = {"id": "1", "ground_truth": [], "predictions":
             [{"label": "object", "bbox": [0, 0, 2, 2]}]}
    with pytest.raises(ValueError, match="schema"):
        evaluate([frame])
    with pytest.raises(ValueError, match="IoU"):
        evaluate([], float("nan"))


def test_complete_negative_frames_measure_false_positives(tmp_path):
    dataset = {
        "data_origin": "simulated",
        "annotation_status": "complete",
        "config": {"negative_frames": "verified empty annotations"},
        "frames": [
            {"id": "no-target-1", "ground_truth": [], "predictions": [
                {"label": "object", "bbox": [1, 2, 3, 4], "score": 0.7}
            ]},
            {"id": "no-target-2", "ground_truth": [], "predictions": []},
        ],
    }
    result = report(dataset, tmp_path)
    assert result["metrics"]["tp"] == 0
    assert result["metrics"]["fp"] == 1
    assert result["metrics"]["fn"] == 0
    assert result["metrics"]["frames"] == 2


def test_incomplete_annotation_status_is_rejected(tmp_path):
    dataset = {"data_origin": "simulated", "annotation_status": "partial",
               "config": {}, "frames": [{"id": "1", "ground_truth": [], "predictions": []}]}
    with pytest.raises(ValueError, match="annotation_status"):
        report(dataset, tmp_path)

def test_identical_extreme_boxes_fail_closed_instead_of_returning_zero_iou():
    box = {"label": "object", "bbox": [0.0, 0.0, 1e308, 1e308]}
    pred = {**box, "score": 1.0}
    frame = {"id": "extreme", "ground_truth": [box], "predictions": [pred]}
    with pytest.raises(ValueError, match="geometry"):
        evaluate([frame])
