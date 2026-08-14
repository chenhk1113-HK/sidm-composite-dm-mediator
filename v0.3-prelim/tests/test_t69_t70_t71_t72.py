"""
Tests for T69-T72 (reviewer recommendations on cross-validation).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T69_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t69_velocity_scaling_cross_check.py"
T70_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t70_mev_mass_window.py"
T71_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t71_relic_density_mechanism_comparison.py"
T72_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t72_cross_validation_plot.py"


class TestT69VelocityScaling:
    """T69 — Velocity scaling cross-check."""

    def test_t69_importable(self):
        t69 = pytest.importorskip("t69_velocity_scaling_cross_check")
        assert hasattr(t69, "beta_param")
        assert hasattr(t69, "predicted_slope_a")

    def test_t69_drobczyk_classical(self):
        """Drobczyk benchmark should be deep classical regime."""
        t69 = pytest.importorskip("t69_velocity_scaling_cross_check")
        beta = t69.beta_param(600.0, 15.0, 0.30)
        assert beta > 100, f"Drobczyk beta = {beta} should be > 100 (classical)"

    def test_t69_t54_classical(self):
        """T54 MAP should also be deep classical regime."""
        t69 = pytest.importorskip("t69_velocity_scaling_cross_check")
        beta = t69.beta_param(34.16, 3.55, 1.51)
        assert beta > 100, f"T54 beta = {beta} should be > 100 (classical)"


class TestT70MeVMassWindow:
    """T70 — MeV mass window preference."""

    def test_t70_importable(self):
        t70 = pytest.importorskip("t70_mev_mass_window")
        assert hasattr(t70, "force_range_cm")
        assert hasattr(t70, "fifth_force_safe")

    def test_t70_mev_window_safe(self):
        """Mediators in MeV range should be fifth-force safe."""
        t70 = pytest.importorskip("t70_mev_mass_window")
        for m in [3.5, 10, 15, 30]:
            assert t70.fifth_force_safe(m), f"m={m} MeV should be safe"


class TestT71RelicMechanism:
    """T71 — Relic density mechanism comparison."""

    def test_t71_importable(self):
        t71 = pytest.importorskip("t71_relic_density_mechanism_comparison")
        assert hasattr(t71, "main")


class TestT72Plot:
    """T72 — Cross-validation plot."""

    def test_t72_importable(self):
        t72 = pytest.importorskip("t72_cross_validation_plot")
        assert hasattr(t72, "main")

    def test_t72_plot_generated(self):
        plot_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/outputs/Cross_Validation_T54_vs_Drobczyk_2026-08-13.png")
        if not plot_path.exists():
            pytest.skip("Plot not yet generated")
        assert plot_path.stat().st_size > 1000, "Plot should be > 1 KB"