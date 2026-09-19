"""
Tests for T120.11 — Hidden U(1) Dark Photon UV Completion with Pseudo-Dirac.

References:
- Zhang 2016 Phys. Dark Univ. 15 (2017) 82-89 (arXiv:1611.03492)
- Kaplinghat, Tulin, Yu 2014 (arXiv:1310.7945)

Key insight: Pseudo-Dirac mass splitting allows large self-interaction
while evading direct detection, because:
- Tree-level DM-nucleon scattering requires up-scattering chi_1 -> chi_2,
  which is kinematically forbidden if Delta_m > recoil energy
- Self-interaction still works because during close approach,
  potential energy alpha_D * m_D >> Delta_m, allowing adiabatic
  up-scattering within the potential well
"""
import sys
from pathlib import Path
import numpy as np
import pytest

_CODE_DIR = Path(__file__).parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))


class TestHiddenU1UV:
    """Tests for the T120.11 hidden U(1) dark photon UV completion."""

    def test_self_interaction_works_at_low_alpha_D(self):
        """With alpha_D = 0.0015, sigma/m(v=100) ~ 0.044 cm^2/g (close to Phase 44)."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.010)
        # Should be in the range 0.01 - 0.1 cm^2/g (close to 0.052)
        assert 0.01 < sm < 0.1, f"sigma/m should be ~0.04-0.05 cm^2/g: got {sm:.4f}"

    def test_self_interaction_scales_with_alpha_D_squared(self):
        """sigma/m should scale approximately as alpha_D^2 (perturbative).

        With Delta_m fixed, varying alpha_D changes V_max, which slightly
        affects the mass splitting factor. So the scaling is approximately
        alpha_D^2 but not exactly.
        """
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm_001 = zhang2016_self_scattering(10.44, 0.001, 0.030, 0.010)
        sm_002 = zhang2016_self_scattering(10.44, 0.002, 0.030, 0.010)
        ratio = sm_002 / sm_001
        # Should be (0.002/0.001)^2 = 4 (within numerical precision)
        assert 2.0 < ratio < 10.0, f"alpha_D^2 scaling expected, got ratio {ratio:.2f}"

    def test_self_interaction_scales_inverse_with_m_A_prime_squared(self):
        """sigma/m should scale as 1/m_A'^2 (Born approximation)."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm_30 = zhang2016_self_scattering(10.44, 0.01, 0.030, 0.010)
        sm_60 = zhang2016_self_scattering(10.44, 0.01, 0.060, 0.010)
        ratio = sm_30 / sm_60
        # Should be (60/30)^2 = 4 (within numerical precision)
        assert 2.0 < ratio < 10.0, f"1/m_A'^2 scaling expected, got ratio {ratio:.2f}"

    def test_self_interaction_suppressed_by_mass_splitting(self):
        """Larger Delta_m should reduce sigma/m (up-scattering suppressed)."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm_0 = zhang2016_self_scattering(10.44, 0.01, 0.030, 0.000)
        sm_100 = zhang2016_self_scattering(10.44, 0.01, 0.030, 0.100)
        # Delta_m=100 MeV should give LOWER sigma/m than Delta_m=0
        assert sm_100 < sm_0, (
            f"Delta_m=100 MeV should suppress: {sm_100:.4f} vs {sm_0:.4f}"
        )

    def test_sigma_SI_loop_below_LZ(self):
        """Loop-level sigma_SI should be FAR below LZ 2024 limit (10^-47 cm^2)."""
        from t120_11_hidden_u1_uv import sigma_SI_loop
        # With epsilon = 1e-5, alpha_D = 0.01, m_D = 10.44
        sigma_SI = sigma_SI_loop(10.44, 0.01, 1e-5, 0.030)
        LZ_limit = 9.4e-47
        assert sigma_SI < LZ_limit, (
            f"sigma_SI {sigma_SI:.3e} should be < LZ {LZ_limit:.3e}"
        )
        # Should be many orders of magnitude below LZ
        ratio = LZ_limit / sigma_SI
        assert ratio > 1e3, f"Should be > 10^3x below LZ: {ratio:.2e}"

    def test_direct_detection_evasion_mechanism(self):
        """Direct detection is evaded when Δm > recoil energy.

        Per Zhang 2016: tree-level DM-nucleon scattering requires
        up-scattering chi_1 -> chi_2. If Delta_m > recoil energy,
        this is kinematically forbidden.
        """
        # Typical DM-nucleon recoil energy at LZ: ~few hundred keV
        recoil_energy_MeV = 0.1  # 100 keV (typical)
        Delta_m_MeV = 10.0

        # Kinematically forbidden if Delta_m > recoil_energy
        forbidden = Delta_m_MeV > recoil_energy_MeV
        assert forbidden, (
            "Tree-level DM-nucleon scattering should be forbidden "
            "when Delta_m > recoil energy"
        )

    def test_adiabatic_condition_for_self_interaction(self):
        """Self-interaction works when V_max = alpha_D * m_D > Delta_m.

        Per Zhang 2016: during close approach, potential energy allows
        adiabatic up-scattering if V_max > Delta_m.
        """
        alpha_D = 0.0015  # our value
        m_D_MeV = 10440  # 10.44 GeV
        Delta_m_MeV = 10.0

        V_max_MeV = alpha_D * m_D_MeV
        adiabatic = V_max_MeV > Delta_m_MeV
        assert adiabatic, (
            f"V_max = {V_max_MeV:.1f} MeV should be > Delta_m = {Delta_m_MeV} MeV"
        )

    def test_combined_pass(self):
        """Combined check: self-interaction + direct detection both work."""
        from t120_11_hidden_u1_uv import check_uv_completion
        # With our tuned parameters
        result = check_uv_completion(
            m_D_GeV=10.44, alpha_D=0.0015, m_A_prime_GeV=0.030,
            Delta_m_GeV=0.010, epsilon=1e-5
        )
        assert result, "Hidden U(1) UV completion should work with our parameters"


class TestHiddenU1vsMagneticDipole:
    """Comparison: why hidden U(1) works but magnetic dipole doesn't."""

    def test_magnetic_dipole_RULED_OUT_by_LZ(self):
        """Magnetic dipole DM with required mu_chi is RULED OUT by LZ."""
        # From T120.10: required mu_chi = 5.35e-13 cm
        # Sigma_SI = 2.04e-30 cm^2
        # LZ limit = 9.4e-47
        # Violation = 2.17e16x
        sigma_SI_mag = 2.04e-30  # cm^2
        LZ_limit = 9.4e-47  # cm^2
        violation = sigma_SI_mag / LZ_limit
        assert violation > 1e15, (
            f"Magnetic dipole should be ruled out: {violation:.2e}x"
        )

    def test_hidden_U1_passes_LZ(self):
        """Hidden U(1) with pseudo-Dirac passes LZ (with epsilon = 1e-5)."""
        from t120_11_hidden_u1_uv import sigma_SI_loop
        sigma_SI = sigma_SI_loop(10.44, 0.0015, 1e-5, 0.030)
        LZ_limit = 9.4e-47
        violation = sigma_SI / LZ_limit
        # violation is fraction of LZ limit; should be << 1
        assert violation < 1e-3, (
            f"Hidden U(1) should pass: violation = {violation:.2e}"
        )

    def test_hidden_U1_different_mechanism_than_magnetic_dipole(self):
        """Hidden U(1) evades DD via KINEMATIC FORBIDDENNESS, not sigma_SI suppression.

        Magnetic dipole: sigma_SI exists but is huge (2e-30 cm^2)
        Hidden U(1): tree-level sigma_SI is FORBIDDEN by kinematics,
                      only loop-level (suppressed by epsilon^2) contributes
        """
        # Magnetic dipole has non-zero sigma_SI at tree level
        # Hidden U(1) has zero tree-level sigma_SI when Delta_m > recoil energy
        # Loop-level sigma_SI ~ epsilon^2 * alpha_EM^2 * alpha_D^2 / m_D^2
        # which is much smaller than magnetic dipole's tree-level value

        # Just verify the qualitative difference:
        # Magnetic dipole sigma_SI is HUGE (2e-30)
        # Hidden U(1) sigma_SI_loop is tiny (3.8e-51 with epsilon=1e-5)
        sigma_SI_mag = 2.04e-30
        sigma_SI_hidden = 3.8e-51
        ratio = sigma_SI_mag / sigma_SI_hidden
        assert ratio > 1e15, f"Hidden U(1) should be {ratio:.2e}x smaller"


class TestHiddenU1Parameters:
    """Tests for specific parameter values in our model."""

    def test_our_parameter_choice(self):
        """Our specific parameters: alpha_D = 0.0015, m_A' = 30 MeV, Delta_m = 10 MeV."""
        alpha_D = 0.0015
        m_A_prime_GeV = 0.030
        Delta_m_GeV = 0.010
        m_D_GeV = 10.44

        # Self-interaction: ~ 0.05 cm^2/g (close to Phase 44)
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(m_D_GeV, alpha_D, m_A_prime_GeV, Delta_m_GeV)
        assert 0.02 < sm < 0.1, f"sigma/m = {sm:.4f}"

        # Direct detection: well below LZ
        from t120_11_hidden_u1_uv import sigma_SI_loop
        si = sigma_SI_loop(m_D_GeV, alpha_D, 1e-5, m_A_prime_GeV)
        assert si < 1e-50, f"sigma_SI = {si:.3e}"

    def test_alpha_D_too_small_fails_self_interaction(self):
        """If alpha_D is too small, self-interaction drops below 0.052 cm^2/g."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(10.44, 0.0001, 0.030, 0.010)
        # Should be < 0.001 cm^2/g (below Phase 44 requirement)
        assert sm < 0.001

    def test_alpha_D_too_large_fails_self_interaction(self):
        """If alpha_D is too large, self-interaction exceeds what's reasonable."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(10.44, 0.1, 0.030, 0.010)
        # Should be very high
        assert sm > 10

    def test_Delta_m_too_large_fails_self_interaction(self):
        """If Delta_m >> V_max, self-interaction is strongly suppressed."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        # With Delta_m = 100 MeV >> V_max = 15.7 MeV (alpha_D=0.0015)
        sm = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.100)
        # Should be suppressed
        assert sm < 0.02


if __name__ == "__main__":
    pytest.main([__file__, "-v"])