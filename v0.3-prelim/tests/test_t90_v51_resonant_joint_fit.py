"""T90.51 tests -- Resonant SIDM joint posterior.

Covers:
  - Channel loglike shape (peak at expected value, 1-sided tail correct)
  - Joint loglike at the T90.50 best-fit point
  - Prior transform: unit cube -> physical, in-range
  - End-to-end smoke run at nlive=50
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v51_resonant_joint_fit import (
    loglike_cloud9,
    loglike_galaxy,
    loglike_bullet,
    loglike_resonant_3ch,
    prior_transform_6,
    LOG_RANGES,
    _CLOUD9_LOG_CENTER,
    _CLOUD9_LOG_WIDTH,
    _GAL_UPPER_LIMIT_LOG,
    _BUL_UPPER_LIMIT_LOG,
)


# ---------------------------------------------------------------------------
# Channel loglike tests
# ---------------------------------------------------------------------------
def test_cloud9_peak_at_geometric_mean():
    """Cloud-9 loglike is maximized at sigma/m = sqrt(30*500) ~ 122.5."""
    sm_peak = np.sqrt(30.0 * 500.0)
    ll_peak = loglike_cloud9(sm_peak)
    ll_low = loglike_cloud9(30.0)
    ll_high = loglike_cloud9(500.0)
    assert ll_peak > ll_low
    assert ll_peak > ll_high
    # At geometric mean, z=0, so loglike = 0 (up to constant)
    assert abs(ll_peak) < 1e-6, f"expected ~0, got {ll_peak}"


def test_cloud9_outside_range_penalized():
    """sigma/m(28) = 0.1 cm^2/g is way outside [30, 500]; loglike should be very negative."""
    ll = loglike_cloud9(0.1)
    assert ll < -5.0, f"expected strong penalty, got {ll}"


def test_galaxy_1sided_above_limit_penalized():
    """sigma/m(100) = 5 cm^2/g is above the <2 limit; loglike should be negative."""
    ll = loglike_galaxy(5.0)
    assert ll < 0.0
    # At limit: 0
    ll_at = loglike_galaxy(2.0)
    assert abs(ll_at) < 1e-6, f"expected ~0 at limit, got {ll_at}"
    # Below limit: 0
    ll_below = loglike_galaxy(1.0)
    assert abs(ll_below) < 1e-6


def test_bullet_1sided_above_limit_penalized():
    """sigma/m(3000) = 2 cm^2/g is above the <0.5 limit; loglike should be negative."""
    ll = loglike_bullet(2.0)
    assert ll < 0.0
    ll_at = loglike_bullet(0.5)
    assert abs(ll_at) < 1e-6


def test_galaxy_negative_rejected():
    """Physical sanity: negative sigma/m rejected (should not happen in practice)."""
    ll = loglike_galaxy(-1.0)
    assert ll == -np.inf


# ---------------------------------------------------------------------------
# Joint loglike at T90.50 best-fit
# ---------------------------------------------------------------------------
def test_joint_at_T90_50_best_fit():
    """At T90.50 best-fit, joint loglike should be close to 0 (within limit)."""
    bf = [30.0, 65.0, 0.1, 0.01, 0.01, 1.0]
    ll = loglike_resonant_3ch(bf)
    assert np.isfinite(ll), f"T90.50 best-fit should give finite ll, got {ll}"
    # Cloud-9: sigma/m(28) = 40.6 (in [30,500]), Gal: 0.94 (<2), Bul: 0.041 (<0.5)
    # -> all 3 channels at 0 loglike, so total ~ 0
    assert ll > -1.0, f"T90.50 best-fit should be highly compatible, got {ll}"


def test_joint_outside_priors_rejected():
    """Out-of-prior theta -> -inf."""
    # m_chi = 1e6 (way too heavy)
    bad = [1e6, 65.0, 0.1, 0.01, 0.01, 1.0]
    assert loglike_resonant_3ch(bad) == -np.inf
    # sigma_0 = 100 (way too large)
    bad = [30.0, 65.0, 0.1, 100.0, 0.01, 1.0]
    assert loglike_resonant_3ch(bad) == -np.inf


def test_joint_wrong_point_penalized():
    """A point with sigma/m(28)=1 cm^2/g (far below 30) should be heavily penalized."""
    bad = [30.0, 1e6, 0.1, 0.01, 0.01, 1.0]  # E_R way off, sigma/m(C9)~0
    ll = loglike_resonant_3ch(bad)
    assert ll < -5.0


# ---------------------------------------------------------------------------
# Prior transform
# ---------------------------------------------------------------------------
def test_prior_transform_in_range():
    """prior_transform_6 maps u in [0,1]^6 to physical values inside prior ranges."""
    rng = np.random.default_rng(42)
    for _ in range(100):
        u = rng.uniform(size=6)
        theta = prior_transform_6(u)
        for i in range(6):
            lo, hi = LOG_RANGES[i]
            assert lo <= np.log10(theta[i]) <= hi, \
                f"param {i}: log10(theta)={np.log10(theta[i])} outside [{lo},{hi}]"


def test_prior_transform_corners():
    """At u=0 and u=1, prior_transform returns the prior edges."""
    theta_lo = prior_transform_6(np.zeros(6))
    theta_hi = prior_transform_6(np.ones(6))
    for i in range(6):
        lo, hi = LOG_RANGES[i]
        # Allow tiny numerical tolerance
        assert abs(np.log10(theta_lo[i]) - lo) < 1e-9
        assert abs(np.log10(theta_hi[i]) - hi) < 1e-9


# ---------------------------------------------------------------------------
# End-to-end smoke test
# ---------------------------------------------------------------------------
def test_smoke_run():
    """Short dynesty run (nlive=50, dlogz=0.5) -- should complete and find a posterior
    that includes the T90.50 best-fit neighborhood.
    """
    from t90_v51_resonant_joint_fit import run_dynesty
    s = run_dynesty(nlive=50, dlogz=0.5)
    # Should produce finite log Z
    assert np.isfinite(s["log_Z"])
    # Posterior median sigma/m(Cloud-9) should be in or near [30, 500]
    pred = s["posterior_median_predictions"]
    sm_c9 = pred["sigma_m_Cloud9_cm2_per_g"]
    # Smoke run at nlive=50 may give noisy median; allow broader band
    assert 1.0 < sm_c9 < 5000.0, f"sm(Cloud-9) = {sm_c9} wildly off"
    # Galactic should respect <2 limit (median may be in tail)
    assert pred["sigma_m_Galaxy_cm2_per_g"] < 10.0
    # Bullet should be small
    assert pred["sigma_m_Bullet_cm2_per_g"] < 1.0
    # loglike at T90.50 best-fit point should be high
    assert s["best_fit_point_from_T90_50"]["loglike"] > -1.0


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
