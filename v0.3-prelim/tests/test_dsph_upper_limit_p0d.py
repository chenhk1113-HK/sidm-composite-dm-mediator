"""Regression tests for the dSph channel R12 P0-D (2026-08-17).

The dSph channel was previously a bimodal-with-dip surrogate (peaks at
sigma/m ~ 0.1 AND ~10 cm^2/g). R12 P0-D replaced this with the actual
published Horigome+ 2025 upper limit (sigma/m < 0.2 cm^2/g for v-
independent SIDM, arXiv:2503.13650).

The legacy surrogate was a misread of the Horigome+ paper, which
actually gives a 95% CL UPPER LIMIT, not a bimodal posterior.

These tests assert:
  - The likelihood peaks at very low sigma/m (well below 0.2 cm^2/g)
    and decreases monotonically above the upper limit.
  - log L at sigma/m = 10 cm^2/g (the OLD large peak) is strongly
    negative (< -3).
  - log L at sigma/m = 0.05 cm^2/g (the OLD small peak) is finite and
    near zero (in the upper-limit mode).
  - The function still respects v-dependence: sigma/m_0 = 0.06 cm^2/g
    with a = 1 maps to sigma/m(v_DSPH) = 0.2 cm^2/g (at the limit).
"""
from __future__ import annotations
import sys
import os
from pathlib import Path

# Add the v0.3-prelim code dir AND the v0.1-prelim code dir (halo_profiles
# and sparc_loader live in v0.1-prelim/code). v0.1-prelim MUST come
# before v0.3-prelim in sys.path so that `from halo_profiles import ...`
# resolves correctly even when PYTHONPATH already includes v0.3-prelim/code.
WSL = Path("/home/lamkuenai/sidm-composite-dm-mediator")
WIN = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator")
PROJ = WSL if WSL.exists() else WIN
if not PROJ.exists():
    raise ImportError(f"Project root not found at {WSL} or {WIN}")

# Insert v0.1-prelim at position 0, then v0.3-prelim after it.
# Use insert(0, ...) to bypass any PYTHONPATH ordering.
sys.path.insert(0, str(PROJ / "v0.1-prelim/code"))
sys.path.insert(1, str(PROJ / "v0.3-prelim/code"))

import numpy as np
import channels_v03 as ch_v03
import sidm_velocity_dependent as svd
import t28_published_style_dsph as t28


class TestDsphUpperLimit:
    """R12 P0-D regression: dSph channel encodes published upper limit."""

    def test_low_sigmam_is_in_mode_region(self):
        """sigma/m_0 = 0.05 cm^2/g is well below the upper limit;
        log L should be ~ 0 (in the upper-limit mode)."""
        ll = ch_v03.loglike_dsph_v03(0.05, 0.0)
        assert ll >= -0.5, f"At well-below-limit sigma/m_0=0.05, log L = {ll}; expected near 0"

    def test_at_limit_has_moderate_penalty(self):
        """At sigma/m(v_DSPH) = 0.2 cm^2/g (the published limit),
        log L should be moderately negative (not -inf, not 0)."""
        # For a=0, sigma/m(v_DSPH) = sigma/m_0 = 0.2.
        ll = ch_v03.loglike_dsph_v03(0.2, 0.0)
        assert -5.0 < ll < 0.0, (
            f"At the upper limit (sigma/m=0.2) log L = {ll}; "
            "expected moderately negative (boundary of allowed region)"
        )

    def test_extreme_sigmam_is_disfavored(self):
        """sigma/m_0 = 10 cm^2/g is far above the upper limit;
        log L should be strongly negative (< -3)."""
        # This is the critical R12 P0-D test. The OLD bimodal surrogate
        # gave log L ~ 0 at sigma/m_0 = 10 (the "large peak").
        # The new upper-limit form has log L < -3.
        ll = ch_v03.loglike_dsph_v03(10.0, 0.0)
        assert ll < -3.0, (
            f"REGRESSION: at sigma/m_0 = 10 cm^2/g log L = {ll}; "
            "expected < -3 (the old bimodal surrogate gave ~0 here). "
            "Re-introducing the bimodal is a regression."
        )

    def test_monotonic_decrease_above_limit(self):
        """log L must decrease monotonically as sigma/m_0 increases above
        the upper limit. The OLD surrogate had a SECOND PEAK at sigma/m ~10,
        which is non-monotonic and contradicts the upper limit.
        """
        sm_grid = [0.2, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0]
        lls = [ch_v03.loglike_dsph_v03(sm, 0.0) for sm in sm_grid]
        # Check monotonic decrease.
        for i in range(1, len(lls)):
            assert lls[i] < lls[i-1], (
                f"Non-monotonic dSph log L above limit: "
                f"sm={sm_grid[i]} log L = {lls[i]} not < sm={sm_grid[i-1]} log L = {lls[i-1]}"
            )

    def test_velocity_dependence(self):
        """For a > 0 (falling sigma/m with v), sigma/m_0 = 0.06 cm^2/g
        at a = 1 gives sigma/m(v_DSPH) = 0.06 * (30/100)^(-1) = 0.2 cm^2/g,
        which is exactly at the upper limit. log L should be moderately
        negative, NOT in the mode.
        """
        # At a=1, sigma/m_0 = 0.06 maps to sigma/m(v_DSPH) = 0.2 (at limit).
        ll_at_limit = ch_v03.loglike_dsph_v03(0.06, 1.0)
        assert -5.0 < ll_at_limit < 0.0, (
            f"sigma/m_0=0.06, a=1 -> sigma/m(v_DSPH)=0.2; "
            f"log L = {ll_at_limit}; expected moderately negative"
        )
        # At a=1, sigma/m_0 = 0.03 maps to sigma/m(v_DSPH) = 0.1 (well below).
        ll_well_below = ch_v03.loglike_dsph_v03(0.03, 1.0)
        assert ll_well_below >= -0.5, (
            f"sigma/m_0=0.03, a=1 -> sigma/m(v_DSPH)=0.1 (well below limit); "
            f"log L = {ll_well_below}; expected near 0"
        )


class TestDsphPublishedStyle:
    """The legacy `loglike_dsph_published_style` was the same bimodal
    surrogate; P0-D propagated the fix here."""

    def test_t28_extreme_sigmam_is_disfavored(self):
        ll_extreme = t28.loglike_dsph_published_style(10.0, 0.0)
        assert ll_extreme < -3.0, (
            f"t28.loglike_dsph_published_style(10, 0) = {ll_extreme}; "
            "expected < -3 (the legacy bimodal surrogate gave ~0 here)"
        )


class TestDsphPublished:
    """sidm_velocity_dependent.loglike_dsph_published also had the bug."""

    def test_svd_extreme_sigmam_is_disfavored(self):
        ll_extreme = svd.loglike_dsph_published(10.0, 0.0)
        assert ll_extreme < -3.0, (
            f"svd.loglike_dsph_published(10, 0) = {ll_extreme}; "
            "expected < -3 (the legacy bimodal surrogate gave ~0 here)"
        )

    def test_svd_equals_channels_v03(self):
        """loglike_dsph_published should now DELEGATE to channels_v03."""
        for sm in [0.05, 0.2, 1.0, 10.0]:
            a = 0.5
            ll_ch = ch_v03.loglike_dsph_v03(sm, a)
            ll_svd = svd.loglike_dsph_published(sm, a)
            assert ll_ch == ll_svd, (
                f"Mismatch at sm={sm}, a={a}: ch={ll_ch}, svd={ll_svd}"
            )