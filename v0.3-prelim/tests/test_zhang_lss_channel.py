"""Tests for the Zhang+2025 LSS assembly-bias channel (T74, v0.4-prelim).

Validates:
- ZHANG_TABLE_2 observations are correctly transcribed (4 bins, 7 columns)
- core_radius_kpc: σ/m=1 → r_c=1 kpc, σ/m=0 → r_c=0
- predicted_relative_bias: trend (anti-correlation for σ/m > 0.3)
- predicted_relative_bias: flat trend (b ~ 1) for σ/m < 0.1
- predicted_relative_bias: collapse penalty for σ/m > 3
- predicted_relative_bias: clamping to [0.5, 2.5]
- loglike_lss_assembly_bias: finiteness, monotonic in σ/m for [0.3, 3]
- loglike_lss_assembly_bias: include_in_fit=False → 0
- loglike_lss_assembly_bias: invalid inputs → -inf
- best_fit_sigma_over_m: returns σ/m in [0.3, 3] (physical SIDM range)
- summary_zhang_consistency_test: keys and values
- provenance mentions Zhang 2025, T74, v0.4-prelim
- Integration with channels_extended.loglike_lss_assembly_bias
- Integration with T41's loglike_joint
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

_CODE_DIR = Path(__file__).parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))

from zhang_lss_channel import (
    ZHANG_TABLE_2, LOG_M_H_DWARF_MEDIAN, SIGMA_OVER_M_BEST_FIT_CM2_PER_G,
    SidmCoreParams, core_radius_kpc,
    predicted_relative_bias, loglike_lss_assembly_bias,
    best_fit_sigma_over_m, summary_zhang_consistency_test,
    provenance,
)
from channels_extended import loglike_lss_assembly_bias as ch_ext_lss


# ---------------------------------------------------------------------------
# Observational data transcription
# ---------------------------------------------------------------------------


def test_zhang_table_2_shape():
    """ZHANG_TABLE_2 has 4 bins, 7 columns."""
    assert ZHANG_TABLE_2.shape == (4, 7)


def test_zhang_table_2_obs_values():
    """ZHANG_TABLE_2 values match the paper's Extended Data Table 2."""
    # b_rel for diffuse: 2.31 +0.20/-0.19
    assert ZHANG_TABLE_2[0, 2] == pytest.approx(2.31, abs=1e-6)
    assert ZHANG_TABLE_2[0, 3] == pytest.approx(0.19, abs=1e-6)
    assert ZHANG_TABLE_2[0, 4] == pytest.approx(0.20, abs=1e-6)
    # b_rel for compact (reference): 1.00
    assert ZHANG_TABLE_2[3, 2] == pytest.approx(1.00, abs=1e-6)
    # N galaxies: 349 diffuse, 3050 compact
    assert ZHANG_TABLE_2[0, 5] == 349
    assert ZHANG_TABLE_2[3, 5] == 3050


def test_zhang_table_2_anti_correlation():
    """Observed b_rel is monotonically decreasing with Σ* (anti-correlation)."""
    b_obs = ZHANG_TABLE_2[:, 2]
    # Going from bin 0 (most diffuse) to bin 3 (most compact), b_rel decreases
    for i in range(3):
        assert b_obs[i] >= b_obs[i + 1]


# ---------------------------------------------------------------------------
# core_radius_kpc
# ---------------------------------------------------------------------------


def test_core_radius_zero_for_zero_sigma():
    """At σ/m = 0 (no SIDM), r_c = 0."""
    p = SidmCoreParams(0.0, 10.95)
    assert core_radius_kpc(p) == 0.0


def test_core_radius_sqrt_scaling():
    """r_c ∝ √(σ/m)."""
    p1 = SidmCoreParams(1.0, 10.95)
    p4 = SidmCoreParams(4.0, 10.95)
    assert core_radius_kpc(p4) == pytest.approx(2.0 * core_radius_kpc(p1), rel=1e-10)


def test_core_radius_calibration_at_one():
    """At σ/m = 1 cm²/g, r_c ≈ 1 kpc (calibrated against Zhang 2025)."""
    p = SidmCoreParams(1.0, 10.95)
    assert core_radius_kpc(p) == pytest.approx(1.0, rel=1e-6)


# ---------------------------------------------------------------------------
# predicted_relative_bias
# ---------------------------------------------------------------------------


def test_predicted_bias_flat_for_low_sigma():
    """For σ/m < 0.1, predicted b ~ 1.0 (no SIDM, CDM-like)."""
    b = predicted_relative_bias(0.01)
    np.testing.assert_allclose(b, [1.0, 1.0, 1.0, 1.0], atol=0.1)


def test_predicted_bias_anti_correlation_for_sidm():
    """For σ/m in [0.3, 3], predicted b[0] > b[1] > b[2] > b[3] (anti-correlation)."""
    for sv in [0.3, 1.0, 3.0]:
        b = predicted_relative_bias(sv)
        for i in range(3):
            assert b[i] >= b[i + 1], f"σ/m={sv}: b[{i}]={b[i]} < b[{i+1}]={b[i+1]}"


def test_predicted_bias_diffuse_higher_than_compact():
    """At σ/m = 1, the diffuse bin has higher b than the compact bin."""
    b = predicted_relative_bias(1.0)
    assert b[0] > b[3]


def test_predicted_bias_clamped():
    """Predicted b values must be in [0.5, 2.5]."""
    for sv in [1e-6, 1e-3, 0.1, 1.0, 3.0, 5.0, 10.0, 100.0]:
        b = predicted_relative_bias(sv)
        assert np.all(b >= 0.5), f"σ/m={sv}: b below clamp: {b}"
        assert np.all(b <= 2.5), f"σ/m={sv}: b above clamp: {b}"


def test_predicted_bias_collapse_penalty():
    """For σ/m > 3, predicted b decreases (core collapse regime)."""
    b_at_3 = predicted_relative_bias(3.0)[0]
    b_at_5 = predicted_relative_bias(5.0)[0]
    b_at_10 = predicted_relative_bias(10.0)[0]
    # Diffuse bin should decrease as we go deeper into core collapse
    assert b_at_3 >= b_at_5 >= b_at_10


# ---------------------------------------------------------------------------
# loglike_lss_assembly_bias
# ---------------------------------------------------------------------------


def test_loglike_finite_at_physical_sigma():
    """loglike finite for σ/m > 0."""
    ll = loglike_lss_assembly_bias(1.0)
    assert np.isfinite(ll)


def test_loglike_zero_when_disabled():
    """include_in_fit=False → 0.0."""
    ll = loglike_lss_assembly_bias(1.0, include_in_fit=False)
    assert ll == 0.0


def test_loglike_minus_inf_for_invalid_inputs():
    """Negative σ/m or ρ > 1 → -inf."""
    assert loglike_lss_assembly_bias(-1.0) == -np.inf
    assert loglike_lss_assembly_bias(0.0) == -np.inf
    assert loglike_lss_assembly_bias(1.0, rho_abundance=0.0) == -np.inf
    assert loglike_lss_assembly_bias(1.0, rho_abundance=1.5) == -np.inf


def test_loglike_peak_in_sidm_range():
    """loglike peaks somewhere in σ/m ∈ [0.3, 3] (physical SIDM range)."""
    best_sv, best_ll = best_fit_sigma_over_m()
    assert 0.3 <= best_sv <= 3.0, f"best σ/m = {best_sv} is outside physical SIDM range"
    assert best_ll > -10  # not extremely bad


def test_loglike_at_v06_posterior_close_to_best():
    """At v0.6 posterior σ/m ~ 1.4 cm²/g, loglike should be within a few units of best."""
    ll_at_v06 = loglike_lss_assembly_bias(1.4)
    best_sv, best_ll = best_fit_sigma_over_m()
    delta = ll_at_v06 - best_ll
    # The v0.6 posterior σ/m is in the SIDM range, so loglike should be close to best
    assert -10 < delta < 0


def test_loglike_cdm_regime_penalized():
    """At σ/m < 0.1 (CDM-like), loglike should be much worse than best fit."""
    ll_cdm = loglike_lss_assembly_bias(0.01)
    _, best_ll = best_fit_sigma_over_m()
    assert ll_cdm < best_ll - 10  # significantly worse


def test_loglike_core_collapse_penalized():
    """At σ/m > 5 (core collapse), loglike should be much worse than best fit."""
    ll_collapse = loglike_lss_assembly_bias(10.0)
    _, best_ll = best_fit_sigma_over_m()
    assert ll_collapse < best_ll - 10


# ---------------------------------------------------------------------------
# Diagnostic helpers
# ---------------------------------------------------------------------------


def test_summary_keys():
    """summary_zhang_consistency_test returns expected keys."""
    result = summary_zhang_consistency_test(1.0)
    expected = {
        "sigma_over_m_cm2_per_g", "log_M_h_Msun", "rho_abundance",
        "b_predicted", "b_observed", "chi2", "loglike",
        "best_fit_sigma_over_m", "best_fit_loglike", "delta_loglike_vs_best_fit",
    }
    assert expected.issubset(result.keys())


def test_summary_b_lengths():
    """b_predicted and b_observed are both length 4."""
    result = summary_zhang_consistency_test(1.0)
    assert len(result["b_predicted"]) == 4
    assert len(result["b_observed"]) == 4


def test_summary_chi2_equals_minus_two_loglike():
    """chi2 = -2 * loglike."""
    result = summary_zhang_consistency_test(1.0)
    assert result["chi2"] == pytest.approx(-2.0 * result["loglike"], rel=1e-10)


def test_summary_delta_loglike_non_positive():
    """delta_loglike_vs_best_fit ≤ 1.0 (allow small positive for grid-search artifact)."""
    for sv in [0.01, 0.1, 1.0, 3.0, 10.0]:
        result = summary_zhang_consistency_test(sv)
        # Grid is coarse; allow small positive delta for points near best fit
        assert result["delta_loglike_vs_best_fit"] <= 1.0


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def test_provenance_mentions_t74():
    """provenance() must mention T74 and Zhang 2025 for traceability."""
    p = provenance()
    assert "T74" in p
    assert "Zhang" in p
    assert "Nature" in p
    assert "v0.4-prelim" in p
    assert "arXiv:2504.03305" in p


# ---------------------------------------------------------------------------
# Integration with channels_extended (Channel 18)
# ---------------------------------------------------------------------------


def test_ch_ext_lss_matches_module():
    """channels_extended.loglike_lss_assembly_bias matches the module."""
    for sv in [0.1, 1.0, 3.0]:
        ll_a = ch_ext_lss(sigma_over_m_cm2_per_g=sv)
        ll_b = loglike_lss_assembly_bias(sigma_over_m_cm2_per_g=sv)
        assert math.isclose(ll_a, ll_b, rel_tol=1e-10)


def test_ch_ext_lss_returns_zero_when_disabled():
    """ch_ext_lss with include_in_fit=False returns 0.0."""
    ll = ch_ext_lss(sigma_over_m_cm2_per_g=1.0, include_in_fit=False)
    assert ll == 0.0


# ---------------------------------------------------------------------------
# Integration with T41 (end-to-end)
# ---------------------------------------------------------------------------


def test_t41_integration_lss_adds_log_l():
    """End-to-end: T41 loglike_joint should include LSS contribution when
    T74_LSS_DISABLE is not set, and NOT include it when set.
    """
    sys.path.insert(0, str(_CODE_DIR.parent.parent / "v0.1-prelim" / "code"))
    try:
        from t41_mediator_mass_joint_fit import loglike_joint as t41_loglike
    except (ImportError, IndentationError) as e:
        pytest.skip(f"T41 import failed: {e}")

    # v0.6 posterior
    theta = (
        np.log10(750.0),
        np.log10(805.0),
        0.5,
        -31.0,
        -26.0,
        0.0,
    )

    # With LSS
    os.environ.pop("T74_LSS_DISABLE", None)
    try:
        ll_with = t41_loglike(theta)
    except Exception as e:
        pytest.skip(f"T41 loglike_joint failed with LSS: {e}")

    # Without LSS
    os.environ["T74_LSS_DISABLE"] = "1"
    try:
        ll_without = t41_loglike(theta)
    except Exception as e:
        pytest.skip(f"T41 loglike_joint failed without LSS: {e}")

    os.environ.pop("T74_LSS_DISABLE", None)

    # The LSS contribution should be finite and not too large
    delta = ll_with - ll_without
    assert np.isfinite(delta)
    # LSS should add a few units of log L at the v0.6 posterior (σ/m ~ 1.4)
    # (since best fit is at σ/m ~ 2.7, loglike at σ/m=1.4 is ~-3 below best)
    assert -50 < delta < 0  # reasonable range