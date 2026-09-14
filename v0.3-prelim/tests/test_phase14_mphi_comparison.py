"""
Tests for Phase 14 m_phi comparison.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from phase14_mphi_comparison import loglike_mphi


class TestLoglikeStability:
    """σ/m should NOT depend strongly on m_phi choice."""

    def test_loglike_finite_at_phase8d_map(self):
        """Phase 8d MAP should give finite loglike at all m_phi values."""
        theta = [-1.18, -0.56, -8.28, -0.91, -1.46]
        for m_phi in [100, 150, 200, 500]:
            ll = loglike_mphi(theta, m_phi_MeV=m_phi)
            assert np.isfinite(ll), f"Loglike not finite for m_phi={m_phi}"

    def test_loglike_outside_prior_returns_neg_inf(self):
        """Out-of-prior theta → -inf."""
        bad_theta = [-10, 1.0, -100, -10, -10]
        for m_phi in [100, 200, 500]:
            ll = loglike_mphi(bad_theta, m_phi_MeV=m_phi)
            assert ll == -np.inf


class TestResultsConsistency:
    """Validate saved Phase 14 JSON."""

    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase14_mphi_comparison.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 14 results not yet generated"
    )
    def test_sigma_m_invariant_across_mphi(self):
        """σ/m MAP should be approximately equal across m_phi values."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sms = [data["results"][k]["MAP_sigma_m"] for k in data["results"]]
        sm_mean = np.mean(sms)
        for i, sm in enumerate(sms):
            assert abs(sm - sm_mean) / sm_mean < 0.2, \
                f"σ/m[{i}] = {sm}, mean = {sm_mean}, spread > 20%"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 14 results not yet generated"
    )
    def test_g_D_around_fermi_limit(self):
        """g_D should be ~0.14 (Fermi limit) for all m_phi values."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        for label, r in data["results"].items():
            g_D = r["MAP_g_D"]
            assert 0.10 < g_D < 0.20, \
                f"g_D[{label}] = {g_D} outside Fermi-constrained range"
