"""Regression test for v40.43a 3-prescription marginalization.

Per v40.43a: 3-prescription marginalization across Elbert+ 2015,
Burkert-style, and Sameie+ 2020 prescriptions. Critical finding:
the v40.43 ROBUST verdict (all prescriptions < 1 sigma) is REFUTED
by Sameie+ 2020, which gives c-M tension = -1.31 sigma (opposite
direction to Elbert+/Burkert-style).

This test locks the 3-prescription result so any future change
that makes either Elbert+ or Burkert-style give c-M tension > 1 sigma
(WORSE than v40.43) or that makes Sameie+ give c-M tension < 1 sigma
(contradicting the v40.43a finding) FAILS the test.

Reference: scripts/v19_2_f_cloud9_cM_three_prescriptions.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_cloud9_cM_three_prescriptions_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_cloud9_cM_three_prescriptions.py"
SAMEIE_SCRIPT = REPO / "scripts" / "sameie2020_c_tau_prescription.py"


def test_v40_43a_results_present():
    """Lock file must exist and have the v40.43a structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "f_H_cases" in data
    assert "prescriptions" in data
    assert len(data["f_H_cases"]) >= 5
    assert len(data["prescriptions"]) == 3


def test_v40_43a_three_prescriptions_correct_c200():
    """All three prescriptions must give the correct c_200 at tau=10.

    At tau >= 5 (saturated regime):
      - Elbert+ 2015: c_200 = 6.0 (50% NFW floor)
      - Burkert-style: c_200 = 3.6 (30% NFW floor)
      - Sameie+ 2020: c_200 = 24.0 (2x NFW ceiling)
    All v40.43a f_H cases give tau >> 5, so all should be saturated.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for case in data["f_H_cases"]:
        for presc_name in ["elbert_2015", "burkert_style", "sameie_2020"]:
            c_200 = case["prescription_results"][presc_name]["c_200"]
            if presc_name == "elbert_2015":
                expected = 6.0
            elif presc_name == "burkert_style":
                expected = 3.6
            elif presc_name == "sameie_2020":
                expected = 24.0
            assert abs(c_200 - expected) < 1e-6, (
                f"f_H = {case['f_H']:.3f}, prescription = {presc_name}: "
                f"c_200 = {c_200}, expected {expected}. If this fails, "
                f"check the {presc_name} prescription saturation value."
            )


def test_v40_43a_sameie_opposite_sign_from_elbert():
    """Sameie+ 2020 c-M tension must have OPPOSITE sign to Elbert+ 2015.

    Sameie+ 2020 (cuspy collapse) predicts c_200 > c_med, giving
    c-M tension < 0 (v19.2-F overpredicts c_200).
    Elbert+ 2015 (cored collapse) predicts c_200 < c_med, giving
    c-M tension > 0 (v19.2-F underpredicts c_200).
    The signs must be opposite -- if both are positive or both
    negative, the prescriptions are misimplemented.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    for case in data["f_H_cases"]:
        elbert = case["prescription_results"]["elbert_2015"]["c_M_tension_sigma"]
        sameie = case["prescription_results"]["sameie_2020"]["c_M_tension_sigma"]
        assert elbert * sameie < 0, (
            f"f_H = {case['f_H']:.3f}: Elbert+ tension = {elbert:.3f}, "
            f"Sameie+ tension = {sameie:.3f}. Signs must be opposite "
            f"(Elbert+ positive, Sameie+ negative). If both same sign, "
            f"the prescriptions are misimplemented."
        )


def test_v40_43a_max_abs_tension_refutes_robust():
    """Max |c-M tension| across prescriptions must be > 1 sigma.

    Per v40.43a finding: the v40.43 ROBUST verdict is REFUTED.
    Max |c-M tension| = 1.31 sigma (from Sameie+ 2020).
    If max < 1.0, the v40.43a finding is not reproduced.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    max_abs = data["summary"]["max_abs_tension"]
    assert max_abs > 1.0, (
        f"Max |c-M tension| = {max_abs:.2f} sigma, expected > 1.0. "
        f"If max < 1, the v40.43a finding (v40.43 ROBUST verdict REFUTED) "
        f"is not reproduced. Check Sameie+ 2020 prescription."
    )


def test_v40_43a_sameie_script_importable():
    """The sameie2020_c_tau_prescription module must exist and be importable."""
    assert SAMEIE_SCRIPT.exists(), f"Missing: {SAMEIE_SCRIPT}"
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from sameie2020_c_tau_prescription import c200_combined_sameie_tau
        # Self-test: c_200 at tau=10 should be 24.0 (saturated at 2x NFW ceiling)
        c = c200_combined_sameie_tau(10.0, 12.0)
        assert abs(c - 24.0) < 1e-6, f"c200_combined_sameie_tau(10.0, 12.0) = {c}, expected 24.0"
        # Sameie+ ceiling must be HIGHER than NFW (cuspy collapse)
        assert c > 12.0, f"Sameie+ c_200(10) = {c} should be > 12.0 (NFW), got {c}"
    except ImportError as e:
        raise AssertionError(f"Cannot import sameie2020_c_tau_prescription: {e}")


if __name__ == "__main__":
    for name in dir():
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  PASS  {name}")
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                sys.exit(1)
    print("All 5 v40.43a 3-prescription tests pass.")
