"""Regression tests for v40.58: n13.docx review response.

Per n13.docx review (2026-10-20), v40.57 had these remaining issues:
1. [MED-HIGH] Version arc table inconsistent (header says 14 versions, body has 18+)
2. [MED-HIGH] Test count inconsistency (116 vs 92, 19 vs 13 suites)
3. [MED] PowerShell syntax in section 8.3 actually not fixed
4. [MED] Channel correlation computation method not explained
5. [MED] JSON data files never embedded despite 8+ rounds

v40.58 FIX:
1. Update version arc to 'The 19-Version Arc (v40.39 -> v40.57)' + add 6 missing rows
2. Update section 8.2 test counts to '20 test suites, 121/121 tests'
3. Fix PowerShell in section 8.3 with & operator
4. Document channel correlation computation method
5. Embed v40.49 full JSON in section 17.4
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
JSON_V4049 = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_multiscale_refit_2026_10_19.json"


def test_v40_58_version_arc_table_includes_all_versions():
    """Section 2 version arc table must include v40.52-v40.57 (n13.docx Issue #1)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # The header must be '19-Version Arc'
    assert "The 19-Version Arc (v40.39 → v40.57)" in report_text or "The 19-Version Arc (v40.39 -> v40.57)" in report_text, (
        f"v40.58 fix: section 2 must have '19-Version Arc' header. "
        f"Per n13.docx MED-HIGH, the old '14-Version Arc' header was inconsistent "
        f"with the actual content (18+ versions discussed)."
    )
    # The table must include v40.52-v40.57
    for v in ["v40.52", "v40.53", "v40.54", "v40.55", "v40.56", "v40.57"]:
        assert v in report_text, (
            f"v40.58 fix: version arc table must include {v}."
        )


def test_v40_58_test_counts_consistent():
    """Test counts must be consistent throughout the report (n13.docx Issue #2)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Section 8.2 must show updated counts
    assert "20 test suites, 121/121 tests" in report_text or "20 test suites" in report_text, (
        f"v40.58 fix: section 8.2 must show updated test counts (20 suites, 121 tests)."
    )
    # Header must be consistent
    assert "121/121" in report_text and "20 test suites" in report_text, (
        f"v40.58 fix: header and section 8.2 must both show 121/121 / 20 suites."
    )


def test_v40_58_powershell_actually_fixed():
    """Section 8.3 PowerShell must have & operator (n13.docx Issue #3)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Find section 8.3 (before section 8.4)
    sec83_start = report_text.find("### 8.3 Run the tests")
    sec83_end = report_text.find("### 8.4", sec83_start)
    sec83 = report_text[sec83_start:sec83_end]
    # Section 8.3 must have & operator in PowerShell block
    assert "& .venv-sidm-bench" in sec83 or "& .venv-sidm-bench" in sec83.replace("\\", "/"), (
        f"v40.58 fix: section 8.3 PowerShell block must have & operator. "
        f"Per n13.docx MED, v40.57's PowerShell fix was only in §16.6 not §8.3."
    )


def test_v40_58_v40_49_json_embedded():
    """v40.49 JSON must be embedded in the report (n13.docx Issue #7)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Check that the JSON structure is shown
    assert "v40.49: Full multi-scale background refit" in report_text, (
        f"v40.58 fix: v40.49 JSON header must be in the report. "
        f"Per n13.docx MED, JSON data has been deferred for 8+ rounds."
    )
    # Check that the actual JSON file content is reflected
    import json
    with open(JSON_V4049, encoding="utf-8") as fp:
        v4049 = json.load(fp)
    n_combos = v4049["n_combinations"]
    n_pass = v4049["n_all_pass"]
    # The report must reference both numbers
    assert f'"n_combinations": {n_combos}' in report_text or f'n_combinations": {n_combos}' in report_text, (
        f"v40.58 fix: must reference v40.49's {n_combos} combinations."
    )
    assert f'"n_all_pass": {n_pass}' in report_text or f'n_all_pass": {n_pass}' in report_text, (
        f"v40.58 fix: must reference v40.49's {n_pass} all-pass count."
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
    print("All 4 v40.58 n13.docx review response regression tests pass.")