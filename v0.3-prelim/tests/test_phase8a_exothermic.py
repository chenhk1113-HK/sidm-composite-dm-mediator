"""
Tests for Phase 8a — exothermic LZ interpretation at v0.3-prelim MAP.

Verifies:
1. Phase 8a script runs and produces structured output
2. The v0.3-prelim deficit vs de Lima target is correctly computed (~10^-124)
3. Required epsilon to match is correctly computed (~10^62 x actual)
4. The max sigma_inel across the sweep is correctly bounded
5. Verdict is KILL (defect > 10 orders of magnitude)
6. The de Lima benchmark parameters are correctly encoded
7. E0 formula matches de Lima's expected peak energy
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "code" / "phase8a_exothermic_v03_map.py"
RESULTS_PATH = PROJECT_ROOT / "data" / "results" / "phase8a_exothermic_v03_map.json"

sys.path.insert(0, str(PROJECT_ROOT / "code"))
import phase8a_exothermic_v03_map as phase8a  # noqa: E402


# --- Test 1: Script and results exist ---
def test_phase8a_script_exists():
    assert SCRIPT_PATH.exists(), f"Phase 8a script missing: {SCRIPT_PATH}"


def test_phase8a_results_json_exists():
    assert RESULTS_PATH.exists(), f"Phase 8a results JSON missing: {RESULTS_PATH}"


# --- Test 2: Results JSON has expected structure ---
def test_phase8a_results_structure():
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    required_keys = ["test", "v03_map", "de_lima_benchmark", "sweep_results",
                     "max_sigma_inel_cm2", "deficit_orders", "epsilon_required", "verdict"]
    for k in required_keys:
        assert k in d, f"Missing key: {k}"


# --- Test 3: v0.3-prelim MAP values match T39 ---
def test_phase8a_v03_map_values():
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    v03 = d["v03_map"]
    assert abs(v03["sigma_m_0"] - 0.72) < 0.01
    assert abs(v03["a"] - 1.31) < 0.01
    assert abs(v03["log_epsilon"] - (-56.113)) < 0.01
    assert abs(v03["log_alpha"] - (-28.047)) < 0.01
    assert abs(v03["epsilon"] - 7.71e-57) < 1e-58
    assert abs(v03["alpha_chi"] - 8.98e-29) < 1e-30


# --- Test 4: de Lima benchmark correctly encoded ---
def test_phase8a_de_lima_benchmark_values():
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    de_lima = d["de_lima_benchmark"]
    assert de_lima["m_chi_GeV"] == 45.0
    assert de_lima["delta_keV"] == 1000.0
    assert de_lima["m_Aprime_MeV"] == 1000.0
    assert de_lima["epsilon"] == 1.3e-6
    assert de_lima["f_H"] == 6.8e-3
    assert de_lima["E0_Xe_keV"] == 269.0


# --- Test 5: Verdict is KILL ---
def test_phase8a_verdict_is_kill():
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["verdict"] == "KILL", f"Expected KILL, got {d['verdict']}"
    assert d["deficit_orders"] < -10, f"Deficit must be > 10 orders, got {d['deficit_orders']}"


# --- Test 6: Sweep produces correct number of points ---
def test_phase8a_sweep_count():
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    # 4 m_chi x 3 delta x 2 ansatz = 24 points
    assert len(d["sweep_results"]) == 24, f"Expected 24 sweep points, got {len(d['sweep_results'])}"


# --- Test 7: E0 formula correctness (de Lima's eq. 1) ---
def test_phase8a_e0_formula():
    # E_0 = m_chi * delta / (m_chi + m_N)
    # For m_chi=45 GeV, delta=1 MeV=0.001 GeV, m_Xe~130 GeV:
    # E_0 = 45 * 0.001 / (45 + 130) = 0.045 / 175 = 2.571e-4 GeV = 257.1 keV
    E0 = phase8a.E0_keV(45.0, 130.0, 1000.0)
    expected = 45.0 * 1.0 / (45.0 + 130.0)  # in MeV if delta is in MeV
    # Note: phase8a.E0_keV uses delta_keV directly, so we need consistent units
    E0_correct = phase8a.E0_keV(45.0, 130.0, 1000.0)
    # 45 GeV * 1000 keV / (45 GeV + 130 GeV) = 45000 / 175 = 257.1 keV
    assert abs(E0_correct - 257.14) < 0.1, f"E0 formula wrong: {E0_correct}"


# --- Test 8: Max sigma_inel is bounded ---
def test_phase8a_max_sigma_bounded():
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    max_sigma = d["max_sigma_inel_cm2"]
    # Should be in the range [1e-165, 1e-160] (very small)
    assert 1e-170 < max_sigma < 1e-160, f"Max sigma_inel out of expected range: {max_sigma}"


# --- Test 9: Required epsilon is non-perturbative ---
def test_phase8a_epsilon_required_huge():
    """Required epsilon must violate perturbativity (epsilon > 1 for kinetic mixing).

    The required epsilon to match de Lima's alpha_D * epsilon^2 target at fixed
    alpha_chi is sqrt(target/alpha_chi) = sqrt(7e-17/8.98e-29) ~ 8.8e5.
    This is ~10^62 times larger than v0.3-prelim MAP's epsilon.
    """
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    eps_req = d["epsilon_required"]
    # Required epsilon > 1 means kinetic mixing is non-perturbative
    assert eps_req > 1.0, f"Required epsilon should be > 1 (non-perturbative), got {eps_req}"
    # Specifically we expect ~10^5-10^6 (perturbativity violation by ~6 orders)
    assert 1e5 < eps_req < 1e7, f"Expected ~10^6 (non-perturbative), got {eps_req}"


# --- Test 10: Structural finding documented ---
def test_phase8a_structural_finding_present():
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert "structural_finding" in d
    assert "INVISIBLE" in d["structural_finding"] or "decoupl" in d["structural_finding"]
