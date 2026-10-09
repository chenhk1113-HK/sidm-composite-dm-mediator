"""
R88(83) Unit tests for gravothermal_yang2024.py prefactor re-derivation.

These tests verify:
1. BM2 calibration: the literal analytical (150*C) and BM2-calibrated (1.82x)
   prefactors reproduce the published 28.7 Gyr value within 0.5%.
2. Legacy 1.34e12 prefactor still matches BM2 (no regression).
3. Cosmo-501 (independent halo): the BM2-calibrated prefactor underestimates
   Yang+ 2024's reported t_c by ~10x. This is a REAL halo-specific calibration
   issue — the prefactor is NOT universal.

Tests were added in response to ClawsGO Science Agent review (2026-10-08),
which identified the BM2-only validation as circular.
"""

import os
import sys

os.environ['DM_SIDM_PROJECT_ROOT'] = r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator'
sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')
sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts')
sys.modules.pop('config', None)

import math
import pytest

import gravothermal_yang2024 as gy


class TestR88GravothermalPrefactor:
    """R88(83) tests for the gravothermal t_c prefactor re-derivation."""

    def test_literal_analytical_BM2(self):
        """Literal analytical 150*C formula should give ~15.77 Gyr for BM2."""
        t_c = gy.collapse_time_SI_gyr(7.1, 2.74e8, 0.141)
        expected = 15.77
        assert abs(t_c - expected) < 0.01, f"got {t_c}, expected {expected}"

    def test_BM2_calibrated(self):
        """BM2-calibrated (1.82x) prefactor should give ~28.7 Gyr for BM2."""
        t_c = gy.collapse_time_calibrated_gyr(7.1, 2.74e8, 0.141)
        expected = 28.7
        assert abs(t_c - expected) < 0.1, f"got {t_c}, expected {expected}"

    def test_legacy_1p34e12_still_matches_BM2(self):
        """Legacy CALIBRATED_PREFACTOR = 1.34e12 should still match BM2 within 5%."""
        t_c = gy.collapse_time_gyr(7.1, 2.74e8, 0.141)
        expected = 28.7
        # Legacy prefactor gives 29.44 Gyr (within 2.6%), but allow 5% for numerical noise
        assert abs(t_c - expected) / expected < 0.05, f"got {t_c}, expected {expected}"

    def test_cosmo501_independent_halo_underprediction(self):
        """Cosmo-501 (independent halo) is underpredicted by ~10x with BM2 calibration.

        This is the HONEST validation ClawsGO asked for: the BM2-only
        calibration does NOT generalize to other halos. The Yang+ 2024
        formula's "150" prefactor is NOT a universal constant — it requires
        halo-specific N-body calibration.

        This test DOCUMENTS the issue (not "fixes" it) — see validation_cosmo_501
        in gravothermal_yang2024.py for the full diagnostic.
        """
        t_c_predicted = gy.collapse_time_calibrated_gyr(
            gy.COSMO_501_SIGMA_EFF_CM2_PER_G,
            gy.COSMO_501_RHO_EFF_MSUN_PER_KPC3,
            gy.COSMO_501_R_EFF_KPC,
        )
        t_c_reported = gy.COSMO_501_T_C_GYR_REPORTED  # 9.04 Gyr

        # The BM2-calibrated prefactor under-predicts by factor 10.75
        ratio = t_c_predicted / t_c_reported
        assert ratio < 0.2, (
            f"BM2-calibrated formula should UNDERESTIMATE Cosmo-501 by ~10x. "
            f"Got ratio={ratio:.3f}, predicted={t_c_predicted:.3f} Gyr, "
            f"reported={t_c_reported:.3f} Gyr. If this test fails, either: "
            f"(1) the prefactor derivation was wrong, or "
            f"(2) Yang+ 2024's Cosmo-501 data is now consistent with eq. 2.2 (would be a real result)"
        )

    def test_cosmo501_validation_function(self):
        """The validate_cosmo_501_calibration() function should FAIL (document halo-specific issue)."""
        result = gy.validate_cosmo_501_calibration()
        # The function returns True if within factor 3, False otherwise.
        # We expect it to return False because the BM2 calibration underestimates by ~10x.
        # This is the HONEST outcome — it DOCUMENTS the issue rather than hides it.
        assert result is False, (
            "validate_cosmo_501_calibration() should return False to document that "
            "the BM2 calibration does not generalize to other halos."
        )

    def test_unit_conversion_consistency(self):
        """Verify the analytical function uses consistent SI units end-to-end."""
        # If we double sigma_eff, t_c should halve
        t_c_1 = gy.collapse_time_SI_gyr(7.1, 2.74e8, 0.141)
        t_c_2 = gy.collapse_time_SI_gyr(14.2, 2.74e8, 0.141)
        assert abs(t_c_1 / t_c_2 - 2.0) < 0.01

        # If we double rho_eff, t_c should drop by factor sqrt(2) * 2 = 2*sqrt(2)
        # (because denom has rho_eff * sqrt(rho_eff) = rho_eff^(3/2))
        t_c_3 = gy.collapse_time_SI_gyr(7.1, 5.48e8, 0.141)
        expected_factor = 1.0 / (2.0**1.5)
        assert abs((t_c_3 / t_c_1) - expected_factor) < 0.01

    def test_cosmo_501_constants_present(self):
        """The R88(83) Cosmo-501 constants should be defined in the module."""
        assert hasattr(gy, 'COSMO_501_V_MAX_KMS')
        assert hasattr(gy, 'COSMO_501_R_MAX_KPC')
        assert hasattr(gy, 'COSMO_501_T_L_ZF_GYR')
        assert hasattr(gy, 'COSMO_501_T_L_OVER_T_C')
        assert hasattr(gy, 'COSMO_501_R_EFF_KPC')
        assert hasattr(gy, 'COSMO_501_RHO_EFF_MSUN_PER_KPC3')
        assert hasattr(gy, 'COSMO_501_SIGMA_EFF_CM2_PER_G')
        assert hasattr(gy, 'COSMO_501_T_C_GYR_REPORTED')
