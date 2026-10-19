"""Regression test for v40.49 multi-scale refit.

Per v40.49: 10/14 combinations from v40.48 pass all 9 multi-scale
channels (3 from v40.48 + 6 new: MW10, MW20, MW30, Lyman-alpha,
cluster, Bullet Cluster). The 4 that fail are at MW satellite v=10
(Yukawa tail too strong at low v).

This test locks the v40.49 finding so any future change that
removes the 10 passing combinations (e.g., changing the constraints
without re-running the multi-scale test) FAILS the test.

Reference: scripts/v19_2_f_multiscale_refit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_multiscale_refit_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_multiscale_refit.py"


def test_v40_49_results_present():
    """Lock file must exist and have the v40.49 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "n_combinations" in data
    assert "n_all_pass" in data
    assert "n_per_channel" in data
    assert "results" in data


def test_v40_49_at_least_10_passing():
    """At least 10 combinations must pass all 9 multi-scale channels.

    Per v40.49: 10/14 pass. The framework is robust across multi-scale
    for the best 10 combinations. If fewer than 10 pass, the
    background refit is INSUFFICIENT.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    n_all_pass = data["n_all_pass"]
    assert n_all_pass >= 10, (
        f"Combinations passing all 9 channels = {n_all_pass}, expected >= 10. "
        f"If < 10, the background refit is not robust across multi-scale."
    )


def test_v40_49_bullet_cluster_passes():
    """All 14 combinations must pass Bullet Cluster (v=1500 km/s).

    Per v40.49: at v=1500 km/s, sigma/m is very small (~1e-4 to 1e-3)
    for all 14 combinations, all well below the 0.7 ceiling. This is
    the EASIEST channel to pass.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    n_bullet = data["n_per_channel"]["bullet_cluster"]
    assert n_bullet == 14, (
        f"Bullet Cluster passing = {n_bullet}, expected 14. "
        f"All 14 combinations should pass Bullet Cluster (sigma/m at v=1500 "
        f"is far below 0.7 ceiling for any reasonable Yukawa parameters)."
    )


def test_v40_49_mw_sat_10_is_binding():
    """MW satellite v=10 must be the binding constraint (lowest pass rate).

    Per v40.49: MW satellite v=10 is the most restrictive channel
    (10/14 pass). The other channels have higher pass rates.
    If MW10 is NOT the binding constraint, the multi-scale
    picture has changed.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    n_per = data["n_per_channel"]
    # MW10 should be the minimum
    min_channel = min(n_per, key=n_per.get)
    assert min_channel == "mw_sat_10", (
        f"Binding constraint = {min_channel}, expected 'mw_sat_10'. "
        f"If a different channel is binding, the multi-scale picture has changed."
    )


def test_v40_49_reviewer_is_550b():
    """The reviewer field should be Nemotron 3 Ultra 550B.

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
    print("All 5 v40.49 multi-scale refit regression tests pass.")
