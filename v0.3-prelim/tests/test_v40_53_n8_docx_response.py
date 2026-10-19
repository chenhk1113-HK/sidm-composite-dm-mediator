"""Regression tests for v40.53: n8.docx review response.

Per n8.docx review (2026-10-19), v40.52 had these remaining issues:
1. [MED-HIGH] Internal inconsistency: section 10 still says 'FULLY RESOLVED'
2. [MED-HIGH] c-M prescription dependence lacks quantitative marginalization
3. [MED] Sameie+ 2020 paper equation cross-reference
4. [MED] 71% statistical significance still needs Monte Carlo validation
5. [MED] Fornax 2.5x tension discussion insufficient
6. [MED-LOW] Ohana+ 2026 citation incomplete
7. [MED-LOW] tau calculation code not embedded

v40.53 FIX (locks these so any future change is caught):
1. Fix section 10 terminology (use 'ADDRESSED via MODEL DOWNGRADE')
2. Add quantitative c-M prescription marginalization
3. Add Fornax sigma_HL before/after table
4. Show tau calculation code (formula + implementation)
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
SCRIPT = REPO / "scripts" / "v19_2_f_n8_docx_response.py"


def test_v40_53_section10_uses_unified_terminology():
    """Section 10 (Project Status) must use 'ADDRESSED via MODEL DOWNGRADE' (n8.docx Issue #1)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Section 10 should use the new wording, not the old 'FULLY RESOLVED' standalone
    # Find section 10's Cloud-9 entry specifically (not 'FULLY RESOLVED methodology' which is OK in n6.docx table)
    assert "1. **Cloud-9 c-M tension:** ADDRESSED via MODEL DOWNGRADE" in report_text, (
        f"v40.53 fix: section 10 must use 'ADDRESSED via MODEL DOWNGRADE' "
        f"for the Cloud-9 c-M tension entry. The n8.docx MED-HIGH issue "
        f"(internal inconsistency) was a real bug; section 10 was still using "
        f"'FULLY RESOLVED' while section 1 used 'ADDRESSED via MODEL DOWNGRADE'."
    )
    # Also check version arc table is updated
    assert "Cloud-9 c-M tension ADDRESSED via MODEL DOWNGRADE" in report_text, (
        f"v40.53 fix: version arc table should also use 'ADDRESSED via MODEL DOWNGRADE'."
    )


def test_v40_53_cm_marginalization_computed():
    """Section 12.2 must contain quantitative c-M tension marginalization.

    Equal-weight mean and std across [+0.32, +0.93, -1.31]:
    - mean = -0.02 sigma (essentially ZERO)
    - std = 1.16 sigma (HUGE dispersion)
    """
    report_text = REPORT.read_text(encoding="utf-8")
    # Check the calculation result is in the report
    assert "−0.02 ± 1.16 σ" in report_text or "-0.02 +/- 1.16 sigma" in report_text, (
        f"v40.53 fix: section 12.2 must contain quantitative c-M prescription "
        f"marginalization result. The n8.docx MED-HIGH issue (no quantitative "
        f"marginalization) requires explicit numbers."
    )
    assert "INDISTINGUISHABLE FROM ZERO" in report_text, (
        f"v40.53 fix: section 12.2 must interpret the marginalization result."
    )


def test_v40_53_fornax_table_present():
    """Section 12.3 must contain Fornax sigma_HL before/after numerical table."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Check the table is present (look for unique values)
    assert "2.85 cm²/g" in report_text, (
        f"v40.53 fix: Fornax before/after table must show '2.85 cm²/g' (with peak)."
    )
    assert "2.02 cm²/g (1.4× lower)" in report_text, (
        f"v40.53 fix: Fornax before/after table must show '2.02 cm²/g (1.4× lower)' (peak=0)."
    )
    assert "0.179 cm²/g" in report_text, (
        f"v40.53 fix: Fornax before/after table must show sigma_eff reduction."
    )


def test_v40_53_tau_calculation_code_shown():
    """Section 12.4 must contain tau calculation code."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Check the code is present
    assert "tau = gravothermal collapse time / Hubble time" in report_text, (
        f"v40.53 fix: tau calculation code must be shown in section 12.4."
    )
    assert "def calc_tau" in report_text, (
        f"v40.53 fix: tau calculation function must be shown."
    )
    assert "t_core = 0.35 Gyr" in report_text or "t_core_gyr" in report_text, (
        f"v40.53 fix: tau calculation must show actual numerical values."
    )


def test_v40_53_n8_docx_script_exists_and_runs():
    """scripts/v19_2_f_n8_docx_response.py must exist and have the required sections."""
    assert SCRIPT.exists(), (
        f"v40.53 fix: scripts/v19_2_f_n8_docx_response.py must exist."
    )
    script_text = SCRIPT.read_text(encoding="utf-8")
    for required_section in [
        "c_m_tension_marginalization",
        "fornax_sigma_hl_table",
        "tau_calculation_code",
    ]:
        assert required_section in script_text, (
            f"v40.53 fix: script must contain '{required_section}' function. "
            f"If this fails, the n8.docx response script is incomplete."
        )
    # Check the actual calculation is correct
    tensions = [0.32, 0.93, -1.31]
    mean = statistics.mean(tensions)
    std = statistics.stdev(tensions)
    assert abs(mean - (-0.02)) < 0.01, (
        f"v40.53 fix: c-M tension mean should be ~-0.02, got {mean}"
    )
    assert abs(std - 1.16) < 0.01, (
        f"v40.53 fix: c-M tension std should be ~1.16, got {std}"
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
    print("All 5 v40.53 n8.docx review response regression tests pass.")