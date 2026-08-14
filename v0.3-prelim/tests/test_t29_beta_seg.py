"""
Tests for T29 (beta_seg as fitted free parameter, T3.4 from R2 review).
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


class TestT29Module:
    """t29_beta_seg_fitted.py is importable."""

    def test_t29_importable(self):
        t29 = pytest.importorskip("t29_beta_seg_fitted")
        assert hasattr(t29, "loglike_two_comp_yang_real_kiss_with_beta")
        assert hasattr(t29, "loglike_two_comp_yang_with_fixed_beta")
        assert hasattr(t29, "BETA_SEG_RANGE")
        assert hasattr(t29, "prior_transform_5")
        assert hasattr(t29, "main")

    def test_beta_seg_range(self):
        """BETA_SEG_RANGE is physically motivated."""
        t29 = pytest.importorskip("t29_beta_seg_fitted")
        lo, hi = t29.BETA_SEG_RANGE
        assert 0.0 <= lo < hi <= 2.0, f"BETA_SEG_RANGE = ({lo}, {hi}), expected physically motivated bounds"

    def test_segregation_factor_monotonic(self):
        """segregation_factor should monotonically decrease with v for positive beta_seg."""
        t29 = pytest.importorskip("t29_beta_seg_fitted")
        import two_component_sidm as tcs
        # For beta_seg > 0, g(v) = (V_REF/v)^beta_seg, so g DECREASES with v
        g_low = tcs.segregation_factor(10.0, beta_seg=0.5)
        g_high = tcs.segregation_factor(1000.0, beta_seg=0.5)
        assert g_low > g_high, f"g(10)={g_low} should be > g(1000)={g_high} for positive beta_seg"

    def test_fixed_beta_likelihood_at_peak(self):
        """loglike_two_comp_yang_with_fixed_beta returns finite at reasonable point."""
        t29 = pytest.importorskip("t29_beta_seg_fitted")
        # Load KISS data (mock for test)
        kiss_data = {"snapshots": [{"r_core_over_rs": 0.01, "t_Gyr": 10.0}]}
        # At log_sigma1=-0.5, log_sigma2=0.5, f1=0.5, a=0.5
        ll = t29.loglike_two_comp_yang_with_fixed_beta([-0.5, 0.5, 0.5, 0.5], 0.25, kiss_data)
        assert np.isfinite(ll), f"Fixed-beta log L should be finite: {ll}"

    def test_fitted_beta_likelihood_at_peak(self):
        """loglike_two_comp_yang_real_kiss_with_beta returns finite at reasonable point."""
        t29 = pytest.importorskip("t29_beta_seg_fitted")
        kiss_data = {"snapshots": [{"r_core_over_rs": 0.01, "t_Gyr": 10.0}]}
        # 5D: log_sigma1, log_sigma2, f1, a, beta_seg
        ll = t29.loglike_two_comp_yang_real_kiss_with_beta([-0.5, 0.5, 0.5, 0.5, 0.5], kiss_data)
        assert np.isfinite(ll), f"Fitted-beta log L should be finite: {ll}"


class TestT29Result:
    """If T29 result JSON exists, validate it."""

    def test_t29_result_or_skip(self):
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t29_beta_seg_fitted.json"
        if not result_path.exists():
            pytest.skip("No T29 result JSON; run t29_beta_seg_fitted.py first")
        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "comparison" in data
        # Both fits must exist
        assert "A_fixed_beta_0.25" in data["fits"]
        assert "B_fitted_beta" in data["fits"]
        # Comparison must have beta_seg_MAP and verdict
        comp = data["comparison"]
        assert "beta_seg_MAP" in comp
        assert "verdict" in comp
        # beta_seg_MAP must be in [0, 1] (the prior range)
        assert 0.0 <= comp["beta_seg_MAP"] <= 1.0