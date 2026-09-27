"""Tests for T90.32 population-level RELHIC likelihood.

Per T90.32 scope:
  - Monaci+ 2026 70-candidate catalog statistics
  - RELHIC survival bound ~ 100 cm^2/g (back-of-envelope)
  - Gaussian penalty at sigma_m > survival bound
"""

import numpy as np
import pytest

# Import the T90.32 module
from t90_v32_relhic_population import (
    loglike_relhic_population_monaci2026,
    loglike_relhic_population_t90v32,
    OBSERVED_DGC_COUNT,
    SURVIVAL_BOUND_SIGMA_M_CM2_PER_G,
    MEDIAN_LOG_M_HI,
    MEDIAN_W50_KM_S,
    MEDIAN_V_CIRC_KM_S,
)


def test_module_constants():
    """T90.32 module constants match Monaci+ 2026 published values."""
    assert OBSERVED_DGC_COUNT == 70
    assert SURVIVAL_BOUND_SIGMA_M_CM2_PER_G == pytest.approx(100.0)
    # Median log M_HI ~ 7.8 from Monaci+ 2026 (Section 5.2)
    assert MEDIAN_LOG_M_HI == pytest.approx(7.8)
    # Median W50 ~ 70 km/s
    assert MEDIAN_W50_KM_S == pytest.approx(70.0)
    # Median V_circ ~ 35 km/s
    assert MEDIAN_V_CIRC_KM_S == pytest.approx(35.0)


def test_pop_likelihood_heavy_mediator():
    """Heavy-mediator MAP (low sigma_m): no penalty."""
    # T41 v0.7 MAP: m_phi=750 MeV, m_chi=500 GeV, g_chi=0.1 -> sigma_m ~ 1e-6
    ll = loglike_relhic_population_monaci2026(750, 500, 0.1)
    assert np.isfinite(ll)
    # At sigma_m = 1e-6 cm^2/g, log L = -0.5 * (1e-6/100)^2 ~ 0
    assert ll > -0.01


def test_pop_likelihood_cloud9_regime():
    """Cloud-9 regime (sigma_m ~ 50 cm^2/g): small penalty."""
    # m_phi=10 MeV, m_chi=500 GeV, g_chi=0.22 -> sigma_m ~ 50 cm^2/g
    ll = loglike_relhic_population_monaci2026(10, 500, 0.22)
    # log L = -0.5 * (50/100)^2 = -0.125
    assert np.isfinite(ll)
    assert -0.3 < ll < -0.05


def test_pop_likelihood_high_sigma_m_evaporation():
    """Very high sigma_m (>100 cm^2/g): severe penalty (clouds evaporate)."""
    # m_phi=1 MeV, g_chi=0.5 -> sigma_m ~ 10^4 cm^2/g (way over the bound)
    ll = loglike_relhic_population_monaci2026(1, 500, 0.5)
    assert ll < -100  # Severe penalty


def test_pop_likelihood_invalid_inputs():
    """Invalid inputs (NaN, zero, negative): gracefully handled."""
    assert loglike_relhic_population_monaci2026(np.nan, 500, 0.1) == 0.0
    assert loglike_relhic_population_monaci2026(10, np.nan, 0.1) == 0.0
    assert loglike_relhic_population_monaci2026(10, 500, np.nan) == 0.0
    assert loglike_relhic_population_monaci2026(-1, 500, 0.1) == 0.0
    assert loglike_relhic_population_monaci2026(10, -1, 0.1) == 0.0
    assert loglike_relhic_population_monaci2026(10, 500, -0.1) == 0.0


def test_t90v32_wrapper_5d():
    """T90.32 wrapper handles 5D theta tuples (T41 v0.5 compat)."""
    # log_m_phi=1, log_m_chi=2, g_chi=0.5, log_eps=-30, log_alpha=-10
    # -> m_phi=10 MeV, m_chi=100 GeV
    theta_5d = (1.0, 2.0, 0.5, -30.0, -10.0)
    ll = loglike_relhic_population_t90v32(theta_5d)
    assert np.isfinite(ll)


def test_t90v32_wrapper_6d():
    """T90.32 wrapper handles 6D theta tuples (T41 v0.6 canonical)."""
    # log_m_phi=1, log_m_chi=2, g_chi=0.5, log_eps=-30, log_alpha=-10, log_xi=0
    theta_6d = (1.0, 2.0, 0.5, -30.0, -10.0, 0.0)
    ll = loglike_relhic_population_t90v32(theta_6d)
    assert np.isfinite(ll)


def test_t90v32_wrapper_invalid_inputs():
    """T90.32 wrapper gracefully handles invalid inputs."""
    assert loglike_relhic_population_t90v32((np.nan, 2.0, 0.5, -30.0, -10.0)) == 0.0
    assert loglike_relhic_population_t90v32((1.0, np.nan, 0.5, -30.0, -10.0)) == 0.0
    assert loglike_relhic_population_t90v32((1.0, 2.0, np.nan, -30.0, -10.0)) == 0.0


def test_pop_likelihood_monotonic_with_sigma_m():
    """log L pop decreases monotonically as sigma_m increases (above bound)."""
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g

    # Sweep g_chi at fixed m_phi=10 MeV, m_chi=500 GeV to span sigma_m range
    sigma_ms = []
    lls = []
    for g_chi in [0.1, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
        sm = sigma_m_cm2_per_g(28.0, 10.0, 500.0, g_chi)
        ll = loglike_relhic_population_monaci2026(10.0, 500.0, g_chi)
        sigma_ms.append(sm)
        lls.append(ll)

    # Filter to only the points above the survival bound (sigma_m > 100)
    above_bound = [(sm, ll) for sm, ll in zip(sigma_ms, lls) if sm > 100]
    if len(above_bound) >= 2:
        # log L should be decreasing (more negative) as sigma_m grows
        for i in range(1, len(above_bound)):
            assert above_bound[i][1] < above_bound[i-1][1]


def test_pop_likelihood_weight_scales_correctly():
    """Weight parameter scales the log-likelihood linearly."""
    ll1 = loglike_relhic_population_monaci2026(10, 500, 0.22, weight=1.0)
    ll2 = loglike_relhic_population_monaci2026(10, 500, 0.22, weight=2.0)
    assert np.isfinite(ll1) and np.isfinite(ll2)
    assert ll2 == pytest.approx(2.0 * ll1)