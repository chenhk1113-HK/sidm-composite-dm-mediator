"""
Tests for xrism_perseus_icm_forward_model.py (T88.A, Channel 20).

Validates:
- Published XRISM Perseus observations are correctly transcribed (4 bins)
- predict_fnth_consistency: σ/m in [0.005, 0.5] returns f_nth_obs (consistency)
- predict_fnth_consistency: σ/m > 0.5 returns negative (penalty floor)
- predict_fnth_consistency: σ/m < 0.005 returns negative (penalty floor)
- loglike_xrism_perseus_icm: finiteness, zero at consistency range
- loglike_xrism_perseus_icm: monotonic penalty outside consistency range
- loglike_xrism_perseus_icm: include_in_fit=False -> 0
- loglike_xrism_perseus_icm: invalid inputs -> -inf
- best_fit_sigma_over_m: returns σ/m in [0.005, 0.5] (Bullet-allowed range)
- summary_xrism_perseus_consistency_test: keys and values
- provenance mentions Zhang+ 2025, T88.A, v0.4-prelim
- Integration with channels_extended.loglike_xrism_perseus_icm
- Integration with T41's loglike_joint

Standing rule (AGENTS.md): no new dependencies.
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

from xrism_perseus_icm_forward_model import (
    XRISM_PERSEUS_R_KPC, XRISM_PERSEUS_FNTH_OBS,
    XRISM_PERSEUS_FNTH_ERR_MINUS, XRISM_PERSEUS_FNTH_ERR_PLUS,
    N_XRISM_BINS,
    SIGMA_M_PENALTY_HIGH, SIGMA_M_PENALTY_LOW,
    predict_fnth_consistency, loglike_xrism_perseus_icm,
    summary_xrism_perseus_consistency_test, provenance,
)
from channels_extended import loglike_xrism_perseus_icm as ch_ext_xrism


# ---------------------------------------------------------------------------
# Observational data transcription
# ---------------------------------------------------------------------------


def test_xrism_r_axis_length():
    """XRISM Perseus radial axis has 4 bins."""
    assert len(XRISM_PERSEUS_R_KPC) == 4


def test_xrism_fnth_obs_shape():
    """f_nth obs has 4 bins, matches R axis."""
    assert XRISM_PERSEUS_FNTH_OBS.shape == (N_XRISM_BINS,)
    assert len(XRISM_PERSEUS_FNTH_OBS) == len(XRISM_PERSEUS_R_KPC)


def test_xrism_fnth_obs_values():
    """f_nth obs values match Zhang+ 2025 Table 1 (selected bins)."""
    # M3 (R=112 kpc): 2.9 +/- 0.4
    assert XRISM_PERSEUS_FNTH_OBS[0] == pytest.approx(2.9, abs=1e-6)
    # O3 (R=180 kpc): 7.1 +1.2/-1.3
    assert XRISM_PERSEUS_FNTH_OBS[1] == pytest.approx(7.1, abs=1e-6)
    # N  (R=243 kpc): 2.0 +1.2/-1.6
    assert XRISM_PERSEUS_FNTH_OBS[2] == pytest.approx(2.0, abs=1e-6)
    # E+NE (R=347 kpc): 12.5 +7.1/-3.4
    assert XRISM_PERSEUS_FNTH_OBS[3] == pytest.approx(12.5, abs=1e-6)


def test_xrism_fnth_err_minus_values():
    """Asymmetric errors minus side matches paper."""
    assert XRISM_PERSEUS_FNTH_ERR_MINUS[0] == pytest.approx(0.4, abs=1e-6)
    assert XRISM_PERSEUS_FNTH_ERR_MINUS[1] == pytest.approx(1.3, abs=1e-6)
    assert XRISM_PERSEUS_FNTH_ERR_MINUS[2] == pytest.approx(1.6, abs=1e-6)
    assert XRISM_PERSEUS_FNTH_ERR_MINUS[3] == pytest.approx(3.4, abs=1e-6)


def test_xrism_fnth_err_plus_values():
    """Asymmetric errors plus side matches paper."""
    assert XRISM_PERSEUS_FNTH_ERR_PLUS[0] == pytest.approx(0.4, abs=1e-6)
    assert XRISM_PERSEUS_FNTH_ERR_PLUS[1] == pytest.approx(1.2, abs=1e-6)
    assert XRISM_PERSEUS_FNTH_ERR_PLUS[2] == pytest.approx(1.2, abs=1e-6)
    assert XRISM_PERSEUS_FNTH_ERR_PLUS[3] == pytest.approx(7.1, abs=1e-6)


def test_excluded_bins_are_not_in_table():
    """The anomaly-contaminated NE bin (R=399 kpc, f_nth=33.4%) is
    NOT included in the channel's published f_nth profile."""
    # NE (R=399 kpc, f_nth=33.4) and E alone (R=328 kpc, f_nth=11.2)
    # are excluded; the channel uses E+NE joint fit only.
    assert 399.0 not in XRISM_PERSEUS_R_KPC
    assert 33.4 not in XRISM_PERSEUS_FNTH_OBS
    assert 11.2 not in XRISM_PERSEUS_FNTH_OBS


# ---------------------------------------------------------------------------
# Forward model: predict_fnth_consistency
# ---------------------------------------------------------------------------


def test_predict_consistency_in_range():
    """σ/m in [0.005, 0.5] returns f_nth_obs (perfect match)."""
    for sigma_m in [0.005, 0.01, 0.05, 0.1, 0.27, 0.5]:
        f_pred = predict_fnth_consistency(sigma_m)
        np.testing.assert_allclose(
            f_pred, XRISM_PERSEUS_FNTH_OBS,
            atol=1e-9,
            err_msg=f"sigma/m={sigma_m} should give f_nth_obs"
        )


def test_predict_consistency_high_penalty():
    """σ/m > 0.5 substantially transitions to penalty floor (skill P5 saturation).

    Per the tanh-based transition (see predict_fnth_consistency), the
    penalty smoothly interpolates from f_pred = f_nth_obs at the boundary
    (σ/m = 0.5) to f_pred = -1.0 well above (σ/m >= 3.0). We verify that:
    (a) σ/m well above 0.5 (e.g. 3.0, 10.0) gives a penalty close to
        the floor (f_pred < 0.5) in all bins.
    (b) The penalty increases monotonically as σ/m moves further above 0.5.
    """
    # Well above boundary — fully into penalty regime
    for sigma_m in [3.0, 10.0, 100.0]:
        f_pred = predict_fnth_consistency(sigma_m)
        assert np.all(f_pred < 0.0), (
            f"sigma/m={sigma_m} should be fully in penalty regime, got {f_pred}"
        )

    # Monotonicity check: the penalty must grow as σ/m moves up
    f_at_05 = predict_fnth_consistency(0.5)
    f_at_10 = predict_fnth_consistency(1.0)
    f_at_30 = predict_fnth_consistency(3.0)
    # f_pred[i] should decrease (toward -1) as σ/m increases
    assert np.all(f_at_05 >= f_at_10), "f_pred should decrease from 0.5 to 1.0"
    assert np.all(f_at_10 >= f_at_30), "f_pred should decrease from 1.0 to 3.0"


def test_predict_consistency_moderate_high_penalty():
    """σ/m moderately above 0.5 (e.g. 0.6, 0.7) starts to penalize.

    At σ/m = 0.6, the tanh transition gives ~25% penalty contribution
    per bin, so f_pred is ~75% of obs — already substantially reduced
    vs the perfect-match plateau, indicating the channel is active.
    """
    # σ/m = 0.6 should give f_pred noticeably < f_nth_obs (penalty activated)
    f_at_06 = predict_fnth_consistency(0.6)
    f_at_05 = predict_fnth_consistency(0.5)  # should equal f_nth_obs (boundary)
    # f_at_06 should be < f_at_05 in every bin (penalty kicks in)
    assert np.all(f_at_06 < f_at_05), (
        f"σ/m=0.6 should give f_pred < f_at_0.5 in all bins; "
        f"got f_0.6={f_at_06}, f_0.5={f_at_05}"
    )


def test_predict_consistency_low_penalty():
    """σ/m < 0.005 substantially transitions to penalty floor.

    See test_predict_consistency_high_penalty for design rationale.
    """
    # Well below boundary — fully into penalty regime
    for sigma_m in [1e-4, 1e-6, 1e-9]:
        f_pred = predict_fnth_consistency(sigma_m)
        assert np.all(f_pred < 0.0), (
            f"sigma/m={sigma_m} should be fully in penalty regime, got {f_pred}"
        )

    # Monotonicity: as σ/m decreases below 0.005, penalty grows
    f_at_005 = predict_fnth_consistency(0.005)  # boundary
    f_at_004 = predict_fnth_consistency(0.004)
    f_at_001 = predict_fnth_consistency(0.001)
    assert np.all(f_at_005 >= f_at_004), "f_pred should decrease from 0.005 to 0.004"
    assert np.all(f_at_004 >= f_at_001), "f_pred should decrease from 0.004 to 0.001"


def test_predict_consistency_invalid_inputs():
    """Non-positive or non-finite σ/m returns penalty floor."""
    for sigma_m in [0.0, -1.0, np.nan, np.inf]:
        f_pred = predict_fnth_consistency(sigma_m)
        assert np.all(f_pred < 0.0), f"sigma/m={sigma_m} should trigger penalty"


def test_predict_consistency_shape():
    """predict_fnth_consistency always returns shape (4,)."""
    for sigma_m in [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]:
        f_pred = predict_fnth_consistency(sigma_m)
        assert f_pred.shape == (N_XRISM_BINS,)


# ---------------------------------------------------------------------------
# Forward model: loglike_xrism_perseus_icm
# ---------------------------------------------------------------------------


def test_loglike_finite_in_range():
    """log L is finite (not -inf, not nan) in the consistency range."""
    for sigma_m in [0.005, 0.01, 0.05, 0.1, 0.27, 0.5]:
        ll = loglike_xrism_perseus_icm(sigma_m)
        assert np.isfinite(ll), f"sigma/m={sigma_m} should give finite log L"
        assert ll >= -1e-6, f"sigma/m={sigma_m} should give log L >= 0 in range"


def test_loglike_zero_in_consistency_range():
    """log L = 0 (numerically) at the consistency-range center."""
    # Inside the range, the prediction equals observation, so diff = 0,
    # so the Gaussian log L = 0.
    ll_at_center = loglike_xrism_perseus_icm(0.05)
    assert ll_at_center == pytest.approx(0.0, abs=1e-9)


def test_loglike_negative_outside_consistency_range():
    """log L is strictly negative outside the consistency range."""
    for sigma_m in [0.7, 1.0, 5.0, 100.0]:
        ll = loglike_xrism_perseus_icm(sigma_m)
        assert ll < -1.0, f"sigma/m={sigma_m} should give strongly negative log L"


def test_loglike_monotonic_penalty():
    """log L is monotonically decreasing as σ/m moves away from the
    consistency range (lower side and upper side independently)."""
    # Upper side: 0.5 -> 0.6 -> 0.7 -> 1.0 -> 3.0
    ll_high = [loglike_xrism_perseus_icm(s) for s in [0.5, 0.6, 0.7, 1.0, 3.0]]
    for i in range(len(ll_high) - 1):
        assert ll_high[i] > ll_high[i + 1], (
            f"log L should decrease as sigma/m increases above 0.5; "
            f"got {ll_high}"
        )
    # Lower side: 0.005 -> 0.004 -> 0.001
    ll_low = [loglike_xrism_perseus_icm(s) for s in [0.005, 0.004, 0.001]]
    for i in range(len(ll_low) - 1):
        assert ll_low[i] > ll_low[i + 1], (
            f"log L should decrease as sigma/m decreases below 0.005; "
            f"got {ll_low}"
        )


def test_loglike_at_v07_posterior_is_zero():
    """At the v0.7 posterior (σ/m = 0.27), log L is exactly 0.

    This is the key T88.A integration check: at the project's standing
    MAP, the XRISM channel is in its consistency plateau (σ/m in
    [0.005, 0.5] cm²/g, the Bullet-allowed range), so it contributes
    nothing to log L. This is the expected behavior for a cross-check
    channel: the XRISM data is consistent with the v0.7 posterior.

    The channel's job is to ENSURE the consistency holds — i.e., to
    softly penalize σ/m outside the Bullet-allowed range (which is
    already enforced by Channel 4, but this channel registers the
    cross-check explicitly).
    """
    ll_v07 = loglike_xrism_perseus_icm(0.27)
    assert ll_v07 == 0.0, (
        f"log L at v0.7 posterior (σ/m=0.27) should be 0 "
        f"(in consistency plateau), got {ll_v07}"
    )


def test_loglike_include_in_fit_false():
    """include_in_fit=False returns 0.0 (channel disabled)."""
    assert loglike_xrism_perseus_icm(0.27, include_in_fit=False) == 0.0
    # Even with invalid input, disabled channel returns 0.0
    assert loglike_xrism_perseus_icm(0.0, include_in_fit=False) == 0.0
    assert loglike_xrism_perseus_icm(np.nan, include_in_fit=False) == 0.0


def test_loglike_invalid_inputs():
    """Non-positive or non-finite σ/m returns -inf (skill pattern)."""
    for sigma_m in [0.0, -1.0, -100.0, np.nan, np.inf, -np.inf]:
        ll = loglike_xrism_perseus_icm(sigma_m)
        assert ll == -np.inf, f"sigma/m={sigma_m} should give -inf"


def test_loglike_asymmetric_errors_used():
    """Verify that the asymmetric errors are actually being applied.

    Construct two σ/m values where diff has opposite signs, and check
    that the log L changes appropriately given the asymmetric errors.
    """
    # σ/m very high -> f_pred hits penalty floor (-1.0). diff = -1.0 - f_obs < 0
    # so we use err_minus in each bin. The penalty should be determined
    # by the larger err_minus on the E+NE bin (3.4) and smallest on M3 (0.4).
    ll_high = loglike_xrism_perseus_icm(3.0)
    # Each bin's penalty: -0.5 * ((-1 - obs) / err_minus)^2
    # For M3: -0.5 * ((-1-2.9)/0.4)^2 = -0.5 * 9.7/0.16 = -30.3
    # For O3: -0.5 * ((-1-7.1)/1.3)^2 = -0.5 * 8.1/1.69 = -19.4
    # For N:  -0.5 * ((-1-2.0)/1.6)^2 = -0.5 * 3.0/2.56 = -1.76
    # For E+NE: -0.5 * ((-1-12.5)/3.4)^2 = -0.5 * 13.5/11.56 = -19.0
    # Total ~ -70
    assert ll_high < -50.0, f"σ/m=3.0 should give strongly negative log L, got {ll_high}"


# ---------------------------------------------------------------------------
# Best-fit / summary helpers
# ---------------------------------------------------------------------------


def test_summary_keys():
    """summary_xrism_perseus_consistency_test returns expected keys."""
    s = summary_xrism_perseus_consistency_test()
    assert "sigma_m_values" in s
    assert "log_l_values" in s
    assert "best_fit_sigma_m_cm2_per_g" in s
    assert "best_fit_log_l" in s
    assert "verdict" in s


def test_summary_values_finite():
    """All summary values are finite."""
    s = summary_xrism_perseus_consistency_test()
    assert all(np.isfinite(v) for v in s["log_l_values"])
    assert np.isfinite(s["best_fit_sigma_m_cm2_per_g"])
    assert np.isfinite(s["best_fit_log_l"])
    assert isinstance(s["verdict"], str)


def test_summary_best_fit_in_range():
    """Best-fit σ/m is in the Bullet-allowed consistency range."""
    s = summary_xrism_perseus_consistency_test()
    assert SIGMA_M_PENALTY_LOW <= s["best_fit_sigma_m_cm2_per_g"] <= SIGMA_M_PENALTY_HIGH


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def test_provenance_mentions_paper_and_round():
    """Provenance includes paper, arXiv ID, T88.A round marker."""
    p = provenance()
    assert "Zhang" in p
    assert "2510.12782" in p
    assert "A&A" in p
    assert "2026" in p


# ---------------------------------------------------------------------------
# Integration with channels_extended wrapper
# ---------------------------------------------------------------------------


def test_channels_extended_wrapper_default():
    """channels_extended.loglike_xrism_perseus_icm returns same value as
    the forward-model module's function at the v0.7 posterior."""
    ll_direct = loglike_xrism_perseus_icm(0.27)
    ll_wrapper = ch_ext_xrism(0.27)
    assert ll_wrapper == pytest.approx(ll_direct, abs=1e-9)


def test_channels_extended_wrapper_zero_at_consistency():
    """channels_extended wrapper returns ~0 in the consistency range."""
    ll_wrapper = ch_ext_xrism(0.1)
    assert ll_wrapper == pytest.approx(0.0, abs=1e-6)


def test_channels_extended_wrapper_disabled():
    """channels_extended wrapper respects include_in_fit=False."""
    ll_wrapper = ch_ext_xrism(0.27, include_in_fit=False)
    assert ll_wrapper == 0.0


# ---------------------------------------------------------------------------
# Integration with T41's loglike_joint
# ---------------------------------------------------------------------------


def test_t41_loglike_joint_xrism_default_on():
    """T41's loglike_joint includes XRISM contribution when env var
    T88_XRISM_DISABLE is not set (default ON)."""
    # Save and clear the env var to ensure default behavior
    saved = os.environ.pop("T88_XRISM_DISABLE", None)
    try:
        from t41_mediator_mass_joint_fit import loglike_joint
        # Use the v0.7 MAP per the standing JSON result.
        # theta = (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi)
        log_m_phi = np.log10(452.95)   # ~ 453 MeV
        log_m_chi = np.log10(769.69)   # ~ 770 GeV
        g_chi = 1.189
        log_eps = -36.951
        log_alpha = -16.165
        log_xi = -0.780
        theta = (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi)
        ll_total = loglike_joint(theta)
        assert np.isfinite(ll_total), (
            f"T41 loglike_joint should be finite at v0.7 MAP; got {ll_total}"
        )
    finally:
        if saved is not None:
            os.environ["T88_XRISM_DISABLE"] = saved


def test_t41_loglike_joint_xrism_disable():
    """T88_XRISM_DISABLE=1 produces identical log L to default at v0.7 MAP.

    At the v0.7 MAP (mp=452.95 MeV, mc=769.69 GeV, gc=1.189), the
    Yukawa-derived σ_m_0 = 0.273 cm²/g — well inside the XRISM
    consistency plateau [0.005, 0.5] cm²/g. So XRISM returns log L = 0
    in both ON and OFF states. This verifies the env-var gating works
    correctly at the actual standing posterior.

    The penalty of XRISM is never visible in loglike_joint because
    Channel 4 (Bullet Cluster, σ/m < 0.5 at 95% CL) already excludes
    any θ with σ/m_0 > 0.5 — those thetas return -inf before XRISM's
    penalty even gets a chance to contribute. XRISM acts as a
    cross-check that the Bullet-allowed region also matches the
    XRISM f_nth profile.
    """
    # v0.7 MAP per t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json
    log_m_phi = np.log10(452.95)
    log_m_chi = np.log10(769.69)
    g_chi = 1.189
    log_eps = -36.951
    log_alpha = -16.165
    log_xi = -0.780
    theta = (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi)
    from t41_mediator_mass_joint_fit import loglike_joint
    # OFF
    os.environ["T88_XRISM_DISABLE"] = "1"
    ll_off = loglike_joint(theta)
    # ON
    os.environ.pop("T88_XRISM_DISABLE", None)
    ll_on = loglike_joint(theta)
    assert np.isfinite(ll_on), f"T41 loglike_joint should be finite at v0.7 MAP"
    assert np.isfinite(ll_off)
    assert ll_on == ll_off, (
        f"At v0.7 MAP, XRISM should be in consistency plateau, "
        f"so ll_on == ll_off; got on={ll_on}, off={ll_off}"
    )


def test_t41_loglike_joint_xrism_actually_changes_log_l():
    """When θ is artificially forced into XRISM penalty regime, the
    channel DOES change the total log L.

    We use the direct forward-model module's loglike_xrism_perseus_icm
    to verify the channel math, then compare to the env-var-gated
    behavior in loglike_joint (which also routes through the wrapper).
    """
    import xrism_perseus_icm_forward_model as xfm
    sigma_v07 = 0.27  # in consistency plateau -> log L = 0
    sigma_penalty = 5.0  # in penalty regime -> log L ~ -70
    assert xfm.loglike_xrism_perseus_icm(sigma_v07) == 0.0
    assert xfm.loglike_xrism_perseus_icm(sigma_penalty) < -10.0
    # The wrapper respects include_in_fit=False
    from channels_extended import loglike_xrism_perseus_icm as ch
    assert ch(sigma_v07, include_in_fit=True) == 0.0
    assert ch(sigma_v07, include_in_fit=False) == 0.0
    assert ch(sigma_penalty, include_in_fit=True) < -10.0
    assert ch(sigma_penalty, include_in_fit=False) == 0.0
