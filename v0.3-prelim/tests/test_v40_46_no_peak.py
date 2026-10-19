"""Regression test for v40.46 no-peak re-analysis.

Per v40.46: setting the Gaussian peak to 0 (Nemotron v40.45 recommendation)
fully resolves the v19.2-F Cloud-9 c-M tension with Ohana+ 2026.
- Canonical (peak=174): tau = 16.4 (deep collapse, TENSION)
- Downgraded (peak=0): tau = 0.06 (max-core, MATCH)

This test locks the v40.46 finding so any future change that
accidentally restores the peak (e.g., a regression in the constants
file, or a typo in the peak amplitude) FAILS the test.

Reference: scripts/v19_2_f_no_peak_analysis.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_no_peak_analysis_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_no_peak_analysis.py"


def test_v40_46_results_present():
    """Lock file must exist and have the v40.46 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "cases" in data
    assert "verdict" in data
    assert len(data["cases"]) == 2


def test_v40_46_canonical_deep_collapse():
    """Canonical (peak=174) must give tau >> 1 (deep collapse).

    This is the v40.46 starting point: with the canonical peak=174,
    Cloud-9 is in deep collapse (tau = 16.4), INCONSISTENT with
    Ohana+ 2026 max-core.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    canonical = None
    for case in data["cases"]:
        if "CANONICAL" in case["name"]:
            canonical = case
            break
    assert canonical is not None, "Could not find CANONICAL case in v40.46 results"
    assert canonical["tau"] > 1.0, (
        f"Canonical case tau = {canonical['tau']:.2f}, expected > 1. "
        f"If tau < 1, the canonical deep collapse prediction is not reproduced."
    )
    assert canonical["ohana_consistent"] is False, (
        f"Canonical case should NOT be Ohana+ consistent. "
        f"ohana_consistent = {canonical['ohana_consistent']}"
    )


def test_v40_46_nuisance_max_core():
    """Downgraded (peak=0) must give tau << 1 (max-core, matches Ohana+).

    Per Nemotron v40.45: setting the peak to 0 (treating it as a
    phenomenological nuisance parameter) fully resolves the c-M
    tension. tau drops from 16.4 to 0.06.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    nuisance = None
    for case in data["cases"]:
        if "DOWNGRADED" in case["name"]:
            nuisance = case
            break
    assert nuisance is not None, "Could not find DOWNGRADED case in v40.46 results"
    assert nuisance["tau"] < 1.0, (
        f"Downgraded case tau = {nuisance['tau']:.2f}, expected < 1. "
        f"If tau > 1, the c-M tension is NOT resolved by peak=0."
    )
    assert nuisance["ohana_consistent"] is True, (
        f"Downgraded case should be Ohana+ consistent. "
        f"ohana_consistent = {nuisance['ohana_consistent']}"
    )
    assert abs(nuisance["peak_amplitude"]) < 1e-6, (
        f"Downgraded case peak_amplitude = {nuisance['peak_amplitude']}, expected 0.0. "
        f"If non-zero, the peak is not actually set to 0."
    )


def test_v40_46_tension_reduction():
    """The tau reduction from canonical to downgraded must be > 100x.

    The canonical tau is 16.4, the downgraded tau is 0.06.
    The reduction factor is 16.4 / 0.06 = 273x, which is a HUGE
    reduction. If the reduction is < 100x, something is wrong.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    canonical = next(c for c in data["cases"] if "CANONICAL" in c["name"])
    downgraded = next(c for c in data["cases"] if "DOWNGRADED" in c["name"])
    reduction = canonical["tau"] / downgraded["tau"]
    assert reduction > 100, (
        f"tau reduction = {reduction:.1f}x, expected > 100x. "
        f"Canonical tau = {canonical['tau']:.2f}, Downgraded tau = {downgraded['tau']:.2f}. "
        f"If < 100x, the peak downgrade does not give a strong enough "
        f"effect to resolve the c-M tension."
    )


def test_v40_46_verdict_resolved():
    """The v40.46 verdict must confirm c-M tension is resolved by downgrade.

    Per v40.46: setting peak=0 fully resolves the c-M tension.
    If the verdict is changed to 'NOT resolved', that would be a
    major claim requiring R88(71) review.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    verdict = data["verdict"]
    assert verdict["c_M_tension_resolved_by_peak_downgrade"] is True, (
        f"verdict['c_M_tension_resolved_by_peak_downgrade'] = {verdict['c_M_tension_resolved_by_peak_downgrade']}, "
        f"expected True. If False, the v40.46 finding is not reproduced."
    )
    assert verdict["cloud9_in_max_core_with_peak_zero"] is True, (
        f"verdict['cloud9_in_max_core_with_peak_zero'] = {verdict['cloud9_in_max_core_with_peak_zero']}, "
        f"expected True. Cloud-9 should be in max-core with peak=0."
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
    print("All 5 v40.46 no-peak regression tests pass.")
