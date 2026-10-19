"""Regression test for the v19.2-F Cloud-9 c-M tension test (negative result).

Per v40.38 self-verification framework: lock the v19.2-F NEGATIVE result so
any future change that accidentally makes the result positive (i.e., claims
v19.2-F works for Cloud-9) FAILS this test.

The v19.2-F result: canonical parameters (sigma_peak=174, f_H=0.297) predict
sigma_eff = 14.6 at v=28 km/s, giving tau = 16.3 (deep core collapse). This
is OUTSIDE the Yang+ Eq. 5 polynomial validity range (tau in [0, 1]) and is
INCONSISTENT with the observed Cloud-9 c=4 (max-core, tau ~ 0.18 per
Ohana+ 2026).

This is a STRUCTURAL CONSTRAINT: v19.2-F's parameters are too strong for
Cloud-9. Per R88(68) lesson, do NOT pretend this is a "win" -- it is an
honest negative result.

Per the v19.1.5 honest framing: lock this as "FAILED VALIDATION" so any
future accidental "fix" is caught at test time.

Reference: scripts/v19_2_f_cloud9_cM_tension.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_cloud9_cM_tension.json"


def test_v19_2_f_cloud9_results_present():
    """Lock file must exist and have the v19.2-F structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "gravothermal" in data
    assert "c_M_result" in data
    assert "params" in data


def test_v19_2_f_canonical_tau_in_deep_collapse():
    """v19.2-F canonical parameters MUST predict tau > 1 (deep core collapse).

    With sigma_peak=174 and f_H=0.297, the effective cross-section at v=28
    is sigma_eff ~ 14.6 cm^2/g. The Balberg t_core at this sigma_eff for
    Cloud-9 (M=4.7e9, c=12, V_max~30 km/s) is ~0.84 Gyr, giving tau ~ 16.

    If this test fails, it means EITHER:
    (a) The script was modified to use lower sigma_peak or f_H (good, but
        should be documented as a parameter change in the note field).
    (b) The Balberg formula was changed (BAD -- the formula is verified by
        T208/T212 review and should not be silently modified).
    (c) The Cloud-9 halo parameters were changed (BAD -- these are
        published from Anand+ 2025 / Ohana+ 2026).

    Allowed: tau in [10, 30] (allow ±50% drift for numerical noise).
    If anyone changes the script in a way that gives tau in [0, 1], this
    test will catch it. That's the goal.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    tau = data["gravothermal"]["tau"]
    assert tau > 1.0, (
        f"v19.2-F canonical tau is now {tau:.2f} (was 16.35 in v40.39 baseline). "
        f"This means the script's parameters were changed in a way that puts "
        f"Cloud-9 in max-core regime. THIS IS A RED FLAG (R88(68) overfitting risk): "
        f"if v19.2-F's parameters genuinely put Cloud-9 in max-core, that should "
        f"go through the full R88(71) BREAKTHROUGH checklist, not silent test fix. "
        f"Document any parameter change in the note field of the JSON."
    )


def test_v19_2_f_yang_plus_validity_outside():
    """v19.2-F must explicitly flag tau > 1 as OUTSIDE Yang+ Eq. 5 validity.

    Per the script: Yang+ 2024 Eq. 5 polynomial fit is only valid for tau in
    [0, 1]. v19.2-F's tau > 1 means the model is outside its domain of
    applicability. This flag prevents silently using a wrong model.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    validity = data["gravothermal"]["tau_yang_plus_validity"]
    assert "OUTSIDE" in validity, (
        f"tau_yang_plus_validity = {validity!r}, expected to contain 'OUTSIDE' "
        f"for v19.2-F canonical parameters (tau > 1). If this changed, the "
        f"script's validity flag was modified -- verify the Yang+ model is "
        f"actually being applied in its valid range."
    )


def test_v19_2_f_verdict_acknowledges_uncertainty():
    """Verdict must acknowledge tau > 1 uncertainty, NOT claim a 'win'.

    v19.2-F's canonical parameters do NOT improve on Ohana+ 3.2 sigma. Any
    verdict claiming a "win" (REDUCTION in tension) is a R88(68) red flag.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    verdict = data["c_M_result"]["verdict"]
    assert "uncertain" in verdict.lower() or "INCREASES" in verdict, (
        f"v19.2-F verdict = {verdict!r}. Expected to acknowledge tau > 1 "
        f"uncertainty OR explicitly say tension INCREASES. A verdict claiming "
        f"v19.2-F REDUCES tension would be a R88(68) red flag (silent overfitting)."
    )


def test_v19_2_f_sigma_eff_in_expected_range():
    """v19.2-F sigma_eff at v=28 must be in expected range [10, 25] cm^2/g.

    v19.2-F canonical: sigma_peak=174, f_H=0.297
    sigma_m(v=28) = 174 * exp(-0.5 * ((28-29.4)/4.4)^2) = 165 cm^2/g
    sigma_eff = 0.297^2 * 165 = 14.6 cm^2/g

    Allowed drift: [10, 25] cm^2/g (allow ±50% for numerical noise).
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    sigma_eff = data["params"]["sigma_eff_cm2_g"]
    assert 10 <= sigma_eff <= 25, (
        f"v19.2-F sigma_eff = {sigma_eff:.2f} cm^2/g, expected 10-25 "
        f"(v40.39 baseline = 14.6). If outside this range, the canonical "
        f"parameters (sigma_peak=174, f_H=0.297) were changed -- document in JSON note."
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
    print("All 5 v19.2-F Cloud-9 c-M tension tests pass.")
