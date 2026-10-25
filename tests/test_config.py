import tomllib
from pathlib import Path

import pytest

from arc_rgbt.common import load_yaml


def test_yaml_root_rejected(tmp_path):
    p = tmp_path / "invalid.yaml"
    p.write_text("- no mapping\n")
    with pytest.raises(ValueError):
        load_yaml(p)

def test_pytest_src_layout_is_configured_without_editable_install():
    config = Path(__file__).resolve().parents[1] / "pyproject.toml"
    settings = tomllib.loads(config.read_text(encoding="utf-8"))
    assert "src" in settings["tool"]["pytest"]["ini_options"]["pythonpath"]
