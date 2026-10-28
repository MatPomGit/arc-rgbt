"""Guard the full research portfolio contract used by Research Autopilot.

These tests validate structure and conservative activation metadata.
They do not validate scientific novelty, data licensing or empirical results.
"""

import json
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPER_IDS = tuple(f"P{i:02d}" for i in range(1, 9))
CORE_IDS = PAPER_IDS[:6]
OPTIONAL_IDS = PAPER_IDS[6:]


def _state():
    return yaml.safe_load((ROOT / "PROJECT_STATE.yaml").read_text(encoding="utf-8"))


def test_portfolio_state_is_json_compatible_and_references_exist():
    state = _state()
    assert isinstance(state["updated"], str)
    date.fromisoformat(state["updated"])
    json.dumps(state, allow_nan=False)
    assert state["repository"]["canonical_branch"] == "main"
    for key in (
        "software_version_source",
        "shared_code_root",
        "experiment_root",
        "research_programme",
        "implementation_roadmap",
        "documentation",
        "plan",
    ):
        assert (ROOT / state["repository"][key]).exists()
    assert state["portfolio_control"]["source_of_truth"] == "PROJECT_STATE.yaml"
    assert state["publication_portfolio"]["status"] == "concepts_not_submitted"


def test_eight_publication_entries_are_unique_and_have_reviewable_protocols():
    state = _state()
    portfolio = state["publication_portfolio"]
    lines = portfolio["lines"]
    ids = [entry["id"] for entry in lines]
    assert ids == list(PAPER_IDS)
    assert len(ids) == len(set(ids))
    assert tuple(portfolio["core_ids"]) == CORE_IDS
    assert tuple(portfolio["optional_ids"]) == OPTIONAL_IDS
    assert portfolio["planned_core_count"] == len(CORE_IDS)
    assert portfolio["optional_hold_count"] == len(OPTIONAL_IDS)
    assert not set(CORE_IDS).intersection(OPTIONAL_IDS)

    for entry in lines:
        paper_id = entry["id"]
        assert entry["title"].strip()
        assert entry["gate"]
        assert entry["evidence"]
        expected = (
            "core_planned" if paper_id in CORE_IDS else "optional_hold_evidence"
        )
        assert entry["activation"] == expected
        for relpath in ("README.md", "hypotheses/README.md", "protocol/README.md"):
            assert (ROOT / "publications" / paper_id / relpath).is_file()
        assert paper_id in state["evidence_state"]

    # Physical measurements and independently validated data are not available.
    assert state["evidence_state"]["independent_sensor_dataset"] == "not_yet_verified"
    assert state["evidence_state"]["embedded_mcu_power_or_latency"] == "not_measured"
    assert state["evidence_state"]["manuscripts_submitted"] == "not_claimed"


def test_optional_papers_stay_blocked_until_all_evidence_gates_pass():
    state = _state()
    portfolio = state["publication_portfolio"]
    rules = portfolio["optional_activation_rules"]
    assert set(rules) == set(OPTIONAL_IDS)

    for paper_id in OPTIONAL_IDS:
        rule = rules[paper_id]
        assert rule["status"] == "hold"
        assert len(set(rule["prerequisites"])) >= 4
        assert "independent_novelty_review" in rule["prerequisites"]
        assert "E02" in " ".join(rule["excluded_evidence"])

    assert "P03_real_hardware_baseline" in rules["P07"]["prerequisites"]
    assert "adaptive_policy_metered_energy" in rules["P07"]["prerequisites"]
    assert "independent_registration_uncertainty" in rules["P08"]["prerequisites"]
    assert "independent_risk_coverage" in rules["P08"]["prerequisites"]

    actions = state["next_actions"]
    assert len({action["id"] for action in actions}) == len(actions)
    assert [action["order"] for action in actions] == list(range(1, len(actions) + 1))
    for paper_id in OPTIONAL_IDS:
        matches = [
            action for action in actions if action["id"].endswith(f"{paper_id}_OPTIONAL")
        ]
        assert len(matches) == 1
        assert matches[0]["status"] == "optional_hold_evidence"
        assert matches[0]["procedure"] == f"publications/{paper_id}/protocol/README.md"

    blockers = {blocker["id"]: blocker for blocker in state["current_blockers"]}
    assert blockers["B05_OPTIONAL_GATES"]["status"] == "hold"
