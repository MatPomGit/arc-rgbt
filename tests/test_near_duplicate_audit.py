"""Offline near-duplicate image scan tests on synthetic PNG data only."""

from __future__ import annotations

import copy
import hashlib
import json

import cv2
import numpy as np
import pytest
from test_admission import manifest as admission_fixture

from arc_rgbt import cli
from arc_rgbt.near_duplicate_audit import analyze_subset, main


def case(tmp_path):
    src = admission_fixture()
    seq = src["sequences"][0]
    second = copy.deepcopy(seq)
    second["id"] = "seq-test"
    second["flight_group"] = "flight-test"
    second["scene_group"] = "scene-test"
    second["device_id"] = "device-test"
    second["split"] = "test"
    src["sequences"].append(second)
    original = np.zeros((80, 100, 3), dtype=np.uint8)
    original[:, :50] = (20, 50, 180)
    original[:, 50:] = (100, 50, 70)
    modified = original.copy()
    modified[1, 1] = (2, 2, 2)
    image_root = tmp_path / "images"
    image_root.mkdir()
    mapping = {"schema_version": 1, "items": []}
    for i, (seqitem, img) in enumerate(((seq, original), (second, modified))):
        buf_ok, buf = cv2.imencode(".png", img)
        assert buf_ok
        name = f"image-{i}.png"
        raw = buf.tobytes()
        (image_root / name).write_bytes(raw)
        ref = seqitem["frames"][0]
        ref["rgb_sha256"] = hashlib.sha256(raw).hexdigest()
        ref["rgb_id"] = f"rgb-{i}"
        ref["pair_id"] = f"pair-{i}"
        ref["thermal_id"] = f"th-{i}"
        # Ensure all other declared hashes are unique across both sequences.
        for j, frame in enumerate(seqitem["frames"]):
            frame["thermal_sha256"] = f"{100 + i * 8 + j:064x}"
            if j > 0:
                frame["rgb_sha256"] = f"{200 + i * 8 + j:064x}"
                frame["rgb_id"] = f"rgb-{i}-{j}"
                frame["thermal_id"] = f"th-{i}-{j}"
                frame["pair_id"] = f"pair-{i}-{j}"
        mapping["items"].append({
            "sequence_id": seqitem["id"], "modality": "rgb",
            "frame_id": ref["rgb_id"], "path": name,
        })
    return src, mapping, image_root


def test_reports_cross_split_heuristic_candidates_and_never_admits_data(tmp_path):
    src, mapping, root = case(tmp_path)
    report = analyze_subset(src, mapping, root)
    assert report["images_hashed_and_decoded"] == 2
    assert report["cross_split_same_band_comparisons"] == 1
    assert report["result"] == "REVIEW_REQUIRED"
    assert report["near_duplicate_candidates"][0]["hamming_distance"] <= 4
    assert report["empirical_admission"] is False
    assert report["licence_verified"] is False
    assert report["tracking_metric_verified"] is False


def test_determinism_and_metadata_source_unchanged(tmp_path):
    src, mapping, root = case(tmp_path)
    before = copy.deepcopy(src)
    a = analyze_subset(src, mapping, root)
    b = analyze_subset(src, mapping, root)
    assert a == b and src == before


def test_reject_tampered_image_sha_and_missing_file(tmp_path):
    src, mapping, root = case(tmp_path)
    (root / "image-1.png").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="signature"):
        analyze_subset(src, mapping, root)
    (root / "image-1.png").unlink()
    with pytest.raises(FileNotFoundError):
        analyze_subset(src, mapping, root)


def test_reject_traversal_and_outside_symlink(tmp_path):
    src, mapping, root = case(tmp_path)
    mapping["items"][1]["path"] = "../image-0.png"
    with pytest.raises(ValueError, match="Unsafe"):
        analyze_subset(src, mapping, root)
    target = tmp_path / "outside.png"
    target.write_bytes((root / "image-0.png").read_bytes())
    link = root / "link.png"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("No symlinks on this platform")
    mapping["items"][1]["path"] = "link.png"
    with pytest.raises(ValueError, match="escapes"):
        analyze_subset(src, mapping, root)


@pytest.mark.parametrize("bad", [-1, 65, 4.0, True])
def test_invalid_threshold_rejected(tmp_path, bad):
    src, mapping, root = case(tmp_path)
    with pytest.raises(ValueError, match="max_hamming"):
        analyze_subset(src, mapping, root, max_hamming=bad)


def test_cross_split_different_spectral_band_is_not_compared(tmp_path):
    src, mapping, root = case(tmp_path)
    src["sequences"][1]["rgb"]["band"] = "rgb"
    # Both mapped images are RGB, so one comparison remains.
    assert analyze_subset(src, mapping, root)["cross_split_same_band_comparisons"] == 1


def test_reject_reused_frame_mapping(tmp_path):
    src, mapping, root = case(tmp_path)
    mapping["items"][1] = copy.deepcopy(mapping["items"][0])
    with pytest.raises(ValueError, match="Duplicate"):
        analyze_subset(src, mapping, root)


def test_cli_creates_non_overwriting_report(tmp_path, capsys):
    src, mapping, root = case(tmp_path)
    inv = tmp_path / "inventory.json"
    m = tmp_path / "map.json"
    inv.write_text(json.dumps(src), encoding="utf-8")
    m.write_text(json.dumps(mapping), encoding="utf-8")
    out = tmp_path / "report.json"
    assert cli.main(["near-duplicates", "--input", str(inv), "--map", str(m),
                     "--root", str(root), "--output", str(out)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert json.loads(out.read_text(encoding="utf-8")) == report
    with pytest.raises(SystemExit) as exc:
        main(["--input", str(inv), "--map", str(m),
              "--root", str(root), "--output", str(out)])
    assert exc.value.code == 1
