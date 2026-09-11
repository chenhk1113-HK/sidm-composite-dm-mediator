#!/usr/bin/env python
"""
T90.57 -- Hybrid 11D joint fit with KSFR/PCAC channel (5 channels).

Adds the KSFR/PCAC theoretical validity mask (Channel 15 from T41) on top
of the T90.56 4-channel hybrid (Cloud-9 + Galactic + Bullet + LZ).

The KSFR/PCAC channel wraps `loglike_ksfr_pcac_validity(theta, N_dc, N_f)`
from `ksfr_pcac_validity.py`, which expects a 5-tuple of physical parameters:
    (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha)

Mapping from the hybrid 10D theta to KSFR's expected 5-tuple:
    log_m_phi_MeV = theta[1]               # log m_phi_A
    log_m_chi_GeV = theta[0]               # log m_chi
    g_chi         = theta[2]               # g_A
    log_epsilon   = -50.0                  # nuisance (way below LZ detection)
    log_alpha     = theta[8]               # log alpha_Y (Sommerfeld coupling)

The KSFR validity mask rejects theta points where m_phi_A is outside the
KSFR box [418, 4180] MeV (for default Nc=Nf=3). This is a HARD mask —
returns -inf if violated, 0 if satisfied.

Per the project's convention (v0.5 default), KSFR is DISABLED by default
via the env var SIDM_DISABLE_KSFR_MASK=1. To enable it, set
SIDM_DISABLE_KSFR_MASK=0 before running. This module reads the env var
at import time and respects it.

References:
    T90.56 (predecessor, 4-channel)
    ksfr_pcac_validity.py (KSFR mask implementation)
    REVIEWER_AUDIT_R13.md (R13 H1 concern, KSFR/PCAC validity)
    MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §6
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Reuse T90.56's prior + likelihood + WIMpy handling
from t90_v56_hybrid_lz import (
    loglike_hybrid_4ch,
    prior_transform_10 as prior_transform_10_v56,
    LOG_RANGES_10,
    PARAM_NAMES_10,
    IS_LOG_10,
    unpack_theta_10,
    _check_wimpy,
)
from ksfr_pcac_validity import loglike_ksfr_pcac_validity


# KSFR enabled flag -- read env var at import time per project convention.
# Per project convention: SIDM_DISABLE_KSFR_MASK=1 disables (default v0.5).
KSFR_ENABLED = os.environ.get("SIDM_DISABLE_KSFR_MASK", "1") == "0"


def set_ksfr_enabled(enabled: bool):
    """Runtime override for KSFR_ENABLED (also updates env var for downstream code)."""
    global KSFR_ENABLED
    KSFR_ENABLED = enabled
    os.environ["SIDM_DISABLE_KSFR_MASK"] = "0" if enabled else "1"


# Re-export T90.56's prior_transform_10 under the same name
prior_transform_10 = prior_transform_10_v56


def loglike_hybrid_5ch(theta_log):
    """11D joint 5-channel log-likelihood for hybrid + LZ + KSFR/PCAC.

    theta_log: 10D vector in mixed log/linear form (same as T90.56).
    The 11th dimension is conceptually the KSFR Nc/Nf but we use defaults.
    """
    # Same prior bounds enforcement as T90.56
    for i in range(10):
        lo, hi = LOG_RANGES_10[i]
        if not (lo <= theta_log[i] <= hi):
            return -np.inf

    # T90.56's 4-channel likelihood (Cloud-9 + Galactic + Bullet + LZ)
    ll_4ch = loglike_hybrid_4ch(theta_log)
    if not np.isfinite(ll_4ch):
        return -np.inf

    # KSFR/PCAC channel (Channel 15) -- only fires if enabled
    if KSFR_ENABLED:
        theta_9, mu_x = unpack_theta_10(theta_log)
        m_phi_A_MeV = theta_9[1]
        g_A = theta_9[2]
        alpha_Y = theta_9[8]
        m_chi_GeV = theta_9[0]
        # Build KSFR 5-tuple
        ksfr_theta = (
            np.log10(m_phi_A_MeV),
            np.log10(m_chi_GeV),
            g_A,
            -50.0,                # log_epsilon: nuisance, far below LZ
            np.log10(alpha_Y) if alpha_Y > 0 else -10.0,
        )
        ll_ksfr = loglike_ksfr_pcac_validity(ksfr_theta)
        if not np.isfinite(ll_ksfr):
            return -np.inf
    else:
        ll_ksfr = 0.0

    total = ll_4ch + ll_ksfr
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


def run_hybrid_joint_fit_5ch(nlive: int = 500, dlogz: float = 0.1,
                                output_dir: str = None):
    """Run the 10D hybrid 5-channel joint fit (with KSFR if enabled)."""
    import dynesty

    if output_dir is None:
        if os.name == "nt":
            output_dir = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
        else:
            output_dir = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    sampler = dynesty.NestedSampler(
        loglike_hybrid_5ch,
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
    # Compute σ/m at the 3 canonical velocities
    from t90_v54_hybrid_sigma_m import sigma_m_hybrid
    r_c9 = sigma_m_hybrid(28.0, med_theta_9)
    r_gal = sigma_m_hybrid(100.0, med_theta_9)
    r_bul = sigma_m_hybrid(3000.0, med_theta_9)

    c9_ok = 30.0 < r_c9["sigma_m_total_cm2_per_g"] < 500.0
    gal_ok = r_gal["sigma_m_total_cm2_per_g"] < 2.0
    bul_ok = r_bul["sigma_m_total_cm2_per_g"] < 0.5

    summary = {
        "framework": "T90.57 hybrid 10D (multi-portal + resonance + Sommerfeld + LZ + KSFR/PCAC)",
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
            "m_phi_A_MeV_at_median": float(med_theta_9[1]),
            "in_KSFR_box": bool(418.0 <= med_theta_9[1] <= 4180.0),
        },
        "channel_satisfaction_at_median": {
            "Cloud9": bool(c9_ok),
            "Galaxy": bool(gal_ok),
            "Bullet": bool(bul_ok),
            "n_satisfied_3ch": int(c9_ok) + int(gal_ok) + int(bul_ok),
        },
        "channel_likelihood_match": "T90.56 (C9 + Gal + Bul + LZ) + KSFR/PCAC (Channel 15)",
        "wimpy_available": _check_wimpy(),
        "ksfr_enabled": KSFR_ENABLED,
    }
    out_path = Path(output_dir) / "t90_v57_hybrid_5ch_joint_posterior.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[T90.57] Wrote {out_path}")
    return summary


def compare_5ch(hybrid_summary: dict,
                res_path: str = None) -> dict:
    """Compare 5-channel log Z to T90.56 4-channel log Z."""
    log_z_h = hybrid_summary["log_Z"]
    log_z_h_err = hybrid_summary["log_Z_err"]
    wimpy = hybrid_summary.get("wimpy_available", False)
    ksfr = hybrid_summary.get("ksfr_enabled", False)
    cs = hybrid_summary["channel_satisfaction_at_median"]

    return {
        "log_Z_hybrid_5ch": log_z_h,
        "log_Z_hybrid_5ch_err": log_z_h_err,
        "channels_satisfied_at_median_3ch": cs["n_satisfied_3ch"],
        "LZ_active": wimpy,
        "KSFR_active": ksfr,
        "verdict": f"5-channel fit (LZ {'active' if wimpy else 'silent'}, KSFR {'active' if ksfr else 'inactive'})",
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--nlive", type=int, default=500)
    p.add_argument("--dlogz", type=float, default=0.1)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--ksfr", choices=["on", "off"], default="off",
                   help="Enable KSFR/PCAC channel (default off per v0.5 convention)")
    args = p.parse_args()

    if args.ksfr == "on":
        set_ksfr_enabled(True)

    if args.smoke:
        s = run_hybrid_joint_fit_5ch(nlive=50, dlogz=0.5)
    else:
        s = run_hybrid_joint_fit_5ch(nlive=args.nlive, dlogz=args.dlogz)

    print("\n[T90.57] Hybrid 5ch log Z =", round(s["log_Z"], 3),
          "+/-", round(s["log_Z_err"], 3))
    print("[T90.57] wall =", round(s["wall_seconds"], 1), "s")
    p_ = s["posterior_median_predictions"]
    cs = s["channel_satisfaction_at_median"]
    print(f"[T90.57] Posterior median:")
    print(f"  sigma/m(Cloud-9) = {p_['sigma_m_Cloud9_cm2_per_g']:.3f}")
    print(f"  sigma/m(Galaxy)  = {p_['sigma_m_Galaxy_cm2_per_g']:.3f}")
    print(f"  sigma/m(Bullet)  = {p_['sigma_m_Bullet_cm2_per_g']:.4f}")
    print(f"  mu_x at median   = {p_['mu_x_at_median']:.3e} mu_N")
    print(f"  m_phi_A at med   = {p_['m_phi_A_MeV_at_median']:.2f} MeV")
    print(f"  in_KSFR_box      = {p_['in_KSFR_box']}")
    print(f"[T90.57] 3-ch satisfaction: {cs['n_satisfied_3ch']}/3")
    print(f"[T90.57] WIMpy available: {s['wimpy_available']}, KSFR enabled: {s['ksfr_enabled']}")
