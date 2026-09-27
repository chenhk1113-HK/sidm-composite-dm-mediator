"""
Tests for Phase 7e — unit-conversion audit of T87 LZ event rate formula.

These tests verify:
1. The phase7e script runs without errors
2. The N_T bug factor is correctly identified (~365x)
3. All Phase 7 N_pred values are off by a constant factor (~365x)
4. The corrected N_T formula gives the right magnitude
5. The kill verdicts are NOT changed by the bug fix
"""
from __future__ import annotations
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "code" / "phase7e_unit_conversion_audit.py"
RESULTS_PATH = REPO_ROOT / "data" / "results" / "phase7e_unit_conversion_audit.json"


def test_phase7e_script_exists():
    """Phase 7e script must exist at the expected location."""
    assert SCRIPT_PATH.is_file(), f"Missing script: {SCRIPT_PATH}"


def test_phase7e_results_json_exists():
    """Phase 7e results JSON must exist."""
    assert RESULTS_PATH.is_file(), f"Missing results: {RESULTS_PATH}"


def test_phase7e_results_schema():
    """The results JSON has the expected schema."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["phase"] == "7e"
    assert d["bug_found"] is True
    assert "bug_location" in d
    assert "bug_factor" in d
    assert "v07_MAP_audit" in d
    assert "v03_MAP_audit" in d
    assert "kill_verdicts_unchanged" in d


def test_phase7e_bug_factor_is_365():
    """The N_T bug factor should be exactly 365.25 (days per year) for 1 tonne-year exposure."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    # At 1 tonne-year exposure, the bug factor should be exactly 365.25 days/year
    n_t_correct = d["N_T_correct_for_1_ty"]
    n_t_buggy = d["N_T_buggy_for_1_ty"]
    ratio = n_t_buggy / n_t_correct
    assert abs(ratio - 365.25) < 0.01, f"Bug factor should be 365.25, got {ratio:.4f}"


def test_phase7e_v07_audit_bug_factor_consistent():
    """The bug factor in the audit JSON should be ~365 across entries.

    Note: this test compares the audit's stored buggy/corrected values
    (which were captured BEFORE the fix). After the fix, the actual
    ratio in production is 1.0 (no bug). This test verifies the AUDIT
    report's recorded bug factor is consistent.
    """
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    # Read the audit data; the JSON should have N_buggy and N_correct fields
    # that were captured before the fix
    ratios = []
    for r in d["v07_MAP_audit"]:
        if "ratio_buggy_over_correct" in r and math.isfinite(r["ratio_buggy_over_correct"]):
            ratios.append(r["ratio_buggy_over_correct"])
    assert len(ratios) >= 5
    # All ratios should be ~365 (within numerical precision)
    for r in ratios:
        assert 360 < r < 380, f"Bug factor should be ~365, got {r:.2f}"


def test_phase7e_v03_audit_bug_factor_consistent():
    """The bug factor for v0.3-prelim MAP audit entries should be ~365."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    ratios = []
    for r in d["v03_MAP_audit"]:
        if "ratio_buggy_over_correct" in r and math.isfinite(r["ratio_buggy_over_correct"]):
            ratios.append(r["ratio_buggy_over_correct"])
    assert len(ratios) >= 3
    for r in ratios:
        assert 360 < r < 380, f"Bug factor should be ~365, got {r:.2f}"


def test_phase7e_kill_verdicts_unchanged():
    """Even with the bug fix, the Phase 7 kill verdicts should remain valid.

    All N_pred values are 60+ orders of magnitude below 1. The 365x bug factor
    does not change this qualitative verdict.
    """
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    # The corrected N_pred values should still be << 1 (so kill still valid)
    for r in d["v07_MAP_audit"]:
        if math.isfinite(r["N_correct"]) and r["N_correct"] > 0:
            assert r["N_correct"] < 0.1, (
                f"Corrected N_pred at delta={r['delta_keV']} should be < 0.1 "
                f"(kill verdict), got {r['N_correct']:.3e}"
            )
    for r in d["v03_MAP_audit"]:
        if math.isfinite(r["N_correct"]) and r["N_correct"] > 0:
            assert r["N_correct"] < 0.1, (
                f"Corrected N_pred at delta={r['delta_keV']} should be < 0.1 "
                f"(kill verdict), got {r['N_correct']:.3e}"
            )


def test_phase7e_correct_N_T_magnitude():
    """The CORRECT N_T for 1 tonne-year should be ~4.6e27 (1 tonne of Xe in nuclei)."""
    # Hand-computed: 1000 kg * 1000 g/kg / 131 g/mol * 6.022e23 = 4.597e27
    expected = 1000.0 * 1000.0 / 131.0 * 6.022e23
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    n_t_correct = d["N_T_correct_for_1_ty"]
    assert abs(n_t_correct - expected) / expected < 0.01, (
        f"N_T correct should be ~{expected:.4e}, got {n_t_correct:.4e}"
    )


def test_phase7e_correct_N_pred_at_v07_delta297():
    """Corrected N_pred at v0.7 MAP, delta=297 keV should be ~1.3e-75."""
    # (T87 buggy says 4.81e-73; corrected should be ~1.29e-75)
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    v07_audit = d["v07_MAP_audit"]
    delta297_entry = next((r for r in v07_audit if r["delta_keV"] == 297), None)
    assert delta297_entry is not None
    n_correct = delta297_entry["N_correct"]
    # Should be ~4.81e-73 / 372.6 = ~1.29e-75
    assert 1e-76 < n_correct < 1e-74, f"Expected ~1.3e-75, got {n_correct:.3e}"


def test_phase7e_runs_as_script():
    """The phase7e script must be runnable as `python phase7e_...py` without error."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Script failed: {result.stderr[:500]}"
    # Output should mention "FINDING" or "BUG"
    assert "BUG" in result.stdout.upper() or "FINDING" in result.stdout.upper()
