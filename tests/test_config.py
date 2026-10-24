import pytest

from arc_rgbt.common import load_yaml


def test_yaml_root_rejected(tmp_path):
    p = tmp_path / "invalid.yaml"
    p.write_text("- no mapping\n")
    with pytest.raises(ValueError):
        load_yaml(p)
