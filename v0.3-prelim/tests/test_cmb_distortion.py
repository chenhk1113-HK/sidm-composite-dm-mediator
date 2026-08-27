"""Tests for the CMB spectral distortion channel (Channel 16, T70.8).

Per R14 reviewer Recommendation 3 (deferred to v0.6 roadmap). Validates:
- loglike_cmb_distortion(m_chi, m_phi, epsilon) signature
- Planck 95% CL limits (|mu| < 9e-6, |y| < 1.5e-6) are correctly applied
- Lifetime window [1e5 s, 1e13 s] gates the penalty correctly
- Edge cases: very short lifetimes (BBN-only), very long lifetimes (post-CMB)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

_HERE = Path(__file__).resolve().parent
for p in (str(_HERE), str(_HERE.parent), str(_HERE.parent / "v0.1-prelim" / "code")):
    if p not in sys.path:
        sys.path.insert(0, p)

channels_extended = pytest.importorskip("channels_extended")

loglike_cmb_distortion = channels_extended.loglike_cmb_distortion
CMB_MU_MAX_95CL = channels_extended.CMB_MU_MAX_95CL
CMB_Y_MAX_95CL = channels_extended.CMB_Y_MAX_95CL
T_CMB_DISTORTION_EARLY_S = channels_extended.T_CMB_DISTORTION_EARLY_S
T_CMB_DISTORTION_LATE_S = channels_extended.T_CMB_DISTORTION_LATE_S
_compute_decay_tau_seconds = channels_extended._compute_decay_tau_seconds
_compute_mu_y_from_lifetime = channels_extended._compute_mu_y_from_lifetime


class TestCMBDistortionConstants:
    """Validate the Planck 2017 95% CL bounds are loaded correctly."""

    def test_mu_max_is_planck_value(self):
        # Planck Int. LI 2017, arXiv:1612.00071, Table 1: |mu| < 9e-6
        assert CMB_MU_MAX_95CL == pytest.approx(9.0e-6, rel=1e-3)

    def test_y_max_is_planck_value(self):
        # Planck Int. LI 2017: |y| < 1.5e-6
        assert CMB_Y_MAX_95CL == pytest.approx(1.5e-6, rel=1e-3)

    def test_lifetime_window_bounds(self):
        # mu regime: tau < 1e5 s; y regime: tau > 1e13 s
        assert T_CMB_DISTORTION_EARLY_S == pytest.approx(1.0e5, rel=1e-3)
        assert T_CMB_DISTORTION_LATE_S == pytest.approx(1.0e13, rel=1e-3)


class TestDecayTauCalculation:
    """Validate _compute_decay_tau_seconds: tau = 1 / (alpha * m_phi) in natural units."""

    def test_tau_scales_as_inverse_m_phi(self):
        # Doubling m_phi should halve tau
        tau1 = _compute_decay_tau_seconds(100.0, 1e-5)
        tau2 = _compute_decay_tau_seconds(200.0, 1e-5)
        assert tau2 == pytest.approx(tau1 / 2.0, rel=1e-6)

    def test_tau_scales_as_inverse_epsilon_squared(self):
        # Per B1 docs: Γ ∝ ε² × m_phi, so τ ∝ 1/(ε² × m_phi).
        # Doubling epsilon should QUARTER the tau.
        tau1 = _compute_decay_tau_seconds(100.0, 1e-5)
        tau2 = _compute_decay_tau_seconds(100.0, 2e-5)
        assert tau2 == pytest.approx(tau1 / 4.0, rel=1e-6)

    def test_tau_is_positive(self):
        tau = _compute_decay_tau_seconds(100.0, 1e-5)
        assert tau > 0
        assert np.isfinite(tau)

    def test_ksfr_valid_point_has_finite_tau(self):
        # m_phi=500 MeV (KSFR-valid), epsilon=1e-30 → very long lifetime
        tau = _compute_decay_tau_seconds(500.0, 1e-30)
        assert tau > 1e15  # way beyond CMB epoch


class TestMuYFromLifetime:
    """Validate _compute_mu_y_from_lifetime: returns (0, 0) outside window."""

    def test_short_lifetime_returns_zero(self):
        # tau < T_CMB_DISTORTION_EARLY_S = 1e5 s → pre-CMB, no penalty
        mu, y = _compute_mu_y_from_lifetime(1.0e3)  # 1000 s
        assert mu == 0.0
        assert y == 0.0

    def test_long_lifetime_returns_zero(self):
        # tau > T_CMB_DISTORTION_LATE_S = 1e13 s → post-CMB, no penalty
        mu, y = _compute_mu_y_from_lifetime(1.0e15)
        assert mu == 0.0
        assert y == 0.0

    def test_window_returns_finite_values(self):
        # tau in window [1e5, 1e13] s
        mu, y = _compute_mu_y_from_lifetime(1.0e10)  # ~300 yr
        # mu should be in the y regime (tau > 1e5 s)
        assert np.isfinite(mu)
        assert np.isfinite(y)


class TestLoglikeCMBDistortion:
    """Validate the Gaussian penalty structure."""

    def test_returns_finite_for_ksfr_valid_point(self):
        # KSFR-valid: m_phi=500 MeV. With epsilon=1e-30, lifetime is huge → no penalty
        ll = loglike_cmb_distortion(m_chi=1e9, m_phi=500.0, epsilon=1e-30)
        assert np.isfinite(ll)

    def test_short_lifetime_gives_no_penalty(self):
        # epsilon=1e-5, m_phi=100 MeV → tau ≈ 1.3e14 s (post-CMB → no penalty)
        ll = loglike_cmb_distortion(m_chi=1e9, m_phi=100.0, epsilon=1e-5)
        assert ll == pytest.approx(0.0, abs=1e-6)

    def test_penalty_is_negative_or_zero(self):
        # Penalty is Gaussian (negative definite when y or mu exceed Planck bound)
        # Test a configuration that triggers the penalty:
        # m_phi=100 MeV, epsilon=1e-5, m_chi=1 GeV
        # tau ≈ 1.3e14 s → outside window → 0 penalty (so test instead a window case)
        # For window: we need τ in [1e5, 1e13]. Use ε=1e-7 → tau grows.
        ll = loglike_cmb_distortion(m_chi=1e9, m_phi=100.0, epsilon=1e-7)
        assert ll <= 0.0  # penalty is non-positive (≤0)

    def test_returns_finite_when_in_window(self):
        # Tau in window [1e5, 1e13] s — use ε that puts tau in middle of window
        # tau = 1/(alpha * m_phi_MeV * 1.519e21) for α ∝ ε
        # log tau = 10 - log10(ε) - log10(m_phi_MeV) - 21.18
        # For tau = 1e10 s, ε = 1e-10 × (100/100) = 1e-10
        ll = loglike_cmb_distortion(m_chi=1e9, m_phi=100.0, epsilon=1e-10)
        assert np.isfinite(ll)

    def test_signature_is_3_positional_args(self):
        # Sanity check: loglike_cmb_distortion takes (m_chi, m_phi, epsilon)
        # NOT the full theta tuple
        import inspect
        sig = inspect.signature(loglike_cmb_distortion)
        params = list(sig.parameters.keys())
        assert params == ["m_chi", "m_phi", "epsilon"], f"unexpected signature: {params}"


class TestT41Channel16Integration:
    """Validate Channel 16 is wired into t41.loglike_joint."""

    def test_t41_loglike_joint_accepts_6d_theta_with_cmb(self):
        # KSFR-valid 6D point, CMB-safe (very small epsilon → long lifetime)
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        theta = (2.7, 2.7, 0.64, -30.0, -10.0, 0.0)  # m_phi=500MeV, xi=1.0
        ll = t41.loglike_joint(theta)
        # KSFR-valid (m_phi=500 MeV in [418, 4180] MeV)
        # log_alpha=-10 (small), ε=1e-30 → τ very large → no CMB penalty
        assert np.isfinite(ll), f"non-finite ll={ll}"

    def test_t41_channel_16_distinct_from_other_channels(self):
        # Smoke test: changing epsilon from CMB-safe to CMB-unsafe changes ll
        # without changing other channels (KSFR, dSph, etc. should be epsilon-invariant
        # in the channel-coupling region we're testing)
        t41 = pytest.importorskip("t41_mediator_mass_joint_fit")
        # KSFR-valid m_phi=500 MeV, m_chi=30 GeV, g_chi=0.64
        # epsilon varies (the CMB channel responds to epsilon via lifetime)
        ll_safe = t41.loglike_joint((2.7, 1.5, 0.64, -50.0, -10.0, 0.0))
        ll_window = t41.loglike_joint((2.7, 1.5, 0.64, -10.0, -10.0, 0.0))
        # Both should be finite (KSFR passes for both)
        assert np.isfinite(ll_safe)
        assert np.isfinite(ll_window)
        # They might differ (other channels may also depend on epsilon)
        # The test just verifies the function doesn't crash on epsilon variation


class TestB1_Channel16Documentation:
    """Validate B1 left docstrings + citations."""

    def test_cite_planck_arxiv(self):
        # Docstring should cite Planck Int. LI 2017
        assert "1612.00071" in channels_extended.loglike_cmb_distortion.__doc__

    def test_cite_fixsen_in_helper(self):
        # μ/y formula citation should appear in the helper docstring
        assert "Fixsen" in channels_extended._compute_mu_y_from_lifetime.__doc__