"""
Tests for Phase 31a (3 critical review tests: C, H, I).
"""
import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase31aC:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase31a_C_subhalo_real_data.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31a-C results not yet generated"
    )
    def test_subhalo_verdict_recorded(self):
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "verdict" in data
        assert data["verdict"] in ["CONSISTENT_WITH_DATA", "MILD_TENSION", "EXCLUDED_BY_DATA"]


class TestPhase31aH:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase31a_H_core_size.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31a-H results not yet generated"
    )
    def test_core_size_halos_evaluated(self):
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert len(data["halo_predictions"]) >= 3

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31a-H results not yet generated"
    )
    def test_aggregate_verdict_recorded(self):
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["aggregate"] in [
            "CONSISTENT_WITH_OBS", "MILD_OVERSHOOT", "OVERSHOOTS_DWARF_CORES"
        ]


class TestPhase31aI:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase31a_I_direct_detection.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31a-I results not yet generated"
    )
    def test_dd_verdict_recorded(self):
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["verdict"] in ["EVADES_DD_LIMITS", "EXCLUDED_BY_DD"]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 31a-I results not yet generated"
    )
    def test_lz_limit_recorded(self):
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["lz_limit_cm2"] > 0