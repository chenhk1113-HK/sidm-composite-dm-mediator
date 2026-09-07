"""
Tests for t90_v16_uv_completion.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_composite_d5_mu_x():
    """For D5 with r_12 = r_13 = 1, mu_D = mu_3 = mu_1."""
    from t90_v16_uv_completion import composite_dm_mu_x
    r = composite_dm_mu_x(
        m_chi_GeV=1000.0,
        m_constituent_GeV=333.0,
        mu_constituent_mu_B=1e-11,
        r_mass_ratios=(1.0, 1.0, 1.0),
        state='D5',
    )
    assert abs(r['mu_x_mu_B'] - 1e-11) / 1e-11 < 1e-6


def test_composite_d1_octet_formula():
    """mu_D1 = (1/3)(4 mu_1 - mu_2). With r_12 = 1: mu_D1 = (1/3)(4-1) mu_1 = mu_1."""
    from t90_v16_uv_completion import composite_dm_mu_x
    r = composite_dm_mu_x(
        m_chi_GeV=1000.0,
        m_constituent_GeV=333.0,
        mu_constituent_mu_B=1e-11,
        r_mass_ratios=(1.0, 1.0, 1.0),
        state='D1',
    )
    expected = (1.0/3.0) * (4 - 1) * 1e-11  # mu_2 = mu_1 since r=1
    assert abs(r['mu_x_mu_B'] - expected) / expected < 1e-6


def test_composite_dstar9_equals_3mu1():
    """mu_D*9 = 3 mu_1 (decuplet, all three q1 constituents)."""
    from t90_v16_uv_completion import composite_dm_mu_x
    r = composite_dm_mu_x(
        m_chi_GeV=1000.0,
        m_constituent_GeV=333.0,
        mu_constituent_mu_B=1e-11,
        r_mass_ratios=(1.0, 1.0, 1.0),
        state='D*9',
    )
    assert abs(r['mu_x_mu_B'] - 3e-11) / 3e-11 < 1e-6


def test_vectorlike_mu_x_scales_as_inv_M_psi():
    """In heavy mediator limit (M_psi >> m_chi), mu_x ~ 1/M_psi."""
    from t90_v16_uv_completion import vectorlike_fermion_mu_x
    r1 = vectorlike_fermion_mu_x(1.0, 1000.0, 10000.0)  # M_psi = 10 TeV
    r2 = vectorlike_fermion_mu_x(1.0, 1000.0, 20000.0)  # M_psi = 20 TeV
    # mu_x(20 TeV) / mu_x(10 TeV) ~ (10/20) = 0.5
    ratio = r2['mu_x_mu_B'] / r1['mu_x_mu_B']
    assert abs(ratio - 0.5) < 0.05, (
        f"Expected ratio ~0.5, got {ratio}"
    )


def test_vectorlike_mu_x_scales_as_g_Y_squared():
    """mu_x ~ g_Y^2."""
    from t90_v16_uv_completion import vectorlike_fermion_mu_x
    r1 = vectorlike_fermion_mu_x(1.0, 1000.0, 10000.0)
    r2 = vectorlike_fermion_mu_x(2.0, 1000.0, 10000.0)
    # mu_x(g_Y=2) / mu_x(g_Y=1) ~ 4
    ratio = r2['mu_x_mu_B'] / r1['mu_x_mu_B']
    assert abs(ratio - 4.0) < 0.1, (
        f"Expected ratio ~4, got {ratio}"
    )


def test_dark_photon_mu_x_scales_as_inv_M_A_prime_squared():
    """mu_x ~ 1/M_A'^2."""
    from t90_v16_uv_completion import dark_photon_mu_x
    r1 = dark_photon_mu_x(1e-4, 1.0, 1000.0, 100.0)   # M_A' = 100 GeV
    r2 = dark_photon_mu_x(1e-4, 1.0, 1000.0, 200.0)   # M_A' = 200 GeV
    ratio = r2['mu_x_mu_B'] / r1['mu_x_mu_B']
    assert abs(ratio - 0.25) < 0.01, (
        f"Expected ratio ~0.25 (1/4), got {ratio}"
    )


def test_unitarity_bound_at_lz():
    """At m_chi = 1 TeV, unitarity bound is mu_x < 20 m_e / 1 TeV = 1.02e-5 mu_B."""
    from t90_v16_uv_completion import unitarity_bound
    bound = unitarity_bound(1000.0)
    # 20 m_e / 1000 GeV = 20 * 5.11e-4 / 1000 = 1.022e-5
    assert abs(bound - 1.022e-5) / 1.022e-5 < 1e-3


def test_perturbative_bound_at_lz():
    """At m_chi = 1 TeV, perturbativity bound is mu_x < e / 1 TeV."""
    from t90_v16_uv_completion import perturbative_bound
    bound = perturbative_bound(1000.0)
    # sqrt(4*pi*alpha)/1000 = sqrt(4*pi/137.036)/1000 = 0.303/1000 = 3.03e-4
    assert abs(bound - 3.03e-4) / 3.03e-4 < 1e-2


def test_calibrate_composite_to_lz():
    """Composite calibration should reproduce LZ mu_x."""
    from t90_v16_uv_completion import calibrate_composite_to_lz
    r = calibrate_composite_to_lz(target_mu_x_mu_N=6.10e-8, m_chi_GeV=1000.0)
    assert abs(r['mu_x_mu_N'] - 6.10e-8) / 6.10e-8 < 1e-3


def test_calibrate_vectorlike_to_lz():
    """Vector-like calibration should reproduce LZ mu_x."""
    from t90_v16_uv_completion import calibrate_vectorlike_to_lz
    r = calibrate_vectorlike_to_lz(target_mu_x_mu_N=6.10e-8, m_chi_GeV=1000.0, g_Y=1.0)
    assert abs(r['mu_x_mu_N'] - 6.10e-8) / 6.10e-8 < 1e-3


def test_calibrate_dark_photon_to_lz():
    """Dark photon calibration should reproduce LZ mu_x."""
    from t90_v16_uv_completion import calibrate_dark_photon_to_lz
    r = calibrate_dark_photon_to_lz(target_mu_x_mu_N=6.10e-8, m_chi_GeV=1000.0,
                                       epsilon=1e-4, g_D=1.0)
    assert abs(r['mu_x_mu_N'] - 6.10e-8) / 6.10e-8 < 1e-3
