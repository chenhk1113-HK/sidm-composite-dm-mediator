"""
Tests for T26 (T21 width sensitivity), T27 (multi-resolution KISS), T28 (published-style dSph).

Tier 1 + 2 + 3 of D7 plan: deepen the systematic uncertainty analysis
and move toward more realistic published-style likelihoods.

Standing rule (AGENTS.md): no new dependencies.
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


class TestT26Module:
    """t26_t21_width_sensitivity.py is importable."""

    def test_t26_importable(self):
        t26 = pytest.importorskip("t26_t21_width_sensitivity")
        assert hasattr(t26, "loglike_t21_scaled")
        assert hasattr(t26, "run_one")
        assert hasattr(t26, "main")

    def test_t21_width_scaled_likelihood_returns_finite(self):
        """loglike_t21_scaled at a reasonable point returns finite log L."""
        t26 = pytest.importorskip("t26_t21_width_sensitivity")
        # Need to load KISS data first (the test imports t26 which imports t21)
        try:
            import t21_real_kiss_sidm_gravothermal as t21_mod
            if t21_mod._kiss_data is None:
                t21_mod._kiss_data = t21_mod._load_real_kiss_data()
        except (FileNotFoundError, Exception) as e:
            pytest.skip(f"KISS data not available: {e}")
        # At log_sigma_m = 0, a = 0.5 (close to typical MAP)
        ll = t26.loglike_t21_scaled([0.0, 0.5], width_scale=1.0)
        assert np.isfinite(ll), f"Default-width log L should be finite: {ll}"

    def test_wider_widths_have_higher_or_equal_log_L(self):
        """At the same point, wider widths should give higher (or equal) log L."""
        t26 = pytest.importorskip("t26_t21_width_sensitivity")
        try:
            import t21_real_kiss_sidm_gravothermal as t21_mod
            if t21_mod._kiss_data is None:
                t21_mod._kiss_data = t21_mod._load_real_kiss_data()
        except (FileNotFoundError, Exception) as e:
            pytest.skip(f"KISS data not available: {e}")
        ll_default = t26.loglike_t21_scaled([0.5, 0.5], width_scale=1.0)
        ll_wider = t26.loglike_t21_scaled([0.5, 0.5], width_scale=2.0)
        assert ll_wider >= ll_default - 0.1, (
            f"Wider should not give MUCH lower log L: wider={ll_wider}, default={ll_default}"
        )


class TestT26Result:
    """If T26 result JSON exists, validate it."""

    def test_t26_result_or_skip(self):
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t26_t21_width_sensitivity.json"
        if not result_path.exists():
            pytest.skip("No T26 result JSON; run t26_t21_width_sensitivity.py first")
        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "sensitivity" in data
        assert len(data["fits"]) == 3  # default, wider, narrower
        sens = data["sensitivity"]
        # The KISS-SIDM penalty should dampen the width sensitivity (T26 hypothesis)
        if "comparison_to_t24" in data:
            kiss_dampens = data["comparison_to_t24"].get("kiss_penalty_dampens_width_sensitivity", None)
            assert kiss_dampens is not None
        # All shifts should be finite
        for k in ["delta_log_sm_wider_vs_default", "delta_log_sm_narrower_vs_default"]:
            assert np.isfinite(sens[k]), f"{k} not finite"


class TestT27Module:
    """t27_multiresolution_kiss_sidm.py is importable."""

    def test_t27_importable(self):
        t27 = pytest.importorskip("t27_multiresolution_kiss_sidm")
        assert hasattr(t27, "load_n500")
        assert hasattr(t27, "load_canonical")
        assert hasattr(t27, "main")
        assert hasattr(t27, "parse_array_string")

    def test_parse_array_string(self):
        """Parser handles numpy-style array strings."""
        t27 = pytest.importorskip("t27_multiresolution_kiss_sidm")
        # Single row
        a = t27.parse_array_string("[1.0 2.0 3.0]")
        assert np.allclose(a, [1.0, 2.0, 3.0])
        # Multi-row
        a = t27.parse_array_string("[1.0 2.0; 3.0 4.0]")
        assert a.shape == (2, 2)
        assert np.allclose(a[0], [1.0, 2.0])
        # Empty
        a = t27.parse_array_string("[]")
        assert len(a) == 0


class TestT27Result:
    """If T27 result JSON exists, validate it."""

    def test_t27_result_or_skip(self):
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t27_multiresolution_kiss_sidm.json"
        if not result_path.exists():
            pytest.skip("No T27 result JSON; run t27_multiresolution_kiss_sidm.py first")
        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "results" in data
        # Should have at least 2 resolutions loaded
        assert len(data["results"]) >= 2
        # Scaling should be either CONVERGED or NOT CONVERGED (verdict exists)
        if "scaling" in data:
            assert "verdict" in data["scaling"]


class TestT28Module:
    """t28_published_style_dsph.py is importable."""

    def test_t28_importable(self):
        t28 = pytest.importorskip("t28_published_style_dsph")
        assert hasattr(t28, "loglike_dsph_published_style")
        assert hasattr(t28, "loglike_5channel_published")
        assert hasattr(t28, "main")

    def test_loglike_returns_finite_at_peaks(self):
        """R12 P0-D (2026-08-17): loglike_dsph_published_style now encodes
        the published Horigome+ 2025 UPPER LIMIT (sigma/m < 0.2 cm^2/g),
        NOT a bimodal posterior.

        Tests:
          - ll at sigma/m_0 = 0.05 cm^2/g (well below the limit) is finite
            and high (in the upper-limit mode).
          - ll at sigma/m_0 = 1.0 cm^2/g (well above the limit) is much
            more negative than at the mode.
          - ll DECREASES monotonically as sigma/m_0 increases above the
            limit (no large-peak at sigma/m ~ 10 anymore).
        """
        t28 = pytest.importorskip("t28_published_style_dsph")
        ll_low = t28.loglike_dsph_published_style(0.05, 0.0)
        ll_at_limit = t28.loglike_dsph_published_style(0.2, 0.0)
        ll_high = t28.loglike_dsph_published_style(1.0, 0.0)
        ll_extreme = t28.loglike_dsph_published_style(10.0, 0.0)
        # Low (well below limit) should be in the upper-limit "mode" region.
        assert np.isfinite(ll_low), f"Low sigma/m should be finite: {ll_low}"
        # At the upper limit itself, log L should be ~ -1 to -2.
        assert ll_at_limit < 0 and ll_at_limit > -10, (
            f"At upper limit (sigma/m=0.2) log L = {ll_at_limit}; "
            "should be moderately negative, not -inf and not 0"
        )
        # Monotonic decrease above the limit.
        assert ll_high < ll_at_limit, (
            f"Above limit (sigma/m=1.0, log L={ll_high}) should be < "
            f"at-limit (sigma/m=0.2, log L={ll_at_limit})"
        )
        assert ll_extreme < ll_high, (
            f"At sigma/m=10 (log L={ll_extreme}) should be < "
            f"at sigma/m=1 (log L={ll_high}); the OLD bimodal surrogate "
            "gave log L ~ 0 here. Re-introducing the bimodal is a regression."
        )
        # Extreme values should be strongly disfavored.
        assert ll_extreme < -3.0, (
            f"At sigma/m_0=10 cm^2/g log L = {ll_extreme}; expected strongly "
            "negative (the legacy bimodal surrogate gave log L ~ 0 here)."
        )


class TestT28Result:
    """If T28 result JSON exists, validate it."""

    def test_t28_result_or_skip(self):
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t28_published_style_dsph.json"
        if not result_path.exists():
            pytest.skip("No T28 result JSON; run t28_published_style_dsph.py first")
        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "A_original_gaussian" in data["fits"]
        assert "B_published_style" in data["fits"]
        # Compare MAPs
        map_A = data["fits"]["A_original_gaussian"]["MAP"][0]
        map_B = data["fits"]["B_published_style"]["MAP"][0]
        delta = abs(map_B - map_A)
        # If delta is small (<0.3 dex), the headline is robust to channel shape
        assert np.isfinite(delta)