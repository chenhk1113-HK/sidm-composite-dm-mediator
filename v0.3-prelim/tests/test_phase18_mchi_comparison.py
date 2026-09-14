"""
Tests for Phase 18 m_chi comparison.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from phase18_mchi_comparison import loglike_mchi


class TestLoglikeStability:
    def test_loglike_finite_at_phase8d_map(self):
        """Phase 8d MAP should give finite loglike at all m_chi values."""
        theta = [-1.18, -0.56, -8.28, -0.91, -1.46]
        for m_chi in [5, 10, 45]:
            ll = loglike_mchi(theta, m_chi_GeV=m_chi)
            assert np.isfinite(ll), f"Loglike not finite for m_chi={m_chi}"

    def test_loglike_outside_prior_returns_neg_inf(self):
        bad_theta = [-10, 1.0, -100, -10, -10]
        for m_chi in [5, 10, 45]:
            ll = loglike_mchi(bad_theta, m_chi_GeV=m_chi)
            assert ll == -np.inf


class TestResultsConsistency:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase18_mchi_comparison.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 18 results not yet generated"
    )
    def test_sigma_m_invariant_across_mchi(self):
        """σ/m MAP should be approximately equal across m_chi values."""
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
        reason="Phase 18 results not yet generated"
    )
    def test_asymmetric_dm_natural_at_5GeV(self):
        """η/η_B at m_chi=5 should be ~1 (natural 1:1 transfer)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        eta_5 = data["results"]["5"]["eta_DM_over_eta_B"]
        assert 0.5 < eta_5 < 2.0, f"η/η_B at 5 GeV = {eta_5}, expected ~1"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 18 results not yet generated"
    )
    def test_tau_core_consistent_across_mchi(self):
        """τ_core should be ~15-20 Gyr at all m_chi (since σ/m is invariant)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        for label, r in data["results"].items():
            tau = r["tau_core_Gyr"]
            assert 5 < tau < 30, f"τ[{label}] = {tau} Gyr, expected 5-30"
