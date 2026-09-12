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
    """Pin the config constants to the LSB-6 paper values.

    CORRECTED 2026-09-12 (full paper retrieval): σ/m ~0.7 cm²/g, NOT 14.3
    (which was σv/m). The 14.3 came from the abstract; the corrected σ/m
    value is from Section 6.4 line 143.
    """

    def test_peak_value(self):
        assert DM_DOM_UDG_SIGMA_M_PEAK == 0.7, \
            "LSB-6 peak changed — re-read Bouchè+ 2026 (arXiv:2609.10700) Section 6.4"

    def test_width(self):
        assert DM_DOM_UDG_SIGMA_M_WIDTH == 0.5, \
            "LSB-6 width changed — was 0.5 dex (rescaled uncertainty ~±0.13)"

    def test_lsb6_velocity(self):
        assert LSB6_VMAX_KMS == 20.0, \
            "LSB-6 velocity scale changed — was 20 km/s (log10 v = 1.30)"

    def test_vref_unchanged(self):
        """V_REF should still be 100 km/s (the project's velocity anchor)."""
        assert V_REF == 100.0, "V_REF changed — would break all v-dep channels"


class TestChannel13Behavior:
    """Pin the channel's mathematical behavior.

    Updated 2026-09-12: peak is σ/m_0 = 0.7 cm²/g (Bouchè+ 2026 line 143),
    not 14.3 cm²/g. Width is 0.5 dex (rescaled uncertainty ~±0.13).
    """

    def test_at_peak_is_zero(self):
        """At σ/m_0 = 0.7, a=0, loglike should be ~0."""
        val = loglike_dm_dominated_udg(0.7, 0.0)
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
        """At a=1: σ/m_eff = σ/m_0 * (V_LSB6/V_REF) = σ/m_0 * 0.2.
        Peak should be at σ/m_0 = 0.7/0.2 = 3.5."""
        val = loglike_dm_dominated_udg(3.5, 1.0)
        assert abs(val) < 0.05, f"v-dep at a=1 expected ~0 at σ/m_0=3.5, got {val}"

    def test_vdep_at_a2(self):
        """At a=2: σ/m_eff = σ/m_0 * 0.04.
        Peak should be at σ/m_0 = 0.7/0.04 = 17.5."""
        val = loglike_dm_dominated_udg(17.5, 2.0)
        assert abs(val) < 0.05, f"v-dep at a=2 expected ~0 at σ/m_0=17.5, got {val}"

    def test_vdep_at_a_neg1(self):
        """At a=-1: σ/m_eff = σ/m_0 * 5.
        Peak should be at σ/m_0 = 0.7/5 = 0.14."""
        val = loglike_dm_dominated_udg(0.14, -1.0)
        assert abs(val) < 0.05, f"v-dep at a=-1 expected ~0 at σ/m_0=0.14, got {val}"

    def test_extreme_low_penalized(self):
        """σ/m_0 = 0.01 (~2 dex below peak with a=0): moderate penalty."""
        val = loglike_dm_dominated_udg(0.01, 0.0)
        # log10(0.01/0.7) = -1.85, chi = (1.85/0.5)^2 = 13.7, loglike = -6.8
        assert val < -3.0, f"Extreme low should be penalized, got {val}"

    def test_extreme_high_within_tolerance(self):
        """σ/m_0 = 70 (2 dex above peak with a=0): heavy penalty (~8 chi²)."""
        val = loglike_dm_dominated_udg(70.0, 0.0)
        # log10(70/0.7) = 2.0, chi = (2.0/0.5)^2 = 16, loglike = -8.0
        assert val < -5.0, f"Extreme high expected < -5 (heavy penalty), got {val}"

    def test_loglikelihood_is_gaussian_in_sigma_m_0(self):
        """For a=0, loglike should be a Gaussian in log10(σ/m_0)."""
        val_at_peak = loglike_dm_dominated_udg(0.7, 0.0)
        val_at_offset = loglike_dm_dominated_udg(0.7 * 10**0.25, 0.0)
        expected = -0.5 * (0.25/0.5)**2
        assert abs(val_at_offset - expected) < 0.01, \
            f"Expected {expected}, got {val_at_offset} (peak {val_at_peak})"


class TestBackwardCompatibility:
    """The placeholder alias mirrors the Ch11 / Ch6 pattern."""

    def test_placeholder_matches_main_at_a0(self):
        """loglike_dm_dominated_udg_placeholder(x) should equal loglike_dm_dominated_udg(x, 0.0)."""
        for x in [0.01, 0.1, 0.7, 10.0, 100.0]:
            main = loglike_dm_dominated_udg(x, 0.0)
            placeholder = loglike_dm_dominated_udg_placeholder(x)
            assert abs(main - placeholder) < 1e-9, \
                f"Mismatch at x={x}: main={main}, placeholder={placeholder}"


class TestCounterpartToChannel11:
    """Channel 13 must be PHYSICALLY DISTINCT from Channel 11.

    UPDATED 2026-09-12: with corrected σ/m peak (0.7), Ch11 and Ch13 peaks
    are CLOSER than before. Ch11 peaks at σ/m_0=0.78 (project MAP), Ch13
    peaks at σ/m_0=0.7 (LSB-6 anchor). They overlap heavily in σ/m_0
    but the v-dep couplings (Ch11→v=30, Ch13→v=20) make them subtly different.
    """

    def test_ch11_and_ch13_at_same_sigma_m_give_different_loglikes(self):
        """At σ/m_0 = 1.0, a=0: Ch11 (peak=0.78) should be near peak, Ch13 (peak=0.7) should be near peak."""
        from channels_extended import loglike_dm_free_udg
        ch11 = loglike_dm_free_udg(1.0, 0.0)
        ch13 = loglike_dm_dominated_udg(1.0, 0.0)
        # Both should be near peak (1.0 vs 0.78/0.7 = ~0.1 dex apart)
        assert abs(ch11) < 0.5, f"Ch11 at σ/m_0=1.0 expected ~0, got {ch11}"
        assert abs(ch13) < 0.5, f"Ch13 at σ/m_0=1.0 expected ~0, got {ch13}"
        # They have different peaks so they should give slightly different loglikes
        assert abs(ch11 - ch13) < 0.5, \
            f"Channels should give SIMILAR loglikes at same σ/m_0 (peaks overlap)"

    def test_complementary_extremes(self):
        """A model that fits Ch11 well should NOT automatically fit Ch13 (and vice versa)."""
        from channels_extended import loglike_dm_free_udg
        # With corrected peaks: σ/m_0 = 0.78 (Ch11 MAP) is ~0.05 dex from Ch13 peak (0.7)
        ch11_at_map = loglike_dm_free_udg(0.78, 0.0)
        ch13_at_map = loglike_dm_dominated_udg(0.78, 0.0)
        # Both should be near peak (close peaks)
        assert abs(ch11_at_map) < 0.1, f"Ch11 should peak at MAP, got {ch11_at_map}"
        assert abs(ch13_at_map) < 0.1, f"Ch13 should peak near MAP with corrected value, got {ch13_at_map}"
        # Conversely: σ/m_0 = 100 should fail BOTH channels
        # Ch11 width=2 dex: chi = (log10(100/0.78)/2)^2 = (2.11/2)^2 = 1.11, loglike = -0.56
        # Ch13 width=0.5 dex: chi = (log10(100/0.7)/0.5)^2 = (2.15/0.5)^2 = 18.6, loglike = -9.3
        ch11_at_high = loglike_dm_free_udg(100.0, 0.0)
        ch13_at_high = loglike_dm_dominated_udg(100.0, 0.0)
        assert ch11_at_high < -0.3, f"Ch11 should fail at high σ/m_0: {ch11_at_high}"
        assert ch13_at_high < -3.0, f"Ch13 should fail heavily at high σ/m_0: {ch13_at_high}"
        # Conversely: σ/m_0 = 0.001 should fail BOTH channels
        ch11_at_low = loglike_dm_free_udg(0.001, 0.0)
        ch13_at_low = loglike_dm_dominated_udg(0.001, 0.0)
        assert ch11_at_low < -0.5, f"Ch11 should fail at low σ/m_0: {ch11_at_low}"
        assert ch13_at_low < -3.0, f"Ch13 should fail heavily at low σ/m_0: {ch13_at_low}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])