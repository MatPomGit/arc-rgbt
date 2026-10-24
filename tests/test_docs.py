"""Regression tests for the offline MkDocs documentation verifier."""

from pathlib import Path
from shutil import copy2, copytree

import pytest

from tools.check_docs import ROOT, check


def _fixture(tmp_path: Path) -> Path:
    copytree(ROOT / "docs", tmp_path / "docs")
    copy2(ROOT / "mkdocs.yml", tmp_path / "mkdocs.yml")
    copy2(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    return tmp_path


def test_all_documentation_pages_and_links_are_resolved():
    pages, links = check()
    assert pages >= 16
    assert links >= 35


def test_missing_nav_page_detected(tmp_path):
    root = _fixture(tmp_path)
    (root / "docs" / "newpage.md").write_text("# Orphan\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Navigation mismatch"):
        check(root)


def test_broken_local_link_detected(tmp_path):
    root = _fixture(tmp_path)
    with (root / "docs" / "index.md").open("a", encoding="utf-8") as file:
        file.write("\n[Broken](missing.md)\n")
    with pytest.raises(ValueError, match="Broken documentation link"):
        check(root)


def test_path_traversal_link_detected(tmp_path):
    root = _fixture(tmp_path)
    with (root / "docs" / "index.md").open("a", encoding="utf-8") as file:
        file.write("\n[Outside](../../pyproject.toml)\n")
    with pytest.raises(ValueError, match="Broken documentation link"):
        check(root)


def test_missing_cli_reference_detected(tmp_path):
    root = _fixture(tmp_path)
    project = root / "pyproject.toml"
    project.write_text(
        project.read_text(encoding="utf-8").replace(
            '[project.scripts]\n',
            '[project.scripts]\nnew-example-tool = "arc_rgbt.e00:main"\n',
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Undocumented CLI"):
        check(root)
