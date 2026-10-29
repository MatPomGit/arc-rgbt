"""Synthetic regression cases for explicitly bounded evaluation metrics."""

import copy

import pytest

from arc_rgbt.evaluation_contracts import detection_contract, tracking_reference_contract


def box(x, score=None):
    result = {"label": "vehicle", "bbox": [x, 0, 10, 10]}
    if score is not None:
        result["score"] = score
    return result


def frame(fid, truth, preds):
    return {"id": fid, "ground_truth": truth, "predictions": preds}


def test_perfect_ap_and_complete_negative_frame():
    frames = [frame("a", [box(0)], [box(0, 0.9)]),
              frame("b", [], [box(0, 0.2)])]
    r = detection_contract(frames, annotation_status="complete", operating_score=0.5)
    assert r["mean_ap"] == 1.0
    assert r["recall_at_operating_score"] == 1.0
    assert r["fp_per_frame"] == 0.0
    assert r["empirical_admission"] is False


def test_high_scored_false_positive_reduces_ap():
    r = detection_contract([frame("a", [box(0)], [box(30, 0.9), box(0, 0.5)])],
                           annotation_status="complete")
    assert r["mean_ap"] == pytest.approx(0.5)
    assert r["tp"] == 1 and r["fp"] == 1


def test_no_gt_and_no_predictions_have_explicit_null_denominators():
    r = detection_contract([frame("negative", [], [box(0, 0.9)])],
                           annotation_status="complete")
    assert r["mean_ap"] is None and r["recall_at_operating_score"] is None
    assert r["fp_per_frame"] == 1.0
    r = detection_contract([frame("positive", [box(0)], [])],
                           annotation_status="complete")
    assert r["mean_ap"] == 0.0 and r["precision_at_operating_score"] is None


@pytest.mark.parametrize("bad", [True, 0, 2, float("nan")])
def test_bad_iou_fails(bad):
    with pytest.raises(ValueError):
        detection_contract([frame("a", [box(0)], [])],
                           annotation_status="complete", iou_threshold=bad)


def test_incomplete_labels_fail():
    with pytest.raises(ValueError, match="Complete"):
        detection_contract([frame("a", [], [])], annotation_status="unknown")


def tracking():
    return [
        {"frame_id": "f0", "frame_index": 0, "annotation_status": "complete",
         "ground_truth": [{"track_id": "car", "label": "vehicle",
                           "bbox_xywh": [0, 0, 10, 10]}],
         "predictions": [{"track_id": "hyp", "label": "vehicle",
                          "bbox_xywh": [0, 0, 10, 10]}]},
        {"frame_id": "f1", "frame_index": 1, "annotation_status": "complete",
         "ground_truth": [], "predictions": []},
    ]


def test_track_reference_never_claims_hota_or_idf1():
    result = tracking_reference_contract(tracking())
    assert result["schema_validation"] == "PASS"
    assert result["hota"] is None and result["idf1"] is None
    assert result["empirical_admission"] is False


@pytest.mark.parametrize(("field", "bad", "message"), [
    ("frame_id", "f0", "frame ID"),
    ("frame_index", 0, "strictly"),
    ("annotation_status", "partial", "complete"),
])
def test_bad_tracking_frame_rejected(field, bad, message):
    data = tracking()
    data[1][field] = bad
    with pytest.raises(ValueError, match=message):
        tracking_reference_contract(data)


def test_duplicate_or_inconsistent_track_rejected():
    data = tracking()
    data[0]["ground_truth"].append(copy.deepcopy(data[0]["ground_truth"][0]))
    with pytest.raises(ValueError, match="Duplicate track"):
        tracking_reference_contract(data)
    data = tracking()
    data[1]["ground_truth"] = [{"track_id": "car", "label": "pedestrian",
                                "bbox_xywh": [0, 0, 1, 1]}]
    with pytest.raises(ValueError, match="class changes"):
        tracking_reference_contract(data)
