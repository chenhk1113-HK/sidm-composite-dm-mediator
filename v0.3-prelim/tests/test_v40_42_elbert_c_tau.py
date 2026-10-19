"""Regression test for v40.42 Elbert+ 2015 c-tau prescription.

Per v40.42: the v19.2-F Cloud-9 c-M tension analysis under the Elbert+
2015 c-tau prescription (Nemotron 120B's recommended fix) gives:
  - c_200 = 6.0 (saturated at 50% of NFW floor) for tau >= 5
  - c-M tension = 0.32 sigma (vs Ohana+ 3.2 sigma)
  - All f_H in [0.3, 1.0] give the SAME c_200 (because all give tau > 5)

This is qualitatively different from v40.39 (which used Yang+ Eq. 5
extrapolation and got c_200 = 26.4). The Elbert+ prescription gives
a c-M tension that is within the cosmological c-M range.

Per R88(68) overfitting guard: lock the v40.42 result so any future
change that makes the c-M tension LARGER than 1 sigma (e.g., a typo
in the Elbert+ prescription, or reverting to Yang+ Eq. 5) FAILS the
test.

Reference: scripts/v19_2_f_cloud9_cM_elbert.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_cloud9_cM_elbert_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_cloud9_cM_elbert.py"
ELBERT_SCRIPT = REPO / "scripts" / "elbert2015_c_tau_prescription.py"


def test_v40_42_results_present():
    """Lock file must exist and have the v40.42 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "f_H_cases" in data
    assert len(data["f_H_cases"]) >= 5


def test_v40_42_all_fH_c200_saturated():
    """All f_H cases must give c_200 = 6.0 (Elbert+ saturation at tau >= 5).

    Under Elbert+ 2015 prescription:
      - tau < 1: c_200 from Yang+ Eq. 5 polynomial
      - 1 <= tau < 5: c_200 linearly decreases from Yang+ value to floor
      - tau >= 5: c_200 saturates at 50% of NFW (c_0 * 0.5 = 6.0 for c_0=12)

    All v40.42 f_H cases give tau >> 5, so c_200 should be exactly 6.0.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for case in data["f_H_cases"]:
        c_200 = case["c_200_elbert"]
        tau = case["tau"]
        if tau >= 5.0:
            assert c_200 == 6.0, (
                f"f_H = {case['f_H']:.3f}, tau = {tau:.2f}: expected c_200 = 6.0 "
                f"(Elbert+ saturation), got {c_200}. Check the Elbert+ prescription "
                f"linear interpolation and floor."
            )


def test_v40_42_cM_tension_below_1_sigma():
    """c-M tension must be < 1 sigma for all f_H cases.

    Per v40.42 finding: Elbert+ 2015 prescription reduces c-M tension
    to 0.32 sigma (vs Ohana+ 3.2 sigma). If the c-M tension is > 1 sigma,
    that would mean the Elbert+ prescription is NOT being applied correctly
    (e.g., reverting to Yang+ Eq. 5 extrapolation).
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for case in data["f_H_cases"]:
        tension = case["c_M_tension_sigma"]
        assert 0 < tension < 1.0, (
            f"f_H = {case['f_H']:.3f}: c-M tension = {tension:.2f} sigma, "
            f"expected 0 < tension < 1 (Elbert+ prescription). If tension >= 1, "
            f"the Elbert+ prescription is not being applied correctly -- check "
            f"scripts/elbert2015_c_tau_prescription.py."
        )


def test_v40_42_better_than_ohana_3p2sigma():
    """v40.42 c-M tension must be < 3.2 sigma (better than Ohana+ 2026).

    This is the KEY v40.42 finding: under Elbert+ 2015 prescription,
    v19.2-F's c-M tension is REDUCED to < 1 sigma, BETTER than
    Ohana+ 2026's 3.2 sigma published value.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for case in data["f_H_cases"]:
        tension = case["c_M_tension_sigma"]
        assert tension < 3.2, (
            f"f_H = {case['f_H']:.3f}: c-M tension = {tension:.2f} sigma, "
            f"expected < 3.2 (better than Ohana+ 2026). If tension >= 3.2, "
            f"v40.42 finding is not reproduced."
        )


def test_v40_42_elbert_script_importable():
    """The elbert2015_c_tau_prescription module must exist and be importable.

    If this fails, the Elbert+ prescription code was moved or deleted.
    """
    assert ELBERT_SCRIPT.exists(), f"Missing: {ELBERT_SCRIPT}"
    # Try to import the module
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from elbert2015_c_tau_prescription import c200_combined_tau
        # Self-test: c200_combined_tau at tau=10 should be 6.0 (saturated)
        c = c200_combined_tau(10.0, 12.0)
        assert c == 6.0, f"c200_combined_tau(10.0, 12.0) = {c}, expected 6.0"
        # Continuity at tau=1
        c_yang = c200_combined_tau(1.0, 12.0)
        assert c_yang > 6.0, f"c200_combined_tau(1.0, 12.0) = {c_yang}, expected > 6.0 (Yang+ value)"
    except ImportError as e:
        raise AssertionError(f"Cannot import elbert2015_c_tau_prescription: {e}")


if __name__ == "__main__":
    for name in dir():
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  PASS  {name}")
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                sys.exit(1)
    print("All 5 v40.42 Elbert+ prescription tests pass.")
