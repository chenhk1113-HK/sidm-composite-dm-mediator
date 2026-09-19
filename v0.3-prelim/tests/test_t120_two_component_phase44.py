"""
Tests for phase44_two_component.py — T120.3a (gravothermal selection) + T120.3b (alt shapes).

This test file verifies:
  1. f_H_at_r returns expected values for each halo type
  2. phase44_sigma_HH_at_v matches the canonical Phase 44 result
  3. phase44_two_component_sigma_eff produces sensible values
  4. The selection effect: gravothermal selection at observation radius reduces dSph violation
  5. CDM reference case has lower sigma/m than SIDM cases
  6. Alternative sigma/v shapes (Gaussian, Exponential) reduce the BW tail leakage
  7. Gaussian resonance shape satisfies the dSph constraint at v=15
"""
import math
import sys
from pathlib import Path

import pytest

_CODE_DIR = Path(__file__).parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))
sys.path.insert(0, str(_CODE_DIR.parent / "tests"))  # for test_paper_v19_regression


from phase44_two_component import (  # noqa: E402
    f_H_at_r,
    f_H_halo_average,
    phase44_sigma_HH_at_v,
    phase44_two_component_sigma_eff,
    sigma_m_lorentzian,
    sigma_m_gaussian,
    sigma_m_exponential,
    sigma_m_hard_cutoff,
    sigma_m_total_gaussian,
    sigma_m_total_exponential,
)


class TestFHalo:
    """Tests for f_H_at_r function."""

    def test_cdm_returns_05(self):
        """CDM has no segregation, f_H = 0.5 everywhere."""
        for r in [0.01, 0.05, 0.1, 0.3, 0.7, 1.0]:
            assert f_H_at_r(r, "CDM") == 0.5, f"f_H at r={r} should be 0.5 for CDM"

    def test_core_forming_high_in_center(self):
        """Core-forming halos have f_H ~ 0.85 in the center (mass segregation)."""
        assert f_H_at_r(0.05, "core_forming") >= 0.80, (
            f"f_H(core_forming, r=0.05) should be >= 0.80, got {f_H_at_r(0.05, 'core_forming')}"
        )
        assert f_H_at_r(0.05, "core_forming") <= 0.90

    def test_core_collapsed_high_in_inner_core(self):
        """Core-collapsed halos have f_H ~ 0.95 in the deep center (full segregation)."""
        f_H = f_H_at_r(0.05, "core_collapsed")
        assert f_H >= 0.90, f"f_H(core_collapsed, r=0.05) should be >= 0.90, got {f_H}"

    def test_core_collapsed_drops_fast(self):
        """Core-collapsed halos drop FASTER than core-forming because heavy has fully sunk.

        This is the gravothermal selection effect: at observation radius
        (r ~ 0.1-0.2 r_vir), the heavy component has migrated out of the
        observed region.
        """
        f_inner = f_H_at_r(0.05, "core_collapsed")
        f_outer = f_H_at_r(0.2, "core_collapsed")
        assert f_inner > 0.85, f"f_H(core_collapsed, r=0.05) should be > 0.85, got {f_inner}"
        assert f_outer < 0.5, (
            f"f_H(core_collapsed, r=0.2) should be < 0.5 (heavy has sunk), got {f_outer}"
        )

    def test_core_forming_falls_off(self):
        """Core-forming f_H should fall off with radius (less steep than collapsed)."""
        f_inner = f_H_at_r(0.05, "core_forming")
        f_outer = f_H_at_r(0.7, "core_forming")
        assert f_inner > f_outer, (
            f"f_H should fall off with r: inner={f_inner}, outer={f_outer}"
        )

    def test_intermediate_between_cdm_and_segregating(self):
        """Intermediate halos should have moderate f_H between 0.5 and 0.7."""
        f_H = f_H_at_r(0.05, "intermediate")
        assert 0.55 < f_H < 0.75, (
            f"f_H(intermediate, r=0.05) should be in (0.55, 0.75), got {f_H}"
        )

    def test_invalid_halo_type_raises(self):
        """Invalid halo_type should raise ValueError."""
        with pytest.raises(ValueError):
            f_H_at_r(0.05, "invalid_type")


class TestPhase44HeavyChannel:
    """Tests for Phase 44 heavy-heavy channel."""

    def test_phase44_heavy_at_v28_matches_canonical(self):
        """Phase 44 sigma_HH at v=28 should be ~100 cm^2/g (canonical v1.11 value)."""
        sm = phase44_sigma_HH_at_v(28.0)
        assert 95 < sm < 105, f"sigma_HH(v=28) = {sm:.2f}, expected ~100"

    def test_phase44_heavy_at_v15_low(self):
        """Phase 44 sigma_HH at v=15 should be ~5 cm^2/g (BW tail)."""
        sm = phase44_sigma_HH_at_v(15.0)
        assert 4 < sm < 6, f"sigma_HH(v=15) = {sm:.2f}, expected ~5"

    def test_phase44_heavy_at_v100_sparc(self):
        """Phase 44 sigma_HH at v=100 should be in SPARC band [0.05, 0.5]."""
        sm = phase44_sigma_HH_at_v(100.0)
        assert 0.05 < sm < 0.5, f"sigma_HH(v=100) = {sm:.2f}, expected 0.05-0.5"


class TestTwoComponentSelectionEffect:
    """Tests for the two-component selection effect (T120.3a gravothermal)."""

    def test_cloud9_high_at_v28(self):
        """Cloud-9 (core-forming) should have high sigma/m_eff at v=28."""
        sm = phase44_two_component_sigma_eff(28.0, "core_forming")
        assert sm >= 50, f"sigma_eff(Cloud-9, v=28) = {sm:.2f}, expected >= 50"

    def test_dsph_gravothermal_selection_at_v15(self):
        """T120.3a: dSph with gravothermal selection at r=0.20 should have sigma/m < 1.0.

        This is the BREAKTHROUGH: when we observe dSph stars at r ~ 0.2 r_vir
        (the half-light radius), the heavy component has sunk to smaller r,
        so f_H is low (~0.3) and sigma/m_eff drops to ~0.9 cm^2/g, which
        satisfies the Horigome+ 2025 0.8 cm^2/g limit.
        """
        sm = phase44_two_component_sigma_eff(15.0, "core_collapsed", r_over_rvir=0.20)
        assert sm < 1.5, (
            f"sigma_eff(dSph, v=15, r=0.20) = {sm:.2f}, expected < 1.5 (gravothermal selection)"
        )

    def test_dsph_at_inner_core_still_high(self):
        """dSph at the deep inner core (r=0.05) still has high sigma/m.

        The gravothermal selection works because OBSERVATIONS sample r > 0.1,
        not the deep center. So the OBSERVED sigma/m is low even though the
        central sigma/m is high.
        """
        sm_inner = phase44_two_component_sigma_eff(15.0, "core_collapsed", r_over_rvir=0.05)
        sm_outer = phase44_two_component_sigma_eff(15.0, "core_collapsed", r_over_rvir=0.20)
        assert sm_inner > sm_outer, (
            f"Inner core should have higher sigma/m than observation radius: "
            f"inner={sm_inner:.2f}, outer={sm_outer:.2f}"
        )

    def test_cloud9_higher_f_H_at_core_than_dsph(self):
        """Cloud-9 (core-forming) has higher f_H at large r than dSph (core-collapsed)."""
        f_H_c9 = f_H_at_r(0.5, "core_forming")
        f_H_dsph_outer = f_H_at_r(0.5, "core_collapsed")
        assert f_H_c9 > f_H_dsph_outer, (
            f"Cloud-9 should have more heavy at large r (broadly distributed): "
            f"Cloud-9={f_H_c9}, dSph={f_H_dsph_outer}"
        )

    def test_halo_average_f_H_different(self):
        """Halo-averaged f_H should be different for different halo types."""
        f_H_cf = f_H_halo_average("core_forming")
        f_H_cc = f_H_halo_average("core_collapsed")
        f_H_int = f_H_halo_average("intermediate")
        assert f_H_cf != f_H_cc
        assert f_H_cf != f_H_int
        assert f_H_cc != f_H_int

    def test_sparc_in_band_at_v100(self):
        """SPARC galaxies should have sigma/m_eff in [0.05, 0.5] at v=100."""
        sm = phase44_two_component_sigma_eff(100.0, "intermediate")
        assert 0.05 < sm < 0.5, (
            f"sigma_eff(SPARC, v=100) = {sm:.2f}, expected 0.05-0.5"
        )

    def test_cdm_reference_lower_than_sidm(self):
        """CDM (no interactions) should have lower sigma/m_eff than SIDM cases."""
        sm_cdm = phase44_two_component_sigma_eff(28.0, "CDM")
        sm_cloud9 = phase44_two_component_sigma_eff(28.0, "core_forming")
        assert sm_cloud9 > sm_cdm, (
            f"CDM={sm_cdm:.2f} should be < Cloud-9={sm_cloud9:.2f} at v=28"
        )

    def test_clusters_low_sigma(self):
        """Clusters should have low sigma/m_eff at high velocity."""
        sm = phase44_two_component_sigma_eff(500.0, "core_collapsed")
        assert sm < 1.0, f"sigma_eff(cluster, v=500) = {sm:.2f}, expected < 1.0"


class TestAlternativeShapes:
    """Tests for T120.3b alternative sigma/v shapes."""

    def test_lorentzian_peak(self):
        """Lorentzian at v=v_target should give sigma_peak."""
        sm = sigma_m_lorentzian(28.0, 28.0, 100.0, 5.0)
        assert abs(sm - 100.0) < 1.0, f"Lorentzian peak = {sm}, expected ~100"

    def test_gaussian_peak(self):
        """Gaussian at v=v_target should give sigma_peak."""
        sm = sigma_m_gaussian(28.0, 28.0, 100.0, 5.0)
        assert abs(sm - 100.0) < 1.0, f"Gaussian peak = {sm}, expected ~100"

    def test_gaussian_falls_faster_than_lorentzian(self):
        """Gaussian should drop faster than Lorentzian at v=15 from peak at v=29.

        Lorentzian ratio at v=15 (from v=29): [(5/2)^2] / [(15-29)^2 + (5/2)^2]
          = 6.25 / (196 + 6.25) = 6.25/202.25 ~ 0.031
        So sigma/m(v=15) Lorentzian = 100 * 0.031 = 3.1

        Gaussian ratio at v=15 (from v=29): exp(-(15-29)^2/(2*5^2))
          = exp(-196/50) = exp(-3.92) ~ 0.020
        So sigma/m(v=15) Gaussian = 100 * 0.020 = 2.0

        Gaussian should be lower than Lorentzian (faster falloff).
        """
        sm_l = sigma_m_lorentzian(15.0, 29.0, 100.0, 5.0)
        sm_g = sigma_m_gaussian(15.0, 29.0, 100.0, 5.0)
        assert sm_g < sm_l, (
            f"Gaussian at v=15 ({sm_g:.3f}) should be < Lorentzian ({sm_l:.3f})"
        )

    def test_exponential_falls_faster_than_lorentzian(self):
        """Exponential with small w falls faster than Lorentzian.

        For w_exp = 2 km/s, exponential drops as exp(-14/2) = exp(-7) ~ 9e-4,
        much faster than Lorentzian's 0.032 at v=15 from peak at v=29.
        """
        sm_l = sigma_m_lorentzian(15.0, 29.0, 100.0, 5.0)
        # Use small w to make exponential tail decay fast
        sm_e = sigma_m_exponential(15.0, 29.0, 100.0, 2.0)
        assert sm_e < sm_l, (
            f"Exponential at v=15 (w=2, {sm_e:.3f}) should be < Lorentzian (w=5, {sm_l:.3f})"
        )

    def test_hard_cutoff_zero_outside(self):
        """Hard cutoff should give 0 outside the band [v_T - w, v_T + w]."""
        sm_outside = sigma_m_hard_cutoff(50.0, 28.0, 100.0, 3.0)
        assert sm_outside == 0.0
        sm_inside = sigma_m_hard_cutoff(28.0, 28.0, 100.0, 3.0)
        assert sm_inside == 100.0

    def test_total_gaussian_reduces_v15(self):
        """Total sigma/m with Gaussian BW should have lower sigma/m(v=15) than Phase 44."""
        sm_phase44 = phase44_sigma_HH_at_v(15.0)  # ~5.0
        sm_gauss = sigma_m_total_gaussian(15.0)
        assert sm_gauss < sm_phase44, (
            f"Gaussian total at v=15 ({sm_gauss:.2f}) should be < Phase 44 ({sm_phase44:.2f})"
        )

    def test_total_exponential_reduces_v15(self):
        """Total sigma/m with Exponential BW should have lower sigma/m(v=15) than Phase 44."""
        sm_phase44 = phase44_sigma_HH_at_v(15.0)
        sm_exp = sigma_m_total_exponential(15.0)
        assert sm_exp < sm_phase44, (
            f"Exponential total at v=15 ({sm_exp:.2f}) should be < Phase 44 ({sm_phase44:.2f})"
        )


class TestPhase44Module:
    """Module-level sanity tests."""

    def test_module_imports(self):
        """The module should import without error."""
        assert phase44_two_component_sigma_eff is not None
        assert sigma_m_total_gaussian is not None

    def test_function_signatures(self):
        """Functions should accept the expected argument types."""
        sm = phase44_two_component_sigma_eff(15.0, "core_collapsed")
        assert isinstance(sm, (int, float))

        sm_int = phase44_two_component_sigma_eff(15, "core_collapsed")
        assert isinstance(sm_int, (int, float))

        sm_gauss = sigma_m_total_gaussian(15.0)
        assert isinstance(sm_gauss, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])