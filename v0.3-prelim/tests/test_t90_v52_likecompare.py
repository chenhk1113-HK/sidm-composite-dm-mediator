"""T90.52 tests -- apples-to-apples log Z comparison (multi-portal vs resonant).

Covers:
  - loglike_multi_portal_3ch shape (matches T90.45 reference point)
  - prior_transform_9_mp in-range + corners
  - End-to-end smoke run (nlive=50) that completes and produces a posterior
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v52_likecompare import (
    loglike_multi_portal_3ch,
    prior_transform_9_mp,
    LOG_RANGES_MP,
    PARAM_NAMES_MP,
    IS_LOG_MP,
    run_multi_portal,
    compare_with_resonant,
)


def test_loglike_at_T90_45_reference():
    """At T90.45 reference point (m_phi_A=700, m_chi_A=100, g_A=1.5,
    m_phi_B=5, m_chi_B=500, g_B=0.20), joint loglike should be finite
    and the Cloud-9 channel should be reasonably compatible.
    """
    # T90.45 references: portal A (700, 100, 1.5), portal B (5, 500, 0.20)
    # nuisance params (eps_A, alpha_A, xi) arbitrary in 3-channel comparison
    theta = [
        np.log10(700.0), np.log10(100.0), 1.5,
        np.log10(5.0), np.log10(500.0), 0.20,
        -30.0, -10.0, 0.0,
    ]
    ll = loglike_multi_portal_3ch(theta)
    assert np.isfinite(ll), f"reference point should give finite ll, got {ll}"
    # T90.45 docs say this point gives sm(28)~50 -- in Cloud-9 range, so
    # the Cloud-9 channel contribution should be small (not heavily penalized).


def test_loglike_out_of_prior_rejected():
    """Out-of-prior theta -> -inf."""
    bad = [
        np.log10(700.0), np.log10(100.0), 1.5,
        np.log10(5.0), np.log10(500.0), 0.20,
        -100.0, -10.0, 0.0,  # eps_A = 1e-100 (way below -50)
    ]
    assert loglike_multi_portal_3ch(bad) == -np.inf


def test_loglike_zero_coupling_penalized():
    """g_chi = 0 -> zero sigma/m -> Cloud-9 channel strongly penalized."""
    theta = [
        np.log10(700.0), np.log10(100.0), 0.0,  # g_chi_A = 0
        np.log10(5.0), np.log10(500.0), 0.0,    # g_chi_B = 0
        -30.0, -10.0, 0.0,
    ]
    ll = loglike_multi_portal_3ch(theta)
    # Should be heavily negative (Cloud-9 channel penalty)
    assert ll < -5.0


def test_prior_transform_in_range():
    rng = np.random.default_rng(42)
    for _ in range(100):
        u = rng.uniform(size=9)
        theta = prior_transform_9_mp(u)
        for i in range(9):
            lo, hi = LOG_RANGES_MP[i]
            assert lo <= theta[i] <= hi, \
                f"param {i} ({PARAM_NAMES_MP[i]}): {theta[i]} outside [{lo},{hi}]"


def test_prior_transform_corners():
    theta_lo = prior_transform_9_mp(np.zeros(9))
    theta_hi = prior_transform_9_mp(np.ones(9))
    for i in range(9):
        lo, hi = LOG_RANGES_MP[i]
        assert abs(theta_lo[i] - lo) < 1e-9
        assert abs(theta_hi[i] - hi) < 1e-9


def test_smoke_run():
    """Short dynesty run -- should complete and produce finite log Z."""
    s = run_multi_portal(nlive=50, dlogz=0.5)
    assert np.isfinite(s["log_Z"])
    # Sigma/m predictions should be positive
    p = s["posterior_median_predictions"]
    assert p["sigma_m_Cloud9_cm2_per_g"] > 0
    assert p["sigma_m_Galaxy_cm2_per_g"] > 0
    assert p["sigma_m_Bullet_cm2_per_g"] > 0


def test_compare_returns_verdict():
    """compare_with_resonant loads the T90.51 JSON and returns a verdict string."""
    s = run_multi_portal(nlive=50, dlogz=0.5)
    cmp = compare_with_resonant(s)
    assert "delta_log_Z_resonant_minus_mp" in cmp
    assert cmp["verdict"] in [
        "VERY STRONG: resonant preferred (Jeffreys)",
        "STRONG: resonant preferred",
        "MODERATE: resonant preferred",
        "INCONCLUSIVE",
        "MULTI-PORTAL PREFERRED",
    ]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
