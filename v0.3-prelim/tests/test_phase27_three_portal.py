"""
Tests for Phase 27 (three-portal diagnostic).
"""
import pytest
import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase27:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase27_three_portal_diagnostic.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 27 results not yet generated"
    )
    def test_scan_executed(self):
        """Scan should have tested Portal C configurations."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["scan"]["n_tested"] > 50

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 27 results not yet generated"
    )
    def test_baseline_recorded(self):
        """Baseline 2-portal sigma/m values should be recorded."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        baseline = data["baseline_2portal"]
        assert baseline["sigma_m_28"] > 30  # Cloud-9 OK
        assert baseline["sigma_m_100"] > 1   # SPARC conflict
        assert baseline["sigma_m_150"] > 1   # Euclid conflict

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 27 results not yet generated"
    )
    def test_yukawa_positive_limitation_documented(self):
        """The honest finding that additive portals can't reduce sigma/m should be recorded."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        # Either the scan found NO reduction (verdict), OR verdict documents the issue
        assert "verdict" in data
        assert "HONEST" in data["honest_physics_note"].upper() or "always" in data["honest_physics_note"]
