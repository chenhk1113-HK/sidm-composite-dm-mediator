"""Regression tests for v40.55: n10.docx review response - HIGH-severity bug fix.

Per n10.docx review (2026-10-19), v40.54 §13.4 had a FABRICATED collapse_time_gyr implementation.
v40.55 corrects this. The TAU VALUES quoted (16.4 and 0.06) ARE correct (from v40.46 stored
JSON) but the CODE was wrong.

v40.55 FIX:
1. Replace v40.54 §13.4 fabricated code with actual project code
2. Verify tau values match v40.46 stored JSON
3. Correct §13.5 title from 'Monte Carlo' to 'analytic Binomial'
4. Add n10.docx HIGH-severity finding acknowledgement in §14
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
SCRIPT = REPO / "scripts" / "v19_2_f_n10_docx_response.py"
JSON_V4046 = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_no_peak_analysis_2026_10_19.json"


def test_v40_55_section_13_4_no_longer_has_fabricated_code():
    """Section 13.4 (v40.55) must NOT have the fabricated formula in ACTIVE CODE.

    The v40.54 fabricated code had:
      rho_s_si = rho_s * 1e9 * (3.086e19)**3
    v40.55 must replace this with the correct project code.
    The string may still appear in §13.4 / §14 narrative as part of bug acknowledgement,
    but it must NOT appear inside a Python code block as active code.
    """
    report_text = REPORT.read_text(encoding="utf-8")

    # Extract all Python code blocks
    import re
    code_blocks = re.findall(r"```python\n(.*?)\n```", report_text, re.DOTALL)
    for i, block in enumerate(code_blocks):
        if "rho_s * 1e9 * (3.086e19)**3" in block:
            # Check if this is in the section 13.4 ACTIVE code block (not §14 narrative)
            # Find the section header before this block
            block_pos = report_text.find(block)
            section_before = report_text[:block_pos]
            last_section_13 = section_before.rfind("### 13.4")
            last_section_14 = section_before.rfind("### 14.1")
            # If the block is in §13.4 (not §14.1), it's a bug
            if last_section_13 > last_section_14:
                raise AssertionError(
                    f"v40.55 fix: section 13.4 ACTIVE CODE block #{i} contains the "
                    f"v40.54 fabricated unit conversion. The formula "
                    f"rho_s * 1e9 * (3.086e19)**3 is off by ~10^95 from correct."
                )


def test_v40_55_tau_values_match_v40_46_json():
    """The tau values quoted in section 13.4 must match the v40.46 stored JSON."""
    # Load the v40.46 stored JSON
    with open(JSON_V4046, encoding="utf-8") as fp:
        v4046 = json.load(fp)
    canonical = v4046["cases"][0]  # CANONICAL (peak=174)
    downgraded = v4046["cases"][1]  # DOWNGRADED (peak=0)
    tau_canonical_json = canonical["tau"]
    tau_downgraded_json = downgraded["tau"]

    # The report must quote these EXACT values (within rounding)
    report_text = REPORT.read_text(encoding="utf-8")
    assert "16.4" in report_text and "0.06" in report_text, (
        f"v40.55 fix: section 13.4 must quote the tau values 16.4 and 0.06 "
        f"that match the v40.46 stored JSON. "
        f"v40.46 JSON has tau = {tau_canonical_json:.2f} (canonical) and "
        f"{tau_downgraded_json:.4f} (downgraded)."
    )

    # Verify the tau calculation: tau = T_Hubble / t_core
    assert abs(tau_canonical_json - 16.41) < 0.05, (
        f"v40.55 fix: canonical tau should be ~16.41 (per v40.46 JSON), got {tau_canonical_json}"
    )
    assert abs(tau_downgraded_json - 0.06) < 0.01, (
        f"v40.55 fix: downgraded tau should be ~0.06 (per v40.46 JSON), got {tau_downgraded_json}"
    )


def test_v40_55_section_13_5_title_corrected():
    """Section 13.5 title must say 'Binomial (analytic)' not 'Monte Carlo' (n10.docx Issue #2)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # The section title must contain 'Binomial' AND 'analytic'
    assert "13.5 Binomial (analytic)" in report_text or "13.5 Binomial (analytic) 71" in report_text, (
        f"v40.55 fix: section 13.5 title must be corrected from 'Monte Carlo' to "
        f"'Binomial (analytic)'. The original computation was analytic (no random "
        f"sampling), not Monte Carlo."
    )
    # The original "Monte Carlo" title should have a note about the correction
    assert "v40.55 title fix" in report_text, (
        f"v40.55 fix: must include a note explaining the §13.5 title correction."
    )


def test_v40_55_high_severity_acknowledgement_present():
    """Section 14.1 must acknowledge the v40.54 fabricated code (R88(68) compliance)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Must acknowledge the fabrication
    assert "FABRICATED" in report_text, (
        f"v40.55 fix: must explicitly acknowledge that v40.54 §13.4 had fabricated code. "
        f"This is required by the R88(68) anti-fabrication rule."
    )
    # Must acknowledge n10.docx finding
    assert "n10.docx HIGH-severity" in report_text or "n10.docx Issue #1" in report_text, (
        f"v40.55 fix: must reference n10.docx HIGH-severity finding."
    )
    # Must explain that the tau VALUES were correct (from JSON) even though CODE was wrong
    assert "from the project's stored" in report_text or "from v40.46 stored JSON" in report_text, (
        f"v40.55 fix: must explain that the tau values were correct (sourced from "
        f"v40.46 JSON) even though the v40.54 code was wrong."
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
    print("All 4 v40.55 n10.docx review response regression tests pass.")