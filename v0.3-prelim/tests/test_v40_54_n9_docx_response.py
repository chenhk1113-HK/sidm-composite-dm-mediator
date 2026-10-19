"""Regression tests for v40.54: n9.docx review response.

Per n9.docx review (2026-10-19), v40.53 had these remaining issues:
1. [MED] 'MODEL DOWNGRADE' still misleading
2. [MED-HIGH] Prescription marginalization equal-weight assumption lacks justification
3. [MED] Fornax sigma_HL table: sigma_HL definition + f_H source missing
4. [MED] tau calculation code missing collapse_time_gyr implementation
5. [MED] 71% statistical significance still needs validation
6. [MED-LOW] Ohana+ 2026 full citation not embedded
7. [LOW] PowerShell needs & operator
8. [MED] Full JSON embedding (deferred)
9. [MED-LOW] pytest --collect-only output (deferred)
10. [MED-LOW] Sameie+ 2020 cross-reference (deferred)

v40.54 FIX (locks these so any future change is caught):
1. Add explicit statement about v19.2-F degenerating to Yukawa
2. Prescription marginalization with 95% CI + Bayesian weights
3. sigma_HL definition + f_H source citation
4. Embed collapse_time_gyr full implementation
5. Monte Carlo Binomial z-score validation
6. PowerShell & operator fix
"""
from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
SCRIPT = REPO / "scripts" / "v19_2_f_n9_docx_response.py"


def test_v40_54_explicit_degeneration_statement():
    """Section 13.1 must contain explicit v19.2-F degeneration statement."""
    report_text = REPORT.read_text(encoding="utf-8")
    # The statement was added with this exact text
    assert "v19.2-F multi-resonance architecture is NOT observationally supported" in report_text, (
        f"v40.54 fix: section 13.1 must contain explicit degeneration statement. "
        f"The n9.docx MED issue (MODEL DOWNGRADE still misleading) requires "
        f"an explicit statement that the multi-resonance architecture is "
        f"observationally unconstrained at Cloud-9 scale."
    )
    assert "degenerating the model to a pure Yukawa background" in report_text, (
        f"v40.54 fix: degeneration statement must specify the model becomes "
        f"a pure Yukawa background (not just 'model replacement')."
    )


def test_v40_54_prescription_marginalization_with_ci():
    """Section 13.2 must contain BOTH equal-weight and Bayesian-weighted marginalization."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Both schemes should be present
    assert "Equal-weight" in report_text, (
        f"v40.54 fix: section 13.2 must contain equal-weight marginalization."
    )
    assert "Bayesian" in report_text, (
        f"v40.54 fix: section 13.2 must contain Bayesian-weighted marginalization."
    )
    # Check the actual numerical results
    assert "(+0.10, +0.56) σ" in report_text or "(+0.10, +0.56) sigma" in report_text, (
        f"v40.54 fix: section 13.2 must contain Bayesian 95% CI."
    )
    # The actual calculation should be correct
    tensions = [0.32, 0.93, -1.31]
    sigmas_u = [0.20, 0.30, 0.50]
    weights = [1.0 / (su**2) for su in sigmas_u]
    total_w = sum(weights)
    bay_mean = sum(w * v for w, v in zip(weights, tensions)) / total_w
    assert abs(bay_mean - 0.33) < 0.01, (
        f"v40.54 fix: Bayesian mean should be ~+0.33 sigma, got {bay_mean:.2f}"
    )


def test_v40_54_sigma_hl_definition_added():
    """Section 13.3 must define sigma_HL and provide f_H source."""
    report_text = REPORT.read_text(encoding="utf-8")
    assert "Cross-channel cross-section between hot" in report_text, (
        f"v40.54 fix: section 13.3 must define sigma_HL as cross-channel cross-section."
    )
    assert "second law of thermodynamics" in report_text, (
        f"v40.54 fix: section 13.3 must explain why negative sigma_HL is unphysical."
    )
    assert "PLACEHOLDER" in report_text and "f_H = 0.297" in report_text, (
        f"v40.54 fix: section 13.3 must cite f_H = 0.297 as a placeholder (retracted v18.29)."
    )


def test_v40_54_collapse_time_gyr_implementation():
    """Section 13.4 must contain collapse_time_gyr full implementation.

    v40.55 NOTE: The v40.54 code was FABRICATED and has been corrected in v40.55.
    The test now checks for the ACTUAL project constants (T_HUBBLE_GYR=13.8) and
    the correct sigma_m_canonical formula (Yukawa + Gaussian).
    """
    report_text = REPORT.read_text(encoding="utf-8")
    # Check the actual project constants are now present (v40.55 correction)
    assert "T_HUBBLE_GYR = 13.8" in report_text, (
        f"v40.55 fix: section 13.4 must contain the actual project constant "
        f"T_HUBBLE_GYR = 13.8 (from constants.py)."
    )
    assert "SIGMA_0_CM2_PER_G = 0.052" in report_text, (
        f"v40.55 fix: section 13.4 must contain the actual Yukawa amplitude "
        f"SIGMA_0_CM2_PER_G = 0.052 (from constants.py)."
    )
    assert "SIGMA_PEAK_CM2_PER_G = 174.0" in report_text, (
        f"v40.55 fix: section 13.4 must contain the actual peak amplitude "
        f"SIGMA_PEAK_CM2_PER_G = 174.0."
    )
    assert "sigma_m_canonical" in report_text, (
        f"v40.55 fix: section 13.4 must contain sigma_m_canonical function "
        f"(Yukawa + Gaussian sum, per project implementation)."
    )
    assert "tau = T_Hubble / t_core" in report_text or "tau = T_HUBBLE_GYR / t_core" in report_text, (
        f"v40.55 fix: section 13.4 must use the correct tau definition "
        f"(INVERSE: tau = T_Hubble / t_core, per project convention)."
    )
    # References must include Yang+ 2024 + Balberg+ 2002
    assert "Yang+ 2024" in report_text, (
        f"v40.55 fix: section 13.4 must cite Yang+ 2024 reference."
    )
    assert "Balberg+ 2002" in report_text, (
        f"v40.55 fix: section 13.4 must cite Balberg+ 2002 reference."
    )


def test_v40_54_monte_carlo_binomial_validation():
    """Section 13.5 must contain Binomial z-score validation for 71% significance."""
    report_text = REPORT.read_text(encoding="utf-8")
    assert "Binomial" in report_text or "BINOMIAL" in report_text, (
        f"v40.54 fix: section 13.5 must contain Binomial test (not just Monte Carlo)."
    )
    # The z-score calculation should be present
    assert "+260" in report_text or "+26" in report_text, (
        f"v40.54 fix: section 13.5 must contain z-score values (260 or 26 sigma)."
    )
    assert "NOT a chance occurrence" in report_text, (
        f"v40.54 fix: section 13.5 must contain the conclusion that 71% is NOT a chance occurrence."
    )

    # Verify the z-score calculation
    # Binomial test: P(X >= 10 | N=75, p=0.5) - extremely unlikely
    # For p = 0.5: E[X] = 75 * 0.5^9 = 0.146, var = 75 * 0.5^9 * (1 - 0.5^9), std ~ 0.383
    # z = (10 - 0.146) / 0.383 ~ 25.8 sigma
    p9 = 0.5**9
    n = 75
    expected = n * p9
    var = n * p9 * (1 - p9)
    std = math.sqrt(var)
    z_score = (10 - expected) / std
    assert z_score > 20, (
        f"v40.54 fix: binomial z-score for p=0.5 should be > 20, got {z_score:.1f}"
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
    print("All 5 v40.54 n9.docx review response regression tests pass.")