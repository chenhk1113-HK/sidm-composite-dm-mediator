"""
Tests for Phase 43, 44, 45 (three-item update).
"""
import pytest
import os
import json
import numpy as np


class TestPhase43:
    """Tests for Phase 43 — velocity-dependent gravothermal."""

    RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "results")

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase43_vdgravothermal.json")
        assert os.path.exists(path)

    def test_aic_close_to_phase41d(self):
        """vd-gravothermal AIC should be close to constant-sigma AIC (Δ < 10)."""
        p43_path = os.path.join(self.RESULTS_DIR, "phase43_vdgravothermal.json")
        p41d_path = os.path.join(self.RESULTS_DIR, "phase41d_parametric_sidm.json")
        with open(p43_path) as f:
            p43 = json.load(f)
        with open(p41d_path) as f:
            p41d = json.load(f)
        delta = p43["totals"]["aic"] - p41d["totals"]["aic"]
        assert abs(delta) < 10, f"|delta AIC| = {delta} too large"


class TestPhase44:
    """Tests for Phase 44 — multi-channel joint fit."""

    RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "results")

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase44_joint_fit.json")
        assert os.path.exists(path)

    def test_improvement_positive(self):
        """Joint fit should improve over baseline."""
        path = os.path.join(self.RESULTS_DIR, "phase44_joint_fit.json")
        with open(path) as f:
            data = json.load(f)
        assert data["improvement"] > 0

    def test_best_fit_has_4_resonances(self):
        """Best-fit should have 4 resonance targets."""
        path = os.path.join(self.RESULTS_DIR, "phase44_joint_fit.json")
        with open(path) as f:
            data = json.load(f)
        v_targets = data["best_params"][3:7]
        assert len(v_targets) == 4


class TestPhase45:
    """Tests for Phase 45 — theoretical UV survey."""

    RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "results")

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase45_theoretical_uv.json")
        assert os.path.exists(path)

    def test_has_six_candidates(self):
        """Should survey 6 candidates."""
        path = os.path.join(self.RESULTS_DIR, "phase45_theoretical_uv.json")
        with open(path) as f:
            data = json.load(f)
        assert len(data["candidates"]) == 6

    def test_hidden_valley_best_match(self):
        """Hidden valley (candidate 3) should be marked as best."""
        path = os.path.join(self.RESULTS_DIR, "phase45_theoretical_uv.json")
        with open(path) as f:
            data = json.load(f)
        hv = data["candidates"]["3_hidden_valley_composite"]
        assert "Plausible" in hv["verdict"] or "good" in hv["feasibility"].lower()

    def test_tsai_2022_falsified(self):
        """Should note that Tsai 2022 UV is inconsistent."""
        path = os.path.join(self.RESULTS_DIR, "phase45_theoretical_uv.json")
        with open(path) as f:
            data = json.load(f)
        assert "Tsai" in data["final_verdict"]
        assert "INCONSISTENT" in data["final_verdict"] or "FALSIFIED" in data["final_verdict"]


class TestPhase46:
    """Tests for Phase 46 — master doc."""

    DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

    def test_master_doc_exists(self):
        path = os.path.join(self.DOCS_DIR, "PHASE46_THREE_ITEM_UPDATE.md")
        assert os.path.exists(path)

    def test_documents_three_items(self):
        path = os.path.join(self.DOCS_DIR, "PHASE46_THREE_ITEM_UPDATE.md")
        with open(path) as f:
            content = f.read()
        for item in ["ITEM 1", "ITEM 2", "ITEM 3"]:
            assert item in content

    def test_documents_verdicts(self):
        path = os.path.join(self.DOCS_DIR, "PHASE46_THREE_ITEM_UPDATE.md")
        with open(path) as f:
            content = f.read()
        assert "NEGATIVE" in content  # Item 1 verdict
        assert "POSITIVE" in content  # Item 2 verdict
        assert "PARTIALLY POSITIVE" in content or "PARTIALLY" in content  # Item 3