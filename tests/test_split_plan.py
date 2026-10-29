"""Synthetic deterministic split-planning regression tests."""

from __future__ import annotations

from copy import deepcopy

import pytest
from test_admission import manifest

from arc_rgbt.split_plan import propose_splits


def source(group: int, *, flight=None, scene=None, device=None):
    template = manifest()["sequences"][0]
    seq = deepcopy(template)
    seq["id"] = f"seq-{group}"
    seq["flight_group"] = flight or f"flight-{group}"
    seq["scene_group"] = scene or f"scene-{group}"
    seq["device_id"] = device or f"device-{group}"
    for i, frame in enumerate(seq["frames"]):
        frame["rgb_sha256"] = f"{4 * group + 1 + 2 * i:064x}"
        frame["thermal_sha256"] = f"{4 * group + 2 + 2 * i:064x}"
    return seq


def dataset(n=6):
    d = manifest()
    d["sequences"] = [source(i) for i in range(n)]
    return d


def test_seeded_proposal_deterministic_does_not_mutate_manifest():
    d = dataset()
    before = deepcopy(d)
    result = propose_splits(d, seed=4)
    assert d == before
    assert result == propose_splits(d, seed=4)
    assert result["group_quotas"] == {"train": 4, "validation": 1, "test": 1}
    assert result["component_count"] == 6
    assert result["empirical_admission"] is False
    assert set(result["assignments"].values()) == {"train", "validation", "test"}


def test_connected_flight_and_scene_components_not_split():
    d = dataset(7)
    d["sequences"][1]["flight_group"] = d["sequences"][0]["flight_group"]
    d["sequences"][2]["scene_group"] = d["sequences"][1]["scene_group"]
    planned = propose_splits(d, seed=9)
    assignments = planned["assignments"]
    assert planned["component_count"] == 5
    assert assignments["seq-0"] == assignments["seq-1"] == assignments["seq-2"]
    assert sum(planned["split_frame_counts"].values()) == 14


def test_device_strictness_can_reduce_independent_components():
    d = dataset(5)
    d["sequences"][1]["device_id"] = d["sequences"][0]["device_id"]
    a = propose_splits(d)
    b = propose_splits(d, device_disjoint=True)
    assert a["component_count"] == 5
    assert b["component_count"] == 4
    assert b["assignments"]["seq-0"] == b["assignments"]["seq-1"]


def test_insufficient_independent_groups_fails_closed():
    d = dataset(3)
    d["sequences"][1]["flight_group"] = d["sequences"][0]["flight_group"]
    with pytest.raises(ValueError, match="three independent"):
        propose_splits(d)


@pytest.mark.parametrize("kwargs", [
    {"seed": True}, {"seed": -1}, {"seed": 2**32},
    {"device_disjoint": 1}, {"proportions": (1, 0, 0)},
    {"proportions": (0.5, 0.2, 0.2)},
    {"proportions": [0.5, True, 0.5]},
])
def test_invalid_plan_inputs_rejected(kwargs):
    with pytest.raises(ValueError):
        propose_splits(dataset(), **kwargs)


def test_existing_split_leakage_rejected_before_planning():
    d = dataset()
    d["sequences"][1]["flight_group"] = d["sequences"][0]["flight_group"]
    d["sequences"][1]["split"] = "test"
    with pytest.raises(ValueError, match="Split leakage"):
        propose_splits(d)


def test_duplicate_image_hash_rejected_before_planning():
    d = dataset()
    d["sequences"][1]["frames"][0]["rgb_sha256"] = (
        d["sequences"][0]["frames"][0]["rgb_sha256"]
    )
    with pytest.raises(ValueError, match="Duplicate image"):
        propose_splits(d)


def test_split_cli_creates_report_without_changing_metadata(tmp_path, capsys):
    import json

    from arc_rgbt import cli

    original = dataset(5)
    src = tmp_path / "input.json"
    src.write_text(json.dumps(original), encoding="utf-8")
    dst = tmp_path / "proposal.json"
    assert cli.main(["split", "--input", str(src), "--output", str(dst)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert json.loads(dst.read_text(encoding="utf-8")) == output
    assert json.loads(src.read_text(encoding="utf-8")) == original
    assert output["empirical_admission"] is False
    with pytest.raises(SystemExit) as raised:
        cli.main(["split", "--input", str(src), "--output", str(dst)])
    assert raised.value.code == 1
