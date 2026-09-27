"""
Tests for Phase 13 mediator mass survey.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestClassification:
    """Validate the SIDM-channel vs DD-channel classification."""

    def test_below_100_meV_is_sidm(self):
        from phase13_mediator_mass_survey import classify_channel
        assert classify_channel({"m_phi_MeV": 50}) == "SIDM-channel"
        assert classify_channel({"m_phi_MeV": 30}) == "SIDM-channel"
        assert classify_channel({"m_phi_MeV": 10}) == "SIDM-channel"

    def test_above_100_meV_is_dd(self):
        from phase13_mediator_mass_survey import classify_channel
        assert classify_channel({"m_phi_MeV": 200}) == "DD-channel"
        assert classify_channel({"m_phi_MeV": 500}) == "DD-channel"

    def test_boundary_at_100_meV(self):
        """Boundary at 100 MeV: classify as DD-channel."""
        from phase13_mediator_mass_survey import classify_channel
        # 100 is borderline; convention here is DD-channel (>=100)
        assert classify_channel({"m_phi_MeV": 100}) == "DD-channel"


class TestResultsConsistency:
    """Validate the saved Phase 13 JSON."""

    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase13_mediator_mass_survey.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 13 results not yet generated"
    )
    def test_bimodality_strong(self):
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        gap = data["statistics"]["log10_gap_dex"]
        assert gap > 1.0, f"Bimodality gap too small: {gap}"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 13 results not yet generated"
    )
    def test_sidm_count_dominant(self):
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        n_sidm = data["statistics"]["n_sidm_channel"]
        n_dd = data["statistics"]["n_dd_channel"]
        assert n_sidm > n_dd, "SIDM-channel should dominate the literature"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 13 results not yet generated"
    )
    def test_mediator_medians_in_range(self):
        """SIDM median should be 1-30 MeV; DD median should be 100-500 MeV."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sidm_med = data["statistics"]["sidm_mphi_median_MeV"]
        dd_med = data["statistics"]["dd_mphi_median_MeV"]
        assert 1 < sidm_med < 50, f"SIDM median out of range: {sidm_med}"
        assert 100 <= dd_med <= 500, f"DD median out of range: {dd_med}"
