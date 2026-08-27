"""
Tests for T37 (Direction B closure: T22 BF with beta_seg at T29-MAP value).

D12 deliverable: re-run T22 2-comp-vs-1-comp Bayes factor with beta_seg
at the data-fitted T29-MAP value (0.899) instead of the hardcoded 0.25.
This test file enforces:
  - t37 script is importable
  - T37 result JSON exists
  - T37's 2-comp-vs-1-comp BF shifted by <2.5 units (the "robustness" verdict)
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


class TestT37Module:
    """t37_t22_with_fitted_beta_seg.py is importable."""

    def test_t37_importable(self):
        t37 = pytest.importorskip("t37_t22_with_fitted_beta_seg")
        # Imports + patching in main module
        assert hasattr(t37, "BETA_SEG_FITTED_MAP")
        assert hasattr(t37, "BETA_SEG_HARDCODED_DEFAULT")
        assert hasattr(t37, "patched_beta_seg")
        assert hasattr(t37, "main")
        # The patched two-component likelihood is built via patched_beta_seg
        # wrapping the underlying t22 module, so we don't expose
        # `loglike_two_comp_yang_real_kiss` as a top-level name. Verify
        # the actual public surface instead.
        assert hasattr(t37, "run_one"), "missing run_one entry point"

    def test_beta_seg_map_value(self):
        """T37 must lock beta_seg at the T29-MAP value (0.899)."""
        t37 = pytest.importorskip("t37_t22_with_fitted_beta_seg")
        assert t37.BETA_SEG_FITTED_MAP == pytest.approx(0.899, abs=1e-6), (
            f"BETA_SEG_FITTED_MAP = {t37.BETA_SEG_FITTED_MAP}, expected 0.899 (T29-MAP)"
        )
        assert t37.BETA_SEG_HARDCODED_DEFAULT == pytest.approx(0.25, abs=1e-6)

    def test_patched_beta_seg_roundtrip(self):
        """patched_beta_seg should set+restore the module-level constant."""
        t37 = pytest.importorskip("t37_t22_with_fitted_beta_seg")
        import two_component_sidm as tcs
        original = tcs.SEGREGATION_BETA
        with t37.patched_beta_seg(0.5):
            assert tcs.SEGREGATION_BETA == 0.5
        assert tcs.SEGREGATION_BETA == original


class TestT37Result:
    """If T37 result JSON exists, validate it."""

    def test_t37_result_or_skip(self):
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t37_t22_with_fitted_beta_seg.json"
        if not result_path.exists():
            pytest.skip("No T37 result JSON; run t37 first")
        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "bayes_factors_t37" in data
        assert "comparison_to_t22" in data
        # All 3 fits must exist
        assert "A_two_comp_beta0899_with_imfp" in data["fits"]
        assert "B_two_comp_beta0899_no_imfp" in data["fits"]
        assert "C_one_comp_nested_with_imfp" in data["fits"]

    def test_t37_headline_bf_shift_below_threshold(self):
        """Robustness criterion: |BF shift| < 2.5 means the verdict is robust."""
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t37_t22_with_fitted_beta_seg.json"
        if not result_path.exists():
            pytest.skip("No T37 result JSON")
        with open(result_path) as f:
            data = json.load(f)
        shift_imfp = data["comparison_to_t22"].get("t37_delta_A_C_minus_t22_delta_A_C")
        shift_no_imfp = data["comparison_to_t22"].get("t37_delta_B_C_minus_t22_delta_B_C")
        if shift_imfp is None or shift_no_imfp is None:
            pytest.skip("Comparison skipped (T22 baseline JSON missing)")
        # Headline verdict: is the 2-comp-vs-1-comp BF robust to beta_seg?
        max_shift = max(abs(shift_imfp), abs(shift_no_imfp))
        assert max_shift < 2.5, (
            f"|BF shift| = {max_shift:.3f} > 2.5 -- the 2-comp-vs-1-comp verdict "
            f"depends on beta_seg choice. This is the publishable 'beta_seg is a "
            f"missing hyperparameter' finding."
        )
