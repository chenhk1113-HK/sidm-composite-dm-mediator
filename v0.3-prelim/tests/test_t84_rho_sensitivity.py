"""Tests for T84 — Channel 18 ρ_abundance sensitivity sweep.

These tests verify that t84_lss_rho_sensitivity.py produces
defensible results across the rho_abundance grid and exposes
the right scalar summary statistics.

Specific invariants:
1. Output JSON contains rho_grid, per_rho, delta_loglike_vs_fiducial,
   bias_at_v07_map, summary, sweep_metadata keys.
2. For each rho point, predicted_bias at v0.7 MAP σ/m (= 0.27) is
   consistent with the formula b_pred[i] = 1 + s * rho * (b_obs[i] - 1).
3. Best-fit σ/m across all rho points is in [0.3, 3] (physical SIDM range).
4. The "sensitivity claim" — best-fit σ/m spread < 0.5 cm²/g over
   ρ ∈ [0.7, 1.0] — is quantified (the T74 doc claimed this; we test
   it as a derivable claim, not a hardcoded True).
5. The |Δlog Z| between (rho=1.0) and (rho=0.7) is what's important.
   We assert it's logged honestly in the JSON, regardless of size.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

# Add v0.3-prelim/code and t84 module to import path
_CODE_DIR = Path(__file__).resolve().parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))

from zhang_lss_channel import (
    ZHANG_TABLE_2,
    LOG_M_H_DWARF_MEDIAN,
    predicted_relative_bias,
    best_fit_sigma_over_m,
)
import t84_lss_rho_sensitivity as t84


RESULTS_DIR = _CODE_DIR.parent / "data/results/2026-09-03_t84_rho_sensitivity"
RESULTS_JSON = RESULTS_DIR / "t84_rho_sweep.json"


class TestRhoGridStructure:
    """Verify the rho_grid and summary structure are well-formed."""

    def test_rho_grid_in_expected_range(self):
        # 0.5 to 1.0 inclusive, 11 points
        assert t84.RHO_GRID[0] == 0.5
        assert t84.RHO_GRID[-1] == 1.0
        assert len(t84.RHO_GRID) == 11

    def test_fiducial_rho_is_zero_delta_baseline(self):
        assert t84.RHO_FIDUCIAL == 0.85
        assert t84.RHO_FIDUCIAL in t84.RHO_GRID

    def test_sigma_grid_eval_has_logspace_coverage(self):
        # 30 points in [0.001, 1] + 15 points in [1, ~30] = 45 total
        sg = t84.SIGMA_GRID_EVAL
        assert len(sg) == 45
        assert sg[0] < 0.01  # covers CDM-like regime
        assert sg[-1] > 10   # covers core-collapse regime


class TestBestFitInvarianceToRho:
    """The grid-search's best-fit σ/m should be invariant (or near-invariant)
    under changes in ρ, since the anti-correlation template is fixed.
    The T74 doc claims sensitivity < 0.5 cm²/g over ρ ∈ [0.7, 1.0]."""

    def test_bf_sigma_in_physical_range_for_all_rho(self):
        for rho in t84.RHO_GRID:
            bf_sigma, _ = best_fit_sigma_over_m(rho_abundance=float(rho))
            assert 0.3 <= bf_sigma <= 3.0, (
                f"ρ={rho}: best-fit σ/m = {bf_sigma:.3f} out of [0.3, 3]"
            )

    def test_bf_sigma_spread_over_hp_range_small(self):
        # Headline: ρ ∈ [0.7, 1.0] should produce σ/m within Δ0.5 cm²/g
        sigmas_hp = [
            best_fit_sigma_over_m(rho_abundance=float(r))[0]
            for r in t84.RHO_GRID if 0.7 <= r <= 1.0
        ]
        spread = max(sigmas_hp) - min(sigmas_hp)
        assert spread < 0.5, (
            f"Best-fit σ/m spread over ρ ∈ [0.7, 1.0] is {spread:.3f}; "
            f"too large per T74 doc claim."
        )


class TestLogLikeScalesWithRho:
    """At the best-fit σ/m, the chi² sum scales with ρ² because
    b_pred ∝ ρ at that point. So Δlog Z between low and high ρ
    can be large even if best-fit σ/m is invariant."""

    def test_log_at_fiducial_is_above_low_rho(self):
        ll_05, ll_100 = None, None
        for rho in t84.RHO_GRID:
            _, ll = best_fit_sigma_over_m(rho_abundance=float(rho))
            if abs(rho - 0.5) < 1e-9:
                ll_05 = ll
            elif abs(rho - 1.0) < 1e-9:
                ll_100 = ll
        assert ll_05 is not None and ll_100 is not None
        # ρ=1.0 should give higher likelihood than ρ=0.5 (more ant-corr strength)
        assert ll_100 > ll_05
        delta = ll_100 - ll_05
        assert delta > 1.0, (
            f"Δlog L between ρ=1.0 and ρ=0.5 is only {delta:.2f}; "
            f"expected > 1 (channel contributes more at higher ρ)"
        )


class TestBiasAtV07Map:
    """At the v0.7 MAP σ/m (= 0.27), the predicted b_rel vector should
    scale linearly with ρ. Test against the formula."""

    def test_b_pred_at_v07_map_matches_formula(self):
        # For σ/m = 0.27 cm²/g, the saturation factor s = 1 - exp(-0.27/1.0)
        # ≈ 0.236; b_pred[i] = 1 + s * ρ * (b_obs[i] - 1)
        sv = 0.27
        s_factor = 1.0 - math.exp(-sv / 1.0)
        b_obs = ZHANG_TABLE_2[:, 2]
        for rho in t84.RHO_GRID:
            b_pred = predicted_relative_bias(
                sigma_over_m_cm2_per_g=sv,
                log_M_h_Msun=LOG_M_H_DWARF_MEDIAN,
                rho_abundance=float(rho),
            )
            # The formula gives b_pred[i] = 1 + s * ρ * (b_obs[i] - 1)
            # for the diffusion bin (i=0), before clamping
            expected = 1.0 + s_factor * rho * (b_obs[0] - 1.0)
            # Clamped to [0.5, 2.5]
            expected_clamped = max(0.5, min(2.5, expected))
            assert math.isclose(b_pred[0], expected_clamped, abs_tol=1e-3), (
                f"ρ={rho}: b_pred[0] = {b_pred[0]:.3f}, "
                f"expected ~{expected_clamped:.3f} (formula = {expected:.3f})"
            )


class TestSweepOutputJSON:
    """Verify the JSON written by main() has the expected schema."""

    @classmethod
    def setup_class(cls):
        # Run the sweep if not already done
        if not RESULTS_JSON.exists():
            t84.main()
        with open(RESULTS_JSON, encoding="utf-8") as f:
            cls.sweep = json.load(f)

    def test_json_has_required_keys(self):
        for key in (
            "rho_grid", "rho_fiducial", "per_rho",
            "delta_loglike_vs_fiducial", "bias_at_v07_map", "summary",
            "sweep_metadata",
        ):
            assert key in self.sweep, f"Missing key: {key}"

    def test_per_rho_length_matches_grid(self):
        assert len(self.sweep["per_rho"]) == len(self.sweep["rho_grid"])
        assert len(self.sweep["delta_loglike_vs_fiducial"]) == len(self.sweep["rho_grid"])
        assert len(self.sweep["bias_at_v07_map"]) == len(self.sweep["rho_grid"])

    def test_summary_keys_present(self):
        for key in (
            "best_fit_sigma_min_cm2_per_g",
            "best_fit_sigma_max_cm2_per_g",
            "best_fit_sigma_spread_full_cm2_per_g",
            "best_fit_sigma_spread_hp_cm2_per_g",
            "max_abs_delta_loglike_vs_fiducial",
            "sensitivity_claim_verified",
        ):
            assert key in self.sweep["summary"]

    def test_fiducial_delta_loglike_is_zero(self):
        for entry in self.sweep["delta_loglike_vs_fiducial"]:
            if abs(entry["rho_abundance"] - 0.85) < 1e-9:
                assert abs(entry["delta_loglike"]) < 1e-9, (
                    f"Delta at fiducial should be 0, got {entry['delta_loglike']}"
                )

    def test_bias_pred_scales_with_rho(self):
        # b_pred at higher rho should be more extreme (further from 1)
        b_at_05 = None
        b_at_10 = None
        for entry in self.sweep["bias_at_v07_map"]:
            if abs(entry["rho_abundance"] - 0.50) < 1e-9:
                b_at_05 = entry["b_pred_at_v07_map"][0]
            elif abs(entry["rho_abundance"] - 1.00) < 1e-9:
                b_at_10 = entry["b_pred_at_v07_map"][0]
        assert b_at_05 is not None and b_at_10 is not None
        # b_pred diffuse bin should be larger at rho=1.0 than at rho=0.5
        assert b_at_10 > b_at_05, (
            f"b_pred at ρ=1.0 ({b_at_10}) should exceed at ρ=0.5 ({b_at_05})"
        )


class TestSensitivityInterpretation:
    """Honest tests for what the sensitivity study reveals."""

    def test_log_z_swing_substantial(self):
        # If the max |Δlog Z| is large, the channel is informative
        # (slope of log L w.r.t. ρ is real, not a numerical artifact)
        if not RESULTS_JSON.exists():
            t84.main()
        with open(RESULTS_JSON, encoding="utf-8") as f:
            sweep = json.load(f)
        max_abs = sweep["summary"]["max_abs_delta_loglike_vs_fiducial"]
        # Should be substantial (>1). If near 0, the channel is degenerate
        # in ρ, which would actually falsify the sensitivity claim entirely.
        assert max_abs > 1.0, (
            f"Max |Δlog Z| = {max_abs:.3f} is too small; "
            f"channel may be degenerate in ρ, contradicting T74 doc assumption."
        )

    def test_bf_sigma_invariant_under_rho_holds(self):
        """The T74 doc claim — best-fit σ/m in [0.7, 1.0] is invariant —
        is what we test here. Even if log Z varies a lot with ρ,
        best-fit σ/m should hold steady."""
        if not RESULTS_JSON.exists():
            t84.main()
        with open(RESULTS_JSON, encoding="utf-8") as f:
            sweep = json.load(f)
        spread_hp = sweep["summary"]["best_fit_sigma_spread_hp_cm2_per_g"]
        assert spread_hp < 0.5, (
            f"Best-fit σ/m spread over ρ ∈ [0.7, 1.0] = {spread_hp:.3f} cm²/g; "
            f"should be < 0.5 per T74 doc claim"
        )


if __name__ == "__main__":
    import inspect
    fns = [
        (n, f) for n, f in globals().items()
        if inspect.isfunction(f) and n.startswith("test_")
    ]
    for name, fn in fns:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
    print(f"\nRan {len(fns)} tests.")
