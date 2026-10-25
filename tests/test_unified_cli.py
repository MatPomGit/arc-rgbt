import json

import numpy as np
import pytest

from arc_rgbt import cli


def test_discoverable_help(capsys):
    assert cli.main([]) == 0
    text = capsys.readouterr().out
    for command in ("doctor", "demo", "sensor", "degrade", "fuse", "bench", "edge",
                    "e00", "e01", "e02", "sync", "register", "thermal"):
        assert command in text


def test_diagnostic_json(capsys):
    assert cli.main(["doctor", "--json"]) == 0
    diagnostic = json.loads(capsys.readouterr().out)
    assert diagnostic["ok"] is True
    assert diagnostic["python_supported"] is True
    assert all(value["ok"] for value in diagnostic["dependencies"].values())


def test_invalid_subcommand_does_not_run_tools(capsys):
    with pytest.raises(SystemExit) as raised:
        cli.main(["unknown-command"])
    assert raised.value.code == 2
    assert "unknown command" in capsys.readouterr().err


def test_child_help_forwards_to_original_parser(capsys):
    with pytest.raises(SystemExit) as raised:
        cli.main(["fuse", "--help"])
    assert raised.value.code == 0
    assert "--thermal" in capsys.readouterr().out


def test_read_error_is_human_readable(capsys, tmp_path):
    with pytest.raises(SystemExit) as raised:
        cli.main(["degrade", "--input", str(tmp_path / "missing.npy"),
                  "--config", str(tmp_path / "missing.yaml")])
    assert raised.value.code == 1
    stderr = capsys.readouterr().err
    assert "arc-rgbt degrade" in stderr and "FileNotFoundError" in stderr


def test_demo_writes_interpretable_artifacts_and_guards_output(tmp_path):
    target = tmp_path / "przykład_RGB–IR"
    assert cli.main(["demo", "--output", str(target), "--seed", "41"]) == 0
    summary = json.loads((target / "summary.json").read_text())
    assert summary["synthetic_demo"] is True
    assert summary["seed"] == 41
    assert summary["native_shape_px"] == [128, 96]
    assert len(summary["limitations"]) >= 3
    for name in summary["files"]:
        assert (target / name).is_file(), name
    assert np.load(target / "fused.npy", allow_pickle=False).shape == (96, 128)
    page = (target / "index.html").read_text()
    assert "Synthetic" in page and "bench/bench.html" in page
    with pytest.raises(SystemExit) as raised:
        cli.main(["demo", "--output", str(target), "--seed", "41"])
    assert raised.value.code == 2
    assert (target / "summary.json").is_file()


@pytest.mark.parametrize("seed", ["-1", "4294967296", "not-a-number"])
def test_demo_rejects_bad_seed_before_creating_output(seed, tmp_path):
    path = tmp_path / "bad-demo"
    with pytest.raises(SystemExit) as raised:
        cli.main(["demo", "--output", str(path), "--seed", seed])
    assert raised.value.code == 2
    assert not path.exists()
