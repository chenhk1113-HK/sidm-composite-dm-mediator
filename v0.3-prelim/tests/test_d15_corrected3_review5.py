"""
Tests for D15-CORRECTED3 fixes (review5.docx):
  FIX-8: caveat in plot titles
  FIX-9: summarize_results.py aggregator
  FIX-10: T39 4D corner plot
  FIX-11: FINDINGS.md Appendix S (systematic offsets)
"""
import json
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestSummarizeResultsModule:
    """FIX-9: summarize_results.py exists and works."""

    def test_summarize_results_importable(self):
        try:
            import summarize_results  # noqa: F401
        except ImportError:
            pytest.skip("summarize_results is a WSL-side script")
        # Has the main function
        import summarize_results
        assert hasattr(summarize_results, "main")
        assert hasattr(summarize_results, "collect_results")
        assert hasattr(summarize_results, "write_csv")
        assert hasattr(summarize_results, "write_md")


class TestSummarizeResultsOutput:
    """FIX-9: outputs/summary_table.{csv,md,txt} exist."""

    def test_summary_outputs_exist_or_skip(self):
        outputs_dir = PROJECT_ROOT / "outputs"
        if not outputs_dir.exists():
            pytest.skip("outputs/ not yet generated")
        csv_path = outputs_dir / "summary_table.csv"
        md_path = outputs_dir / "summary_table.md"
        # At least one must exist if FIX-9 was applied
        assert csv_path.exists() or md_path.exists(), (
            "FIX-9 incomplete: neither summary_table.csv nor summary_table.md found."
        )

    def test_summary_md_has_required_columns(self):
        md_path = PROJECT_ROOT / "outputs" / "summary_table.md"
        if not md_path.exists():
            pytest.skip("summary_table.md not yet generated")
        content = md_path.read_text()
        # Required columns from FIX-9 spec
        required = ["name", "direction", "log Z", "MAP log σ/m", "median σ/m"]
        for r in required:
            assert r in content, (
                f"summary_table.md missing required column: {r!r}. "
                f"Content head: {content[:300]}"
            )


class TestPlotCornerAdded:
    """FIX-10: T39 4D corner plot generated."""

    def test_corner_plot_exists(self):
        plots_dir = PROJECT_ROOT / "outputs" / "plots"
        if not plots_dir.exists():
            pytest.skip("plots/ not yet generated")
        corner_path = plots_dir / "t39_4d_corner.png"
        assert corner_path.exists(), (
            f"FIX-10 incomplete: {corner_path} not generated."
        )


class TestFindingsAppendixS:
    """FIX-11: FINDINGS.md Appendix S added."""

    def test_findings_has_appendix_s(self):
        findings_path = PROJECT_ROOT / "v0.3-prelim" / "docs" / "FINDINGS.md"
        if not findings_path.exists():
            pytest.skip("FINDINGS.md not found")
        content = findings_path.read_text()
        assert "Appendix S" in content, (
            "FIX-11 incomplete: FINDINGS.md missing 'Appendix S' section."
        )
        assert "systematic" in content.lower() or "Systematic" in content, (
            "FIX-11 incomplete: Appendix S doesn't mention 'systematic'."
        )
        assert "SASHIMI" in content, (
            "FIX-11 incomplete: Appendix S doesn't mention SASHIMI."
        )

    def test_findings_has_total_systematic_budget(self):
        findings_path = PROJECT_ROOT / "v0.3-prelim" / "docs" / "FINDINGS.md"
        if not findings_path.exists():
            pytest.skip("FINDINGS.md not found")
        content = findings_path.read_text()
        # Should have a "Total systematic budget" section
        assert "total systematic budget" in content.lower() or "TOTAL" in content, (
            "FIX-11 incomplete: Appendix S missing total systematic budget."
        )


class TestReview5Audit:
    """review5_audit.py + review5_audit.json exist."""

    def test_review5_audit_file_exists(self):
        """review5_audit.py file exists in code/."""
        audit_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "review5_audit.py"
        assert audit_path.exists(), f"review5_audit.py not found at {audit_path}"

    def test_review5_audit_json_exists(self):
        audit_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "review5_audit.json"
        if not audit_path.exists():
            pytest.skip("review5_audit.json not yet generated")
        with open(audit_path) as f:
            data = json.load(f)
        assert "tier_1_verified_correct" in data
        assert "tier_5_review_quality_assessment" in data