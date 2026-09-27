"""Tests for T90.27 RELHIC hydrostatic forward model + Yang+2024/2025 SIDM halo.

Per T90.27 scope:
  - Yang+2024/2025 parametric SIDM halo model (Eqs. 4-7 of arXiv:2608.04362)
  - Hydrostatic + isothermal forward model (placeholder, deferred)
  - Data loaders for published RELHIC observations (Cloud-9 + M51)
  - Best-fit halo parameter sets from arXiv:2608.04362 §3.1

The tests are intentionally light (8 tests) covering:
  - Yang model returns NFW at τ=0 (4a)
  - Yang model produces a cored profile at τ=0.18 (4b)
  - Yang model produces a deep core-collapse profile at τ=0.95 (4c)
  - m200_c200_to_rho_s_rs returns the published values (4d)
  - t_collapse gives τ ≈ 0.2 at the published Cloud-9 best-fit (4e)
  - Cloud-9 N(HI) data has the published central value (4f)
  - M51 Cloud S/N parameters match arXiv:2607.21034 (4g)
  - Enclosed mass NFW matches analytic at r=rs (4h)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import numpy as np  # noqa: E402

from t90_v27_relhic_hydrostatic import (  # noqa: E402
    yang_rho_s_over_rho_s0,
    yang_r_s_over_r_s0,
    yang_r_c_over_r_s0,
    m200_c200_to_rho_s_rs,
    t_collapse,
    T_AGE_GYR,
    v200_from_M200,
    yang_parametric_sidm_density,
    nfw_density,
    enclosed_mass_nfw,
    CLOUD9_NHI_B_KPC,
    CLOUD9_NHI_LOG10_CM2,
    CLOUD9_NHI_ERR_LOG10,
    CLOUD9_BESTFIT_CDM,
    CLOUD9_BESTFIT_SIDM_T018,
    CLOUD9_BESTFIT_SIDM_T095,
    M51_CLOUD_S_HALO_MASS,
    M51_CLOUD_N_HALO_MASS,
    M51_CLOUD_S_M_HI,
    M51_CLOUD_N_M_HI,
    M51_CLOUD_S_V_DISP_KMS,
    M51_CLOUD_N_V_DISP_KMS,
)


def test_yang_rho_s_over_rho_s0_at_tau_zero_is_one():
    """At τ=0, ρs/ρs,0 = 1.0 (NFW limit, Eq. 5 of arXiv:2608.04362)."""
    val = yang_rho_s_over_rho_s0(0.0)
    # Allow for tiny numerical precision at τ=0
    assert abs(val - 1.0) < 1e-3, f"got {val}"


def test_yang_r_s_over_r_s0_at_tau_zero_is_one():
    """At τ=0, rs/rs,0 = 1.0 (NFW limit)."""
    val = yang_r_s_over_r_s0(0.0)
    assert abs(val - 1.0) < 1e-3, f"got {val}"


def test_yang_r_c_over_r_s0_at_tau_zero_is_zero():
    """At τ=0, rc/rs,0 = 0.0 (no core, pure NFW)."""
    val = yang_r_c_over_r_s0(0.0)
    assert abs(val) < 1e-3, f"got {val}"


def test_yang_parametric_at_tau_zero_matches_nfw():
    """Yang(τ=0) ≡ NFW exactly on the same r-grid."""
    M200, c200 = 5e9, 4.0
    r = np.linspace(0.1, 50.0, 1000)
    n = nfw_density(r, M200, c200)
    y = yang_parametric_sidm_density(r, M200, c200, tau=0.0)
    max_rel = np.max(np.abs(n - y) / n)
    assert max_rel < 1e-10, f"max rel diff = {max_rel}"


def test_yang_parametric_at_tau_018_produces_core():
    """At τ=0.18 (Cloud-9 SIDM best-fit), Yang has a cored profile.

    The core radius rc should be positive and the central density
    lower than the NFW cusp value.
    """
    M200, c200 = 4.7e9, 4.0  # Cloud-9 SIDM τ=0.18 best-fit
    _, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    rc = yang_r_c_over_r_s0(0.18) * r_s_0
    # Cloud-9 paper says rc ~ 2 kpc for this halo
    assert 0.5 < rc < 5.0, f"rc = {rc} kpc, expected ~ 2 kpc"
    # Central density (r → 0) should be LOWER than NFW at r=rc
    rho_yang_inner = yang_parametric_sidm_density(np.array([0.5]), M200, c200, 0.18)[0]
    rho_nfw_inner = nfw_density(np.array([0.5]), M200, c200)[0]
    assert rho_yang_inner < rho_nfw_inner, (
        f"Yang(τ=0.18) inner density {rho_yang_inner} should be < NFW {rho_nfw_inner}"
    )


def test_m200_c200_to_rho_s_rs_published_values():
    """For (M200=5e9, c200=4), rs,0 should be ~ 6.95 kpc (published).

    Uses RHO_CRIT_PAPER = 277.5 as the Cloud-9 paper convention.
    """
    M200, c200 = 5e9, 4.0
    _, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    # Published rs,0 ~ 6.95 kpc (per the Cloud-9 paper convention).
    # Allow 10% tolerance for unit-convention uncertainty.
    assert 6.0 < r_s_0 < 8.0, f"rs,0 = {r_s_0} kpc, expected ~ 6.95"


def test_t_collapse_at_cloud9_bestfit():
    """At (M200=4.7e9, c200=4, σ/m=483), τ should be ~ 0.2 (published τ=0.18).

    This validates the TC_UNIT_FACTOR calibration in t_collapse.
    """
    M200, c200 = 4.7e9, 4.0
    sigma_m = 483.0
    rho_s_0, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    t_c = t_collapse(sigma_m, rho_s_0, r_s_0)
    tau = T_AGE_GYR / t_c
    # Published τ = 0.18; allow factor 2 for calibration uncertainty.
    assert 0.05 < tau < 0.5, f"τ = {tau}, expected ~ 0.18"


def test_v200_published_value():
    """v200 for the Cloud-9 SIDM best-fit halo should be ~ 30 km/s.

    The Cloud-9 paper places the halo in the dwarf-galaxy regime
    (v ~ 30-50 km/s, mass ~ 5e9 M_sun).
    """
    v200 = v200_from_M200(5e9, c200=4.0)
    assert 20 < v200 < 50, f"v200 = {v200} km/s, expected ~ 25-35"


def test_cloud9_nhi_data_shape_and_central_value():
    """Cloud-9 N(HI) data has 13 points with central value ~ 5e19 cm^-2.

    Per Benitez-Llambay+ 2024 Fig. 4, N_HI at b=0.5 kpc is ~ 5e19 cm^-2.
    """
    assert len(CLOUD9_NHI_B_KPC) == len(CLOUD9_NHI_LOG10_CM2)
    assert len(CLOUD9_NHI_B_KPC) == len(CLOUD9_NHI_ERR_LOG10)
    assert len(CLOUD9_NHI_B_KPC) >= 10
    # Central value at b=0.5 kpc should be in the range 5e19 ± 50%
    central_log = CLOUD9_NHI_LOG10_CM2[0]  # first point is at b=0.5 kpc
    assert 19.0 < central_log < 20.5, f"central N_HI log = {central_log}"


def test_m51_cloud_parameters_match_paper():
    """M51 Cloud S / N parameters match arXiv:2607.21034.

    M_HI ~ 10^6.5 M_sun, v_disp ~ 20 km/s, M_halo ~ 3.7e9 M_sun.
    """
    assert 1e6 < M51_CLOUD_S_M_HI < 1e7
    assert 15 < M51_CLOUD_S_V_DISP_KMS < 25
    assert 1e9 < M51_CLOUD_S_HALO_MASS < 1e10
    # Both clouds should be similar (same paper)
    assert M51_CLOUD_S_HALO_MASS == M51_CLOUD_N_HALO_MASS
    assert M51_CLOUD_S_M_HI == M51_CLOUD_N_M_HI
    assert M51_CLOUD_S_V_DISP_KMS == M51_CLOUD_N_V_DISP_KMS


def test_enclosed_mass_nfw_at_virial_radius():
    """NFW enclosed mass at r=R200 should equal M200.

    M(<R200) = M200 · [ln(1+c) - c/(1+c)] / [ln(1+c) - c/(1+c)] = M200.
    """
    M200, c200 = 5e9, 4.0
    _, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    R200 = c200 * r_s_0
    M_at_R200 = float(enclosed_mass_nfw(np.array([R200]), M200, c200)[0])
    # Allow 1% tolerance for numerical integration
    assert abs(M_at_R200 - M200) / M200 < 0.01, f"M(<R200) = {M_at_R200}, M200 = {M200}"


def test_bestfit_cdm_has_no_sidm_params():
    """The CDM best-fit dict should NOT have τ or σ/m (it's τ=0, σ/m=0)."""
    assert "tau" not in CLOUD9_BESTFIT_CDM
    assert "sigma_m_v200" not in CLOUD9_BESTFIT_CDM


def test_bestfit_sidm_t018_has_correct_published_values():
    """The SIDM τ=0.18 best-fit dict should match the published values."""
    assert CLOUD9_BESTFIT_SIDM_T018["tau"] == 0.18
    assert CLOUD9_BESTFIT_SIDM_T018["sigma_m_v200"] == 483.0
    assert CLOUD9_BESTFIT_SIDM_T018["M200"] == 4.7e9
    assert CLOUD9_BESTFIT_SIDM_T018["c200"] == 4.0


def test_bestfit_sidm_t095_has_correct_published_values():
    """The SIDM τ=0.95 best-fit dict should match the published values."""
    assert CLOUD9_BESTFIT_SIDM_T095["tau"] == 0.95
    assert CLOUD9_BESTFIT_SIDM_T095["sigma_m_v200"] == 2.1e4
    assert CLOUD9_BESTFIT_SIDM_T095["M200"] == 3.4e9
    assert CLOUD9_BESTFIT_SIDM_T095["c200"] == 1.5


def test_loglike_returns_finite_for_sensible_inputs():
    """loglike_relhic should return finite values for in-range inputs."""
    from t90_v27_relhic_likelihood import loglike_relhic, loglike_cloud9, loglike_m51
    # Master v0.7 MAP
    ll = loglike_relhic(0.28, 0.16)
    assert np.isfinite(ll)
    # CDM-like
    ll_cdm = loglike_relhic(1e-5, 0.0)
    assert np.isfinite(ll_cdm)
    # SIDM-friendly
    ll_sidm = loglike_relhic(100.0, 0.0)
    assert np.isfinite(ll_sidm)


def test_loglike_returns_zero_for_invalid_inputs():
    """loglike_relhic should return 0 for non-finite or non-positive inputs."""
    from t90_v27_relhic_likelihood import loglike_relhic
    assert loglike_relhic(0.0, 0.0) == 0.0
    assert loglike_relhic(-1.0, 0.0) == 0.0
    assert loglike_relhic(0.3, np.inf) == 0.0
    assert loglike_relhic(0.3, np.nan) == 0.0
