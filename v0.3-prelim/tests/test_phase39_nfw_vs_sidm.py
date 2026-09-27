"""
Tests for Phase 39 (NFW vs SIDM comparison).
"""
import pytest
import os
import json
import numpy as np


class TestPhase39:
    """Tests for Phase 39 — head-to-head NFW vs multi-resonant SIDM."""

    RESULTS_DIR = os.path.join(
        os.path.dirname(__file__), "..", "data", "results"
    )

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase39_nfw_vs_sidm.json")
        assert os.path.exists(path), f"Missing: {path}"

    def test_n_galaxies_reasonable(self):
        """At least 5 galaxies should be fitted."""
        path = os.path.join(self.RESULTS_DIR, "phase39_nfw_vs_sidm.json")
        with open(path) as f:
            data = json.load(f)
        n_galaxies = len(data["results"]["NFW"])
        assert n_galaxies >= 5
        assert n_galaxies == len(data["results"]["SIDM"])

    def test_logL_sane(self):
        """log L values should be finite and negative (Gaussian likelihood)."""
        path = os.path.join(self.RESULTS_DIR, "phase39_nfw_vs_sidm.json")
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]["NFW"]:
            assert np.isfinite(r["log_L"])
            assert r["log_L"] < 0
        for r in data["results"]["SIDM"]:
            assert np.isfinite(r["log_L"])
            assert r["log_L"] < 0

    def test_verdict_in_known_values(self):
        """Verdict should be one of the known Kass-Raftery values."""
        path = os.path.join(self.RESULTS_DIR, "phase39_nfw_vs_sidm.json")
        with open(path) as f:
            data = json.load(f)
        valid_verdicts = [
            "STRONG_SIDM", "MODERATE_SIDM", "WEAK_SIDM",
            "INCONCLUSIVE", "WEAK_NFW", "MODERATE_NFW", "STRONG_NFW"
        ]
        assert data["verdict"] in valid_verdicts

    def test_delta_logL_consistent(self):
        """delta log L = SIDM log L - NFW log L should match sum of per-galaxy."""
        path = os.path.join(self.RESULTS_DIR, "phase39_nfw_vs_sidm.json")
        with open(path) as f:
            data = json.load(f)
        total_sidm = sum(r["log_L"] for r in data["results"]["SIDM"])
        total_nfw = sum(r["log_L"] for r in data["results"]["NFW"])
        expected_delta = total_sidm - total_nfw
        actual_delta = data["totals"]["delta_logL_sidm_minus_nfw"]
        assert abs(expected_delta - actual_delta) < 1e-6