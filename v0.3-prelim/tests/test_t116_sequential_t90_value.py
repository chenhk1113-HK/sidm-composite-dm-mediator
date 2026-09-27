"""
Tests for t116_sequential_t90_value.

T116 is the sequential confirmation of the T90-era workable
magnetic-moment value (mu_chi = 6.10e-8 mu_N at m_chi = 1000 GeV).

Tests pin:
  - T90 magnetic-moment value (mu_chi = 6.10e-8 mu_N, m_chi = 1000 GeV)
  - predict_lz_events_at_t90_value function returns expected structure
  - check_v07_preserved_at_t90_value function
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
CODE_DIR = SCRIPT_DIR.parent / "code"
ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(CODE_DIR))

from t116_sequential_t90_value import (
    T90_MU_CHI_MU_N,
    T90_M_CHI_GEV,
    predict_lz_events_at_t90_value,
    check_v07_preserved_at_t90_value,
)


def _approx(x, atol=1e-3):
    return abs(x) < atol


class TestT90Value:
    """Pin the T90-era workable magnetic-moment value."""

    def test_mu_chi_value(self):
        """T90-era mu_chi = 6.10e-8 mu_N."""
        assert _approx(T90_MU_CHI_MU_N - 6.10e-8, atol=1e-10)

    def test_m_chi_value(self):
        """T90-era m_chi = 1000 GeV (1 TeV)."""
        assert T90_M_CHI_GEV == 1000.0


class TestPredictLZ:
    """Test LZ event prediction at T90 value."""

    def test_returns_dict(self):
        """predict_lz_events_at_t90_value returns dict."""
        result = predict_lz_events_at_t90_value()
        assert isinstance(result, dict)
        for k in ["m_chi_GeV", "mu_chi_mu_N", "log_L", "N_pred", "in_reasonable_range", "wimpy_available"]:
            assert k in result

    def test_at_t90_value(self):
        """T90 value: m_chi = 1000 GeV, mu_chi = 6.10e-8 mu_N."""
        result = predict_lz_events_at_t90_value()
        assert result["m_chi_GeV"] == 1000.0
        assert _approx(result["mu_chi_mu_N"] - 6.10e-8, atol=1e-10)

    def test_n_pred_at_t90_value(self):
        """N_pred at T90 value should match LZ observation (~1 event)."""
        result = predict_lz_events_at_t90_value()
        n_pred = result["N_pred"]
        # The T90 workable value was tuned to match LZ, so N_pred ~ 1
        assert n_pred > 0
        assert n_pred < 10  # not unreasonable


class TestPreservationCheck:
    """Test preservation check function."""

    def test_check_returns_dict(self):
        """check_v07_preserved_at_t90_value returns dict with expected keys."""
        result = check_v07_preserved_at_t90_value(-163.5)
        assert "log_Z_with_mu" in result
        assert "log_Z_drift" in result
        assert "log_Z_preserved" in result
        assert "verdict" in result
        # At published v0.7 log Z, should be preserved
        assert result["log_Z_preserved"]

    def test_check_detects_drift(self):
        """check_v07_preserved_at_t90_value detects drift."""
        result = check_v07_preserved_at_t90_value(-200.0)
        assert not result["log_Z_preserved"]


class TestT116Output:
    """Verify T116 output if it exists."""

    def test_output_structure_if_exists(self):
        """If T116 ran, check output structure."""
        out_path = ROOT / "v0.3-prelim" / "outputs" / "t95" / "t116_sequential_t90_value.json"
        if not out_path.exists():
            import pytest
            pytest.skip(f"T116 output not yet produced at {out_path}")
        with open(out_path) as f:
            result = json.load(f)
        assert "t90_value_used" in result
        assert "preservation_check" in result
        assert "lz_event_prediction" in result
        assert "overall_verdict" in result
        assert "comparison_to_t110_global" in result
        assert result["t90_value_used"]["mu_chi_mu_N"] == 6.10e-8
        assert result["t90_value_used"]["m_chi_GeV"] == 1000.0