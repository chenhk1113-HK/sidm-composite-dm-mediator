"""
Tests for Phase 30 (critical review response).
"""
import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))


class TestPhase30:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase30_critical_review_response.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 30 results not yet generated"
    )
    def test_fine_tuning_natural(self):
        """Test D: Resonance should NOT be extremely fine-tuned."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        d = data["results"]["D_fine_tuning"]
        assert d["naturalness"] in ["NATURAL", "MILDLY_TUNED"]
        assert d["max_sensitivity"] < 100  # Not extremely fine-tuned

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 30 results not yet generated"
    )
    def test_relic_density_reasonable(self):
        """Test F: Asymmetric DM eta/eta_B should be O(1)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        f_test = data["results"]["F_relic_density"]
        assert f_test["verdict"] in ["REASONABLE", "ACCEPTABLE"]
        assert 0.1 < f_test["eta_over_eta_B_required"] < 10

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 30 results not yet generated"
    )
    def test_other_low_v_partial(self):
        """Test A: Resonance should work for SOME low-v systems (not all)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        a = data["results"]["A_other_low_velocity"]
        # Should NOT be TUNED_TO_CLOUD9_ONLY (must work for at least 1 more system)
        assert a["verdict"] != "TUNED_TO_CLOUD9_ONLY"
        assert a["systems_in_band"] >= 1

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 30 results not yet generated"
    )
    def test_sparc_bayes_factor_modest(self):
        """Test B: |delta log L| should be modest (not catastrophic)."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        b = data["results"]["B_bayes_factor_sparc"]
        # |delta log L| should be modest (< 10)
        assert abs(b["delta_log_L"]) < 10

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 30 results not yet generated"
    )
    def test_aggregate_verdict_recorded(self):
        """Aggregate verdict should be one of recognized categories."""
        import json
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert data["aggregate_verdict"] in [
            "PLAUSIBLE", "FINE_TUNED_BUT_PLAUSIBLE", "PREMATURE_FULL_SOLUTION"
        ]
