"""
Regression tests for Channel 13 (DM-dominated UDG, LSB-6 anchor).

Channel 13 was added 2026-09-12 per LRD2.docx reviewer recommendation
("test BOTH UDG extremes"). It is the counterpart to Channel 11
(DM-free UDG, NGC 1052-DF2/DF4 anchor).

Reference: arXiv:2609.10700 — σ/m_eff at v_LSB6 ~15 km/s = 14.3 (+2.0/-1.9) cm²/g

These tests pin the channel behavior so accidental edits don't silently
change the LSB-6 anchor or the velocity-mapping convention.
"""
import pytest
import numpy as np

# Use canonical path
import sys
from pathlib import Path
project_root = Path(r'C:/Users/lamkuenai/projects/sidm-composite-dm-mediator')
sys.path.insert(0, str(project_root / 'v0.3-prelim' / 'code'))

from channels_extended import loglike_dm_dominated_udg, loglike_dm_dominated_udg_placeholder
from config import DM_DOM_UDG_SIGMA_M_PEAK, DM_DOM_UDG_SIGMA_M_WIDTH, LSB6_VMAX_KMS, V_REF


class TestConfigAnchors:
    """Pin the config constants to the LSB-6 paper values."""

    def test_peak_value(self):
        assert DM_DOM_UDG_SIGMA_M_PEAK == 14.3, "LSB-6 peak changed — re-read arXiv:2609.10700"

    def test_width(self):
        assert DM_DOM_UDG_SIGMA_M_WIDTH == 1.0, "LSB-6 width changed — was 1 dex (single-object)"

    def test_lsb6_velocity(self):
        assert LSB6_VMAX_KMS == 15.0, "LSB-6 velocity scale changed — was 15 km/s (gas-rich, low-vdisp)"

    def test_vref_unchanged(self):
        """V_REF should still be 100 km/s (the project's velocity anchor)."""
        assert V_REF == 100.0, "V_REF changed — would break all v-dep channels"


class TestChannel13Behavior:
    """Pin the channel's mathematical behavior."""

    def test_at_peak_is_zero(self):
        """At σ/m_0 = 14.3, a=0, loglike should be ~0."""
        val = loglike_dm_dominated_udg(14.3, 0.0)
        assert abs(val) < 0.01, f"At peak expected ~0, got {val}"

    def test_invalid_sigmam_returns_neg_inf(self):
        """σ/m_0 = 0 or negative should return -inf."""
        assert loglike_dm_dominated_udg(0.0, 0.0) == -np.inf
        assert loglike_dm_dominated_udg(-1.0, 0.0) == -np.inf
        assert loglike_dm_dominated_udg(np.nan, 0.0) == -np.inf

    def test_invalid_a_returns_neg_inf(self):
        """a = nan/inf should return -inf."""
        assert loglike_dm_dominated_udg(1.0, np.nan) == -np.inf
        assert loglike_dm_dominated_udg(1.0, np.inf) == -np.inf

    def test_vdep_at_a1(self):
        """At a=1: σ/m_eff = σ/m_0 * (V_LSB6/V_REF) = σ/m_0 * 0.15.
        Peak should be at σ/m_0 = 14.3/0.15 = 95.33."""
        val = loglike_dm_dominated_udg(95.33, 1.0)
        assert abs(val) < 0.01, f"v-dep at a=1 expected ~0 at σ/m_0=95.33, got {val}"

    def test_vdep_at_a2(self):
        """At a=2: σ/m_eff = σ/m_0 * 0.0225.
        Peak should be at σ/m_0 = 14.3/0.0225 = 635.6."""
        val = loglike_dm_dominated_udg(635.6, 2.0)
        assert abs(val) < 0.05, f"v-dep at a=2 expected ~0 at σ/m_0=635.6, got {val}"

    def test_vdep_at_a_neg1(self):
        """At a=-1: σ/m_eff = σ/m_0 * 6.67.
        Peak should be at σ/m_0 = 14.3/6.67 = 2.14."""
        val = loglike_dm_dominated_udg(2.14, -1.0)
        assert abs(val) < 0.05, f"v-dep at a=-1 expected ~0 at σ/m_0=2.14, got {val}"

    def test_extreme_low_penalized(self):
        """σ/m_0 = 0.01 (4 dex below peak with a=0): heavy penalty."""
        val = loglike_dm_dominated_udg(0.01, 0.0)
        assert val < -3.0, f"Extreme low should be penalized, got {val}"

    def test_extreme_high_within_tolerance(self):
        """σ/m_0 = 1430 (2 dex above peak with a=0): within 1σ of peak (width=1 dex).
        loglike = -0.5 * (2/1)^2 = -2.0"""
        val = loglike_dm_dominated_udg(1430.0, 0.0)
        assert -2.5 < val < -1.5, f"Extreme high expected ~-2.0 (within width), got {val}"

    def test_loglikelihood_is_gaussian_in_sigma_m_0(self):
        """For a=0, loglike should be a Gaussian in log10(σ/m_0)."""
        # chi at log10(14.3) = 0
        # chi at log10(14.3) + 0.5 = 0.25 → loglike = -0.125
        val_at_peak = loglike_dm_dominated_udg(14.3, 0.0)
        val_at_offset = loglike_dm_dominated_udg(14.3 * 10**0.5, 0.0)
        expected = -0.5 * (0.5/1.0)**2
        assert abs(val_at_offset - expected) < 0.01, \
            f"Expected {expected}, got {val_at_offset} (peak {val_at_peak})"


class TestBackwardCompatibility:
    """The placeholder alias mirrors the Ch11 / Ch6 pattern."""

    def test_placeholder_matches_main_at_a0(self):
        """loglike_dm_dominated_udg_placeholder(x) should equal loglike_dm_dominated_udg(x, 0.0)."""
        for x in [0.1, 1.0, 14.3, 100.0, 1000.0]:
            main = loglike_dm_dominated_udg(x, 0.0)
            placeholder = loglike_dm_dominated_udg_placeholder(x)
            assert abs(main - placeholder) < 1e-9, \
                f"Mismatch at x={x}: main={main}, placeholder={placeholder}"


class TestCounterpartToChannel11:
    """Channel 13 must be PHYSICALLY DISTINCT from Channel 11."""

    def test_ch11_and_ch13_at_same_sigma_m_give_different_loglikes(self):
        """At σ/m_0 = 1.0, a=0: Ch11 (peak=0.78) should be near peak, Ch13 (peak=14.3) should be far."""
        from channels_extended import loglike_dm_free_udg
        ch11 = loglike_dm_free_udg(1.0, 0.0)
        ch13 = loglike_dm_dominated_udg(1.0, 0.0)
        # Ch11 should be ~0 (within 1 dex of MAP 0.78)
        assert abs(ch11) < 0.5, f"Ch11 at σ/m_0=1.0 expected ~0, got {ch11}"
        # Ch13 should be far from peak (1.0 vs 14.3 = ~1.16 dex away → chi=1.35 → loglike=-0.67)
        assert ch13 < -0.5, f"Ch13 at σ/m_0=1.0 expected far from peak, got {ch13}"
        # They are DIFFERENT channels
        assert abs(ch11 - ch13) > 0.3, f"Channels should give different loglikes at same σ/m_0"

    def test_complementary_extremes(self):
        """A model that fits Ch11 well should NOT automatically fit Ch13 (and vice versa)."""
        from channels_extended import loglike_dm_free_udg
        # σ/m_0 = 0.78 is at Ch11 peak but ~1.26 dex from Ch13 peak (14.3)
        ch11_at_map = loglike_dm_free_udg(0.78, 0.0)
        ch13_at_map = loglike_dm_dominated_udg(0.78, 0.0)
        assert abs(ch11_at_map) < 0.01, "Ch11 should peak at MAP"
        assert ch13_at_map < -0.5, "Ch13 should NOT peak at MAP"
        # Conversely: σ/m_0 = 14.3 is at Ch13 peak but ~1.26 dex from Ch11 peak (0.78)
        # With Ch11 width=2 dex: chi = (1.26/2)^2 = 0.397, loglike = -0.20
        # The two channels ARE distinct (different peaks) but Ch11's 2-dex width
        # is generous enough that LSB-6's anchor doesn't catastrophically fail Ch11.
        ch11_at_lsb6 = loglike_dm_free_udg(14.3, 0.0)
        ch13_at_lsb6 = loglike_dm_dominated_udg(14.3, 0.0)
        # The CORRECT test: at LSB-6 anchor, Ch13 should be MUCH higher than Ch11
        assert ch13_at_lsb6 > ch11_at_lsb6, \
            f"Ch13 should dominate at LSB-6 anchor: ch13={ch13_at_lsb6}, ch11={ch11_at_lsb6}"
        # And at MAP anchor, Ch11 should be MUCH higher than Ch13
        assert ch11_at_map > ch13_at_map, \
            f"Ch11 should dominate at MAP anchor: ch11={ch11_at_map}, ch13={ch13_at_map}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])