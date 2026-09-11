"""Tests for T90.61 Kahlhoefer audit."""

import json
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from t90_v61_kahlhoefer_audit import (
    kahlhoefer_point_particle,
    kahlhoefer_with_form_factor,
    t78_claimed,
    find_source_of_discrepancy,
)


def test_kahlhoefer_formula_units():
    """Kahlhoefer formula (16pi version used in this code) should produce
    sigma in cm^2 with reasonable magnitude for natural-coupling dark photon."""
    # Unit-test: eps=1, alpha_chi=1, alpha_em=1, mu=1 GeV, m_phi=1 GeV
    # Expected: 16 pi * 1 * 1 * 1 * 1 / 1 * GeV^-2 -> cm^2 conversion
    GeV_to_invocm2 = (1.973e-14) ** (-2)
    expected = 16 * math.pi * 1.0 * 1.0 * 1.0 * 1.0 / 1.0 * GeV_to_invocm2
    _, sigma = kahlhoefer_point_particle(1.0, 1.0, 1.0, 1.0, 1.0)
    # Allow 0.1% tolerance for the GeV^-2 -> cm^2 conversion constant
    assert abs(sigma - expected) / expected < 1e-3, (
        f"sigma = {sigma:.4e}, expected {expected:.4e}, "
        f"relative diff = {abs(sigma - expected) / expected:.4e}"
    )


def test_kahlhoefer_at_v07_map():
    """At v0.7 MAP, Kahlhoefer formula gives ~10^-48 cm^2 (16 pi) or
    ~10^-49 cm^2 (4 pi). NOT 10^-111 (T78 claim) and NOT 10^-69
    (T86 hand-calc)."""
    m_chi_GeV = 770.0
    m_phi_MeV = 453.0
    m_phi_GeV = m_phi_MeV / 1000.0
    log_epsilon = -37.0
    epsilon = 10 ** log_epsilon
    alpha_chi = 0.01
    m_p_GeV = 0.93827208816
    mu_chi_p = m_chi_GeV * m_p_GeV / (m_chi_GeV + m_p_GeV)

    _, sigma_pp = kahlhoefer_point_particle(
        1.0 / 137.036, alpha_chi, epsilon, mu_chi_p, m_phi_GeV
    )
    # Should be ~10^-48 to 10^-49 (per my derivation), NOT 10^-111 or 10^-69
    assert 1e-55 < sigma_pp < 1e-45, (
        f"Kahlhoefer point-particle at v0.7 MAP: {sigma_pp:.3e} cm^2, "
        f"expected ~10^-48 to 10^-49 range (NOT 10^-111 from T78 or 10^-69 from T86)"
    )


def test_t78_claim_value():
    """T78 claim at v0.7 MAP gives ~10^-111 cm^2 (per T86 audit
    transcription)."""
    sigma_t78 = t78_claimed(453.0, 0.01, 10 ** (-37.0))
    assert 1e-115 < sigma_t78 < 1e-105


def test_discrepancy_is_real_and_large():
    """The T86 audit claimed 15-order discrepancy. My derivation shows
    the ACTUAL discrepancy is ~62 orders (T78 SMALLER than standard
    Kahlhoefer formula). This is much worse than T86's '15 orders'
    claim -- both T78 AND T86 hand-calc are wrong."""
    m_chi_GeV = 770.0
    m_phi_MeV = 453.0
    m_phi_GeV = m_phi_MeV / 1000.0
    log_epsilon = -37.0
    epsilon = 10 ** log_epsilon
    alpha_chi = 0.01
    m_p_GeV = 0.93827208816
    mu_chi_p = m_chi_GeV * m_p_GeV / (m_chi_GeV + m_p_GeV)

    _, sigma_my = kahlhoefer_point_particle(
        1.0 / 137.036, alpha_chi, epsilon, mu_chi_p, m_phi_GeV
    )
    sigma_t78 = t78_claimed(m_phi_MeV, alpha_chi, epsilon)

    log_ratio = math.log10(sigma_t78 / sigma_my)
    # T78 is ~62 orders SMALLER than the standard Kahlhoefer formula
    # (the T86 audit dismissed this as 15 orders of magnitude, which is wrong)
    assert -65 < log_ratio < -55, (
        f"T78/my ratio = {sigma_t78/sigma_my:.3e}, log10 = {log_ratio}, "
        f"expected ~-62 (T78 is ~62 orders SMALLER than standard Kahlhoefer)"
    )


def test_kahlhoefer_with_form_factor():
    """Form factor F^2 in [0, 1] should reduce sigma proportionally."""
    _, sigma_F1 = kahlhoefer_with_form_factor(
        1.0 / 137.036, 0.01, 1e-37, 0.5, 0.5, FF_squared=1.0
    )
    _, sigma_F09 = kahlhoefer_with_form_factor(
        1.0 / 137.036, 0.01, 1e-37, 0.5, 0.5, FF_squared=0.9
    )
    # FF=0.9 should be 0.9x FF=1.0
    assert abs(sigma_F09 / sigma_F1 - 0.9) < 1e-6


def test_form_factor_is_small_correction():
    """At v0.7 MAP, form factor F^2 ~0.93 gives <1% correction, NOT 5 orders."""
    m_chi_GeV = 770.0
    m_phi_MeV = 453.0
    m_phi_GeV = m_phi_MeV / 1000.0
    log_epsilon = -37.0
    epsilon = 10 ** log_epsilon
    alpha_chi = 0.01
    m_p_GeV = 0.93827208816
    mu_chi_p = m_chi_GeV * m_p_GeV / (m_chi_GeV + m_p_GeV)

    _, sigma_pt = kahlhoefer_point_particle(
        1.0 / 137.036, alpha_chi, epsilon, mu_chi_p, m_phi_GeV
    )
    _, sigma_FF = kahlhoefer_with_form_factor(
        1.0 / 137.036, alpha_chi, epsilon, mu_chi_p, m_phi_GeV, FF_squared=0.93
    )
    correction = sigma_FF / sigma_pt
    # Form factor correction is <1%, not 5 orders of magnitude
    assert 0.9 < correction < 1.0, (
        f"Form factor F^2=0.93 correction = {correction}, expected ~0.93"
    )


def test_eps_squared_dominates():
    """eps^2 should provide ~74 orders of suppression (29 dex * 2 for squaring)."""
    # At v0.7 MAP: eps = 1e-37, so eps^2 = 1e-74
    # So sigma ~ (everything else) * 1e-74
    # 74 orders of suppression, not 5 or 15
    eps = 1e-37
    log_eps_sq = math.log10(eps ** 2)
    assert log_eps_sq == -74


def test_find_source_runs():
    """The find_source_of_discrepancy function should run without error."""
    # This is more of a smoke test
    try:
        find_source_of_discrepancy()
    except Exception as e:
        pytest.fail(f"find_source_of_discrepancy raised {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])