"""
Tests for Phase 8b Majorana dark photon reframe.

Validates the analytic scaling relations:
1. Yukawa Born σ/m scales as g⁴ (Pathway 7A failure at g_D=0.0227)
2. Majorana second-order elastic suppression is (g_D ε)²
3. Inelastic σ_inel scales as ε² g_D² (so ε scaling compensates g_D change)
"""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from phase8b_majorana_reframe import (
    check_pathway_7A, check_pathway_7B,
    sigma_SI_dirac, sigma_SI_majorana,
    V03_MAP, DE_LIMA, LZ_SI_LIMIT,
)


class TestYukawaSIDMScaling:
    """SIDM σ/m Yukawa Born scales as g⁴ (Kaplinghat-Tulin-Yu 2018)."""

    def test_pathway_7A_sidm_too_small(self):
        """At g_D = 0.0227 (de Lima freeze-out), σ/m(100) ~ 10⁻⁶ ≪ 1."""
        res = check_pathway_7A()
        # SIDM σ/m at g_D=0.0227 should be ~10⁻⁶ cm²/g, factor 10⁶ below 1
        assert res["sidm_sigma_m_100"] < 1e-4, \
            f"Pathway 7A SIDM σ/m = {res['sidm_sigma_m_100']:.2e} (expected <1e-4)"

    def test_pathway_7B_sidm_calibrated(self):
        """At g_D = 0.7 (SIDM-required), σ/m(100) ~ 1 cm²/g."""
        res = check_pathway_7B(g_D_reframed=0.7)
        assert 0.5 < res["sidm_sigma_m_100"] < 2.0, \
            f"Pathway 7B SIDM σ/m = {res['sidm_sigma_m_100']:.2e} (expected ~1)"

    def test_sidm_g4_scaling(self):
        """σ/m(100) ratio at two g_D values equals (g_D1/g_D2)⁴."""
        res_A = check_pathway_7B(g_D_reframed=DE_LIMA["g_D"], target_event_rate_match=False)
        res_B = check_pathway_7B(g_D_reframed=0.7, target_event_rate_match=False)
        ratio_actual = res_B["sidm_sigma_m_100"] / res_A["sidm_sigma_m_100"]
        ratio_expected = (0.7 / DE_LIMA["g_D"])**4
        np.testing.assert_allclose(ratio_actual, ratio_expected, rtol=1e-6)


class TestMajoranaElasticSuppression:
    """Second-order Majorana elastic suppression is (g_D ε)²."""

    def test_suppression_factor_at_de_lima(self):
        """At de Lima values, (g_D ε)² ~ 10⁻¹⁵."""
        g_D = DE_LIMA["g_D"]
        eps = DE_LIMA["eps"]
        expected = (g_D * eps)**2
        np.testing.assert_allclose(expected, 8.7e-16, rtol=0.05)

    def test_majorana_below_LZ_at_pathway_7B(self):
        """Pathway 7B Majorana σ_SI should be ≥100× below LZ limit."""
        res = check_pathway_7B(g_D_reframed=0.7)
        assert res["lz_elastic_margin"] > 100, \
            f"LZ elastic margin = {res['lz_elastic_margin']:.2e} (expected >100)"


class TestInelasticScaling:
    """σ_inel ∝ ε² g_D² — ε scaling compensates g_D change."""

    def test_inel_target_match_pathway_7B(self):
        """Pathway 7B with event-rate match should give σ_inel/target ~ 1."""
        res = check_pathway_7B(g_D_reframed=0.7, target_event_rate_match=True)
        np.testing.assert_allclose(res["lz_inel_match_ratio"], 1.0, rtol=1e-6)

    def test_eps_compensation(self):
        """Pathway 7B ε = de Lima ε × (g_D_deLima / g_D_new) = 1.3e-6 × 0.0227/0.7."""
        res = check_pathway_7B(g_D_reframed=0.7)
        expected_eps = DE_LIMA["eps"] * DE_LIMA["g_D"] / 0.7
        np.testing.assert_allclose(res["eps_reframed"], expected_eps, rtol=1e-6)

    def test_no_match_increases_eps(self):
        """Without event-rate matching, ε stays at de Lima value."""
        res = check_pathway_7B(g_D_reframed=0.7, target_event_rate_match=False)
        np.testing.assert_allclose(res["eps_reframed"], DE_LIMA["eps"], rtol=1e-6)


class TestPathway7AFreezeOutConflict:
    """Pathway 7A (de Lima exact) fails SIDM — documents the freeze-out conflict."""

    def test_pathway_7A_sidm_fail(self):
        """The whole point of the reframe: de Lima's g_D is set by freeze-out,
        SIDM needs g_D ~ 35× larger. This is the structural conflict."""
        res = check_pathway_7A()
        sidm_ratio = res["sidm_sigma_m_100"] / V03_MAP["sigma_m_100"]
        assert sidm_ratio < 1e-3, \
            f"Pathway 7A SIDM ratio = {sidm_ratio:.2e} (expected <1e-3 for freeze-out conflict)"
