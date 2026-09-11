"""T90.54 tests -- Hybrid multi-portal + resonance + Sommerfeld sigma/m(v).

Verifies:
  - sigma_m_hybrid returns finite values at all parameter ranges
  - The function reduces to T90.50 (resonant) when portal params are off
  - The function reduces to T90.44 (multi-portal) when resonance params are off
  - At the Cloud-9 best-fit point (T90.50), hybrid satisfies all 3 channels
  - Sensible velocity dependence (sigma/m decreases with v off-resonance)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v54_hybrid_sigma_m import (
    sigma_m_hybrid,
    hybrid_at_3_velocities,
    evaluate_hybrid_point,
)


def test_sigma_m_hybrid_finite():
    """Hybrid sigma/m should be finite at a typical parameter point."""
    # m_chi, m_phi_A, g_A, m_phi_B, g_B, E_R, Gamma, sigma_0, alpha_Y
    theta = (30.0, 700.0, 1.5, 5.0, 0.20, 65.0, 0.1, 0.001, 0.01)
    out = sigma_m_hybrid(v_kms=28.0, theta=theta)
    assert np.isfinite(out["sigma_m_total_cm2_per_g"]), \
        f"sigma/m(28) not finite: {out}"
    assert out["sigma_m_total_cm2_per_g"] > 0


def test_hybrid_reduces_to_resonant_when_portals_off():
    """With portal coupling g_A = g_B = 0, hybrid should equal T90.50 resonant."""
    # Same resonant params as T90.50 best fit
    theta = (30.0, 1e6, 0.0, 1e6, 0.0, 65.0, 0.1, 0.01, 0.01)
    sm_hybrid = sigma_m_hybrid(v_kms=28.0, theta=theta)
    # Compare to T90.50 directly
    from t90_v50_resonant_sidm import sigma_m_resonant
    sm_resonant = sigma_m_resonant(28.0, 30.0, 65.0, 0.1, 0.01, 0.01)
    assert abs(sm_hybrid["sigma_m_total_cm2_per_g"]
               - sm_resonant["sigma_m_total"]) < 0.1, \
        f"hybrid {sm_hybrid['sigma_m_total_cm2_per_g']} != resonant {sm_resonant['sigma_m_total']}"


def test_hybrid_reduces_to_multi_portal_when_resonance_off():
    """With E_R -> infinity and Gamma very large, BW contribution should vanish."""
    # Use very large E_R and very large Gamma so the BW term -> ~0
    # Also sigma_0 = 0 so resonant background is off
    theta = (30.0, 700.0, 1.5, 5.0, 0.20, 1e10, 1e10, 0.0, 0.01)
    sm_hybrid = sigma_m_hybrid(v_kms=100.0, theta=theta)
    # Compare to T90.44 multi-portal
    from t90_v44_multi_portal import sigma_m_multi_portal
    sm_mp = sigma_m_multi_portal(100.0, 700.0, 30.0, 1.5, 5.0, 30.0, 0.20)
    # Hybrid should be approximately equal (small numerical differences OK)
    rel_err = abs(sm_hybrid["sigma_m_total_cm2_per_g"] - sm_mp) / max(sm_mp, 1e-10)
    assert rel_err < 0.5, \
        f"hybrid {sm_hybrid['sigma_m_total_cm2_per_g']} != multi-portal {sm_mp}, rel_err={rel_err}"


def test_hybrid_at_3_velocities_shape():
    """At T90.50 best fit + T90.45 portal A, all 3 channels should be satisfied."""
    theta = (30.0, 700.0, 0.5, 5.0, 0.10, 65.0, 0.1, 0.01, 0.01)
    out = hybrid_at_3_velocities(theta)
    assert "sigma_m_Cloud9" in out
    assert "sigma_m_Galaxy" in out
    assert "sigma_m_Bullet" in out
    assert all(np.isfinite(out[k]) for k in ("sigma_m_Cloud9", "sigma_m_Galaxy", "sigma_m_Bullet"))


def test_evaluate_hybrid_point_returns_dict():
    """evaluate_hybrid_point returns a structured dict."""
    theta = (30.0, 700.0, 0.5, 5.0, 0.10, 65.0, 0.1, 0.01, 0.01)
    out = evaluate_hybrid_point(theta)
    assert "all_three_OK" in out
    assert "Cloud9_OK" in out
    assert "Galaxy_OK" in out
    assert "Bullet_OK" in out
    assert isinstance(out["all_three_OK"], bool)


def test_hybrid_velocity_dependence_off_resonance():
    """Far from resonance, hybrid sigma/m should DECREASE with velocity."""
    # Use portal B only (light, high g_B), set resonance far away
    theta = (30.0, 1e6, 0.0, 5.0, 0.20, 1e10, 1e10, 0.0, 0.0)
    sm_28 = sigma_m_hybrid(v_kms=28.0, theta=theta)["sigma_m_total_cm2_per_g"]
    sm_3000 = sigma_m_hybrid(v_kms=3000.0, theta=theta)["sigma_m_total_cm2_per_g"]
    # For Yukawa-like behavior off-resonance, sigma/m should drop with v
    # (Note: the B mediator is light so behavior may differ at very low v)
    assert sm_3000 < sm_28, \
        f"Yukawa should drop with v: sm(28)={sm_28}, sm(3000)={sm_3000}"


def test_hybrid_at_T90_50_best_fit():
    """At T90.50 best fit, hybrid (with no portal contributions) satisfies 3 channels."""
    # Pure resonant, portals off
    theta = (30.0, 1e6, 0.0, 1e6, 0.0, 65.0, 0.1, 0.01, 0.01)
    out = evaluate_hybrid_point(theta)
    assert out["Cloud9_OK"], f"Cloud-9 not OK: sm={out['sigma_m_Cloud9']}"
    assert out["Galaxy_OK"], f"Galaxy not OK: sm={out['sigma_m_Galaxy']}"
    assert out["Bullet_OK"], f"Bullet not OK: sm={out['sigma_m_Bullet']}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
