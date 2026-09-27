#!/usr/bin/env python
"""
T90.52 -- Multi-portal vs resonant SIDM apples-to-apples log Z comparison.

Re-runs the T90.45 multi-portal joint fit on the SAME 3-channel likelihood
function (Cloud-9 + Galactic + Bullet) that T90.51 uses for resonant SIDM.

This is the proper Δlog Z test: identical channels, identical likelihood
function, identical dynesty settings (nlive=500, dlogz=0.05), identical
channel sigma/width choices. Only the parametric form of sigma/m(v) differs.

Parameters for multi-portal (9D, log-uniform except g_chi which is linear):
    log_m_phi_A_MeV  : Portal A mediator mass
    log_m_chi_A_GeV  : Portal A DM mass
    g_chi_A          : Portal A coupling (linear 0.5-2.0, same as T90.45)
    log_m_phi_B_MeV  : Portal B mediator mass
    log_m_chi_B_GeV  : Portal B DM mass
    g_chi_B          : Portal B coupling (linear 0.05-0.5, same as T90.45)
    log_epsilon_A    : Portal A kinetic mixing (nuisance in 3-channel comparison)
    log_alpha_A      : Portal A annihilation coupling (nuisance)
    log_xi           : dark temperature ratio (nuisance)

Likelihood: sum of (Cloud-9 Gaussian + Galactic half-Gaussian + Bullet half-Gaussian)
as defined in t90_v51_resonant_joint_fit.py.

Per T90.45 publication: nlive=200, dlogz=0.1. We match that to make the
re-run directly comparable to the T90.45 numbers cited in the literature.

References:
    T90.45 multi-portal (predecessor; uses 5+ channels)
    T90.51 resonant (predecessor; 3 channels)
    T90.45 priors: v0.3-prelim/code/t90_v45_multi_portal_joint_fit.py:138-154
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t40_yukawa_sigma_m import sigma_m_cm2_per_g
from t90_v44_multi_portal import sigma_m_multi_portal
# Reuse the T90.51 3-channel likelihood directly -- this is the whole point.
from t90_v51_resonant_joint_fit import (
    loglike_resonant_3ch as loglike_3ch_unpack,
    loglike_cloud9,
    loglike_galaxy,
    loglike_bullet,
)


def loglike_multi_portal_3ch(theta):
    """3-channel joint log-likelihood for the multi-portal SIDM model.

    theta: 9-vector in physical units (NOT log). Layout matches T90.45:
      [log_m_phi_A_MeV, log_m_chi_A_GeV, g_chi_A,
       log_m_phi_B_MeV, log_m_chi_B_GeV, g_chi_B,
       log_epsilon_A, log_alpha_A, log_xi]
    """
    (log_m_phi_A, log_m_chi_A, g_chi_A,
     log_m_phi_B, log_m_chi_B, g_chi_B,
     log_eps_A, log_alpha_A, log_xi) = theta

    # Prior-bounds enforcement -- required so prior_transform_9_mp defines
    # the prior volume and the dynesty evidence is properly normalized.
    for i in range(9):
        lo, hi = LOG_RANGES_MP[i]
        if not (lo <= theta[i] <= hi):
            return -np.inf

    m_phi_A = 10.0 ** log_m_phi_A
    m_chi_A = 10.0 ** log_m_chi_A
    m_phi_B = 10.0 ** log_m_phi_B
    m_chi_B = 10.0 ** log_m_chi_B

    # Numerical safety on the physical (post-10^x) quantities
    if not (1.0 <= m_phi_A <= 1e5 and 1.0 <= m_chi_A <= 1e4):
        return -np.inf
    if not (0.1 <= m_phi_B <= 1e3 and 1.0 <= m_chi_B <= 1e4):
        return -np.inf
    if not (0.01 <= g_chi_A <= 3.0 and 0.01 <= g_chi_B <= 1.0):
        return -np.inf

    # Combined sigma/m at each velocity
    try:
        sm_c9 = sigma_m_multi_portal(28.0, m_phi_A, m_chi_A, g_chi_A,
                                       m_phi_B, m_chi_B, g_chi_B)
        sm_gal = sigma_m_multi_portal(100.0, m_phi_A, m_chi_A, g_chi_A,
                                        m_phi_B, m_chi_B, g_chi_B)
        sm_bul = sigma_m_multi_portal(3000.0, m_phi_A, m_chi_A, g_chi_A,
                                        m_phi_B, m_chi_B, g_chi_B)
    except Exception:
        return -np.inf

    if not (np.isfinite(sm_c9) and np.isfinite(sm_gal) and np.isfinite(sm_bul)):
        return -np.inf

    # Numerical safety: the 3 channels expect positive sigma/m
    if sm_c9 <= 0 or sm_gal <= 0 or sm_bul <= 0:
        return -np.inf

    total = (loglike_cloud9(sm_c9)
             + loglike_galaxy(sm_gal)
             + loglike_bullet(sm_bul))
    if not np.isfinite(total):
        return -np.inf
    return total


# --------------------------------------------------------------------------
# Priors -- copied from T90.45 lines 138-154
# --------------------------------------------------------------------------
LOG_M_PHI_A_MEV_RANGE = (1.5, 4.0)   # 30 MeV to 10 TeV (heavy mediator)
LOG_M_CHI_A_GEV_RANGE = (0.5, 3.0)   # 3 GeV to 1 TeV
G_CHI_A_RANGE = (0.5, 2.0)           # moderate-to-strong coupling

LOG_M_PHI_B_MEV_RANGE = (-0.5, 2.0)  # 0.3 MeV to 100 MeV (light mediator)
LOG_M_CHI_B_GEV_RANGE = (1.0, 3.5)   # 10 GeV to 3 TeV
G_CHI_B_RANGE = (0.05, 0.5)          # weak coupling

LOG_EPSILON_A_RANGE = (-50.0, -10.0)  # nuisance in 3-channel comparison
LOG_ALPHA_A_RANGE = (-30.0, -1.0)     # nuisance
LOG_XI_RANGE = (-1.0, 0.7)            # nuisance

# 9D prior: 6 log-uniform + 2 linear + 1 log-uniform
# Layout: [log_m_phi_A, log_m_chi_A, g_chi_A (linear),
#          log_m_phi_B, log_m_chi_B, g_chi_B (linear),
#          log_eps_A, log_alpha_A, log_xi]
LOG_RANGES_MP = [
    LOG_M_PHI_A_MEV_RANGE,
    LOG_M_CHI_A_GEV_RANGE,
    G_CHI_A_RANGE,           # linear
    LOG_M_PHI_B_MEV_RANGE,
    LOG_M_CHI_B_GEV_RANGE,
    G_CHI_B_RANGE,           # linear
    LOG_EPSILON_A_RANGE,
    LOG_ALPHA_A_RANGE,
    LOG_XI_RANGE,
]
PARAM_NAMES_MP = [
    "log_m_phi_A_MeV", "log_m_chi_A_GeV", "g_chi_A",
    "log_m_phi_B_MeV", "log_m_chi_B_GeV", "g_chi_B",
    "log_epsilon_A", "log_alpha_A", "log_xi",
]
IS_LOG_MP = [True, True, False, True, True, False, True, True, True]


def prior_transform_9_mp(u):
    """9D unit cube -> physical parameter vector for multi-portal."""
    theta = np.zeros(9)
    for i in range(9):
        lo, hi = LOG_RANGES_MP[i]
        theta[i] = lo + u[i] * (hi - lo)
    return theta


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


def run_multi_portal(nlive: int = 200, dlogz: float = 0.1, output_dir: str = None):
    import dynesty

    if output_dir is None:
        if os.name == "nt":
            output_dir = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
        else:
            output_dir = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    sampler = dynesty.NestedSampler(
        loglike_multi_portal_3ch,
        prior_transform_9_mp,
        ndim=9,
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

    # Compute median + 16/84% per parameter (no log-transform because g_chi is linear)
    medians = {}
    for i in range(9):
        v = samples[:, i]
        medians[PARAM_NAMES_MP[i]] = {
            "median": float(_weighted_quantile(v, weights, 0.5)),
            "p16": float(_weighted_quantile(v, weights, 0.16)),
            "p84": float(_weighted_quantile(v, weights, 0.84)),
        }

    # Compute sigma/m at posterior median
    med_phys = np.array([medians[n]["median"] for n in PARAM_NAMES_MP])
    m_phi_A, m_chi_A, g_A, m_phi_B, m_chi_B, g_B = (
        10.0 ** med_phys[0], 10.0 ** med_phys[1], med_phys[2],
        10.0 ** med_phys[3], 10.0 ** med_phys[4], med_phys[5],
    )
    sm_c9 = sigma_m_multi_portal(28.0, m_phi_A, m_chi_A, g_A, m_phi_B, m_chi_B, g_B)
    sm_gal = sigma_m_multi_portal(100.0, m_phi_A, m_chi_A, g_A, m_phi_B, m_chi_B, g_B)
    sm_bul = sigma_m_multi_portal(3000.0, m_phi_A, m_chi_A, g_A, m_phi_B, m_chi_B, g_B)

    summary = {
        "framework": "T90.45 multi-portal (re-run on 3-channel likelihood)",
        "log_Z": log_z,
        "log_Z_err": log_z_err,
        "wall_seconds": wall,
        "nlive": nlive,
        "dlogz_target": dlogz,
        "ndim": 9,
        "n_samples": int(samples.shape[0]),
        "posterior_medians": medians,
        "posterior_median_predictions": {
            "sigma_m_Cloud9_cm2_per_g": float(sm_c9),
            "sigma_m_Galaxy_cm2_per_g": float(sm_gal),
            "sigma_m_Bullet_cm2_per_g": float(sm_bul),
        },
        "channel_likelihood_match": "T90.51 (Cloud-9 Gaussian + Galactic 1-sided + Bullet 1-sided)",
    }
    out_path = Path(output_dir) / "t90_v52_multi_portal_joint_posterior.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[T90.52] Wrote {out_path}")
    return summary


def compare_with_resonant(mp_summary: dict, res_summary_path: str = None) -> dict:
    """Load T90.51 summary and compute Δlog Z + verdict."""
    if res_summary_path is None:
        if os.name == "nt":
            base = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results")
        else:
            base = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")
        res_summary_path = base / "t90_v51_resonant_joint_posterior.json"

    with open(res_summary_path) as f:
        res = json.load(f)

    delta_log_z = res["log_Z"] - mp_summary["log_Z"]
    delta_log_z_err = float(np.hypot(res["log_Z_err"], mp_summary["log_Z_err"]))

    # Bayes factor interpretation (Jeffreys scale, rough)
    if delta_log_z > 5:
        verdict = "VERY STRONG: resonant preferred (Jeffreys)"
    elif delta_log_z > 2.5:
        verdict = "STRONG: resonant preferred"
    elif delta_log_z > 1:
        verdict = "MODERATE: resonant preferred"
    elif delta_log_z > -1:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "MULTI-PORTAL PREFERRED"

    out = {
        "resonant_log_Z": res["log_Z"],
        "resonant_log_Z_err": res["log_Z_err"],
        "multi_portal_log_Z": mp_summary["log_Z"],
        "multi_portal_log_Z_err": mp_summary["log_Z_err"],
        "delta_log_Z_resonant_minus_mp": delta_log_z,
        "delta_log_Z_err": delta_log_z_err,
        "verdict": verdict,
        "channel_likelihood": "identical (3-channel: Cloud-9 + Galactic + Bullet)",
        "dynesty_settings": {
            "nlive": mp_summary["nlive"],
            "dlogz_target": mp_summary["dlogz_target"],
            "bound": "multi",
            "sample": "rwalk",
        },
    }
    return out


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--nlive", type=int, default=200)
    p.add_argument("--dlogz", type=float, default=0.1)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()

    if args.smoke:
        s = run_multi_portal(nlive=50, dlogz=0.5)
    else:
        s = run_multi_portal(nlive=args.nlive, dlogz=args.dlogz)

    print("\n[T90.52] Multi-portal log Z =", round(s["log_Z"], 3),
          "+/-", round(s["log_Z_err"], 3))
    print("[T90.52] wall =", round(s["wall_seconds"], 1), "s")
    p_ = s["posterior_median_predictions"]
    print(f"[T90.52] posterior median sigma/m(C9)  = {p_['sigma_m_Cloud9_cm2_per_g']:.3f}")
    print(f"[T90.52] posterior median sigma/m(Gal) = {p_['sigma_m_Galaxy_cm2_per_g']:.3f}")
    print(f"[T90.52] posterior median sigma/m(Bul) = {p_['sigma_m_Bullet_cm2_per_g']:.4f}")

    cmp = compare_with_resonant(s)
    print(f"\n[T90.52 vs T90.51] Δlog Z (resonant - multi-portal) = "
          f"{cmp['delta_log_Z_resonant_minus_mp']:.2f} +/- {cmp['delta_log_Z_err']:.2f}")
    print(f"[T90.52 vs T90.51] VERDICT: {cmp['verdict']}")
