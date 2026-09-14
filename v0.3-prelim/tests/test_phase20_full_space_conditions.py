"""
Tests for Phase 20 full space-conditions test.
"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestResultsConsistency:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase20_full_space_conditions.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 20 results not yet generated"
    )
    def test_all_channels_evaluable(self):
        """All 20 channels should be evaluable at the v0.3-prelim MAP."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["n_fail"] == 0, f"{data['n_fail']} channels failed"
        assert data["n_channels"] >= 18, f"Only {data['n_channels']} channels tested"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 20 results not yet generated"
    )
    def test_ksfr_pcac_flagged(self):
        """KSFR/PCAC is a hard validity check; should be -inf or very negative."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        ksfr = data["channels"].get("ksfr_pcac", {})
        ll = ksfr.get("loglike", 0.0)
        # Should be -inf or very negative
        assert ll < -10, f"KSFR/PCAC loglike = {ll}, expected << 0"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 20 results not yet generated"
    )
    def test_indirect_detection_channels_recorded(self):
        """XRISM, DAMPE, eROSITA channels should be recorded."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        chs = data["channels"]
        assert "xrism_perseus" in chs
        assert "dampe_cre" in chs
        assert "erosita" in chs
