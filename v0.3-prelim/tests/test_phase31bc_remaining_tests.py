"""
Tests for Phase 31b and 31c (UV completion + stream gaps).
"""
import pytest
import os
import json

sys = __import__("sys")


class TestPhase31bE:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase31b_E_uv_completion.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31b results not yet generated"
    )
    def test_uv_aggregate_recorded(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["aggregate_verdict"] in [
            "NO_KNOWN_UV", "ONE_KNOWN_UV", "MULTIPLE_UV"
        ]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31b results not yet generated"
    )
    def test_scenarios_evaluated(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert len(data["scenarios"]) == 4  # 4 UV scenarios tested


class TestPhase31cG:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase31c_G_stream_gaps.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31c results not yet generated"
    )
    def test_stream_gap_verdict_recorded(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["verdict"] in [
            "TOO_FEW_GAPS", "FEWER_GAPS_THAN_OBSERVED",
            "TOO_MANY_GAPS", "CONSISTENT_WITH_STREAMS"
        ]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31c results not yet generated"
    )
    def test_stream_velocities_evaluated(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert len(data["gap_predictions"]) >= 3

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31c results not yet generated"
    )
    def test_gap_density_low(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        # The model's gap density should be lower than observed (0.2-0.5)
        assert data["avg_gap_density"] < 0.2