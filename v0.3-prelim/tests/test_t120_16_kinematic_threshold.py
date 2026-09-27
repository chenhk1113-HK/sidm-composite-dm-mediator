"""
Tests for T120.16 kinematic threshold check.

These tests verify that:
1. The KE_CM calculation is correct (matches referee's 23 eV for Cloud-9)
2. Zhang 2016's V_max formula is alpha_D^2 * m_chi (NOT alpha_D * m_phi)
3. The chosen T120.11 parameters (Delta_m = 10 MeV) are outside the allowed regime
4. Future parameter choices can be screened by this check
"""
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/code")

from t120_16_kinematic_threshold import (
    ke_cm_eV,
    zhang2016_well_depth,
    zhang2016_allowed_splitting,
    kinematic_threshold_check,
    zhang2016_self_scattering_v,
)


class TestKECalculation:
    """Verify KE_CM matches referee's calculation."""

    def test_cloud9_KE_matches_referee_23_eV(self):
        """Referee says Cloud-9 KE_CM = 23 eV. Verify."""
        KE = ke_cm_eV(m_chi_GeV=10.7, v_km_s=28)
        # Referee computed 23.3 eV (close enough to 23 ± 0.5)
        assert 22 < KE < 25, f"Cloud-9 KE = {KE} eV, expected ~23 eV"

    def test_dSph_KE_is_6_7_eV(self):
        """dSph (v=15) KE_CM = 6.7 eV per our verification."""
        KE = ke_cm_eV(m_chi_GeV=10.7, v_km_s=15)
        assert 6 < KE < 8, f"dSph KE = {KE} eV, expected ~6.7 eV"

    def test_UFD_KE_is_sub_eV(self):
        """UFD (v=3) KE_CM is sub-eV."""
        KE = ke_cm_eV(m_chi_GeV=10.7, v_km_s=3)
        assert KE < 1.0, f"UFD KE = {KE} eV, should be sub-eV"

    def test_SPARC_KE_is_hundreds_of_eV(self):
        """SPARC (v=100) KE_CM is ~300 eV."""
        KE = ke_cm_eV(m_chi_GeV=10.7, v_km_s=100)
        assert 250 < KE < 350, f"SPARC KE = {KE} eV, expected ~300 eV"

    def test_cluster_KE_is_keV(self):
        """Cluster (v=500) KE_CM is ~7 keV."""
        KE = ke_cm_eV(m_chi_GeV=10.7, v_km_s=500)
        assert 5e3 < KE < 1e4, f"Cluster KE = {KE} eV, expected ~7.5 keV"


class TestZhangFormula:
    """Verify Zhang 2016's V_max formula is alpha_D^2 * m_chi."""

    def test_zhang_V_max_is_alpha_D_sq_m_chi(self):
        """Zhang's actual formula: V_max = alpha_D^2 * m_chi."""
        V = zhang2016_well_depth(alpha_D=0.0015, m_chi_MeV=10700)
        # 0.0015^2 * 10700 = 0.0241 MeV
        assert 0.020 < V < 0.030, f"V_max = {V} MeV, expected ~0.024 MeV"

    def test_zhang_allowed_splitting_is_24_keV(self):
        """For our params, allowed Delta_m < 24.1 keV (= 0.0241 MeV)."""
        allowed_MeV = zhang2016_allowed_splitting(alpha_D=0.0015, m_chi_MeV=10700)
        # Returns MeV: 0.0015^2 * 10700 = 0.024 MeV = 24.1 keV
        assert 0.020 < allowed_MeV < 0.030, f"Allowed = {allowed_MeV} MeV, expected ~0.024 MeV (24 keV)"
        assert 20 < allowed_MeV * 1000 < 30, f"Allowed = {allowed_MeV*1000} keV, expected ~24 keV"

    def test_our_V_max_was_16_MeV_wrong(self):
        """Verify our old claim V_max = alpha_D * m_chi = 16 MeV was wrong."""
        # Old wrong claim: 0.0015 * 10700 MeV = 16.05 MeV
        V_old = 0.0015 * 10700
        assert V_old > 10, "Old claim should be 16 MeV"
        # Correct Zhang formula: 0.024 MeV
        V_new = zhang2016_well_depth(0.0015, 10700)
        # Difference is factor: V_old / V_new = (alpha_D * m_chi) / (alpha_D^2 * m_chi) = 1/alpha_D ~ 667
        ratio = V_old / V_new
        assert 600 < ratio < 700, f"Ratio = {ratio}, expected ~667 (1/alpha_D)"


class TestKinematicForbiddenness:
    """Verify T120.11 parameters fail the kinematic check."""

    def test_T120_11_Delta_m_is_415x_beyond_zhang_allowed(self):
        """Our Delta_m = 10 MeV is ~415x beyond Zhang's allowed 24 keV."""
        Delta_m_MeV = 10.0
        allowed_MeV = zhang2016_allowed_splitting(0.0015, 10700)  # 0.024 MeV
        ratio = Delta_m_MeV / allowed_MeV
        # 10 / 0.024 = ~415
        assert 400 < ratio < 500, f"Ratio = {ratio}, expected ~415"

    def test_cloud9_is_in_forbidden_regime(self):
        """At v=28 km/s, our parameters are forbidden."""
        r = kinematic_threshold_check(alpha_D=0.0015, m_chi_GeV=10.7,
                                       Delta_m_MeV=10.0, v_km_s=28)
        assert r['regime'] == 'forbidden'
        assert r['Delta_m_over_KE'] > 1e5

    def test_dSph_is_in_forbidden_regime(self):
        """At v=15 km/s, our parameters are forbidden."""
        r = kinematic_threshold_check(alpha_D=0.0015, m_chi_GeV=10.7,
                                       Delta_m_MeV=10.0, v_km_s=15)
        assert r['regime'] == 'forbidden'
        assert r['Delta_m_over_KE'] > 1e5

    def test_UFD_is_in_forbidden_regime(self):
        """At v=3 km/s, our parameters are forbidden (worst case)."""
        r = kinematic_threshold_check(alpha_D=0.0015, m_chi_GeV=10.7,
                                       Delta_m_MeV=10.0, v_km_s=3)
        assert r['regime'] == 'forbidden'
        assert r['Delta_m_over_KE'] > 1e6


class TestCrossSectionReturnsNaN:
    """Verify sigma_DM-DM returns NaN when forbidden."""

    def test_zhang_sigma_returns_NaN_for_our_params(self):
        """Our (forbidden) parameters should give NaN, not 0.044 cm^2/g."""
        sigma_m = zhang2016_self_scattering_v(
            v_km_s=100, alpha_D=0.0015, m_chi_GeV=10.7,
            Delta_m_MeV=10.0, m_phi_MeV=30.0
        )
        assert np.isnan(sigma_m), f"sigma/m = {sigma_m}, expected NaN for forbidden regime"

    def test_zhang_sigma_works_for_allowed_params(self):
        """With Delta_m = 0.001 MeV (1 keV, well within allowed), sigma/m should be real."""
        sigma_m = zhang2016_self_scattering_v(
            v_km_s=100, alpha_D=0.0015, m_chi_GeV=10.7,
            Delta_m_MeV=0.001, m_phi_MeV=30.0  # 1 keV, well below 24 keV threshold
        )
        assert not np.isnan(sigma_m), f"sigma/m = {sigma_m}, expected real number"
        assert sigma_m > 0


class TestParameterScreening:
    """Use the kinematic check to screen future parameter choices."""

    def test_Delta_m_24_keV_is_at_boundary(self):
        """Delta_m = 24 keV (Zhang's max) should be in preserved regime."""
        r = kinematic_threshold_check(alpha_D=0.0015, m_chi_GeV=10.7,
                                       Delta_m_MeV=0.024, v_km_s=100)
        # At the boundary, should be 'preserved' or 'transition'
        assert r['regime'] in ['preserved', 'transition']

    def test_Delta_m_1_keV_is_preserved(self):
        """Delta_m = 1 keV (well below Zhang max) should be preserved."""
        r = kinematic_threshold_check(alpha_D=0.0015, m_chi_GeV=10.7,
                                       Delta_m_MeV=0.001, v_km_s=100)
        assert r['regime'] == 'preserved'

    def test_Delta_m_1_MeV_is_forbidden(self):
        """Delta_m = 1 MeV (~40x Zhang max) should be forbidden."""
        r = kinematic_threshold_check(alpha_D=0.0015, m_chi_GeV=10.7,
                                       Delta_m_MeV=1.0, v_km_s=100)
        assert r['regime'] == 'forbidden'
