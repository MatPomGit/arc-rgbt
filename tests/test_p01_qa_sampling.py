"""Synthetic tests for the metadata-only P01 blinded QA selection tool."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = (Path(__file__).resolve().parents[1] /
          "publications/P01/analyses/select_blinded_qa.py")
spec = importlib.util.spec_from_file_location("p01_qa_sample", SCRIPT)
qa = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(qa)


def frame(fid, group, *, qa_state="approved", negative=False, positive=True,
          conflict=False):
    return {
        "frame_id": fid, "group_id": group, "qa_state": qa_state,
        "class_conflict": conflict, "geometry_conflict": False,
        "clipped_box": False, "rider_only": False,
        "candidate_negative": negative, "target_positive": positive,
    }


def inventory():
    return {
        "schema_version": 1, "source_release": "synthetic-only",
        "group_basis": "video_id_proxy",
        "frames": [
            frame("a", "g1", qa_state="missing"),
            frame("b", "g2", conflict=True),
            frame("c", "g3", negative=True, positive=False),
            frame("d", "g4"),
        ],
    }


def sample(data, quotas=None, **kwargs):
    return qa.plan_sample(
        data, quotas=quotas or dict.fromkeys(qa.STRATA, 1),
        seed=42, max_per_group=1, **kwargs,
    )


def test_selection_is_reproducible_and_overlaps_count_once():
    data = inventory()
    data["frames"][0]["candidate_negative"] = True
    data["frames"][0]["target_positive"] = False
    a = sample(data)
    data["frames"].reverse()
    b = sample(data)
    assert a == b
    assert a["status"] == "SAMPLE_PLAN_ONLY"
    assert a["population_strata"] == dict.fromkeys(qa.STRATA, 1)
    assert len(a["selected_frames"]) == 4
    assert a["selected_frames"][0]["stratum"] == "A"
    assert "candidate_negative" in a["selected_frames"][0]["risk_flags"]
    assert a["empirical_admission"] is False
    assert a["blinded_source_qa_executed"] is False
    assert a["group_basis_verified"] is False
    assert all(row["reviewer_a"] is None for row in a["selected_frames"])


def test_group_cap_detects_incomplete_sample_and_does_not_impute_reviews():
    data = inventory()
    for row in data["frames"]:
        row["group_id"] = "same-video"
    report = sample(data)
    assert report["status"] == "SAMPLE_PLAN_INCOMPLETE"
    assert len(report["selected_frames"]) == 1
    assert sum(report["shortfalls"].values()) == 3


@pytest.mark.parametrize("bad", [
    lambda d: d["frames"].append(d["frames"][0].copy()),
    lambda d: d["frames"][0].update(predictions=[]),
    lambda d: d["frames"][0].update(target_positive=True, candidate_negative=True),
    lambda d: d["frames"][0].update(qa_state="unknown"),
    lambda d: d["frames"][0].update(class_conflict=1),
    lambda d: d.update(group_basis="independent_proven"),
    lambda d: d["frames"][0].update(group_id=""),
])
def test_invalid_source_metadata_fails_closed(bad):
    data = inventory()
    bad(data)
    with pytest.raises(ValueError):
        sample(data)


def test_unclassified_frame_rejected():
    data = inventory()
    data["frames"][0] = frame("a", "g1", positive=False)
    with pytest.raises(ValueError, match="Unclassified"):
        sample(data)


def test_quota_validation_and_zero_quota_allowed():
    data = inventory()
    with pytest.raises(ValueError, match="quotas"):
        sample(data, quotas={"A": 1})
    report = sample(data, quotas={"A": 1, "B": 0, "C": 0, "D": 0})
    assert len(report["selected_frames"]) == 1
    assert report["status"] == "SAMPLE_PLAN_ONLY"


def test_cli_writes_an_offline_manifest_and_refuses_overwrite(tmp_path):
    source = tmp_path / "local-metadata.json"
    dest = tmp_path / "qa-selection.json"
    raw = json.dumps(inventory(), sort_keys=True)
    source.write_text(raw, encoding="utf-8")
    arguments = ["--input", str(source), "--output", str(dest),
                 "--seed", "42", "--max-per-group", "1",
                 "--quotas", "A=1,B=1,C=1,D=1"]
    assert qa.main(arguments) == 0
    expected = json.loads(dest.read_text(encoding="utf-8"))
    assert expected == sample(inventory())
    assert source.read_text(encoding="utf-8") == raw
    with pytest.raises(FileExistsError):
        qa.main(arguments)


def test_cli_rejects_duplicate_json_keys(tmp_path):
    source, dest = tmp_path / "input.json", tmp_path / "out.json"
    source.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        qa.main(["--input", str(source), "--output", str(dest),
                 "--seed", "42", "--max-per-group", "1",
                 "--quotas", "A=1,B=1,C=1,D=1"])
    assert not dest.exists()
