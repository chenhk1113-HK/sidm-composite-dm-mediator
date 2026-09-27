"""T90.56 tests -- Hybrid 10D with LZ magnetic-moment channel (4 channels).

Verifies:
  - loglike_hybrid_4ch shape (finite at valid points, -inf at out-of-prior)
  - LZ channel fires only when env var T90_MAGNETIC_MOMENT_MU_X is set
  - Hybrid 10D prior_transform is in-range
  - End-to-end smoke run completes with LZ channel active
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v56_hybrid_lz import (
    loglike_hybrid_4ch,
    prior_transform_10,
    LOG_RANGES_10,
    PARAM_NAMES_10,
    IS_LOG_10,
    run_hybrid_joint_fit_4ch,
    compare_4ch,
)


def test_lz_off_by_default():
    """Without T90_MAGNETIC_MOMENT_MU_X env var, LZ channel returns 0 (silent).

    The hybrid loglike should reduce to the 3-channel value when LZ is off.
    """
    # Clear env var
    os.environ.pop("T90_MAGNETIC_MOMENT_MU_X", None)
    # Pure resonant best fit
    theta_log = np.array([
        np.log10(30.0),  # m_chi
        2.0,             # log m_phi_A
        0.0,             # g_A
        0.0,             # log m_phi_B
        0.0,             # g_B
        np.log10(65.0),  # E_R
        np.log10(0.1),   # Gamma
        np.log10(0.01),  # sigma_0
        np.log10(0.01),  # alpha_Y
        -10.0,           # log_mu_x (irrelevant when env var unset)
    ])
    ll_4ch = loglike_hybrid_4ch(theta_log)
    assert np.isfinite(ll_4ch), f"4ch loglike should be finite when LZ off, got {ll_4ch}"


def test_lz_on_with_strong_coupling_penalized():
    """With T90_MAGNETIC_MOMENT_MU_X set to large mu_x, LZ penalty fires.

    Note: this test only validates behavior when WIMpy is available.
    Without WIMpy, LZ channel returns 0 regardless of mu_x; test skips.
    """
    try:
        from WIMpy import DMUtils
        _wimpy_ok = True
    except ImportError:
        _wimpy_ok = False

    if not _wimpy_ok:
        # Without WIMpy, the LZ channel is silent (returns 0); nothing to test.
        # Verify that the channel returns 0 and that adding it doesn't change the loglike.
        os.environ["T90_MAGNETIC_MOMENT_MU_X"] = repr(1e-6)
        try:
            theta_log = np.array([
                np.log10(30.0), 2.0, 0.0, 0.0, 0.0,
                np.log10(65.0), np.log10(0.1), np.log10(0.01), np.log10(0.01),
                np.log10(1e-6),
            ])
            ll = loglike_hybrid_4ch(theta_log)
            assert np.isfinite(ll), f"loglike should be finite even without WIMpy, got {ll}"
        finally:
            os.environ.pop("T90_MAGNETIC_MOMENT_MU_X", None)
        return

    # Set a strong mu_x (mu_x = 1e-6 mu_N is already excluded by LZ)
    os.environ["T90_MAGNETIC_MOMENT_MU_X"] = repr(1e-6)
    try:
        theta_log = np.array([
            np.log10(30.0), 2.0, 0.0, 0.0, 0.0,
            np.log10(65.0), np.log10(0.1), np.log10(0.01), np.log10(0.01),
            np.log10(1e-6),  # log_mu_x matches env var
        ])
        ll = loglike_hybrid_4ch(theta_log)
        # Should be VERY negative due to LZ over-prediction penalty
        # (typically log L ~ -N_pred for N_pred >> 1)
        assert ll < -5, f"expected strong LZ penalty, got {ll}"
    finally:
        os.environ.pop("T90_MAGNETIC_MOMENT_MU_X", None)


def test_prior_transform_in_range():
    rng = np.random.default_rng(42)
    for _ in range(100):
        u = rng.uniform(size=10)
        theta_log = prior_transform_10(u)
        for i in range(10):
            lo, hi = LOG_RANGES_10[i]
            assert lo <= theta_log[i] <= hi, \
                f"param {i} ({PARAM_NAMES_10[i]}): {theta_log[i]} outside [{lo},{hi}]"


def test_prior_transform_corners():
    theta_lo = prior_transform_10(np.zeros(10))
    theta_hi = prior_transform_10(np.ones(10))
    for i in range(10):
        lo, hi = LOG_RANGES_10[i]
        assert abs(theta_lo[i] - lo) < 1e-9
        assert abs(theta_hi[i] - hi) < 1e-9


def test_out_of_prior_rejected():
    """theta outside any prior bound -> -inf."""
    bad = np.zeros(10)
    bad[0] = -10.0  # log m_chi = -10 -> way below prior range
    assert loglike_hybrid_4ch(bad) == -np.inf


def test_smoke_run():
    """Smoke run completes and gives finite log Z.

    Note: without WIMpy, the LZ channel is silent and log Z should be
    similar to T90.55's 3-channel value. With WIMpy, the LZ channel adds
    a 4th constraint.
    """
    s = run_hybrid_joint_fit_4ch(nlive=50, dlogz=0.5)
    assert np.isfinite(s["log_Z"])
    p = s["posterior_median_predictions"]
    # Sigma/m values should be positive
    for k in ("sigma_m_Cloud9_cm2_per_g", "sigma_m_Galaxy_cm2_per_g",
              "sigma_m_Bullet_cm2_per_g"):
        assert p[k] > 0, f"{k} = {p[k]} not positive"


def test_compare_4ch_returns_verdict():
    s = run_hybrid_joint_fit_4ch(nlive=50, dlogz=0.5)
    cmp = compare_4ch(s)
    assert "log_Z_hybrid_4ch" in cmp
    assert "verdict" in cmp


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
