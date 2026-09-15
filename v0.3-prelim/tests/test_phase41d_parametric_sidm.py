"""
Tests for Phase 41D (gravothermal parametric SIDM).
"""
import pytest
import os
import json
import numpy as np


class TestPhase41D:
    """Tests for Phase 41D — self-consistent gravothermal parametric SIDM."""

    RESULTS_DIR = os.path.join(
        os.path.dirname(__file__), "..", "data", "results"
    )

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        assert os.path.exists(path), f"Missing: {path}"

    def test_n_galaxies(self):
        """Should fit 100+ galaxies."""
        path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        with open(path) as f:
            data = json.load(f)
        n = len(data["results"])
        assert n >= 100, f"Only {n} galaxies"

    def test_k_fit_4(self):
        """Parametric SIDM has k_fit=4 (one extra for t_r)."""
        path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            assert r["k_fit"] == 4

    def test_tr_in_range(self):
        """t_r should be in [0, 1] for all galaxies."""
        path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            t_r = r["params"][2]
            assert 0 <= t_r <= 1, f"Galaxy {r['galaxy']}: t_r={t_r} out of range"

    def test_logL_finite(self):
        """All log L values should be finite and negative."""
        path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            assert np.isfinite(r["log_L"])
            assert r["log_L"] < 0

    def test_verdict_in_known(self):
        """Verdict should be PARAMETRIC_WORSE/SIMILAR/BETTER."""
        path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        with open(path) as f:
            data = json.load(f)
        valid = {"PARAMETRIC_WORSE", "PARAMETRIC_SIMILAR", "PARAMETRIC_BETTER"}
        assert data["comparison_to_phase41"]["verdict"] in valid

    def test_comparison_aic_positive(self):
        """delta_aic should be > 0 (parametric has more params)."""
        path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        with open(path) as f:
            data = json.load(f)
        delta = data["comparison_to_phase41"]["delta_aic"]
        # Parametric has 1 extra param, so delta_aic = 2*1*120 + (chi2_parametric - chi2_hybrid)
        # This is always positive if chi2 didn't improve by 240+ (240 = 2*k*120)
        # In our case, parametric is worse, so delta_aic should be clearly positive
        assert delta > 0

    def test_uses_yang_model(self):
        """Should reference Yang+ 2023 parametric model."""
        path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        with open(path) as f:
            data = json.load(f)
        assert "yang" in data["model_summary"]["calibrated_from"].lower() or "Yang" in data["model_summary"]["calibrated_from"]