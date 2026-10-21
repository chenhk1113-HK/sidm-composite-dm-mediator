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

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
JSON_V4049 = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_multiscale_refit_2026_10_19.json"


def test_v40_58_version_arc_table_includes_all_versions():
    """Section 2 version arc table must be internally consistent (n13.docx Issue #1).

    v40.61 (n14.docx Item 2) fix: the assertion was hard-coded to the literal
    'The 19-Version Arc (v40.39 -> v40.57)' and to a frozen version list
    v40.52-v40.57. Every arc bump broke it. It is now version-agnostic:
      (a) the §2 header must declare a version range,
      (b) the arc TABLE must contain a row for every version in that range,
      (c) the header's stated version count must equal the number of
          SEQUENTIAL version numbers in that range.
    """
    report_text = REPORT.read_text(encoding="utf-8")
    sec2 = report_text[report_text.find("## 2. The"):report_text.find("## 3.")]

    # (a) the header must declare a range
    arc_range = re.search(r"v40\.(\d+)\s*(?:→|->)\s*v40\.(\d+)", sec2)
    assert arc_range is not None, (
        "v40.61 fix: section 2 header must declare a version range "
        "like 'The 21-Version Arc (v40.39 -> v40.59)'."
    )
    lo, hi = int(arc_range.group(1)), int(arc_range.group(2))
    assert lo <= hi, f"v40.61 fix: version range {lo}..{hi} is inverted."

    # (b) every sequential version in the range must have a table row
    for n in range(lo, hi + 1):
        assert f"v40.{n}" in sec2, (
            f"v40.61 fix: version arc table must include v40.{n}. "
            f"Range declared in header: v40.{lo}..v40.{hi}."
        )

    # (c) the header's stated count must equal the sequential range length
    n_sequential = hi - lo + 1
    count_match = re.search(r"The (\d+)-Version Arc", sec2)
    assert count_match is not None, (
        "v40.61 fix: section 2 header must state the version count, "
        "e.g. 'The 21-Version Arc'."
    )
    assert int(count_match.group(1)) == n_sequential, (
        f"v40.61 fix: header says '{count_match.group(1)}-Version Arc' but the "
        f"declared range v40.{lo}..v40.{hi} spans {n_sequential} sequential "
        f"versions. Per n14.docx Item 2, these must agree."
    )


def test_v40_58_test_counts_consistent():
    """Header test count and §8.2 test count must agree (n13.docx Issue #2).

    v40.61 (n14.docx Item 2) fix: the original assertion hard-coded
    '20 test suites, 121/121 tests' and matched only because that string
    still appeared in the HISTORICAL §17.2 text — a false pass. It is now
    version-agnostic: the header's passed-count and §8.2's passed-count must
    be the SAME number, and both must appear in §8.3's expected-output block.
    """
    report_text = REPORT.read_text(encoding="utf-8")

    # Header count (line 10 area): 'Test count: N passed, ...'
    header = re.search(r"\*\*Test count:\*\* (\d+) passed", report_text)
    assert header is not None, (
        "v40.61 fix: report header must declare a '**Test count:** N passed' value."
    )
    n_header = int(header.group(1))

    # Section 8.2 must state the same number
    sec82 = report_text[report_text.find("### 8.2"):report_text.find("### 8.3")]
    sec82 = re.search(r"(\d+) passed", sec82)
    assert sec82 is not None, (
        "v40.61 fix: section 8.2 must state a passed count."
    )
    assert int(sec82.group(1)) == n_header, (
        f"v40.61 fix: header says {n_header} passed but section 8.2 says "
        f"{sec82.group(1)}. Per n14.docx Item 2 these must agree."
    )

    # Section 8.3's expected-output fenced block must show the same number.
    # Anchored on the FULL pytest summary line (N passed, M skipped, ...) so a
    # stray prose mention of the number cannot satisfy the check.
    sec83 = report_text[report_text.find("### 8.3"):report_text.find("### 8.4")]
    summary_line = re.search(
        rf"^{n_header} passed, \d+ skipped, \d+ deselected", sec83, re.MULTILINE
    )
    assert summary_line is not None, (
        f"v40.61 fix: section 8.3 must contain a fenced pytest summary line "
        f"starting '{n_header} passed, <N> skipped, <N> deselected'. "
        f"Per n14.docx Item 3, the stale '121 passed' contradicted the header."
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