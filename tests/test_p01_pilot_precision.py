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
_t_one_sided_upper = module._t_one_sided_upper
_trial_differences = module._trial_differences
run_pilot = module.run_pilot
_wilson_interval = module._wilson_interval


def test_constant_acquisition_contrast_has_zero_width_interval():
    assert _interval([-0.2] * 10, 200, random.Random(5)) == (-0.2, -0.2)
    assert _t_interval([-0.2] * 10) == (-0.2, -0.2)
    assert _t_one_sided_upper([-0.2] * 10) is None


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
        directional = scenario["directional_test"]
        assert directional["null"] == "Delta >= 0"
        assert directional["alpha"] == 0.05
        assert 0 <= directional["rejection_fraction"] <= 1
        assert 0 <= directional["undefined_fraction"] <= 1
        assert directional["rate_kind"] == (
            "null_boundary_type_i_error"
            if scenario["true_group_mean_delta"] == 0
            else "synthetic_directional_detection"
        )
        lower, upper = directional["rejection_mc_95_interval"]
        assert 0 <= lower <= directional["rejection_fraction"] <= upper <= 1


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


def test_wilson_monte_carlo_intervals_are_bounded():
    lower, upper = _wilson_interval(0, 250)
    assert lower == 0
    assert 0 < upper < 0.03
    lower, upper = _wilson_interval(250, 250)
    assert 0.97 < lower < 1
    assert upper == 1
    lower, upper = _wilson_interval(125, 250)
    assert lower < 0.5 < upper


def test_stress_scenarios_reproducible_and_well_formed():
    result = run_pilot(trials=5, bootstrap=100, seed=17, stress=True)
    assert result == run_pilot(trials=5, bootstrap=100, seed=17, stress=True)
    assert result["stress_scenarios_enabled"] is True
    assert len(result["scenarios"]) == 36
    assert {scenario["design"] for scenario in result["scenarios"]} == {
        "balanced", "unequal_counts_shared_shock", "skewed_sparse",
    }
    for scenario in result["scenarios"]:
        for method in scenario["methods"].values():
            lo, hi = method["coverage_mc_95_interval"]
            assert 0 <= lo <= method["coverage_95_fraction"] <= hi <= 1
            lo, hi = method["negative_ci_mc_95_interval"]
            assert 0 <= lo <= method["negative_ci_fraction"] <= hi <= 1


def test_stress_preserves_population_difference_with_many_independent_groups():
    result = _trial_differences(
        2000, 20, -0.15, random.Random(20261102),
        unequal_counts=True, correlated_hits=True,
    )
    assert len(result) == 2000
    assert all(-1 <= difference <= 1 for difference in result)
    assert abs(sum(result) / len(result) + 0.15) < 0.03


@pytest.mark.parametrize("kwargs", [{"stress": 1}, {"stress": None}])
def test_invalid_stress_options_rejected(kwargs):
    with pytest.raises(ValueError, match="Invalid pilot"):
        run_pilot(trials=1, bootstrap=100, **kwargs)


def test_one_sided_t_decision_is_distinct_from_two_sided_95_ci():
    # t statistic is between the one-sided and two-sided 5% cutoffs.
    differences = [-0.12] * 5 + [0.02] * 5
    assert _t_one_sided_upper(differences) < 0
    assert _t_interval(differences)[1] > 0
    assert _t_one_sided_upper([-1.0] * 5 + [1.0] * 5) > 0


def test_skewed_sparse_generator_preserves_population_mean_in_large_pilot():
    differences = _trial_differences(
        4000, 20, -0.15, random.Random(20261104), skewed_sparse=True,
    )
    assert all(-1 <= delta <= 1 for delta in differences)
    assert abs(sum(differences) / len(differences) + 0.15) < 0.03


def test_directional_false_positive_rate_is_a_simulation_not_inference():
    result = run_pilot(trials=100, bootstrap=100, seed=20261104)
    for scenario in result["scenarios"]:
        if scenario["true_group_mean_delta"] == 0:
            test = scenario["directional_test"]
            assert test["rate_kind"] == "null_boundary_type_i_error"
            assert test["rejection_fraction"] <= 0.2
        else:
            assert scenario["directional_test"]["rate_kind"] == (
                "synthetic_directional_detection"
            )
