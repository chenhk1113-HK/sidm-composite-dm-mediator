"""Tests for T90.29 v3 Yukawa-form Cloud-9 likelihood.

Per T90.29 scope:
  - σ/m at v=28 km/s via the Yukawa form (Born approximation)
  - σ/m at v=28 km/s matches Cloud-9's published 50-500 cm²/g range
    for m_phi = 1-10 MeV and g_chi = 0.13-0.4 (perturbative)
  - T90.29 v3 likelihood returns finite values for sensible inputs
  - T90.29 v3 likelihood returns the expected off-grid penalty
  - T90.29 v3 supersedes T90.28 v2 when both are available

The tests are intentionally light (10 tests) covering:
  - Yukawa σ/m at v=28 km/s (3 tests)
  - σ/m matches Cloud-9 published range (1 test)
  - loglike_relhic_v29_yukawa edge cases (3 tests)
  - loglike_relhic_t90v29 wrapper (2 tests)
  - Module importability (1 test)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import numpy as np  # noqa: E402

from t90_v29_relhic_yukawa import (  # noqa: E402
    sigma_m_cloud9_v200_yukawa,
    tau_at_sigma_m_yukawa,
    loglike_relhic_v29_yukawa,
    loglike_relhic_t90v29,
)
from t40_yukawa_sigma_m import (  # noqa: E402
    sigma_m_cm2_per_g,
    g_chi_to_match_sigma_m_0,
)


def test_yukawa_sigma_m_at_cloud9_v200_low_mphi_high_sigma():
    """At (m_phi=10 MeV, g_chi=0.4), Yukawa gives σ/m(28) ~ 600 cm²/g.

    This is the high-σ/m Cloud-9-favorable regime.
    """
    sm = sigma_m_cloud9_v200_yukawa(10, 500, 0.4)
    assert 100 < sm < 2000, f"σ/m = {sm}, expected ~ 600"


def test_yukawa_sigma_m_at_cloud9_v200_pure_cdm():
    """At g_chi=0 (CDM, no self-interaction), σ/m should be 0."""
    sm = sigma_m_cloud9_v200_yukawa(750, 500, 0.0)
    assert sm == 0.0, f"σ/m = {sm}, expected 0 for CDM"


def test_yukawa_sigma_m_at_cloud9_v200_at_v07_map():
    """At the T41 v0.7 MAP (m_phi=750, m_chi=500, g_chi=0.1), σ/m(28) is tiny.

    This is the off-grid case that requires a different m_phi prior
    to resolve (deferred to T90.30+).
    """
    sm = sigma_m_cloud9_v200_yukawa(750, 500, 0.1)
    assert sm < 1e-3, f"σ/m = {sm}, expected << 1 cm²/g"


def test_yukawa_matches_cloud9_published_range():
    """At m_phi=10 MeV and g_chi=0.22, Yukawa gives σ/m(28) in Cloud-9's published range.

    Per arXiv:2608.04362 §3.1, the SIDM best-fit has σ/m ~ 50-500 cm²/g
    at the dwarf-halo v200. We verify that g_chi=0.22 reproduces this.
    """
    sm = sigma_m_cloud9_v200_yukawa(10, 500, 0.22)
    assert 30 < sm < 100, f"σ/m = {sm}, expected ~ 50 cm²/g"


def test_tau_at_sigma_m_in_published_range():
    """At Cloud-9 SIDM τ=0.18 best-fit (σ/m=483 at v200=28), τ should be ~ 0.2."""
    sm = 483.0
    tau = tau_at_sigma_m_yukawa(sm)
    # Allow factor 2 tolerance for the t_collapse calibration uncertainty
    assert 0.05 < tau < 0.5, f"τ = {tau}, expected ~ 0.18"


def test_tau_at_sigma_m_zero_for_cdm():
    """At σ/m → 0 (CDM), τ → 0 (no gravothermal evolution)."""
    tau = tau_at_sigma_m_yukawa(0.0)
    assert tau == 0.0, f"τ = {tau}, expected 0 for CDM"


def test_loglike_relhic_v29_yukawa_finite_at_cloud9_bestfit():
    """loglike is finite at the Cloud-9 best-fit (m_phi=10, g_chi=0.4)."""
    ll = loglike_relhic_v29_yukawa(10, 500, 0.4)
    assert np.isfinite(ll), f"loglike = {ll}"


def test_loglike_relhic_v29_yukawa_returns_offgrid_penalty_at_v07_map():
    """At the v0.7 MAP (σ/m(28) << Cloud-9 MCMC range), the off-grid penalty is -10."""
    ll = loglike_relhic_v29_yukawa(750, 500, 0.1)
    # Should be -10.0 (off-grid) since σ/m(28) = 1.4e-6 is way below the
    # T90.28 v2 grid range (log10 σ/m ~ -1 to 5).
    assert ll <= -10.0, f"loglike = {ll}, expected <= -10 (off-grid penalty)"


def test_loglike_relhic_v29_yukawa_zero_for_invalid_inputs():
    """loglike returns 0 for non-finite or non-positive inputs."""
    assert loglike_relhic_v29_yukawa(0, 500, 0.1) == 0.0
    assert loglike_relhic_v29_yukawa(10, 0, 0.1) == 0.0
    assert loglike_relhic_v29_yukawa(10, 500, 0) == 0.0
    assert loglike_relhic_v29_yukawa(10, 500, -0.1) == 0.0
    assert loglike_relhic_v29_yukawa(10, np.inf, 0.1) == 0.0


def test_loglike_relhic_t90v29_wrapper_extracts_correctly():
    """loglike_relhic_t90v29 correctly extracts (m_phi, m_chi, g_chi) from T41 theta."""
    # T41 theta = (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_eps, log_alpha, log_xi)
    # m_phi = 10 MeV, m_chi = 500 GeV, g_chi = 0.22
    theta = (np.log10(10), np.log10(500), 0.22, -30.0, -3.0, 0.0)
    ll = loglike_relhic_t90v29(theta)
    # Compare with direct call
    ll_direct = loglike_relhic_v29_yukawa(10, 500, 0.22)
    assert abs(ll - ll_direct) < 1e-10, f"wrapper loglike {ll} != direct {ll_direct}"


def test_module_imports_without_error():
    """The T90.29 v3 module imports cleanly (sanity check)."""
    import t90_v29_relhic_yukawa  # noqa: F401
    assert hasattr(t90_v29_relhic_yukawa, "loglike_relhic_v29_yukawa")
    assert hasattr(t90_v29_relhic_yukawa, "loglike_relhic_t90v29")


def test_loglike_relhic_v29_yukawa_no_indexerror_at_grid_edge():
    """Regression test: T90.29 v3 must not IndexError when (log10_sm, tau)
    lands exactly on the last grid bin.

    The original bug was np.clip(i_sm, 0, H.shape[0] - 1) which left
    H[i_sm + 1] out of bounds when i_sm was the last index. The fix
    is np.clip(..., 0, H.shape[0] - 2) so that i_sm + 1 is always
    a valid index.
    """
    # Force-load the T90.28 v2 posterior (lazy)
    import t90_v28_relhic_likelihood as v28
    v28._ensure_posterior_loaded()
    H = v28._POSTERIOR_CACHE
    log10_sm_bins = v28._LOG10_SM_BINS_CACHE
    tau_bins = v28._TAU_BINS_CACHE

    # Test 1: log10_sm exactly at the last bin edge
    log10_sm_max = log10_sm_bins[-1]
    # Find a tau inside the grid
    tau_in = 0.3
    # Find the corresponding (m_phi, m_chi, g_chi) that produces
    # log10_sm exactly at the last bin edge
    from t90_v29_relhic_yukawa import (
        sigma_m_cloud9_v200_yukawa, tau_at_sigma_m_yukawa,
    )
    # Sweep g_chi to find one that gives log10_sm at the grid edge
    for g_chi_test in [0.5, 0.7, 1.0, 1.5, 2.0]:
        sm = sigma_m_cloud9_v200_yukawa(10.0, 500.0, g_chi_test)
        if sm > 0 and np.log10(sm) >= log10_sm_max - 0.1:
            break
    # Call the likelihood — should not IndexError
    try:
        ll = loglike_relhic_v29_yukawa(10.0, 500.0, g_chi_test)
        assert np.isfinite(ll) or ll == -10.0, f"unexpected loglike: {ll}"
    except IndexError as e:
        raise AssertionError(f"IndexError at grid edge: {e}")

    # Test 2: tau exactly at the last bin edge
    tau_max = tau_bins[-1]
    for g_chi_test in [0.1, 0.5, 1.0]:
        sm = sigma_m_cloud9_v200_yukawa(100.0, 500.0, g_chi_test)
        if sm > 0:
            tau_test = tau_at_sigma_m_yukawa(sm)
            if tau_test >= tau_max - 0.05:
                try:
                    ll = loglike_relhic_v29_yukawa(100.0, 500.0, g_chi_test)
                    assert np.isfinite(ll) or ll == -10.0
                except IndexError as e:
                    raise AssertionError(f"IndexError at tau edge: {e}")
                break


def test_g_chi_to_match_cloud9_is_perturbative():
    """The g_chi needed to match Cloud-9's σ/m at m_phi=10 MeV is perturbative.

    Per the T90.29 doc: at m_phi=10 MeV, m_chi=500 GeV, g_chi=0.22
    gives σ/m(28) ~ 50 cm²/g (Cloud-9 lower bound). g_chi=0.4 gives
    σ/m(28) ~ 600 cm²/g (Cloud-9 upper bound). Both are well within
    the perturbative regime (g_chi < 4π ≈ 12.6).
    """
    g_lo = g_chi_to_match_sigma_m_0(50.0, 10, 500, v_ref_kms=28.0)
    g_hi = g_chi_to_match_sigma_m_0(500.0, 10, 500, v_ref_kms=28.0)
    assert g_lo is not None and g_hi is not None
    assert 0.1 < g_lo < 0.5, f"g_chi(50) = {g_lo}, expected 0.1-0.5"
    assert 0.3 < g_hi < 1.0, f"g_chi(500) = {g_hi}, expected 0.3-1.0"
    assert g_lo < 4 * np.pi and g_hi < 4 * np.pi, "both should be perturbative"
