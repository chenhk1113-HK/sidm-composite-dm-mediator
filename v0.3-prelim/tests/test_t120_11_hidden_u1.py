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

F18 / D9 note (2026-11-05): the class TestPseudoDiracCompatibityWithV113 used to
assert Cloud-9 sigma/m ~128 and 'all 8 constraints still pass'. Measured through
v0.3-prelim/code/t120_constraint_scoreboard.py the Cloud-9 arm is 99.801690
(MARGINAL, 0.198% short of >= 100) and the a_slope=1.0 tally is 6 PASS / 1
MARGINAL / 1 FAIL with all_pass False. See docs/INTEGRITY_FINDINGS_2026-11-04.md.
"""
import sys
from pathlib import Path
import numpy as np
import pytest

_CODE_DIR = Path(__file__).parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))

# F18/D9: artifact reads are anchored to this file, never to the current
# working directory (the same defect class as the T90 CWD-relative paths).
_RESULTS_DIR = Path(__file__).resolve().parents[1] / "data" / "results"


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


class TestHiddenU1SigmaVCurve:
    """Tests for the full σ/m(v) curve in 3-30 km/s window (comment12 point 2)."""

    def test_sigma_v_at_extreme_ufd(self):
        """σ/m at v=3 km/s (extreme UFD) should be < 0.8 cm²/g."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.010, v_rel_c=3/2.998e5)
        assert sm < 0.8, f"sigma/m at v=3 should be < 0.8: got {sm:.3f}"

    def test_sigma_v_at_ufd(self):
        """σ/m at v=5 km/s (UFD) should be < 0.8 cm²/g."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.010, v_rel_c=5/2.998e5)
        assert sm < 0.8, f"sigma/m at v=5 should be < 0.8: got {sm:.3f}"

    def test_sigma_v_at_dsph(self):
        """σ/m at v=15 km/s (dSph) should be < 0.8 cm²/g."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.010, v_rel_c=15/2.998e5)
        assert sm < 0.8, f"sigma/m at v=15 should be < 0.8: got {sm:.3f}"

    def test_sigma_v_at_sparc(self):
        """σ/m at v=100 km/s (SPARC) should be in [0.05, 0.5] cm²/g."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.010, v_rel_c=100/2.998e5)
        assert 0.05 < sm < 0.5, f"sigma/m at v=100 should be in band: got {sm:.3f}"

    def test_sigma_v_at_cloud9_yukawa_only(self):
        """σ/m from Yukawa at v=28 should be < 0.8 (BW peak handles Cloud-9)."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.010, v_rel_c=28/2.998e5)
        assert sm < 0.8, f"Yukawa sigma/m at v=28 should be < 0.8: got {sm:.3f}"

    def test_sigma_v_velocity_scaling(self):
        """σ/m should decrease with increasing v (1/v dependence)."""
        from t120_11_hidden_u1_uv import zhang2016_self_scattering
        sm_low = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.010, v_rel_c=10/2.998e5)
        sm_high = zhang2016_self_scattering(10.44, 0.0015, 0.030, 0.010, v_rel_c=100/2.998e5)
        assert sm_low > sm_high, (
            f"sigma/m should decrease with v: {sm_low:.3f} (v=10) > {sm_high:.3f} (v=100)?"
        )


class TestExcitedStateAbundance:
    """Tests for χ_2 excited state abundance (comment12 point 3)."""

    def test_excited_state_zero_at_BBN(self):
        """n_χ2/n_χ1 at BBN (T=1 MeV, Δm=10 MeV) should be exponentially small."""
        import numpy as np
        Delta_m_eV = 10e6  # 10 MeV in eV
        T_BBN_eV = 1e6  # 1 MeV
        ratio = np.exp(-Delta_m_eV / T_BBN_eV)
        assert ratio < 1e-3, (
            f"Excited state should be negligible at BBN: n_chi2/n_chi1 = {ratio:.2e}"
        )

    def test_excited_state_zero_at_recombination(self):
        """n_χ2/n_χ1 at recombination should be ~0 (Δm >> T)."""
        import numpy as np
        Delta_m_eV = 10e6
        T_recomb_eV = 0.26
        # exp(-4e7) is effectively 0
        log_ratio = -Delta_m_eV / T_recomb_eV
        assert log_ratio < -100, (
            f"log ratio should be very negative at recombination: {log_ratio:.2e}"
        )

    def test_excited_state_zero_today(self):
        """n_χ2/n_χ1 today is essentially 0."""
        import numpy as np
        Delta_m_eV = 10e6
        T_today_eV = 1e-4  # ~1 K in eV (CMB temperature)
        log_ratio = -Delta_m_eV / T_today_eV
        assert log_ratio < -1e10


class TestPseudoDiracCompatibityWithV113:
    """Tests that pseudo-Dirac UV is COMPATIBLE with v1.13.1 phenomenology."""

    def test_pseudo_dirac_does_not_break_cloud9(self):
        """RETIRED (F18/D9): 'pseudo-Dirac Yukawa + BW peaks give Cloud-9 sigma/m ~ 128'.

        Measured in this task with the repo venv through the same producers the
        scoreboard calls (sigma_0 = 0.05156371513303437 cm^2/g from
        phase44_joint_fit.json, default w_list = [3, 30, 30, 50, 50]):

            sigma_HH(v=28)               = 177.337429 cm^2/g
            f_H_at_r(0.05, core_forming) =   0.750186   (this test's old comment said 0.85)
            sigma_eff = f_H^2 * sigma_HH =  99.801690 cm^2/g

        99.801690 is 0.198% BELOW the stated >= 100 floor, so it scores MARGINAL,
        not PASS. The floor is not moved; the '~128' claim is retired. The honest
        statement is: the pseudo-Dirac arm lands on a Cloud-9 near-miss.
        """
        import json
        from phase44_two_component import f_H_at_r
        from t120_4_joint_fit import (total_sigma_m_gaussian, T120_4_V_TARGETS,
                                      T120_4_SIGMA_PEAKS, T120_4_W_LIST_DEFAULT)
        from t120_constraint_scoreboard import four_constraint_scoreboard

        sigma_0 = json.loads((_RESULTS_DIR / "phase44_joint_fit.json").read_text())["best_params"][1]
        sigma_HH = total_sigma_m_gaussian(28.0, T120_4_V_TARGETS, T120_4_SIGMA_PEAKS,
                                          T120_4_W_LIST_DEFAULT, sigma_0, 1.0)
        f_H = f_H_at_r(0.05, "core_forming")
        sigma_eff = f_H * f_H * sigma_HH

        assert sigma_HH == pytest.approx(177.33742881952278, rel=1e-9)
        assert f_H == pytest.approx(0.7501856343179664, rel=1e-9)
        assert sigma_eff == pytest.approx(99.80168969102034, rel=1e-9), sigma_eff
        assert sigma_eff < 100.0, f"measured Cloud-9 is short of the floor: {sigma_eff}"

        obs = four_constraint_scoreboard(a_slope_override=1.0)["observations"]["Cloud-9"]
        assert obs["verdict"] == "MARGINAL", obs
        assert obs["value"] == pytest.approx(99.80168969102034, rel=1e-9)

    def test_pseudo_dirac_does_not_break_dsph(self):
        """Pseudo-Dirac + BW peaks + gravothermal keeps dSph under the 0.8 ceiling.

        Numbers corrected to measured values (F18/D9): f_H_at_r(0.20, core_collapsed)
        is 0.750226 (this test's old comment claimed 0.30) and sigma_eff = 0.198717
        cm^2/g (the old comment claimed ~0.03). The verdict survives — 0.198717 is a
        clean PASS — but it has 4x less margin than the retired comment implied.
        """
        import json
        from phase44_two_component import f_H_at_r
        from t120_4_joint_fit import (total_sigma_m_gaussian, T120_4_V_TARGETS,
                                      T120_4_SIGMA_PEAKS, T120_4_W_LIST_DEFAULT)
        from t120_constraint_scoreboard import four_constraint_scoreboard

        sigma_0 = json.loads((_RESULTS_DIR / "phase44_joint_fit.json").read_text())["best_params"][1]
        sigma_HH = total_sigma_m_gaussian(15.0, T120_4_V_TARGETS, T120_4_SIGMA_PEAKS,
                                          T120_4_W_LIST_DEFAULT, sigma_0, 1.0)
        f_H = f_H_at_r(0.20, "core_collapsed")
        sigma_eff = f_H * f_H * sigma_HH

        assert sigma_HH == pytest.approx(0.353061164104642, rel=1e-9)
        assert f_H == pytest.approx(0.7502259041964671, rel=1e-9)
        assert sigma_eff == pytest.approx(0.1987165598243989, rel=1e-9), sigma_eff

        obs = four_constraint_scoreboard(a_slope_override=1.0)["observations"]["dSph"]
        assert obs["verdict"] == "PASS", obs
        assert obs["value"] == pytest.approx(0.1987165598243989, rel=1e-9)

    def test_uv_completion_does_not_change_observables(self):
        """RETIRED (F18/D9): 'therefore all 8 observational constraints still pass'.

        What survives: the UV layer changes no number — every observable equals the
        producer's own value at a_slope = 1.0, which is what this test verifies.
        What is retired: 'all 8 pass'. Measured at the Hidden U(1) prediction
        a_slope = 1.0 the tally is 6 PASS / 1 MARGINAL / 1 FAIL:
          v3.0_extreme_UFD = 0.968611 (1.210764x the 0.8 ceiling -> FAIL)
          v28.0_Cloud-9    = 99.801690 (0.198% short of >= 100 -> MARGINAL)
        """
        from t120_4_joint_fit import joint_fit_full_evaluation
        from t120_constraint_scoreboard import constraint_scoreboard

        r = joint_fit_full_evaluation(a_slope_override=1.0)
        sb = constraint_scoreboard(a_slope_override=1.0)
        s = sb["summary"]

        assert (s["n_pass"], s["n_marginal"], s["n_fail"], s["n_total"]) == (6, 1, 1, 8), s
        assert bool(r["all_pass"]) is False, f"all_pass unexpectedly True: {r}"
        # The UV-completion claim proper: observables are exactly the producer's.
        for key, obs in sb["observations"].items():
            assert float(r[key]) == pytest.approx(obs["value"], rel=1e-12), key
        assert r["v3.0_extreme_UFD"] == pytest.approx(0.9686107942907997, rel=1e-9)
        assert r["v28.0_Cloud-9"] == pytest.approx(99.80168969102034, rel=1e-9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])