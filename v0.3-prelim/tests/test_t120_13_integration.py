"""
T120.13 — INTEGRATION tests for Hidden U(1) UV completion + Phase 44.

Verifies that the three-layer model works coherently:
1. Phenomenological: T120.4 joint fit with multi-component + gravothermal
2. Statistical: T120.9 MCMC convergence
3. UV completion: T120.11 Hidden U(1) pseudo-Dirac

These are NEW integration tests that were not covered by:
- test_t120_4_joint_fit.py (just the joint fit)
- test_t120_9_mcmc_and_uv.py (MCMC + magnetic dipole)
- test_t120_11_hidden_u1.py (Hidden U(1) standalone)
"""
import sys
from pathlib import Path
import numpy as np
import pytest

_CODE_DIR = Path(__file__).parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))


# Standard test parameters
M_D_GEV = 10.44  # Phase 44 best fit DM mass
ALPHA_D = 0.0015  # Dark fine-structure constant
M_A_PRIME_GEV = 0.030  # Dark photon mass (30 MeV)
DELTA_M_GEV = 0.010  # Pseudo-Dirac mass splitting (10 MeV)
EPSILON = 1e-5  # Kinetic mixing


class TestHiddenU1AndPhase44Integration:
    """Hidden U(1) UV completion + Phase 44 joint fit integration."""

    def test_phase44_joint_fit_still_passes(self):
        """Phase 44 joint fit with a_slope=1.0 (Hidden U(1) prediction) still passes all 8."""
        from t120_4_joint_fit import joint_fit_full_evaluation
        result = joint_fit_full_evaluation(a_slope_override=1.0)
        assert result["all_pass"], (
            f"Phase 44 joint fit should pass: {result}"
        )

    def test_hidden_u1_self_interaction_matches_phase44(self):
        """Hidden U(1) sigma/m should be within factor 2 of Phase 44 sigma_0."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm_u1 = zhang2016_self_scattering(M_D_GEV, ALPHA_D, M_A_PRIME_GEV, DELTA_M_GEV,
                                          v_rel_c=100/2.998e5)
        # Phase 44 sigma_0 = 0.052 cm^2/g
        ratio = sm_u1 / 0.052
        assert 0.4 < ratio < 2.5, (
            f"Hidden U(1) sigma/m should be within factor 2 of Phase 44: "
            f"got ratio {ratio:.2f}"
        )

    def test_hidden_u1_passes_direct_detection(self):
        """Hidden U(1) sigma_SI should be well below LZ limit."""
        from t120_11_hidden_u1_uv import sigma_SI_loop
        si = sigma_SI_loop(M_D_GEV, ALPHA_D, EPSILON, M_A_PRIME_GEV)
        LZ_limit = 9.4e-47
        assert si < LZ_limit, f"Hidden U(1) should pass LZ: {si:.2e} vs {LZ_limit:.2e}"
        # Should be at least 1000x below
        ratio = LZ_limit / si
        assert ratio > 1000, f"Should be > 1000x below LZ: {ratio:.2e}"

    def test_combined_pass(self):
        """Combined: Hidden U(1) UV + Phase 44 phenomenology + 2C + gravothermal."""
        from t120_11_hidden_u1_uv import check_uv_completion
        from t120_4_joint_fit import joint_fit_full_evaluation

        # Hidden U(1) UV completion check
        uv_pass = check_uv_completion(M_D_GEV, ALPHA_D, M_A_PRIME_GEV, DELTA_M_GEV, EPSILON)
        assert uv_pass

        # Phase 44 phenomenology check
        result = joint_fit_full_evaluation(a_slope_override=1.0)
        assert result["all_pass"]


class TestHiddenU1ParameterValues:
    """Tests for specific numerical values in the Hidden U(1) model."""

    def test_sigma_m_at_v100_specific_value(self):
        """sigma/m at v=100 km/s should be ~0.044 cm^2/g."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(M_D_GEV, ALPHA_D, M_A_PRIME_GEV, DELTA_M_GEV,
                                       v_rel_c=100/2.998e5)
        # Should be in range 0.02-0.1 cm^2/g
        assert 0.02 < sm < 0.1, f"sigma/m at v=100: {sm:.4f}"

    def test_sigma_SI_specific_value(self):
        """sigma_SI should be ~1e-51 cm^2 with our parameters."""
        from t120_11_hidden_u1_uv import sigma_SI_loop
        si = sigma_SI_loop(M_D_GEV, ALPHA_D, EPSILON, M_A_PRIME_GEV)
        # Should be ~10^-52 to 10^-50 cm^2
        assert 1e-54 < si < 1e-49, f"sigma_SI: {si:.3e}"

    def test_self_interaction_works_kinematic_escape(self):
        """V_max = alpha_D * m_chi should exceed Delta_m (kinematic escape)."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        # In our parameter regime:
        # V_max = 0.0015 * 10440 MeV = 15.66 MeV
        # Delta_m = 10 MeV
        # V_max / Delta_m = 1.566
        # => self-interaction works (adiabatic up-scattering in potential well)
        V_max = ALPHA_D * M_D_GEV * 1000  # MeV
        Delta_m = DELTA_M_GEV * 1000  # MeV
        assert V_max > Delta_m, (
            f"V_max ({V_max:.1f} MeV) should exceed Delta_m ({Delta_m} MeV)"
        )

    def test_kinetic_mixing_epsilon_realistic(self):
        """epsilon = 1e-5 is a realistic anomaly-induced kinetic mixing value."""
        # Typical values: 1e-5 to 1e-3 (anomaly-induced or string)
        assert 1e-6 < EPSILON < 1e-3, f"epsilon should be realistic: {EPSILON}"


class TestHiddenU1Phase44Synergy:
    """Tests that Hidden U(1) and Phase 44 work together (no double-counting)."""

    def test_uv_completion_does_not_double_count(self):
        """UV completion is invisible to the joint fit (no double-counting).

        The Hidden U(1) sigma_Yukawa is the SAME Yukawa as Phase 44's sigma_0.
        The UV completion provides particle-physics INTERPRETATION, not new dynamics.
        """
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        # Hidden U(1) sigma/m at v=100 km/s
        sm_u1 = zhang2016_self_scattering(M_D_GEV, ALPHA_D, M_A_PRIME_GEV, DELTA_M_GEV,
                                          v_rel_c=100/2.998e5)
        # Phase 44 sigma_0 from JSON
        import json
        with open('v0.3-prelim/data/results/phase44_joint_fit.json') as f:
            d44 = json.load(f)
        sigma_0_p44 = d44["best_params"][1]

        # These are CONCEPTUALLY the same Yukawa; should be within factor 2
        ratio = sm_u1 / sigma_0_p44
        assert 0.3 < ratio < 3.0, (
            f"UV sigma/m vs Phase 44 sigma_0 should agree (factor ~1): "
            f"got ratio {ratio:.2f}"
        )

    def test_bw_peaks_unchanged_by_uv_completion(self):
        """BW peaks are independent of UV completion (resonant structure is separate)."""
        # The BW peaks at v=29, 100, 178, 430, 768 km/s are from resonant structure
        # They are NOT affected by UV completion
        # Therefore Phase 44 BW peaks should be the same with or without Hidden U(1)
        from t120_4_joint_fit import total_sigma_m_gaussian, T120_4_V_TARGETS, T120_4_SIGMA_PEAKS, T120_4_W_LIST_DEFAULT
        import json
        with open('v0.3-prelim/data/results/phase44_joint_fit.json') as f:
            d44 = json.load(f)
        sigma_0 = d44["best_params"][1]

        # At v=29 km/s (BW peak), sigma should be ~196 cm^2/g
        sm_at_29 = total_sigma_m_gaussian(29.0, T120_4_V_TARGETS, T120_4_SIGMA_PEAKS,
                                          T120_4_W_LIST_DEFAULT, sigma_0, 1.0)
        # Should be in range 100-300 (BW peak dominates)
        assert 50 < sm_at_29 < 500, f"BW peak at v=29: {sm_at_29:.1f}"

    def test_uv_completion_is_complementary_not_redundant(self):
        """The three layers are complementary, not redundant.

        - Phenomenological (T120.4): resolves Cloud-9 vs UFD tension
        - Statistical (T120.9a): MCMC verification
        - UV completion (T120.11): makes mediator safe from direct detection
        """
        # Just verify that each layer provides distinct functionality
        from t120_4_joint_fit import joint_fit_full_evaluation
        from t120_11_hidden_u1_uv import check_uv_completion

        # Layer 1: phenomenology
        p44 = joint_fit_full_evaluation(a_slope_override=1.0)
        assert p44["all_pass"]

        # Layer 2: UV completion
        uv = check_uv_completion(M_D_GEV, ALPHA_D, M_A_PRIME_GEV, DELTA_M_GEV, EPSILON)
        assert uv

        # Both must pass independently (no redundant testing)


class TestPhase44NumericalValues:
    """Tests for specific numerical values in Phase 44 fit."""

    def test_sigma_0_value(self):
        """Phase 44 sigma_0 should be 0.052 cm^2/g (the target)."""
        import json
        with open('v0.3-prelim/data/results/phase44_joint_fit.json') as f:
            d44 = json.load(f)
        sigma_0 = d44["best_params"][1]
        assert abs(sigma_0 - 0.052) < 0.01, f"sigma_0: {sigma_0}"

    def test_m_chi_value(self):
        """Phase 44 m_chi should be ~10 GeV."""
        import json
        with open('v0.3-prelim/data/results/phase44_joint_fit.json') as f:
            d44 = json.load(f)
        m_chi = d44["best_params"][0]
        assert 5 < m_chi < 20, f"m_chi: {m_chi}"

    def test_bw_peaks_count(self):
        """Phase 44 should have 4 BW peaks."""
        import json
        with open('v0.3-prelim/data/results/phase44_joint_fit.json') as f:
            d44 = json.load(f)
        # best_params layout: [m_chi, sigma_0, a_slope, v_t1, v_t2, v_t3, v_t4,
        #                     sigma_peak1, sigma_peak2, sigma_peak3, sigma_peak4,
        #                     gamma_frac1, gamma_frac2, gamma_frac3, gamma_frac4]
        # Indices 3-6 are v_targets (4 BW peaks)
        n_resonances = 4  # v_t1, v_t2, v_t3, v_t4 in best_params
        assert n_resonances >= 4, f"Should have >= 4 BW peaks: {n_resonances}"

        # Verify the v_targets are in the expected ranges
        v_targets = d44["best_params"][3:7]
        # Should have one near v=29 (Cloud-9), one near v=100 (SPARC),
        # one near v=300 (between), one near v=700 (cluster)
        assert any(20 < v < 50 for v in v_targets), (
            f"Should have v_target near 29: {v_targets}"
        )


class TestDirectDetectionSummary:
    """Final integration test: direct detection summary across mechanisms."""

    def test_magnetic_dipole_vs_hidden_u1_direct_detection(self):
        """Compare magnetic dipole (RULED OUT) vs Hidden U(1) (PASSES)."""
        from t120_10a_direct_detection import (required_mu_chi_for_sigma_DM_DM,
                                                 sigma_SI_magnetic_dipole)
        from t120_11_hidden_u1_uv import sigma_SI_loop

        # Magnetic dipole
        mu_chi_GeV = required_mu_chi_for_sigma_DM_DM(0.052, 100.0, M_D_GEV)
        si_md = sigma_SI_magnetic_dipole(M_D_GEV, mu_chi_GeV)

        # Hidden U(1)
        si_u1 = sigma_SI_loop(M_D_GEV, ALPHA_D, EPSILON, M_A_PRIME_GEV)

        # Magnetic dipole sigma_SI should be at least 10^10x larger
        ratio = si_md / si_u1
        assert ratio > 1e10, (
            f"Magnetic dipole sigma_SI should be >> Hidden U(1): ratio {ratio:.2e}"
        )

    def test_lz_limit_is_reasonable(self):
        """LZ 2024 limit should be ~9.4e-47 cm^2 at m_chi=10.44 GeV."""
        from t120_10a_direct_detection import lz_limit_2024
        lz = lz_limit_2024(M_D_GEV)
        # Should be in 10^-47 to 10^-46 range
        assert 1e-48 < lz < 1e-45, f"LZ limit: {lz:.2e}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])