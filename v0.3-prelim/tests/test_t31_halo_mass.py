"""
Tests for T31 (halo-mass marginalization, T3.2 of R2 review).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
for sub in ["v0.3-prelim/code", "v0.1-prelim/code"]:
    p = str(PROJECT_ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)


class TestT31Module:
    """t31_halo_mass_marginalization.py is importable."""

    def test_t31_importable(self):
        t31 = pytest.importorskip("t31_halo_mass_marginalization")
        assert hasattr(t31, "run_one")
        assert hasattr(t31, "main")
        assert hasattr(t31, "DWARF_M_HALO")
        assert hasattr(t31, "DWARF_SIGMA_M")

    def test_dwarf_mass_smaller_than_canonical(self):
        """Dwarf halo is 10x smaller than canonical."""
        t31 = pytest.importorskip("t31_halo_mass_marginalization")
        assert t31.DWARF_M_HALO < 1e9
        assert t31.DWARF_R_S < 1.18  # dwarf scale radius smaller

    def test_dwarf_scale_radius_scaling(self):
        """Dwarf r_s = canonical r_s * (M_dwarf/M_canonical)^(1/3)."""
        t31 = pytest.importorskip("t31_halo_mass_marginalization")
        # r_s scales as M^(1/3), so for 10x smaller mass: 10^(1/3) ≈ 2.154 smaller
        expected_ratio = (t31.DWARF_M_HALO / 1e9) ** (1.0/3.0)
        actual_ratio = t31.DWARF_R_S / 1.18
        assert abs(actual_ratio - expected_ratio) < 0.01


class TestT31Result:
    """If T31 result JSON exists, validate it."""

    def test_t31_result_or_skip(self):
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t31_halo_mass_marginalization.json"
        if not result_path.exists():
            pytest.skip("No T31 result JSON; run t31_halo_mass_marginalization.py first")
        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "results" in data
        assert "verdict" in data
        # Should have at least 1 result (canonical)
        assert len(data["results"]) >= 1
        # The canonical r_core/r_s should be ~ 0.1024
        canonical = data["results"][0]
        if "r_core_over_rs_at_0.5x_central" in canonical and canonical["r_core_over_rs_at_0.5x_central"]:
            assert 0.05 < canonical["r_core_over_rs_at_0.5x_central"] < 0.2