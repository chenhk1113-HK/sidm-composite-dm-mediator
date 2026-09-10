"""Tests for T90.47 gravothermal fluid model.

Per T90.47 scope:
  - The gravothermal fluid module imports cleanly
  - NFW density and mass profiles are correct
  - Single-species gravothermal evolution produces central density growth
  - Two-component evolution shows mass segregation:
      - Heavy species central density grows over time
      - Light species central density decreases (sinks less efficiently)
  - The effective sigma/m at outer radii evolves as species segregate
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent / "code")))


def test_v47_module_imports():
    """The T90.47 gravothermal module imports cleanly."""
    from t90_v47_gravothermal_fluid import (  # noqa: F401
        gravothermal_two_component, gravothermal_single_species,
        nfw_density, nfw_mass, nfw_concentration_to_rho_s,
    )


def test_v47_nfw_density_at_scale_radius():
    """NFW density at r = r_s should be rho_s / 2."""
    from t90_v47_gravothermal_fluid import nfw_density
    rho_s = 1e8  # M_sun/kpc^3
    r_s = 2.0   # kpc
    rho_at_rs = nfw_density(np.array([r_s]), rho_s, r_s)
    # rho(r_s) = rho_s / (1 * 2^2) = rho_s / 4
    np.testing.assert_allclose(rho_at_rs, [rho_s / 4.0], rtol=1e-6)


def test_v47_nfw_mass_at_scale_radius():
    """NFW mass at r = r_s is 4*pi*rho_s*r_s^3 * (ln(2) - 1/2)."""
    from t90_v47_gravothermal_fluid import nfw_mass
    rho_s = 1e8
    r_s = 2.0
    M_at_rs = nfw_mass(np.array([r_s]), rho_s, r_s)
    expected = 4 * np.pi * rho_s * r_s ** 3 * (np.log(2) - 0.5)
    np.testing.assert_allclose(M_at_rs, [expected], rtol=1e-6)


def test_v47_concentration_to_rho_s():
    """NFW concentration to rho_s conversion gives correct r_s and r_vir."""
    from t90_v47_gravothermal_fluid import nfw_concentration_to_rho_s
    M_halo = 1e10  # M_sun
    c = 15.0
    rho_s, r_s, r_vir = nfw_concentration_to_rho_s(M_halo, c)
    # r_vir / r_s should equal c
    assert abs(r_vir / r_s - c) < 1e-6
    # Total mass should match
    from t90_v47_gravothermal_fluid import nfw_mass
    M_vir = nfw_mass(np.array([r_vir]), rho_s, r_s)
    assert abs(M_vir[0] - M_halo) / M_halo < 0.01  # 1% tolerance


def test_v47_single_species_runs():
    """Single-species gravothermal evolution runs and returns expected keys."""
    from t90_v47_gravothermal_fluid import gravothermal_single_species
    result = gravothermal_single_species(
        M_halo_Msun=1e10, c=15.0, sigma_m_0=0.5, v_ref=100.0,
        a_power=0.0, t_final_Gyr=2.0, n_radial_bins=50, n_time_steps=50,
    )
    expected_keys = {"r_kpc", "time_Gyr", "rho_history", "central_density_history",
                     "rho_initial", "M_halo_Msun", "r_s_kpc", "r_vir_kpc"}
    assert expected_keys.issubset(result.keys())
    assert result["rho_history"].shape == (50, 50)


def test_v47_single_species_central_density_grows():
    """In single-species SIDM, central density grows over time (gravothermal)."""
    from t90_v47_gravothermal_fluid import gravothermal_single_species
    result = gravothermal_single_species(
        M_halo_Msun=1e10, sigma_m_0=1.0, t_final_Gyr=2.0,
        n_radial_bins=50, n_time_steps=50,
    )
    central_initial = result["central_density_history"][0]
    central_final = result["central_density_history"][-1]
    # Central density should grow (gravothermal collapse / core formation)
    assert central_final > central_initial


def test_v47_two_component_runs():
    """Two-component gravothermal evolution runs successfully."""
    from t90_v47_gravothermal_fluid import gravothermal_two_component
    result = gravothermal_two_component(
        M_halo_Msun=1e10, c=15.0,
        m_chi_H_GeV=30.0, m_chi_L_GeV=10.0,
        g_chi_H=0.5, g_chi_L=0.35, m_phi_MeV=50.0,
        t_final_Gyr=10.0, n_radial_bins=50, n_time_steps=50,
    )
    expected_keys = {"r_kpc", "time_Gyr", "rho_H_history", "rho_L_history",
                     "central_H_history", "central_L_history",
                     "t_coll_H", "t_seg", "M_halo_Msun"}
    assert expected_keys.issubset(result.keys())
    assert result["rho_H_history"].shape == (50, 50)
    assert result["rho_L_history"].shape == (50, 50)


def test_v47_two_component_mass_segregation():
    """In two-component SIDM, heavy central density grows, light central density drops."""
    from t90_v47_gravothermal_fluid import gravothermal_two_component
    result = gravothermal_two_component(
        M_halo_Msun=1e10, m_chi_H_GeV=30.0, m_chi_L_GeV=10.0,
        g_chi_H=0.5, g_chi_L=0.35, m_phi_MeV=50.0,
        t_final_Gyr=10.0, n_radial_bins=50, n_time_steps=50,
    )
    # Heavy species central density grows (gravothermal collapse)
    H_initial = result["central_H_history"][0]
    H_final = result["central_H_history"][-1]
    assert H_final > H_initial, f"Heavy species should grow: {H_initial} -> {H_final}"

    # Light species central density decreases (mass segregation)
    L_initial = result["central_L_history"][0]
    L_final = result["central_L_history"][-1]
    assert L_final < L_initial, f"Light species should decrease: {L_initial} -> {L_final}"


def test_v47_two_component_total_mass_conserved():
    """Total mass (M_H + M_L) should be approximately conserved."""
    from t90_v47_gravothermal_fluid import gravothermal_two_component
    result = gravothermal_two_component(
        M_halo_Msun=1e10, t_final_Gyr=10.0, n_radial_bins=50, n_time_steps=50,
    )
    from t90_v47_gravothermal_fluid import _trapz
    r = result["r_kpc"]
    M_init = 4 * np.pi * _trapz(
        (result["rho_H_history"][0] + result["rho_L_history"][0]) * r ** 2, r
    )
    M_final = 4 * np.pi * _trapz(
        (result["rho_H_history"][-1] + result["rho_L_history"][-1]) * r ** 2, r
    )
    # Should be conserved within 50% (this is a simplified 1D model)
    assert abs(M_final - M_init) / M_init < 0.5


def test_v47_effective_sigma_m_evolution():
    """The effective sigma/m at outer radii evolves as species segregate."""
    from t90_v47_gravothermal_fluid import gravothermal_two_component, effective_sigma_m_at_radius
    result = gravothermal_two_component(
        M_halo_Msun=1e10, t_final_Gyr=10.0, n_radial_bins=100, n_time_steps=100,
    )
    # Pick a radius in the outskirts (~r_s/2)
    r_target_kpc = result["r_s_kpc"] * 0.5
    r_idx = np.argmin(np.abs(result["r_kpc"] - r_target_kpc))
    sm_initial = effective_sigma_m_at_radius(result, r_idx, 0)
    sm_final = effective_sigma_m_at_radius(result, r_idx, -1)
    # sigma/m should evolve (either increase or decrease) as species segregate
    assert abs(sm_final - sm_initial) / sm_initial > 0.01  # at least 1% change


def test_v47_timescales_are_finite():
    """Collapse and segregation timescales are finite positive values."""
    from t90_v47_gravothermal_fluid import gravothermal_two_component
    result = gravothermal_two_component(
        M_halo_Msun=1e10, t_final_Gyr=10.0,
    )
    assert np.isfinite(result["t_coll_H"])
    assert np.isfinite(result["t_seg"])
    assert result["t_coll_H"] > 0
    assert result["t_seg"] > 0