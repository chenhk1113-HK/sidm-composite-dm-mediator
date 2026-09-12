"""Test class for Channel 27 (NGC 1052 linear-trail velocity-scale constraint)."""
from __future__ import annotations
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v0.3-prelim" / "code"))

from ch27_ngc1052_trail_channel import (
    COLLISION_VELOCITY_KMS,
    TIME_SINCE_COLLISION_GYR,
    SURVIVING_HALO_MASS_MSUN,
    NGC1052_TRAIL_LOG_SM_PEAK,
    NGC1052_TRAIL_LOG_SM_WIDTH,
    loglike_ngc1052_trail,
    ngc1052_trail_summary,
)


class TestNgc1052TrailChannel:
    """Channel 27: NGC 1052 linear-trail velocity-scale constraint.

    Verifies:
    - Constants match published observables (arXiv:2205.08552).
    - Channel returns finite values across the prior range.
    - Channel is near-neutral at the v0.3-prelim MAP (sigma/m_0 ~ 0.78, a ~ 0.5).
    - Channel penalizes extreme sigma/m values.
    - v-dependence is correctly applied via log10(V_REF/v) = log10(100/358).
    """

    def test_constants_match_published_observables(self):
        """Collision velocity (358 km/s) and time-since-collision (8 Gyr)
        match van Dokkum+ 2022 (arXiv:2205.08552) Figure 1 caption."""
        assert COLLISION_VELOCITY_KMS == pytest.approx(358.0, abs=1.0)
        assert TIME_SINCE_COLLISION_GYR == pytest.approx(8.0, abs=1.0)
        assert math.isfinite(SURVIVING_HALO_MASS_MSUN)
        assert SURVIVING_HALO_MASS_MSUN > 0

    def test_at_amuse_peak_is_near_neutral(self):
        """At the AMUSE-derived anchor (sigma/m_0 ~ 3.07 cm^2/g, a ~ 0.0),
        the channel should be near-zero (model-consistent with simulation).
        With velocity-dependence, the anchor at v=358 km/s is sigma/m(v) = sigma/m_0.
        """
        result = loglike_ngc1052_trail(sigma_m_0=3.07, a=0.0)
        # The peak is anchored to this value, so log L should be near zero
        assert math.isfinite(result)
        assert result >= -0.1, f"AMUSE-anchor penalty too strong: {result}"

    def test_at_v0p3_prelim_map_is_now_penalized(self):
        """At the v0.3-prelim MAP (sigma/m_0 ~ 0.78, a ~ 0.5), the channel
        is now penalized because the AMUSE-derived peak (3.07 cm^2/g at v=358)
        is ~0.87 dex above this MAP's implied sigma/m(v=358) ~ 0.41 cm^2/g.
        Old placeholder peak (0.5) gave near-neutral; new peak (3.07) penalizes.
        Penalty = -0.5 * (0.87)^2 ~ -0.38
        """
        result = loglike_ngc1052_trail(sigma_m_0=0.78, a=0.5)
        assert math.isfinite(result)
        assert result < -0.3, f"v0.3-prelim MAP not penalized enough by new peak: {result}"
        assert result > -0.5, f"v0.3-prelim MAP penalized too strongly: {result}"

    def test_at_extreme_high_sigma_m_penalizes(self):
        """sigma/m_0 = 100, a = -1 should be strongly penalized.
        With new peak=3.07 cm^2/g: sigma/m(v=358) ~ 358 cm^2/g, ~2.05 dex above peak.
        Penalty = -0.5 * (2.05)^2 ~ -2.10
        """
        result = loglike_ngc1052_trail(sigma_m_0=100.0, a=-1.0)
        assert math.isfinite(result)
        assert result < -2.0, f"Extreme high sigma/m not penalized enough: {result}"

    def test_at_extreme_low_sigma_m_penalizes(self):
        """sigma/m_0 = 0.1, a = 1.5 gives sigma/m(v=358) ~ 0.015 cm^2/g,
        ~1.5 dex below peak — should be penalized."""
        result = loglike_ngc1052_trail(sigma_m_0=0.1, a=1.5)
        assert math.isfinite(result)
        assert result < -1.0, f"Extreme low sigma/m not penalized enough: {result}"

    def test_negative_sigma_m_returns_neg_inf(self):
        """Defensive: negative or zero sigma/m_0 returns -inf."""
        assert loglike_ngc1052_trail(sigma_m_0=-1.0, a=0.5) == -np.inf
        assert loglike_ngc1052_trail(sigma_m_0=0.0, a=0.5) == -np.inf

    def test_nan_inf_input_returns_neg_inf(self):
        """Defensive: NaN/inf inputs return -inf."""
        assert loglike_ngc1052_trail(sigma_m_0=np.nan, a=0.5) == -np.inf
        assert loglike_ngc1052_trail(sigma_m_0=1.0, a=np.nan) == -np.inf
        assert loglike_ngc1052_trail(sigma_m_0=np.inf, a=0.5) == -np.inf

    def test_include_in_fit_false_returns_zero(self):
        """Ablation knob: include_in_fit=False returns 0 (channel disabled)."""
        assert loglike_ngc1052_trail(sigma_m_0=0.78, a=0.5, include_in_fit=False) == 0.0

    def test_v_dependence_via_a(self):
        """Velocity-dependence test: at fixed sigma/m_0, changing a should
        change the implied sigma/m(v=358) and hence the log L.

        For a > 0 (sigma/m DECREASES with v), sigma/m(358) < sigma/m_0.
        For a < 0 (sigma/m INCREASES with v), sigma/m(358) > sigma/m_0.
        """
        ll_a0 = loglike_ngc1052_trail(sigma_m_0=1.0, a=0.0)
        ll_ap1 = loglike_ngc1052_trail(sigma_m_0=1.0, a=1.0)
        ll_an1 = loglike_ngc1052_trail(sigma_m_0=1.0, a=-1.0)
        # All finite
        for r in (ll_a0, ll_ap1, ll_an1):
            assert math.isfinite(r)
        # Direction check: positive a -> lower sigma/m at v=358 -> different log L
        assert ll_ap1 != ll_a0, "Velocity-dependence not applied"

    def test_summary_returns_expected_keys(self):
        """Diagnostic helper returns all expected keys."""
        s = ngc1052_trail_summary(0.78, 0.5)
        for key in ("log_sigma_m_0", "a", "log_sm_at_collision_velocity",
                    "sm_at_collision_velocity_cm2_per_g", "log_L"):
            assert key in s
        # Numerical sanity
        assert s["log_sigma_m_0"] == pytest.approx(np.log10(0.78), abs=1e-6)
        # log10(100/358) ~ -0.554
        expected_log_sm_v = np.log10(0.78) + 0.5 * np.log10(100.0/358.0)
        assert s["log_sm_at_collision_velocity"] == pytest.approx(expected_log_sm_v, abs=1e-6)

    def test_finite_across_prior_range(self):
        """Channel should be finite across a representative prior sweep."""
        for sm0 in [0.01, 0.1, 1.0, 10.0, 100.0]:
            for a in [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
                result = loglike_ngc1052_trail(sigma_m_0=sm0, a=a)
                assert math.isfinite(result), (
                    f"Non-finite log L at sigma/m_0={sm0}, a={a}: {result}"
                )
