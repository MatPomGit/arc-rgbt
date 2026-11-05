"""Synthetic pre-freeze precision audit for P01 paired acquisition recall.

No image, label, sensor or independent source evidence is used here.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics


GROUP_COUNTS = (10, 20, 40)
TARGET_COUNTS = (4, 20)
EFFECTS = (0.0, -0.15)
# Two-sided 0.975 quantiles of Student t for 9, 19 and 39 degrees of freedom.
T_CRITICAL = {10: 2.262157, 20: 2.093024, 40: 2.022691}
# One-sided alpha=0.05 critical values for the same acquisition counts.
T_CRITICAL_ONE_SIDED = {10: 1.833113, 20: 1.729133, 40: 1.684875}


def _percentile(sorted_values: list[float], probability: float) -> float:
    """Linearly interpolate the same percentile definition as P01 metrics."""
    index = (len(sorted_values) - 1) * probability
    lower, upper = math.floor(index), math.ceil(index)
    return (sorted_values[lower] +
            (sorted_values[upper] - sorted_values[lower]) * (index - lower))


def _interval(
    differences: list[float], draws: int, rng: random.Random,
) -> tuple[float, float]:
    """Resample whole paired acquisition differences with equal weights."""
    count = len(differences)
    estimates = sorted(
        sum(rng.choices(differences, k=count)) / count
        for _ in range(draws)
    )
    return _percentile(estimates, 0.025), _percentile(estimates, 0.975)


def _t_interval(differences: list[float]) -> tuple[float, float]:
    """Comparison CI on independent acquisition means, not per-frame data."""
    count = len(differences)
    if count not in T_CRITICAL:
        raise ValueError(f"Unsupported paired acquisition count: {count}")
    mean = statistics.mean(differences)
    half_width = T_CRITICAL[count] * statistics.stdev(differences) / math.sqrt(count)
    return mean - half_width, mean + half_width


def _t_one_sided_upper(differences: list[float]) -> float | None:
    """Directional 95% upper t bound; undefined for zero sample variance."""
    count = len(differences)
    if count not in T_CRITICAL_ONE_SIDED:
        raise ValueError(f"Unsupported paired acquisition count: {count}")
    deviation = statistics.stdev(differences)
    if deviation == 0:
        return None
    return (statistics.mean(differences) +
            T_CRITICAL_ONE_SIDED[count] * deviation / math.sqrt(count))


def _wilson_interval(successes: int, trials: int) -> tuple[float, float]:
    """95% Monte Carlo binomial uncertainty for an estimated frequency."""
    p = successes / trials
    z = 1.959963984540054
    denom = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denom
    half = z * math.sqrt(p * (1 - p) / trials +
                         z * z / (4 * trials * trials)) / denom
    lower = 0.0 if successes == 0 else max(0.0, centre - half)
    upper = 1.0 if successes == trials else min(1.0, centre + half)
    return lower, upper


def _group_bin_counts(
    group: int, targets_per_bin: int, *, unequal_counts: bool,
    skewed_sparse: bool,
) -> tuple[int, int]:
    """Return (reference, small) denominators independently of outcomes."""
    half = max(1, targets_per_bin // 2)
    if skewed_sparse:
        return (
            1 if group % 4 == 0 else max(2, targets_per_bin + half),
            1 if group % 5 == 0 else max(2, targets_per_bin - half),
        )
    if unequal_counts:
        return (
            max(2, targets_per_bin + (half if group % 2 else -half)),
            max(2, targets_per_bin + (half if group % 3 else -half)),
        )
    return targets_per_bin, targets_per_bin


def _trial_differences(
    groups: int, targets_per_bin: int, effect: float, rng: random.Random,
    *, unequal_counts: bool = False, correlated_hits: bool = False,
    skewed_sparse: bool = False,
) -> list[float]:
    """Simulate paired acquisition recalls with optional additional stress.

    A random acquisition probability generates heterogeneous groups.
    The sparse stress uses highly asymmetric zero-mean contrast shocks and
    outcome-independent, highly unequal within-group denominators.
    Probabilities remain in [0, 1] for the declared effect grid; the
    population equal-acquisition contrast remains the specified effect.
    """
    differences = []
    for group in range(groups):
        if skewed_sparse:
            reference_p = 0.40 + 0.35 * rng.random()
            # E[shock] = 0.2*(-0.18) + 0.8*(0.045) = 0.
            shock = -0.18 if rng.random() < 0.2 else 0.045
            small_p = reference_p + effect + shock
        else:
            reference_p = 0.35 + 0.40 * rng.random()
            small_p = reference_p + effect + 0.08 * (2 * rng.random() - 1)
            if correlated_hits:
                shock = 0.08 * (2 * rng.random() - 1)
                reference_p += shock
                small_p += shock
        reference_count, small_count = _group_bin_counts(
            group, targets_per_bin, unequal_counts=unequal_counts,
            skewed_sparse=skewed_sparse,
        )
        reference_hits = sum(rng.random() < reference_p for _ in range(reference_count))
        small_hits = sum(rng.random() < small_p for _ in range(small_count))
        differences.append(small_hits / small_count - reference_hits / reference_count)
    return differences


def run_pilot(
    *, trials: int = 250, bootstrap: int = 2000, seed: int = 20261102,
    stress: bool = False, directional_only: bool = False,
) -> dict:
    """Estimate interval coverage and directional frequency, never empirical power."""
    if (type(trials) is not int or trials < 1 or type(bootstrap) is not int
            or bootstrap < 100 or type(seed) is not int or type(stress) is not bool
            or type(directional_only) is not bool):
        raise ValueError("Invalid pilot trials, bootstrap draws, seed or stress")
    rng = random.Random(seed)
    scenarios = []
    designs = [("balanced", False, False)]
    if stress:
        designs.extend([
            ("unequal_counts_shared_shock", True, True),
            ("skewed_sparse", False, False),
        ])
    for design, unequal_counts, correlated_hits in designs:
        for groups in GROUP_COUNTS:
            for targets in TARGET_COUNTS:
                for effect in EFFECTS:
                    denominators = [
                        _group_bin_counts(
                            g, targets, unequal_counts=unequal_counts,
                            skewed_sparse=design == "skewed_sparse",
                        )
                        for g in range(groups)
                    ]
                    actual_counts = {}
                    for name, index in (("reference", 0), ("small", 1)):
                        sample = [pair[index] for pair in denominators]
                        actual_counts[name] = {
                            "min": min(sample), "median": statistics.median(sample),
                            "max": max(sample),
                        }
                    counts = {
                        method: {
                            "covered": 0, "negative": 0, "degenerate": 0,
                            "width_sum": 0.0,
                        }
                        for method in (() if directional_only else
                                       ("percentile_bootstrap", "cluster_t"))
                    }
                    rejected, undefined = 0, 0
                    for _ in range(trials):
                        diffs = _trial_differences(
                            groups, targets, effect, rng,
                            unequal_counts=unequal_counts,
                            correlated_hits=correlated_hits,
                            skewed_sparse=design == "skewed_sparse",
                        )
                        # Candidate directional test differs from two-sided CI.
                        upper = _t_one_sided_upper(diffs)
                        undefined += upper is None
                        rejected += upper is not None and upper < 0
                        intervals = {}
                        if not directional_only:
                            intervals = {
                                "percentile_bootstrap": _interval(
                                    diffs, bootstrap, rng,
                                ),
                                "cluster_t": _t_interval(diffs),
                            }
                        for method, (lower, upper) in intervals.items():
                            item = counts[method]
                            item["covered"] += lower <= effect <= upper
                            item["negative"] += upper < 0
                            item["degenerate"] += lower == upper
                            item["width_sum"] += upper - lower
                    methods = {}
                    for method, item in counts.items():
                        coverage = item["covered"] / trials
                        negative_fraction = item["negative"] / trials
                        methods[method] = {
                            "coverage_95_fraction": coverage,
                            "coverage_mcse": math.sqrt(
                                coverage * (1 - coverage) / trials
                            ),
                            "coverage_mc_95_interval": _wilson_interval(
                                item["covered"], trials
                            ),
                            "mean_ci_width": item["width_sum"] / trials,
                            "negative_ci_fraction": negative_fraction,
                            "negative_ci_mcse": math.sqrt(
                                negative_fraction * (1 - negative_fraction) / trials
                            ),
                            "negative_ci_mc_95_interval": _wilson_interval(
                                item["negative"], trials
                            ),
                            "degenerate_ci_fraction": item["degenerate"] / trials,
                        }
                    rejection_rate = rejected / trials
                    scenarios.append({
                        "design": design,
                        "paired_groups": groups,
                        "nominal_targets_per_bin": targets,
                        "actual_targets_per_bin_per_group": actual_counts,
                        "true_group_mean_delta": effect,
                        "methods": methods,
                        "directional_test": {
                            "procedure": "one_sided_acquisition_student_t",
                            "alpha": 0.05,
                            "null": "Delta >= 0",
                            "decision": "one_sided_95_upper_bound_below_zero",
                            "rate_kind": ("null_boundary_type_i_error" if effect == 0
                                          else "synthetic_directional_detection"),
                            "rejection_fraction": rejection_rate,
                            "rejection_mcse": math.sqrt(
                                rejection_rate * (1 - rejection_rate) / trials
                            ),
                            "rejection_mc_95_interval": _wilson_interval(
                                rejected, trials
                            ),
                            "undefined_fraction": undefined / trials,
                        },
                    })
    return {
        "evidence": "synthetic_precision_audit_only",
        "empirical_admission": False,
        "preregistration_frozen": False,
        "trials_per_scenario": trials,
        "bootstrap_draws_per_trial": 0 if directional_only else bootstrap,
        "directional_only": directional_only,
        "seed": seed,
        "stress_scenarios_enabled": stress,
        "generating_model": {
            "reference_probability": "Uniform(0.35, 0.75) by acquisition",
            "small_probability": "reference + delta + Uniform(-0.08, 0.08)",
            "hits": "conditionally independent Bernoulli given group probabilities",
            "stress": (
                "unequal counts plus group shock; additionally asymmetric "
                "zero-mean contrast shocks and sparse group bin counts"
            ),
            "contrast": "equal-weight mean of paired acquisition recall differences",
            "ci": "whole-group percentile bootstrap versus group Student t, both 95%",
            "directional_test": "one-sided acquisition Student t, alpha=0.05",
        },
        "limitations": (
            "Assumed independent acquisition groups, known footprint bins, "
            "fixed sampling rules and independent Bernoulli hits conditional on "
            "group probabilities. One-sided null calibration is estimated only "
            "at the boundary Delta=0 under declared generating models; other "
            "nonnegative null effects are not simulated. The sparse design fixes "
            "bin-count patterns by group index. No score/FP-frame selection, "
            "imaging physics, missing annotations, source rights or actual LWIR."
        ),
        "scenarios": scenarios,
    }


def main() -> None:
    """Print a reproducible synthetic-only JSON audit to standard output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=250)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261102)
    parser.add_argument(
        "--directional-only", action="store_true",
        help="skip descriptive CI calculations for fast null-boundary calibration",
    )
    parser.add_argument(
        "--stress", action="store_true",
        help="also simulate unequal bin counts and an added shared shock",
    )
    args = parser.parse_args()
    print(json.dumps(run_pilot(
        trials=args.trials, bootstrap=args.bootstrap, seed=args.seed,
        stress=args.stress, directional_only=args.directional_only,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
