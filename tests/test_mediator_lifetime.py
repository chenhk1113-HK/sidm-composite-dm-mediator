"""
Test class for Channel 14 (R13 H2): mediator lifetime + BBN consistency check.

Per R13 reviewer H2 suggestion in sidm review2.docx (2026-08-25):

  'Compute mediator lifetime for each sampled point. Explicitly
   distinguish decays pre-BBN vs post-BBN. Post-BBN decays require
   more sophisticated constraints than simple ΔN_eff cut. Add this as
   a likelihood penalty or rejection condition.'

Physics (per Berlin et al. 2018 PRD 97, 055033 + the project's T39 wide-prior
epsilon posterior):

  Dark photon decay rate to SM charged fermions (assuming m_A' > 2 m_f):
    Gamma(A' -> f f-bar) = (1/3) * alpha_EM * epsilon^2 * m_A' * N_c(f) * K(s)
    where K(s) is a kinematic factor ~ O(1) for m_A' >> 2 m_f
  Total width: Gamma_tot = sum over f of Gamma(A' -> f f-bar)
  Lifetime: tau = hbar / Gamma_tot

  Benchmarks:
    m_A' = 26.6 MeV (T41 MAP), epsilon = 10^-35 (T39 wide-prior median):
      Gamma ~ 10^-50 eV ~ 10^-36 s^-1, tau ~ 10^36 s ~ 10^28 yr >> t_universe

  BBN boundary:
    t_BBN ~ 1 s (after big bang, before deuterium formation)
    If tau < t_BBN (~ 1 s), decays happen during BBN -> must satisfy N_eff
    If tau > t_BBN and < t_universe, decays happen after BBN -> must satisfy
      CMB + structure-formation bounds (degenerate with delta N_eff)
    If tau > t_universe, mediator is stable -> no constraint beyond
      cosmological relic density

This channel implements the lifetime calculation + a soft penalty for
post-BBN-but-pre-CMB decays (where bounds are most stringent).
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v0.1-prelim" / "code"))
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))


class TestMediatorLifetime:
    """Tests for Channel 14 (mediator lifetime + BBN consistency)."""

    def test_function_imports(self):
        from channels_extended import (
            loglike_mediator_lifetime,
            MEDIATOR_LIFETIME_FLOOR_S,
            T_UNIVERSE_S,
            T_BBN_S,
        )
        assert callable(loglike_mediator_lifetime)

    def test_constants_are_finite(self):
        from channels_extended import (
            MEDIATOR_LIFETIME_FLOOR_S,
            T_UNIVERSE_S,
            T_BBN_S,
        )
        assert math.isfinite(MEDIATOR_LIFETIME_FLOOR_S)
        assert math.isfinite(T_UNIVERSE_S)
        assert math.isfinite(T_BBN_S)
        assert T_UNIVERSE_S > T_BBN_S  # universe age > BBN time
        assert MEDIATOR_LIFETIME_FLOOR_S > 0

    def test_at_project_posterior_no_penalty(self):
        """At T41 MAP (m_A'=26.6 MeV) + T39 wide-prior median (eps=10^-35),
        lifetime is ~10^28 years >> t_universe. Should return ~0."""
        from channels_extended import loglike_mediator_lifetime
        result = loglike_mediator_lifetime(m_chi=14.8e9, m_ap=26.6e6, epsilon=1e-35)
        assert math.isfinite(result)
        # Should be 0 or very close (mediator stable at this epsilon)
        assert result >= -0.1, f"got {result}, expected ~0 (stable mediator)"

    def test_at_canonical_epsilon_unstable(self):
        """At canonical epsilon = 10^-5 (NOT the project's wide-prior median;
        this is the 'naive' canonical secluded WIMP value), the mediator is
        extremely short-lived. Should return -inf (pre-BBN decay)."""
        from channels_extended import loglike_mediator_lifetime
        result = loglike_mediator_lifetime(m_chi=14.8e9, m_ap=26.6e6, epsilon=1e-5)
        # Should be -inf: decays pre-BBN
        assert result == -np.inf, f"got {result}, expected -inf"

    def test_at_sub_bb_time_returns_neg_inf(self):
        """If tau < t_BBN (~1 s) AND mass > 2 m_e (can decay to e+e-),
        the decay happens during nucleosynthesis. Strong penalty."""
        from channels_extended import loglike_mediator_lifetime
        # Pick epsilon that gives tau ~ 10^-3 s (well before BBN)
        # Gamma ~ 10^3 s^-1 -> tau ~ 10^-3 s
        # For m_A' = 26.6 MeV: Gamma = (1/3)*alpha*eps^2*m_A' = eps^2 * ~10^14 s^-1
        #   => 10^3 s^-1 -> eps^2 ~ 10^-11 -> eps ~ 3e-6
        result = loglike_mediator_lifetime(m_chi=14.8e9, m_ap=26.6e6, epsilon=3e-6)
        assert result < -5, f"got {result}, expected strong penalty for pre-BBN decay"

    def test_below_2_electron_mass_no_decay(self):
        """If m_A' < 2 m_e (~1.022 MeV), decay to e+e- is kinematically forbidden.
        Mediator is stable regardless of epsilon."""
        from channels_extended import loglike_mediator_lifetime, M_E_MEV
        # m_A' = 0.5 MeV (below 2 m_e)
        result = loglike_mediator_lifetime(m_chi=14.8e9, m_ap=0.5e6, epsilon=1e-5)
        assert result == 0.0, f"got {result}, expected 0 (no decay channel)"

    def test_negative_mass_returns_neg_inf(self):
        from channels_extended import loglike_mediator_lifetime
        assert loglike_mediator_lifetime(m_chi=14.8e9, m_ap=-1.0, epsilon=1e-35) == -np.inf
        assert loglike_mediator_lifetime(m_chi=-1.0, m_ap=26.6e6, epsilon=1e-35) == -np.inf

    def test_negative_epsilon_returns_neg_inf(self):
        from channels_extended import loglike_mediator_lifetime
        assert loglike_mediator_lifetime(m_chi=14.8e9, m_ap=26.6e6, epsilon=-1e-35) == -np.inf

    def test_nan_returns_neg_inf(self):
        from channels_extended import loglike_mediator_lifetime
        assert loglike_mediator_lifetime(m_chi=np.nan, m_ap=26.6e6, epsilon=1e-35) == -np.inf
        assert loglike_mediator_lifetime(m_chi=14.8e9, m_ap=np.nan, epsilon=1e-35) == -np.inf
        assert loglike_mediator_lifetime(m_chi=14.8e9, m_ap=26.6e6, epsilon=np.nan) == -np.inf

    def test_lifetime_calculation_is_physically_reasonable(self):
        """The lifetime should follow tau = hbar / Gamma where Gamma is
        proportional to eps^2 * m_A'. Test this scaling directly."""
        from channels_extended import compute_mediator_lifetime_s
        # tau should scale as 1/eps^2
        tau1 = compute_mediator_lifetime_s(m_ap_mev=26.6, epsilon=1e-5)
        tau2 = compute_mediator_lifetime_s(m_ap_mev=26.6, epsilon=1e-10)
        # tau2 / tau1 = (1e-5 / 1e-10)^2 = 1e10
        ratio = tau2 / tau1
        assert 1e8 < ratio < 1e12, f"ratio = {ratio}, expected ~1e10"

    def test_lifetime_scales_inversely_with_mass(self):
        """Gamma ~ m_A' (for m_A' >> 2 m_f), so tau ~ 1/m_A'."""
        from channels_extended import compute_mediator_lifetime_s
        tau1 = compute_mediator_lifetime_s(m_ap_mev=26.6, epsilon=1e-10)
        tau2 = compute_mediator_lifetime_s(m_ap_mev=53.2, epsilon=1e-10)  # 2x mass
        # tau2 / tau1 = 26.6/53.2 = 0.5
        ratio = tau2 / tau1
        assert 0.4 < ratio < 0.6, f"ratio = {ratio}, expected ~0.5"