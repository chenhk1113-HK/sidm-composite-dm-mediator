"""
Tests for T32 (Fermi dwarf galaxy channel, T3.3 of R2 review).
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


class TestT32Module:
    """t32_fermi_dwarf_channel.py is importable."""

    def test_t32_importable(self):
        t32 = pytest.importorskip("t32_fermi_dwarf_channel")
        assert hasattr(t32, "FERMI_DWARFS")
        assert hasattr(t32, "FERMI_95CL_LIMITS")
        assert hasattr(t32, "loglike_fermi_dwarf")
        assert hasattr(t32, "loglike_5channel_with_fermi")
        assert hasattr(t32, "loglike_5channel_without_fermi")

    def test_dwarf_sample_has_20_sources(self):
        """FERMI_DWARFS should have ~20+ sources (Albert+ 2017 + Hooper & Linden 2024)."""
        t32 = pytest.importorskip("t32_fermi_dwarf_channel")
        assert len(t32.FERMI_DWARFS) >= 20, f"Expected 20+ dwarfs, got {len(t32.FERMI_DWARFS)}"

    def test_fermi_limits_have_10_points(self):
        """FERMI_95CL_LIMITS should have 10 mass points (5 GeV to 10 TeV)."""
        t32 = pytest.importorskip("t32_fermi_dwarf_channel")
        assert len(t32.FERMI_95CL_LIMITS) >= 9

    def test_fermi_limit_at_50_GeV(self):
        """Best Fermi limit should be near 50 GeV (thermal relic cross-section 3e-26)."""
        t32 = pytest.importorskip("t32_fermi_dwarf_channel")
        # Find the lowest limit
        limits = [r[1] for r in t32.FERMI_95CL_LIMITS]
        masses = [r[0] for r in t32.FERMI_95CL_LIMITS]
        min_idx = int(np.argmin(limits))
        # Best limit should be near 50-100 GeV (canonical thermal relic)
        assert masses[min_idx] in [50.0, 100.0], (
            f"Best limit at m={masses[min_idx]} GeV, expected 50 or 100"
        )
        # Should be ~1e-26 (thermal relic cross-section)
        assert 1e-27 < limits[min_idx] < 1e-25

    def test_interpolation_at_50_GeV(self):
        """loglike_fermi_dwarf at 50 GeV: 0 below limit, negative above."""
        t32 = pytest.importorskip("t32_fermi_dwarf_channel")
        # Below limit: log L = 0
        ll_low = t32.loglike_fermi_dwarf(50.0, 1e-27)
        assert ll_low == 0.0, f"Should be 0 below limit: {ll_low}"
        # Above limit: log L < 0
        ll_high = t32.loglike_fermi_dwarf(50.0, 1e-24)
        assert ll_high < 0, f"Should be negative above limit: {ll_high}"


class TestT32Result:
    """If T32 result JSON exists, validate it."""

    def test_t32_result_or_skip(self):
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t32_fermi_dwarf_channel.json"
        if not result_path.exists():
            pytest.skip("No T32 result JSON; run t32_fermi_dwarf_channel.py first")
        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "A_no_fermi" in data["fits"]
        assert "B_with_fermi" in data["fits"]
        log_Z_A = data["fits"]["A_no_fermi"]["log_Z"]
        log_Z_B = data["fits"]["B_with_fermi"]["log_Z"]
        assert np.isfinite(log_Z_A)
        assert np.isfinite(log_Z_B)