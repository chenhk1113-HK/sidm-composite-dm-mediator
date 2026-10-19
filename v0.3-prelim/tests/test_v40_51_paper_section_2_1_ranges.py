"""Regression tests for v40.51: parameter ranges in paper section 2.1.

Per n6.docx review (2026-10-19): v40.50 report had hand-written
parameter ranges that did NOT match the actual v40.49 passing
combinations. v40.51 fix: ranges are computed from data via f-string
interpolation in scripts/v19_2_f_paper_section_2_1_update.py.

This test locks the correct ranges (from min/max of the 10 v40.49
passing combinations) so any future change to the multi-scale refit
that affects these numbers FAILS the test.

Correct ranges (from v40.49 data):
- sigma_0: [0.010, 0.052]
- a:       [1.50, 2.50]
- v_ref:   [50, 150]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_multiscale_refit_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_paper_section_2_1_update.py"


def test_v40_51_v40_49_results_present():
    """Lock file must exist and have the v40.49 structure."""
    assert RESULTS.exists(), f"Missing v40.49 results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "n_all_pass" in data
    assert "results" in data


def test_v40_51_sigma_0_range_correct():
    """sigma_0 range must be [0.010, 0.052] (NOT the v40.50 wrong [0.010, 0.030])."""
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    passing = [r["combo"] for r in data["results"] if r["all_pass"]]
    sigma_0_min = min(c["sigma_0"] for c in passing)
    sigma_0_max = max(c["sigma_0"] for c in passing)
    assert abs(sigma_0_min - 0.010) < 1e-6, (
        f"sigma_0_min = {sigma_0_min}, expected 0.010. "
        f"v40.51 FIX: range must be [0.010, 0.052], NOT the wrong v40.50 [0.010, 0.030]."
    )
    assert abs(sigma_0_max - 0.052) < 1e-6, (
        f"sigma_0_max = {sigma_0_max}, expected 0.052 (Phase 44's sigma_0). "
        f"v40.51 FIX: this confirms Phase 44's sigma_0 is WITHIN the passing region, "
        f"NOT 'OUTSIDE' as v40.50 erroneously claimed."
    )


def test_v40_51_a_range_correct():
    """a range must be [1.50, 2.50] (NOT the v40.50 wrong [1.50, 1.93])."""
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    passing = [r["combo"] for r in data["results"] if r["all_pass"]]
    a_min = min(c["a_slope"] for c in passing)
    a_max = max(c["a_slope"] for c in passing)
    assert abs(a_min - 1.50) < 1e-6, (
        f"a_min = {a_min}, expected 1.50. "
        f"v40.51 FIX: range must be [1.50, 2.50], NOT the wrong v40.50 [1.50, 1.93]."
    )
    assert abs(a_max - 2.50) < 1e-6, (
        f"a_max = {a_max}, expected 2.50. "
        f"v40.51 FIX: the 10/14 passing combos include a=2.50 (sigma_0=0.010, a=2.50, v_ref=50)."
    )


def test_v40_51_v_ref_range_correct():
    """v_ref range must be [50, 150] (NOT the v40.50 wrong [50, 100])."""
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    passing = [r["combo"] for r in data["results"] if r["all_pass"]]
    v_ref_min = min(c["v_ref"] for c in passing)
    v_ref_max = max(c["v_ref"] for c in passing)
    assert abs(v_ref_min - 50.0) < 1e-6, (
        f"v_ref_min = {v_ref_min}, expected 50.0."
    )
    assert abs(v_ref_max - 150.0) < 1e-6, (
        f"v_ref_max = {v_ref_max}, expected 150.0. "
        f"v40.51 FIX: the 10/14 passing combos include v_ref=150 (sigma_0=0.010, a=1.50, v_ref=150)."
    )


def test_v40_51_script_uses_fstring():
    """The v40.51 script must use f-string interpolation, not hardcoded ranges.

    Per n6.docx review, the v40.50 bug was hardcoded ranges in a heredoc.
    v40.51 fix: ranges are computed from data via min/max of passing combos.
    """
    script_text = SCRIPT.read_text(encoding="utf-8")
    # Check that the script uses f-string interpolation for sigma_0_range
    assert "sigma_0_range[0]" in script_text, (
        f"v40.51 fix: script should use sigma_0_range[0] (computed) NOT hardcoded [0.010]."
    )
    assert "sigma_0_range[1]" in script_text, (
        f"v40.51 fix: script should use sigma_0_range[1] (computed) NOT hardcoded [0.030]."
    )
    # Check that the WRONG v40.50 hardcoded values are NOT in the heredoc
    assert "∈ [0.010, 0.030] cm²/g" not in script_text, (
        f"v40.51 fix: the wrong v40.50 range [0.010, 0.030] should be replaced."
    )
    assert "is OUTSIDE the passing region" not in script_text, (
        f"v40.51 fix: the wrong v40.50 claim 'Phase 44 is OUTSIDE' should be replaced "
        f"with 'IS WITHIN' (Phase 44's sigma_0=0.052 IS in the passing region)."
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
    print("All 5 v40.51 parameter range regression tests pass.")
