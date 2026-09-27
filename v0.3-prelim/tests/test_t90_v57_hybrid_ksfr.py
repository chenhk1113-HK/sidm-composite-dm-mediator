"""T90.57 tests -- KSFR/PCAC validity channel added to hybrid (5-channel).

Verifies:
  - loglike_hybrid_5ch shape (finite at valid points, -inf at out-of-prior)
  - KSFR returns -inf when m_phi_A is outside the KSFR box (when enabled)
  - KSFR returns 0 when env var SIDM_DISABLE_KSFR_MASK=1 (default)
  - End-to-end smoke run completes and gives finite log Z
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v57_hybrid_ksfr import (
    loglike_hybrid_5ch,
    prior_transform_10,
    LOG_RANGES_10,
    PARAM_NAMES_10,
    IS_LOG_10,
    run_hybrid_joint_fit_5ch,
    compare_5ch,
    KSFR_ENABLED,
    set_ksfr_enabled,
)


def test_ksfr_disabled_by_default_via_env():
    """Without SIDM_DISABLE_KSFR_MASK=1 set, KSFR may be active.
    By default the project's convention is KSFR disabled via env var.

    This test verifies that we can read and respect the env var.
    """
    # The test sets SIDM_DISABLE_KSFR_MASK=1 to disable KSFR.
    # If it was set differently, that means KSFR is enabled by default in
    # this test environment, which would change test behavior.
    saved = os.environ.get("SIDM_DISABLE_KSFR_MASK")
    try:
        os.environ["SIDM_DISABLE_KSFR_MASK"] = "1"
        # Re-import to pick up env var
        import importlib
        import t90_v57_hybrid_ksfr as m
        importlib.reload(m)
        assert m.KSFR_ENABLED is False
    finally:
        if saved is None:
            os.environ.pop("SIDM_DISABLE_KSFR_MASK", None)
        else:
            os.environ["SIDM_DISABLE_KSFR_MASK"] = saved


def test_loglike_finite_at_KSFR_box_point():
    """At a hybrid point with m_phi_A in the KSFR box [418, 4180] MeV,
    loglike should be finite when KSFR is disabled (env var set)."""
    os.environ["SIDM_DISABLE_KSFR_MASK"] = "1"
    import importlib
    import t90_v57_hybrid_ksfr as m
    importlib.reload(m)

    theta_log = np.array([
        np.log10(30.0),       # m_chi = 30 GeV
        np.log10(1000.0),     # m_phi_A = 1000 MeV (within KSFR box 418-4180)
        0.5,                  # g_A = 0.5
        0.0,                  # log m_phi_B = 0 -> m_phi_B = 1 MeV (outside KSFR box)
        0.0,                  # g_B = 0 (off)
        np.log10(65.0),       # E_R = 65 eV
        np.log10(0.1),        # Gamma = 0.1 eV
        np.log10(0.01),       # sigma_0 = 0.01
        np.log10(0.01),       # alpha_Y = 0.01
        -10.0,                # log_mu_x (LZ off)
    ])
    ll = m.loglike_hybrid_5ch(theta_log)
    assert np.isfinite(ll), f"expected finite, got {ll}"


def test_ksfr_rejects_m_phi_outside_box():
    """When KSFR is enabled and m_phi_A is outside [418, 4180] MeV, loglike returns -inf."""
    os.environ["SIDM_DISABLE_KSFR_MASK"] = "0"  # enable KSFR
    import importlib
    import t90_v57_hybrid_ksfr as m
    importlib.reload(m)
    assert m.KSFR_ENABLED, "KSFR should be enabled when SIDM_DISABLE_KSFR_MASK=0"

    # m_phi_A = 10 MeV (way below KSFR box [418, 4180])
    theta_log = np.array([
        np.log10(30.0),
        np.log10(10.0),       # m_phi_A = 10 MeV (below KSFR box)
        0.5,
        0.0, 0.0,
        np.log10(65.0), np.log10(0.1),
        np.log10(0.01), np.log10(0.01),
        -10.0,
    ])
    ll = m.loglike_hybrid_5ch(theta_log)
    assert ll == -np.inf, f"KSFR outside box should reject, got {ll}"


def test_out_of_prior_rejected():
    """theta outside any prior bound -> -inf."""
    bad = np.zeros(10)
    bad[0] = -10.0
    assert loglike_hybrid_5ch(bad) == -np.inf


def test_prior_transform_in_range():
    rng = np.random.default_rng(42)
    for _ in range(100):
        u = rng.uniform(size=10)
        theta_log = prior_transform_10(u)
        for i in range(10):
            lo, hi = LOG_RANGES_10[i]
            assert lo <= theta_log[i] <= hi, \
                f"param {i} ({PARAM_NAMES_10[i]}): {theta_log[i]} outside [{lo},{hi}]"


def test_smoke_run():
    """Smoke run completes and gives finite log Z."""
    s = run_hybrid_joint_fit_5ch(nlive=50, dlogz=0.5)
    assert np.isfinite(s["log_Z"])
    p = s["posterior_median_predictions"]
    for k in ("sigma_m_Cloud9_cm2_per_g", "sigma_m_Galaxy_cm2_per_g",
              "sigma_m_Bullet_cm2_per_g"):
        assert p[k] > 0, f"{k} = {p[k]} not positive"


def test_compare_5ch_returns_verdict():
    s = run_hybrid_joint_fit_5ch(nlive=50, dlogz=0.5)
    cmp = compare_5ch(s)
    assert "log_Z_hybrid_5ch" in cmp
    assert "verdict" in cmp


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
