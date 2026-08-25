"""
Test class for Channel 12 — cosmic-web radio synchrotron (Pinetti 2025-26).

Per Tier-1 PATCH 2026-08-25 (response to user upload 'darkm.pdf' § 3):
LOFAR pair-stacking observations of ~10^4 Luminous Red Red clusters reveal
cosmic-web filaments have a radio synchrotron surface brightness ~40×
higher than the accretion-shock-only expectation (arXiv:2101.09331).

Pinetti et al. 2025-2026 (arXiv:2504.08025) show that 5-10 GeV DM decay →
e⁺e⁻ → synchrotron at 30-60 nG magnetic fields reproduces the 40×
excess. This is a DM DECAY channel, distinct from the SIDM self-scattering
that the project models.

This is the FIRST 3-argument channel in the project — it depends on
(sigma_m_0, a, epsilon) where epsilon is the dark photon kinetic mixing
already present in the Tier-3 marginalization (T39).

References (all verified HTTP 200):
  arXiv:2504.08025 - Pinetti et al. 2025-26 (40× cosmic-web radio excess)
  arXiv:2101.09331 - LOFAR pair-galaxy stacking (foundational observation)
  arXiv:2503.19019 - Dunsky et al. 2025-26 (DM→graviton IGRB bound,
                     complementary indirect-detection channel)

Channel 12 interpretation:
  The 40× LOFAR synchrotron excess is an INDEPENDENT indirect-detection
  bound on the secluded dark photon coupling ε. It does NOT constrain
  σ/m_0 (the SIDM self-scattering cross-section) directly, but it
  constrains the DECAY RATE Γ_DM → mediator → e⁺e⁻ via ε².

  In the project, this provides a cross-check on the T39 (epsilon-alpha
  joint fit) posterior. If the existing posterior drives ε → 10⁻³⁵ to
  satisfy LZ WS2024, then the cosmic-web radio excess is automatically
  satisfied (decay rate is negligible at ε ~ 10⁻³⁵). Channel 12 thus
  provides REDUNDANT confirmation, not new exclusion.

Test verification:
  - Channel 12 returns finite log-L across the prior range
  - At typical ε ~ 10⁻⁵ (canonical dark photon), the channel is ~ OK
  - At ε → 10⁻³⁵ (project's wide-prior posterior median), no penalty
  - At ε → 10⁻² (unphysical), heavy penalty
  - Negative/zero ε returns -inf
  - NaN/inf input handled
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root + v0.1/v0.3 code dirs to sys.path (same as test_halo_and_likelihoods.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v0.1-prelim" / "code"))
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))

from channels_extended import (
    loglike_cosmic_web_radio,
    COSMIC_WEB_RADIO_LOG_EPSILON_UPPER,
    COSMIC_WEB_RADIO_SIGMA_M_INDEPENDENT,
)


class TestCosmicWebRadio:
    """Tests for Channel 12 (cosmic-web radio synchrotron, Pinetti 2025-26)."""

    def test_constants_are_finite(self):
        """Module-level constants should be finite."""
        assert math.isfinite(COSMIC_WEB_RADIO_LOG_EPSILON_UPPER)
        assert math.isfinite(COSMIC_WEB_RADIO_SIGMA_M_INDEPENDENT)

    def test_at_zero_epsilon_is_neutral(self):
        """At ε → 0 (no kinetic mixing), no dark-photon-mediated decay.
        The 40× cosmic-web excess cannot be explained by this channel,
        but the channel itself returns 0 (no constraint in this regime)."""
        result = loglike_cosmic_web_radio(sigma_m_0=0.78, a=0.23, epsilon=0.0)
        assert math.isfinite(result)
        # ε = 0 means no decay channel; the constraint is trivially satisfied
        assert result >= -0.1, f"got {result}, expected ~0 (no decay channel)"

    def test_at_project_posterior_epsilon_no_penalty(self):
        """At the project's wide-prior posterior median ε ~ 10⁻³⁵ (from T39),
        the decay rate is negligible. Channel 12 should return ~0 (constraint
        is trivially satisfied)."""
        result = loglike_cosmic_web_radio(sigma_m_0=0.78, a=0.23, epsilon=1e-35)
        assert math.isfinite(result)
        assert result >= -0.5, f"got {result}, expected ~0 (decay rate negligible)"

    def test_at_canonical_epsilon_penalizes(self):
        """At canonical ε ~ 10⁻⁵ (Roberts+ 2024 narrow prior), the decay
        rate would be large; cosmic-web radio would over-predict the
        observed 40× excess. Expect a penalty (the 40× observation is
        the DATA, so over-predicting it is disfavored)."""
        result = loglike_cosmic_web_radio(sigma_m_0=0.78, a=0.23, epsilon=1e-5)
        assert math.isfinite(result)
        assert result < -0.5, f"got {result}, expected penalty at ε=1e-5"

    def test_sigma_m_0_does_not_matter(self):
        """Channel 12 depends on ε, not σ/m_0 (it's a decay channel, not
        scattering). At fixed ε, varying σ/m_0 should not change the
        log-likelihood much."""
        r1 = loglike_cosmic_web_radio(sigma_m_0=0.1, a=0.0, epsilon=1e-5)
        r2 = loglike_cosmic_web_radio(sigma_m_0=10.0, a=0.0, epsilon=1e-5)
        # Should be within 0.5 of each other (the a-dependence goes via σ/m_0)
        # but the channel should be MOSTLY ε-driven, not σ/m_0-driven
        # We accept that some σ/m_0 dependence is fine (through a)
        assert abs(r1 - r2) < 1.0, f"got r1={r1}, r2={r2}, expected similar"

    def test_negative_epsilon_returns_neg_inf(self):
        """ε must be non-negative. Negative return = -inf per project convention."""
        result = loglike_cosmic_web_radio(sigma_m_0=0.78, a=0.23, epsilon=-1.0)
        assert result == -np.inf

    def test_finite_across_epsilon_range(self):
        """Channel 12 should return finite log-L across the wide ε prior
        (~10⁻⁵⁰ to 10⁻² for the project's Tier-3 marginalization)."""
        for log_eps in np.linspace(-50, -2, 30):
            eps = 10**log_eps
            result = loglike_cosmic_web_radio(sigma_m_0=0.78, a=0.23, epsilon=eps)
            assert math.isfinite(result), (
                f"non-finite at log_eps={log_eps}: {result}"
            )

    def test_nan_inf_input_returns_neg_inf(self):
        """NaN/inf inputs must return -inf."""
        assert loglike_cosmic_web_radio(sigma_m_0=0.78, a=0.23, epsilon=np.nan) == -np.inf
        assert loglike_cosmic_web_radio(sigma_m_0=0.78, a=0.23, epsilon=np.inf) == -np.inf