"""No third-party code or external data is executed in ordinary CI."""

from __future__ import annotations

import copy
import json

import pytest

from arc_rgbt import cli
from arc_rgbt.trackeval_adapter import PINNED_SHA, audit, prepare, run


def frame(index, *, gt=None, pred=None):
    return {
        "frame_id": f"f-{index}", "frame_index": index,
        "annotation_status": "complete", "ground_truth": gt or [],
        "predictions": pred or [],
    }


def obj(track_id, *, label="vehicle", x=0):
    return {"track_id": track_id, "label": label, "bbox_xywh": [x, 0, 10, 10]}


def perfect():
    return [
        frame(0, gt=[obj("real")], pred=[obj("hyp")]),
        frame(1, gt=[obj("real")], pred=[obj("hyp")]),
    ]


def test_perfect_sequence_exports_exact_trackeval_arrays_without_executing():
    frames = perfect()
    before = copy.deepcopy(frames)
    cases = prepare(frames)
    assert frames == before
    assert cases == {
        "vehicle": {
            "num_timesteps": 2, "num_gt_ids": 1, "num_tracker_ids": 1,
            "num_gt_dets": 2, "num_tracker_dets": 2,
            "gt_ids": [[0], [0]], "tracker_ids": [[0], [0]],
            "similarity_scores": [[[1.0]], [[1.0]]],
        }
    }
    result = audit(frames)
    assert result["evaluation_status"] == "DRY_RUN_REFERENCE_NOT_EXECUTED"
    assert result["results"] == {"vehicle": {"hota": None, "idf1": None}}
    assert result["reference_sha"] == PINNED_SHA
    assert result["empirical_admission"] is False


def test_missing_tracks_and_cross_class_labels_are_not_falsely_matched():
    frames = [
        frame(0, gt=[obj("person", label="pedestrian")],
              pred=[obj("vehicle_tracker", label="vehicle")]),
        frame(1, gt=[obj("person", label="pedestrian")], pred=[]),
    ]
    cases = prepare(frames)
    assert cases["pedestrian"]["num_gt_dets"] == 2
    assert cases["pedestrian"]["num_tracker_dets"] == 0
    assert cases["vehicle"]["num_tracker_dets"] == 1
    assert cases["vehicle"]["num_gt_dets"] == 0
    assert cases["pedestrian"]["similarity_scores"] == [[[]], [[]]]


def test_crossing_label_and_reused_pred_tracks_use_distinct_role_dictionaries():
    frames = [
        frame(0, gt=[obj("same")], pred=[obj("same")]),
        frame(1, gt=[obj("same")], pred=[obj("new")]),
    ]
    cases = prepare(frames)
    assert cases["vehicle"]["num_gt_ids"] == 1
    assert cases["vehicle"]["num_tracker_ids"] == 2
    assert cases["vehicle"]["tracker_ids"] == [[1], [0]]


@pytest.mark.parametrize("bad", [
    [frame(1, gt=[obj("a")])],
    [frame(0, gt=[obj("a")]), frame(2, gt=[obj("a")])],
    [frame(0, gt=[obj("a")], pred=[obj("b")],)],
    [],
])
def test_invalid_time_or_empty_cases_fail_or_explicit_dry_run(bad):
    if not bad:
        with pytest.raises(ValueError):
            prepare(bad)
    elif bad[0]["frame_index"] != 0 or len(bad) > 1 and bad[-1]["frame_index"] != 1:
        with pytest.raises(ValueError, match="contiguous"):
            prepare(bad)
    else:
        assert audit(bad)["reference_execution"] is False


def test_cannot_execute_without_explicit_trusted_checkout(tmp_path):
    with pytest.raises(ValueError, match="requires"):
        audit(perfect(), run_reference=True)
    with pytest.raises(ValueError, match="without explicit"):
        audit(perfect(), reference_root=tmp_path)
    with pytest.raises(ValueError, match="TrackEval source checkout"):
        audit(perfect(), reference_root=tmp_path, run_reference=True)


def test_json_cli_dry_run_reproducible_and_refuses_overwrite(tmp_path, capsys):
    path = tmp_path / "tracking.json"
    path.write_text(json.dumps({
        "schema_version": 1, "data_origin": "synthetic",
        "sequence_id": "synthetic-flight", "frames": perfect(),
    }), encoding="utf-8")
    expected = run(path)
    target = tmp_path / "tracking-report.json"
    assert cli.main(["trackeval", "--input", str(path), "--output", str(target)]) == 0
    assert json.loads(capsys.readouterr().out) == expected
    assert json.loads(target.read_text(encoding="utf-8")) == expected
    with pytest.raises(SystemExit):
        cli.main(["trackeval", "--input", str(path), "--output", str(target)])


def test_schema_missing_frame_and_unknown_status_are_rejected(tmp_path):
    path = tmp_path / "tracking.json"
    for payload in [
        {"schema_version": 1, "data_origin": "synthetic", "frames": perfect()},
        {"schema_version": True, "data_origin": "synthetic",
         "sequence_id": "seq", "frames": perfect()},
        {"schema_version": 1, "data_origin": "real",
         "sequence_id": "seq", "frames": perfect()},
    ]:
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError):
            run(path)
    frames = perfect()
    frames[0]["annotation_status"] = "unknown"
    with pytest.raises(ValueError, match="complete"):
        prepare(frames)



def test_committed_tracking_fixture_is_dry_run():
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "datasets/manifests/tracking-synthetic.json"
    r = run(path)
    assert r["sequence_id"] == "synthetic-tracking-example"
    assert r["results"]["vehicle"] == {"hota": None, "idf1": None}
    assert r["reference_execution"] is False


def test_official_sanity_cases_are_embedded_but_not_auto_executed():
    from arc_rgbt.trackeval_adapter import _REFERENCE_SCRIPT

    assert "no_confusion" in _REFERENCE_SCRIPT
    assert "8 / 17" in _REFERENCE_SCRIPT
    assert "Perfect-track" in _REFERENCE_SCRIPT
