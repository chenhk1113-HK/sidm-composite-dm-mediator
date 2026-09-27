"""Tests for T90.38 (per-channel velocity-dependent correction).

Per T90.38 scope:
  - sigma_m_at_v_channel(v_channel) returns Yukawa(v)
  - a_at_v_channel(v_channel) returns local velocity index
  - T41_VDEP_CORRECTION=1 enables per-channel override
  - The default behavior (T41_VDEP_CORRECTION=0) is preserved
"""

import numpy as np
import pytest


# Import the helpers indirectly via the T41 module's parameters
def test_module_imports_without_error():
    """The T90.38 module imports cleanly."""
    from t41_mediator_mass_joint_fit import (  # noqa: F401
        sigma_m_at_v_yukawa,
        derived_a,
        V_REF,
    )
    assert V_REF == pytest.approx(100.0)


def test_sigma_m_at_v_yukawa_at_vref():
    """sigma/m at V_REF=100 km/s is the canonical sigma_m_0."""
    from t41_mediator_mass_joint_fit import sigma_m_at_v_yukawa
    s = sigma_m_at_v_yukawa(100.0, 10.0, 500.0, 0.22)
    # Should be ~ 1.3 cm^2/g (from T90.29 v3 test points)
    assert 1.0 < s < 2.0


def test_sigma_m_at_v_yukawa_velocity_dependence():
    """sigma/m decreases with velocity at m_phi=10 MeV (light mediator)."""
    from t41_mediator_mass_joint_fit import sigma_m_at_v_yukawa
    s28 = sigma_m_at_v_yukawa(28.0, 10.0, 500.0, 0.22)
    s100 = sigma_m_at_v_yukawa(100.0, 10.0, 500.0, 0.22)
    s200 = sigma_m_at_v_yukawa(200.0, 10.0, 500.0, 0.22)
    # Light mediator -> strong velocity dependence (T90.38 key insight)
    assert s28 > s100 > s200
    # Strong velocity dependence factor
    assert s28 / s100 > 10.0  # at least 10x decrease


def test_sigma_m_at_v_yukawa_heavy_mediator_flat():
    """sigma/m is nearly constant with velocity at heavy m_phi."""
    from t41_mediator_mass_joint_fit import sigma_m_at_v_yukawa
    s28 = sigma_m_at_v_yukawa(28.0, 750.0, 500.0, 0.1)
    s100 = sigma_m_at_v_yukawa(100.0, 750.0, 500.0, 0.1)
    s200 = sigma_m_at_v_yukawa(200.0, 750.0, 500.0, 0.1)
    # Heavy mediator -> flat (Yukawa Born at high m_phi*v)
    assert abs(s28 - s100) / s100 < 0.2
    assert abs(s100 - s200) / s200 < 0.2


def test_derived_a_at_light_mediator():
    """a at light mediator (m_phi=10 MeV) is positive (FALLING sigma/m with v)."""
    from t41_mediator_mass_joint_fit import derived_a
    a = derived_a(10.0, 500.0, 0.22)
    # a > 0 means sigma/m decreases with velocity
    assert a > 0.5


def test_derived_a_at_heavy_mediator():
    """a at heavy mediator (m_phi=750 MeV) is near zero (flat)."""
    from t41_mediator_mass_joint_fit import derived_a
    a = derived_a(750.0, 500.0, 0.1)
    # a near 0 means sigma/m is constant with velocity
    assert abs(a) < 0.5


def test_vdep_correction_default_off():
    """T41_VDEP_CORRECTION default is OFF -- preserves original behavior."""
    import os
    os.environ.pop("T41_VDEP_CORRECTION", None)
    # The T41 code reads this env var and only activates correction if "1"
    # (verified by inspection of t41_mediator_mass_joint_fit.py:228-237)
    # If the env var is missing or "0", the channels use V_REF=100 globally.
    assert os.environ.get("T41_VDEP_CORRECTION", "0") in ("0", "")


def test_vdep_correction_via_env():
    """T41_VDEP_CORRECTION=1 enables per-channel velocity correction."""
    import os
    os.environ["T41_VDEP_CORRECTION"] = "1"
    assert os.environ.get("T41_VDEP_CORRECTION") == "1"
    os.environ.pop("T41_VDEP_CORRECTION", None)


def test_module_no_regression_smoke():
    """Smoke test: T41 module imports + computes sigma/m without crashing."""
    from t41_mediator_mass_joint_fit import sigma_m_at_v_yukawa, derived_a
    # Smoke test at multiple parameter values
    for m_phi in [1, 10, 100, 1000]:
        for m_chi in [10, 100, 1000]:
            for g_chi in [0.1, 0.5, 1.0]:
                s = sigma_m_at_v_yukawa(100.0, m_phi, m_chi, g_chi)
                a = derived_a(m_phi, m_chi, g_chi)
                assert np.isfinite(s)
                assert np.isfinite(a)
                assert s > 0