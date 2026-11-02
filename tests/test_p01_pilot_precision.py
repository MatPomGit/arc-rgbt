"""Deterministic synthetic checks for the P01 precision pilot."""

import importlib.util
import random
from pathlib import Path

import pytest

SCRIPT = (Path(__file__).resolve().parents[1] /
          "publications/P01/analyses/pilot_cluster_precision.py")
spec = importlib.util.spec_from_file_location("p01_precision_pilot", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
_interval = module._interval
_t_interval = module._t_interval
_trial_differences = module._trial_differences
run_pilot = module.run_pilot


def test_constant_acquisition_contrast_has_zero_width_interval():
    assert _interval([-0.2] * 10, 200, random.Random(5)) == (-0.2, -0.2)
    assert _t_interval([-0.2] * 10) == (-0.2, -0.2)


def test_pilot_is_seeded_and_scenarios_cover_null_and_alternative():
    result = run_pilot(trials=5, bootstrap=100, seed=7)
    assert result == run_pilot(trials=5, bootstrap=100, seed=7)
    assert result["empirical_admission"] is False
    assert result["preregistration_frozen"] is False
    assert len(result["scenarios"]) == 12
    for scenario in result["scenarios"]:
        assert set(scenario["methods"]) == {"percentile_bootstrap", "cluster_t"}
        for method in scenario["methods"].values():
            assert 0 <= method["coverage_95_fraction"] <= 1
            assert 0 <= method["negative_ci_fraction"] <= 1
            assert method["mean_ci_width"] >= 0
        assert scenario["true_group_mean_delta"] in (0, -0.15)


def test_group_differences_are_valid_recall_differences():
    differences = _trial_differences(10, 4, -0.15, random.Random(12))
    assert len(differences) == 10
    assert all(-1 <= difference <= 1 for difference in differences)


@pytest.mark.parametrize("kwargs", [
    {"trials": 0}, {"bootstrap": 99}, {"seed": True}, {"trials": 2.5},
])
def test_invalid_pilot_configuration_rejected(kwargs):
    with pytest.raises(ValueError, match="Invalid pilot"):
        run_pilot(**kwargs)
