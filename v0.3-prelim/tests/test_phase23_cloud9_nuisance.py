"""
Tests for Phase 23 Cloud-9 nuisance marginalization + multi-portal wrapper.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase23:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase23_cloud9_nuisance_marginalization.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 23 results not yet generated"
    )
    def test_sigma_m_in_cloud9_range(self):
        """T90.45 median sigma/m(28) should be in Cloud-9 [30, 500] cm²/g range."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sm28 = data["sigma_m_at_v200"]
        assert 30 <= sm28 <= 500, f"σ/m(28) = {sm28}, expected in [30, 500]"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 23 results not yet generated"
    )
    def test_marginalization_at_least_neutral(self):
        """Marginalization should not HURT the loglike."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        delta = data["delta_loglike_marginalization_gain"]
        assert delta >= -0.5, f"Marginalization gain = {delta}, expected ≥ -0.5"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 23 results not yet generated"
    )
    def test_verdict_field(self):
        """Verdict should be one of the recognized categories."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        verdict = data["verdict"]
        assert verdict in ["PASS_AFTER_MARGINALIZATION", "IMPROVED_VIA_MARGINALIZATION",
                           "SLIGHT_IMPROVEMENT", "NO_HELP"]


class TestMultiPortalWrapper:
    """Test the new t90_v45_cloud9_multi_portal wrapper."""

    def test_multi_portal_wrapper_compiles(self):
        """The multi-portal wrapper should import cleanly."""
        from t90_v45_cloud9_multi_portal import loglike_relhic_multi_portal, loglike_relhic_multi_portal_9d
        assert callable(loglike_relhic_multi_portal)
        assert callable(loglike_relhic_multi_portal_9d)

    def test_multi_portal_wrapper_passes_for_T90_45_median(self):
        """T90.45 median should pass Cloud-9 via the multi-portal wrapper."""
        from t90_v45_cloud9_multi_portal import loglike_relhic_multi_portal
        # T90.45 median params
        ll = loglike_relhic_multi_portal(
            m_phi_A_MeV=366, m_chi_A_GeV=41, g_chi_A=1.19,
            m_phi_B_MeV=20.5, m_chi_B_GeV=302, g_chi_B=0.276,
        )
        # Multi-portal sum should be much better than single-portal Portal A
        assert ll > -2.0, f"Multi-portal Cloud-9 loglike = {ll}, expected > -2"

    def test_multi_portal_wrapper_different_from_portal_a_alone(self):
        """Multi-portal should give different (better) result than Portal A alone."""
        from t90_v45_cloud9_multi_portal import loglike_relhic_multi_portal
        from t90_v29_relhic_yukawa import loglike_relhic_v29_yukawa
        # Portal A only
        ll_A = loglike_relhic_v29_yukawa(366, 41, 1.19)
        # Both portals
        ll_both = loglike_relhic_multi_portal(
            m_phi_A_MeV=366, m_chi_A_GeV=41, g_chi_A=1.19,
            m_phi_B_MeV=20.5, m_chi_B_GeV=302, g_chi_B=0.276,
        )
        # Multi-portal should be better (less negative)
        assert ll_both > ll_A, f"Multi-portal {ll_both} not better than Portal A {ll_A}"
