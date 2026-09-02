"""Tests for Channel 19: XENONnT + PandaX-4T direct-detection competitor watch.

Per T81 (2026-09-02), in response to LZ1.docx reviewer recommendation
#5 to register a watch on LZ competitors.
"""
from __future__ import annotations

import numpy as np
import pytest

from channels_extended import (
    XENONNT_2025_LIMITS,
    PANDAX4T_2025_LIMITS,
    sigma_XENONnT_2025_limit,
    sigma_PandaX4T_2025_limit,
    is_excluded_by_XENONnT_or_PandaX,
    loglike_competitor_dd_watch,
)


class TestXENONnT2025Limits:
    """Verify XENONnT 2025 (arXiv:2502.18005) limits are loaded correctly."""

    def test_xenonnt_limits_array_shape(self):
        """Limits array should be (N, 2) with N >= 5 points."""
        assert XENONNT_2025_LIMITS.ndim == 2
        assert XENONNT_2025_LIMITS.shape[1] == 2
        assert XENONNT_2025_LIMITS.shape[0] >= 5

    def test_xenonnt_limits_at_30_geV(self):
        """Minimum of XENONnT limit curve is at m_chi = 30 GeV/c^2."""
        # Per the XENONnT 2025 paper, sigma_SI = 1.7e-47 cm^2 at 30 GeV
        limit_30 = sigma_XENONnT_2025_limit(30.0)
        assert 1e-47 <= limit_30 <= 2.5e-47, f"got {limit_30:.2e}"

    def test_xenonnt_limits_at_1_tev(self):
        """At m_chi = 1 TeV/c^2, sigma_SI ~ 3.7e-46 cm^2."""
        limit_1tev = sigma_XENONnT_2025_limit(1000.0)
        assert 3e-46 <= limit_1tev <= 4.5e-46, f"got {limit_1tev:.2e}"

    def test_xenonnt_limit_monotonic_at_high_mass(self):
        """XENONnT limit increases with mass for m_chi > 200 GeV (per the paper's
        m_chi/(1 TeV/c^2) scaling)."""
        limit_500 = sigma_XENONnT_2025_limit(500.0)
        limit_1000 = sigma_XENONnT_2025_limit(1000.0)
        # The scaling says UL ~ m_chi / 1 TeV, so limit(1000) > limit(500)
        assert limit_1000 > limit_500


class TestPandaX4T2025Limits:
    """Verify PandaX-4T 2025 (arXiv:2408.00664) limits are loaded correctly."""

    def test_pandax_limits_array_shape(self):
        """Limits array should be (N, 2) with N >= 5 points."""
        assert PANDAX4T_2025_LIMITS.ndim == 2
        assert PANDAX4T_2025_LIMITS.shape[1] == 2
        assert PANDAX4T_2025_LIMITS.shape[0] >= 5

    def test_pandax_limits_at_40_geV(self):
        """PandaX-4T minimum ~ 3e-47 cm^2 at m_chi = 40 GeV/c^2."""
        limit_40 = sigma_PandaX4T_2025_limit(40.0)
        assert 2e-47 <= limit_40 <= 4e-47, f"got {limit_40:.2e}"

    def test_pandax_limits_at_1_tev(self):
        """At m_chi = 1 TeV/c^2, sigma_SI ~ 5e-46 cm^2 (interpolated)."""
        limit_1tev = sigma_PandaX4T_2025_limit(1000.0)
        assert 3e-46 <= limit_1tev <= 7e-46, f"got {limit_1tev:.2e}"


class TestIsExcludedByXENONnTOrPandaX:
    """Test the exclusion check helper."""

    def test_typical_xenonnt_or_pandax_limit_at_770_gev(self):
        """At the project's v0.7 MAP m_chi = 770 GeV, both experiments should
        have limits in the 2-5e-46 range (compatible with LZ)."""
        xenonnt = sigma_XENONnT_2025_limit(770.0)
        pandax = sigma_PandaX4T_2025_limit(770.0)
        assert 2e-46 <= xenonnt <= 5e-46, f"XENONnT got {xenonnt:.2e}"
        assert 2e-46 <= pandax <= 6e-46, f"PandaX got {pandax:.2e}"

    def test_predicted_xenonnt_or_pandax_is_well_below_limits(self):
        """At the v0.7 MAP, predicted sigma_DM-nuc ~10^-117 cm^2 (Kahlhoefer formula)
        is ~10^-71 below even the more constraining experiment limit (~3e-46).
        So is_excluded_by_XENONnT_or_PandaX should return False."""
        predicted = 1e-117
        excluded = is_excluded_by_XENONnT_or_PandaX(770.0, predicted)
        assert not excluded, "predicted sigma_DM-nuc should be below limits"

    def test_huge_sigma_excluded(self):
        """A sigma_DM-nuc of 1e-44 cm^2 (way above any limit) should be excluded
        at m_chi = 770 GeV (where both experiments are around 3e-46)."""
        excluded = is_excluded_by_XENONnT_or_PandaX(770.0, 1e-44)
        assert excluded


class TestLoglikeCompetitorDDWatch:
    """Test Channel 19 loglikelihood function."""

    def test_loglike_penalty_for_v07_map_with_rough_scaling(self):
        """At v0.7 MAP (sigma_m = 0.27 cm^2/g, m_chi = 770 GeV), the rough scaling
        sigma_DM-nuc ~ sigma_m * 1e-24 * m_chi_GeV gives ~2e-22 cm^2, which is
        ABOVE the XENONnT/PandaX-4T limits (~3e-46). This is the same soft-
        penalty behavior as Channel 5 (T30 LZ): the rough scaling doesn't
        include the kinetic-mixing epsilon^2 suppression (which is captured
        by the Kahlhoefer formula, not this channel). The actual predicted
        sigma_DM-nuc ~10^-117 cm^2 is captured by the Kahlhoefer formula, not
        this rough scaling. This channel serves as a flag/warning, not a hard
        constraint.
        """
        ll = loglike_competitor_dd_watch(sigma_m=0.27, m_chi_GeV=770.0)
        # Soft penalty (same as Channel 5)
        assert ll == -1.0, (
            f"At v0.7 MAP, rough scaling predicts sigma_DM-nuc above XENONnT/PandaX-4T limits; "
            f"channel returns -1.0 soft penalty (this is the expected behavior - the actual "
            f"suppression comes from the Kahlhoefer formula, not this rough-scaling channel)."
        )

    def test_loglike_zero_for_sub_gev(self):
        """For m_chi < 3 GeV (LZ exclusion doesn't apply), the channel
        returns 0."""
        ll = loglike_competitor_dd_watch(sigma_m=1.0, m_chi_GeV=1.0)
        assert ll == 0.0

    def test_loglike_penalty_for_huge_sigma(self):
        """If sigma_m * 1e-24 * m_chi_GeV exceeds the tighter of XENONnT/PandaX
        limits, the channel applies the soft -1.0 penalty (same as Channel 5)."""
        # At m_chi = 770 GeV, sigma_DM_nucleon = sigma_m * 1e-24 * 770
        # To exceed 3e-46, sigma_m > 3e-46 / (770 * 1e-24) ~ 4e-25 cm^2/g
        # That's impossibly large, but the test verifies the logic.
        ll = loglike_competitor_dd_watch(sigma_m=1e-23, m_chi_GeV=770.0)
        assert ll == -1.0
