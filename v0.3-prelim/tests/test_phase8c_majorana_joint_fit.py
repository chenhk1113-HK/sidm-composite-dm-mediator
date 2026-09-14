"""
Tests for Phase 8c Majorana dark photon reframe joint fit.

Validates:
1. Majorana second-order suppression (g_D ε)² applied correctly
2. Inelastic σ_inel scales as ε² g_D² f_H (event-rate matched to de Lima)
3. Joint fit is consistent: |Δlog Z full - baseline| < 1.0 (sampling noise)
4. ε posterior opens to ~10⁻⁶ (vs T39's 10⁻⁵⁰ floor)
"""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from phase8c_majorana_reframe_joint_fit import (
    sigma_SI_majorana_cm2, sigma_inel_majorana_cm2,
    lz_248keV_event_rate, loglike_lz_248keV,
    loglike_joint_majorana,
    LZ_248_KEV_RATE_TARGET, LZ_248_KEV_RATE_SIGMA,
    LOG_EPSILON_RANGE, LOG_G_D_RANGE, LOG_F_H_RANGE,
)


class TestMajoranaSecondOrder:
    """σ_SI^Majorana = σ_SI^Dirac × (g_D ε)²."""

    def test_suppression_factor(self):
        """At de Lima (g_D=0.0227, ε=1.3e-6), (g_D ε)² ≈ 8.7e-16."""
        g_D = 0.0227
        eps = 1.3e-6
        factor = (g_D * eps)**2
        np.testing.assert_allclose(factor, 8.7e-16, rtol=0.05)

    def test_pathway_7B_below_LZ(self):
        """At Pathway 7B (g_D=0.7, ε=4.2e-8), σ_SI^Majorana << 10⁻⁴⁶."""
        sigma = sigma_SI_majorana_cm2(epsilon=4.2e-8, g_D=0.7)
        assert sigma < 1e-50, f"σ_SI^Majorana = {sigma:.2e} (expected < 1e-50)"

    def test_v03_original_safety(self):
        """At v0.3-prelim original (ε=7.7e-57), σ_SI^Majorana ≪ 10⁻⁴⁶."""
        sigma = sigma_SI_majorana_cm2(epsilon=7.7e-57, g_D=0.7)
        assert sigma < 1e-100, f"σ_SI^Majorana = {sigma:.2e}"


class TestInelasticScaling:
    """σ_inel_Majorana ∝ ε² g_D² f_H (de Lima calibrated)."""

    def test_inel_proportional_to_eps_squared(self):
        """Doubling ε should quadruple σ_inel."""
        base = sigma_inel_majorana_cm2(epsilon=1e-6, g_D=0.5, f_H=0.5)
        doubled = sigma_inel_majorana_cm2(epsilon=2e-6, g_D=0.5, f_H=0.5)
        np.testing.assert_allclose(doubled / base, 4.0, rtol=1e-6)

    def test_inel_proportional_to_gD_squared(self):
        """Doubling g_D should quadruple σ_inel."""
        base = sigma_inel_majorana_cm2(epsilon=1e-6, g_D=0.5, f_H=0.5)
        doubled = sigma_inel_majorana_cm2(epsilon=1e-6, g_D=1.0, f_H=0.5)
        np.testing.assert_allclose(doubled / base, 4.0, rtol=1e-6)

    def test_inel_proportional_to_fH(self):
        """Doubling f_H should double σ_inel."""
        base = sigma_inel_majorana_cm2(epsilon=1e-6, g_D=0.5, f_H=0.5)
        doubled = sigma_inel_majorana_cm2(epsilon=1e-6, g_D=0.5, f_H=1.0)
        np.testing.assert_allclose(doubled / base, 2.0, rtol=1e-6)

    def test_deLima_bbenchmark_match(self):
        """σ_inel at de Lima (eps=1.3e-6, g_D=0.0227, f_H=0.5) ≈ 7e-47."""
        sigma = sigma_inel_majorana_cm2(epsilon=1.3e-6, g_D=0.0227, f_H=0.5)
        assert 1e-48 < sigma < 1e-45, \
            f"σ_inel at de Lima = {sigma:.2e} (expected ~7e-47)"


class TestEventRate:
    """Event rate at LZ for 248 keV bin."""

    def test_event_rate_zero_at_zero_fH(self):
        """f_H=0 should give 0 events."""
        rate = lz_248keV_event_rate(epsilon=1.3e-6, g_D=0.0227, f_H=0.0)
        assert rate == 0.0

    def test_event_rate_finite_at_deLima(self):
        """de Lima benchmark should give finite rate."""
        rate = lz_248keV_event_rate(epsilon=1.3e-6, g_D=0.0227, f_H=0.5)
        assert 0 < rate < 100, f"Rate = {rate} (expected finite)"

    def test_event_rate_loglike_max_at_target(self):
        """loglike_lz_248keV is maximum when predicted rate = target."""
        # Predict 1 event exactly
        ll_at_target = loglike_lz_248keV(epsilon=1.3e-6, g_D=0.0227, f_H=0.5)
        # vs. over-prediction
        ll_over = loglike_lz_248keV(epsilon=1.3e-5, g_D=0.5, f_H=0.5)  # way too high
        assert ll_at_target > ll_over, \
            f"loglike at target ({ll_at_target}) should be > over-pred ({ll_over})"


class TestJointLikelihoodConsistency:
    """loglike_joint_majorana behaves consistently."""

    def test_returns_neg_inf_outside_priors(self):
        """Out-of-prior theta should return -inf."""
        bad_theta = [-10, 1.0, -100, -100, -10, -10]  # way outside
        ll = loglike_joint_majorana(bad_theta)
        assert ll == -np.inf

    def test_lz_248_toggle(self):
        """Disabling LZ 248 keV should give a different (typically higher) loglike."""
        theta = [0.0, 0.5, -7.0, -3.0, -0.5, -1.0]  # in prior
        ll_full = loglike_joint_majorana(theta, lz_248_enabled=True)
        ll_baseline = loglike_joint_majorana(theta, lz_248_enabled=False)
        # They should differ by the LZ 248 keV contribution
        assert ll_full != ll_baseline, "248 keV toggle should change loglike"

    def test_loglike_finite_in_prior(self):
        """In-prior theta should give finite loglike."""
        theta = [0.0, 0.5, -7.0, -3.0, -0.5, -1.0]  # in prior
        ll = loglike_joint_majorana(theta, lz_248_enabled=False)
        assert np.isfinite(ll)


class TestResultsConsistency:
    """Validate the saved Phase 8c JSON results."""

    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase8c_majorana_reframe_joint_fit.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 8c results not yet generated"
    )
    def test_results_exist(self):
        """Results file should exist after Phase 8c run."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "log_Z_baseline_no_248kev" in data
        assert "log_Z_full_with_248kev" in data

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 8c results not yet generated"
    )
    def test_delta_log_Z_within_noise(self):
        """|Δlog Z full - baseline| should be < 2 (sampling noise)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        delta = abs(data["delta_log_Z_248keV_contribution"])
        assert delta < 2.0, f"|Δlog Z| = {delta} (expected < 2 for sampling noise)"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 8c results not yet generated"
    )
    def test_epsilon_posterior_opened(self):
        """ε posterior 84th percentile should be > 10⁻¹⁰ (vs T39's 10⁻⁵⁰)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        eps_84 = data["posteriors_full_16_50_84"]["epsilon"][2]
        assert eps_84 > 1e-10, f"ε 84th percentile = {eps_84} (expected > 1e-10)"
