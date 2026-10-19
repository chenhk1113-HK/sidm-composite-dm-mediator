"""Regression test for v40.48 background refit.

Per v40.48: parameter sweep over (sigma_0, a_slope, v_ref) with
peak=0 finds 14/75 combinations that satisfy all 3 constraints
(Cloud-9 sigma/m(28) < 1.0, Fornax sigma/m(15) < 0.8, SPARC
sigma/m(100) < 0.1).

Best: sigma_0=0.01, a_slope=1.50, v_ref=50.0 gives:
  - sigma/m(28) = 0.024 cm^2/g (Cloud-9)
  - sigma/m(15) = 0.061 cm^2/g (Fornax)
  - sigma/m(100) = 0.0035 cm^2/g (SPARC)

This test locks the v40.48 finding so any future change that
removes the passing combinations (e.g., changing the constraints
without re-running the sweep) FAILS the test.

Reference: scripts/v19_2_f_background_refit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_background_refit_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_background_refit.py"


def test_v40_48_results_present():
    """Lock file must exist and have the v40.48 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "total_combinations" in data
    assert "passing_combinations" in data
    assert "best_passing" in data
    assert "parameter_grids" in data


def test_v40_48_at_least_one_passing():
    """At least one parameter combination must satisfy all 3 constraints.

    Per v40.48: 14 combinations pass. If 0 combinations pass, the
    Yukawa power-law form is INSUFFICIENT and additional physics
    is needed.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    passing = data["passing_combinations"]
    assert passing >= 1, (
        f"Passing combinations = {passing}, expected >= 1. "
        f"If 0, the Yukawa power-law form is INSUFFICIENT for the "
        f"v19.2-F framework downgrade."
    )


def test_v40_48_best_passing_satisfies_constraints():
    """The best_passing triple must actually satisfy all 3 constraints.

    Per v40.48: best_passing has sigma/m(28) < 1.0, sigma/m(15) < 0.8,
    sigma/m(100) < 0.1. If any constraint is violated, the sweep
    logic is wrong.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    best = data["best_passing"]
    if best is None:
        return  # No passing combinations; skip
    assert best["sigma_m_cloud9"] < 1.0, (
        f"Cloud-9 sigma/m(28) = {best['sigma_m_cloud9']:.4f}, expected < 1.0. "
        f"If >= 1.0, the Cloud-9 constraint is violated."
    )
    assert best["sigma_m_fornax"] < 0.8, (
        f"Fornax sigma/m(15) = {best['sigma_m_fornax']:.4f}, expected < 0.8. "
        f"If >= 0.8, the Fornax dSph constraint is violated."
    )
    assert best["sigma_m_sparc"] < 0.1, (
        f"SPARC sigma/m(100) = {best['sigma_m_sparc']:.4f}, expected < 0.1. "
        f"If >= 0.1, the SPARC constraint is violated."
    )


def test_v40_48_total_combinations_consistent():
    """The total_combinations must equal the product of grid sizes.

    5 sigma_0 * 5 a_slope * 3 v_ref = 75 combinations.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    grids = data["parameter_grids"]
    expected = len(grids["sigma_0_grid"]) * len(grids["a_slope_grid"]) * len(grids["v_ref_grid"])
    assert data["total_combinations"] == expected, (
        f"Total combinations = {data['total_combinations']}, expected {expected}. "
        f"If mismatch, the parameter grid is wrong."
    )


def test_v40_48_reviewer_is_550b():
    """The reviewer field should be Nemotron 3 Ultra 550B (per upgrade).

    Per user directive 2026-10-19: switch from 120B to 550B Ultra.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    reviewer = data.get("reviewer", "")
    assert "550B" in reviewer, (
        f"Reviewer = '{reviewer}', expected to contain '550B'. "
        f"Per user directive 2026-10-19, all Nemotron calls should use 550B Ultra."
    )


if __name__ == "__main__":
    for name in dir():
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  PASS  {name}")
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                sys.exit(1)
    print("All 5 v40.48 background-refit regression tests pass.")
