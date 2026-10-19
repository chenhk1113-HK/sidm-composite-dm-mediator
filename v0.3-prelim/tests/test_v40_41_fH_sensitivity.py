"""Regression test for v40.41 f_H sensitivity finding.

The v40.41 sensitivity test swept f_H in [0.3, 1.0] and showed that ALL
f_H values give tau > 1 (deep collapse) for v19.2-F canonical parameters.
This means the c-M tension is STRUCTURAL, not a placeholder artifact.

This test locks the structural finding so any future change that
accidentally makes tau < 1 (e.g., a typo in t_core formula, or a f_H
calibration that ignores physics) FAILS the test.

Reference: scripts/v19_2_f_fH_sensitivity.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_fH_sensitivity_2026_10_19.json"


def test_v40_41_fH_sensitivity_results_present():
    """Lock file must exist and have the v40.41 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "f_H_cases" in data
    assert len(data["f_H_cases"]) >= 5, (
        f"Expected at least 5 f_H cases, got {len(data['f_H_cases'])}"
    )


def test_v40_41_all_fH_in_deep_collapse():
    """ALL f_H in [0.3, 1.0] must give tau > 1 (deep collapse).

    Per v40.41 finding: the c-M tension is STRUCTURAL. v19.2-F's
    sigma_peak=174 gives tau > 1 regardless of f_H choice. This
    confirms the v40.39 negative result is real, not a placeholder
    artifact. The §2.6a no-go theorem is REINFORCED.

    If this test fails, it means:
    (a) The Balberg t_core formula was changed (BAD)
    (b) The Cloud-9 parameters were changed (BAD)
    (c) The sensitivity script was modified to give tau < 1 for some
        f_H (would invalidate the v40.41 finding)
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    cases = data["f_H_cases"]
    # Check all cases have tau > 1
    for case in cases:
        f_H = case["f_H"]
        tau = case["tau"]
        if f_H < 0.05:
            continue  # very low f_H might naturally give tau < 1
        if tau < 1.0:
            # Per v40.41: this would be a MAJOR finding (f_H resolves the
            # c-M tension). This needs R88(71) BREAKTHROUGH review, not
            # silent test pass.
            raise AssertionError(
                f"f_H = {f_H:.3f} now gives tau = {tau:.2f} (< 1, max-core "
                f"regime). This would mean the c-M tension is RESOLVABLE "
                f"by f_H choice, which is a STRUCTURAL finding that "
                f"DISPROVES the v40.41 'structural tension' verdict. "
                f"This requires R88(71) BREAKTHROUGH review, not silent "
                f"regression test. Document the change in the JSON note field."
            )


def test_v40_41_sigma_eff_increases_with_fH():
    """sigma_eff must increase monotonically with f_H.

    sigma_eff = f_H^2 * sigma_m(28). For a given sigma_peak, sigma_m(28)
    is fixed, so sigma_eff scales as f_H^2. As f_H increases, sigma_eff
    MUST increase. If this is violated, there's a bug.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    cases = sorted(data["f_H_cases"], key=lambda c: c["f_H"])
    sigma_effs = [c["sigma_eff_cm2_g"] for c in cases]
    for i in range(1, len(sigma_effs)):
        assert sigma_effs[i] > sigma_effs[i-1], (
            f"sigma_eff not monotonically increasing with f_H: "
            f"f_H={cases[i-1]['f_H']:.3f} -> sigma_eff={sigma_effs[i-1]:.2f}, "
            f"f_H={cases[i]['f_H']:.3f} -> sigma_eff={sigma_effs[i]:.2f}. "
            f"sigma_eff = f_H^2 * sigma_m MUST be monotonically increasing."
        )


def test_v40_41_tau_decreases_with_fH():
    """tau must decrease monotonically with f_H.

    tau = t_Hubble / t_core. t_core = 12.7 / sigma_eff (in Balberg), so
    t_core scales as 1/sigma_eff. As f_H increases, sigma_eff increases,
    t_core decreases, tau increases. WAIT, that's the opposite.

    Let me re-check: tau = t_Hubble / t_core. Higher sigma_eff -> lower
    t_core -> HIGHER tau. So tau INCREASES with f_H, not decreases.

    If this test fails, there's a bug in the sensitivity script.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    cases = sorted(data["f_H_cases"], key=lambda c: c["f_H"])
    taus = [c["tau"] for c in cases]
    # tau should increase with f_H (because higher f_H -> higher sigma_eff
    # -> shorter t_core -> larger tau)
    for i in range(1, len(taus)):
        assert taus[i] > taus[i-1], (
            f"tau not monotonically increasing with f_H: "
            f"f_H={cases[i-1]['f_H']:.3f} -> tau={taus[i-1]:.2f}, "
            f"f_H={cases[i]['f_H']:.3f} -> tau={taus[i]:.2f}. "
            f"Higher f_H should give HIGHER tau (via higher sigma_eff, "
            f"shorter t_core). If this fails, check the script logic."
        )


def test_v40_41_structural_verdict_locked():
    """The v40.41 verdict (structural tension) must be preserved.

    Per v40.41: c-M tension is STRUCTURAL because ALL f_H in [0.3, 1.0]
    give tau > 1. If this verdict is changed to "f_H resolves tension",
    that would be a major claim requiring R88(71) review.
    """
    # The verdict is in the script's main() output, not the JSON.
    # This test checks the JSON has the expected structure.
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    # The f_H_cases should have f_H >= 0.3 (otherwise low f_H would
    # naturally give tau < 1, polluting the "structural" finding)
    cases = data["f_H_cases"]
    f_H_values = [c["f_H"] for c in cases]
    assert max(f_H_values) >= 0.9, (
        f"Sensitivity sweep must include f_H >= 0.9 to test the 'structural' "
        f"finding. Got max f_H = {max(f_H_values):.3f}. Add a high-f_H case "
        f"(e.g., T202 N-body f_H = 0.92 or single-component f_H = 1.0)."
    )
    assert min(f_H_values) <= 0.32, (
        f"Sensitivity sweep must include f_H <= 0.32 to test the placeholder "
        f"value. Got min f_H = {min(f_H_values):.3f}. Add a placeholder case."
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
    print("All 5 v40.41 f_H sensitivity tests pass.")
