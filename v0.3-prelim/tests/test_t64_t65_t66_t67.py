"""
Tests for T64-T67 (manuscript revisions).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T64_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t64_uncertainty_quantification.py"
T65_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t65_slope_mitigation.py"
T66_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t66_uv_caveat.py"
T67_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t67_comparison_table.py"
T64_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t64_uncertainty_quantification.json"
T67_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t67_comparison_table.json"


class TestT64Uncertainty:
    """T64 — Uncertainty quantification."""

    def test_t64_importable(self):
        t64 = pytest.importorskip("t64_uncertainty_quantification")
        assert hasattr(t64, "compute_uncertainty")

    def test_t64_combined_uncertainty_positive(self):
        """Combined upper and lower bounds should both be positive."""
        if not T64_RESULT.exists():
            pytest.skip("T64 not yet completed")
        with open(T64_RESULT) as f:
            d = json.load(f)
        u = d["uncertainty"]
        assert u["combined_upper"] > 0
        assert u["combined_lower"] > 0


class TestT65SlopeMitigation:
    """T65 — Slope mitigation."""

    def test_t65_importable(self):
        t65 = pytest.importorskip("t65_slope_mitigation")
        assert hasattr(t65, "sigma_m_mixed")
        assert hasattr(t65, "sigma_m_multi_med")


class TestT66UVCaveat:
    """T66 — UV caveat."""

    def test_t66_importable(self):
        t66 = pytest.importorskip("t66_uv_caveat")
        assert hasattr(t66, "heavy_quark_limit_check")
        assert hasattr(t66, "LITERATURE")

    def test_t66_t54_in_heavy_quark_regime(self):
        """T54 has m_q >> Lambda_dark, so should be heavy-quark regime."""
        t66 = pytest.importorskip("t66_uv_caveat")
        r = t66.heavy_quark_limit_check(0.021, 0.000150)
        assert r["heavy_quark_regime"] is True


class TestT67Comparison:
    """T67 — Comparison table."""

    def test_t67_importable(self):
        t67 = pytest.importorskip("t67_comparison_table")
        assert hasattr(t67, "main")

    def test_t67_table_has_required_keys(self):
        if not T67_RESULT.exists():
            pytest.skip("T67 not yet completed")
        with open(T67_RESULT) as f:
            d = json.load(f)
        # Should have the table
        assert "table" in d
        # Should have multiple categories
        keys = list(d["table"].keys())
        assert len(keys) >= 3