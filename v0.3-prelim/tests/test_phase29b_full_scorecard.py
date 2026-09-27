"""
Tests for Phase 29b (full 20+ channel scorecard at resonant median).
"""
import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase29b:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase29b_full_20_channel_scorecard.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29b results not yet generated"
    )
    def test_at_least_20_channels_evaluated(self):
        """At least 20 channels should be evaluated."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["n_total"] >= 20

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29b results not yet generated"
    )
    def test_all_channels_pass(self):
        """All channels should PASS or PASS_N/A (asymmetric DM nullifies indirect)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        n_fail = data["n_fail"]
        assert n_fail == 0, f"{n_fail} channels still FAIL"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29b results not yet generated"
    )
    def test_cloud9_in_scorecard(self):
        """Cloud-9 should be in the scorecard."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "Cloud9_RELHIC" in data["scorecard"]
        assert data["scorecard"]["Cloud9_RELHIC"]["status"] in ["PASS", "PASS_N/A"]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 29b results not yet generated"
    )
    def test_sparc_in_scorecard(self):
        """SPARC should be in the scorecard."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "SPARC" in data["scorecard"]
