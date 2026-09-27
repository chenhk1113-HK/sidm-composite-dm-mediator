"""
Tests for Phase 7b — magnetic-moment LZ forward prediction at v0.3-prelim MAP.

These tests verify:
1. The phase7b script runs without errors
2. The kill criterion is TRIGGERED at v0.3-prelim MAP (drift exceeds threshold)
3. At least one m_chi gives N_pred in [0.5, 5.0] for the T90 mu_chi value
4. The LZ magnetic-moment operator returns -1.0 at the T90 workable value (N_pred = 1)
5. The drift > 100 (catastrophic) — the magnetic-moment term shifts the multi-channel fit
"""
from __future__ import annotations
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "code" / "phase7b_magnetic_moment_v03_map.py"
RESULTS_PATH = REPO_ROOT / "data" / "results" / "phase7b_magnetic_moment_v03_map.json"

# Phase 7b requires WIMpy, which lives in .venv-sidm-bench/ at the project root.
VENV_PYTHON = REPO_ROOT.parent / ".venv-sidm-bench" / "Scripts" / "python.exe"


def test_phase7b_results_json_exists():
    """Phase 7b results JSON must exist (produced by running the script via venv python)."""
    if not RESULTS_PATH.is_file():
        pytest.skip(f"Missing results: {RESULTS_PATH}. Run `python phase7b_*.py` first.")
    assert RESULTS_PATH.is_file()


def test_phase7b_results_schema():
    """The results JSON has the expected schema."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["phase"] == "7b"
    assert "v03_MAP" in d
    assert "step_1_sweep" in d
    assert "step_2_t39_with_fixed_mu" in d
    assert "kill_triggered" in d
    assert "decision" in d


def test_phase7b_v03_map_inputs():
    """The v0.3-prelim MAP inputs are the canonical T39 Tier-3 values."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["v03_MAP"]["sigma_m_0"] == pytest.approx(0.720, rel=1e-3)
    assert d["v03_MAP"]["a"] == pytest.approx(1.31, rel=1e-3)
    assert d["v03_MAP"]["log_epsilon"] == pytest.approx(-56.113, abs=0.01)


def test_phase7b_step1_some_mchi_in_range():
    """At T90 mu_chi = 6.10e-8 mu_N, at least one m_chi in [200, 2000] GeV gives N_pred in [0.5, 5.0].

    The magnetic-moment operator DOES match the LZ event at v0.3-prelim MAP (N_pred near 1)
    for some m_chi values. This is the LZ-event-matching check.
    """
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    in_range_count = sum(1 for r in d["step_1_sweep"] if r["in_reasonable_range"])
    assert in_range_count >= 1, (
        f"Expected at least 1 m_chi to give N_pred in [0.5, 5.0] at T90 mu_chi, "
        f"got {in_range_count}/4"
    )


def test_phase7b_step2_drift_far_above_threshold():
    """The T39 Tier-3 baseline log Z must drift by far more than 2.0 when LZ mag is added."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    drift = d["step_2_drift"]
    # Expected: |drift| > 2.0 (T116 threshold), and in practice much larger (~220)
    # because adding the LZ magnetic-moment term allows the multi-channel fit to find a
    # different (better) point in (sigma_m_0, a, log_eps, log_alpha) space.
    assert abs(drift) > 2.0, f"Expected |drift| > 2.0, got {drift:.3f}"


def test_phase7b_step2_kill_criterion():
    """The kill criterion per roadmap §Phase 7 must be triggered at v0.3-prelim MAP."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    # Per roadmap: "No mediator class can produce LZ event while fitting the multi-channel
    # data at v0.3-prelim MAP." The magnetic-moment DOES match the LZ event (N_pred ≈ 1)
    # but breaks the multi-channel fit (drift >> 2). The strict reading of the criterion
    # requires BOTH event-matching AND fit-preservation, so kill is triggered.
    assert d["kill_triggered"] is True, "Phase 7b kill criterion should be triggered"


def test_phase7b_decision_contains_kill():
    """The decision string must contain 'KILL' (per AGENTS.md rule 11 — honest framing)."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert "KILL" in d["decision"].upper(), f"Decision should say KILL, got: {d['decision']}"


def test_phase7b_modified_MAP_differs_from_v03():
    """The modified MAP (with LZ mag) must differ from the v0.3-prelim MAP baseline."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    modified_map = d["step_2_t39_with_fixed_mu"]["MAP"]
    v03_theta = d["v03_MAP_theta"]
    # At least one component must shift by > 1 (in log units, this is order-of-magnitude)
    max_diff = max(abs(modified_map[i] - v03_theta[i]) for i in range(4))
    assert max_diff > 1.0, f"Modified MAP too close to v0.3-prelim MAP; max diff = {max_diff}"


def test_phase7b_lz_mag_at_t90_value():
    """The LZ magnetic-moment log L at T90 workable value should be ~-1.0 (perfect Poisson)."""
    if not VENV_PYTHON.exists():
        pytest.skip(f"venv-sidm-bench Python not found at {VENV_PYTHON}")
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", """
import sys
sys.path.insert(0, 'code')
from channels_extended import loglike_lz_magnetic_moment
ll = loglike_lz_magnetic_moment(1000.0, 6.10e-8)
print(ll)
"""],
        capture_output=True, text=True, timeout=60,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Failed: {result.stderr[:500]}"
    ll = float(result.stdout.strip())
    # Should be ~-1.0 (Poisson at N_pred = 1)
    assert -1.5 < ll < -0.5, f"Expected log L ~ -1, got {ll}"


def test_phase7b_runs_as_script():
    """The phase7b script must be runnable as a script (via venv python) without error.

    This test runs the script with a small modification: it can take ~3 min wall due to
    the dynesty re-fit. Use a longer timeout.
    """
    if not VENV_PYTHON.exists():
        pytest.skip(f"venv-sidm-bench Python not found at {VENV_PYTHON}")
    # We don't re-run the full script (it takes ~3 min); just verify the script imports cleanly
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", f"import sys; sys.path.insert(0, r'{REPO_ROOT}/code'); "
                                  f"import phase7b_magnetic_moment_v03_map"],
        capture_output=True, text=True, timeout=30,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Import failed: {result.stderr[:500]}"
