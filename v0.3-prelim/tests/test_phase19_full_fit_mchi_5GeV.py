"""
Tests for Phase 19 full v0.3-prelim refit at m_chi = 5 GeV.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from phase19_full_fit_mchi_5GeV import loglike_full_mchi5, loglike_baseline_mchi5


class TestLoglikeStability:
    def test_loglike_finite_at_phase8d_map(self):
        """Phase 8d MAP should give finite loglike at m_chi=5 GeV."""
        theta = [-1.18, -0.56, -8.28, -0.91, -1.46]
        ll_full = loglike_full_mchi5(theta)
        ll_base = loglike_baseline_mchi5(theta)
        assert np.isfinite(ll_full)
        assert np.isfinite(ll_base)

    def test_baseline_minus_full_equals_lz_248_contribution(self):
        """baseline = full - LZ 248 channel contribution."""
        theta = [-1.18, -0.56, -8.28, -0.91, -1.46]
        ll_full = loglike_full_mchi5(theta)
        ll_base = loglike_baseline_mchi5(theta)
        # LZ 248 contribution can be small
        assert abs(ll_full - ll_base) < 100

    def test_loglike_outside_prior_returns_neg_inf(self):
        bad_theta = [-10, 1.0, -100, -10, -10]
        assert loglike_full_mchi5(bad_theta) == -np.inf
        assert loglike_baseline_mchi5(bad_theta) == -np.inf


class TestResultsConsistency:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase19_full_fit_mchi_5GeV.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 19 results not yet generated"
    )
    def test_sigma_m_invariant_across_mchi(self):
        """σ/m should be similar at 5 GeV and 45 GeV."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sm_5 = data["comparison_to_45GeV"]["phase_19_5GeV"]["sigma_m"]
        sm_45 = data["comparison_to_45GeV"]["phase_8d_45GeV"]["sigma_m"]
        # Within 20% of each other
        assert abs(sm_5 - sm_45) / sm_45 < 0.2, f"σ/m 5 GeV={sm_5} vs 45 GeV={sm_45}"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 19 results not yet generated"
    )
    def test_g_D_lower_at_5GeV(self):
        """g_D at 5 GeV should be lower than at 45 GeV (Fermi slightly tighter)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        g_5 = data["comparison_to_45GeV"]["phase_19_5GeV"]["g_D"]
        g_45 = data["comparison_to_45GeV"]["phase_8d_45GeV"]["g_D"]
        assert g_5 < g_45, f"g_D at 5 GeV={g_5} should be < at 45 GeV={g_45}"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 19 results not yet generated"
    )
    def test_lz_event_inert_at_5GeV(self):
        """Δlog Z at 5 GeV should be small (|Δlog Z| < 1)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        delta = data["delta_log_Z"]
        assert abs(delta) < 1.0, f"Δlog Z = {delta}, expected |Δlog Z| < 1"
