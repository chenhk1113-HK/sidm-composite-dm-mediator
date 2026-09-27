"""
Tests for Phase 21 T90.45 multi-portal space-conditions test.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestResultsConsistency:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase21_t90_45_multi_portal.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 21 results not yet generated"
    )
    def test_both_modes_evaluable(self):
        """Both MAP and median modes should be evaluable."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "map_results" in data
        assert "median_results" in data
        assert len(data["map_results"]) >= 15
        assert len(data["median_results"]) >= 15

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 21 results not yet generated"
    )
    def test_median_achieves_high_sigma_m_at_low_v(self):
        """Median (Cloud-9 mode) should have σ/m(28) ≥ 30."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sm28_median = data["median_params"]["sigma_m_28"]
        assert sm28_median >= 30, f"σ/m(28) median = {sm28_median}, expected ≥ 30 (Cloud-9)"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 21 results not yet generated"
    )
    def test_map_has_low_sigma_m_at_low_v(self):
        """MAP (non-Cloud-9 mode) should have σ/m(28) < 30."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sm28_map = data["map_params"]["sigma_m_28"]
        assert sm28_map < 30, f"σ/m(28) MAP = {sm28_map}, expected < 30"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 21 results not yet generated"
    )
    def test_bimodality_visible(self):
        """The two modes should give DIFFERENT σ/m(28)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        sm28_map = data["map_params"]["sigma_m_28"]
        sm28_median = data["median_params"]["sigma_m_28"]
        # Median should be much higher than MAP (Cloud-9 mode)
        assert sm28_median > 5 * sm28_map, f"Ratio = {sm28_median/sm28_map}, expected > 5"