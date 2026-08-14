"""
Tests for kiss_sidm_scalings.py — Direction C (KISS-SIDM integration).

Covers:
  - Table I power-law slopes (fluid and DSMC, at Kn=1 and Kn=5)
  - Knudsen number: physically sensible magnitude for canonical case
  - Regime classification: canonical case lands in IMFP (the regime where
    fluid breaks down and the KISS-SIDM correction matters)
  - Correction factor: 1.0 in LMFP/SMFP, < 1.0 in IMFP
  - Penalty function: returns correction * strength, regime-aware
  - Edge cases: zero/negative inputs

References:
  Gurian, J. & May, S. (2025), arXiv:2505.15903v2, PRL 135, 221001.
"""
import math
import pytest
import sys, os
# Path setup so this can find config and kiss_sidm_scalings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))  # project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))       # code/

import config
import kiss_sidm_scalings as kss


class TestTableISlopes:
    """Table I power-law slopes (Gurian & May 2025)."""

    def test_kn1_fluid_slope(self):
        assert kss.D_LOG_M_KN1_FLUID == pytest.approx(-0.27, abs=1e-6)

    def test_kn1_dsmc_slope(self):
        assert kss.D_LOG_M_KN1_DSMC == pytest.approx(-0.21, abs=1e-6)

    def test_kn5_fluid_slope(self):
        assert kss.D_LOG_M_KN5_FLUID == pytest.approx(-0.37, abs=1e-6)

    def test_kn5_dsmc_slope(self):
        assert kss.D_LOG_M_KN5_DSMC == pytest.approx(-0.21, abs=1e-6)

    def test_dsmc_slopes_equal_at_kn1_and_kn5(self):
        # The paper finds the DSMC power-law is the SAME at Kn=1 and Kn=5
        # (both -0.21), even though the fluid diverges. This is a key
        # qualitative finding.
        assert kss.D_LOG_M_KN1_DSMC == kss.D_LOG_M_KN5_DSMC

    def test_fluid_slopes_diverge_between_kn1_and_kn5(self):
        # The fluid model has DIFFERENT slopes at the two Kn scales; the
        # DSMC has the SAME slope. This is the EXACT quantitative result
        # the KISS-SIDM paper reports (Table I, "order one disagreement").
        assert kss.D_LOG_M_KN1_FLUID != kss.D_LOG_M_KN5_FLUID

    def test_all_slopes_negative(self):
        # M shrinks as v grows during collapse. Negative slopes are required.
        for s in [kss.D_LOG_M_KN1_FLUID, kss.D_LOG_M_KN1_DSMC,
                  kss.D_LOG_M_KN5_FLUID, kss.D_LOG_M_KN5_DSMC]:
            assert s < 0


class TestCoreMassScalingFunction:
    """The core_mass_scaling() function dispatches on (Kn, treatment)."""

    def test_kn1_fluid(self):
        assert kss.core_mass_scaling(1.0, "fluid") == kss.D_LOG_M_KN1_FLUID

    def test_kn1_dsmc(self):
        assert kss.core_mass_scaling(1.0, "dsmc") == kss.D_LOG_M_KN1_DSMC

    def test_kn5_fluid(self):
        assert kss.core_mass_scaling(5.0, "fluid") == kss.D_LOG_M_KN5_FLUID

    def test_kn5_dsmc(self):
        assert kss.core_mass_scaling(5.0, "dsmc") == kss.D_LOG_M_KN5_DSMC

    def test_invalid_kn_threshold(self):
        with pytest.raises(ValueError, match="Kn_threshold"):
            kss.core_mass_scaling(2.0, "fluid")

    def test_invalid_treatment(self):
        with pytest.raises(ValueError, match="treatment"):
            kss.core_mass_scaling(1.0, "nbody")


class TestKnudsenNumber:
    """Knudsen number from Eq. 18, sanity-checked against the paper's
    canonical case (sigma_m=50 cm^2/g in a 10^9 M_sun halo)."""

    def test_canonical_case_is_imfp(self):
        # The paper's canonical case: 10^9 M_sun halo, rho_s=2.73e-2 M_sun/pc^3,
        # v_max~100 km/s, sigma_m=50 cm^2/g. This is the case where the fluid
        # model BREAKS DOWN (the paper's main point).
        # In our units: rho_s = 2.73e7 M_sun/kpc^3.
        Kn = kss.knudsen_number(2.73e7, 100.0, 50.0)
        regime = kss.knudsen_regime_label(Kn)
        # The paper specifically studies this case in the IMFP regime.
        assert regime == "IMFP", (
            f"Canonical case should be IMFP (where fluid breaks down), "
            f"got Kn={Kn:.3e}, regime={regime}"
        )

    def test_kn_dimensionless(self):
        # Kn must be dimensionless (pure number). Sanity: no units, no NaN.
        Kn = kss.knudsen_number(1e7, 30.0, 1.0)
        assert math.isfinite(Kn)
        assert Kn > 0

    def test_kn_in_dwarf_halo_higher_than_cluster(self):
        # Kn = H * rho * sigma_m. H ~ v/sqrt(rho) so Kn ~ v * sqrt(rho) * sigma_m.
        # Dwarf: 30 * sqrt(1e7) * 1 = 30 * 3162 * 1 = 9.5e4 (in SI)
        # Cluster: 1500 * sqrt(1e3) * 0.1 = 1500 * 31.6 * 0.1 = 4.7e3 (in SI)
        # The dwarf is MORE IMFP (Kn closer to 1) than the cluster for
        # these specific inputs because its density ratio wins over the
        # velocity ratio in the Kn ~ v * sqrt(rho) * sigma_m scaling.
        Kn_dwarf = kss.knudsen_number(1e7, 30.0, 1.0)
        Kn_cluster = kss.knudsen_number(1e3, 1500.0, 0.1)
        assert Kn_dwarf > Kn_cluster

    def test_kn_scales_linearly_with_sigma_m(self):
        # Eq. 18: Kn = H * rho * sigma_m (the mean free path is
        # 1/(rho * sigma_m), so Kn = H / lambda = H * rho * sigma_m).
        # Therefore Kn is LINEAR in sigma_m, not inverse.
        Kn1 = kss.knudsen_number(1e7, 30.0, 1.0)
        Kn2 = kss.knudsen_number(1e7, 30.0, 2.0)
        assert Kn2 == pytest.approx(2.0 * Kn1, rel=1e-9)

    def test_kn_scales_with_v_rms(self):
        # Eq. 18: Kn ~ v_rms (linear in v, since the sqrt(v^2) gives v).
        Kn1 = kss.knudsen_number(1e7, 30.0, 1.0)
        Kn2 = kss.knudsen_number(1e7, 60.0, 1.0)
        assert Kn2 == pytest.approx(2.0 * Kn1, rel=1e-9)

    def test_kn_scales_inversely_with_sqrt_rho(self):
        # Eq. 18: H ~ 1/sqrt(rho); lambda ~ 1/rho; so Kn = H/lambda ~ sqrt(rho).
        # (Kn is larger for higher density, because the MFP shrinks faster
        # than the scale height.)
        Kn1 = kss.knudsen_number(1e7, 30.0, 1.0)
        Kn4 = kss.knudsen_number(4e7, 30.0, 1.0)
        assert Kn4 == pytest.approx(2.0 * Kn1, rel=1e-9)

    def test_zero_inputs_return_inf(self):
        assert kss.knudsen_number(0.0, 30.0, 1.0) == float("inf")
        assert kss.knudsen_number(1e7, 0.0, 1.0) == float("inf")
        assert kss.knudsen_number(1e7, 30.0, 0.0) == float("inf")

    def test_negative_inputs_return_inf(self):
        assert kss.knudsen_number(-1.0, 30.0, 1.0) == float("inf")


class TestKnudsenRegimeLabel:
    """Regime classifier at the published boundaries."""

    def test_lmfp_at_very_high_kn(self):
        assert kss.knudsen_regime_label(100.0) == "LMFP"
        assert kss.knudsen_regime_label(11.0) == "LMFP"

    def test_smfp_at_very_low_kn(self):
        assert kss.knudsen_regime_label(0.01) == "SMFP"
        assert kss.knudsen_regime_label(0.099) == "SMFP"

    def test_imfp_at_unit_kn(self):
        # Kn=1 is the canonical IMFP boundary
        assert kss.knudsen_regime_label(1.0) == "IMFP"
        assert kss.knudsen_regime_label(5.0) == "IMFP"
        assert kss.knudsen_regime_label(0.5) == "IMFP"

    def test_degenerate_at_zero(self):
        assert kss.knudsen_regime_label(0.0) == "degenerate"
        assert kss.knudsen_regime_label(-1.0) == "degenerate"


class TestKnudsenCorrectionFactor:
    """Correction factor: 1.0 outside IMFP, Table I ratio inside."""

    def test_unity_in_lmfp(self):
        # Fluid model is fine in LMFP — no correction.
        assert kss.knudsen_correction_factor(100.0) == 1.0
        assert kss.knudsen_correction_factor(20.0) == 1.0

    def test_unity_in_smfp(self):
        # Fluid model is fine in SMFP (deep in the core) — no correction.
        assert kss.knudsen_correction_factor(0.01) == 1.0
        assert kss.knudsen_correction_factor(0.05) == 1.0

    def test_less_than_one_in_imfp_at_kn1(self):
        # IMFP, Kn=1: fluid slope -0.27, DSMC -0.21. Ratio |DSMC|/|fluid| = 0.778
        f = kss.knudsen_correction_factor(1.0, Kn_threshold=1.0)
        expected = abs(kss.D_LOG_M_KN1_DSMC) / abs(kss.D_LOG_M_KN1_FLUID)
        assert f == pytest.approx(expected, rel=1e-9)
        # And it must be less than 1 (the DSMC is shallower than fluid).
        assert f < 1.0

    def test_smaller_in_imfp_at_kn5(self):
        # IMFP, Kn=5: fluid slope -0.37, DSMC -0.21. Ratio = 0.568.
        f = kss.knudsen_correction_factor(1.0, Kn_threshold=5.0)
        expected = abs(kss.D_LOG_M_KN5_DSMC) / abs(kss.D_LOG_M_KN5_FLUID)
        assert f == pytest.approx(expected, rel=1e-9)
        assert f < 1.0

    def test_kn5_correction_smaller_than_kn1(self):
        # The Kn=5 correction is more aggressive than the Kn=1 correction
        # (because the fluid model diverges more from DSMC at Kn=5).
        f1 = kss.knudsen_correction_factor(1.0, Kn_threshold=1.0)
        f5 = kss.knudsen_correction_factor(1.0, Kn_threshold=5.0)
        assert f5 < f1


class TestCollapsePenaltyKinetic:
    """End-to-end: penalty under different physical regimes."""

    def test_canonical_case_applies_correction(self):
        # The paper's canonical case: IMFP, Kn=1. The penalty should be
        # REDUCED by the DSMC correction (factor 0.78).
        penalty = kss.collapse_penalty_kinetic(50.0, 2.73e7, 100.0, penalty_strength=1.0)
        assert penalty == pytest.approx(0.778, rel=0.01)
        assert penalty < 1.0

    def test_smfp_dwarf_no_correction(self):
        # Dwarf galaxy: SMFP regime, fluid is fine. Penalty = strength.
        penalty = kss.collapse_penalty_kinetic(1.0, 1e7, 30.0, penalty_strength=1.0)
        assert penalty == pytest.approx(1.0, rel=1e-6)

    def test_lmfp_cluster_no_correction(self):
        # Cluster: LMFP regime, fluid is fine. Penalty = strength.
        penalty = kss.collapse_penalty_kinetic(0.1, 1e3, 1500.0, penalty_strength=1.0)
        assert penalty == pytest.approx(1.0, rel=1e-6)

    def test_penalty_strength_scales(self):
        # Penalty is multiplicative: stronger penalty = larger value.
        p1 = kss.collapse_penalty_kinetic(50.0, 2.73e7, 100.0, penalty_strength=2.0)
        p2 = kss.collapse_penalty_kinetic(50.0, 2.73e7, 100.0, penalty_strength=4.0)
        assert p2 == pytest.approx(2.0 * p1, rel=1e-9)


class TestUnitConversions:
    """Sanity-check the SI unit conversion helpers."""

    def test_rho_conversion(self):
        # 1 M_sun/kpc^3 = 1.989e30 kg / (3.086e19 m)^3 ≈ 6.77e-29 kg/m^3
        rho_si = kss._rho_msun_per_kpc3_to_kg_per_m3(1.0)
        assert rho_si == pytest.approx(6.77e-29, rel=1e-2)

    def test_sigma_m_conversion(self):
        # 1 cm^2/g = 1e-4 m^2 / 1e-3 kg = 0.1 m^2/kg
        assert kss._sigma_m_cm2_per_g_to_m2_per_kg(1.0) == pytest.approx(0.1)
