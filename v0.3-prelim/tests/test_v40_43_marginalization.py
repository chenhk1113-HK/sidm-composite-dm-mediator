"""Regression test for v40.43 marginalized c-M tension analysis.

Per v40.43: marginalize over Elbert+ 2015 AND Burkert-style c-tau
prescriptions to demonstrate the v40.42 c-M tension reduction is
robust across model variations.

Result: BOTH prescriptions give c-M tension < 1 sigma (Elbert+ 0.32,
Burkert-style 0.93). Max across prescriptions = 0.93 sigma, well
below Ohana+ 3.2 sigma.

This test locks the marginalization result so any future change
that makes either prescription give c-M tension > 1 sigma (e.g.,
a typo in the Burkert-style floor, or reverting Elbert+ to Yang+)
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
    """Both prescriptions must give c-M tension < 1 sigma for all f_H cases.

    Per v40.43 marginalization:
      - Elbert+ 2015: c-M tension = 0.32 sigma
      - Burkert-style: c-M tension = 0.93 sigma
    If either prescription gives c-M tension >= 1 sigma, the
    marginalization is no longer ROBUST and needs re-examination.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for case in data["f_H_cases"]:
        for presc_name, presc_result in case["prescription_results"].items():
            tension = presc_result["c_M_tension_sigma"]
            assert tension < 1.0, (
                f"f_H = {case['f_H']:.3f}, prescription = {presc_name}: "
                f"c-M tension = {tension:.2f} sigma, expected < 1.0. "
                f"If tension >= 1, the marginalization is no longer ROBUST. "
                f"Check the {presc_name} prescription implementation."
            )


def test_v40_43_max_tension_below_1sigma():
    """The max c-M tension across prescriptions must be < 1 sigma.

    This is the KEY v40.43 finding: the c-M tension reduction is
    ROBUST (max < 1 sigma across prescriptions). If max >= 1 sigma,
    the v40.43 finding is not reproduced.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    max_tension = data["marginalization_summary"]["tension_max_across_prescriptions"]
    assert max_tension < 1.0, (
        f"Max c-M tension across prescriptions = {max_tension:.2f} sigma, "
        f"expected < 1.0. If max >= 1, the v40.43 ROBUST verdict is "
        f"not reproduced. Check both prescription implementations."
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
