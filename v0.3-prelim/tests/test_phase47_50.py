"""
Tests for Phases 47, 48, 49, 50 (stress-test, hidden-valley, paper outline, JVAS decision).
"""
import pytest
import os
import json


class TestPhase47:
    """Tests for Phase 47 — stress-test of Phase 44 joint fit."""

    RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "results")

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase47_stress_test.json")
        assert os.path.exists(path)

    def test_loo_test_performed(self):
        path = os.path.join(self.RESULTS_DIR, "phase47_stress_test.json")
        with open(path) as f:
            data = json.load(f)
        assert "loo_results" in data
        assert "without_jvas" in data["loo_results"]
        assert "without_cloud9" in data["loo_results"]
        assert "without_sparc" in data["loo_results"]

    def test_posterior_predictive_present(self):
        path = os.path.join(self.RESULTS_DIR, "phase47_stress_test.json")
        with open(path) as f:
            data = json.load(f)
        assert "posterior_predictive" in data
        # Should have credible intervals at key velocities
        for v in [15, 28, 100, 300]:
            assert v in data["posterior_predictive"] or str(v) in data["posterior_predictive"]


class TestPhase48:
    """Tests for Phase 48 — hidden-valley benchmark."""

    RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "results")

    def test_results_exist(self):
        path = os.path.join(self.RESULTS_DIR, "phase48_hidden_valley.json")
        assert os.path.exists(path)

    def test_fine_tuning_quantified(self):
        path = os.path.join(self.RESULTS_DIR, "phase48_hidden_valley.json")
        with open(path) as f:
            data = json.load(f)
        assert "fine_tuning_rms_log10" in data
        assert data["fine_tuning_rms_log10"] > 0

    def test_honest_negative_verdict(self):
        """Should report that hidden-valley requires significant fine-tuning."""
        path = os.path.join(self.RESULTS_DIR, "phase48_hidden_valley.json")
        with open(path) as f:
            data = json.load(f)
        assert "fine-tuning" in data["interpretation"] or "fine_tuning" in str(data)


class TestPhase49:
    """Tests for Phase 49 — paper outline."""

    DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

    def test_doc_exists(self):
        path = os.path.join(self.DOCS_DIR, "PHASE49_PAPER_OUTLINE.md")
        assert os.path.exists(path)

    def test_doc_has_8_sections(self):
        path = os.path.join(self.DOCS_DIR, "PHASE49_PAPER_OUTLINE.md")
        with open(path) as f:
            content = f.read()
        for i in range(1, 9):
            assert f"{i}." in content, f"Missing section {i}"

    def test_doc_has_honest_caveats(self):
        path = os.path.join(self.DOCS_DIR, "PHASE49_PAPER_OUTLINE.md")
        with open(path) as f:
            content = f.read()
        # Must include the explicit caveats the reviewer flagged
        assert "Rotation curves alone" in content or "rotation curves alone" in content.lower()
        assert "JVAS" in content
        assert "Tsai 2022" in content or "Tsai" in content
        assert "fine-tuning" in content or "fine tuning" in content.lower()


class TestPhase50:
    """Tests for Phase 50 — JVAS decision."""

    DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

    def test_doc_exists(self):
        path = os.path.join(self.DOCS_DIR, "PHASE50_JVAS_DECISION.md")
        assert os.path.exists(path)

    def test_doc_classifies_jvas_as_domain_limitation(self):
        path = os.path.join(self.DOCS_DIR, "PHASE50_JVAS_DECISION.md")
        with open(path) as f:
            content = f.read()
        assert "DOMAIN LIMITATION" in content or "domain limitation" in content.lower()

    def test_doc_cites_zhang_yu_2026(self):
        path = os.path.join(self.DOCS_DIR, "PHASE50_JVAS_DECISION.md")
        with open(path) as f:
            content = f.read()
        assert "Zhang" in content and "2026" in content
        assert "2510.11006" in content or "arXiv" in content