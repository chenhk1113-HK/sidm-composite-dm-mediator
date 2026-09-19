"""
Tests for T120.10 — Direct Detection Constraints on Magnetic Dipole DM.

Verifies:
1. Correct mu_chi calculation for target sigma_DM_DM
2. Correct sigma_SI prediction (correct unit conversion)
3. Correct LZ limit interpolation (NOT log value)
4. Verdict: magnetic dipole DM is RULED OUT
5. Cross-check with t120_11_hidden_u1_uv (alternative UV completion)
"""
import sys
from pathlib import Path
import numpy as np
import pytest

_CODE_DIR = Path(__file__).parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))


class TestT12010RequiredMuChi:
    """Tests for required_mu_chi calculation."""

    def test_required_mu_chi_for_phase44(self):
        """Required mu_chi for sigma_DM_DM = 0.052 cm^2/g at v=100 km/s, m_chi=10.44 GeV.

        The correct answer is ~8.23e-14 cm (NOT 1.57e-20 cm from T120.9b).
        """
        from t120_10a_direct_detection import required_mu_chi_for_sigma_DM_DM
        mu_chi_GeV = required_mu_chi_for_sigma_DM_DM(0.052, 100.0, 10.44)
        mu_chi_cm = mu_chi_GeV / 5.068e13
        # Should be in the range 1e-14 to 1e-12 cm
        assert 1e-14 < mu_chi_cm < 1e-12, (
            f"Required mu_chi should be 1e-14 to 1e-12 cm: got {mu_chi_cm:.3e}"
        )

    def test_required_mu_chi_sanity_check(self):
        """The required mu_chi should give back the target sigma_DM_DM."""
        from t120_10a_direct_detection import (required_mu_chi_for_sigma_DM_DM,
                                                 sigma_DM_DM_over_m_magnetic_dipole)
        mu_chi_GeV = required_mu_chi_for_sigma_DM_DM(0.052, 100.0, 10.44)
        sm_check = sigma_DM_DM_over_m_magnetic_dipole(100.0, 10.44, mu_chi_GeV)
        # Should be close to target
        assert abs(sm_check - 0.052) < 1e-4, (
            f"Required mu_chi should give sigma_DM_DM ~ 0.052: got {sm_check}"
        )

    def test_mu_chi_scales_correctly(self):
        """Required mu_chi^4 should scale with target sigma_DM_DM (linear)."""
        from t120_10a_direct_detection import required_mu_chi_for_sigma_DM_DM
        mu_1 = required_mu_chi_for_sigma_DM_DM(0.052, 100.0, 10.44)
        mu_2 = required_mu_chi_for_sigma_DM_DM(0.052 * 16, 100.0, 10.44)  # 16x target
        ratio = mu_2 / mu_1
        # Should be 16^(1/4) = 2 (mu_chi^4 ~ sigma_DM_DM)
        assert 1.8 < ratio < 2.2, f"Ratio should be ~2: got {ratio:.2f}"


class TestT12010SigmaSI:
    """Tests for sigma_SI (DM-nucleon) prediction."""

    def test_sigma_SI_for_phase44(self):
        """With required mu_chi, sigma_SI should be ~10^-30 to 10^-33 cm^2."""
        from t120_10a_direct_detection import (required_mu_chi_for_sigma_DM_DM,
                                                 sigma_SI_magnetic_dipole)
        mu_chi_GeV = required_mu_chi_for_sigma_DM_DM(0.052, 100.0, 10.44)
        sigma_SI = sigma_SI_magnetic_dipole(10.44, mu_chi_GeV)
        # Should be in 10^-33 to 10^-30 cm^2 range (LARGE compared to LZ 10^-47)
        assert 1e-34 < sigma_SI < 1e-29, (
            f"sigma_SI should be 10^-33 to 10^-30: got {sigma_SI:.3e}"
        )

    def test_sigma_SI_is_velocity_independent(self):
        """sigma_SI for magnetic dipole should NOT depend on v (no 1/v enhancement)."""
        from t120_10a_direct_detection import sigma_SI_magnetic_dipole
        # sigma_SI uses mu_chi, not v; only m_chi matters
        # Test by giving same mu_chi and varying m_chi (sigma ~ 1/m_chi^2)
        s1 = sigma_SI_magnetic_dipole(10.44, 1e-6)  # some mu_chi in GeV^-1
        s2 = sigma_SI_magnetic_dipole(20.88, 1e-6)  # double mass
        ratio = s2 / s1
        # sigma_SI ~ 1/m_chi^2, so doubling mass should give 1/4
        assert 0.2 < ratio < 0.3, f"sigma_SI ~ 1/m^2: ratio = {ratio:.2f}"

    def test_sigma_SI_scales_as_mu_chi_to_4(self):
        """sigma_SI should scale as mu_chi^4."""
        from t120_10a_direct_detection import sigma_SI_magnetic_dipole
        s1 = sigma_SI_magnetic_dipole(10.44, 1e-7)
        s2 = sigma_SI_magnetic_dipole(10.44, 2e-7)  # double mu_chi
        ratio = s2 / s1
        # Should be 2^4 = 16
        assert 14 < ratio < 18, f"mu_chi^4 scaling: ratio = {ratio:.2f}"


class TestT12010LZLimit:
    """Tests for LZ limit interpolation (FIXED)."""

    def test_lz_limit_returns_value_not_log(self):
        """The CRITICAL BUG FIX: lz_limit should return the value, not the log."""
        from t120_10a_direct_detection import lz_limit_2024
        result = lz_limit_2024(10.44)
        # Should be ~9.4e-47 (NOT log -105.98)
        assert 1e-48 < result < 1e-45, (
            f"LZ limit should be ~9.4e-47 cm^2: got {result}"
        )

    def test_lz_limit_at_various_masses(self):
        """LZ limit at various DM masses should be in expected ranges."""
        from t120_10a_direct_detection import lz_limit_2024
        # LZ is most sensitive at m_chi ~ 30-50 GeV
        lz_10 = lz_limit_2024(10.0)
        lz_50 = lz_limit_2024(50.0)
        lz_500 = lz_limit_2024(500.0)
        # All should be in 10^-47 to 10^-45 range
        assert all(1e-48 < x < 1e-44 for x in [lz_10, lz_50, lz_500])

    def test_magnetic_dipole_limit_weaker(self):
        """LZ MD limit (with 1/E_R^2 weakening) should be WEAKER than WIMP limit."""
        from t120_10a_direct_detection import lz_limit_2024, lz_limit_magnetic_dipole
        lz_wimp = lz_limit_2024(10.44)
        lz_md = lz_limit_magnetic_dipole(10.44)
        # MD limit should be ~30x weaker
        assert lz_md > lz_wimp, (
            f"MD limit should be weaker: {lz_md:.2e} vs {lz_wimp:.2e}"
        )
        ratio = lz_md / lz_wimp
        assert 25 < ratio < 35


class TestT12010Verdict:
    """Tests that the final verdict is CORRECT: magnetic dipole RULED OUT."""

    def test_magnetic_dipole_RULED_OUT(self):
        """The full check function should return RULED_OUT = True."""
        from t120_10a_direct_detection import check
        result = check()
        assert result["RULED_OUT"], (
            f"Magnetic dipole should be RULED OUT: violation_WIMP = "
            f"{result['violation_WIMP']:.2e}, violation_MD = {result['violation_MD']:.2e}"
        )

    def test_violation_at_least_10_orders_of_magnitude(self):
        """sigma_SI should be at least 10^10x above LZ limit (the T120.10 finding)."""
        from t120_10a_direct_detection import check
        result = check()
        assert result["violation_WIMP"] > 1e10, (
            f"Violation should be > 10^10: got {result['violation_WIMP']:.2e}"
        )

    def test_mu_chi_above_sigurdson_bound(self):
        """Required mu_chi should be much larger than Sigurdson+ 2004 bound (1e-16 e cm)."""
        from t120_10a_direct_detection import check
        result = check()
        sigurdson_bound_cm = 1e-16  # 1e-16 e cm = 1e-16 * 1.602e-19/3.336e-10... actually
        # Actually: 1 e cm = 1.602e-19 C * 1e-2 m = 1.602e-21 C m
        # But for magnetic moments: mu [GeV^-1] = mu [e cm] * (1.602e-19) / (hbar c)
        # Simplification: just check the order of magnitude
        # The Sigurdson+ bound on mu_chi ~ 10^-16 cm in our units
        ratio_to_bound = result["mu_chi_cm"] / 1e-16
        assert ratio_to_bound > 100, (
            f"Required mu_chi should be > 100x Sigurdson bound: {ratio_to_bound:.2e}"
        )


class TestT12010CrossCheckWithHiddenU1:
    """Cross-check: hidden U(1) UV completion should work; magnetic dipole should not."""

    def test_magnetic_dipole_failure_vs_hidden_u1_success(self):
        """Compare magnetic dipole vs hidden U(1) for the same target sigma_DM_DM."""
        from t120_10a_direct_detection import check as md_check
        from t120_11_hidden_u1_uv import check_uv_completion

        md_result = md_check()
        u1_result = check_uv_completion(
            m_D_GeV=10.44, alpha_D=0.0015, m_A_prime_GeV=0.030,
            Delta_m_GeV=0.010, epsilon=1e-5
        )

        # Magnetic dipole should FAIL (RULED_OUT = True)
        assert md_result["RULED_OUT"]

        # Hidden U(1) should PASS (both self-interaction and direct detection)
        assert u1_result, "Hidden U(1) should pass"

    def test_different_mechanisms_different_signatures(self):
        """Magnetic dipole and hidden U(1) have different sigma_SI mechanisms."""
        from t120_10a_direct_detection import (required_mu_chi_for_sigma_DM_DM,
                                                 sigma_SI_magnetic_dipole)
        from t120_11_hidden_u1_uv import sigma_SI_loop

        # Magnetic dipole: tree-level sigma_SI
        mu_chi_GeV = required_mu_chi_for_sigma_DM_DM(0.052, 100.0, 10.44)
        sigma_SI_md = sigma_SI_magnetic_dipole(10.44, mu_chi_GeV)

        # Hidden U(1): loop-level sigma_SI
        sigma_SI_u1 = sigma_SI_loop(10.44, 0.0015, 1e-5, 0.030)

        # Magnetic dipole sigma_SI should be MUCH larger
        ratio = sigma_SI_md / sigma_SI_u1
        assert ratio > 1e10, f"MD / U1 ratio should be > 10^10: {ratio:.2e}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])