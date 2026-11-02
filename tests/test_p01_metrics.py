"""Synthetic tests of prospective, explicitly unverified P01 metrics."""

import pytest

from arc_rgbt.p01_metrics import choose_validation_threshold, native_footprint_recall


def box(x, size, score=None, label="vehicle"):
    obj = {"label": label, "bbox": [x, 0, size, size]}
    if score is not None:
        obj["score"] = score
    return obj


def frame(fid, gt, pred):
    return {"id": fid, "ground_truth": gt, "predictions": pred}


def run(frames, groups, **kwargs):
    return native_footprint_recall(
        frames, acquisition_ids=groups, annotation_status="complete",
        grid_origin="original_native", **kwargs,
    )


def test_gt_footprint_bins_duplicates_wrong_class_and_negative_frames():
    frames = [
        frame("a", [box(0, 4), box(40, 20), box(80, 10)],
              [box(40, 20, 0.95, "person"), box(0, 4, 0.9), box(0, 4, 0.8)]),
        frame("b", [], [box(60, 5, 0.75)]),
    ]
    result = run(frames, ["flight", "flight"])
    assert [(x["bin"], x["matched"]) for x in result["per_object"]] == [
        ("small", True), ("reference", False), ("intermediate", False),
    ]
    assert result["per_bin"]["small"]["recall"] == 1.0
    assert result["per_bin"]["reference"]["recall"] == 0.0
    assert result["fp"] == 3 and result["fp_per_frame"] == 1.5
    assert result["primary_group_mean_delta"] is None
    assert result["empirical_admission"] is False


def test_ten_paired_groups_equal_weight_bootstrap_seed():
    frames, groups = [], []
    for idx in range(10):
        pred = box(0, 4, 0.9) if idx < 5 else box(40, 20, 0.9)
        frames.append(frame(str(idx), [box(0, 4), box(40, 20)], [pred]))
        groups.append(f"g{idx}")
    result = run(frames, groups)
    assert result["groups_with_both_bins"] == 10
    assert result["status"] == "PROSPECTIVE_UNFROZEN"
    assert result["primary_group_mean_delta"] == 0.0
    assert result["candidate_percentile_ci_95"] == run(
        frames, groups)["candidate_percentile_ci_95"]
    assert result["candidate_percentile_ci_95"][0] < 0
    assert result["candidate_percentile_ci_95"][1] > 0


def test_unpaired_groups_are_not_pseudopaired():
    result = run([frame("a", [box(0, 4)], []),
                  frame("b", [box(0, 20)], [])], ["a", "b"])
    assert result["groups_with_both_bins"] == 0
    assert result["candidate_percentile_ci_95"] is None


@pytest.mark.parametrize("grid", ["aligned_crop", "unknown", ""])
def test_resized_or_unknown_grid_rejected(grid):
    with pytest.raises(ValueError, match="Original-native"):
        native_footprint_recall([frame("a", [], [])],
                                acquisition_ids=["g"], annotation_status="complete",
                                grid_origin=grid)


def test_incomplete_labels_and_invalid_groups_rejected():
    with pytest.raises(ValueError, match="Complete"):
        native_footprint_recall([frame("a", [], [])],
                                acquisition_ids=["g"], annotation_status="partial",
                                grid_origin="original_native")
    with pytest.raises(ValueError, match="acquisition ID"):
        run([frame("a", [], [])], [""])


def test_validation_threshold_is_not_selected_from_test_frames():
    frames = [frame(str(i), [], [box(0, 4, 0.6)] if 1 <= i <= 21 else [])
              for i in range(200)]
    frames[0]["ground_truth"] = [box(0, 4)]
    frames[0]["predictions"] = [box(0, 4, 0.8)]
    result = choose_validation_threshold(
        frames, acquisition_ids=[f"g{i // 20}" for i in range(200)],
        annotation_status="complete",
    )
    assert result["status"] == "CANDIDATE_ONLY"
    assert result["threshold"] == 0.8
    assert result["validation_fp_per_frame"] == 0


def test_validation_size_and_no_tp_block_selection():
    one = [frame("a", [box(0, 4)], [box(0, 4, 0.9)])]
    result = choose_validation_threshold(
        one, acquisition_ids=["g"], annotation_status="complete")
    assert result["status"] == "BLOCKED_VALIDATION_SIZE"
    assert result["threshold"] is None
    negatives = [frame(str(i), [], [box(0, 4, 0.9)]) for i in range(200)]
    result = choose_validation_threshold(
        negatives, acquisition_ids=[str(i // 20) for i in range(200)],
        annotation_status="complete")
    assert result["status"] == "BLOCKED_NO_TRUE_POSITIVES"
    assert result["threshold"] is None


def test_bin_edges_are_unambiguous():
    result = run([frame("x", [box(0, 8), box(20, 16)], [])], ["g"])
    assert [x["bin"] for x in result["per_object"]] == ["intermediate", "reference"]
