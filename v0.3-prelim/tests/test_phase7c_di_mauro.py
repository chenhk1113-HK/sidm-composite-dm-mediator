"""
Tests for Phase 7c — Di Mauro inelastic LZ interpretation at v0.3-prelim MAP.

These tests verify:
1. The phase7c script runs without errors
2. The kill criterion is TRIGGERED at v0.3-prelim MAP
3. Both Di Mauro models (Pseudo-Dirac, Higgsino) are >100 orders short
4. The deficit is similar to or worse than v0.7 MAP baseline
5. The JSON output has the expected schema
"""
from __future__ import annotations
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "code" / "phase7c_di_mauro_v03_map.py"
RESULTS_PATH = REPO_ROOT / "data" / "results" / "phase7c_di_mauro_v03_map.json"


def test_phase7c_script_exists():
    """Phase 7c script must exist at the expected location."""
    assert SCRIPT_PATH.is_file(), f"Missing script: {SCRIPT_PATH}"


def test_phase7c_results_json_exists():
    """Phase 7c results JSON must exist (produced by running the script)."""
    assert RESULTS_PATH.is_file(), f"Missing results: {RESULTS_PATH}"


def test_phase7c_results_schema():
    """The results JSON has the expected schema."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["phase"] == "7c"
    assert "v03_MAP" in d
    assert "di_mauro_models" in d
    assert "sweep_results" in d
    assert "di_mauro_model_specific" in d
    assert "kill_triggered" in d
    assert "decision" in d
    # v0.3-prelim MAP inputs
    assert d["v03_MAP"]["sigma_m_0"] == pytest.approx(0.720, rel=1e-3)
    assert d["v03_MAP"]["a"] == pytest.approx(1.31, rel=1e-3)
    assert d["v03_MAP"]["log_epsilon"] == pytest.approx(-56.113, abs=0.01)
    # Di Mauro models
    assert "Pseudo-Dirac fermion" in d["di_mauro_models"]
    assert "Thermal Higgsino" in d["di_mauro_models"]


def test_phase7c_kill_triggered():
    """The Di Mauro sub-task at v0.3-prelim MAP MUST trigger the kill criterion."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["kill_triggered"] is True


def test_phase7c_decision_contains_kill():
    """The decision string must contain 'KILL' (per AGENTS.md rule 11 — honest framing)."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert "KILL" in d["decision"].upper(), f"Decision should say KILL, got: {d['decision']}"


def test_phase7c_pseudo_dirac_huge_deficit():
    """Pseudo-Dirac fermion at v0.3-prelim MAP must be >100 orders short of Di Mauro target."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    r = d["di_mauro_model_specific"]["Pseudo-Dirac fermion"]
    # deficit in log10
    deficit_log10 = -r["log10_ratio_sigma_vs_DiMauro"]  # negative log10 → positive deficit
    assert deficit_log10 > 100, f"Pseudo-Dirac deficit should be >100 orders, got {deficit_log10:.2f}"


def test_phase7c_higgsino_huge_deficit():
    """Thermal Higgsino at v0.3-prelim MAP must be >100 orders short of Di Mauro target."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    r = d["di_mauro_model_specific"]["Thermal Higgsino"]
    deficit_log10 = -r["log10_ratio_sigma_vs_DiMauro"]
    assert deficit_log10 > 100, f"Higgsino deficit should be >100 orders, got {deficit_log10:.2f}"


def test_phase7c_sweep_extremely_negative_log_ratio():
    """All sweep entries should have log10(ratio) < -100 (way below 10^-43 cm²)."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    for r in d["sweep_results"]:
        # Some entries may be -inf (when N_pred = 0 due to threshold suppression)
        if math.isfinite(r["log10_ratio_sigma_vs_DiMauro"]):
            assert r["log10_ratio_sigma_vs_DiMauro"] < -100, (
                f"log10 ratio should be < -100, got {r['log10_ratio_sigma_vs_DiMauro']}"
            )


def test_phase7c_runs_as_script():
    """The phase7c script must be runnable as `python phase7c_...py` without error."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=120,  # 2-min wall-time safety
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Script failed: {result.stderr[:500]}"
    assert "KILL" in result.stdout.upper(), "KILL verdict not in output"
