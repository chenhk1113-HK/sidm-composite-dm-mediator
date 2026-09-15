"""
Tests for Phase 32b (multi-resonant joint fit).
"""
import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase32b:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase32b_multi_resonant_joint_fit.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32b results not yet generated"
    )
    def test_results_file_valid(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "best_sample" in data
        assert "posterior_summary" in data
        assert data["max_loglike"] > -5.0  # reasonable fit

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32b results not yet generated"
    )
    def test_m_chi_in_expected_range(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        m_chi = data["best_sample"]["m_chi_GeV"]
        assert 3.0 < m_chi < 15.0  # within prior

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32b results not yet generated"
    )
    def test_cloud9_velocity_in_range(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        v_C9 = data["best_sample"]["v_targets_kms"][0]
        assert 15.0 < v_C9 < 35.0  # within Cloud-9 prior

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 32b results not yet generated"
    )
    def test_all_resonances_present(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        v_targets = data["best_sample"]["v_targets_kms"]
        assert len(v_targets) == 4  # Cloud-9, SPARC, Stream, Cluster