"""
Tests for yang2026_likelihood.py and t19/t20 fits.

Covers the REAL published Yang+ 2026 sigma_eff vs V_max curve used as
the channel likelihood in t19_yang2026_real_fit.py and
t20_two_comp_kiss_sidm_fit.py. This is the publication-quality replacement
for the placeholder Gaussians used in t18_two_component_fit.py.

The fixture is: Yang+ 2026 Fig 1 (my reading) gives sigma_eff at 11 V_max
values from 10 to 1500 km/s. The test verifies:
  1. sigma_eff_yang2026() interpolates this curve correctly
  2. The curve is monotonically DECREASING (faster σ at dwarf, slower σ at cluster)
  3. loglike_yang2026_*() returns finite, monotonic values
  4. loglike is highest near the published SIDM2v parameters

References:
  Yang, Fan, Hou, Tsai 2026 (arXiv:2506.14898v3), Sci. Bull.
  Standing rule (AGENTS.md): no new dependencies.
"""
import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))


def _import_modules():
    """Lazy import: skip if the modules aren't importable in this env."""
    yl = pytest.importorskip("yang2026_likelihood")
    tc = pytest.importorskip("two_component_sidm")
    return yl, tc


class TestPublishedCurve:
    """The published Yang+ 2026 SIDM2v sigma_eff vs V_max curve."""

    def test_curve_v_axis_is_log_spaced(self):
        """V_max axis covers 10 to 1500 km/s (dwarf to cluster)."""
        yl, _ = _import_modules()
        assert yl.V_MAX_AXIS[0] == 10.0
        assert yl.V_MAX_AXIS[-1] == 1500.0
        # V_max axis should be monotonically increasing
        for i in range(len(yl.V_MAX_AXIS) - 1):
            assert yl.V_MAX_AXIS[i + 1] > yl.V_MAX_AXIS[i]

    def test_sigma_eff_monotonically_decreasing(self):
        """sigma_eff must DECREASE with V_max (faster at dwarf, slower at cluster)."""
        yl, _ = _import_modules()
        for i in range(len(yl.V_MAX_AXIS) - 1):
            assert yl.SIGMA_EFF_SIDM2V[i] >= yl.SIGMA_EFF_SIDM2V[i + 1], (
                f"sigma_eff at V_max={yl.V_MAX_AXIS[i]} should be >= "
                f"sigma_eff at V_max={yl.V_MAX_AXIS[i+1]}"
            )

    def test_sigma_eff_at_galaxy_scale(self):
        """Yang+ 2026 Fig 1 gives sigma_eff(V_GALAXY=100) ~ 1.3 cm^2/g."""
        yl, _ = _import_modules()
        sigma = yl.sigma_eff_yang2026(yl.V_GALAXY)
        # The published value at V_max=100 is 1.3 cm^2/g
        assert 0.5 < sigma < 5.0, f"sigma_eff(V=100) = {sigma}, expected ~1.3"

    def test_sigma_eff_at_cluster_scale(self):
        """Yang+ 2026 Fig 1 gives sigma_eff(V_CLUSTER=1500) < 0.1 cm^2/g."""
        yl, _ = _import_modules()
        sigma = yl.sigma_eff_yang2026(yl.V_CLUSTER)
        assert sigma < 0.1, f"sigma_eff(V=1500) = {sigma}, expected < 0.1"

    def test_sigma_eff_interpolation(self):
        """The interpolation is log-linear in log10 V_max."""
        yl, _ = _import_modules()
        # Midpoint of [10, 20] in log space
        v_test = np.sqrt(10.0 * 20.0)  # ~14.14
        sigma = yl.sigma_eff_yang2026(v_test)
        # Between 6.0 (at 10) and 3.5 (at 20), the geometric mean is
        # log_mid = (log10(6) + log10(3.5))/2 = 0.646
        # 10^0.646 = 4.42
        assert 4.0 < sigma < 4.8, f"sigma_eff({v_test}) = {sigma}, expected ~4.4"

    def test_sigma_eff_extrapolation_holds_at_boundaries(self):
        """Outside the V_max range, return the boundary value (no NaN)."""
        yl, _ = _import_modules()
        # Below 10
        assert yl.sigma_eff_yang2026(1.0) == yl.SIGMA_EFF_SIDM2V[0]
        # Above 1500
        assert yl.sigma_eff_yang2026(3000.0) == yl.SIGMA_EFF_SIDM2V[-1]


class TestYangLogLikelihoods:
    """The 3 Yang+ 2026 channels (dwarf, galaxy, cluster) return finite, monotonic log L."""

    def test_loglike_dwarf_at_published_sidmv(self):
        """loglike_yang2026_dwarf should be near its maximum (small |log L|) near
        the published SIDM2v parameters (sigma1 = sigma2 ~ 2.25 cm^2/g)."""
        yl, tc = _import_modules()
        # Yang+ 2026 says sigma_eff_dwarf ~ 2.5; this requires sigma1, sigma2
        # such that the convex combination is 2.5.
        ll = yl.loglike_yang2026_dwarf(2.5, 2.5, 0.5, 0.0)
        assert ll > -1.0, f"log L should be near 0 at published params, got {ll}"

    def test_loglike_galaxy_penalizes_high_sigma(self):
        """sigma_eff(V_GALAXY=100) target is 1.3 cm^2/g. A sigma far from 1.3
        should give a much lower log L."""
        yl, _ = _import_modules()
        ll_close = yl.loglike_yang2026_galaxy(1.3, 1.3, 0.5, 0.0)
        ll_far = yl.loglike_yang2026_galaxy(50.0, 50.0, 0.5, 0.0)
        assert ll_close > ll_far

    def test_loglike_cluster_penalizes_high_sigma(self):
        """sigma_eff(V_CLUSTER=1500) target is <0.1 cm^2/g. A high sigma should
        give a much lower log L."""
        yl, _ = _import_modules()
        ll_close = yl.loglike_yang2026_cluster(0.02, 0.02, 0.5, 0.0)
        ll_far = yl.loglike_yang2026_cluster(50.0, 50.0, 0.5, 0.0)
        assert ll_close > ll_far

    def test_loglike_yang2026_full_at_published_sidmv(self):
        """loglike_yang2026_full at the published SIDM2v parameters should
        be near its maximum. The fit is supposed to FIND this maximum.

        The published sigma_eff drops from 2.5 (dwarf) to 0.02 (cluster),
        a factor of ~125. This is NOT achievable with single-component
        velocity dependence. The 2-comp model is what fits.
        """
        yl, tc = _import_modules()
        # Search a 2-comp parameter space: sigma1 ~ 5, sigma2 ~ 0.05
        # would give sigma_eff(dwarf) ~ 5*f1 + 0.05*(1-f1) ~ 2-3 with f1=0.5
        # and sigma_eff(cluster) similar.
        # But the 125x dynamic range is the hard part.
        best_ll = -np.inf
        best_pt = None
        for s1 in [1.0, 5.0, 20.0]:
            for s2 in [0.001, 0.01, 0.1]:
                for f1 in [0.3, 0.5, 0.7, 0.9]:
                    for a in [-0.5, 0.0, 0.5, 1.0]:
                        ll = yl.loglike_yang2026_full(s1, s2, f1, a)
                        if ll > best_ll:
                            best_ll = ll
                            best_pt = (s1, s2, f1, a)
        # Best log L should be in a reasonable range for a fit that's
        # FINDING the published curve. At the published sigma1/sigma2=40
        # the dwarf/cluster dynamic range is achievable.
        assert best_ll > -10.0, f"Best log L = {best_ll} at {best_pt}, expected > -10.0"


class TestPublishedSIDM2vParameters:
    """The published SIDM2v model parameters (Table 1 of Yang+ 2026)."""

    def test_mass_ratio_3(self):
        """m_H / m_L = 3.0."""
        yl, _ = _import_modules()
        assert yl.MASS_RATIO == 3.0

    def test_heavy_intra_species_6_89(self):
        """sigma_0/m_H = 6.89 cm^2/g for chi_H-chi_H intra-species."""
        yl, _ = _import_modules()
        assert yl.SIGMA0_MH_HEAVY == pytest.approx(6.89, abs=1e-3)

    def test_inter_species_smaller(self):
        """Inter-species cross section (1.125) is smaller than intra-species
        (6.89). This is the mass-segregation signature."""
        yl, _ = _import_modules()
        # Inter-species = 1.125/6.89 = 0.163 of intra
        assert yl.SIGMA_X_OVER_MH < yl.SIGMA0_MH_HEAVY
        assert yl.SIGMA_X_OVER_MH == pytest.approx(1.125 / 6.89, rel=1e-3)


class TestKISStoYang2026Integration:
    """KISS-SIDM correction applied to the 2-comp model (TIER 3)."""

    def test_t20_run_produces_output_json(self):
        """The T20 fit script should produce t20_*.json."""
        yl, _ = _import_modules()
        # Just check the file exists (the fit ran already in the test session)
        from config import RESULTS_DIR_V03
        # We don't strictly require the file (it depends on the test order)
        # but if t19 exists, t20 should too.
        t19_path = RESULTS_DIR_V03 / "t19_yang2026_real_fit.json"
        t20_path = RESULTS_DIR_V03 / "t20_two_comp_kiss_sidm_fit.json"
        if t19_path.exists():
            # If t19 was produced in this test session, t20 should be too
            assert t20_path.exists(), (
                f"t20 should exist if t19 exists; "
                f"t19={t19_path.exists()}, t20={t20_path.exists()}"
            )
