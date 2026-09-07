"""
T95 Option 3.5 — Real 8D nested-sampling fit (7D + Channel 27 likelihood).

PURPOSE
=======
The Option 3 estimator used the existing 7D posterior and added
Channel 27 (Euclid Q1 sub-halo forecast) as a median-logL
penalty. The estimator told us Channel 27 disfavors the
LZ-anchored Yukawa by Delta log Z ~ -3.8.

This script does a PROPER 8D model comparison by adding
Channel 27 to the joint likelihood and re-running the
nested sampling. The result is:

  7D model:   loglike = loglike_joint (T41 v0.6 + Channel 26 magnetic)
  8D model:   loglike = loglike_joint + loglike_euclid_q1_subhalo

The Bayes factor B(8D, 7D) = exp(log Z_8D - log Z_7D) tells
us whether the data (LZ + Channel 27) prefer the augmented
model.

NOTE: This is 7D parameters + 1 additional likelihood component,
not 8D parameters. The "8D" label refers to model space, not
parameter space. Adding Channel 27 as a function of the
existing 7D parameters doesn't add a dimension.

WHAT THIS IS NOT
================
- This is NOT a new GIZMO install or hydro sim.
- This is NOT a full GD-1 stream-gap likelihood.
- This is NOT a change to the 6D canonical T41 fit.
- This is NOT a change to the 7D T90.1 fit.

This IS a wrapper that re-runs the 7D fit with Channel 27
added to the likelihood, behind an env var. Branch-local.

REFERENCES
==========
- 7D T90.1 fit: t41_v07_magnetic_moment_7d.py
- Channel 27: v0.3-prelim/code/euclid_q1_subhalo_forecast_forward_model.py
- T89 benchmark: T89_SIDMKIT_SIDMVDSIGMAS_BENCHMARK.md
- T95 Option 3: T95_OPTION3_SUBHALO_FORECAST.md
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Make t41 importable
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

import t41_mediator_mass_joint_fit as t41
from t40_yukawa_sigma_m import sigma_m_cm2_per_g
from euclid_q1_subhalo_forecast_forward_model import (
    loglike_euclid_q1_subhalo_forecast,
    V_REF,
    EUCLID_Q1_SUBHALO_VMAX_KMS,
)

from dynesty import NestedSampler


def fit_velocity_powerlaw(sigma_arr_at_v100, sigma_arr_at_v200):
    """
    Fit sigma/m(v) = sigma_m_0 * (V_REF/v)^a to two points.

    Returns (sigma_m_0, a):
      sigma_m_0: cross-section at V_REF
      a: velocity slope (positive = falls with v)
    """
    # If both sigmas are equal, a = 0
    if abs(sigma_arr_at_v100 - sigma_arr_at_v200) < 1e-10 * max(sigma_arr_at_v100, sigma_arr_at_v200):
        return sigma_arr_at_v100, 0.0
    log_v = np.log10([100.0, 200.0])
    log_s = np.log10([sigma_arr_at_v100, sigma_arr_at_v200])
    slope, intercept = np.polyfit(log_v, log_s, 1)
    a = -slope
    log_sigma_0 = intercept + a * np.log10(V_REF)
    return 10 ** log_sigma_0, a


def loglike_joint_7d_with_channel27(theta):
    """
    7D log-likelihood + Channel 27 (Euclid Q1 sub-halo forecast).

    Reads the 6 canonical T41 parameters + log_mu_x (the 7th),
    computes the 7D loglike via env-var handoff, then adds
    Channel 27 logL.

    The env-var handoff is the same pattern as t41_v07.
    """
    if len(theta) != 7:
        raise ValueError(f"loglike_joint_7d_with_channel27 expects 7-D theta, got {len(theta)}")
    log_mu_x = theta[6]
    mu_x = 10.0 ** log_mu_x
    os.environ["T90_MAGNETIC_MOMENT_MU_X"] = repr(mu_x)
    try:
        ll_7d = t41.loglike_joint(theta[:6])
    finally:
        os.environ.pop("T90_MAGNETIC_MOMENT_MU_X", None)

    # Channel 27: compute (sigma_m_0, a) from theta[:3]
    # (m_phi, m_chi, g_chi) are theta[0:3] in log_m_phi, log_m_chi, g_chi
    m_phi_MeV = 10 ** theta[0]
    m_chi_GeV = 10 ** theta[1]
    g_chi = theta[2]
    sigma_at_100 = sigma_m_cm2_per_g(100.0, m_phi_MeV, m_chi_GeV, g_chi)
    sigma_at_200 = sigma_m_cm2_per_g(200.0, m_phi_MeV, m_chi_GeV, g_chi)
    sigma_m_0, a = fit_velocity_powerlaw(sigma_at_100, sigma_at_200)
    ll_channel27 = loglike_euclid_q1_subhalo_forecast(sigma_m_0, a)
    return ll_7d + ll_channel27


def main():
    print("=" * 80)
    print("T41 v0.8 — 8D model comparison (7D + Channel 27)")
    print("=" * 80)
    print()
    print("Model comparison:")
    print("  7D: T41 v0.6 + Channel 26 magnetic-moment (existing T90.1 fit)")
    print("  8D: 7D + Channel 27 (Euclid Q1 sub-halo forecast)")
    print()
    print("Bayes factor B(8D, 7D) = exp(log Z_8D - log Z_7D)")
    print("Jeffreys scale:")
    print("  |Delta log Z| < 1:  barely worth mentioning")
    print("  1 < |Delta log Z| < 3:  substantial")
    print("  3 < |Delta log Z| < 5:  strong")
    print("  |Delta log Z| > 5:  very strong")
    print()

    # Nested sampling
    nlive = 200
    ndim = 7
    print(f"Running 8D nested sampling with nlive={nlive}, ndim={ndim}...")

    # Use the v07 7D prior transform (same shape, just log_mu_x added)
    from t41_v07_magnetic_moment_7d import prior_transform_7

    t0 = time.time()
    sampler = NestedSampler(
        loglike_joint_7d_with_channel27,
        prior_transform_7,
        ndim=ndim,
        nlive=nlive,
        bound='multi',
    )
    sampler.run_nested(dlogz=0.5)
    res = sampler.results
    wall_time = time.time() - t0
    print(f"Wall time: {wall_time:.1f} sec")
    print()

    log_Z_8D = float(res.logz[-1])
    log_Z_8D_err = float(res.logzerr[-1])
    print(f"log Z (8D model) = {log_Z_8D:.3f} ± {log_Z_8D_err:.3f}")

    # Compare to 7D
    log_Z_7D = -164.959
    log_Z_7D_err = 0.247
    delta_logZ = log_Z_8D - log_Z_7D
    print(f"log Z (7D model, T90.1) = {log_Z_7D:.3f} ± {log_Z_7D_err:.3f}")
    print(f"Delta log Z (8D - 7D) = {delta_logZ:.3f}")
    print()

    # Jeffreys verdict
    if abs(delta_logZ) < 1.0:
        jeffreys = "barely worth mentioning"
    elif abs(delta_logZ) < 3.0:
        jeffreys = "substantial"
    elif abs(delta_logZ) < 5.0:
        jeffreys = "strong"
    else:
        jeffreys = "very strong"
    direction = "FAVORS 8D" if delta_logZ > 0 else "FAVORS 7D"
    print(f"Jeffreys verdict: {direction} ({jeffreys})")

    # Importance-sampled posterior
    samples_equal = res.samples
    log_w = res.logwt
    weights = np.exp(log_w - log_w.max())
    weights /= weights.sum()
    median_params = np.array([
        np.median(samples_equal[:, k]) for k in range(7)
    ])

    print()
    print("=" * 80)
    print("8D posterior medians")
    print("=" * 80)
    labels = ["log_m_phi_MeV", "log_m_chi_GeV", "g_chi", "log_epsilon",
              "log_alpha", "log_xi", "log_mu_x"]
    for label, med in zip(labels, median_params):
        print(f"  {label:>20s} = {med:.4f}")

    # Save results
    out_dir = _THIS_DIR.parent / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "option3_5_8d_results.json"
    summary = {
        "phase": "T95 Option 3.5",
        "task": "Real 8D nested-sampling fit (7D + Channel 27)",
        "nlive": nlive,
        "ndim_params": ndim,
        "model_comparison": {
            "log_Z_7D": log_Z_7D,
            "log_Z_7D_err": log_Z_7D_err,
            "log_Z_8D": log_Z_8D,
            "log_Z_8D_err": log_Z_8D_err,
            "delta_logZ": delta_logZ,
            "jeffreys_verdict": jeffreys,
            "direction": direction,
        },
        "wall_time_sec": wall_time,
        "posterior_medians": {
            label: float(med) for label, med in zip(labels, median_params)
        },
        "comparison_to_option3_estimator": {
            "option3_estimator_delta_logZ": -3.81,
            "option3_5_real_fit_delta_logZ": delta_logZ,
            "consistent": abs(delta_logZ - (-3.81)) < 2.0,
        },
        "caveats": [
            "8D refers to model space (7D params + 1 likelihood), not 8 parameters",
            "Channel 27 is a forecast, not a measurement (arXiv:2503.15330)",
            "Adding Channel 27 as a function of the 7D parameters does not",
            "add a parameter dimension; the posterior is 7D-shaped but",
            "reweighted by Channel 27.",
            "Master's 6D canonical fit is unchanged. The 7D T90.1 fit is",
            "unchanged. This is a separate experiment, branch-local.",
        ],
    }
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote: {out_json}")


if __name__ == "__main__":
    main()