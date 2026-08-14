"""
Tests for T39 prior robustness (D15 FIX-3) and plot_posteriors.py (D15 FIX-5).
"""
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T39_PR_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t39_prior_robustness.json"


class TestT39PriorRobustnessModule:
    """t39_prior_robustness.py is importable."""

    def test_t39pr_importable(self):
        t39pr = pytest.importorskip("t39_prior_robustness")
        assert hasattr(t39pr, "main")
        assert hasattr(t39pr, "PRIOR_A_WIDE")
        assert hasattr(t39pr, "PRIOR_B_NARROW")
        # Two prior ranges
        assert t39pr.PRIOR_A_WIDE["label"] == "WIDE (current)"
        assert t39pr.PRIOR_B_NARROW["label"] == "NARROW (no SM-decoupling)"
        # WIDE allows SM-decoupling
        assert t39pr.PRIOR_A_WIDE["log_epsilon"][0] <= -50
        # NARROW does NOT allow SM-decoupling
        assert t39pr.PRIOR_B_NARROW["log_epsilon"][0] >= -10


class TestT39PriorRobustnessResult:
    """If T39 prior robustness result exists, validate it."""

    def test_t39pr_result_or_skip(self):
        if not T39_PR_RESULT.exists():
            pytest.skip("T39 prior robustness not yet run")
        with open(T39_PR_RESULT) as f:
            data = json.load(f)
        assert "fits" in data
        assert "WIDE (current)" in data["fits"]
        assert "NARROW (no SM-decoupling)" in data["fits"]

    def test_t39pr_wide_prior_resolves(self):
        """WIDE prior log Z should be > -100 (Tier-3 RESOLVED)."""
        if not T39_PR_RESULT.exists():
            pytest.skip("T39 prior robustness not yet run")
        with open(T39_PR_RESULT) as f:
            data = json.load(f)
        z_wide = data["fits"]["WIDE (current)"]["log_Z"]
        assert z_wide > -100, (
            f"WIDE prior log_Z = {z_wide:.2f} does NOT resolve Tier-3 (need > -100)."
        )

    def test_t39pr_narrow_prior_does_not_resolve(self):
        """NARROW prior log Z should be < -100 (Tier-3 NOT RESOLVED)."""
        if not T39_PR_RESULT.exists():
            pytest.skip("T39 prior robustness not yet run")
        with open(T39_PR_RESULT) as f:
            data = json.load(f)
        z_narrow = data["fits"]["NARROW (no SM-decoupling)"]["log_Z"]
        assert z_narrow < -100, (
            f"NARROW prior log_Z = {z_narrow:.2f} unexpectedly resolves Tier-3 "
            f"(expected NOT to resolve, requiring SM-decoupling regime)."
        )

    def test_t39pr_verdict_classifies(self):
        """T39 prior robustness verdict must classify as ROBUST or PRIOR-DEPENDENT."""
        if not T39_PR_RESULT.exists():
            pytest.skip("T39 prior robustness not yet run")
        with open(T39_PR_RESULT) as f:
            data = json.load(f)
        verdict = data.get("robustness_verdict", "")
        acceptable = ("ROBUST", "PRIOR-DEPENDENT", "PRIOR DEPENDENT")
        assert any(kw in verdict.upper() for kw in acceptable), (
            f"T39 prior robustness verdict unparseable: {verdict!r}"
        )


class TestT39SMDecouplingFlag:
    """T39 main result must include 'requires_sm_decoupling' flag (FIX-4)."""

    def test_t39_requires_sm_decoupling_flag(self):
        """T39 JSON must include the requires_sm_decoupling field added in FIX-4."""
        t39_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t39_tier3_epsilon_alpha_joint_fit.json"
        if not t39_path.exists():
            pytest.skip("T39 not yet run")
        with open(t39_path) as f:
            data = json.load(f)
        assert "requires_sm_decoupling" in data, (
            "T39 JSON missing 'requires_sm_decoupling' field. FIX-4 incomplete."
        )
        assert "publishable_caveat" in data, (
            "T39 JSON missing 'publishable_caveat' field. FIX-4 incomplete."
        )


class TestPlotPosteriorsScript:
    """plot_posteriors.py exists and is runnable (FIX-5)."""

    def test_plot_posteriors_importable(self):
        try:
            import plot_posteriors  # noqa: F401
        except ImportError:
            # Not on Windows Python; WSL Python has it
            pytest.skip("plot_posteriors is a WSL-side script")

    def test_plots_generated(self):
        plots_dir = PROJECT_ROOT / "outputs" / "plots"
        if not plots_dir.exists():
            pytest.skip("plots/ not yet generated")
        png_files = list(plots_dir.glob("*.png"))
        assert len(png_files) >= 3, (
            f"Expected at least 3 PNG plots in outputs/plots/, got {len(png_files)}"
        )