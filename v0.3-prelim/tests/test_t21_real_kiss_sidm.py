"""
Tests for t21_real_kiss_sidm_gravothermal.py.

T21 is the publication-quality replacement for T17 (KISS-SIDM corrected
fit) using the REAL KiSS-SIDM simulation (Gurian & May 2025) for the
gravothermal penalty instead of the placeholder fluid model.

These tests verify:
  1. The T21 module is importable
  2. The real KISS-SIDM data can be loaded (if aggregated JSON exists)
  3. The parser handles Julia's 1D/2D array print formats
  4. The T21 result JSON (if it exists) has the expected structure

Standing rule (AGENTS.md): no new dependencies.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))


class TestT21Module:
    """t21_real_kiss_sidm_gravothermal.py module is importable."""

    def test_t21_importable(self):
        """The T21 module is importable."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        assert hasattr(t21, "_load_real_kiss_data")
        assert hasattr(t21, "_compute_real_r_core")
        assert hasattr(t21, "_kiss_sidm_correction")
        assert hasattr(t21, "loglike_t21_with_real_kiss")
        assert hasattr(t21, "loglike_t21_no_kiss_correction")

    def test_parser_handles_julia_1d_space_separated(self):
        """The array parser handles Julia's 1D space-separated format."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        s = "[0.0 0.5 1.0 1.5 2.0]"
        arr = t21._parse_array_string(s)
        assert len(arr) == 5
        assert arr[0] == 0.0
        assert arr[-1] == 2.0

    def test_parser_handles_2d_semicolon_separated(self):
        """The array parser handles Julia's 2D semicolon-separated format."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        s = "[1.0 2.0 3.0; 4.0 5.0 6.0; 7.0 8.0 9.0]"
        arr = t21._parse_array_string(s)
        assert arr.shape == (3, 3)
        assert arr[0, 0] == 1.0
        assert arr[2, 2] == 9.0

    def test_parser_handles_json_format(self):
        """The array parser handles JSON-style arrays with brackets."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        s = "[[1.0,2.0,3.0],[4.0,5.0,6.0]]"
        arr = t21._parse_array_string(s)
        assert arr.shape == (2, 3)

    def test_parser_handles_comma_separated_1d(self):
        """The array parser handles comma-separated 1D arrays."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        s = "[1.0, 2.0, 3.0]"
        arr = t21._parse_array_string(s)
        assert len(arr) == 3

    def test_parser_handles_empty(self):
        """The array parser handles empty strings."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        arr = t21._parse_array_string("")
        assert len(arr) == 0

    def test_kiss_sidm_correction_in_range(self):
        """KISS-SIDM correction factor is in [0.778, 1.0]."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        # Small sigma -> LMFP/SMFP -> correction = 1.0
        assert 0.7 <= t21._kiss_sidm_correction(0.01) <= 1.0
        # Large sigma -> IMFP -> correction = 0.778
        # (depends on Kn threshold, may not be 0.778 exactly for our canonical halo)
        c = t21._kiss_sidm_correction(50.0)
        assert 0.7 <= c <= 1.0


class TestRealKISSDataLoading:
    """If the real KISS-SIDM data is available, the loader should work."""

    def test_aggregated_json_or_skip(self):
        """If the aggregated JSON exists, validate its structure."""
        agg_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "real_kiss_sidm_aggregated.json"
        if not agg_path.exists():
            pytest.skip("No aggregated JSON; run kiss_sidm_julia_reader.py first")

        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        data = t21._load_real_kiss_data()
        assert data["n_snapshots"] > 0
        assert "r_over_rs" in data
        assert "time_Gyr" in data
        assert "rho_over_rhos" in data
        # Verify shapes
        n_snap = data["n_snapshots"]
        n_bins = len(data["r_over_rs"])
        assert data["rho_over_rhos"].shape == (n_snap, n_bins), (
            f"rho shape {data['rho_over_rhos'].shape} != ({n_snap}, {n_bins})"
        )
        assert data["time_Gyr"].shape == (n_snap,)
        # canonical_halo metadata
        halo = data["canonical_halo"]
        assert halo["M_halo_Msun"] == 1e9
        assert halo["sigma_m_cm2_per_g"] == 50.0


class TestComputeRCore:
    """Test the r_core computation from real KISS-SIDM data."""

    def test_compute_r_core_returns_positive(self):
        """r_core computation should return a positive value."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        agg_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "real_kiss_sidm_aggregated.json"
        if not agg_path.exists():
            pytest.skip("No aggregated JSON")
        data = t21._load_real_kiss_data()
        # At t=10 Gyr, r_core should be positive
        r_core = t21._compute_real_r_core(data, t_target_Gyr=10.0)
        assert r_core > 0
        # r_core is in units of r_s, should be in physical range
        assert 0.001 < r_core < 100.0

    def test_compute_r_core_finds_nearby_snapshot(self):
        """The closest snapshot should be within the time range."""
        t21 = pytest.importorskip("t21_real_kiss_sidm_gravothermal")
        agg_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "real_kiss_sidm_aggregated.json"
        if not agg_path.exists():
            pytest.skip("No aggregated JSON")
        data = t21._load_real_kiss_data()
        t_min = data["time_Gyr"][0]
        t_max = data["time_Gyr"][-1]
        # Test at the middle of the time range
        t_mid = 0.5 * (t_min + t_max)
        r_core = t21._compute_real_r_core(data, t_target_Gyr=t_mid)
        assert r_core > 0


class TestT21Result:
    """If T21 result JSON exists, validate it."""

    def test_t21_result_or_skip(self):
        """If T21 result JSON exists, check it has the expected structure."""
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t21_real_kiss_sidm_gravothermal.json"
        if not result_path.exists():
            pytest.skip("No T21 result JSON; run t21_real_kiss_sidm_gravothermal.py first")

        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "T21_A_with_kiss_correction" in data
        assert "T21_B_no_kiss_correction" in data
        assert "data_source" in data
        # Log Z should be finite
        assert np.isfinite(data["T21_A_with_kiss_correction"]["log_Z"])
        assert np.isfinite(data["T21_B_no_kiss_correction"]["log_Z"])
        # MAP should be in the prior range
        map_a = data["T21_A_with_kiss_correction"]["MAP"]
        assert -2.0 <= map_a[0] <= 2.0
        assert -2.0 <= map_a[1] <= 2.0
        # Compare to t17 placeholder
        t17 = data.get("t17_placeholder_summary", {})
        if t17:
            # The real KISS-SIDM should give a HIGHER (less negative) log Z
            # than the placeholder because the real r_core is smaller
            assert data["T21_B_no_kiss_correction"]["log_Z"] > t17.get("log_Z_no_correction", -np.inf), (
                f"Real KISS-SIDM should improve fit: "
                f"T21 B log Z = {data['T21_B_no_kiss_correction']['log_Z']} "
                f"vs t17 placeholder = {t17.get('log_Z_no_correction')}"
            )
