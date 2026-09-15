"""
Tests for Phase 42 (master summary doc).
"""
import pytest
import os


class TestPhase42:
    """Tests for Phase 42 — master rotation-curve verdict summary."""

    DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
    README = os.path.join(os.path.dirname(__file__), "..", "README.md")

    def test_master_doc_exists(self):
        path = os.path.join(self.DOCS_DIR, "PHASE42_ROTATION_CURVE_FINAL_VERDICT.md")
        assert os.path.exists(path), f"Missing: {path}"

    def test_branch_readme_exists(self):
        assert os.path.exists(self.README), f"Missing: {self.README}"

    def test_master_doc_has_key_phases(self):
        path = os.path.join(self.DOCS_DIR, "PHASE42_ROTATION_CURVE_FINAL_VERDICT.md")
        with open(path) as f:
            content = f.read()
        # Should mention all 4 phases
        for phase in ["Phase 39", "Phase 40", "Phase 41", "Phase 41D"]:
            assert phase in content, f"Missing phase reference: {phase}"

    def test_master_doc_states_final_verdict(self):
        path = os.path.join(self.DOCS_DIR, "PHASE42_ROTATION_CURVE_FINAL_VERDICT.md")
        with open(path) as f:
            content = f.read()
        # Should be honest about not preferring SIDM over cored profiles
        assert "Burkert wins" in content or "Burkert" in content
        assert "Occam" in content or "AIC" in content

    def test_branch_readme_has_test_count(self):
        with open(self.README) as f:
            content = f.read()
        assert "171" in content  # 171 tests pass

    def test_branch_readme_links_to_master_doc(self):
        with open(self.README) as f:
            content = f.read()
        assert "PHASE42" in content or "final verdict" in content.lower()