"""
Tests for t90_v15_indirect_signals.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))


def test_sigma_gamma_gamma_mu_x_squared_scaling():
    """sigma_gamma_gamma * v should scale as mu_x^2 (since it comes
    from a dipole-dipole squared amplitude)."""
    from t90_v15_indirect_signals import sigma_gamma_gamma_to_mu_x
    r1 = sigma_gamma_gamma_to_mu_x(1e-8, 1000.0)
    r2 = sigma_gamma_gamma_to_mu_x(2e-8, 1000.0)
    ratio = r2['sigma_v_cm3_s'] / r1['sigma_v_cm3_s']
    assert abs(ratio - 4.0) < 0.01, (
        f"Expected ratio = 4 (mu_x^2 scaling), got {ratio}"
    )


def test_sigma_gamma_gamma_mu_x_mu_N_squared_scaling():
    """sigma_gamma_gamma * v should scale as (mu_x_mu_N)^2.

    Since mu_x_natural = mu_x_mu_N * m_chi / m_e (linear in m_chi),
    and sigma ~ mu_x_natural^2 / m_chi^2 ~ mu_x_mu_N^2 * m_chi^2/m_e^2 / m_chi^2
    ~ mu_x_mu_N^2, the result scales as (mu_x_mu_N)^2 with NO m_chi dependence.
    """
    from t90_v15_indirect_signals import sigma_gamma_gamma_to_mu_x
    r1 = sigma_gamma_gamma_to_mu_x(1e-8, 1000.0)
    r2 = sigma_gamma_gamma_to_mu_x(1e-8, 2000.0)  # different m_chi, same mu_x_mu_N
    # sigma should be the same (no m_chi dependence in mu_x_mu_N units)
    ratio = r2['sigma_v_cm3_s'] / r1['sigma_v_cm3_s']
    assert abs(ratio - 1.0) < 0.01, (
        f"Expected same sigma for same mu_x_mu_N at different m_chi, got ratio = {ratio}"
    )


def test_gamma_ray_flux_proportional_to_j_factor():
    """Flux should scale linearly with J-factor."""
    from t90_v15_indirect_signals import gamma_ray_flux_at_earth
    sigma_v = 1e-30
    f1 = gamma_ray_flux_at_earth(sigma_v, 1000.0, 1e-23, target_mass_factor=1)
    f2 = gamma_ray_flux_at_earth(sigma_v, 1000.0, 2e-23, target_mass_factor=1)
    assert abs(f2['flux_photons_cm2_s'] / f1['flux_photons_cm2_s'] - 2.0) < 1e-6


def test_gamma_ray_flux_proportional_to_sigma_v():
    """Flux should scale linearly with sigma_v."""
    from t90_v15_indirect_signals import gamma_ray_flux_at_earth
    f1 = gamma_ray_flux_at_earth(1e-30, 1000.0, 1e-23, target_mass_factor=1)
    f2 = gamma_ray_flux_at_earth(2e-30, 1000.0, 1e-23, target_mass_factor=1)
    assert abs(f2['flux_photons_cm2_s'] / f1['flux_photons_cm2_s'] - 2.0) < 1e-6


def test_solar_capture_mu_x_squared_scaling():
    """Capture rate should scale as mu_x^2 (cross-section squared)."""
    from t90_v15_indirect_signals import solar_capture_rate_mu_x
    r1 = solar_capture_rate_mu_x(1e-8, 1000.0)
    r2 = solar_capture_rate_mu_x(2e-8, 1000.0)
    ratio = r2['capture_rate_per_s'] / r1['capture_rate_per_s']
    assert abs(ratio - 4.0) < 0.01, (
        f"Expected ratio = 4 (mu_x^2 scaling), got {ratio}"
    )


def test_solar_capture_inverse_mass():
    """Capture rate should scale as 1/m_chi (Griest-Seckel formula)."""
    from t90_v15_indirect_signals import solar_capture_rate_mu_x
    r1 = solar_capture_rate_mu_x(6.10e-8, 1000.0)
    r2 = solar_capture_rate_mu_x(6.10e-8, 2000.0)
    ratio = r2['capture_rate_per_s'] / r1['capture_rate_per_s']
    assert abs(ratio - 0.5) < 0.01, (
        f"Expected ratio = 0.5 (1/m_chi scaling), got {ratio}"
    )


def test_neutrino_flux_proportional_to_capture():
    """Neutrino flux should scale linearly with capture rate."""
    from t90_v15_indirect_signals import neutrino_flux_from_sun
    f1 = neutrino_flux_from_sun(1e20)
    f2 = neutrino_flux_from_sun(2e20)
    assert abs(f2['flux_per_GeV_per_cm2_per_s'] / f1['flux_per_GeV_per_cm2_per_s'] - 2.0) < 1e-6


def test_antiproton_flux_proportional_to_sigma_v():
    """Antiproton flux should scale linearly with sigma_v."""
    from t90_v15_indirect_signals import cosmic_ray_antiproton_flux
    f1 = cosmic_ray_antiproton_flux(1e-30, 1000.0)
    f2 = cosmic_ray_antiproton_flux(2e-30, 1000.0)
    assert abs(f2['flux_per_cm2_per_s_per_sr_per_GeV'] / f1['flux_per_cm2_per_s_per_sr_per_GeV'] - 2.0) < 1e-6


def test_lz_tuned_below_fermi_line_limit():
    """At LZ-tuned parameters, sigma_gamma_gamma should be below FERMI limit."""
    from t90_v15_indirect_signals import sigma_gamma_gamma_to_mu_x
    r = sigma_gamma_gamma_to_mu_x(6.10e-8, 1000.0)
    fermi_limit = 1e-30  # cm^3/s for m_chi ~ 1 TeV
    assert r['sigma_v_cm3_s'] < fermi_limit, (
        f"LZ-tuned sigma_gamma_gamma = {r['sigma_v_cm3_s']:.3e} cm^3/s "
        f"should be below FERMI line limit {fermi_limit:.3e}"
    )


def test_lz_tuned_below_icecube_limit():
    """At LZ-tuned parameters, solar neutrino flux should be below IceCube limit."""
    from t90_v15_indirect_signals import (
        solar_capture_rate_mu_x,
        neutrino_flux_from_sun,
    )
    capture = solar_capture_rate_mu_x(6.10e-8, 1000.0)
    flux = neutrino_flux_from_sun(capture['capture_rate_per_s'])
    icecube_limit = 1e4  # 1/GeV/cm^2/s
    assert flux['flux_per_GeV_per_cm2_per_s'] < icecube_limit, (
        f"LZ-tuned solar nu flux = {flux['flux_per_GeV_per_cm2_per_s']:.3e} "
        f"should be below IceCube limit {icecube_limit:.3e}"
    )
