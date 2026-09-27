"""
Tests for Phase 15, 16, 17 (the three probe phases).
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


# ============================================================
# Phase 15: g_D limit per annihilation channel
# ============================================================
class TestPhase15Annihilation:
    def test_electron_channel_constrained(self):
        """e+e- has the tightest Fermi limit → smallest g_D_max."""
        from phase15_annihilation_channels import find_max_gD, FERMI_LIMITS
        g_e = find_max_gD("e+e-", FERMI_LIMITS["e+e-"])
        g_tt = find_max_gD("tt", FERMI_LIMITS["tt"])
        assert g_e < g_tt, "e+e- should be more constraining than tt"

    def test_top_quark_unconstrained(self):
        """tt channel: m_t > m_chi, so σv = 0 regardless of g_D."""
        from phase15_annihilation_channels import sigma_v_xx_cm3_per_s
        # At m_chi=45 GeV and m_t=173 GeV, tt is kinematically forbidden
        assert sigma_v_xx_cm3_per_s(0.7, "tt") == 0.0

    def test_fermi_limit_structural(self):
        """All kinematically accessible channels constrain g_D ≤ 0.21."""
        from phase15_annihilation_channels import find_max_gD, FERMI_LIMITS
        for ch in ["e+e-", "μ+μ-", "τ+τ-", "bb", "cc", "uu", "dd", "ss", "gg", "νν"]:
            g_max = find_max_gD(ch, FERMI_LIMITS[ch])
            assert g_max < 0.22, f"{ch}: g_D_max = {g_max} > 0.22"


# ============================================================
# Phase 16: Asymmetric DM ratio
# ============================================================
class TestPhase16AsymmetricDM:
    def test_natural_chi_mass_5GeV(self):
        """1:1 B-L transfer gives m_chi ~ 5 GeV."""
        from phase16_asymmetric_dm_ratio import eta_ratio
        # Check that eta_ratio(5) ≈ 1
        r5 = eta_ratio(5.0)
        assert 0.9 < r5 < 1.1, f"eta_ratio(5 GeV) = {r5}, expected ~1"

    def test_45GeV_chi_offs_natural(self):
        """At m_chi=45 GeV, η_DM/η_B ≈ 0.11, off the natural 1:1 value."""
        from phase16_asymmetric_dm_ratio import eta_ratio
        r45 = eta_ratio(45.0)
        assert 0.05 < r45 < 0.2, f"eta_ratio(45 GeV) = {r45}"

    def test_heavy_chi_unnatural(self):
        """At m_chi=1000 GeV, transfer is highly unphysical."""
        from phase16_asymmetric_dm_ratio import eta_ratio
        r1000 = eta_ratio(1000.0)
        assert r1000 < 0.01, f"eta_ratio(1000 GeV) = {r1000}"


# ============================================================
# Phase 17: Core-collapse time
# ============================================================
class TestPhase17CoreCollapse:
    def test_tau_core_inversely_proportional_to_sigma_m(self):
        """More scattering → faster collapse (τ ∝ 1/σ/m)."""
        from phase17_core_collapse_gD import tau_core_collapse_gyr
        tau_high = tau_core_collapse_gyr(0.5)
        tau_low = tau_core_collapse_gyr(0.05)
        assert tau_high < tau_low

    def test_tau_10gyr_at_0p1(self):
        """At σ/m=0.1, τ=10 Gyr (calibration)."""
        from phase17_core_collapse_gD import tau_core_collapse_gyr
        assert tau_core_collapse_gyr(0.1) == 10.0

    def test_fermi_limit_too_slow_for_collapse(self):
        """At g_D=0.16, σ/m is too small to give τ=10 Gyr."""
        from phase17_core_collapse_gD import tau_core_collapse_gyr
        from t40_yukawa_sigma_m import sigma_m_cm2_per_g
        sm = sigma_m_cm2_per_g(100, 200, 45, 0.16)
        tau = tau_core_collapse_gyr(sm)
        # At g_D=0.16, τ should be much greater than 10 Gyr
        assert tau > 100, f"At g_D=0.16, τ = {tau} Gyr, expected >> 10 Gyr"
