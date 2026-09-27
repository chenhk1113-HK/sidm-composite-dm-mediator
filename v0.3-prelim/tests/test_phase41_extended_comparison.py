"""
Tests for Phase 41 (5-model + nested-sampling comparison).
"""
import pytest
import os
import json
import numpy as np


class TestPhase41:
    """Tests for Phase 41 — 5-model extended comparison + nested sampling."""

    RESULTS_DIR = os.path.join(
        os.path.dirname(__file__), "..", "data", "results"
    )

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase41_extended_comparison.json")
        assert os.path.exists(path), f"Missing: {path}"

    def test_has_five_models(self):
        """5 models: NFW, Burkert, Einasto, PISO, SIDM."""
        path = os.path.join(self.RESULTS_DIR, "phase41_extended_comparison.json")
        with open(path) as f:
            data = json.load(f)
        expected = {"NFW", "Burkert", "Einasto", "PISO", "SIDM"}
        actual = set(data["chi2_results"].keys())
        assert expected == actual, f"Expected {expected}, got {actual}"

    def test_large_sample(self):
        """chi² results should have 100+ galaxies."""
        path = os.path.join(self.RESULTS_DIR, "phase41_extended_comparison.json")
        with open(path) as f:
            data = json.load(f)
        for model_name in ["NFW", "Burkert", "Einasto", "PISO", "SIDM"]:
            n = len(data["chi2_results"][model_name])
            assert n >= 100, f"{model_name}: only {n} galaxies"

    def test_dynesty_present(self):
        """dynesty results should be present (15 galaxies)."""
        path = os.path.join(self.RESULTS_DIR, "phase41_extended_comparison.json")
        with open(path) as f:
            data = json.load(f)
        assert data["dynesty_results"] is not None
        for model_name in ["NFW", "Burkert", "Einasto", "PISO", "SIDM"]:
            n = len(data["dynesty_results"][model_name])
            assert n >= 10, f"dynesty {model_name}: only {n} galaxies"

    def test_einasto_has_k_fit_4(self):
        """Einasto has k_fit=4 (free alpha)."""
        path = os.path.join(self.RESULTS_DIR, "phase41_extended_comparison.json")
        with open(path) as f:
            data = json.load(f)
        for r in data["chi2_results"]["Einasto"]:
            assert r["k_fit"] == 4

    def test_other_models_have_k_fit_3(self):
        """NFW, Burkert, PISO, SIDM all have k_fit=3."""
        path = os.path.join(self.RESULTS_DIR, "phase41_extended_comparison.json")
        with open(path) as f:
            data = json.load(f)
        for model_name in ["NFW", "Burkert", "PISO", "SIDM"]:
            for r in data["chi2_results"][model_name]:
                assert r["k_fit"] == 3

    def test_piso_best_aic(self):
        """PISO should have the lowest chi²-based AIC among 5 models."""
        path = os.path.join(self.RESULTS_DIR, "phase41_extended_comparison.json")
        with open(path) as f:
            data = json.load(f)
        aics = {}
        for model_name in ["NFW", "Burkert", "Einasto", "PISO", "SIDM"]:
            rs = data["chi2_results"][model_name]
            n = len(rs)
            k = rs[0]["k_fit"]
            chi2 = sum(r["chi2"] for r in rs)
            aics[model_name] = n * 2 * k + 2 * chi2
        # PISO has the lowest AIC
        assert aics["PISO"] <= aics["SIDM"]
        assert aics["PISO"] <= aics["Burkert"]
        assert aics["PISO"] <= aics["Einasto"]

    def test_dynesty_log_z_finite(self):
        """All dynesty log Z values should be finite."""
        path = os.path.join(self.RESULTS_DIR, "phase41_extended_comparison.json")
        with open(path) as f:
            data = json.load(f)
        for model_name in ["NFW", "Burkert", "Einasto", "PISO", "SIDM"]:
            for r in data["dynesty_results"][model_name]:
                assert np.isfinite(r["log_Z"])