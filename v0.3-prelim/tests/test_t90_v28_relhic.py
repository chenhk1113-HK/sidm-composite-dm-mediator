"""Tests for T90.28 RELHIC empirical forward model + MCMC + likelihood v2.

Per T90.28 scope:
  - Empirical N(HI) profile shape (calibrated to Cloud-9 published)
  - Cosmological concentration-mass prior (Diemer & Joyce 2019)
  - σ/m <-> τ mapping via t_collapse
  - emcee MCMC for the (M200, c200, τ) posterior
  - T41 Channel 27 v2 likelihood (replaces T90.27 v1 delta-prior)

The tests are intentionally light (10 tests) covering:
  - N(HI) profile matches published Cloud-9 values to 0.1 dex (3 tests)
  - σ/m at v200 mapping for Cloud-9 best-fits (2 tests)
  - Concentration-mass prior at the published points (1 test)
  - MCMC runs and produces finite log_posterior (2 tests)
  - loglike_relhic_v28 returns finite values for sensible inputs (1 test)
  - loglike_relhic_v28 returns the expected off-grid penalty for invalid inputs (1 test)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import numpy as np  # noqa: E402

from t90_v28_relhic_hydrostatic_full import (  # noqa: E402
    CLOUD9_PUBLISHED_B_KPC,
    CLOUD9_PUBLISHED_LOG_NHI,
    N_HI_universal,
    N_HI_scaled,
    c200_median_DiemerJoyce,
    log_prior_concentration_mass,
    LOG10_SIGMA_M_PRIOR_RANGE,
)
from t90_v27_relhic_hydrostatic import (  # noqa: E402
    CLOUD9_NHI_B_KPC,
    CLOUD9_NHI_LOG10_CM2,
    t_collapse,
    T_AGE_GYR,
    m200_c200_to_rho_s_rs,
    v200_from_M200,
)
from t90_v28_relhic_mcmc import (  # noqa: E402
    log_posterior,
    sigma_m_from_halo,
    log_prior_halo,
    log_likelihood_data,
)
from t90_v28_relhic_likelihood import (  # noqa: E402
    loglike_relhic_v28,
    sigma_m_at_v,
    tau_at_sigma_m,
)


def test_NHI_universal_matches_published_at_central():
    """At b=0.5 kpc (innermost data point), N_HI matches the published value."""
    b = np.array([0.5])
    n = N_HI_universal(b)
    assert abs(np.log10(n[0]) - 19.70) < 0.05, f"log N_HI = {np.log10(n[0])}, expected 19.70"


def test_NHI_universal_matches_published_at_outer():
    """At b=10 kpc, N_HI matches the published value."""
    b = np.array([10.0])
    n = N_HI_universal(b)
    assert abs(np.log10(n[0]) - 18.00) < 0.1, f"log N_HI = {np.log10(n[0])}, expected 18.00"


def test_NHI_universal_matches_published_at_all_data_points():
    """At all 13 published data points, N_HI matches within interpolation tolerance."""
    n_pred = N_HI_universal(CLOUD9_PUBLISHED_B_KPC)
    log_n_pred = np.log10(n_pred)
    # Linear interpolation: at the data points themselves, the
    # interpolated value equals the data value (np.interp edge cases).
    max_diff = np.max(np.abs(log_n_pred - CLOUD9_PUBLISHED_LOG_NHI))
    assert max_diff < 1e-10, f"max log10 diff at data points = {max_diff}"


def test_sigma_m_from_halo_at_cloud9_bestfit_t018():
    """At the Cloud-9 SIDM τ=0.18 best-fit, σ/m at v200 should be ~ 483 cm²/g.

    Allow factor 2 tolerance for the calibration uncertainty in t_collapse.
    """
    M200, c200, tau = 4.7e9, 4.0, 0.18
    sm = sigma_m_from_halo(np.log10(M200), c200, tau)
    assert 200 < sm < 1000, f"σ/m = {sm}, expected ~ 483"


def test_sigma_m_from_halo_at_cdm_bestfit():
    """At the CDM best-fit (τ=0), σ/m should be 0 (collisionless)."""
    M200, c200, tau = 7e8, 6.0, 0.0
    sm = sigma_m_from_halo(np.log10(M200), c200, tau)
    assert sm == 0.0, f"σ/m = {sm}, expected 0 for CDM"


def test_concentration_prior_penalizes_extreme_concentrations():
    """The Diemer & Joyce 2019 prior penalizes concentrations far from c_med."""
    M200 = 4.7e9
    c_med = c200_median_DiemerJoyce(M200)
    # At c_med: log_prior = 0
    assert abs(log_prior_concentration_mass(M200, c_med)) < 0.01
    # At 0.1 × c_med (factor 10 below): log_prior << 0
    assert log_prior_concentration_mass(M200, 0.1 * c_med) < -10
    # At 10 × c_med (factor 10 above): log_prior << 0
    assert log_prior_concentration_mass(M200, 10 * c_med) < -10


def test_log_posterior_finite_at_cloud9_bestfit():
    """log_posterior returns finite value at the Cloud-9 SIDM τ=0.18 best-fit."""
    lp = log_posterior((np.log10(4.7e9), 4.0, 0.18))
    assert np.isfinite(lp), f"log_posterior = {lp}"


def test_log_posterior_infinite_outside_prior():
    """log_posterior returns -inf for points outside the prior range."""
    # M200 below the stability floor (2.5e9)
    assert log_posterior((np.log10(1e9), 4.0, 0.18)) == -np.inf
    # c200 below the prior range
    assert log_posterior((np.log10(4.7e9), 1.0, 0.18)) == -np.inf
    # tau above the prior range
    assert log_posterior((np.log10(4.7e9), 4.0, 1.5)) == -np.inf


def test_loglike_relhic_v28_finite_at_sensible_inputs():
    """loglike_relhic_v28 returns finite values for in-range inputs."""
    # Cloud-9 best-fit
    ll = loglike_relhic_v28(483.0, 0.0)
    assert np.isfinite(ll)
    # T41 v0.7 master MAP
    ll2 = loglike_relhic_v28(0.28, 0.16)
    assert np.isfinite(ll2)
    # Intermediate
    ll3 = loglike_relhic_v28(10.0, 0.0)
    assert np.isfinite(ll3)


def test_loglike_relhic_v28_returns_zero_for_invalid_inputs():
    """loglike_relhic_v28 returns 0 for non-finite or non-positive inputs."""
    assert loglike_relhic_v28(0.0, 0.0) == 0.0
    assert loglike_relhic_v28(-1.0, 0.0) == 0.0
    assert loglike_relhic_v28(0.3, np.inf) == 0.0
    assert loglike_relhic_v28(0.3, np.nan) == 0.0


def test_loglike_relhic_v28_offgrid_penalty():
    """loglike_relhic_v28 returns a strong negative penalty for σ/m off-grid.

    The Cloud-9 MCMC posterior is in [σ/m ~ 1, 10^5] cm²/g. Outside
    this range (e.g. CDM-like σ/m → 0), the posterior is essentially
    zero and the likelihood should be strongly negative.
    """
    # Pure CDM: σ/m → 0
    ll_cdm = loglike_relhic_v28(1e-5, 0.0)
    # Cloud-9 best-fit region
    ll_bestfit = loglike_relhic_v28(100.0, 0.0)
    # The CDM case should be MORE negative than the best-fit region
    assert ll_cdm < ll_bestfit, f"CDM loglike {ll_cdm} should be < best-fit {ll_bestfit}"


def test_sigma_m_at_v_joint_fit_parametrization():
    """σ/m at v from the joint-fit (σ_m_0, a) parametrization."""
    # σ/m(v) = σ/m_0 × (v/100)^(-a)
    # At v=100: σ/m = σ/m_0
    assert abs(sigma_m_at_v(0.28, 0.16, 100.0) - 0.28) < 1e-10
    # At v=10, a=0: σ/m = σ/m_0
    assert abs(sigma_m_at_v(0.28, 0.0, 10.0) - 0.28) < 1e-10
    # At v=10, a=1: σ/m = 2.8
    assert abs(sigma_m_at_v(0.28, 1.0, 10.0) - 2.8) < 1e-10
