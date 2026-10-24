"""Regression guard: no unsolicited or untrusted code on permanent CI runners."""

import re
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
PINNED_ACTION = re.compile(r"^[^\s@]+@[0-9a-f]{40}$")


@pytest.mark.parametrize("filename", ["offline-tests.yml", "docs-check.yml"])
def test_self_hosted_workflows_require_manual_main_dispatch(filename):
    # BaseLoader preserves GitHub's literal "on" key despite YAML 1.1 boolean aliases.
    document = yaml.load((WORKFLOWS / filename).read_text(encoding="utf-8"),
                         Loader=yaml.BaseLoader)
    assert set(document["on"]) == {"workflow_dispatch"}
    assert document["permissions"] == {"contents": "read"}
    for job in document["jobs"].values():
        assert job["if"] == "github.ref == 'refs/heads/main'"
        assert "self-hosted" in job["runs-on"]
        assert "ubuntu-latest" not in job["runs-on"]
        for step in job["steps"]:
            if "uses" in step:
                assert PINNED_ACTION.fullmatch(step["uses"])
                if step["uses"].startswith("actions/checkout@"):
                    assert step["with"]["persist-credentials"] == "false"
