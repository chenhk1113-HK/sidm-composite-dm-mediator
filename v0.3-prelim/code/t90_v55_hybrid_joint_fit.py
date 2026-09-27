#!/usr/bin/env python
"""
T90.55 -- Hybrid multi-portal + resonance joint fit (9D, 3 channels).

Joint fit of the T90.54 hybrid sigma/m(v) form on the same 3-channel
likelihood (Cloud-9 + Galactic + Bullet) used in T90.51 (resonant) and
T90.52 (multi-portal).

This is the third point in the apples-to-apples comparison:
  - T90.51 resonant:  log Z = -2.435 +/- 0.064
  - T90.52 multi-portal: log Z = -2.229 +/- 0.067
  - T90.55 hybrid:    log Z = ???

If the hybrid fits the data better than both special cases (Delta log Z > 2
or so in favor of hybrid), it means the data wants BOTH mechanisms operating
together. If hybrid fits worse or equivalent, the simpler special case is
preferred (Occam's razor via Bayes factor).

Parameters (9D, mixed log/linear, same as T90.54 prior_transform_9):
    theta = (m_chi_GeV,            # log-uniform 3 GeV to 1 TeV
             m_phi_A_MeV, g_chi_A, # portal A: log-uniform m, linear g
             m_phi_B_MeV, g_chi_B, # portal B: log-uniform m, linear g
             E_R_eV, Gamma_R_eV,   # resonance energy, width
             sigma_0_cm2_per_g,    # background sigma/m
             alpha_Y)              # Sommerfeld coupling

Likelihood: 3-channel sum as in T90.51.

References:
    T90.51 (resonant joint fit, predecessor)
    T90.52 (multi-portal joint fit, predecessor)
    T90.54 (hybrid sigma/m form, predecessor)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Reuse the T90.51 channel likelihoods -- this is the whole point.
from t90_v51_resonant_joint_fit import (
    loglike_cloud9,
    loglike_galaxy,
    loglike_bullet,
)

# Reuse the T90.54 hybrid sigma/m and prior.
from t90_v54_hybrid_sigma_m import (
    sigma_m_hybrid,
    LOG_RANGES,
    PARAM_NAMES,
    IS_LOG,
    unpack_theta,
)


def loglike_hybrid_3ch(theta_log):
    """Joint 3-channel log-likelihood for hybrid sigma/m(v).

    theta_log: 9D vector in mixed log/linear form (output of prior_transform_9).
    """
    # Prior bounds enforcement -- required for dynesty to compute proper
    # evidence. If any prior bound is violated, return -inf.
    for i in range(9):
        lo, hi = LOG_RANGES[i]
        if not (lo <= theta_log[i] <= hi):
            return -np.inf

    # Convert to physical units
    theta_phys = unpack_theta(theta_log)

    # Compute sigma/m at the 3 canonical velocities via the hybrid form
    sm_c9 = sigma_m_hybrid(28.0, theta_phys)["sigma_m_total_cm2_per_g"]
    sm_gal = sigma_m_hybrid(100.0, theta_phys)["sigma_m_total_cm2_per_g"]
    sm_bul = sigma_m_hybrid(3000.0, theta_phys)["sigma_m_total_cm2_per_g"]

    # Numerical safety
    if sm_c9 <= 0 or sm_gal <= 0 or sm_bul <= 0:
        return -np.inf
    if not (np.isfinite(sm_c9) and np.isfinite(sm_gal) and np.isfinite(sm_bul)):
        return -np.inf

    total = (loglike_cloud9(sm_c9)
             + loglike_galaxy(sm_gal)
             + loglike_bullet(sm_bul))
    if not np.isfinite(total):
        return -np.inf
    return total


def prior_transform_9(u):
    """9D unit cube -> mixed log/linear parameter vector.

    Convention: theta output is in the same units as the LOG_RANGES bounds.
    For IS_LOG=True params, theta[i] is log10(x). For IS_LOG=False params,
    theta[i] is x directly.

    Layout (matches T90.54):
      [log_m_chi, log_m_phi_A, g_A (linear),
       log_m_phi_B, g_B (linear),
       log_E_R, log_Gamma, log_sigma_0, log_alpha_Y]
    """
    theta = np.zeros(9)
    for i in range(9):
        lo, hi = LOG_RANGES[i]
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


def run_hybrid_joint_fit(nlive: int = 500, dlogz: float = 0.05,
                          output_dir: str = None):
    import dynesty

    if output_dir is None:
        if os.name == "nt":
            output_dir = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
        else:
            output_dir = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    sampler = dynesty.NestedSampler(
        loglike_hybrid_3ch,
        prior_transform_9,
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
    samples = res.samples  # shape (N, 9) in mixed log/linear form
    weights = np.exp(res.logwt - res.logz[-1])

    # Posterior medians (with 16/84% CIs)
    medians = {}
    for i in range(9):
        v = samples[:, i]
        medians[PARAM_NAMES[i]] = {
            "median": float(_weighted_quantile(v, weights, 0.5)),
            "p16": float(_weighted_quantile(v, weights, 0.16)),
            "p84": float(_weighted_quantile(v, weights, 0.84)),
        }

    # Posterior median predictions: convert median theta_log -> phys -> sigma/m
    med_log = np.array([medians[n]["median"] for n in PARAM_NAMES])
    med_phys = unpack_theta(med_log)
    r_c9 = sigma_m_hybrid(28.0, med_phys)
    r_gal = sigma_m_hybrid(100.0, med_phys)
    r_bul = sigma_m_hybrid(3000.0, med_phys)

    # Channel satisfaction at posterior median
    c9_ok = 30.0 < r_c9["sigma_m_total_cm2_per_g"] < 500.0
    gal_ok = r_gal["sigma_m_total_cm2_per_g"] < 2.0
    bul_ok = r_bul["sigma_m_total_cm2_per_g"] < 0.5

    summary = {
        "framework": "T90.54 hybrid (multi-portal + resonance + Sommerfeld)",
        "log_Z": log_z,
        "log_Z_err": log_z_err,
        "wall_seconds": wall,
        "nlive": nlive,
        "dlogz_target": dlogz,
        "ndim": 9,
        "n_samples": int(samples.shape[0]),
        "posterior_medians": medians,
        "posterior_median_predictions": {
            "sigma_m_Cloud9_cm2_per_g": float(r_c9["sigma_m_total_cm2_per_g"]),
            "sigma_m_Galaxy_cm2_per_g": float(r_gal["sigma_m_total_cm2_per_g"]),
            "sigma_m_Bullet_cm2_per_g": float(r_bul["sigma_m_total_cm2_per_g"]),
            "portal_Cloud9_cm2_per_g": float(r_c9["sigma_m_portal_cm2_per_g"]),
            "portal_Galaxy_cm2_per_g": float(r_gal["sigma_m_portal_cm2_per_g"]),
            "portal_Bullet_cm2_per_g": float(r_bul["sigma_m_portal_cm2_per_g"]),
            "resonant_Cloud9_cm2_per_g": float(r_c9["sigma_m_resonant_cm2_per_g"]),
            "resonant_Galaxy_cm2_per_g": float(r_gal["sigma_m_resonant_cm2_per_g"]),
            "resonant_Bullet_cm2_per_g": float(r_bul["sigma_m_resonant_cm2_per_g"]),
        },
        "channel_satisfaction_at_median": {
            "Cloud9": bool(c9_ok),
            "Galaxy": bool(gal_ok),
            "Bullet": bool(bul_ok),
            "n_satisfied": int(c9_ok) + int(gal_ok) + int(bul_ok),
        },
        "channel_likelihood_match": "T90.51 (Cloud-9 Gaussian + Galactic 1-sided + Bullet 1-sided)",
    }
    out_path = Path(output_dir) / "t90_v55_hybrid_joint_posterior.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[T90.55] Wrote {out_path}")
    return summary


def compare_with_resonant_and_mp(hybrid_summary: dict,
                                  res_path: str = None,
                                  mp_path: str = None) -> dict:
    """Load T90.51 (resonant) and T90.52 (multi-portal) JSONs and compute
    3-way log Z comparison + verdict."""
    if os.name == "nt":
        base = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results")
    else:
        base = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")
    if res_path is None:
        res_path = base / "t90_v51_resonant_joint_posterior.json"
    if mp_path is None:
        mp_path = base / "t90_v52_multi_portal_joint_posterior.json"

    with open(res_path) as f:
        res = json.load(f)
    with open(mp_path) as f:
        mp = json.load(f)

    log_z_h = hybrid_summary["log_Z"]
    log_z_h_err = hybrid_summary["log_Z_err"]
    log_z_r = res["log_Z"]
    log_z_r_err = res["log_Z_err"]
    log_z_mp = mp["log_Z"]
    log_z_mp_err = mp["log_Z_err"]

    delta_h_r = log_z_h - log_z_r
    delta_h_r_err = float(np.hypot(log_z_h_err, log_z_r_err))
    delta_h_mp = log_z_h - log_z_mp
    delta_h_mp_err = float(np.hypot(log_z_h_err, log_z_mp_err))

    # Best of the three
    log_zs = {"hybrid": log_z_h, "resonant": log_z_r, "multi-portal": log_z_mp}
    winner = max(log_zs, key=log_zs.get)
    winner_log_z = log_zs[winner]

    # Jeffreys-scale verdict for hybrid vs each special case
    def verdict(d):
        if d > 5:
            return "VERY STRONG: hybrid preferred"
        elif d > 2.5:
            return "STRONG: hybrid preferred"
        elif d > 1:
            return "MODERATE: hybrid preferred"
        elif d > -1:
            return "INCONCLUSIVE"
        else:
            return "SPECIAL CASE PREFERRED"

    return {
        "log_Z_hybrid": log_z_h,
        "log_Z_hybrid_err": log_z_h_err,
        "log_Z_resonant": log_z_r,
        "log_Z_resonant_err": log_z_r_err,
        "log_Z_multi_portal": log_z_mp,
        "log_Z_multi_portal_err": log_z_mp_err,
        "winner": winner,
        "winner_log_Z": winner_log_z,
        "delta_log_Z_hybrid_minus_resonant": delta_h_r,
        "delta_log_Z_hybrid_minus_resonant_err": delta_h_r_err,
        "delta_log_Z_hybrid_minus_multi_portal": delta_h_mp,
        "delta_log_Z_hybrid_minus_multi_portal_err": delta_h_mp_err,
        "verdict_vs_resonant": verdict(delta_h_r),
        "verdict_vs_multi_portal": verdict(delta_h_mp),
        "channel_likelihood": "identical (3-channel: Cloud-9 + Galactic + Bullet)",
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--nlive", type=int, default=500)
    p.add_argument("--dlogz", type=float, default=0.05)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()

    if args.smoke:
        s = run_hybrid_joint_fit(nlive=50, dlogz=0.5)
    else:
        s = run_hybrid_joint_fit(nlive=args.nlive, dlogz=args.dlogz)

    print("\n[T90.55] Hybrid log Z =", round(s["log_Z"], 3),
          "+/-", round(s["log_Z_err"], 3))
    print("[T90.55] wall =", round(s["wall_seconds"], 1), "s")
    p_ = s["posterior_median_predictions"]
    cs = s["channel_satisfaction_at_median"]
    print(f"[T90.55] Posterior median sigma/m(Cloud-9) = {p_['sigma_m_Cloud9_cm2_per_g']:.3f}"
          f" (portal {p_['portal_Cloud9_cm2_per_g']:.3f} + resonant {p_['resonant_Cloud9_cm2_per_g']:.3f})")
    print(f"[T90.55] Posterior median sigma/m(Galaxy)  = {p_['sigma_m_Galaxy_cm2_per_g']:.3f}")
    print(f"[T90.55] Posterior median sigma/m(Bullet)  = {p_['sigma_m_Bullet_cm2_per_g']:.4f}")
    print(f"[T90.55] Channel satisfaction: {cs['n_satisfied']}/3"
          f"  (C9={cs['Cloud9']} Gal={cs['Galaxy']} Bul={cs['Bullet']})")

    cmp = compare_with_resonant_and_mp(s)
    print(f"\n[T90.55 vs T90.51/52]")
    print(f"  Δlog Z (hybrid - resonant)     = {cmp['delta_log_Z_hybrid_minus_resonant']:+.3f} +/- {cmp['delta_log_Z_hybrid_minus_resonant_err']:.3f}  -> {cmp['verdict_vs_resonant']}")
    print(f"  Δlog Z (hybrid - multi-portal) = {cmp['delta_log_Z_hybrid_minus_multi_portal']:+.3f} +/- {cmp['delta_log_Z_hybrid_minus_multi_portal_err']:.3f}  -> {cmp['verdict_vs_multi_portal']}")
    print(f"  WINNER: {cmp['winner']} (log Z = {cmp['winner_log_Z']:.3f})")
