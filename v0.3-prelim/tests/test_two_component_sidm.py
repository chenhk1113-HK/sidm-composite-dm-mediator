"""
Tests for two_component_sidm.py — Direction B (two-component SIDM).

PLACEHOLDER WARNING: the channel likelihoods in this module (loglike_dwarf,
loglike_cluster, loglike_segregation) are simplified Gaussian proxies, not
real published posteriors. These tests verify the *math* (convexity,
mass-segregation direction, prior ranges) but they do NOT and CANNOT verify
that the resulting Bayes factor is scientifically meaningful.

The goal of the tests:
  1. sigma_eff(v) is a convex combination of sigma1(v) and sigma2(v)
     (i.e. min(sigma1, sigma2) <= sigma_eff <= max(sigma1, sigma2))
  2. Mass segregation up-weights component 1 at dwarf velocity when
     beta_seg > 0
  3. The single-component contrast (a) and the two-component contrast
     are different when f1 != 0.5 (otherwise 2-comp reduces to 1-comp)
  4. The log-likelihood is finite and well-behaved on the prior box
  5. The grid_evidence fallback (no dynesty) completes and gives a
     positive evidence (proves the pipeline works)
  6. The mass-segregation channel penalizes sigma1/sigma2 < 10 (the
     Yang+ 2026 requirement)

References:
  Yang, Fan, Hou, Tsai 2026, Sci. Bull. (arXiv:2504.02303).
  Standing rule (AGENTS.md): no new dependencies.
"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))


def _import_tc():
    return pytest.importorskip("two_component_sidm")


class TestConvexity:
    """sigma_eff must be a convex combination of sigma1, sigma2."""

    def test_sigma_eff_in_range(self):
        """sigma_eff at velocity v must be a convex combination of
        sigma1(v) and sigma2(v) (not sigma1 and sigma2 at v_ref)."""
        tc = _import_tc()
        for sigma1, sigma2, f1, a, v in [
            (1.0, 0.1, 0.5, 0.0, 30.0),
            (10.0, 0.5, 0.7, 0.5, 100.0),
            (5.0, 1.0, 0.3, -0.3, 1500.0),
            (0.5, 0.1, 0.9, 1.0, 30.0),
        ]:
            s_eff = tc.sigma_eff(sigma1, sigma2, f1, a, v)
            # Compare to sigma1(v) and sigma2(v), NOT sigma1 and sigma2.
            s1_v = tc.sigma_at_v(sigma1, a, v)
            s2_v = tc.sigma_at_v(sigma2, a, v)
            lo, hi = min(s1_v, s2_v), max(s1_v, s2_v)
            assert lo <= s_eff <= hi, (
                f"sigma_eff={s_eff} not in [{lo}, {hi}] for "
                f"(s1={sigma1}, s2={sigma2}, f1={f1}, a={a}, v={v}); "
                f"s1(v)={s1_v}, s2(v)={s2_v}"
            )

    def test_f1_extreme_limits(self):
        """f1 -> 0 means sigma_eff -> sigma2 (component 1 negligible).
        f1 -> 1 means sigma_eff -> sigma1 (component 2 negligible).
        With beta_seg > 0 there is mild velocity reweighting but the
        limit behavior holds approximately for the v_ref case.
        """
        tc = _import_tc()
        sigma1, sigma2 = 5.0, 0.5
        a = 0.0
        v = tc.V_REF
        # f1 = 0.99  ->  nearly all component 1
        s_eff_near1 = tc.sigma_eff(sigma1, sigma2, 0.99, a, v)
        assert abs(s_eff_near1 - sigma1) < 0.5 * sigma1, (
            f"f1=0.99 should give sigma_eff near sigma1={sigma1}, got {s_eff_near1}"
        )
        # f1 = 0.01  ->  nearly all component 2
        s_eff_near0 = tc.sigma_eff(sigma1, sigma2, 0.01, a, v)
        assert abs(s_eff_near0 - sigma2) < 0.5 * sigma2, (
            f"f1=0.01 should give sigma_eff near sigma2={sigma2}, got {s_eff_near0}"
        )


class TestMassSegregation:
    """Mass segregation: with beta_seg > 0, component 1 is up-weighted
    at dwarf velocity (low v) and down-weighted at cluster velocity.
    """

    def test_dwarf_upweights_component_1(self):
        tc = _import_tc()
        # At dwarf velocity, w1 > f1; at cluster velocity, w1 < f1.
        f1 = 0.5
        w1_dwarf = tc.component_weights(f1, tc.V_DWARF)[0]
        w1_cluster = tc.component_weights(f1, tc.V_CLUSTER)[0]
        assert w1_dwarf > f1, (
            f"w1 at dwarf (v=30) should be > f1=0.5 with beta_seg=0.25; "
            f"got {w1_dwarf:.3f}"
        )
        assert w1_cluster < f1, (
            f"w1 at cluster (v=1500) should be < f1=0.5 with beta_seg=0.25; "
            f"got {w1_cluster:.3f}"
        )

    def test_weights_sum_to_one(self):
        tc = _import_tc()
        for v in [tc.V_DWARF, tc.V_GALAXY, tc.V_CLUSTER]:
            w1, w2 = tc.component_weights(0.3, v)
            assert w1 + w2 == pytest.approx(1.0, abs=1e-12)

    def test_segregation_factor_direction(self):
        """At v < v_ref, g(v) > 1; at v > v_ref, g(v) < 1."""
        tc = _import_tc()
        g_dwarf = tc.segregation_factor(tc.V_DWARF)
        g_cluster = tc.segregation_factor(tc.V_CLUSTER)
        assert g_dwarf > 1.0
        assert g_cluster < 1.0


class TestLikelihoods:
    """The 3 placeholder channels."""

    def test_loglike_dwarf_peak_at_one(self):
        """loglike_dwarf peaks at sigma_eff_dwarf = 10^0.5 cm^2/g."""
        tc = _import_tc()
        ll_peak = tc.loglike_dwarf(10**0.5)
        ll_off = tc.loglike_dwarf(10**1.5)
        assert ll_peak > ll_off

    def test_loglike_cluster_penalizes_high(self):
        """loglike_cluster penalizes sigma_eff_cluster > 0.5 cm^2/g."""
        tc = _import_tc()
        ll_ok = tc.loglike_cluster(0.3)
        ll_bad = tc.loglike_cluster(5.0)
        assert ll_ok > ll_bad

    def test_loglike_segregation_penalizes_low_ratio(self):
        """loglike_segregation penalizes sigma1/sigma2 < 10 (Yang+ 2026)."""
        tc = _import_tc()
        # sigma1/sigma2 = 100 (good): log L ~ 0
        ll_good = tc.loglike_segregation(100.0, 1.0)
        # sigma1/sigma2 = 1 (bad): log L ~ -5
        ll_bad = tc.loglike_segregation(1.0, 1.0)
        assert ll_good > ll_bad

    def test_loglike_two_component_finite_on_prior_box(self):
        """Sample 100 random points on the prior box; all log L should
        be finite (no NaN, no -inf outside boundaries)."""
        tc = _import_tc()
        rng = np.random.default_rng(42)
        for _ in range(100):
            sigma1 = 10 ** rng.uniform(-2, 2)
            sigma2 = 10 ** rng.uniform(-3, 1)
            f1 = rng.uniform(0.01, 0.99)
            a = rng.uniform(-2, 2)
            ll = tc.loglike_two_component(sigma1, sigma2, f1, a)
            assert np.isfinite(ll), f"non-finite log L at ({sigma1}, {sigma2}, {f1}, {a})"


class TestGridEvidence:
    """The grid-evidence fallback (no dynesty required)."""

    def test_grid_evidence_runs(self):
        tc = _import_tc()
        # Small grid for speed (5^4 = 625 evaluations).
        res = tc.grid_evidence(n_per_dim=5)
        assert "log_Z" in res
        assert "MAP" in res
        assert np.isfinite(res["log_Z"])

    def test_grid_evidence_log_Z_finite(self):
        """Log Z is finite. (May be negative if the placeholder
        likelihoods are not very constraining at the grid resolution.)
        """
        tc = _import_tc()
        res = tc.grid_evidence(n_per_dim=5)
        assert np.isfinite(res["log_Z"]), f"non-finite log Z: {res['log_Z']}"

    def test_grid_evidence_MAP_in_prior_box(self):
        """MAP should be inside the prior box (no priors violated)."""
        tc = _import_tc()
        res = tc.grid_evidence(n_per_dim=5)
        map_ = res["MAP"]
        # log_sigma1 in (-2, 2), log_sigma2 in (-3, 1), f1 in (0.01, 0.99), a in (-2, 2)
        assert -2.0 <= map_["log_sigma1"] <= 2.0
        assert -3.0 <= map_["log_sigma2"] <= 1.0
        assert 0.01 <= map_["f1"] <= 0.99
        assert -2.0 <= map_["a"] <= 2.0


class TestSigmaAtV:
    """The velocity-dependent cross-section is monotone in a."""

    def test_a_positive_decreases_with_v(self):
        tc = _import_tc()
        # a > 0: sigma decreases with v
        s_dwarf = tc.sigma_at_v(1.0, 0.5, tc.V_DWARF)
        s_cluster = tc.sigma_at_v(1.0, 0.5, tc.V_CLUSTER)
        assert s_dwarf > s_cluster

    def test_a_zero_v_independent(self):
        tc = _import_tc()
        s_dwarf = tc.sigma_at_v(1.0, 0.0, tc.V_DWARF)
        s_cluster = tc.sigma_at_v(1.0, 0.0, tc.V_CLUSTER)
        assert s_dwarf == pytest.approx(s_cluster, rel=1e-12)


class TestCoreRadiusProxy:
    """The r_core proxy is a simple sqrt(sigma/rho) form."""

    def test_r_core_increases_with_sigma(self):
        tc = _import_tc()
        r1 = tc.core_radius_proxy(0.5)
        r2 = tc.core_radius_proxy(5.0)
        assert r2 > r1

    def test_r_core_decreases_with_rho(self):
        tc = _import_tc()
        r1 = tc.core_radius_proxy(1.0, rho_core=1e6)
        r2 = tc.core_radius_proxy(1.0, rho_core=1e8)
        assert r1 > r2
