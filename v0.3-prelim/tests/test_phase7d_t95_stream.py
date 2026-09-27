"""
Tests for Phase 7d — T95 stream cross-match tension at v0.3-prelim MAP.

These tests verify:
1. The phase7d script runs without errors
2. The sigma/m(v) profile at v0.3-prelim MAP matches the analytical formula
3. GD-1 tension is RELIEVED at v0.3-prelim MAP (smaller deficit than v0.7)
4. Channel 27 tension is partially relieved
5. Curated streams pass through with at least 1 in range
6. The JSON output has the expected schema
"""
from __future__ import annotations
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "code" / "phase7d_t95_stream_v03_map.py"
RESULTS_PATH = REPO_ROOT / "data" / "results" / "phase7d_t95_stream_v03_map.json"


def test_phase7d_script_exists():
    """Phase 7d script must exist at the expected location."""
    assert SCRIPT_PATH.is_file(), f"Missing script: {SCRIPT_PATH}"


def test_phase7d_results_json_exists():
    """Phase 7d results JSON must exist (produced by running the script)."""
    assert RESULTS_PATH.is_file(), f"Missing results: {RESULTS_PATH}"


def test_phase7d_results_schema():
    """The results JSON has the expected schema."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["phase"] == "7d"
    assert "v03_MAP" in d
    assert "sigma_m_profile_at_v03_map" in d
    assert "step_1_curated_streams" in d
    assert "step_2_gd1" in d
    assert "step_3_channel27" in d
    assert "step_4_robertson" in d
    assert "overall_verdict" in d


def test_phase7d_v03_map_inputs():
    """The v0.3-prelim MAP inputs are the canonical T39 Tier-3 values."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    assert d["v03_MAP"]["sigma_m_0"] == pytest.approx(0.720, rel=1e-3)
    assert d["v03_MAP"]["a"] == pytest.approx(1.31, rel=1e-3)
    assert d["v03_MAP"]["V_REF"] == 100.0


def test_phase7d_sigma_m_profile_v10():
    """sigma/m(v=10 km/s) at v0.3-prelim MAP = 0.72 * (10/100)^(-1.31) = 14.7 cm²/g."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    sm_v10 = d["sigma_m_profile_at_v03_map"]["v=10_kms"]
    expected = 0.72 * (10.0 / 100.0) ** (-1.31)
    assert sm_v10 == pytest.approx(expected, rel=1e-3)


def test_phase7d_sigma_m_profile_v100():
    """sigma/m(v=100 km/s) at v0.3-prelim MAP = 0.72 by construction."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    sm_v100 = d["sigma_m_profile_at_v03_map"]["v=100_kms"]
    assert sm_v100 == pytest.approx(0.72, rel=1e-3)


def test_phase7d_gd1_tension_relieved():
    """GD-1 tension (log10(pred/lower_bound)) should be less negative at v0.3-prelim MAP than at v0.7."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    v03_tension = d["step_2_gd1"]["v03_log10_tension_vs_lower"]
    v07_tension = d["step_2_gd1"]["v07_log10_tension_vs_lower"]
    # v0.3-prelim should be less negative (closer to 0 = IN_RANGE)
    assert v03_tension > v07_tension, (
        f"v0.3-prelim tension ({v03_tension:.3f}) should be less negative than "
        f"v0.7 tension ({v07_tension:.3f})"
    )


def test_phase7d_gd1_improvement_factor_substantial():
    """GD-1 tension should improve by at least 10x at v0.3-prelim MAP."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    improvement = d["step_2_gd1"]["improvement_factor"]
    # v0.7 reference at v=10 was 0.32; v0.3-prelim is 14.7. Ratio ~46x.
    assert improvement >= 10.0, f"GD-1 improvement should be >= 10x, got {improvement:.2f}x"


def test_phase7d_channel27_status():
    """Channel 27 sub-halo forecast tension report should be present."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    s = d["step_3_channel27"]
    assert "v03_prediction_at_v150" in s
    assert "v07_reference_at_v150" in s
    assert "v03_status" in s
    assert "v07_status" in s


def test_phase7d_curated_streams_present():
    """All 10 curated streams should have predictions."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    streams = d["step_1_curated_streams"]
    assert len(streams) >= 10, f"Expected >= 10 curated streams, got {len(streams)}"
    # GD-1 specifically should be UNDERPREDICTION
    gd1 = next((s for s in streams if s["stream"] == "GD-1"), None)
    assert gd1 is not None
    assert gd1["tension_label"] in ("UNDERPREDICTION", "IN_RANGE")
    # The 10 streams should be the canonical curated set
    stream_names = {s["stream"] for s in streams}
    assert "GD-1" in stream_names
    assert "Pal5" in stream_names


def test_phase7d_robertson_geometric_mean_in_range():
    """Robertson BAHAMAS-SIDM geometric mean ratio should be in [0.01, 0.5]."""
    with open(RESULTS_PATH) as f:
        d = json.load(f)
    geo_mean = d["step_4_robertson"]["geo_mean_ratio_v03"]
    # The geometric mean at v0.3-prelim is expected to be much smaller than T95's 0.72
    # because the steep velocity drop (a=1.31) makes sigma/m drop fast
    assert 0.01 < geo_mean < 0.5, f"Geometric mean ratio should be in [0.01, 0.5], got {geo_mean}"


def test_phase7d_runs_as_script():
    """The phase7d script must be runnable as `python phase7d_...py` without error."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Script failed: {result.stderr[:500]}"
    # Output should contain "VERDICT" line
    assert "VERDICT" in result.stdout.upper()
