"""
Tests for Phase 33a (Bayes factor comparison).
"""
import pytest
import sys
import os
import json


class TestPhase33a:
    RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "results",
        "phase33a_bayes_factor.json"
    )

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33a results not yet generated"
    )
    def test_results_file_valid(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        assert "results" in data
        assert "verdict" in data
        assert "deltas" in data
        for k in ["1_resonance", "2_resonance", "3_resonance", "4_resonance"]:
            assert k in data["results"]

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33a results not yet generated"
    )
    def test_no_model_strongly_disfavored(self):
        """Δlog Z (4 vs 1) should be > -10 (no strong Occam penalty).

        A strong penalty would mean the 4-resonance model is heavily
        overfit. Phase 33a target: inconclusive (Δlog Z > -5).
        """
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        delta = data["deltas"]["delta_4_vs_1"]
        assert delta > -10.0, f"Δlog Z (4 vs 1) = {delta:.2f} — too negative"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33a results not yet generated"
    )
    def test_log_Z_values_finite(self):
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        for k, r in data["results"].items():
            assert -100 < r["log_Z"] < 0, f"{k} log_Z = {r['log_Z']}"

    @pytest.mark.skipif(
        not os.path.exists(RESULTS_PATH),
        reason="Phase 33a results not yet generated"
    )
    def test_each_model_has_three_free_params(self):
        """All models should have N=3 free parameters (background params)."""
        with open(self.RESULTS_PATH) as f:
            data = json.load(f)
        for k, r in data["results"].items():
            assert r["N_params"] == 3, f"{k} has {r['N_params']} params, expected 3"