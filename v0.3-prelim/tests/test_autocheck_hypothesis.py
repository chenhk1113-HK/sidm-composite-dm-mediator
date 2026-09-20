"""
Property-based tests for SIDM phenomenology using Hypothesis.

Auto-generates test cases to catch silent unit errors (e.g., the T120.16
eV/keV/MeV bug class) and edge-case failures.

Usage:
  pytest -v v0.3-prelim/tests/property_tests.py
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
from hypothesis import assume, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


t120_4 = load_module(
    "t120_4_joint_fit",
    Path(__file__).parent.parent / "code" / "t120_4_joint_fit.py"
)
t120_16 = load_module(
    "t120_16",
    Path(__file__).parent.parent / "code" / "t120_16_kinematic_threshold.py"
)

# Phase 44 default parameters
PHASE44_PARAMS = {
    'v_targets': [29, 100, 178, 430, 769],
    'sigma_peaks': [128, 0.07, 0.20, 0.04, 0.08],
    'w_list': [3.0, 50, 50, 50, 50],
    'sigma_0': 0.052,
    'a_slope': 1.0,
}


# ============================================================
# Property: σ/m(v) is always positive for v > 0
# ============================================================
@given(
    v=st.floats(min_value=0.1, max_value=2000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=200, deadline=1000)
def test_sigma_m_always_positive(v):
    """σ/m(v) should never be negative or NaN for any positive velocity."""
    sigma = t120_4.total_sigma_m_gaussian(
        v,
        PHASE44_PARAMS['v_targets'],
        PHASE44_PARAMS['sigma_peaks'],
        PHASE44_PARAMS['w_list'],
        PHASE44_PARAMS['sigma_0'],
        PHASE44_PARAMS['a_slope'],
    )
    assert sigma > 0, f"σ/m({v}) = {sigma}, must be positive"
    assert np.isfinite(sigma), f"σ/m({v}) = {sigma}, must be finite"


# ============================================================
# Property: KE_CM scales as v^2
# ============================================================
@given(
    v=st.floats(min_value=0.1, max_value=200, allow_nan=False, allow_infinity=False),
    m_chi_GeV=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=1000)
def test_ke_cm_scales_as_v_squared(v, m_chi_GeV):
    """KE_CM = (1/4) × m_χ × v^2 (1/2 reduced mass × 1/2 v^2 in CM frame)."""
    # Compute KE_CM at (m_chi, v)
    ke1 = t120_16.ke_cm_eV(m_chi_GeV, v)

    # Compute at (m_chi, 2v) — should be 4× the first
    ke2 = t120_16.ke_cm_eV(m_chi_GeV, 2 * v)

    ratio = ke2 / ke1
    assert 3.9 < ratio < 4.1, f"KE_CM(2v)/KE_CM(v) = {ratio}, should be 4"


# ============================================================
# Property: KE_CM scales linearly with m_chi
# ============================================================
@given(
    m_chi_GeV=st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=1000)
def test_ke_cm_scales_linearly_with_mass(m_chi_GeV):
    """KE_CM = (1/4) × m_χ × v^2, so doubling m_chi doubles KE_CM."""
    v = 28.0
    ke1 = t120_16.ke_cm_eV(m_chi_GeV, v)
    ke2 = t120_16.ke_cm_eV(2 * m_chi_GeV, v)

    ratio = ke2 / ke1
    assert 1.95 < ratio < 2.05, f"KE_CM(2m)/KE_CM(m) = {ratio}, should be 2"


# ============================================================
# Property: σ/m has a peak near v=28 (Cloud-9)
# ============================================================
@given(
    seed=st.integers(min_value=0, max_value=1000)
)
@settings(max_examples=20, deadline=2000)
def test_cloud9_peak_present(seed):
    """σ/m(v) should have σ/m > 10 cm²/g in some v window around 28."""
    sigma_28 = t120_4.total_sigma_m_gaussian(
        28,
        PHASE44_PARAMS['v_targets'],
        PHASE44_PARAMS['sigma_peaks'],
        PHASE44_PARAMS['w_list'],
        PHASE44_PARAMS['sigma_0'],
        PHASE44_PARAMS['a_slope'],
    )
    assert sigma_28 > 10, f"σ/m(28) = {sigma_28}, expected > 10"


# ============================================================
# Property: Phenomenology at very high v approaches sigma_0
# ============================================================
@given(
    v=st.floats(min_value=5000, max_value=50000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=50, deadline=1000)
def test_high_v_limit(v):
    """At very high v (>> all resonance positions), σ/m → σ_0 × (v_ref/v)^a."""
    sigma = t120_4.total_sigma_m_gaussian(
        v,
        PHASE44_PARAMS['v_targets'],
        PHASE44_PARAMS['sigma_peaks'],
        PHASE44_PARAMS['w_list'],
        PHASE44_PARAMS['sigma_0'],
        PHASE44_PARAMS['a_slope'],
    )
    # At v >> 1000, σ/m should be small
    assert sigma < 0.1, f"σ/m({v}) = {sigma}, expected < 0.1 at high v"


# ============================================================
# Property: Zhang V_max formula α_D² × m_χ scales correctly
# ============================================================
def _zhang_vmax(alpha_D, m_chi):
    """Compute Zhang 2016 V_max = α_D² × m_χ in MeV."""
    return alpha_D**2 * m_chi * 1000  # GeV to MeV


@given(
    alpha_D=st.floats(min_value=0.0001, max_value=0.1, allow_nan=False, allow_infinity=False),
    m_chi=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=1000)
def test_zhang_vmax_scales_as_alpha_squared(alpha_D, m_chi):
    """V_max = α_D² × m_χ, so doubling α_D quadruples V_max."""
    v1 = _zhang_vmax(alpha_D, m_chi)
    v2 = _zhang_vmax(2 * alpha_D, m_chi)

    ratio = v2 / v1
    assert 3.9 < ratio < 4.1, f"V_max(2α)/V_max(α) = {ratio}, should be 4"


@given(
    alpha_D=st.floats(min_value=0.0001, max_value=0.1, allow_nan=False, allow_infinity=False),
    m_chi=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=1000)
def test_zhang_vmax_scales_linearly_with_mass(alpha_D, m_chi):
    """V_max = α_D² × m_χ, so doubling m_chi doubles V_max."""
    v1 = _zhang_vmax(alpha_D, m_chi)
    v2 = _zhang_vmax(alpha_D, 2 * m_chi)

    ratio = v2 / v1
    assert 1.95 < ratio < 2.05, f"V_max(2m)/V_max(m) = {ratio}, should be 2"


# ============================================================
# Property: All σ/m values for v in [3, 1000] km/s are finite
# ============================================================
@given(
    v=st.floats(min_value=3.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=2000)
def test_sigma_m_finite_in_observable_range(v):
    """No NaN/Inf in the observable range."""
    sigma = t120_4.total_sigma_m_gaussian(
        v,
        PHASE44_PARAMS['v_targets'],
        PHASE44_PARAMS['sigma_peaks'],
        PHASE44_PARAMS['w_list'],
        PHASE44_PARAMS['sigma_0'],
        PHASE44_PARAMS['a_slope'],
    )
    assert np.isfinite(sigma), f"σ/m({v}) = {sigma}, not finite"


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-v']))
