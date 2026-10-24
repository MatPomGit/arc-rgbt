"""Keep research portfolio handoff safe for JSON-oriented downstream consumers."""

import json
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_portfolio_state_is_json_compatible_and_references_exist():
    state = yaml.safe_load((ROOT / "PROJECT_STATE.yaml").read_text(encoding="utf-8"))
    assert isinstance(state["updated"], str)
    date.fromisoformat(state["updated"])
    json.dumps(state, allow_nan=False)
    assert state["repository"]["canonical_branch"] == "main"
    for key in ("software_version_source", "shared_code_root", "experiment_root",
                "research_programme", "implementation_roadmap", "documentation", "plan"):
        assert (ROOT / state["repository"][key]).exists()
    assert {entry["id"] for entry in state["publication_portfolio"]["lines"]} == {
        "P01", "P02", "P03"
    }
    actions = state["next_actions"]
    assert len({action["id"] for action in actions}) == len(actions)
    assert [action["order"] for action in actions] == list(range(1, len(actions) + 1))
