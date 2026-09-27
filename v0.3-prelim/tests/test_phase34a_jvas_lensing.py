"""
Tests for Phase 34a (JVAS B1938+666 lensing test).
"""
import pytest
import sys
import os
import json


class TestPhase34a:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase34a_jvas_lensing_test.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 34a results not yet generated"
    )
    def test_results_file_valid(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "verdict" in data
        assert "our_sigma_m_at_v15_cm2_per_g" in data
        assert "required_sigma_m_at_v15_cm2_per_g" in data

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 34a results not yet generated"
    )
    def test_sigma_m_evaluated(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sm = data["our_sigma_m_at_v15_cm2_per_g"]
        assert 0 < sm < 1000, f"sigma/m(15) = {sm} — out of expected range"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 34a results not yet generated"
    )
    def test_verdict_recorded(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["verdict"] in ["JVAS_PASS", "JVAS_MARGINAL", "JVAS_FAIL"]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 34a results not yet generated"
    )
    def test_deficit_factor_reported(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        deficit = data["deficit_factor"]
        assert deficit > 0

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 34a results not yet generated"
    )
    def test_core_collapse_timescale_reported(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "core_collapse_timescale_Gyr" in data
        assert data["core_collapse_timescale_Gyr"] > 0