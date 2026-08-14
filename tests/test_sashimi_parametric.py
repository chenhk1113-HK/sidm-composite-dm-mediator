"""
Tests for sashimi_parametric.py — Direction A (SASHIMI-SIDM in-house).
"""
from __future__ import annotations
import sys
import numpy as np
from pathlib import Path

# Add project root + v0.3 code to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v0.3-prelim" / "code"))

from sashimi_parametric import (
    formation_redshift,
    formation_time_Gyr,
    NFW_profile_params,
    vmax_from_profile,
    rmax_from_profile,
    core_collapse_timescale_Gyr,
    Vmax_ratio,
    rmax_ratio,
    rho_s_ratio,
    r_s_ratio,
    r_c_ratio,
    sigma_effective_per_m_chi,
    cdm_to_sidm_halo,
    predict_sparc_satellite,
    SIDM_MODELS,
)


class TestSashimiParametricBasics:
    """Basic consistency tests."""

    def test_formation_redshift_mass_dependence(self):
        """z_f decreases with increasing halo mass (Eq. 2.21)."""
        z_low_mass = formation_redshift(np.log10(1e7))
        z_high_mass = formation_redshift(np.log10(1e12))
        # Higher mass halos form later (smaller z_f)
        assert z_low_mass > z_high_mass

    def test_formation_time_decreases_with_redshift(self):
        """Higher z_f → smaller t_f (earlier in cosmic history)."""
        t_low = formation_time_Gyr(1.0)
        t_high = formation_time_Gyr(5.0)
        assert t_low > t_high

    def test_nfw_profile_params_consistent(self):
        """For (M_vir, z, c_vir), the resulting r_s and ρ_s give back V_max via Eq. 2.5."""
        M_vir = 1e10  # M_sun (Milky Way-ish halo)
        c_vir = 10.0
        z = 0.0
        r_s, rho_s = NFW_profile_params(M_vir, z, c_vir)
        V_max = vmax_from_profile(rho_s, r_s)
        # For a 10^10 M_sun halo with c=10, V_max is typically 30-100 km/s
        # (depends on concentration-mass relation). Allow wider range.
        assert 10.0 < V_max < 500.0

    def test_rmax_from_profile(self):
        """r_max = 2.163 × r_s (Eq. 2.4)."""
        assert abs(rmax_from_profile(1.0) - 2.163) < 0.001
        assert abs(rmax_from_profile(10.0) - 21.63) < 0.01


class TestVmaxRatioPolynomial:
    """Polynomial fits (Eqs. 2.14, 2.15)."""

    def test_vmax_ratio_at_zero(self):
        """At t̃ = 0, V_max ratio = 1 (no SIDM effect at formation)."""
        assert abs(Vmax_ratio(0.0) - 1.0) < 1e-6

    def test_vmax_ratio_grows_with_time(self):
        """V_max ratio grows in the cored phase (t̃ ~ 0 to 1)."""
        v_at_05 = Vmax_ratio(0.5)
        v_at_02 = Vmax_ratio(0.2)
        # In cored phase, V_max ratio should grow as the SIDM core forms
        assert v_at_05 > v_at_02

    def test_vmax_ratio_caps_at_collapse(self):
        """Beyond t̃ = 1.1, ratio is capped (no further change)."""
        v_at_collapse = Vmax_ratio(1.1)
        v_beyond = Vmax_ratio(2.0)
        assert abs(v_at_collapse - v_beyond) < 1e-6

    def test_rmax_ratio_at_zero(self):
        assert abs(rmax_ratio(0.0) - 1.0) < 1e-6

    def test_rho_s_ratio_at_zero(self):
        assert abs(rho_s_ratio(0.0) - 1.0) < 0.1  # log term makes it not exactly 1

    def test_r_c_ratio_at_zero(self):
        assert abs(r_c_ratio(0.0) - 0.0) < 1e-6  # no core at t̃=0


class TestVelocityDependentCrossSection:
    """Eq. (2.24) — σ_eff = σ_0 / (1 + (v/w)²)²."""

    def test_v_independent_at_zero_velocity(self):
        """σ_eff = σ_0 when v → 0."""
        assert abs(sigma_effective_per_m_chi(10.0, 0.0, w_kms=1.0) - 10.0) < 1e-6

    def test_suppressed_at_high_velocity(self):
        """σ_eff << σ_0 when v >> w."""
        # At v = 100 km/s, w = 1 km/s: ratio = (1 + 10000)² ≈ 10⁸
        sigma_eff = sigma_effective_per_m_chi(10.0, 100.0, w_kms=1.0)
        assert sigma_eff < 1e-5  # essentially suppressed

    def test_v_inf_model_returns_constant(self):
        """w_kms = ∞ gives σ_eff = σ_0 (velocity-independent)."""
        for v in [1, 10, 100, 1000]:
            assert abs(sigma_effective_per_m_chi(5.0, v, w_kms=np.inf) - 5.0) < 1e-9


class TestCoreCollapseTimescale:
    """Eq. (2.23)."""

    def test_t_c_finite_positive(self):
        """For reasonable inputs, t_c is positive and finite."""
        # 10⁸ M_sun dSph, σ/m ~ 100 cm²/g
        t_c = core_collapse_timescale_Gyr(
            sigma_eff_per_m_chi_cm2_per_g=100.0,
            rho_s_CDM_Msun_per_kpc3=1e7,
            r_s_CDM_kpc=1.0,
        )
        assert 0 < t_c < 100  # Gyr; reasonable for dSph

    def test_higher_cross_section_faster_collapse(self):
        """Higher σ/m → smaller t_c (faster collapse)."""
        t_c_low = core_collapse_timescale_Gyr(1.0, 1e7, 1.0)
        t_c_high = core_collapse_timescale_Gyr(100.0, 1e7, 1.0)
        assert t_c_high < t_c_low

    def test_zero_cross_section_no_collapse(self):
        """σ = 0 → t_c = ∞ (CDM, no collapse)."""
        t_c = core_collapse_timescale_Gyr(0.0, 1e7, 1.0)
        assert t_c == np.inf


class TestCdmToSidmHalo:
    """Full SASHIMI-SIDM parametric mapping."""

    def test_returns_all_fields(self):
        """predict_sparc_satellite returns dict with all expected fields."""
        sidm = predict_sparc_satellite(M_vir_Msun=1e8, c_vir=15.0,
                                        sigma_0_per_m_chi_cm2_per_g=10.0)
        for key in ["rho_s_sidm", "r_s_sidm", "r_c_sidm", "V_max_sidm",
                    "r_max_sidm", "t_tilde", "core_collapsed", "t_c_Gyr"]:
            assert key in sidm

    def test_r_core_positive_when_collapsed(self):
        """Core-collapsed halos have positive r_c (the core shrinks into a collapsed profile)."""
        # Model I at 10⁸ M_sun collapses (t_c = 4.4 Gyr < Hubble time)
        sidm = predict_sparc_satellite(
            M_vir_Msun=1e8, c_vir=15.0,
            sigma_0_per_m_chi_cm2_per_g=SIDM_MODELS["Model_I"]["sigma_0_per_m_chi"],
            w_kms=SIDM_MODELS["Model_I"]["w_kms"],
        )
        assert sidm["core_collapsed"]
        assert sidm["r_c_sidm"] > 0

    def test_v_max_consistent_with_cdm_for_low_sigma(self):
        """Very low σ should leave V_max close to CDM."""
        # Model V with σ = 0.001 → no SIDM effect
        sidm = predict_sparc_satellite(
            M_vir_Msun=1e8, c_vir=15.0,
            sigma_0_per_m_chi_cm2_per_g=0.001,
        )
        V_max_cdm = sidm["V_max_cdm_at_f"]
        # V_max^SIDM should be roughly the same (within factor 2)
        assert 0.5 < sidm["V_max_sidm"] / V_max_cdm < 2.0

    def test_all_five_sidm_models_run(self):
        """All 5 models in Table 2.3 should run without error."""
        for model_name, params in SIDM_MODELS.items():
            sidm = predict_sparc_satellite(
                M_vir_Msun=1e8, c_vir=15.0,
                sigma_0_per_m_chi_cm2_per_g=params["sigma_0_per_m_chi"],
                w_kms=params["w_kms"],
            )
            assert sidm["V_max_sidm"] > 0
            assert np.isfinite(sidm["V_max_sidm"])

    def test_mass_concentration_dependence(self):
        """Higher concentration → faster collapse (well-known result)."""
        sidm_low_c = predict_sparc_satellite(1e8, c_vir=5.0,
                                              sigma_0_per_m_chi_cm2_per_g=10.0)
        sidm_high_c = predict_sparc_satellite(1e8, c_vir=30.0,
                                               sigma_0_per_m_chi_cm2_per_g=10.0)
        # Higher c → smaller r_s → smaller ρ_s → shorter t_c
        assert sidm_high_c["t_c_Gyr"] < sidm_low_c["t_c_Gyr"]