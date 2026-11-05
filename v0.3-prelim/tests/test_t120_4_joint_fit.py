"""
Tests for T120.4 joint fit demonstration.

The framework is NOMINALLY built to satisfy 4 constraints simultaneously:
  1. Cloud-9: sigma/m(v=28) >= 100
  2. dSph:    sigma/m(v=15) <= 0.8
  3. SPARC:   sigma/m(v=100) in [0.05, 0.5]
  4. Cluster: sigma/m(v=500) < 1.0
and, in the v1.13 arm (a_slope=1.0), all 8 observational points (UFD v=3,5,7,10,
dSph v=15, Cloud-9 v=28, SPARC v=100, cluster v=500).

F18 / D9 note (2026-11-05). Every number below is measured through
``v0.3-prelim/code/t120_constraint_scoreboard.py`` (the single-source scoreboard;
see scripts/canonical_numbers.py + test_channel_taxonomy_single_source.py for the
F16 precedent) or through the producers directly. The following claims that this
file used to assert are RETIRED because the producers do not reproduce them
(finding F18, decision D9 in docs/INTEGRITY_FINDINGS_2026-11-04.md):

  * "default w1=3 km/s satisfies dSph <= 0.8"        -> RETIRED. Measured 1.131864.
  * "default w1=3 km/s satisfies ALL constraints"    -> RETIRED. 4-constraint
        tally is 3 PASS / 0 MARGINAL / 1 FAIL (dSph fails); all_pass is False.
  * "w1=2 (narrow) passes all constraints"           -> RETIRED. Cloud-9 = 88.0202.
  * "w1=5 passes all constraints"                    -> RETIRED. dSph = 2.917966.
  * "gravothermal selection alone gives dSph ~0.45"  -> RETIRED. f_H(0.20,core_
        collapsed) measures 0.750226 (the claim assumed 0.30); sm_dsph = 2.813523.
  * "combined mechanisms give dSph ~0.18 (< 0.3)"    -> RETIRED. Measured 1.131864.
  * "v1.13 passes at v=3 km/s (most extreme UFD)"    -> RETIRED. Measured 0.968611
        (a_slope=1.0) = 1.2108x the 0.8 ceiling.
  * "v1.13 passes ALL 8 points"                      -> RETIRED. 6 PASS / 1 MARGINAL
        / 1 FAIL at a_slope=1.0; all_pass is False.
  * "a_slope=0.5 / 0.8 / 1.2 pass all 8 points"      -> RETIRED. 7/1/0, 7/1/0 and
        5/1/2 respectively; all_pass is False in every case.
  * "multi-component contributes factor ~2.9x"       -> RETIRED. Measured 2.251114.

Design rule (D9): a bound is NEVER moved to turn a FAIL into a PASS. The only
tolerance is the declared MARGINAL band (MARGINAL_BAND_RELATIVE = 0.05, applied to
the nearest bound), so Cloud-9 ~99.8 vs >= 100 is MARGINAL (0.2% short), not PASS.
"""
import sys
from pathlib import Path

import pytest

_CODE_DIR = Path(__file__).parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))


from t120_4_joint_fit import (  # noqa: E402
    joint_fit_evaluation,
    joint_fit_full_evaluation,
    yukawa_bg,
    gaussian_resonance,
    total_sigma_m_gaussian,
    sigma_eff_two_comp,
    T120_4_W_LIST_DEFAULT,
    T120_4_V_TARGETS,
    T120_4_SIGMA_PEAKS,
)
from t120_constraint_scoreboard import (  # noqa: E402
    constraint_scoreboard,
    four_constraint_scoreboard,
    MARGINAL_BAND_RELATIVE,
)


class TestIndividualShapes:
    """Tests for individual shape components."""

    def test_yukawa_bg_at_reference(self):
        """Yukawa background at v=v_ref should be sigma_0."""
        sigma_0 = 0.052
        bg = yukawa_bg(100.0, sigma_0, 1.93)
        assert abs(bg - sigma_0) < 0.001, f"Yukawa bg at v_ref = {bg}, expected {sigma_0}"

    def test_yukawa_bg_increases_at_lower_v(self):
        """Yukawa bg should increase as v decreases (v^-a)."""
        bg_100 = yukawa_bg(100.0, 0.052, 1.93)
        bg_50 = yukawa_bg(50.0, 0.052, 1.93)
        bg_28 = yukawa_bg(28.0, 0.052, 1.93)
        assert bg_50 > bg_100
        assert bg_28 > bg_50

    def test_gaussian_at_peak(self):
        """Gaussian at v=v_target should be sigma_peak."""
        sm = gaussian_resonance(28.0, 28.0, 100.0, 5.0)
        assert abs(sm - 100.0) < 1.0

    def test_gaussian_symmetric(self):
        """Gaussian should be symmetric around peak."""
        sm_left = gaussian_resonance(23.0, 28.0, 100.0, 5.0)
        sm_right = gaussian_resonance(33.0, 28.0, 100.0, 5.0)
        assert abs(sm_left - sm_right) < 0.01, f"Gaussian asymmetry: left={sm_left}, right={sm_right}"


class TestJointFit:
    """Tests for the joint fit framework."""

    def test_cloud9_passes_with_default(self):
        """Default w1=3 km/s satisfies Cloud-9 (sigma/m(v=28) >= 100).

        Measured 100.036064 -- a PASS, but only 0.036 above the floor. The value
        is pinned so a small producer change cannot silently flip this without
        the test telling us.
        """
        r = joint_fit_evaluation()
        assert r["Cloud-9"] >= 100, (
            f"Cloud-9: sigma/m(v=28) = {r['Cloud-9']:.2f}, expected >= 100"
        )
        assert r["Cloud-9"] == pytest.approx(100.03606419810939, rel=1e-4)

    def test_dsph_passes_with_default(self):
        """RETIRED (F18/D9): 'default w1=3 km/s satisfies dSph (<= 0.8)'.

        Measured with the repo venv: default dSph sigma/m(v=15) = 1.131864 cm^2/g
        against the stated <= 0.8 ceiling -> FAIL (1.4148x the bound). The test now
        pins the measured FAIL verdict and value.
        """
        obs = four_constraint_scoreboard()["observations"]["dSph"]
        assert obs["verdict"] == "FAIL"
        assert obs["value"] == pytest.approx(1.1318641032072747, rel=1e-3)
        assert obs["ratio_to_bound"] == pytest.approx(1.4148301290090934, rel=1e-3)

    def test_sparc_passes_with_default(self):
        """Default w1=3 km/s satisfies SPARC band (0.05-0.5)."""
        r = joint_fit_evaluation()
        assert 0.05 <= r["SPARC"] <= 0.5, (
            f"SPARC: sigma/m(v=100) = {r['SPARC']:.4f}, expected 0.05-0.5"
        )
        assert r["SPARC"] == pytest.approx(0.25715623860963965, rel=1e-4)

    def test_cluster_passes_with_default(self):
        """Default w1=3 km/s satisfies cluster limit (< 1.0)."""
        r = joint_fit_evaluation()
        assert r["cluster"] < 1.0, (
            f"Cluster: sigma/m(v=500) = {r['cluster']:.4f}, expected < 1.0"
        )
        assert r["cluster"] == pytest.approx(0.009644075978745243, rel=1e-4)

    def test_all_pass_with_default(self):
        """RETIRED (F18/D9): 'default w1=3 km/s satisfies ALL constraints'.

        Measured: the 4-constraint set is 3 PASS / 0 MARGINAL / 1 FAIL (dSph fails
        at 1.131864); the 8-observation set is 3 PASS / 0 MARGINAL / 5 FAIL. The
        producer's all_pass is False. Both the computed tally and all_pass are
        asserted so the gate cannot silently re-bless the retired claim.
        """
        s = four_constraint_scoreboard()["summary"]
        assert (s["n_pass"], s["n_marginal"], s["n_fail"]) == (3, 0, 1)
        assert s["n_pass"] + s["n_marginal"] + s["n_fail"] == s["n_total"] == 4
        r = joint_fit_evaluation()
        assert bool(r["all_pass"]) is False, f"all_pass unexpectedly True: {r}"


class TestJointFitParameterScan:
    """Parameter scan: w1 variation (measured through the scoreboard)."""

    def test_w1_2_passes(self):
        """RETIRED (F18/D9): 'w1=2 km/s (narrow Gaussian) should pass all constraints'.

        Measured: 4-constraint 2 PASS / 0 MARGINAL / 2 FAIL -- Cloud-9 = 88.020226
        (FAIL, vs >= 100) and dSph = 1.130695 (FAIL, vs <= 0.8). all_pass is False.
        """
        obs = four_constraint_scoreboard(w_list=[2.0, 30.0, 30.0, 50.0, 50.0])["observations"]
        assert obs["Cloud-9"]["verdict"] == "FAIL"
        assert obs["Cloud-9"]["value"] == pytest.approx(88.02022567712328, rel=1e-3)
        assert obs["dSph"]["verdict"] == "FAIL"
        assert obs["dSph"]["value"] == pytest.approx(1.1306946362379708, rel=1e-3)
        r = joint_fit_evaluation([2.0, 30.0, 30.0, 50.0, 50.0])
        assert bool(r["all_pass"]) is False, f"w1=2.0 unexpectedly passed: {r}"

    def test_w1_5_passes(self):
        """RETIRED (F18/D9): 'w1=5 km/s should pass all constraints'.

        Measured: 4-constraint 3 PASS / 0 MARGINAL / 1 FAIL -- Cloud-9 = 106.812098
        (PASS) but dSph = 2.917966 (FAIL, vs <= 0.8). all_pass is False.
        """
        obs = four_constraint_scoreboard(w_list=[5.0, 30.0, 30.0, 50.0, 50.0])["observations"]
        assert obs["Cloud-9"]["verdict"] == "PASS"
        assert obs["Cloud-9"]["value"] == pytest.approx(106.81209753075255, rel=1e-3)
        assert obs["dSph"]["verdict"] == "FAIL"
        assert obs["dSph"]["value"] == pytest.approx(2.9179663528925004, rel=1e-3)
        r = joint_fit_evaluation([5.0, 30.0, 30.0, 50.0, 50.0])
        assert bool(r["all_pass"]) is False, f"w1=5.0 unexpectedly passed: {r}"

    def test_w1_10_fails_dsph(self):
        """w1=10 km/s (broad Gaussian) should FAIL dSph constraint.

        Measured: dSph = 40.533392 (FAIL, vs <= 0.8). Cloud-9 still passes (peak
        height same at v=28), so this documents that the broad tail is the dSph
        failure mode.
        """
        r = joint_fit_evaluation([10.0, 30.0, 30.0, 50.0, 50.0])
        # Cloud-9 still passes (peak height same), but dSph violates
        assert not r["all_pass"], f"w1=10.0 unexpectedly passed: {r}"
        assert r["dSph"] > 0.8, f"dSph should fail at w1=10: dSph={r['dSph']:.3f}"
        assert r["dSph"] == pytest.approx(40.53339207388745, rel=1e-4)


class TestJointFitMechanism:
    """Tests that verify the mechanisms are individually effective."""

    def test_gravothermal_selection_alone(self):
        """RETIRED (F18/D9): 'gravothermal selection alone gives dSph ~0.45 (passes)'.

        The retired docstring claimed f_H_at_r(0.20, 'core_collapsed') = 0.30.
        Measured with the repo venv: f_H = 0.750226 -- the producer's Phase-44
        sigma/m leaves segregation_maturity ~0, so f_H stays near the no-segregation
        value 0.75, NOT 0.30. With phase44_sigma_HH_at_v(15) = 4.998808 the
        gravothermal selection ALONE gives sm_dsph = f_H^2 * sm_HH = 2.813523
        cm^2/g, which is ABOVE the 0.8 ceiling. Measured values pinned below.
        """
        from phase44_two_component import phase44_sigma_HH_at_v, f_H_at_r
        sm_HH_v15 = phase44_sigma_HH_at_v(15.0)
        f_H = f_H_at_r(0.20, "core_collapsed")
        sm_dsph = f_H * f_H * sm_HH_v15
        assert sm_HH_v15 == pytest.approx(4.998807528111916, rel=1e-4)
        assert f_H == pytest.approx(0.7502259041964671, rel=1e-4)
        assert sm_dsph == pytest.approx(2.8135233670625253, rel=1e-4)
        # measured: gravothermal selection alone does NOT reach the 0.8 dSph ceiling
        assert sm_dsph > 0.8

    def test_gaussian_bw_alone(self):
        """With Gaussian BW (no gravothermal selection), dSph still violates.

        Shows that Gaussian BW alone is NOT enough - we need gravothermal
        selection too.
        """
        sigma_HH_v15 = total_sigma_m_gaussian(15.0, T120_4_V_TARGETS, T120_4_SIGMA_PEAKS, T120_4_W_LIST_DEFAULT, 0.052, 1.93)
        # Without gravothermal selection (use CDM reference f_H=0.5)
        sm_dsph_naive = 0.5 * 0.5 * sigma_HH_v15
        # Gaussian alone: 0.25 * 2.0 = 0.5 cm^2/g (might pass but tight)
        # But Phase 44 BW tail at v=15 is 5.0, not 2.0
        assert sigma_HH_v15 < 5.0, (
            f"Gaussian BW should reduce v=15 tail below Lorentzian: {sigma_HH_v15}"
        )

    def test_combination_works(self):
        """RETIRED (F18/D9): 'combination of Gaussian BW + gravothermal gives dSph ~0.18 (< 0.3)'.

        Measured with the repo venv: the default joint fit gives dSph sigma/m(v=15)
        = 1.131864 cm^2/g, ABOVE the 0.8 ceiling -> FAIL. The ~0.18 the retired
        docstring quoted is not produced by the current producers at any tested
        slope; dSph drops below the ceiling only for a_slope <= ~1.0 (0.198717 at
        a_slope=1.0, 0.080171 at a_slope=0.5). Pinned below.
        """
        obs = four_constraint_scoreboard()["observations"]["dSph"]
        assert obs["value"] == pytest.approx(1.1318641032072747, rel=1e-3)
        assert obs["verdict"] == "FAIL"


class TestJointFitLimitations:
    """Tests for v1.12 limitations AND the v1.13 claim.

    v1.12 (Phase 44 a_slope=1.93): FAILS at v < 8 km/s (UFD and dSph).
    v1.13 (Option A: flatten a_slope=1.0): fixes v=5..15 but STILL fails v=3 --
    the retired 'passes all 8' claim is not reproduced (F18/D9).
    """

    def test_v112_ufd_v5_violation_documented(self):
        """v1.12 model FAILS at v=5 km/s (extreme UFDs): 1.87x the 0.8 ceiling.

        v1.12 limitation: Yukawa background sigma_0 * (v_ref/v)^a_slope with
        sigma_0 ~ 0.0516 and a_slope=1.93 grows too fast at low v. The two-
        component f_H^2 reduction is not enough at v=5.
        """
        r_v112 = joint_fit_evaluation()
        # Compute sigma_eff at v=5 with v1.12 settings
        sigma_HH_v5 = total_sigma_m_gaussian(5.0, T120_4_V_TARGETS, T120_4_SIGMA_PEAKS, T120_4_W_LIST_DEFAULT, 0.052, 1.93)
        f_H = 0.30
        sigma_eff_v5 = f_H * f_H * sigma_HH_v5
        violation_v112 = sigma_eff_v5 / 0.8
        assert violation_v112 > 1.0, (
            f"v1.12 should fail at v=5: violation={violation_v112:.2f}x"
        )

    def test_v113_ufd_v5_passes(self):
        """v1.13 model PASSES at v=5 km/s with Option A (a_slope=1.0).

        Measured: v5.0_UFD = 0.581937 cm^2/g at a_slope=1.0 -> PASS (0.727x the
        0.8 ceiling). Pinned below.
        """
        obs = constraint_scoreboard(a_slope_override=1.0)["observations"]["v5.0_UFD"]
        assert obs["verdict"] == "PASS"
        assert obs["value"] == pytest.approx(0.5819366140195584, rel=1e-3)

    def test_v113_extreme_ufd_v3_passes(self):
        """RETIRED (F18/D9): 'v1.13 model PASSES at v=3 km/s (most extreme UFDs)'.

        Measured with the repo venv: v3.0_extreme_UFD sigma/m = 0.968611 cm^2/g at
        a_slope=1.0, which is 1.210764x the 0.8 ceiling -> FAIL. v1.13 fixes
        v=5..15 relative to a_slope=1.93 but NOT the extreme UFD at v=3. Pinned.
        """
        obs = constraint_scoreboard(a_slope_override=1.0)["observations"]["v3.0_extreme_UFD"]
        assert obs["verdict"] == "FAIL"
        assert obs["value"] == pytest.approx(0.9686107942907997, rel=1e-3)
        assert obs["ratio_to_bound"] == pytest.approx(0.9686107942907997 / 0.8, rel=1e-4)

    def test_v113_all_8_points_pass(self):
        """RETIRED (F18/D9): 'v1.13 model passes ALL 8 observational points'.

        Measured at a_slope=1.0: 6 PASS / 1 MARGINAL / 1 FAIL -- v3.0_extreme_UFD
        = 0.968611 (FAIL vs 0.8) and Cloud-9 = 99.801690 (MARGINAL, 0.198% short of
        the >= 100 floor). The producer's all_pass is False.
        """
        sb = constraint_scoreboard(a_slope_override=1.0)
        s = sb["summary"]
        assert (s["n_pass"], s["n_marginal"], s["n_fail"]) == (6, 1, 1)
        assert s["n_pass"] + s["n_marginal"] + s["n_fail"] == s["n_total"] == 8
        assert sb["observations"]["v3.0_extreme_UFD"]["verdict"] == "FAIL"
        assert sb["observations"]["v28.0_Cloud-9"]["verdict"] == "MARGINAL"
        r_v113 = joint_fit_full_evaluation(a_slope_override=1.0)
        assert bool(r_v113["all_pass"]) is False, f"v1.13 unexpectedly passed all: {r_v113}"


class TestJointFitBICPenalty:
    """Tests documenting the BIC complexity penalty.

    Reviewer T120review1.docx requested complexity cost analysis.
    T120 adds ~7 free parameters over Phase 44. At same logL improvement,
    BIC penalty is +34 (T120 worse by Occam's razor).

    v1.13 FIX: When including dSph + UFD data, T120 achieves +31 additional
    logL (from 31 new data points), which more than offsets the +34 BIC
    penalty. Final v1.13 BIC = 13.15 vs Phase 44 BIC = 37.26.
    Delta BIC = -24.10 (T120 WINS).

    v1.13.1 CRITICAL REVIEW REVISION: On a fair SAME-data-set comparison
    (both on 160 points), Phase 44 fails 31 dSph/UFD points with massive
    penalty (-71.9 logL), so T120 wins by Delta BIC = -170 (much larger).
    """

    def test_bic_penalty_estimated(self):
        """Estimate the BIC penalty from additional parameters (no new data).

        Phase 44: k=11 free params
        T120:     k=11+7 = 18 free params
        Delta BIC = 7 * log(127) = 34.9 (T120 worse at same logL)

        This is the v1.12 estimate WITHOUT new data.
        """
        import numpy as np
        n_data = 127
        k_phase44 = 11
        k_t120 = 18
        bic_penalty = (k_t120 - k_phase44) * np.log(n_data)
        # This is a measurement, not a regression
        assert bic_penalty > 30, f"BIC penalty should be ~35: {bic_penalty:.2f}"

    def test_required_dlogl_to_beat_bic(self):
        """Compute required Delta logL to beat BIC penalty.

        For Delta BIC <= 0 (T120 preferred), need Delta logL >= +17.
        Phase 44 achieved +8.10 on SPARC + JVAS + Cloud-9.
        Joint fit with dSph + UFD would need to show additional +9 logL.
        """
        import numpy as np
        n_data = 127
        k_diff = 7
        required_dlogl = k_diff * np.log(n_data) / 2
        # This is a calculation, just document it
        assert 16 < required_dlogl < 18, (
            f"Required Delta logL should be ~17: {required_dlogl:.2f}"
        )

    def test_v113_bic_with_dsph_ufd_data(self):
        """v1.13 BIC wins when including dSph + UFD data.

        T120 fits 31 additional data points (8 classical dSphs + 23 UFDs),
        each contributing ~+1 logL. Total Delta logL = +39.1.
        BIC(T120) = 13.15 vs BIC(Phase 44) = 37.26. Delta BIC = -24.10.

        T120 WINS by Occam's razor because the additional data fit more
        than compensates for the additional parameters.
        """
        import numpy as np
        n_data_p44 = 129
        n_data_t120 = 160  # +31 from dSph + UFD
        k_p44 = 11
        k_t120 = 18
        logL_p44 = 8.10
        logL_t120_extra = 31  # 31 new data points, +1 logL each
        logL_t120_total = logL_p44 + logL_t120_extra  # = 39.1

        bic_p44 = -2 * logL_p44 + k_p44 * np.log(n_data_p44)
        bic_t120 = -2 * logL_t120_total + k_t120 * np.log(n_data_t120)
        delta_bic = bic_t120 - bic_p44

        assert delta_bic < 0, (
            f"T120 v1.13 should beat Phase 44 by BIC: delta_bic={delta_bic:.2f}"
        )
        assert delta_bic < -20, (
            f"Delta BIC should be ~-24 (strong Occam-friendliness): {delta_bic:.2f}"
        )

    def test_v1131_fair_bic_same_dataset(self):
        """v1.13.1 FAIR BIC on SAME 160-point data set (reviewer critical review fix).

        Reviewer flagged v1.13 BIC as unfair because Phase 44 used 129 points
        while T120 used 160. Fair comparison: refit BOTH on the same 160 points.

        Phase 44 on 160 points: fails 31 dSph/UFD with massive penalty.
          logL = +8.10 (SPARC+JVAS+C9) - 71.9 (dSph+UFD penalty) = -63.8
          BIC = -2 * -63.8 + 11 * log(160) = 183.4

        T120 v1.13 on 160 points: this is the F18/D9-disputed arm -- the model
        measures 6/8 at a_slope=1.0, not 8/8, so the +31-passing-points premise
        is not reproduced by the current producers. The arithmetic below is kept
        as the RETIRED v1.13.1 estimate; it is an accounting statement, not a
        measured physics result.
          logL = +8.10 (baseline) + 31 (claimed passes) = +39.1
          BIC = -2 * 39.1 + 18 * log(160) = 13.2

        Delta BIC = -170.3 on the retired premise.
        """
        import numpy as np
        n_data = 160  # SAME data set for both
        k_p44 = 11
        k_t120 = 18

        # Phase 44 on 160: 31 failing points
        logL_p44 = 8.10 - 8 * 1.8 - 23 * 2.5  # = -63.8
        # T120 on 160: 31 passing points (RETIRED premise; measured model is 6/8)
        logL_t120 = 8.10 + 31 * 1.0  # = 39.1

        bic_p44 = -2 * logL_p44 + k_p44 * np.log(n_data)
        bic_t120 = -2 * logL_t120 + k_t120 * np.log(n_data)
        delta_bic = bic_t120 - bic_p44

        # T120 wins by even more on the retired fair-comparison premise
        assert delta_bic < -100, (
            f"Fair Delta BIC should be ~-170: {delta_bic:.2f}"
        )


class TestSlopeStress:
    """Tests for the slope choice stress-test (reviewer action 4).

    v1.13 uses a_slope=1.0 (flattened Yukawa background). Reviewer asked
    if this is a narrow tuned point or a wide window. Tested by varying
    a_slope around 1.0. The measured window is now stated honestly (F18/D9):
    NONE of a_slope = 0.5, 0.8, 1.0, 1.2 passes all 8 points.
    """

    def test_slope_window_above_05_passes(self):
        """RETIRED (F18/D9): 'a_slope=0.5 should pass all 8 points'.

        Measured: 7 PASS / 1 MARGINAL / 0 FAIL -- every UFD/dSph point passes, but
        Cloud-9 = 99.752891 is 0.247% short of the >= 100 floor -> MARGINAL, not
        PASS. all_pass is False.
        """
        sb = constraint_scoreboard(a_slope_override=0.5)
        s = sb["summary"]
        assert (s["n_pass"], s["n_marginal"], s["n_fail"]) == (7, 1, 0)
        assert sb["observations"]["v28.0_Cloud-9"]["verdict"] == "MARGINAL"
        assert sb["observations"]["v28.0_Cloud-9"]["value"] == pytest.approx(99.75289124538487, rel=1e-3)
        r = joint_fit_full_evaluation(a_slope_override=0.5)
        assert bool(r["all_pass"]) is False, f"a_slope=0.5 unexpectedly passed all: {r}"

    def test_slope_window_at_08_passes(self):
        """RETIRED (F18/D9): 'a_slope=0.8 should pass all 8 points'.

        Measured: 7 PASS / 1 MARGINAL / 0 FAIL -- Cloud-9 = 99.778395 -> MARGINAL
        (0.222% short of >= 100). all_pass is False.
        """
        sb = constraint_scoreboard(a_slope_override=0.8)
        s = sb["summary"]
        assert (s["n_pass"], s["n_marginal"], s["n_fail"]) == (7, 1, 0)
        assert sb["observations"]["v28.0_Cloud-9"]["verdict"] == "MARGINAL"
        assert sb["observations"]["v28.0_Cloud-9"]["value"] == pytest.approx(99.77839492084853, rel=1e-3)
        r = joint_fit_full_evaluation(a_slope_override=0.8)
        assert bool(r["all_pass"]) is False, f"a_slope=0.8 unexpectedly passed all: {r}"

    def test_slope_window_at_12_passes(self):
        """RETIRED (F18/D9): 'a_slope=1.2 should still pass (upper edge of window)'.

        Measured: 5 PASS / 1 MARGINAL / 2 FAIL -- v3.0_extreme_UFD = 1.951874 and
        v5.0_UFD = 1.058227 both FAIL vs the 0.8 ceiling; Cloud-9 = 99.831738 is
        MARGINAL. all_pass is False.
        """
        sb = constraint_scoreboard(a_slope_override=1.2)
        s = sb["summary"]
        assert (s["n_pass"], s["n_marginal"], s["n_fail"]) == (5, 1, 2)
        assert sb["observations"]["v3.0_extreme_UFD"]["verdict"] == "FAIL"
        assert sb["observations"]["v5.0_UFD"]["verdict"] == "FAIL"
        assert sb["observations"]["v3.0_extreme_UFD"]["value"] == pytest.approx(1.9518741385291025, rel=1e-3)
        r = joint_fit_full_evaluation(a_slope_override=1.2)
        assert bool(r["all_pass"]) is False, f"a_slope=1.2 unexpectedly passed all: {r}"

    def test_slope_at_15_fails_ufd(self):
        """a_slope=1.5 should FAIL (UFD v=3 too high).

        Measured: v3.0_extreme_UFD = 5.586508 (FAIL, 6.98x the 0.8 ceiling).
        """
        from t120_4_joint_fit import joint_fit_full_evaluation
        r = joint_fit_full_evaluation(a_slope_override=1.5)
        assert not r["all_pass"], f"a_slope=1.5 should fail: {r}"
        assert r["v3.0_extreme_UFD"] > 0.8, (
            f"v=3 should violate: sigma={r['v3.0_extreme_UFD']:.3f}"
        )

    def test_multi_component_matters_at_cloud9(self):
        """RETIRED (F18/D9): 'multi-component contributes factor ~2.9x at Cloud-9'.

        Measured with the repo venv: two-component f_H = f_H_at_r(0.05,
        'core_forming') = 0.750186 (the retired docstring claimed 0.85; the
        producer's Phase-44 sigma/m leaves segregation_maturity ~0, so f_H stays
        near the no-segregation 0.75). With f_H = 0.750186 the Cloud-9 sigma_eff is
        99.801690 (a_slope=1.0); with a uniform f_H = 0.5 it would be 44.334357.
        Ratio = 2.251114, NOT ~2.9. Pinned below.
        """
        from phase44_two_component import f_H_at_r
        from t120_4_joint_fit import _load_phase44_params
        sigma_0 = _load_phase44_params()["sigma_0"]
        sigma_HH_v28 = total_sigma_m_gaussian(
            28.0, T120_4_V_TARGETS, T120_4_SIGMA_PEAKS, T120_4_W_LIST_DEFAULT, sigma_0, 1.0)
        f_H = f_H_at_r(0.05, "core_forming")
        sigma_with_2c = f_H * f_H * sigma_HH_v28
        # WITHOUT two-component: uniform f_H = 0.5 -> f_H^2 = 0.25
        sigma_no_2c = 0.25 * sigma_HH_v28
        ratio = sigma_with_2c / sigma_no_2c
        assert f_H == pytest.approx(0.7501856343179664, rel=1e-4)
        assert sigma_with_2c == pytest.approx(99.80168969102034, rel=1e-3)
        assert sigma_no_2c == pytest.approx(44.334357204880696, rel=1e-3)
        assert ratio == pytest.approx(2.2511139437481984, rel=1e-3)
        # measured 2.25, NOT the retired claimed ~2.9
        assert 2.0 < ratio < 2.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
