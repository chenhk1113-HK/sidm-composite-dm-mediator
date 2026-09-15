"""
Tests for Phase 40 (corrected head-to-head comparison).
"""
import pytest
import os
import json
import numpy as np


class TestPhase40:
    """Tests for Phase 40 — corrected NFW vs Burkert vs SIDM comparison."""

    RESULTS_DIR = os.path.join(
        os.path.dirname(__file__), "..", "data", "results"
    )

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase40_corrected_comparison.json")
        assert os.path.exists(path), f"Missing: {path}"

    def test_has_three_models(self):
        """Results must include NFW, Burkert, and SIDM."""
        path = os.path.join(self.RESULTS_DIR, "phase40_corrected_comparison.json")
        with open(path) as f:
            data = json.load(f)
        assert "NFW" in data["results"]
        assert "Burkert" in data["results"]
        assert "SIDM" in data["results"]

    def test_large_sample(self):
        """Phase 40 should have >100 galaxies (vs Phase 39's 15)."""
        path = os.path.join(self.RESULTS_DIR, "phase40_corrected_comparison.json")
        with open(path) as f:
            data = json.load(f)
        n_gal = len(data["results"]["NFW"])
        assert n_gal >= 100, f"Only {n_gal} galaxies, expected >100"

    def test_logL_finite(self):
        """All log L values should be finite and negative."""
        path = os.path.join(self.RESULTS_DIR, "phase40_corrected_comparison.json")
        with open(path) as f:
            data = json.load(f)
        for model_name in ["NFW", "Burkert", "SIDM"]:
            for r in data["results"][model_name]:
                assert np.isfinite(r["log_L"]), f"{model_name}: non-finite log L"
                assert r["log_L"] < 0, f"{model_name}: log L should be negative"

    def test_burkert_beats_nfw(self):
        """Burkert should beat NFW (well-known result for SPARC)."""
        path = os.path.join(self.RESULTS_DIR, "phase40_corrected_comparison.json")
        with open(path) as f:
            data = json.load(f)
        burk_total = sum(r["log_L"] for r in data["results"]["Burkert"])
        nfw_total = sum(r["log_L"] for r in data["results"]["NFW"])
        assert burk_total > nfw_total, (
            f"Burkert should beat NFW on SPARC: "
            f"Burkert {burk_total:.1f} vs NFW {nfw_total:.1f}"
        )

    def test_occam_penalty_included(self):
        """Results must include Occam penalty info (k_phys varies)."""
        path = os.path.join(self.RESULTS_DIR, "phase40_corrected_comparison.json")
        with open(path) as f:
            data = json.load(f)
        assert "occam_penalty" in data
        op = data["occam_penalty"]
        assert op["k_phys_sidm"] > op["k_phys_nfw"]
        assert op["k_phys_sidm"] >= 10  # multi-resonance has many params

    def test_outlier_analysis_present(self):
        """Outlier analysis must be reported."""
        path = os.path.join(self.RESULTS_DIR, "phase40_corrected_comparison.json")
        with open(path) as f:
            data = json.load(f)
        assert "outlier_analysis" in data
        oa = data["outlier_analysis"]
        assert "outliers_sidm_vs_nfw" in oa
        assert "n_after_dropping" in oa

    def test_deltas_consistent(self):
        """Delta log L should match sum of per-galaxy differences."""
        path = os.path.join(self.RESULTS_DIR, "phase40_corrected_comparison.json")
        with open(path) as f:
            data = json.load(f)
        # Verify SIDM - NFW total
        delta = sum(
            s["log_L"] - n["log_L"]
            for n, s in zip(data["results"]["NFW"], data["results"]["SIDM"])
        )
        assert abs(delta - data["totals"]["delta_sid_minus_nfw_total"]) < 1e-4