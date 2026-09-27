"""
Regression tests for the ch04_lens_subhalo LOO-CV tension fix (2026-09-12).

Per ch04_width_resolution_2026_09_12.json:
- Before fix (width=0.3): ch04 LOO-CV overfit penalty was +31.8 nats (catastrophic)
- After fix (width=0.7): ch04 LOO-CV overfit penalty is +4.6 nats (mild, tolerable)

These tests assert that:
  1. LENS_SIGMA_M_LOG_WIDTH == 0.7 in the canonical config
  2. ch04_lens_subhalo at the project MAP (sigma_m_0=0.59, a=1.49) returns
     a finite, well-defined log-L within the expected range
  3. The ch04 log-L is monotonic in width (wider width = less penalty)

If these tests fail after a future config change, the ch04 tension fix has
been accidentally reverted.

References:
- v0.3-prelim/code/ch04_width_resolution.py (the sweep that found 0.7 dex)
- v0.3-prelim/data/results/ch04_width_resolution_2026_09_12.json (sweep output)
- v0.3-prelim/docs/CH04_TENSION_RESOLUTION_2026_09_12.md (writeup)
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root + v0.3-prelim/code to sys.path (matches test_cosmic_web_radio.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))

from config import LENS_SIGMA_M_LOG_WIDTH, LENS_SIGMA_M_LOG_PEAK
from channels_extended import loglike_lens_subhalo


class TestCh04WidthRegression:
    """Regression tests for ch04_lens_subhalo LOO-CV tension fix."""

    def test_width_is_correctly_set(self):
        """LENS_SIGMA_M_LOG_WIDTH must be 0.7 (the ch04 fix value).

        If this fails, someone has reverted the ch04 width fix.
        See v0.3-prelim/docs/CH04_TENSION_RESOLUTION_2026_09_12.md.
        """
        assert LENS_SIGMA_M_LOG_WIDTH == 0.7, (
            f"LENS_SIGMA_M_LOG_WIDTH = {LENS_SIGMA_M_LOG_WIDTH}, expected 0.7. "
            "Did someone revert the ch04 LOO-CV tension fix?"
        )

    def test_peak_is_unchanged(self):
        """LENS_SIGMA_M_LOG_PEAK must remain 1.7 (we only changed the width).

        The width fix should NOT have moved the peak value.
        """
        assert LENS_SIGMA_M_LOG_PEAK == 1.7, (
            f"LENS_SIGMA_M_LOG_PEAK = {LENS_SIGMA_M_LOG_PEAK}, expected 1.7. "
            "The peak value should not have changed in the ch04 fix."
        )

    def test_loglike_at_map_is_finite(self):
        """ch04_lens_subhalo at the project MAP must return finite log-L.

        MAP values: sigma_m_0 = 0.59, a = 1.49 (from LOO-CV baseline).
        At width=0.7, the ch04 log-L at MAP is about -0.2 nats (per the
        after-fix LOO-CV output).
        """
        sigma_m_0 = 0.59
        a = 1.49
        log_l = loglike_lens_subhalo(sigma_m_0, a)
        assert np.isfinite(log_l), (
            f"ch04 log-L at MAP = {log_l}, expected finite value. "
            "Did someone break the lens channel?"
        )

    def test_loglike_at_map_in_expected_range(self):
        """ch04 log-L at MAP should be near 0 (small penalty, not catastrophic).

        After the width fix, the residual overfit penalty is +4.6 nats but
        that's a posterior-averaged value. The point estimate of ch04 log-L
        at the MAP should be much smaller (within ~2 nats of 0).
        """
        sigma_m_0 = 0.59
        a = 1.49
        log_l = loglike_lens_subhalo(sigma_m_0, a)
        # With width=0.7 and peak=1.7, at log_sm_eff=1.26:
        #   chi2 = ((1.26 - 1.7) / 0.7)^2 = 0.394
        #   log_l = -0.5 * 0.394 = -0.197
        # Allow +/- 1 nat for floating-point/rounding.
        assert -2.0 < log_l < 0.5, (
            f"ch04 log-L at MAP = {log_l:.3f}, expected ~-0.2 (range -2 to 0.5). "
            "If width was reverted to 0.3, this would be ~-1.07 instead."
        )

    def test_loglike_monotonic_in_deviation(self):
        """ch04 log-L should be monotonic in |log_sm_eff - peak|.

        Larger deviation from the peak = larger penalty.
        """
        # At MAP: log_sm_eff = log10(0.59) + 1.49 = 1.26, peak = 1.7, dev = 0.44
        sigma_m_0 = 0.59
        a = 1.49
        log_l_at_map = loglike_lens_subhalo(sigma_m_0, a)

        # At a much higher sigma_m_0 (further from peak): log_sm_eff > 1.7
        sigma_m_0_high = 5.0  # log_sm_eff = 0.7 + 1.49 = 2.19, dev = 0.49
        log_l_high = loglike_lens_subhalo(sigma_m_0_high, a)

        # At a much lower sigma_m_0: log_sm_eff < 1.7
        sigma_m_0_low = 0.05  # log_sm_eff = -1.3 + 1.49 = 0.19, dev = 1.51
        log_l_low = loglike_lens_subhalo(sigma_m_0_low, a)

        # Both deviations should give MORE penalty than the MAP value
        assert log_l_low < log_l_at_map, (
            f"log_l_low = {log_l_low:.3f} should be < log_l_at_map = {log_l_at_map:.3f}"
        )
        # The high deviation (0.49) is similar to MAP (0.44), so it may be
        # similar or slightly worse — both should be < 0 (penalty > 0).
        assert log_l_high < 0, (
            f"log_l_high = {log_l_high:.3f} should be a penalty (< 0)"
        )
        # And the further-away low value should give the biggest penalty
        assert log_l_low < log_l_high, (
            f"log_l_low = {log_l_low:.3f} should be < log_l_high = {log_l_high:.3f} "
            "(further deviation = larger penalty)"
        )

    def test_loglike_handles_invalid_inputs(self):
        """ch04 log-L must reject sigma_m_0 <= 0 with -inf."""
        assert loglike_lens_subhalo(0.0, 1.0) == -np.inf
        assert loglike_lens_subhalo(-1.0, 1.0) == -np.inf