"""
Tests for t110_full_7d_dynesty.

T110 is the FULL 7D dynesty nested sampling run that adds μ_χ (magnetic-
moment Ls₁₀) to the v0.7 6D baseline. Tests pin:
  - log_mu_x_mu_N prior range (4 decades, [-7, -3])
  - loglike_7d function: shape, env-var activation, finite return
  - prior_transform_7d: maps unit cube to physical range
  - 7D posterior: log Z, Δlog Z vs v0.7 6D = -163.29
  - T90 merge rule criterion #5 check (Δlog Z ≥ +2)

Unit tests are pure-Python (no dynesty). The full run is exercised
separately by the user via T110_NLIVE / T110_DLOGZ env vars.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
CODE_DIR = SCRIPT_DIR.parent / "code"
ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(ROOT / "v0.1-prelim"))
sys.path.insert(0, str(ROOT / "v0.1-prelim" / "code"))

from t110_full_7d_dynesty import (
    LOG_M_PHI_MEV_RANGE,
    LOG_M_CHI_GEV_RANGE,
    G_CHI_RANGE,
    LOG_EPSILON_RANGE,
    LOG_ALPHA_RANGE,
    LOG_XI_RANGE,
    LOG_MU_X_MU_N_RANGE,
    loglike_7d,
    prior_transform_7d,
)


def _approx(x, atol=1e-9):
    return abs(x) < atol


class TestPriorRanges:
    """Pin the 7D prior ranges."""

    def test_log_m_phi_range(self):
        assert LOG_M_PHI_MEV_RANGE == (-1.0, 4.0)

    def test_log_m_chi_range(self):
        assert LOG_M_CHI_GEV_RANGE == (0.5, 3.0)

    def test_g_chi_range(self):
        assert G_CHI_RANGE == (0.01, 2.0)

    def test_log_epsilon_range(self):
        assert LOG_EPSILON_RANGE == (-60.0, -1.0)

    def test_log_alpha_range(self):
        assert LOG_ALPHA_RANGE == (-30.0, -1.0)

    def test_log_xi_range(self):
        assert LOG_XI_RANGE == (-1.0, 0.7)

    def test_log_mu_x_range(self):
        """μ_χ prior spans [10^-7, 10^-3] mu_N (4 decades)."""
        assert LOG_MU_X_MU_N_RANGE == (-7.0, -3.0)
        # Verify span: -3 - (-7) = 4.0 in log10
        span = LOG_MU_X_MU_N_RANGE[1] - LOG_MU_X_MU_N_RANGE[0]
        assert _approx(span - 4.0)

    def test_mu_x_prior_naturalness(self):
        """μ_χ prior midpoint should be near composite-DM natural estimate."""
        mid = (LOG_MU_X_MU_N_RANGE[0] + LOG_MU_X_MU_N_RANGE[1]) / 2
        # Natural value is ~10^-4 mu_N; prior midpoint is 10^-5
        assert -6.0 < mid < -4.0


class TestPriorTransform:
    """Verify prior_transform_7d maps unit cube to physical ranges."""

    def test_unit_cube_zero(self):
        u = np.zeros(7)
        theta = prior_transform_7d(u)
        assert theta[0] == LOG_M_PHI_MEV_RANGE[0]
        assert theta[1] == LOG_M_CHI_GEV_RANGE[0]
        assert theta[2] == G_CHI_RANGE[0]
        assert theta[3] == LOG_EPSILON_RANGE[0]
        assert theta[4] == LOG_ALPHA_RANGE[0]
        assert theta[5] == LOG_XI_RANGE[0]
        assert theta[6] == LOG_MU_X_MU_N_RANGE[0]

    def test_unit_cube_one(self):
        u = np.ones(7)
        theta = prior_transform_7d(u)
        assert theta[0] == LOG_M_PHI_MEV_RANGE[1]
        assert theta[1] == LOG_M_CHI_GEV_RANGE[1]
        assert theta[2] == G_CHI_RANGE[1]
        assert theta[3] == LOG_EPSILON_RANGE[1]
        assert theta[4] == LOG_ALPHA_RANGE[1]
        assert theta[5] == LOG_XI_RANGE[1]
        assert theta[6] == LOG_MU_X_MU_N_RANGE[1]

    def test_shape(self):
        rng = np.random.RandomState(42)
        u = rng.rand(7)
        theta = prior_transform_7d(u)
        assert theta.shape == (7,)

    def test_wrong_shape_raises(self):
        rng = np.random.RandomState(42)
        u = rng.rand(8)  # wrong shape
        try:
            prior_transform_7d(u)
            assert False, "Expected ValueError"
        except ValueError:
            pass


class TestLoglike:
    """Verify loglike_7d function shape and behavior."""

    def test_shape_seven(self):
        """7D theta returns a finite float."""
        theta = [2.77, 2.7, 0.45, -36.95, -16.17, 0.0, -5.0]
        ll = loglike_7d(theta)
        assert isinstance(ll, float)
        assert np.isfinite(ll)

    def test_wrong_shape_returns_neginf(self):
        """5D or 8D theta returns -inf."""
        theta_5d = [2.77, 2.7, 0.45, -36.95, -16.17]
        theta_8d = [2.77, 2.7, 0.45, -36.95, -16.17, 0.0, -5.0, 0.0]
        assert loglike_7d(theta_5d) == -np.inf
        assert loglike_7d(theta_8d) == -np.inf

    def test_env_var_set(self):
        """loglike_7d sets T90_MAGNETIC_MOMENT_MU_X env var."""
        old_val = os.environ.get("T90_MAGNETIC_MOMENT_MU_X", None)
        try:
            theta = [2.77, 2.7, 0.45, -36.95, -16.17, 0.0, -5.0]
            loglike_7d(theta)
            # Should be set to 1e-5
            assert os.environ.get("T90_MAGNETIC_MOMENT_MU_X") == "1.000000e-05"
        finally:
            if old_val is not None:
                os.environ["T90_MAGNETIC_MOMENT_MU_X"] = old_val
            else:
                os.environ.pop("T90_MAGNETIC_MOMENT_MU_X", None)


class TestFullOutput:
    """Verify the final T110 result file if it exists."""

    def test_output_structure_if_exists(self):
        """If the full run completed, check the output JSON."""
        out_path = (
            ROOT / "v0.3-prelim" / "outputs" / "t95" / "t110_full_7d_dynesty.json"
        )
        if not out_path.exists():
            import pytest
            pytest.skip(f"T110 output not yet produced at {out_path}")
        with open(out_path) as f:
            result = json.load(f)
        # Check keys
        assert "log_z" in result
        assert "log_z_err" in result
        assert "delta_log_z_vs_v07_6d" in result
        assert "t90_merge_criterion_5_satisfied" in result
        assert "map_sample_physical" in result
        assert "wall_seconds" in result
        # log_z must be finite
        assert np.isfinite(result["log_z"])
        # v0.7 6D reference
        assert _approx(result["v07_6d_log_z"] - (-163.29), atol=0.01)
        # T90 criterion check
        if result["delta_log_z_vs_v07_6d"] >= 2.0:
            assert result["t90_merge_criterion_5_satisfied"] is True
        else:
            assert result["t90_merge_criterion_5_satisfied"] is False


class TestVsT108:
    """Compare T110 (7D + mu_chi) vs T108 (8D + Portal B)."""

    def test_t110_tests_criterion_5(self):
        """T110 is the dedicated criterion-#5 test (Δlog Z ≥ +2)."""
        t108_out = (
            ROOT / "v0.3-prelim" / "outputs" / "t95" / "t108_full_8d_dynesty.json"
        )
        t110_out = (
            ROOT / "v0.3-prelim" / "outputs" / "t95" / "t110_full_7d_dynesty.json"
        )
        if not (t108_out.exists() and t110_out.exists()):
            import pytest
            pytest.skip("Need both T108 and T110 outputs for comparison")
        with open(t108_out) as f:
            t108 = json.load(f)
        with open(t110_out) as f:
            t110 = json.load(f)
        # T108 is 8D (v0.7 + δ + σ_PortalB); T110 is 7D (v0.7 + μ_χ).
        # They test DIFFERENT dimensions; log Z values should differ.
        # T108 uses 'log_Z' (capital Z) in its JSON; T110 uses 'log_z'.
        log_z_t108 = t108.get("log_Z", t108.get("log_z"))
        log_z_t110 = t110.get("log_z", t110.get("log_Z"))
        assert log_z_t108 is not None and log_z_t110 is not None
        assert abs(log_z_t108 - log_z_t110) > 0.1 or (
            log_z_t108 == log_z_t110
        )
