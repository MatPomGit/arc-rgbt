"""Synthetic tests for separate P01 QA reviewer forms and reconciliation."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = (Path(__file__).resolve().parents[1] /
          "publications/P01/analyses/reconcile_blinded_qa.py")
spec = importlib.util.spec_from_file_location("p01_reviewer_qa", SCRIPT)
qa = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(qa)


def sample_plan(tmp_path):
    plan = {
        "schema_version": 1,
        "status": "SAMPLE_PLAN_ONLY",
        "empirical_admission": False,
        "blinded_source_qa_executed": False,
        "inventory_sha256": "a" * 64,
        "frame_inventory_sha256": "b" * 64,
        "selected_frames": [
            {"frame_id": f"val:g1:{i}", "stratum": ("A", "B", "C")[i],
             "risk_flags": ["qa_missing", "class_conflict", "candidate_negative"][i:i+1]}
            for i in range(3)
        ],
    }
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan), encoding="utf-8")
    return p


def templates(tmp_path):
    p = sample_plan(tmp_path)
    a, b = tmp_path / "review-a.csv", tmp_path / "review-b.csv"
    report = qa.prepare(p, a, b)
    return p, a, b, report


def complete_sheet(path, *, override=None):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = [dict(row) for row in reader]
    for row in rows:
        row.update(coverage="complete", target_present="yes",
                   labels="correct", boxes="correct",
                   missing_targets="0", reason_code="none")
        if override and row["frame_id"].endswith(":1"):
            row.update(override)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=qa.FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_prepare_blinds_risk_flags_and_separates_reviewer_sheets(tmp_path):
    p, a, b, info = templates(tmp_path)
    assert info["sample_frames"] == 3
    assert info["status"] == "BLINDED_REVIEW_TEMPLATES_ONLY"
    assert not info["source_admitted"]
    for path in (a, b):
        text = path.read_text(encoding="utf-8")
        assert "qa_missing" not in text
        assert "class_conflict" not in text
        assert "candidate_negative" not in text
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 3
        assert all(row["coverage"] == "" for row in rows)
    with pytest.raises(FileExistsError):
        qa.prepare(p, a, b)


def test_uncompleted_templates_cannot_be_reconciled(tmp_path):
    p, a, b, _ = templates(tmp_path)
    with pytest.raises(ValueError, match="Uncompleted"):
        qa.reconcile(p, a, b)


def test_two_matching_reviews_remain_not_admitted(tmp_path):
    p, a, b, _ = templates(tmp_path)
    complete_sheet(a)
    complete_sheet(b)
    r = qa.reconcile(p, a, b)
    assert r["status"] == "REVIEW_RECORDS_COLLECTED_NOT_ADMITTED"
    assert r["verdict_agreement_rate"] == 1
    assert r["pending_adjudication"] == []
    assert r["counts"]["target_presence_agreement"] == 3
    assert not r["source_admitted"]
    assert not r["independence_of_reviewers_verified"]
    assert r["confirmatory_fp_frame_status"] == "BLOCKED"


def test_disagreement_and_concordant_defect_need_adjudication(tmp_path):
    p, a, b, _ = templates(tmp_path)
    complete_sheet(a, override={"coverage": "incomplete",
                                "missing_targets": "1", "reason_code": "MISSING_GT"})
    complete_sheet(b)
    r = qa.reconcile(p, a, b)
    assert r["status"] == "MANUAL_ADJUDICATION_REQUIRED"
    assert r["counts"]["verdict_disagreement"] == 1
    assert r["pending_adjudication"][0]["reason"] == "reviewer_disagreement"
    complete_sheet(b, override={"coverage": "incomplete",
                                "missing_targets": "1", "reason_code": "MISSING_GT"})
    rr = qa.reconcile(p, a, b)
    assert rr["counts"]["verdict_agreement"] == 3
    assert rr["pending_adjudication"][0]["reason"] == "defect_adjudication_required"


def test_uncertain_consensus_requires_human_review(tmp_path):
    p, a, b, _ = templates(tmp_path)
    complete_sheet(a, override={"target_present": "uncertain"})
    complete_sheet(b, override={"target_present": "uncertain"})
    r = qa.reconcile(p, a, b)
    assert r["status"] == "MANUAL_ADJUDICATION_REQUIRED"
    assert r["pending_adjudication"][0]["reason"] == "uncertain_unresolved"


@pytest.mark.parametrize("override, error", [
    ({"coverage": "complete", "missing_targets": "1"}, "complete coverage"),
    ({"target_present": "no", "missing_targets": "1",
      "coverage": "incomplete"}, "No-target"),
    ({"coverage": "invalid"}, "coverage"),
    ({"missing_targets": "-1"}, "missing_targets"),
    ({"reason_code": "=WEBSERVICE"}, "reason_code"),
])
def test_invalid_reviewer_values_fail_closed(tmp_path, override, error):
    p, a, b, _ = templates(tmp_path)
    complete_sheet(a, override=override)
    complete_sheet(b)
    with pytest.raises(ValueError, match=error):
        qa.reconcile(p, a, b)


def test_duplicate_or_missing_reviewed_frames_fail_closed(tmp_path):
    p, a, b, _ = templates(tmp_path)
    complete_sheet(a)
    complete_sheet(b)
    with b.open("a", encoding="utf-8") as stream:
        stream.write("val:g1:0,complete,yes,correct,correct,0,none\n")
    with pytest.raises(ValueError, match="duplicate"):
        qa.reconcile(p, a, b)


def test_same_reviewer_path_and_duplicate_json_keys_rejected(tmp_path):
    p, a, b, _ = templates(tmp_path)
    complete_sheet(a)
    with pytest.raises(ValueError, match="distinct source files"):
        qa.reconcile(p, a, a)
    p.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        qa.reconcile(p, a, b)


def test_cli_prepare_and_reconcile_safeguards(tmp_path):
    p = sample_plan(tmp_path)
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    assert qa.main(["prepare", "--plan", str(p),
                    "--reviewer-a", str(a), "--reviewer-b", str(b)]) == 0
    complete_sheet(a)
    complete_sheet(b)
    output = tmp_path / "audit.json"
    assert qa.main(["reconcile", "--plan", str(p), "--reviewer-a", str(a),
                    "--reviewer-b", str(b), "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["source_admitted"] is False
    with pytest.raises(SystemExit):
        qa.main(["reconcile", "--plan", str(p), "--reviewer-a", str(a),
                 "--reviewer-b", str(b), "--output", str(output)])
