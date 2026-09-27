#!/usr/bin/env python
"""
T90.56 -- Hybrid 10D joint fit with LZ magnetic-moment channel.

Promotes T90.55's 9D hybrid to 10D by adding log_mu_x (LZ magnetic-moment
coupling in nuclear magnetons). The LZ channel fires when the env var
T90_MAGNETIC_MOMENT_MU_X is set; the value of mu_x is taken from
theta[9] = log_mu_x (NOT from the env var -- the env var is the switch,
theta is the value).

Channels included:
  1. Cloud-9 RELHIC (sigma/m(28) in [30, 500] cm^2/g)
  2. Galactic dSph/UFD (sigma/m(100) < 2 cm^2/g)
  3. Bullet Cluster (sigma/m(3000) < 0.5 cm^2/g)
  4. LZ magnetic-moment EFT (Channel 26 from T90/wip/tier3 branch)

The LZ channel expects WIMpy_NREFT to be available; if not, the channel
silently returns 0 (per the docstring of loglike_lz_magnetic_moment).
Run this via .venv-sidm-bench python to ensure WIMpy is available.

Parameters (10D, all log):
    theta = (m_chi_GeV,            # log10 3 GeV - 1 TeV
             m_phi_A_MeV, g_chi_A, # log m, linear g
             m_phi_B_MeV, g_chi_B, # log m, linear g
             E_R_eV, Gamma_R_eV,   # resonance
             sigma_0, alpha_Y,     # resonance strength + Sommerfeld
             mu_x)                 # LZ magnetic moment, log10 mu_N

Note: g_chi_A and g_chi_B are linear in [0, 2] and [0, 0.5] respectively.

References:
    T90.51/52/55 predecessors
    T90 channel 26 (loglike_lz_magnetic_moment from channels_extended.py)
    arXiv:2512.05850 (LZ 2024 results, 248 keV event)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Reuse the 3-channel likelihoods and the hybrid sigma/m
from t90_v51_resonant_joint_fit import (
    loglike_cloud9,
    loglike_galaxy,
    loglike_bullet,
)
from t90_v54_hybrid_sigma_m import (
    sigma_m_hybrid,
    LOG_RANGES as LOG_RANGES_9,
    IS_LOG as IS_LOG_9,
    unpack_theta as unpack_theta_9,
)

# LZ magnetic-moment channel from channels_extended.py
from channels_extended import loglike_lz_magnetic_moment


# --------------------------------------------------------------------------
# 10D priors (9 from T90.55 + log_mu_x from T90 canonical)
# --------------------------------------------------------------------------
LOG_M_CHI_GEV_RANGE = (0.5, 3.0)        # 3 GeV to 1 TeV
LOG_M_PHI_A_MEV_RANGE = (1.5, 4.0)     # 30 MeV to 10 TeV
G_CHI_A_RANGE = (0.0, 2.0)
LOG_M_PHI_B_MEV_RANGE = (-0.5, 2.0)
G_CHI_B_RANGE = (0.0, 0.5)
LOG_E_R_EV_RANGE = (0.5, 5.0)
LOG_GAMMA_R_EV_RANGE = (-3.0, 3.0)
LOG_SIGMA_0_RANGE = (-5.0, 0.0)
LOG_ALPHA_Y_RANGE = (-5.0, 0.0)
LOG_MU_X_RANGE = (-15.0, -4.0)         # mu_x in [1e-15, 1e-4] mu_N

LOG_RANGES_10 = [
    LOG_M_CHI_GEV_RANGE,
    LOG_M_PHI_A_MEV_RANGE,
    G_CHI_A_RANGE,
    LOG_M_PHI_B_MEV_RANGE,
    G_CHI_B_RANGE,
    LOG_E_R_EV_RANGE,
    LOG_GAMMA_R_EV_RANGE,
    LOG_SIGMA_0_RANGE,
    LOG_ALPHA_Y_RANGE,
    LOG_MU_X_RANGE,
]
PARAM_NAMES_10 = [
    "log_m_chi_GeV",
    "log_m_phi_A_MeV",
    "g_chi_A",
    "log_m_phi_B_MeV",
    "g_chi_B",
    "log_E_R_eV",
    "log_Gamma_R_eV",
    "log_sigma_0",
    "log_alpha_Y",
    "log_mu_x",
]
IS_LOG_10 = [True, True, False, True, False, True, True, True, True, True]


def prior_transform_10(u):
    """10D unit cube -> mixed log/linear parameter vector."""
    theta = np.zeros(10)
    for i in range(10):
        lo, hi = LOG_RANGES_10[i]
        theta[i] = lo + u[i] * (hi - lo)
    return theta


def unpack_theta_10(theta_log):
    """Convert 10D log-mixed vector to the 9-tuple physical form
    expected by sigma_m_hybrid + mu_x scalar for LZ."""
    m_chi = 10.0 ** theta_log[0]
    m_phi_A = 10.0 ** theta_log[1]
    g_A = theta_log[2]
    m_phi_B = 10.0 ** theta_log[3]
    g_B = theta_log[4]
    E_R = 10.0 ** theta_log[5]
    Gamma = 10.0 ** theta_log[6]
    sigma_0 = 10.0 ** theta_log[7]
    alpha_Y = 10.0 ** theta_log[8]
    mu_x = 10.0 ** theta_log[9]
    theta_9 = (m_chi, m_phi_A, g_A, m_phi_B, g_B,
               E_R, Gamma, sigma_0, alpha_Y)
    return theta_9, mu_x


def loglike_hybrid_4ch(theta_log):
    """10D joint 4-channel log-likelihood for hybrid sigma/m(v) + LZ.

    theta_log: 10D vector in mixed log/linear form (output of prior_transform_10).

    Channels:
      - Cloud-9: Gaussian in log10(sigma/m(28)), center = log10(geometric mean of [30, 500])
      - Galactic: 1-sided half-Gaussian above log10(2)
      - Bullet:  1-sided half-Gaussian above log10(0.5)
      - LZ:      Poisson loglike for 248 keV event (uses T90_MAGNETIC_MOMENT_MU_X env var)
    """
    # Prior bounds enforcement
    for i in range(10):
        lo, hi = LOG_RANGES_10[i]
        if not (lo <= theta_log[i] <= hi):
            return -np.inf

    theta_9, mu_x = unpack_theta_10(theta_log)

    # Compute sigma/m at the 3 canonical velocities
    sm_c9 = sigma_m_hybrid(28.0, theta_9)["sigma_m_total_cm2_per_g"]
    sm_gal = sigma_m_hybrid(100.0, theta_9)["sigma_m_total_cm2_per_g"]
    sm_bul = sigma_m_hybrid(3000.0, theta_9)["sigma_m_total_cm2_per_g"]

    # Numerical safety
    if sm_c9 <= 0 or sm_gal <= 0 or sm_bul <= 0:
        return -np.inf
    if not (np.isfinite(sm_c9) and np.isfinite(sm_gal) and np.isfinite(sm_bul)):
        return -np.inf

    # 3-channel sum
    ll = (loglike_cloud9(sm_c9)
          + loglike_galaxy(sm_gal)
          + loglike_bullet(sm_bul))
    if not np.isfinite(ll):
        return -np.inf

    # LZ channel (4th channel)
    m_chi_GeV = theta_9[0]
    ll_lz = loglike_lz_magnetic_moment(m_chi_GeV, mu_x, include_in_fit=True)
    if not np.isfinite(ll_lz):
        ll_lz = 0.0  # if WIMpy not available, treat as silent

    total = ll + ll_lz
    if not np.isfinite(total):
        return -np.inf
    return total


# --------------------------------------------------------------------------
# Run helpers
# --------------------------------------------------------------------------
def _weighted_quantile(values, weights, q):
    idx = np.argsort(values)
    v = values[idx]
    w = weights[idx]
    cum = np.cumsum(w)
    cum = cum / cum[-1] if cum[-1] > 0 else cum
    return float(np.interp(q, cum, v))


def run_hybrid_joint_fit_4ch(nlive: int = 500, dlogz: float = 0.05,
                                output_dir: str = None):
    """Run the 10D hybrid 4-channel joint fit.

    Note: this REQUIRES WIMpy_NREFT to be importable. Run with the
    .venv-sidm-bench python, otherwise LZ channel returns 0 silently.
    """
    import dynesty

    if output_dir is None:
        if os.name == "nt":
            output_dir = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
        else:
            output_dir = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    sampler = dynesty.NestedSampler(
        loglike_hybrid_4ch,
        prior_transform_10,
        ndim=10,
        nlive=nlive,
        bound="multi",
        sample="rwalk",
        walks=50,
    )
    t0 = time.time()
    sampler.run_nested(dlogz=dlogz, maxiter=100000, print_progress=True)
    wall = time.time() - t0

    res = sampler.results
    log_z = float(res.logz[-1])
    log_z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])

    medians = {}
    for i in range(10):
        v = samples[:, i]
        medians[PARAM_NAMES_10[i]] = {
            "median": float(_weighted_quantile(v, weights, 0.5)),
            "p16": float(_weighted_quantile(v, weights, 0.16)),
            "p84": float(_weighted_quantile(v, weights, 0.84)),
        }

    med_log = np.array([medians[n]["median"] for n in PARAM_NAMES_10])
    med_theta_9, med_mu_x = unpack_theta_10(med_log)
    r_c9 = sigma_m_hybrid(28.0, med_theta_9)
    r_gal = sigma_m_hybrid(100.0, med_theta_9)
    r_bul = sigma_m_hybrid(3000.0, med_theta_9)
    # LZ channel at posterior median
    ll_lz_med = loglike_lz_magnetic_moment(med_theta_9[0], med_mu_x,
                                             include_in_fit=True)
    if not np.isfinite(ll_lz_med):
        ll_lz_med = 0.0

    c9_ok = 30.0 < r_c9["sigma_m_total_cm2_per_g"] < 500.0
    gal_ok = r_gal["sigma_m_total_cm2_per_g"] < 2.0
    bul_ok = r_bul["sigma_m_total_cm2_per_g"] < 0.5

    summary = {
        "framework": "T90.56 hybrid 10D (multi-portal + resonance + Sommerfeld + LZ magnetic moment)",
        "log_Z": log_z,
        "log_Z_err": log_z_err,
        "wall_seconds": wall,
        "nlive": nlive,
        "dlogz_target": dlogz,
        "ndim": 10,
        "n_samples": int(samples.shape[0]),
        "posterior_medians": medians,
        "posterior_median_predictions": {
            "sigma_m_Cloud9_cm2_per_g": float(r_c9["sigma_m_total_cm2_per_g"]),
            "sigma_m_Galaxy_cm2_per_g": float(r_gal["sigma_m_total_cm2_per_g"]),
            "sigma_m_Bullet_cm2_per_g": float(r_bul["sigma_m_total_cm2_per_g"]),
            "mu_x_at_median": float(med_mu_x),
            "loglike_LZ_at_median": float(ll_lz_med),
        },
        "channel_satisfaction_at_median": {
            "Cloud9": bool(c9_ok),
            "Galaxy": bool(gal_ok),
            "Bullet": bool(bul_ok),
            "n_satisfied_3ch": int(c9_ok) + int(gal_ok) + int(bul_ok),
        },
        "channel_likelihood_match": "T90.51 (Cloud-9 + Galactic + Bullet) + LZ magnetic moment (Channel 26)",
        "wimpy_available": _check_wimpy(),
    }
    out_path = Path(output_dir) / "t90_v56_hybrid_4ch_joint_posterior.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[T90.56] Wrote {out_path}")
    return summary


def _check_wimpy():
    try:
        from WIMpy import DMUtils
        return True
    except ImportError:
        return False


def compare_4ch(hybrid_summary: dict,
                res_path: str = None) -> dict:
    """Compare hybrid 4ch log Z to T90.51 (resonant, 3ch) for honesty.

    Note: T90.55 multi-portal 3ch log Z was -2.289. Hybrid 4ch should be
    compared to a multi-portal 4ch run (T90.52b, deferred) for apples-to-
    apples. For now, we report the 4ch log Z directly.
    """
    log_z_h = hybrid_summary["log_Z"]
    log_z_h_err = hybrid_summary["log_Z_err"]
    wimpy = hybrid_summary.get("wimpy_available", False)

    # Channels satisfied
    cs = hybrid_summary["channel_satisfaction_at_median"]

    if wimpy:
        verdict = "4-channel fit (LZ active)"
    else:
        verdict = "WIMpy unavailable -- LZ channel silent, reduces to 3-channel fit"

    return {
        "log_Z_hybrid_4ch": log_z_h,
        "log_Z_hybrid_4ch_err": log_z_h_err,
        "channels_satisfied_at_median": cs["n_satisfied_3ch"],
        "LZ_active": wimpy,
        "verdict": verdict,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--nlive", type=int, default=500)
    p.add_argument("--dlogz", type=float, default=0.05)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()

    if args.smoke:
        s = run_hybrid_joint_fit_4ch(nlive=50, dlogz=0.5)
    else:
        s = run_hybrid_joint_fit_4ch(nlive=args.nlive, dlogz=args.dlogz)

    print("\n[T90.56] Hybrid 4ch log Z =", round(s["log_Z"], 3),
          "+/-", round(s["log_Z_err"], 3))
    print("[T90.56] wall =", round(s["wall_seconds"], 1), "s")
    p_ = s["posterior_median_predictions"]
    cs = s["channel_satisfaction_at_median"]
    print(f"[T90.56] Posterior median:")
    print(f"  sigma/m(Cloud-9) = {p_['sigma_m_Cloud9_cm2_per_g']:.3f}")
    print(f"  sigma/m(Galaxy)  = {p_['sigma_m_Galaxy_cm2_per_g']:.3f}")
    print(f"  sigma/m(Bullet)  = {p_['sigma_m_Bullet_cm2_per_g']:.4f}")
    print(f"  mu_x at median   = {p_['mu_x_at_median']:.3e} mu_N")
    print(f"  loglike_LZ at med= {p_['loglike_LZ_at_median']:.3f}")
    print(f"[T90.56] 3-ch satisfaction: {cs['n_satisfied_3ch']}/3  "
          f"(C9={cs['Cloud9']} Gal={cs['Galaxy']} Bul={cs['Bullet']})")
    print(f"[T90.56] WIMpy available: {s['wimpy_available']}")
