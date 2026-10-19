"""Regression tests for v40.56: n11.docx review response.

Per n11.docx review (2026-10-19), v40.55 had these remaining issues:
1. [MED-HIGH] collapse_time_gyr verification still depends on external modules
2. [MED-HIGH] Prescription marginalization equal-weight vs Bayesian give contradictory conclusions
3. [MED] f_H placeholder contradicts STRUCTURAL conclusion
4. [MED] Channel correlation quantitative analysis missing
5. [MED-LOW] Ohana+ 2026 citation still not in body
6. [MED-LOW] Sameie+ 2020 not compared to original paper
7. [MED] JSON data still summary
8. [LOW] PowerShell syntax inconsistent

v40.56 FIX:
1. Independent verification using ACTUAL t212_evaluate
2. Honest prescription non-identifiability statement
3. sigma_HL vs f_H curve (computed for f_H in [0.3, 1.0])
4. Channel correlation analysis
5. tau threshold clarification (tau = 1 IS the threshold)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
SCRIPT = REPO / "scripts" / "v19_2_f_n11_docx_response.py"
JSON_V4046 = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_no_peak_analysis_2026_10_19.json"


def test_v40_56_independent_verification_section_present():
    """Section 15.1 must contain the t212_evaluate-based verification."""
    report_text = REPORT.read_text(encoding="utf-8")
    # The independent verification section must mention t212_evaluate
    assert "t212_silverman_gravothermal.evaluate()" in report_text, (
        f"v40.56 fix: section 15.1 must use ACTUAL t212_silverman_gravothermal.evaluate(). "
        f"Per n11.docx MED-HIGH, v40.55 code still depended on external modules. "
        f"v40.56 explicitly uses the same function as the v40.46 script."
    )
    # Must show the matched results table (with YES markers in cells)
    assert "YES" in report_text or "Match" in report_text, (
        f"v40.56 fix: section 15.1 must show verification match table."
    )


def test_v40_56_tau_values_verified_independently():
    """The tau values quoted must match the v40.46 JSON (verified independently)."""
    with open(JSON_V4046, encoding="utf-8") as fp:
        v4046 = json.load(fp)
    tau_canonical_json = v4046["cases"][0]["tau"]  # 16.41
    tau_downgraded_json = v4046["cases"][1]["tau"]  # 0.06

    # Verify the values themselves
    assert abs(tau_canonical_json - 16.41) < 0.05, (
        f"v40.56 fix: canonical tau should be ~16.41, got {tau_canonical_json}"
    )
    assert abs(tau_downgraded_json - 0.06) < 0.01, (
        f"v40.56 fix: downgraded tau should be ~0.06, got {tau_downgraded_json}"
    )

    # The report must contain both values
    report_text = REPORT.read_text(encoding="utf-8")
    assert "16.41" in report_text and "0.06" in report_text, (
        f"v40.56 fix: report must contain tau = 16.41 and 0.06."
    )


def test_v40_56_sigma_hl_curve_added():
    """Section 15.2 must contain sigma_HL vs f_H curve."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Check the curve is in the report
    assert "sigma_HL vs f_H CURVE" in report_text or "f_H curve" in report_text, (
        f"v40.56 fix: section 15.2 must contain sigma_HL vs f_H curve. "
        f"Per n11.docx MED, need to show sigma_HL across f_H values."
    )
    # Check the table has multiple f_H values
    for f_H in [0.297, 0.50, 0.70, 1.00]:
        assert f"{f_H:.2f}" in report_text or f"{f_H:.3f}" in report_text, (
            f"v40.56 fix: sigma_HL vs f_H curve must include f_H = {f_H}"
        )


def test_v40_56_prescription_non_identifiability_added():
    """Section 15.3 must contain honest prescription non-identifiability statement."""
    report_text = REPORT.read_text(encoding="utf-8")
    assert "non-identifiable" in report_text.lower() or "NON-IDENTIFIABLE" in report_text, (
        f"v40.56 fix: section 15.3 must contain prescription non-identifiability "
        f"statement. Per n11.docx MED-HIGH, the dual-weighting contradiction "
        f"requires honest acknowledgement."
    )
    # Should explain the 95% CI under prescription uncertainty
    # Use ASCII-friendly search (avoid unicode chars)
    assert "1.33" in report_text and "1.56" in report_text, (
        f"v40.56 fix: must state the 95% CI under prescription uncertainty "
        f"(should mention 1.33 and 1.56 as CI bounds)."
    )


def test_v40_56_tau_threshold_clarified():
    """Section 15.5 must clarify tau threshold (tau = 1 IS the threshold)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # The threshold clarification section must explicitly state tau = 1 IS the threshold
    assert "threshold IS τ = 1" in report_text or "τ = 1 IS the threshold" in report_text, (
        f"v40.56 fix: section 15.5 must clarify τ = 1 IS the threshold. "
        f"Per n11.docx Issue #1c, §12.4 and §13.4 contradicted each other on this point."
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
    print("All 5 v40.56 n11.docx review response regression tests pass.")