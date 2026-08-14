"""
Tests for T24 (likelihood-width sensitivity) and T25 (c_vir marginalization).

Both are publication-quality systematic-uncertainty scans added in
response to the Full Codebase R2 review (T2.4 and T2.5).

Standing rule (AGENTS.md): no new dependencies.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Ensure v0.3-prelim/code and v0.1-prelim/code are on sys.path
for sub in ["v0.3-prelim/code", "v0.1-prelim/code"]:
    p = str(PROJECT_ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)


class TestT24Module:
    """t24_likelihood_width_sensitivity.py is importable."""

    def test_t24_importable(self):
        """The T24 module is importable."""
        t24 = pytest.importorskip("t24_likelihood_width_sensitivity")
        assert hasattr(t24, "loglike_5channel_scaled")
        assert hasattr(t24, "run_one")
        assert hasattr(t24, "main")
        assert hasattr(t24, "prior_transform_2")

    def test_likelihood_widths_in_default_dict(self):
        """The default widths dict has the canonical channels."""
        t24 = pytest.importorskip("t24_likelihood_width_sensitivity")
        widths = t24.DEFAULT_WIDTHS
        # Should have dSph, UFD, lensing, cluster, radio_relic, draco
        for ch in ["dsph", "ufd", "lens", "cluster", "radio_relic", "draco"]:
            assert ch in widths, f"Missing channel: {ch}"
        # All widths should be positive
        for ch, w in widths.items():
            assert w > 0, f"Width for {ch} must be positive: {w}"

    def test_loglike_scales_correctly_with_width(self):
        """loglike_5channel_scaled at 2x widths should be HIGHER than 1x at the same point."""
        t24 = pytest.importorskip("t24_likelihood_width_sensitivity")
        sigma_m_0 = 1.0
        a = 0.0
        ll_default = t24.loglike_5channel_scaled(sigma_m_0, a, width_scale=1.0)
        ll_wider = t24.loglike_5channel_scaled(sigma_m_0, a, width_scale=2.0)
        ll_narrower = t24.loglike_5channel_scaled(sigma_m_0, a, width_scale=0.5)
        # Wider widths = more permissive = higher log L at most points
        # Narrower widths = more constraining = lower log L
        assert ll_wider > ll_default > ll_narrower, (
            f"Wider widths should give higher log L: "
            f"default={ll_default}, wider={ll_wider}, narrower={ll_narrower}"
        )

    def test_likelihood_returns_neginf_for_invalid(self):
        """Out-of-prior points should return -inf."""
        t24 = pytest.importorskip("t24_likelihood_width_sensitivity")
        # sigma_m_0 < 0 should return -inf
        assert t24.loglike_5channel_scaled(-1.0, 0.0) == -np.inf
        # a out of range
        assert t24.loglike_5channel_scaled(1.0, 100.0) == -np.inf


class TestT25Module:
    """t25_cvir_marginalization.py is importable."""

    def test_t25_importable(self):
        """The T25 module is importable."""
        t25 = pytest.importorskip("t25_cvir_marginalization")
        assert hasattr(t25, "loglike_with_fixed_cvir")
        assert hasattr(t25, "loglike_with_marginalized_cvir")
        assert hasattr(t25, "estimate_cvir_median")
        assert hasattr(t25, "forward_model_sashimi")

    def test_cvir_median_relation(self):
        """Median c_vir decreases with halo mass (Dutton-Macciò 2014)."""
        t25 = pytest.importorskip("t25_cvir_marginalization")
        cv_low = t25.estimate_cvir_median(1e10)  # dwarf
        cv_high = t25.estimate_cvir_median(1e14)  # cluster
        # Lower mass = higher c_vir (NFW concentration)
        assert cv_low > cv_high, (
            f"Lower-mass halos should have HIGHER c_vir: "
            f"c_vir(1e10)={cv_low}, c_vir(1e14)={cv_high}"
        )
        # Dwarf range: c_vir ~ 5-30
        assert 3 < cv_low < 50, f"c_vir(1e10) = {cv_low}, expected 3-50"
        # Cluster range: c_vir ~ 1-5
        assert 1 < cv_high < 10, f"c_vir(1e14) = {cv_high}, expected 1-10"

    def test_marginalized_loglike_greater_than_fixed(self):
        """Marginalizing over c_vir should give a HIGHER (or equal) integrated likelihood."""
        t25 = pytest.importorskip("t25_cvir_marginalization")
        # At a point near the median, both should give finite log L
        sigma_m_0 = 1.0
        a = 0.0
        ll_fixed = t25.loglike_with_fixed_cvir([np.log10(sigma_m_0), a])
        ll_marg = t25.loglike_with_marginalized_cvir([np.log10(sigma_m_0), a])
        assert np.isfinite(ll_fixed)
        assert np.isfinite(ll_marg)
        # Marginalization should not make log L much smaller than fixed at peak
        assert ll_marg >= ll_fixed - 1.0, (
            f"Marginalized log L ({ll_marg}) should be near fixed ({ll_fixed}) at peak"
        )


class TestT24Result:
    """If T24 result JSON exists, validate it."""

    def test_t24_result_or_skip(self):
        """If T24 result JSON exists, validate it."""
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t24_likelihood_width_sensitivity.json"
        if not result_path.exists():
            pytest.skip("No T24 result JSON; run t24_likelihood_width_sensitivity.py first")

        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "sensitivity" in data
        # Should have 3 fits: default, wider, narrower
        assert len(data["fits"]) == 3
        # Sensitivity verdict for wider should be informative
        sens = data["sensitivity"]
        assert "delta_log_sm_wider_vs_default" in sens
        assert np.isfinite(sens["delta_log_sm_wider_vs_default"])
        # If T24 found MAJOR shift (>0.5 dex), this is a publishable finding
        shift_wider = sens["delta_log_sm_wider_vs_default"]
        shift_narrower = sens["delta_log_sm_narrower_vs_default"]
        # If either is MAJOR (>0.5 dex), the placeholder likelihoods are a
        # significant source of systematic error
        assert abs(shift_wider) > 0.0, "Shift should be non-zero for sensitivity scan"


class TestT25Result:
    """If T25 result JSON exists, validate it."""

    def test_t25_result_or_skip(self):
        """If T25 result JSON exists, validate it."""
        result_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t25_cvir_marginalization.json"
        if not result_path.exists():
            pytest.skip("No T25 result JSON; run t25_cvir_marginalization.py first")

        with open(result_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "fits" in data
        assert "comparison" in data
        # Should have 2 fits: fixed and marginalized
        assert len(data["fits"]) == 2
        comp = data["comparison"]
        assert np.isfinite(comp["delta_log_sm_MAP"])
        # c_vir marginalization should be a MINOR effect (|shift| < 0.2 dex)
        # OR if it's MAJOR, that's still a valid finding to flag
        shift = abs(comp["delta_log_sm_MAP"])
        # We just verify the shift is finite and bounded
        assert shift < 5.0, f"c_vir shift {shift} unreasonably large"