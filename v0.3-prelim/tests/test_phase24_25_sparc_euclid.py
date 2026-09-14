"""
Tests for Phase 24 (multi-portal SPARC) and Phase 25 (Euclid subhalo).
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase24:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase24_multi_portal_sparc.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 24 results not yet generated"
    )
    def test_sparc_preference_recorded(self):
        """SPARC's preferred sigma/m(100) should be recorded."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "sparc_best" in data
        assert data["sparc_best"]["sigma_m_100"] > 0

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 24 results not yet generated"
    )
    def test_sparc_tension_quantified(self):
        """Delta loglike between T90.45 and SPARC max should be computed."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "delta_loglike_vs_sparc_max" in data
        # Honest negative expected — T90.45 has sigma/m(100) much higher than SPARC prefers
        assert data["delta_loglike_vs_sparc_max"] < 0, "Expected negative delta (T90.45 worse than SPARC max)"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 24 results not yet generated"
    )
    def test_verdict_recorded(self):
        """Verdict should be one of the recognized categories."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["verdict"] in ["PASSES_SPARC", "MILD_TENSION", "STRONG_TENSION", "FAILS_SPARC"]


class TestPhase25:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase25_euclid_subhalo_multi_portal.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 25 results not yet generated"
    )
    def test_scan_executed(self):
        """Scan should have tested some combinations."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["scan_n_tested"] > 100, f"Only {data['scan_n_tested']} tested"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 25 results not yet generated"
    )
    def test_current_loglike_recorded(self):
        """Current Euclid subhalo loglike at T90.45 median should be recorded."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "current_ll_euclid" in data
        assert data["current_ll_euclid"] < -5, f"Expected negative loglike, got {data['current_ll_euclid']}"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 25 results not yet generated"
    )
    def test_verdict_recorded(self):
        """Verdict should be FOUND_CONFIGURATION or NO_CONFIGURATION_FOUND."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["verdict"] in ["FOUND_CONFIGURATION", "NO_CONFIGURATION_FOUND"]
