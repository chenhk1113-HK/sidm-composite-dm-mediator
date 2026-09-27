"""
Tests for Phase 28 (resonant Portal B diagnostic).
"""
import pytest
import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase28:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase28_resonant_portal_b.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 28 results not yet generated"
    )
    def test_scan_executed(self):
        """Scan should have tested E_R x Gamma_R combinations."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["scan"]["n_tested"] > 20

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 28 results not yet generated"
    )
    def test_resonance_kinetic_energy_recorded(self):
        """The kinetic energy at Cloud-9 velocity should be recorded."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        E_CM = data["baseline"]["E_CM_at_v28_eV"]
        # For m_chi=30 GeV, v=28 km/s: E_CM ~ 65 eV
        assert 50 < E_CM < 100, f"E_CM = {E_CM}, expected ~65 eV"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 28 results not yet generated"
    )
    def test_verdict_recorded(self):
        """Verdict should be FOUND_CONFIGURATIONS or NO_CONFIGURATION_FOUND."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["verdict"] in ["FOUND_CONFIGURATIONS", "NO_CONFIGURATION_FOUND"]
