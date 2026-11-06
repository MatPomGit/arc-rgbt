"""Synthetic contracts for P01 metadata-only group feasibility."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = (Path(__file__).resolve().parents[1] /
          "publications/P01/analyses/audit_group_feasibility.py")
spec = importlib.util.spec_from_file_location("p01_group_feasibility", SCRIPT)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)


def frame(fid, group, split, *, state="candidate_positive", small=1,
          intermediate=0, reference=1, viewpoint="front", contrast="low"):
    return {
        "frame_id": fid, "group_id": group, "split": split,
        "target_state": state, "small": small, "intermediate": intermediate,
        "reference": reference, "viewpoint": viewpoint, "contrast": contrast,
    }


def inventory():
    return {
        "schema_version": 1, "source_release": "synthetic-only",
        "group_basis": "video_id_proxy", "grid_basis": "export_grid_proxy",
        "frames": [
            frame("1", "g1", "train", small=2, reference=3),
            frame("2", "g1", "train", state="candidate_negative",
                  small=0, reference=0),
            frame("3", "g2", "validation", small=1, reference=1),
            frame("4", "g3", "validation", state="unknown",
                  small=None, intermediate=None, reference=None,
                  viewpoint="unknown", contrast="unknown"),
        ],
    }


def test_candidate_counts_and_no_scientific_promotion():
    report = audit.assess(inventory())
    assert report["status"] == "PROVISIONAL_METADATA_ONLY"
    assert report["empirical_admission"] is False
    assert report["independent_acquisitions_verified"] is False
    assert report["native_footprint_verified"] is False
    assert report["scientific_sample_size_approved"] is False
    assert report["test_outcomes_accessed"] is False
    assert report["frames_total"] == 4
    assert report["groups_declared_total"] == 3
    train = report["per_split"]["train"]
    val = report["per_split"]["validation"]
    assert train["candidate_bin_counts"] == {
        "small": 2, "intermediate": 0, "reference": 3
    }
    assert train["groups_with_both_candidate_bins"] == 1
    assert train["groups_with_at_least_two_per_primary_bin"] == 1
    assert train["groups_with_candidate_negatives"] == 1
    assert train["groups_only_candidate_negative"] == 0
    assert val["groups_with_unknown_frames"] == 1
    assert val["groups_missing_viewpoint"] == 1
    assert val["groups_missing_contrast"] == 1
    assert val["paired_small_targets_per_group"] == {
        "min": 1, "median": 1, "max": 1
    }


def test_group_crossing_train_validation_blocks_split_disjointness():
    data = inventory()
    data["frames"][2]["group_id"] = "g1"
    report = audit.assess(data)
    assert report["status"] == "BLOCKED_SPLIT_GROUP_OVERLAP"
    assert report["groups_declared_in_multiple_splits"] == 1
    assert report["independent_acquisitions_verified"] is False


def test_inventory_fingerprint_is_order_independent_but_binds_declarations():
    data = inventory()
    first = audit.assess(data)
    data["frames"].reverse()
    assert first == audit.assess(data)
    data["group_basis"] = "declared_acquisition"
    changed = audit.assess(data)
    assert changed["input_inventory_sha256"] != first["input_inventory_sha256"]
    assert changed["independent_acquisitions_verified"] is False


@pytest.mark.parametrize("mutation", [
    lambda d: d["frames"].append(d["frames"][0].copy()),
    lambda d: d["frames"][0].update(predictions=[]),
    lambda d: d["frames"][0].update(split="test"),
    lambda d: d["frames"][0].update(small=True),
    lambda d: d["frames"][0].update(small=-1),
    lambda d: d["frames"][1].update(reference=1),
    lambda d: d["frames"][3].update(small=0),
    lambda d: d["frames"][0].update(group_id=""),
    lambda d: d.update(grid_basis="unknown"),
    lambda d: d.update(group_basis="verified_independent"),
    lambda d: d.update(schema_version=True),
])
def test_invalid_metadata_fails_closed(mutation):
    data = inventory()
    mutation(data)
    with pytest.raises(ValueError):
        audit.assess(data)


def test_empty_train_split_is_reported_without_fake_support():
    data = inventory()
    for row in data["frames"]:
        row["split"] = "validation"
    report = audit.assess(data)
    assert report["per_split"]["train"]["groups_declared"] == 0
    assert report["per_split"]["train"]["paired_small_targets_per_group"] is None
    assert report["status"] == "PROVISIONAL_METADATA_ONLY"


def test_cli_creates_immutable_local_report(tmp_path):
    source = tmp_path / "source.json"
    target = tmp_path / "report.json"
    source.write_text(json.dumps(inventory()), encoding="utf-8")
    args = ["--input", str(source), "--output", str(target)]
    assert audit.main(args) == 0
    assert json.loads(target.read_text(encoding="utf-8")) == audit.assess(inventory())
    with pytest.raises(FileExistsError):
        audit.main(args)


def test_duplicate_raw_json_keys_rejected_before_write(tmp_path):
    source = tmp_path / "bad.json"
    dest = tmp_path / "report.json"
    source.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        audit.main(["--input", str(source), "--output", str(dest)])
    assert not dest.exists()


def test_oversized_input_is_rejected_before_read(tmp_path):
    source = tmp_path / "oversized.json"
    source.write_bytes(b"x" * (audit.MAX_INPUT_BYTES + 1))
    dest = tmp_path / "report.json"
    with pytest.raises(SystemExit):
        audit.main(["--input", str(source), "--output", str(dest)])
    assert not dest.exists()
