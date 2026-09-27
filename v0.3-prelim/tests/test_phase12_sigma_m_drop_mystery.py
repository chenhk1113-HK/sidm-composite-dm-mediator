"""
Tests for Phase 12 σ/m drop mystery investigation.

Key finding: σ/m = 0.065 in ALL three LZ 248 keV modes (on/off/null).
The drop is NOT caused by the LZ event — it's intrinsic to the
Majorana reframe framework.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from phase12_sigma_m_drop_mystery import (
    loglike_sigma_m_drop_investigation, prior_transform_5d,
)


class TestSigmaMIsInvariant:
    """σ/m MAP should be invariant across LZ 248 keV modes."""

    def test_loglike_finite_at_typical_point(self):
        """Loglike at typical Majorana reframe point should be finite."""
        # Phase 8d MAP
        theta = [-1.18, -0.56, -8.28, -0.91, -1.46]
        for mode in ["on", "off", "null"]:
            ll = loglike_sigma_m_drop_investigation(theta, lz_248_mode=mode)
            assert np.isfinite(ll), f"Loglike not finite for mode={mode}"

    def test_loglike_outside_prior_returns_neg_inf(self):
        """Out-of-prior theta → -inf."""
        bad_theta = [-10, 1.0, -100, -10, -10]
        for mode in ["on", "off", "null"]:
            ll = loglike_sigma_m_drop_investigation(bad_theta, lz_248_mode=mode)
            assert ll == -np.inf

    def test_three_modes_give_similar_loglike(self):
        """At the MAP, three modes should give similar loglike (channel is small)."""
        theta = [-1.18, -0.56, -8.28, -0.91, -1.46]
        ll_on = loglike_sigma_m_drop_investigation(theta, lz_248_mode="on")
        ll_off = loglike_sigma_m_drop_investigation(theta, lz_248_mode="off")
        ll_null = loglike_sigma_m_drop_investigation(theta, lz_248_mode="null")
        # LZ 248 keV channel contribution is bounded
        assert abs(ll_on - ll_off) < 50, \
            f"Channel contribution too large: |on - off| = {abs(ll_on - ll_off):.1f}"
        assert abs(ll_on - ll_null) < 50, \
            f"Channel contribution too large: |on - null| = {abs(ll_on - ll_null):.1f}"


class TestResultsConsistency:
    """Validate the saved Phase 12 JSON results."""

    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase12_sigma_m_drop_mystery.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 12 results not yet generated"
    )
    def test_sigma_m_invariant_across_modes(self):
        """σ/m MAP should be approximately equal across the three modes."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sm_on = data["results"]["on"]["MAP_sigma_m"]
        sm_off = data["results"]["off"]["MAP_sigma_m"]
        sm_null = data["results"]["null"]["MAP_sigma_m"]
        # All within 5% of each other
        sm_mean = (sm_on + sm_off + sm_null) / 3.0
        for label, sm in [("on", sm_on), ("off", sm_off), ("null", sm_null)]:
            assert abs(sm - sm_mean) / sm_mean < 0.05, \
                f"σ/m mode={label} = {sm}, mean = {sm_mean}, spread > 5%"
