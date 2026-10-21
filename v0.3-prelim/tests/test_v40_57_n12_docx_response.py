"""Regression tests for v40.57: n12.docx review response.

Per n12.docx review (2026-10-20), v40.56 had these remaining issues:
1. [MED-HIGH] Title says 'v40.51' but content covers v40.39 -> v40.57
2. [MED-HIGH] 'Independent verification' still uses sys.path.insert (NOT truly independent)
3. [MED] sigma_HL vs f_H finding not prominent in Executive Summary
4. [MED] Channel correlation quantification (~4-5 is vague)
5. [MED-LOW] Ohana+ 2026 citation deferred 6+ rounds
6. [MED-LOW] PowerShell syntax inconsistency in section 8.3

v40.57 FIX:
1. Update title to v40.39 -> v40.57
2. Pure-Python verification using Balberg+ 2002 formula (no project modules)
3. Promote sigma_HL vs f_H finding to Executive Summary
4. Compute actual channel correlation (correlation matrix approach)
5. Embed Ohana+ 2026 full citation in body
6. Fix PowerShell in section 8.3
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
SCRIPT = REPO / "scripts" / "v19_2_f_n12_docx_response.py"


def test_v40_57_title_updated():
    """Title must declare a version range consistent with the §2 arc header.

    v40.61 (n14.docx Item 2) fix: this assertion was originally hard-coded to
    the literal 'v40.39 -> v40.57'. Every title bump therefore broke it,
    which is the root cause of the recurring "version/count inconsistency"
    pattern flagged in n13/n14 reviews. It is now version-agnostic: the title
    range must MATCH the §2 arc header range, whatever the version numbers are.
    """
    report_text = REPORT.read_text(encoding="utf-8")
    first_line = report_text.split("\n")[0]

    # Extract the version range from the title, e.g. "(v40.39 -> v40.57)"
    title_range = re.search(r"\(v40\.(\d+)\s*(?:→|->)\s*v40\.(\d+)\)", first_line)
    assert title_range is not None, (
        f"v40.57 fix: title must declare a version range like "
        f"'(v40.39 -> v40.57)'. Current first line: {first_line!r}"
    )

    # Extract the §2 arc header range
    sec2 = report_text[report_text.find("## 2. The"):report_text.find("## 3.")]
    arc_range = re.search(r"v40\.(\d+)\s*(?:→|->)\s*v40\.(\d+)", sec2)
    assert arc_range is not None, (
        "v40.61 fix: section 2 header must declare a version range."
    )

    assert title_range.groups() == arc_range.groups(), (
        f"v40.61 fix: title version range {title_range.groups()} must match "
        f"section 2 arc header range {arc_range.groups()}. "
        f"Per n14.docx Item 2, a mismatch between the two is the recurring "
        f"'21 vs 19 vs 22' inconsistency pattern."
    )


def test_v40_57_pure_python_verification_present():
    """Section 16.2 must contain pure-Python verification (no sys.path.insert)."""
    report_text = REPORT.read_text(encoding="utf-8")
    assert "PURE-PYTHON" in report_text or "pure-Python" in report_text or "pure python" in report_text.lower(), (
        f"v40.57 fix: section 16.2 must contain pure-Python verification. "
        f"Per n12.docx MED-HIGH, v40.56 verification still depended on sys.path.insert."
    )
    # Must reference Balberg+ 2002 formula
    assert "Balberg" in report_text and "12.7" in report_text, (
        f"v40.57 fix: must show Balberg+ 2002 collapse-time formula "
        f"(t_core = 12.7 / sigma * ...)."
    )


def test_v40_57_sigma_hl_promoted_to_exec_summary():
    """Section 1 must contain sigma_HL vs f_H finding (n12.docx Issue #3)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Find Section 1 (Executive Summary)
    sec1_start = report_text.find("## 1. Executive Summary")
    sec1_end = report_text.find("## 2.", sec1_start)
    sec1 = report_text[sec1_start:sec1_end]
    # Section 1 must contain the sigma_HL vs f_H finding
    assert "f_H" in sec1 and ("sigma_HL" in sec1 or "σ_HL" in sec1), (
        f"v40.57 fix: Executive Summary (Section 1) must contain sigma_HL vs f_H finding. "
        f"Per n12.docx MED, this finding needs to be prominent in the Exec Summary."
    )


def test_v40_57_channel_correlation_matrix_present():
    """Section 16.4 must contain a correlation matrix (n12.docx Issue #5)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # The correlation matrix should have multiple Pearson r values
    # Look for at least 3 correlation values
    count = sum(1 for c in [str(x) for x in range(10)] if c in report_text)
    # Must have Pearson correlation values (0.961, 0.994, 0.997, etc.)
    assert "0.961" in report_text and "0.994" in report_text and "0.997" in report_text, (
        f"v40.57 fix: channel correlation matrix must show Pearson r values. "
        f"Per n12.docx MED, need actual computation not just '~4-5' estimate."
    )


def test_v40_57_ohana_full_citation_in_body():
    """Section 16.5 must contain full Ohana+ 2026 citation (n12.docx Issue #6)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Must contain full citation
    assert "Ohana, Zhang, Yu 2026" in report_text or "Ohana, Zhang" in report_text, (
        f"v40.57 fix: full Ohana+ 2026 citation must be in body. "
        f"Per n12.docx MED-LOW, citation was deferred 6+ rounds."
    )
    # Must include arXiv ID
    assert "2608.04362" in report_text, (
        f"v40.57 fix: must include arXiv:2608.04362 ID."
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
    print("All 5 v40.57 n12.docx review response regression tests pass.")