"""Safety smoke tests for the local P01 orchestrator, without FLIR or GPU."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "publications/P01/analyses/run_local_pipeline.py"
)
SPEC = importlib.util.spec_from_file_location("p01_local_pipeline", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_missing_archive_never_downloads_without_pinned_manifest(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="FLIR archive absent"):
        MODULE.acquire(tmp_path / "archive", None)
    assert not (tmp_path / "archive").exists()


def test_rights_acknowledgement_required(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as error:
        MODULE.main([
            "--parts-dir", str(tmp_path / "archive"),
            "--work-dir", str(tmp_path / "run"),
        ])
    assert error.value.code == 2
    assert not (tmp_path / "run").exists()


def test_output_inside_repository_rejected() -> None:
    with pytest.raises(SystemExit) as error:
        MODULE.main([
            "--parts-dir", str(MODULE.ROOT / "archive"),
            "--work-dir", str(MODULE.ROOT / "run"),
            "--rights-acknowledged",
        ])
    assert error.value.code == 2


def valid_public_record() -> dict:
    """Controlled validation-only publication fixture, no empirical observations."""
    return {
        "schema_version": 1,
        "generated_utc": "2026-11-23T09:00:00+00:00",
        "research_tier": "A_SOURCE_GT_RELATIVE_DESCRIPTIVE_CANDIDATE",
        "status": "VALIDATION_CANDIDATE_ONLY_UNFROZEN",
        "heldout_opened": False,
        "test_tuned": False,
        "physical_sensor_limit_claim": False,
        "rights_verified_independently": False,
        "native_optics_verified": False,
        "independent_acquisitions_verified": False,
        "checkpoint_sha256": "a" * 64,
        "train_annotation_sha256": "b" * 64,
        "validation_annotation_sha256": "c" * 64,
        "split_manifest_sha256": "d" * 64,
        "validation_predictions_sha256": "e" * 64,
        "source_part_sha256": {name: "f" * 64 for name in MODULE.PARTS},
        "training": {
            "model": "scratch_torchvision_frcnn_mobilenetv3_single_car",
            "seed": 20261121, "epochs": 1, "batch_size": 2,
            "device": "cpu", "torch": "2.9.0+cpu",
            "torchvision": "0.24.0", "loss_by_epoch": [
                {"epoch": 1, "train_mean_loss": 1.25},
            ],
        },
        "validation": {
            "status": "VALIDATION_CANDIDATE_ONLY",
            "threshold_candidate": {
                "status": "CANDIDATE_ONLY",
                "threshold": 0.5,
                "empirical_admission": False,
                "split_role": "declared_validation_unverified",
                "annotation_reference": "source_reference_unverified",
                "group_basis": "source_video_proxy",
                "threshold_selection": "lowest_feasible_sorted_unique_score",
                "score_inclusion_rule": "score >= threshold; ties indivisible",
                "frames": 250, "groups": 11,
                "limitations": "Observed validation FP/frame is not a future upper bound",
                "negative_frames": 30, "negative_groups": 3,
                "validation_fp_per_frame": 0.06, "validation_tp": 7,
                "validation_fp_bootstrap_ci_95": None,
                "validation_fp_upper_ci_exceeds_ceiling": None,
                "bootstrap_replicates": 0,
                "uncertainty_status": "SUPPRESSED_UNVERIFIED_GROUP_INDEPENDENCE",
            },
        },
        "limitations": [
            "Reference labels may be incomplete; FP/frame is source-label-relative.",
            "Video ID is not proof of independently acquired scenes.",
            "No test results, physical optical limits or scientific GO.",
        ],
    }


def test_validation_only_publication_schema_accepts_clean_fixture() -> None:
    MODULE.validate_public_summary(valid_public_record())


@pytest.mark.parametrize("field, contaminated", [
    ("training", {"training": {"torch": "2.9; token=private"}}),
    ("validation", {"validation": {"threshold_candidate": {"hidden": "/home/private"}}}),
    ("limitations", {"limitations": ["/home/private"]}),
    ("source_part_sha256", {"source_part_sha256": {"unexpected": "x" * 64}}),
    ("status", {"status": "BLOCKED_VALIDATION_NO_OPERATING_POINT"}),
])
def test_publication_schema_rejects_nested_tampering(field: str, contaminated: dict) -> None:
    record = valid_public_record()
    if field == "training":
        record["training"].update(contaminated["training"])
    elif field == "validation":
        record["validation"]["threshold_candidate"].update(
            contaminated["validation"]["threshold_candidate"]
        )
    else:
        record[field] = contaminated[field]
    with pytest.raises(ValueError):
        MODULE.validate_public_summary(record)


def test_publisher_requires_controller_approved_existing_pr(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(valid_public_record()), encoding="utf-8")
    calls = []

    def fake_command(args, *, capture=False):
        calls.append(args)
        if "pulls?state=open" in " ".join(args):
            return "[]"
        raise AssertionError("Publisher must stop before any branch or content mutation")

    monkeypatch.setattr(MODULE, "command", fake_command)
    with pytest.raises(ValueError, match="portfolio controller"):
        MODULE.publish(path)
    assert len(calls) == 1


def test_blocked_summary_cannot_be_published(monkeypatch, tmp_path: Path) -> None:
    record = valid_public_record()
    record["status"] = "BLOCKED_VALIDATION_NO_OPERATING_POINT"
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    monkeypatch.setattr(MODULE, "command", lambda *a, **k: pytest.fail(
        "No network access permitted for blocked evidence"
    ))
    with pytest.raises(ValueError, match="eligible validation-only"):
        MODULE.publish(path)
