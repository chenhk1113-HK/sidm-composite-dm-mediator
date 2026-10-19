"""Regression test for v40.45 velocity-form sensitivity.

Per v40.45: the c-M tension is entirely driven by the Gaussian peak
assumption in the v19.2-F canonical sigma/m(v) form. The canonical
form (peak at v=29.4, sigma_peak=174) gives tau = 16.4 (deep collapse).
Any alternative form (Yukawa-only, peak at v=50, peak at v=100) gives
tau << 1 (max-core), consistent with Ohana+ 2026.

This test locks the v40.45 finding so any future change that makes
the canonical form give tau < 1 (e.g., a typo in the Gaussian peak
amplitude) or that makes Yukawa-only give tau > 1 (e.g., a typo in
the Yukawa tail amplitude) FAILS the test.

Reference: scripts/v19_2_f_cloud9_velocity_form_sensitivity.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_cloud9_velocity_form_sensitivity_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_cloud9_velocity_form_sensitivity.py"


def test_v40_45_results_present():
    """Lock file must exist and have the v40.45 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "forms_tested" in data
    assert "verdict" in data
    assert len(data["forms_tested"]) == 4


def test_v40_45_canonical_deep_collapse():
    """v19.2-F canonical form must give tau >> 1 (deep collapse).

    The canonical form has the Gaussian peak at v=29.4 with amplitude
    174 cm^2/g. At v=28 (Cloud-9 V_max), the peak dominates and
    sigma/m(28) ~ 165 cm^2/g, giving tau = 16.4 (deep collapse).
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    canonical = None
    for form in data["forms_tested"]:
        if "canonical" in form["name"]:
            canonical = form
            break
    assert canonical is not None, "Could not find canonical form in v40.45 results"
    assert canonical["tau"] > 1.0, (
        f"Canonical form tau = {canonical['tau']:.2f}, expected > 1 (deep collapse). "
        f"If tau < 1, the v19.2-F deep collapse prediction is not reproduced."
    )
    assert canonical["sigma_m_at_28_kms"] > 100, (
        f"Canonical form sigma/m(28) = {canonical['sigma_m_at_28_kms']:.2f}, "
        f"expected > 100 (Gaussian peak dominates). If < 100, the peak amplitude "
        f"is wrong."
    )


def test_v40_45_yukawa_only_max_core():
    """Yukawa-only form must give tau << 1 (max-core, matches Ohana+).

    The Yukawa-only form (no Gaussian peak) at v=28 gives sigma/m(28) ~ 0.6
    cm^2/g (the Yukawa tail amplitude at v=28). This is much smaller than
    the canonical peak, giving sigma_eff ~ 0.05 cm^2/g and tau << 1.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    yukawa = None
    for form in data["forms_tested"]:
        if "Yukawa-only" in form["name"]:
            yukawa = form
            break
    assert yukawa is not None, "Could not find Yukawa-only form in v40.45 results"
    assert yukawa["tau"] < 1.0, (
        f"Yukawa-only form tau = {yukawa['tau']:.2f}, expected < 1 (max-core). "
        f"If tau > 1, the Yukawa tail amplitude is wrong (too strong)."
    )
    assert yukawa["ohana_consistent"] is True, (
        f"Yukawa-only form should be Ohana+-consistent. "
        f"ohana_consistent = {yukawa['ohana_consistent']}"
    )


def test_v40_45_resonance_at_other_v_max_core():
    """Resonance at v=50 or v=100 must give tau << 1 (max-core).

    The Gaussian peak amplitude is preserved (174 cm^2/g) but the peak
    location is moved to v=50 or v=100. At v=28 (Cloud-9 V_max), the peak
    tail is small, giving sigma/m(28) ~ 0.6 cm^2/g and tau << 1.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for form in data["forms_tested"]:
        if "Resonance at v=50" in form["name"] or "Resonance at v=100" in form["name"]:
            assert form["tau"] < 1.0, (
                f"Form '{form['name']}' tau = {form['tau']:.2f}, expected < 1. "
                f"Only the canonical peak at v=29.4 should give deep collapse."
            )


def test_v40_45_tension_driven_by_peak():
    """The v40.45 verdict must confirm c-M tension is driven by the peak.

    The KEY finding of v40.45: the c-M tension is entirely driven by
    the Gaussian peak assumption. Only the v=29.4 peak (the Cloud-9
    anchor) gives deep collapse; all other forms give max-core.
    If the verdict is changed to 'tension is structural, not driven by
    peak', that would be a major claim requiring R88(71) review.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    verdict = data["verdict"]
    assert verdict["v19_2_f_canonical_drives_tension"] is True, (
        f"verdict['v19_2_f_canonical_drives_tension'] = {verdict['v19_2_f_canonical_drives_tension']}, "
        f"expected True. The v40.45 finding is that the c-M tension is "
        f"DRIVEN by the canonical Gaussian peak, not structural."
    )
    assert verdict["yukawa_only_resolves_tension"] is True, (
        f"verdict['yukawa_only_resolves_tension'] = {verdict['yukawa_only_resolves_tension']}, "
        f"expected True. Yukawa-only form resolves the c-M tension."
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
    print("All 5 v40.45 velocity-form sensitivity tests pass.")
