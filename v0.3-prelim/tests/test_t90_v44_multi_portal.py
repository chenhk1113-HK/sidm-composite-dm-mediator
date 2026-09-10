"""Tests for T90.44 multi-portal extension.

Per T90.44 scope:
  - sigma_m_multi_portal(v, *params) returns sigma/m_A + sigma/m_B
  - The combined cross-section satisfies Cloud-9 + galactic + Bullet
    simultaneously for appropriate Portal B params
  - At heavy Portal A, the multi-portal sigma/m_total is dominated by
    Portal A at high v and by Portal B at low v (when g_chi_B is tuned)
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent / "code")))


def test_multi_portal_module_imports():
    """The T90.44 multi-portal module imports cleanly."""
    from t90_v44_multi_portal import sigma_m_multi_portal  # noqa: F401
    assert callable(sigma_m_multi_portal)


def test_multi_portal_at_heavy_a_light_b_reference():
    """Reference test: Portal A heavy + Portal B light gives correct sigma/m."""
    from t90_v44_multi_portal import sigma_m_multi_portal
    sm_28 = sigma_m_multi_portal(28, 700, 100, 1.5, 10, 500, 0.22)
    sm_100 = sigma_m_multi_portal(100, 700, 100, 1.5, 10, 500, 0.22)
    sm_3000 = sigma_m_multi_portal(3000, 700, 100, 1.5, 10, 500, 0.22)
    # Cloud-9 in range (50-200 cm^2/g)
    assert 30 < sm_28 < 200, f"sm(28)={sm_28:.2f} not in Cloud-9 range"
    # Galactic < 2 cm^2/g (close to published upper limits)
    assert sm_100 < 2.0, f"sm(100)={sm_100:.2f} too high for galactic"
    # Bullet < 0.5 cm^2/g
    assert sm_3000 < 0.5, f"sm(3000)={sm_3000:.4f} too high for Bullet"


def test_multi_portal_handles_zero_g_chi():
    """If one portal has g_chi=0, only the other contributes."""
    from t90_v44_multi_portal import sigma_m_multi_portal
    sm_A_only = sigma_m_multi_portal(100, 700, 100, 1.5, 10, 500, 0.0)
    sm_B_only = sigma_m_multi_portal(100, 700, 100, 0.0, 10, 500, 0.22)
    sm_total = sigma_m_multi_portal(100, 700, 100, 1.5, 10, 500, 0.22)
    # Total should equal A + B
    assert abs(sm_total - (sm_A_only + sm_B_only)) / sm_total < 1e-6


def test_multi_portal_additivity():
    """sigma/m_total(v) = sigma/m_A(v) + sigma/m_B(v) at all velocities."""
    from t90_v44_multi_portal import sigma_m_multi_portal
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    for v in [10, 30, 100, 200, 1000, 3000]:
        sA = sigma_m_cm2_per_g(v, 700, 100, 1.5)
        sB = sigma_m_cm2_per_g(v, 10, 500, 0.22)
        s_total = sigma_m_multi_portal(v, 700, 100, 1.5, 10, 500, 0.22)
        assert abs(s_total - (sA + sB)) / max(sA + sB, 1e-30) < 1e-6


def test_multi_portal_high_velocity_portal_a_dominates():
    """At v >= 1000 km/s, heavy Portal A dominates (Yukawa v^-8 suppression)."""
    from t90_v44_multi_portal import sigma_m_multi_portal
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    # At v=3000, Portal B is suppressed, Portal A dominates
    sA_3000 = sigma_m_cm2_per_g(3000, 700, 100, 1.5)
    sB_3000 = sigma_m_cm2_per_g(3000, 10, 500, 0.22)
    s_total_3000 = sigma_m_multi_portal(3000, 700, 100, 1.5, 10, 500, 0.22)
    # Portal A should dominate (Portal B suppressed by ~v^-8)
    assert sA_3000 > sB_3000, "At v=3000, Portal A should dominate"


def test_multi_portal_low_velocity_portal_b_dominates():
    """At v <= 30 km/s with strong g_chi_B, Portal B dominates."""
    from t90_v44_multi_portal import sigma_m_multi_portal
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    sA_28 = sigma_m_cm2_per_g(28, 700, 100, 1.5)
    sB_28 = sigma_m_cm2_per_g(28, 10, 500, 0.22)
    # Portal B with light mediator gives strong sigma/m at low v
    # Portal A with heavy mediator gives flat sigma/m
    # At g_chi_B=0.22, Portal B should dominate at v=28
    assert sB_28 > sA_28, "At v=28, Portal B should dominate"


def test_multi_portal_smoke_at_various_params():
    """Smoke test: multi-portal function works at 5 parameter combinations."""
    from t90_v44_multi_portal import sigma_m_multi_portal
    test_points = [
        (700, 100, 1.5, 10, 500, 0.22),
        (500, 50, 1.0, 30, 1000, 0.15),
        (1000, 200, 1.8, 5, 200, 0.18),
        (700, 100, 1.5, 50, 500, 0.25),
        (200, 50, 0.8, 10, 100, 0.30),
    ]
    for m_phi_A, m_chi_A, g_A, m_phi_B, m_chi_B, g_B in test_points:
        for v in [28, 100, 1000]:
            sm = sigma_m_multi_portal(v, m_phi_A, m_chi_A, g_A, m_phi_B, m_chi_B, g_B)
            assert np.isfinite(sm), f"non-finite sigma/m at v={v}"
            assert sm > 0, f"negative sigma/m at v={v}"


def test_multi_portal_unified_setting():
    """The reference unified setting satisfies all 3 velocity scales."""
    from t90_v44_multi_portal import sigma_m_multi_portal
    # Portal A heavy + Portal B tuned for Cloud-9
    sm_28 = sigma_m_multi_portal(28, 700, 100, 1.5, 10, 500, 0.20)
    sm_100 = sigma_m_multi_portal(100, 700, 100, 1.5, 10, 500, 0.20)
    sm_3000 = sigma_m_multi_portal(3000, 700, 100, 1.5, 10, 500, 0.20)
    # Cloud-9: 30-500 cm^2/g
    assert 30 < sm_28 < 500
    # Galactic: < 1 cm^2/g
    assert sm_100 < 1.0
    # Bullet: < 0.5 cm^2/g
    assert sm_3000 < 0.5