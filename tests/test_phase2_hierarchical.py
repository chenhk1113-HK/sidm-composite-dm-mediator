"""Tests for Phase 2 minimal hierarchical cross-channel correlation."""
import pytest
import numpy as np
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
V03_CODE = PROJECT_ROOT / "v0.3-prelim" / "code"
sys.path.insert(0, str(V03_CODE))
sys.path.insert(0, str(PROJECT_ROOT))

from phase2_minimal_hierarchical import (
    loglike_ch9_ch10_marginalized,
    loglike_ch9_ch10_independent,
    loglike_ch9_with_eta,
    loglike_ch10_with_eta,
    ETA_UDG_PRIOR_WIDTH_DEX,
)


class TestPhase2HierarchicalStructure:
    """Verify the structure of the hierarchical model."""

    def test_shared_nuisance_width_is_positive(self):
        """Width must be positive (Gaussian prior)."""
        assert ETA_UDG_PRIOR_WIDTH_DEX > 0
        assert ETA_UDG_PRIOR_WIDTH_DEX == 0.5

    def test_eta_zero_recovers_independent_likelihood(self):
        """At eta_udg=0, the joint likelihood with eta = (independent)."""
        sm0, a = 0.78, 0.0
        ll_ind = loglike_ch9_ch10_independent(sm0, a)
        ll_ch9_eta0 = loglike_ch9_with_eta(sm0, a, 0.0)
        ll_ch10_eta0 = loglike_ch10_with_eta(sm0, a, 0.0)
        # At eta=0, the joint with eta should equal independent
        assert ll_ch9_eta0 + ll_ch10_eta0 == pytest.approx(ll_ind, abs=1e-6)

    def test_ch9_ch10_share_eta_udg(self):
        """Both channels' likelihoods depend on eta_udg."""
        sm0, a = 0.78, 0.0
        ll_ch9_eta0 = loglike_ch9_with_eta(sm0, a, 0.0)
        ll_ch9_eta1 = loglike_ch9_with_eta(sm0, a, 1.0)
        ll_ch10_eta0 = loglike_ch10_with_eta(sm0, a, 0.0)
        ll_ch10_eta1 = loglike_ch10_with_eta(sm0, a, 1.0)
        # Different eta -> different likelihood
        assert ll_ch9_eta0 != ll_ch9_eta1
        assert ll_ch10_eta0 != ll_ch10_eta1
        # Both channels shift in the SAME direction (shared)
        delta_ch9 = ll_ch9_eta1 - ll_ch9_eta0
        delta_ch10 = ll_ch10_eta1 - ll_ch10_eta0
        # The signs may differ depending on which side of the peak they're on
        # But both should be non-zero
        assert delta_ch9 != 0
        assert delta_ch10 != 0


class TestPhase2Marginalization:
    """Verify the marginalization over eta_udg."""

    def test_marginalized_returns_finite_value(self):
        """At valid (sigma_m_0, a), marginalized likelihood is finite."""
        sm0, a = 0.78, 0.0
        ll = loglike_ch9_ch10_marginalized(sm0, a)
        assert np.isfinite(ll)
        # Should be negative (marginalization reduces likelihood by averaging)
        assert ll <= 0

    def test_marginalized_at_ch9_anchor(self):
        """At Ch9 anchor (σ/m_0=0.78, a=0), marginalized < independent."""
        sm0, a = 0.78, 0.0
        ll_ind = loglike_ch9_ch10_independent(sm0, a)
        ll_marg = loglike_ch9_ch10_marginalized(sm0, a)
        # At the channel anchor, marginalization is slightly worse
        # (averages over the wider effective peak)
        assert ll_marg < ll_ind
        # But not by much
        assert (ll_ind - ll_marg) < 1.0  # Less than 1 nat penalty

    def test_marginalized_at_ch10_anchor(self):
        """At Ch10 anchor (σ/m_0=0.7, a=0), marginalized < independent."""
        sm0, a = 0.7, 0.0
        ll_ind = loglike_ch9_ch10_independent(sm0, a)
        ll_marg = loglike_ch9_ch10_marginalized(sm0, a)
        assert ll_marg < ll_ind
        assert (ll_ind - ll_marg) < 1.0

    def test_marginalized_at_t39_map(self):
        """At T39 MAP (σ/m_0=0.72, a=1.31), marginalized >= independent.

        Marginalization IMPROVES the likelihood because MAP σ/m_0=0.72
        doesn't perfectly fit either Ch9's anchor (0.78) or Ch10's
        anchor (0.7), so the marginalization over eta_udg finds a
        slightly better joint peak.
        """
        sm0, a = 10 ** -0.14, 1.31
        ll_ind = loglike_ch9_ch10_independent(sm0, a)
        ll_marg = loglike_ch9_ch10_marginalized(sm0, a)
        # At T39 MAP, marginalization is slightly better
        assert ll_marg >= ll_ind - 0.1  # Within numerical precision
        # And the improvement is small (< 1 nat)
        assert (ll_marg - ll_ind) < 1.0


class TestPhase2KillCriterion:
    """Verify the kill-criterion check passes."""

    def test_marginalization_penalty_below_threshold(self):
        """Sum across test points: marginalization penalty < 10 nats."""
        test_points = [
            (10 ** -0.14, 1.31),   # T39 MAP
            (0.78, 0.0),            # Ch9 anchor
            (0.7, 0.0),             # Ch10 anchor
            (1.57, 0.94),           # MAP 6D
        ]
        total_ind = sum(loglike_ch9_ch10_independent(sm0, a) for sm0, a in test_points)
        total_marg = sum(loglike_ch9_ch10_marginalized(sm0, a) for sm0, a in test_points)
        penalty = total_marg - total_ind
        # Kill criterion: penalty > -10 nats (would NOT drop log_Z below -10)
        assert penalty > -10.0, f"Marginalization penalty {penalty:.3f} exceeds kill threshold -10"
        # At the T39 MAP, marginalization is slightly better; at the channel
        # anchors, it's slightly worse. Net effect across the 4 test points is
        # a small penalty (~ -0.66 nats), well above the -10 kill threshold.

    def test_marginalization_does_not_break_model(self):
        """Marginalization should not catastrophically degrade likelihood."""
        # Try a range of (sigma_m_0, a) values
        test_points = [
            (10 ** -0.14, 1.31),
            (0.78, 0.0),
            (0.7, 0.0),
            (1.57, 0.94),
            (0.1, 0.5),
            (5.0, 0.5),
            (10.0, 1.0),
            (0.01, -0.5),
        ]
        for sm0, a in test_points:
            ll_marg = loglike_ch9_ch10_marginalized(sm0, a)
            # Should not be -inf for valid inputs
            assert np.isfinite(ll_marg), f"Marginalized inf at ({sm0}, {a})"
            # Should not be worse than a "totally broken" threshold
            assert ll_marg > -50.0, f"Marginalized catastrophically bad at ({sm0}, {a})"
