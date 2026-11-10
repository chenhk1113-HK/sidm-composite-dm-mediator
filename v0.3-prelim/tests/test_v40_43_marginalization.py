"""Regression test for v40.43 marginalized c-M tension analysis.

Per v40.43: marginalize over Elbert+ 2015 AND Burkert-style c-tau
prescriptions to test whether the v40.42 c-M tension reduction is robust
across model variations.

CORRECTED 2026-11-10 (registry defect D9). The assertions in this file
previously read "Elbert+ 0.32 sigma, Burkert-style 0.93 sigma, max < 1
sigma, ROBUST". Those numbers were produced by c_M_tension_sigma() dividing
a dex deviation by 0.16 * ln(10) instead of 0.16, understating every tension
by a factor ln(10) = 2.303, AND by subtracting them from Ohana+ 2026's 3.2
sigma, which is quoted against a DIFFERENT c-M relation (their own, implied
median 12.81 at Cloud-9 mass) than the Diemer+ 2019 median (7.90) the code
used. Under the corrected convention (1 sigma = 0.16 dex):

    anchor            Elbert+ (c_200 = 6.0)   Burkert-style (c_200 = 3.6)
    Diemer+ 2019          +0.75 sigma               +2.13 sigma
    Ohana+ 2026           +2.06 sigma               +3.45 sigma

so the v40.43 "all prescriptions < 1 sigma -> ROBUST" verdict does NOT hold
and is asserted against here. The reduction is stated anchor-independently:
Elbert+ moves log10(6.0/4.0) = 0.176 dex = 1.10 sigma relative to Ohana+
2026's own measured c_200 = 4.0.

This test locks the marginalization result so any future change that moves
either prescription off these values (a typo in the Burkert-style floor, a
revert of Elbert+ to Yang+, or a re-introduction of the ln(10) unit error)
FAILS the test.

Reference: scripts/v19_2_f_cloud9_cM_marginalized.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_cloud9_cM_marginalized_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_cloud9_cM_marginalized.py"
ELBERT_SCRIPT = REPO / "scripts" / "elbert2015_c_tau_prescription.py"
BURKERT_SCRIPT = REPO / "scripts" / "burkert_style_c_tau_prescription.py"


def test_v40_43_results_present():
    """Lock file must exist and have the v40.43 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "f_H_cases" in data
    assert "prescriptions" in data
    assert len(data["f_H_cases"]) >= 5
    assert len(data["prescriptions"]) == 2


def test_v40_43_both_prescriptions_below_1sigma():
    """DEPRECATED ASSERTION, REPLACED (D9 fix 2026-11-10).

    This test used to require every prescription to give c-M tension
    < 1 sigma. That held only because c_M_tension_sigma() divided the dex
    deviation by 0.16 * ln(10) instead of 0.16 (understating sigma by 2.303).
    With the convention Ohana+ 2026 actually use (1 sigma = 0.16 dex) the
    Burkert-style prescription gives 2.13 sigma (Diemer+ anchor) / 3.45 sigma
    (Ohana+ anchor). This test now pins the corrected per-prescription values
    at BOTH anchors, which is a strictly stronger regression guard than the
    old "< 1 sigma" bound.
    """
    expected = {
        "elbert_2015": {"diemer": 0.746, "ohana": 2.059},
        "burkert_style": {"diemer": 2.132, "ohana": 3.445},
    }
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for case in data["f_H_cases"]:
        for presc_name, presc_result in case["prescription_results"].items():
            exp = expected[presc_name]
            diemer = presc_result["c_M_tension_sigma_diemer2019"]
            ohana = presc_result["c_M_tension_sigma_ohana2026"]
            assert abs(diemer - exp["diemer"]) < 0.05, (
                f"f_H = {case['f_H']:.3f}, prescription = {presc_name}: Diemer+ 2019 "
                f"anchor tension = {diemer:.3f} sigma, expected {exp['diemer']:.2f}. "
                f"A deviation here means the prescription floor changed or the "
                f"ln(10) unit error (defect D9) was reintroduced."
            )
            assert abs(ohana - exp["ohana"]) < 0.05, (
                f"f_H = {case['f_H']:.3f}, prescription = {presc_name}: Ohana+ 2026 "
                f"anchor tension = {ohana:.3f} sigma, expected {exp['ohana']:.2f}. "
                f"The Ohana+ anchor is log10(12.81 / c_med_diemer) / 0.16 = 1.31 sigma "
                f"above the Diemer+ anchor; a different offset means the anchors were "
                f"changed without updating the paper."
            )
            # Anchors must never be mixed: the Ohana+ value is always larger.
            assert ohana > diemer, (
                f"{presc_name}: Ohana+ anchor ({ohana:.2f}) must exceed the Diemer+ "
                f"anchor ({diemer:.2f}) at Cloud-9 mass."
            )


def test_v40_43_max_tension_below_1sigma():
    """v40.43's "max < 1 sigma -> ROBUST" verdict is REFUTED (D9 fix).

    The c-M tension across the two prescriptions spans 0.75-2.13 sigma at the
    Diemer+ 2019 anchor and 2.06-3.45 sigma at the Ohana+ 2026 anchor, so the
    marginalization is prescription-dependent, not robust. This test asserts
    the refutation: if a future change ever makes the max drop back below
    1 sigma, the prescription floors (or the sigma convention) changed and
    the claim must be re-reviewed rather than quietly reinstated.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    summary = data["marginalization_summary"]
    max_tension = summary["tension_max_across_prescriptions"]
    assert max_tension > 1.0, (
        f"Max c-M tension across prescriptions = {max_tension:.2f} sigma. Values "
        f"below 1 sigma indicate the D9 unit error came back or a prescription "
        f"floor was loosened; re-review rather than restoring the ROBUST label."
    )
    assert max_tension < 3.2, (
        f"Max c-M tension = {max_tension:.2f} sigma should stay below Ohana+ 2026's "
        f"published 3.2 sigma at the Diemer+ anchor; if not, the marginalization no "
        f"longer improves on the observation."
    )
    # Anchor-independent statement of the reduction vs Ohana+ measured c_200 = 4.0.
    import math
    shift_sigma = math.log10(6.0 / 4.0) / 0.16
    assert abs(shift_sigma - 1.10) < 0.02, (
        f"Elbert+ vs Ohana+ measured c_200 shift = {shift_sigma:.2f} sigma; expected "
        f"1.10 sigma (0.176 dex at 0.16 dex scatter)."
    )


def test_v40_43_elbert_below_burkert():
    """Elbert+ 2015 c-M tension must be LOWER than Burkert-style.

    Elbert+ has a higher floor (50% NFW vs 30% NFW), so c_200 is
    closer to c_med, giving lower c-M tension. If Elbert+ gives
    higher c-M tension than Burkert-style, the prescriptions are
    swapped or misimplemented.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for case in data["f_H_cases"]:
        elbert = case["prescription_results"]["elbert_2015"]["c_M_tension_sigma"]
        burkert = case["prescription_results"]["burkert_style"]["c_M_tension_sigma"]
        assert elbert < burkert, (
            f"f_H = {case['f_H']:.3f}: Elbert+ tension = {elbert:.2f}, "
            f"Burkert-style tension = {burkert:.2f}. Elbert+ has higher "
            f"NFW floor (50% vs 30%), so c_200 is closer to c_med, "
            f"giving LOWER c-M tension. If Elbert+ > Burkert-style, "
            f"the prescriptions are swapped or misimplemented."
        )


def test_v40_43_both_prescriptions_importable():
    """Both prescription scripts must exist and be importable."""
    assert ELBERT_SCRIPT.exists(), f"Missing: {ELBERT_SCRIPT}"
    assert BURKERT_SCRIPT.exists(), f"Missing: {BURKERT_SCRIPT}"
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from elbert2015_c_tau_prescription import c200_combined_tau
        from burkert_style_c_tau_prescription import c200_combined_burkert_tau
        # Self-test: both prescriptions saturated at tau=10
        c_elbert = c200_combined_tau(10.0, 12.0)
        c_burkert = c200_combined_burkert_tau(10.0, 12.0)
        assert abs(c_elbert - 6.0) < 1e-6, f"Elbert+ c200(10) = {c_elbert}, expected 6.0"
        assert abs(c_burkert - 3.6) < 1e-6, f"Burkert-style c200(10) = {c_burkert}, expected 3.6"
        # Burkert-style floor must be LOWER than Elbert+ floor
        assert c_burkert < c_elbert, (
            f"Burkert-style floor ({c_burkert}) must be LOWER than Elbert+ "
            f"floor ({c_elbert}). If not, the prescriptions are misimplemented."
        )
    except ImportError as e:
        raise AssertionError(f"Cannot import prescriptions: {e}")


if __name__ == "__main__":
    for name in dir():
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  PASS  {name}")
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                sys.exit(1)
    print("All 5 v40.43 marginalization tests pass.")
