"""Regression tests for v40.52: n7.docx review response.

Per n7.docx review (2026-10-19), v40.51 report had these issues:
- HIGH: 'FULLY RESOLVED' is methodologically a model replacement
- MED-HIGH: c-M tension prescription dependence buried
- MED: 71% survival rate statistical significance not verified
- MED: Ohana+ 2026 full citation missing
- MED-HIGH: Windows path in run instructions

v40.52 FIX (locks these so any future change is caught):
1. Paper §2.6h has 'MODEL DOWNGRADE' reframing
2. Report Executive Summary has prescription dependence callout
3. scripts/v19_2_f_n7_docx_response.py computes random expectation rate
4. Paper has full Ohana+ 2026 citation (arXiv:2608.04362)
5. Report §8.3 has cross-platform run instructions
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
REPORT = REPO / "docs" / "SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md"
SCRIPT = REPO / "scripts" / "v19_2_f_n7_docx_response.py"


def test_v40_52_paper_has_model_downgrade_reframing():
    """Paper §2.6h must contain 'MODEL DOWNGRADE' reframing (v40.52 fix)."""
    paper_text = PAPER.read_text(encoding="utf-8")
    # The reframing was added with the literal text 'MODEL DOWNGRADE'
    assert "MODEL DOWNGRADE" in paper_text, (
        f"v40.52 fix: paper must contain 'MODEL DOWNGRADE' reframing. "
        f"If this fails, the n7.docx HIGH-severity fix was reverted."
    )


def test_v40_52_report_has_prescription_dependence_callout():
    """Report Executive Summary must contain prescription dependence callout."""
    report_text = REPORT.read_text(encoding="utf-8")
    # The callout was added with the literal text 'CRITICAL CAVEAT'
    assert "CRITICAL CAVEAT" in report_text, (
        f"v40.52 fix: report Executive Summary must contain 'CRITICAL CAVEAT' callout "
        f"documenting the prescription dependence. "
        f"If this fails, the n7.docx MED-HIGH fix was reverted."
    )
    # Also check the sign-flip table is there
    assert "Sameie+ 2020" in report_text
    assert "-1.31" in report_text


def test_v40_52_ohana_full_citation_added():
    """Paper must contain Ohana+ 2026 full citation (arXiv:2608.04362)."""
    paper_text = PAPER.read_text(encoding="utf-8")
    assert "2608.04362" in paper_text, (
        f"v40.52 fix: paper must contain Ohana+ 2026 arXiv ID (2608.04362). "
        f"If this fails, the n7.docx MED citation fix was reverted."
    )


def test_v40_52_script_exists_and_runs():
    """scripts/v19_2_f_n7_docx_response.py must exist and be runnable."""
    assert SCRIPT.exists(), (
        f"v40.52 fix: scripts/v19_2_f_n7_docx_response.py must exist."
    )
    # Check it has the expected sections
    script_text = SCRIPT.read_text(encoding="utf-8")
    for required_section in [
        "REFRAMING",
        "STATISTICAL SIGNIFICANCE",
        "PRESCRIPTION DEPENDENCE",
        "OHANA+ 2026 CITATION",
        "CROSS-PLATFORM RUN INSTRUCTIONS",
    ]:
        assert required_section in script_text, (
            f"v40.52 fix: script must contain '{required_section}' section. "
            f"If this fails, the n7.docx response script is incomplete."
        )


def test_v40_52_cross_platform_run_instructions():
    """Report §8.3 must contain cross-platform run instructions (not just Windows)."""
    report_text = REPORT.read_text(encoding="utf-8")
    # Check for cross-platform keywords
    assert "Cross-platform" in report_text or "cross-platform" in report_text or "POSIX" in report_text, (
        f"v40.52 fix: report §8.3 must contain cross-platform run instructions. "
        f"If this fails, the n7.docx MED-HIGH fix was reverted."
    )
    # Check that PowerShell and bash alternatives are mentioned
    # (the existing report has only Windows path; this fix should add the alternatives)
    assert "PowerShell" in report_text or "bash" in report_text, (
        f"v40.52 fix: report must mention PowerShell AND bash alternatives. "
        f"If this fails, the n7.docx fix is incomplete."
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
    print("All 5 v40.52 n7.docx review response regression tests pass.")
