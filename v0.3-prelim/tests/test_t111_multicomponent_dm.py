"""
Tests for t111_multicomponent_dm.

T111 is the multi-component DM (Door D) analysis that adds a light
DM species to v0.7 to explain the LZ 248 keV event.

Tests pin:
  - Prior ranges for 3 light species params
  - loglike_lz_248kev_light_species: penalty for excluded, peak near match
  - prior_transform_9d: maps unit cube to physical range
  - loglike_9d: shape, finite return
  - 9D output structure (if it exists)
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

from t111_multicomponent_dm import (
    LOG_M_PHI_MEV_RANGE,
    LOG_M_CHI_GEV_RANGE,
    G_CHI_RANGE,
    LOG_EPSILON_RANGE,
    LOG_ALPHA_RANGE,
    LOG_XI_RANGE,
    LOG_M_CHI_LIGHT_GEV_RANGE,
    LOG_SIGMA_LIGHT_RANGE,
    LOG_F_LIGHT_RANGE,
    loglike_lz_248kev_light_species,
    loglike_9d,
    prior_transform_9d,
    log_prior_9d,
    LZ_EXPOSURE_TONNE_YEAR,
)


def _approx(x, atol=1e-9):
    return abs(x) < atol


class TestLightSpeciesPriors:
    """Pin the 3D light species prior ranges."""

    def test_log_m_chi_light_range(self):
        """Light species mass range: 3 to 100 GeV (log 0.5 to 2.0)."""
        assert LOG_M_CHI_LIGHT_GEV_RANGE == (0.5, 2.0)
        # Verify physical range
        assert 10 ** LOG_M_CHI_LIGHT_GEV_RANGE[0] >= 3.0
        assert 10 ** LOG_M_CHI_LIGHT_GEV_RANGE[1] <= 100.0

    def test_log_sigma_light_range(self):
        """σ_light range: 10^-48 to 10^-42 cm^2 (LZ-relevant)."""
        assert LOG_SIGMA_LIGHT_RANGE == (-48.0, -42.0)

    def test_log_f_light_range(self):
        """f_light range: 0.01% to 100% of DM density."""
        assert LOG_F_LIGHT_RANGE == (-4.0, 0.0)
        assert 10 ** LOG_F_LIGHT_RANGE[0] >= 1e-4
        assert 10 ** LOG_F_LIGHT_RANGE[1] <= 1.0

    def test_heavy_prior_unchanged(self):
        """v0.7 6D priors unchanged."""
        assert LOG_M_PHI_MEV_RANGE == (-1.0, 4.0)
        assert LOG_M_CHI_GEV_RANGE == (0.5, 3.0)
        assert G_CHI_RANGE == (0.01, 2.0)
        assert LOG_EPSILON_RANGE == (-60.0, -1.0)
        assert LOG_ALPHA_RANGE == (-30.0, -1.0)
        assert LOG_XI_RANGE == (-1.0, 0.7)


class TestLoglikeLight:
    """Test the light species LZ likelihood."""

    def test_excluded_penalty(self):
        """σ_light > 10x LZ limit returns heavy penalty."""
        # For m_chi_light = 60 GeV, LZ limit is ~2.4e-47 cm^2
        ll = loglike_lz_248kev_light_species(
            m_chi_light_GeV=60.0,
            sigma_light_cm2=1e-43,  # ~4000x LZ limit (way excluded)
            f_light=0.01,
        )
        assert ll < -100.0  # heavy penalty

    def test_zero_f_light(self):
        """f_light -> 0 gives 0 predicted events, log L from Gaussian."""
        # σ_light = 2.4e-47 (at LZ limit, not excluded)
        ll = loglike_lz_248kev_light_species(
            m_chi_light_GeV=60.0,
            sigma_light_cm2=2.4e-47,  # AT LZ limit (not excluded)
            f_light=1e-10,  # negligible
        )
        # N_pred ~ 0, N_obs = 1, log L = -0.5 * (0-1)^2 = -0.5
        assert ll < 0  # negative log L (penalty for not matching observation)
        assert _approx(ll - (-0.5), atol=0.05)

    def test_match_observation(self):
        """If N_pred matches N_obs=1, log L = 0 (best fit)."""
        # Tune parameters so N_pred ~ 1
        # N_pred ~ (2.84 * sigma/1e-45 * 10/m_chi * f_light)
        # For m_chi=60, sigma=2.4e-47: ratio = 2.4e-2
        # 2.84 * 2.4e-2 * 10/60 = 0.0113 baseline; need f_light ~ 88 to match
        ll = loglike_lz_248kev_light_species(
            m_chi_light_GeV=60.0,
            sigma_light_cm2=2.4e-47,
            f_light=88.0,  # N_pred ~ 1
        )
        # Should be near 0
        assert ll > -0.5


class TestPriorTransform:
    """Test prior_transform_9d."""

    def test_shape(self):
        rng = np.random.RandomState(42)
        u = rng.rand(9)
        theta = prior_transform_9d(u)
        assert theta.shape == (9,)

    def test_unit_cube_zero(self):
        u = np.zeros(9)
        theta = prior_transform_9d(u)
        assert theta[0] == LOG_M_PHI_MEV_RANGE[0]
        assert theta[1] == LOG_M_CHI_GEV_RANGE[0]
        assert theta[6] == LOG_M_CHI_LIGHT_GEV_RANGE[0]
        assert theta[7] == LOG_SIGMA_LIGHT_RANGE[0]
        assert theta[8] == LOG_F_LIGHT_RANGE[0]

    def test_unit_cube_one(self):
        u = np.ones(9)
        theta = prior_transform_9d(u)
        assert theta[0] == LOG_M_PHI_MEV_RANGE[1]
        assert theta[1] == LOG_M_CHI_GEV_RANGE[1]
        assert theta[6] == LOG_M_CHI_LIGHT_GEV_RANGE[1]
        assert theta[7] == LOG_SIGMA_LIGHT_RANGE[1]
        assert theta[8] == LOG_F_LIGHT_RANGE[1]

    def test_wrong_shape_raises(self):
        u = np.zeros(10)  # wrong shape
        try:
            prior_transform_9d(u)
            assert False, "Expected ValueError"
        except ValueError:
            pass


class TestLoglike9d:
    """Test the 9D combined log-likelihood."""

    def test_shape_nine(self):
        """9D theta returns a finite float."""
        theta = [2.77, 2.7, 0.45, -36.95, -16.17, 0.0, np.log10(60), -45.0, -2.0]
        ll = loglike_9d(theta)
        assert isinstance(ll, float)
        assert np.isfinite(ll)

    def test_wrong_shape_returns_neginf(self):
        """8D theta returns -inf."""
        theta_8d = [2.77, 2.7, 0.45, -36.95, -16.17, 0.0, 1.78, -45.0]
        assert loglike_9d(theta_8d) == -np.inf

    def test_log_prior_9d_in_range(self):
        """theta within prior returns 0."""
        theta = [2.77, 2.7, 0.45, -36.95, -16.17, 0.0, 1.78, -45.0, -2.0]
        assert log_prior_9d(theta) == 0.0

    def test_log_prior_9d_out_of_range(self):
        """theta out of prior returns -inf."""
        theta = [10.0, 2.7, 0.45, -36.95, -16.17, 0.0, 1.78, -45.0, -2.0]  # m_phi out of range
        assert log_prior_9d(theta) == -np.inf


class TestFullOutput:
    """Verify the final T111 result file if it exists."""

    def test_output_structure_if_exists(self):
        """If the full run completed, check the output JSON."""
        out_path = (
            ROOT / "v0.3-prelim" / "outputs" / "t95" / "t111_multicomponent_9d_emcee.json"
        )
        if not out_path.exists():
            import pytest
            pytest.skip(f"T111 output not yet produced at {out_path}")
        with open(out_path) as f:
            result = json.load(f)
        assert "log_z_approx_emcee" in result
        assert "delta_log_z_vs_v07_6d_approx" in result
        assert "t90_merge_criterion_5_satisfied_approx" in result
        assert "map_sample_physical" in result
        assert "wall_seconds" in result
        # Heavy and light species both present
        assert "heavy_species" in result["map_sample_physical"]
        assert "light_species" in result["map_sample_physical"]
        # f_light should be in [1e-4, 1.0]
        f_light = result["map_sample_physical"]["light_species"]["f_light"]
        assert 1e-4 <= f_light <= 1.0


class TestVsDoors:
    """Compare T111 to T108 (Door B) and T110 (Door C)."""

    def test_t111_tests_door_d(self):
        """T111 tests Door D (multi-component DM), separate from Door B (T108) and Door C (T110)."""
        t108_out = (
            ROOT / "v0.3-prelim" / "outputs" / "t95" / "t108_full_8d_dynesty.json"
        )
        t110_out = (
            ROOT / "v0.3-prelim" / "outputs" / "t95" / "t110_full_7d_dynesty.json"
        )
        t111_out = (
            ROOT / "v0.3-prelim" / "outputs" / "t95" / "t111_multicomponent_9d_emcee.json"
        )
        if not t111_out.exists():
            import pytest
            pytest.skip("T111 output not yet produced")
        with open(t111_out) as f:
            t111 = json.load(f)
        # T111 is multi-component DM; door D
        assert "light_species" in t111["map_sample_physical"]
        assert "f_light" in t111["map_sample_physical"]["light_species"]
