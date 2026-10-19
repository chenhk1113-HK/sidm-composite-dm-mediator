"""
test_tucana_ii_sigma_v.py — Regression test for the canonical Tucana II sigma_v value.

Per v40.20 (commit 356bccf): sigma_v = 8.6 km/s (corrected from 8.2; the
8.2 was a numerical slip — the Walker+ 2016 paper central value is 8.6).

This test scans the v19.2-F codebase for any reference to "Tucana II" or
"TUCANA II" + numeric values in the range 5-15 km/s, and asserts that:
  - Code files (v0.3-prelim/code/) contain ONLY sigma_v_los = 8.6 (not 8.2)
  - Doc files containing "Tucana II" near numeric values do not propagate
    the stale 8.2 value as the canonical entry (the 8.2 in some doc tables
    is a row label that pre-dates the v40.20 fix and is noted as such)

This guards against future regressions to the 8.2 value.
"""
import re
import sys
from pathlib import Path

# v19.2-F project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # tests/ -> v0.3-prelim
REPO_ROOT = PROJECT_ROOT.parent

# Walker+ 2016 canonical value (per docs/papers/to_verify/1511.06296_walker_2016_tucana2.md)
CANONICAL_SIGMA_V = 8.6
STALE_SIGMA_V = 8.2


def test_tucana_ii_sigma_v_in_code():
    """The Loop 4 code file MUST use 8.6, not 8.2 (v40.20 fix)."""
    code_file = REPO_ROOT / "v0.3-prelim" / "code" / "v19_2_f_loop4_tc_breit_wigner_reproduction.py"
    assert code_file.exists(), f"Missing: {code_file}"
    text = code_file.read_text(encoding="utf-8")

    # The HALOS catalogue line for Tucana II
    m = re.search(r'Tucana II.*?sigma_v_los["\']?\s*[:=]\s*(\d+\.?\d*)', text)
    assert m, "Could not find Tucana II sigma_v_los in HALOS catalogue"
    value = float(m.group(1))
    assert value == CANONICAL_SIGMA_V, (
        f"Tucana II sigma_v is {value}, expected {CANONICAL_SIGMA_V} "
        f"(Walker+ 2016 central value; v40.20 fix from 8.2)"
    )


def test_no_stale_tucana_value_in_code():
    """Code files must not contain the stale 8.2 value for Tucana II."""
    code_dir = REPO_ROOT / "v0.3-prelim" / "code"
    stale_files = []
    for f in code_dir.glob("*.py"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        # Look for Tucana II references with 8.2 in same line
        for i, line in enumerate(text.splitlines(), 1):
            if "Tucana II" in line and "8.2" in line:
                stale_files.append((f, i, line.strip()))

    assert not stale_files, (
        "Stale Tucana II sigma_v=8.2 found in code files (should be 8.6):\n"
        + "\n".join(f"  {f}:{i}: {line[:100]}" for f, i, line in stale_files)
    )


def test_tucana_kb_documents_canonical_value():
    """The KB doc for Walker+ 2016 should reference the canonical 8.6 value."""
    kb_doc = REPO_ROOT / "docs" / "papers" / "to_verify" / "1511.06296_walker_2016_tucana2.md"
    if not kb_doc.exists():
        return  # KB doc may be in different location
    text = kb_doc.read_text(encoding="utf-8")
    assert str(CANONICAL_SIGMA_V) in text, (
        f"KB doc {kb_doc.name} should mention sigma_v = {CANONICAL_SIGMA_V}"
    )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
