"""Synthetic-only tests for metadata admission; no external data are imported."""

from __future__ import annotations

import copy
import json

import pytest

from arc_rgbt import admission, cli


def manifest():
    digest = lambda n: f"{n:064x}"
    return {
        "schema_version": 1,
        "data_origin": "metadata_only",
        "dataset": {
            "id": "synthetic-m3ot-reference",
            "release": "synthetic-v1",
            "owner_url": "https://example.org/owner",
            "licence_url": None,
            "rights_status": "needs_review",
            "archive_sha256": None,
        },
        "sequences": [
            {
                "id": "seq-a", "flight_group": "flight-a", "scene_group": "scene-a",
                "device_id": "drone-1", "split": "train",
                "rgb": {
                    "band": "rgb", "native_grid_wh": [100, 80],
                    "processed_grid_wh": [100, 80], "grid_origin": "original_native",
                },
                "thermal": {
                    "band": "lwir", "native_grid_wh": [60, 40],
                    "processed_grid_wh": [60, 40], "grid_origin": "original_native",
                },
                "pairing_origin": "manual", "exposure_clock": "unknown",
                "frames": [
                    {
                        "pair_id": "pair-0", "frame_index": 0, "rgb_id": "rgb-0",
                        "thermal_id": "thermal-0",
                        "rgb_sha256": digest(1), "thermal_sha256": digest(2),
                        "annotation_status": "complete",
                        "objects": [
                            {"modality": "rgb", "track_id": "car-1", "label": "vehicle",
                             "bbox_xywh": [10, 10, 20, 20]},
                            {"modality": "thermal", "track_id": "car-1",
                             "label": "vehicle", "bbox_xywh": [1, 1, 10, 10]},
                        ],
                    },
                    {
                        "pair_id": "pair-1", "frame_index": 2, "rgb_id": "rgb-1",
                        "thermal_id": "thermal-1",
                        "rgb_sha256": digest(3), "thermal_sha256": digest(4),
                        "annotation_status": "complete",
                        "objects": [
                            {"modality": "rgb", "track_id": "car-1", "label": "vehicle",
                             "bbox_xywh": [11, 10, 20, 20]},
                        ],
                    },
                ],
            },
        ],
    }


def test_synthetic_metadata_success_does_not_promote_scientific_evidence():
    report = admission.analyze(manifest())
    assert report["structural_validation"] == "PASS"
    assert report["empirical_admission"] is False
    assert not report["exposure_clock_verified"]
    assert not report["source_image_accessed"]
    assert report["counts"]["paired_frames"] == 2
    assert report["counts"]["objects"] == 3
    assert report["counts"]["track_gaps_to_review"] == 1
    assert report["thermal_bands_declared"] == ["lwir"]


def test_manifest_and_cli_are_deterministic_and_reports_exclusive(tmp_path, capsys):
    source = tmp_path / "inventory.json"
    source.write_text(json.dumps(manifest()), encoding="utf-8")
    report = admission.run(source)
    assert report == admission.run(source)
    output = tmp_path / "audit.json"
    assert cli.main(["admission", "--input", str(source), "--output", str(output)]) == 0
    assert json.loads(capsys.readouterr().out) == report
    assert json.loads(output.read_text(encoding="utf-8")) == report
    with pytest.raises(SystemExit) as exc:
        cli.main(["admission", "--input", str(source), "--output", str(output)])
    assert exc.value.code == 1
    assert output.read_text(encoding="utf-8")


@pytest.mark.parametrize(("path", "value", "message"), [
    (("schema_version",), True, "schema_version"),
    (("data_origin",), "measured", "metadata_only"),
    (("dataset", "archive_sha256"), "123", "SHA-256"),
    (("dataset", "owner_url"), "file:///tmp/secret", "HTTPS"),
    (("sequences", 0, "thermal", "band"), "rgb", "spectral band"),
    (("sequences", 0, "rgb", "grid_origin"), "original_native", "original_native"),
    (("sequences", 0, "frames", 0, "frame_index"), True, "frame_index"),
    (("sequences", 0, "frames", 1, "pair_id"), "pair-0", "duplicate"),
    (("sequences", 0, "frames", 1, "thermal_sha256"), f"{2:064x}", "Duplicate image"),
    (("sequences", 0, "frames", 0, "objects", 0, "bbox_xywh"), [95, 10, 10, 10],
     "bbox outside"),
    (("sequences", 0, "frames", 0, "objects", 0, "track_id"), "",
     "expected nonempty"),
])
def test_invalid_inventory_rejected(path, value, message):
    bad = copy.deepcopy(manifest())
    current = bad
    for component in path[:-1]:
        current = current[component]
    current[path[-1]] = value
    if path == ("sequences", 0, "rgb", "grid_origin"):
        bad["sequences"][0]["rgb"]["processed_grid_wh"] = [90, 70]
    with pytest.raises(ValueError, match=message):
        admission.analyze(bad)


def test_duplicate_track_id_same_modality_rejected_but_cross_modality_ids_allowed():
    case = manifest()
    existing = case["sequences"][0]["frames"][0]["objects"][0]
    case["sequences"][0]["frames"][0]["objects"].append(copy.deepcopy(existing))
    with pytest.raises(ValueError, match="duplicate track ID"):
        admission.analyze(case)


def test_cross_split_flight_and_scene_leakage_rejected():
    for key in ("flight_group", "scene_group"):
        bad = copy.deepcopy(manifest())
        seq = copy.deepcopy(bad["sequences"][0])
        seq["id"] = "seq-b"
        seq["split"] = "test"
        seq[key] = bad["sequences"][0][key]
        other = "scene_group" if key == "flight_group" else "flight_group"
        seq[other] = f"new-{other}"
        for i, frame in enumerate(seq["frames"]):
            frame["rgb_sha256"] = f"{i + 10:064x}"
            frame["thermal_sha256"] = f"{i + 20:064x}"
        bad["sequences"].append(seq)
        with pytest.raises(ValueError, match="Split leakage"):
            admission.analyze(bad)


def test_label_status_unknown_is_a_warning_not_evidence():
    case = manifest()
    case["sequences"][0]["frames"][0]["objects"] = []
    case["sequences"][0]["frames"][0]["annotation_status"] = "unknown"
    report = admission.analyze(case)
    assert report["counts"]["incomplete_or_unknown_labels"] == 1
    assert report["empirical_admission"] is False


def test_metadata_file_limits_duplicate_json_keys_and_input_untouched(tmp_path):
    source = tmp_path / "manifest.json"
    original = b'{"schema_version":1,"schema_version":1}'
    source.write_bytes(original)
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        admission.run(source)
    assert source.read_bytes() == original
    source.write_bytes(b" " * (admission.MAX_MANIFEST_BYTES + 1))
    with pytest.raises(ValueError, match="8 MiB"):
        admission.run(source)


def test_nir_never_relabelled_as_lwir():
    case = manifest()
    case["sequences"][0]["thermal"]["band"] = "nir"
    report = admission.analyze(case)
    assert report["thermal_bands_declared"] == ["nir"]
    assert report["empirical_admission"] is False
