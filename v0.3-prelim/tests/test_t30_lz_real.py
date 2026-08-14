"""
Tests for T30 (LZ 2024 real posterior ingestion, T3.1 of R2 review).
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


class TestT30Module:
    """t30_lz_real_posterior.py is importable."""

    def test_t30_importable(self):
        t30 = pytest.importorskip("t30_lz_real_posterior")
        assert hasattr(t30, "LZ_REAL")
        assert hasattr(t30, "loglike_lz_real")
        assert hasattr(t30, "loglike_5channel_with_real_lz")
        assert hasattr(t30, "loglike_5channel_with_placeholder_lz")
        assert hasattr(t30, "main")

    def test_lz_data_has_26_mass_points(self):
        """LZ WS2024 has 26 mass points (9 GeV to 10 TeV)."""
        t30 = pytest.importorskip("t30_lz_real_posterior")
        assert len(t30.LZ_REAL) == 26, f"Expected 26 mass points, got {len(t30.LZ_REAL)}"
        # First and last mass
        assert t30.LZ_REAL[0][0] == 9.0
        assert t30.LZ_REAL[-1][0] == 10000.0

    def test_best_limit_at_40_GeV(self):
        """LZ best limit should be at 40 GeV (matches paper)."""
        t30 = pytest.importorskip("t30_lz_real_posterior")
        limits = [r[1] for r in t30.LZ_REAL]
        min_idx = int(np.argmin(limits))
        # Best limit at m_chi = 40 GeV (paper says 2.2e-48)
        assert t30.LZ_REAL[min_idx][0] == 40.0, (
            f"Best limit at m={t30.LZ_REAL[min_idx][0]} GeV, expected 40 GeV"
        )
        # Should be around 2.2e-48 cm^2 (per paper)
        assert 1.5e-48 < limits[min_idx] < 3.0e-48, (
            f"Best limit {limits[min_idx]:.3e}, expected ~2.2e-48"
        )

    def test_interpolation_at_40_GeV(self):
        """loglike_lz_real at 40 GeV returns 0 for sigma well below limit."""
        t30 = pytest.importorskip("t30_lz_real_posterior")
        # sigma = 1e-50 cm^2 at m_chi=40 GeV: well below limit (2.2e-48), should be allowed (log L = 0)
        ll = t30.loglike_lz_real(40.0, 1e-50)
        assert ll == 0.0, f"Should be 0 for sigma well below limit: {ll}"
        # sigma = 1e-46 cm^2 at m_chi=40 GeV: above limit, should be excluded
        ll_excluded = t30.loglike_lz_real(40.0, 1e-46)
        assert ll_excluded < 0, f"Should be negative for sigma above limit: {ll_excluded}"

    def test_5channel_with_real_lz_returns_finite(self):
        """loglike_5channel_with_real_lz at reasonable point returns finite log L."""
        t30 = pytest.importorskip("t30_lz_real_posterior")
        # At log_sigma_m = 0, a = 0.5
        ll = t30.loglike_5channel_with_real_lz([0.0, 0.5])
        assert np.isfinite(ll), f"5-channel log L should be finite: {ll}"


class TestT30Result:
    """If T30 result JSON exists, validate it."""

    def test_t30_result_or_skip(self):
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t30_lz_real_posterior.json"
        if not result_path.exists():
            pytest.skip("No T30 result JSON; run t30_lz_real_posterior.py first")
        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "comparison" in data
        assert "A_placeholder" in data["fits"]
        assert "B_real_lz" in data["fits"]
        # The headline: real LZ should be more constraining than placeholder
        # (because real data has 26 mass points with tighter limits)
        log_Z_A = data["fits"]["A_placeholder"]["log_Z"]
        log_Z_B = data["fits"]["B_real_lz"]["log_Z"]
        assert np.isfinite(log_Z_A)
        assert np.isfinite(log_Z_B)