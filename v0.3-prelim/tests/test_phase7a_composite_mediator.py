"""
Tests for Phase 7a — composite-mediator LZ forward prediction at v0.3-prelim MAP.

These tests verify:
1. The phase7a script runs without errors
2. The kill criterion is TRIGGERED (composite-mediator at v0.3-prelim MAP
   cannot produce the LZ event)
3. The v0.3-prelim MAP operating point gives a N_predicted that is
   *WORSE* (smaller) than v0.7 MAP, by the ε² scaling ratio
4. The JSON output has the expected schema
"""
from __future__ import annotations
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "code" / "phase7a_composite_mediator_v03_map.py"
RESULTS_PATH = REPO_ROOT / "data" / "results" / "phase7a_composite_mediator_v03_map.json"


def test_phase7a_script_exists():
    """The Phase 7a script must exist at the expected location."""
    assert SCRIPT_PATH.is_file(), f"Missing script: {SCRIPT_PATH}"


def test_phase7a_results_json_exists():
    """The Phase 7a results JSON must exist (produced by `python phase7a_...`)."""
    assert RESULTS_PATH.is_file(), f"Missing results: {RESULTS_PATH}"


def test_phase7a_results_schema():
    """The results JSON has the expected schema (verifies structure of Phase 7a output)."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    # Top-level keys
    assert d["phase"] == "7a"
    assert "date" in d
    assert "v03_MAP" in d
    assert "composite_inputs" in d
    assert "sweep_results" in d
    assert "kill_triggered" in d
    assert "decision" in d
    # v0.3-prelim MAP inputs
    assert d["v03_MAP"]["sigma_m_0"] == pytest.approx(0.720, rel=1e-3)
    assert d["v03_MAP"]["a"] == pytest.approx(1.31, rel=1e-3)
    assert d["v03_MAP"]["log_epsilon"] == pytest.approx(-56.113, abs=0.01)
    # Sweep results structure
    assert len(d["sweep_results"]) > 0
    for r in d["sweep_results"]:
        assert "delta_keV" in r
        assert "form_factor_ansatz" in r
        assert "sigma_inel_at_target_cm2" in r
        assert "N_predicted" in r
        assert "verdict" in r


def test_phase7a_kill_triggered():
    """The composite-mediator sub-task at v0.3-prelim MAP MUST trigger the kill criterion.

    Per roadmap §Phase 7: 'No mediator class can produce LZ event at σ_DM-nuc ~10^-43 cm²
    while fitting multi-channel data at v0.3-prelim MAP.' Action: KILL.

    The composite-mediator case (T87-style) must produce N_pred ≪ 1.
    """
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["kill_triggered"] is True
    # The maximum N_predicted across the sweep must be ≪ 1
    max_N = d["max_N_predicted"]
    assert max_N < 0.1, f"Kill criterion should fire (N_pred < 0.1), got max_N = {max_N}"


def test_phase7a_worse_than_v07_map():
    """v0.3-prelim MAP N_predicted must be SMALLER than v0.7 MAP N_predicted.

    Reason: v0.3-prelim MAP has ε ≈ 7.7e-57, v0.7 MAP has ε ≈ 1.12e-37.
    Since σ_DM-nuc ∝ ε² and N_events ∝ σ, the ratio is:
        (ε_v03 / ε_v07)² ≈ (7.7e-57 / 1.12e-37)² ≈ 4.7e-39

    So v0.3-prelim MAP predicts ~10⁻³⁹× FEWER events than v0.7 MAP.
    """
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    v03_N = d["comparison_to_v07"]["v03_N_predicted_at_delta297_gaussian"]
    v07_N = d["comparison_to_v07"]["v07_N_predicted_at_delta297_gaussian"]
    ratio = v03_N / v07_N
    # Expected ratio ≈ (ε_v03/ε_v07)² ≈ 4.7e-39
    # We allow a generous window (1e-50 to 1e-30) for the test
    assert ratio < 1e-30, f"v03/v07 ratio should be ≪ 1, got {ratio:.2e}"
    assert ratio > 1e-50, f"v03/v07 ratio should be finite, got {ratio:.2e}"


def test_phase7a_epsilon_scaling():
    """The ε² scaling factor between v0.3-prelim MAP and v0.7 MAP must be correct.

    (ε_v03 / ε_v07)² where:
        ε_v03 = 10^(-56.113) ≈ 7.71e-57
        ε_v07 = 10^(-36.951) ≈ 1.12e-37
        ratio² ≈ (7.71e-57 / 1.12e-37)² ≈ 4.74e-39
    """
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    eps_v03 = d["v03_MAP"]["epsilon"]
    eps_v07 = d["comparison_to_v07"]["v07_epsilon"]
    scaling = (eps_v03 / eps_v07) ** 2
    # Expected: ~4.7e-39; allow 1e-40 to 1e-38
    assert 1e-40 < scaling < 1e-38, f"ε² scaling out of range: {scaling:.3e}"


def test_phase7a_log10_ratio_extreme():
    """log10(N_pred/observed) must be more negative than -50 (way below 1 observed)."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    min_log_ratio = d["min_log10_ratio"]
    # The finite entries should have log10(N_pred) < -50 (since observed = 1)
    # Some entries may be -inf (when N_pred = 0 due to threshold suppression)
    finite_ratios = [r["log10_ratio"] for r in d["sweep_results"] if math.isfinite(r["log10_ratio"])]
    assert min(finite_ratios) < -50, f"log10 ratio should be very negative, got min = {min(finite_ratios)}"


def test_phase7a_decision_contains_kill():
    """The decision string must contain 'KILL' (per AGENTS.md rule 11 — honest framing)."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert "KILL" in d["decision"].upper(), f"Decision should say KILL, got: {d['decision']}"


def test_phase7a_runs_as_script():
    """The phase7a script must be runnable as `python phase7a_...py` without error."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=300,  # 5-min wall-time safety
        cwd=str(REPO_ROOT),
    )
    # Exit code 0 (clean run)
    assert result.returncode == 0, f"Script failed: {result.stderr[:500]}"
    # The verdict must include the kill phrase
    assert "KILL" in result.stdout.upper() or "KILL" in result.stderr.upper(), \
        f"KILL verdict not in output: {result.stdout[:500]}"
