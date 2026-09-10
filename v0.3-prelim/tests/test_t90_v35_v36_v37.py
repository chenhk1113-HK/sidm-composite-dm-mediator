"""Tests for T90.35 (Yang+ 2024 Cloud-9 likelihood), T90.36 (tuned
Yukawa), and T90.37 (Anand+ 2025 stellar mass cross-validation).
"""

import numpy as np
import pytest


# T90.35
from t90_v35_yang2024_cloud9 import (
    loglike_yang2024_cloud9,
    loglike_yang2024_t90v35,
    yukawa_to_yang_params,
    yang_sigma_eff_v,
    SIGMA_0_MODEL_I,
    W_MODEL_I,
    CLOUD9_TARGET_SIGMA_M_V28,
)


def test_yang2024_constants():
    """Yang+ 2024 Model I constants match the published Table 2.3."""
    assert SIGMA_0_MODEL_I == pytest.approx(147.1)
    assert W_MODEL_I == pytest.approx(24.33)


def test_yang_sigma_eff_velocity_independent():
    """w = inf gives velocity-independent sigma/m = sigma_0."""
    se = yang_sigma_eff_v(50.0, 28.0, np.inf)
    assert se == pytest.approx(50.0)


def test_yang_sigma_eff_velocity_dependent():
    """Yang+ form: sigma_eff(v) = sigma_0 / [1 + (v/w)^2]^2."""
    sigma_0 = 100.0
    w = 30.0  # km/s
    v = 28.0  # km/s
    expected = sigma_0 / (1 + (v/w) ** 2) ** 2
    se = yang_sigma_eff_v(sigma_0, v, w)
    assert se == pytest.approx(expected)


def test_loglike_yang2024_at_cloud9_lower_bound():
    """At sigma_eff(28) = 50 cm^2/g, log L should be near 0 (target hit)."""
    # (m_phi=10, m_chi=500, g_chi=0.22) gives Yukawa(28) = 50 cm^2/g
    ll = loglike_yang2024_cloud9(10.0, 500.0, 0.22)
    assert np.isfinite(ll)
    assert ll > -0.5  # close to 0 (perfect fit)


def test_loglike_yang2024_at_heavy_map():
    """At T41 v0.7 MAP (sigma_eff ~ 1e-6 cm^2/g), log L should be near -0.5."""
    ll = loglike_yang2024_cloud9(750.0, 500.0, 0.1)
    assert np.isfinite(ll)
    assert -1.0 < ll < -0.3


def test_loglike_yang2024_invalid_inputs():
    """NaN/zero/negative inputs handled gracefully."""
    assert loglike_yang2024_cloud9(np.nan, 500, 0.1) == 0.0
    assert loglike_yang2024_cloud9(10, np.nan, 0.1) == 0.0
    assert loglike_yang2024_cloud9(10, 500, np.nan) == 0.0
    assert loglike_yang2024_cloud9(-1, 500, 0.1) == 0.0
    assert loglike_yang2024_cloud9(10, -1, 0.1) == 0.0
    assert loglike_yang2024_cloud9(10, 500, -0.1) == 0.0


def test_loglike_yang2024_t90v35_5d():
    """T90.35 wrapper handles 5D theta."""
    theta_5d = (1.0, 2.0, 0.22, -30.0, -10.0)
    ll = loglike_yang2024_t90v35(theta_5d)
    assert np.isfinite(ll)


def test_loglike_yang2024_t90v35_6d():
    """T90.35 wrapper handles 6D theta."""
    theta_6d = (1.0, 2.0, 0.22, -30.0, -10.0, 0.0)
    ll = loglike_yang2024_t90v35(theta_6d)
    assert np.isfinite(ll)


# T90.36
from t90_v36_yukawa_tuned import (
    loglike_yukawa_tuned_t90v36,
    loglike_yukawa_tuned_t90v36_wrapper,
    CLOUD9_MID_TARGET_SIGMA_M_V28,
    CLOUD9_MID_TARGET_WIDTH,
)


def test_yukawa_tuned_target():
    """T90.36 targets Cloud-9 mid-range (150 cm^2/g, width 200)."""
    assert CLOUD9_MID_TARGET_SIGMA_M_V28 == pytest.approx(150.0)
    assert CLOUD9_MID_TARGET_WIDTH == pytest.approx(200.0)


def test_loglike_yukawa_tuned_aggressive():
    """Tuned aggressive (g_chi=1.3) gives sigma_eff ~ 390 cm^2/g, within Cloud-9 range."""
    ll = loglike_yukawa_tuned_t90v36(50.0, 100.0, 1.3)
    assert np.isfinite(ll)
    assert -1.0 < ll < 0.5  # reasonable likelihood


def test_loglike_yukawa_tuned_heavy_map():
    """T41 v0.7 MAP: heavy mediator, low sigma_eff, mild penalty."""
    ll = loglike_yukawa_tuned_t90v36(750.0, 500.0, 0.1)
    assert np.isfinite(ll)
    assert -1.0 < ll < 0.0


def test_loglike_yukawa_tuned_invalid_inputs():
    """Invalid inputs handled."""
    assert loglike_yukawa_tuned_t90v36(np.nan, 500, 0.1) == 0.0
    assert loglike_yukawa_tuned_t90v36(10, -1, 0.1) == 0.0
    assert loglike_yukawa_tuned_t90v36(10, 500, -0.1) == 0.0


# T90.37
from t90_v37_anand_mstar import (
    loglike_anand_mstar_t90v37,
    loglike_anand_mstar_t90v37_wrapper,
    ANAND_MSTAR_UPPER_LIMIT_MSUN,
    ANAND_CLOUD9_DM_PURE_THRESHOLD_SIGMA,
    ANAND_REWARD_CAP,
)


def test_anand_constants():
    """Anand+ 2025 constants: M_star < 10^3.5, threshold 50 cm^2/g."""
    assert ANAND_MSTAR_UPPER_LIMIT_MSUN == pytest.approx(10 ** 3.5)
    assert ANAND_CLOUD9_DM_PURE_THRESHOLD_SIGMA == pytest.approx(50.0)
    assert ANAND_REWARD_CAP == pytest.approx(2.0)


def test_loglike_anand_at_cloud9():
    """At Cloud-9 (sigma_eff ~ 50 cm^2/g), log L should be near 0 (threshold)."""
    ll = loglike_anand_mstar_t90v37(10.0, 500.0, 0.22)
    assert np.isfinite(ll)
    assert -0.5 < ll < 0.5


def test_loglike_anand_at_cloud9_high():
    """At sigma_eff ~ 500 cm^2/g, log L should be positive (reward)."""
    # Need a high sigma_eff point: m_phi=30, m_chi=50, g_chi=1.5
    ll = loglike_anand_mstar_t90v37(30.0, 50.0, 1.5)
    assert np.isfinite(ll)
    assert 0 < ll <= ANAND_REWARD_CAP


def test_loglike_anand_at_heavy_map():
    """At T41 v0.7 MAP (very low sigma_eff), log L should be negative (penalty)."""
    ll = loglike_anand_mstar_t90v37(750.0, 500.0, 0.1)
    assert np.isfinite(ll)
    assert ll < -2.0  # strong penalty for low sigma_eff


def test_loglike_anand_capped():
    """At very high sigma_eff, log L is capped at +ANAND_REWARD_CAP."""
    # Try a point with sigma_eff ~ 10^6 cm^2/g
    # m_phi=1, m_chi=10, g_chi=2 should give very high sigma
    ll = loglike_anand_mstar_t90v37(1.0, 10.0, 2.0)
    assert np.isfinite(ll)
    assert ll <= ANAND_REWARD_CAP + 0.01


def test_loglike_anand_invalid_inputs():
    """Invalid inputs handled."""
    assert loglike_anand_mstar_t90v37(np.nan, 500, 0.1) == 0.0
    assert loglike_anand_mstar_t90v37(10, np.nan, 0.1) == 0.0
    assert loglike_anand_mstar_t90v37(10, 500, np.nan) == 0.0
    assert loglike_anand_mstar_t90v37(-1, 500, 0.1) == 0.0


def test_loglike_anand_t90v37_wrapper_5d():
    """T90.37 wrapper handles 5D theta."""
    theta_5d = (1.0, 2.0, 0.22, -30.0, -10.0)
    ll = loglike_anand_mstar_t90v37_wrapper(theta_5d)
    assert np.isfinite(ll)


def test_loglike_anand_t90v37_wrapper_6d():
    """T90.37 wrapper handles 6D theta."""
    theta_6d = (1.0, 2.0, 0.22, -30.0, -10.0, 0.0)
    ll = loglike_anand_mstar_t90v37_wrapper(theta_6d)
    assert np.isfinite(ll)