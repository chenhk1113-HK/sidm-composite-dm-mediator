"""
T90.63 -- Hybrid 10D joint fit with LRD channel (6 channels).

Adds the LRD (Little Red Dot) channel via SIDM core collapse
(Jiang et al. 2026 ApJL 996 L19, arXiv:2503.23710) on top of the
T90.57 5-channel hybrid (Cloud-9 + Galactic + Bullet + LZ + KSFR).

The LRD channel wraps `loglike_lrd_jiang2026(sigma_m_log)` from
`t90_v63_lrd_channel.py`, which expects:
    sigma_m_log = log10(sigma/m in cm^2/g)

The hybrid 10D theta gives sigma_m_total_cm2_per_g as a function of
velocity. For the LRD channel, we evaluate at a single characteristic
velocity v=30 km/s (representative of high-z halo virial velocities
at z=5-8), then take log10.

The KSFR/PCAC channel and LRD channel both can be toggled via env vars.

References:
    T90.57 (predecessor, 5-channel hybrid)
    t90_v63_lrd_channel.py (LRD channel implementation)
    Jiang, F. et al. 2026, ApJL 996, L19, arXiv:2503.23710
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Reuse T90.57's prior + likelihood + KSFR handling
from t90_v57_hybrid_ksfr import (
    loglike_hybrid_5ch,
    prior_transform_10,
    LOG_RANGES_10,
    PARAM_NAMES_10,
    IS_LOG_10,
    unpack_theta_10,
    KSFR_ENABLED,
    set_ksfr_enabled,
)
from t90_v63_lrd_channel import loglike_lrd_jiang2026, provenance as lrd_provenance


# LRD enabled flag -- read env var at import time per project convention.
LRD_ENABLED = os.environ.get("T90_LRD_DISABLE", "1") != "1"


def set_lrd_enabled(enabled: bool):
    """Runtime override for LRD_ENABLED (also updates env var for downstream code)."""
    global LRD_ENABLED
    LRD_ENABLED = enabled
    os.environ["T90_LRD_DISABLE"] = "0" if enabled else "1"


def loglike_hybrid_6ch(theta_log):
    """11D joint 6-channel log-likelihood for hybrid + LZ + KSFR + LRD.

    theta_log: 10D vector in mixed log/linear form (same as T90.57).
    The 11th dimension is conceptually the KSFR Nc/Nf but we use defaults.
    """
    # Same prior bounds enforcement as T90.57
    for i in range(10):
        lo, hi = LOG_RANGES_10[i]
        if not (lo <= theta_log[i] <= hi):
            return -np.inf

    # T90.57's 5-channel likelihood (Cloud-9 + Galactic + Bullet + LZ + KSFR)
    ll_5ch = loglike_hybrid_5ch(theta_log)
    if not np.isfinite(ll_5ch):
        return -np.inf

    # LRD channel (Jiang et al. 2026) -- only fires if enabled
    if LRD_ENABLED:
        theta_9, mu_x = unpack_theta_10(theta_log)
        # Compute sigma/m at v=30 km/s (representative high-z halo velocity)
        from t90_v54_hybrid_sigma_m import sigma_m_hybrid
        r_v30 = sigma_m_hybrid(30.0, theta_9)
        sigma_m_cm2_per_g = r_v30["sigma_m_total_cm2_per_g"]
        if sigma_m_cm2_per_g <= 0:
            # No SIDM interaction -> no LRD production
            ll_lrd = -np.inf
        else:
            sigma_m_log = np.log10(sigma_m_cm2_per_g)
            ll_lrd = loglike_lrd_jiang2026(sigma_m_log)
        if not np.isfinite(ll_lrd):
            return -np.inf
    else:
        ll_lrd = 0.0

    total = ll_5ch + ll_lrd
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


def run_hybrid_joint_fit_6ch(nlive: int = 500, dlogz: float = 0.1,
                                output_dir: str = None):
    """Run the 10D hybrid 6-channel joint fit (with KSFR and LRD if enabled)."""
    import dynesty

    if output_dir is None:
        if os.name == "nt":
            output_dir = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
        else:
            output_dir = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    sampler = dynesty.NestedSampler(
        loglike_hybrid_6ch,
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
    from t90_v54_hybrid_sigma_m import sigma_m_hybrid
    r_c9 = sigma_m_hybrid(28.0, med_theta_9)
    r_gal = sigma_m_hybrid(100.0, med_theta_9)
    r_bul = sigma_m_hybrid(3000.0, med_theta_9)
    r_v30 = sigma_m_hybrid(30.0, med_theta_9)

    c9_ok = 30.0 < r_c9["sigma_m_total_cm2_per_g"] < 500.0
    gal_ok = r_gal["sigma_m_total_cm2_per_g"] < 2.0
    bul_ok = r_bul["sigma_m_total_cm2_per_g"] < 0.5

    # LRD posterior prediction
    sigma_m_log_v30 = float(np.log10(r_v30["sigma_m_total_cm2_per_g"])) \
        if r_v30["sigma_m_total_cm2_per_g"] > 0 else -10.0
    from t90_v63_lrd_channel import summary_lrd_at_sigma_m
    lrd_pred = summary_lrd_at_sigma_m(sigma_m_log_v30)
    lrd_loglike = loglike_lrd_jiang2026(sigma_m_log_v30)

    summary = {
        "framework": "T90.63 hybrid 10D (multi-portal + resonance + Sommerfeld + LZ + KSFR/PCAC + LRD/Jiang2026)",
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
            "sigma_m_at_v30_cm2_per_g": float(r_v30["sigma_m_total_cm2_per_g"]),
            "log10_sigma_m_at_v30": sigma_m_log_v30,
            "mu_x_at_median": float(med_mu_x),
            "m_phi_A_MeV_at_median": float(med_theta_9[1]),
            "in_KSFR_box": bool(418.0 <= med_theta_9[1] <= 4180.0),
            "LRD_log10_n_at_z5": float(lrd_pred["log10_n_LRD_z5.0"]),
            "LRD_log10_n_at_z7": float(lrd_pred["log10_n_LRD_z7.0"]),
            "LRD_log10_n_at_z8.5": float(lrd_pred["log10_n_LRD_z8.5"]),
            "LRD_loglike_at_median": float(lrd_loglike),
        },
        "channel_satisfaction_at_median": {
            "Cloud9": bool(c9_ok),
            "Galaxy": bool(gal_ok),
            "Bullet": bool(bul_ok),
            "n_satisfied_3ch": int(c9_ok) + int(gal_ok) + int(bul_ok),
        },
        "channel_likelihood_match": (
            "T90.57 (C9 + Gal + Bul + LZ + KSFR) + LRD (Channel 16, "
            "Jiang et al. 2026 ApJL 996 L19, arXiv:2503.23710)"
        ),
        "lrd_provenance": lrd_provenance(),
        "ksfr_enabled": KSFR_ENABLED,
        "lrd_enabled": LRD_ENABLED,
    }
    out_path = Path(output_dir) / "t90_v63_hybrid_6ch_joint_posterior.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[T90.63] Wrote {out_path}")
    return summary


def compare_6ch(hybrid_summary: dict) -> dict:
    """Compare 6-channel log Z to T90.57 5-channel log Z."""
    log_z_h = hybrid_summary["log_Z"]
    log_z_h_err = hybrid_summary["log_Z_err"]
    lrd = hybrid_summary.get("lrd_enabled", False)
    ksfr = hybrid_summary.get("ksfr_enabled", False)
    cs = hybrid_summary["channel_satisfaction_at_median"]
    p_ = hybrid_summary["posterior_median_predictions"]

    return {
        "log_Z_hybrid_6ch": log_z_h,
        "log_Z_hybrid_6ch_err": log_z_h_err,
        "channels_satisfied_at_median_3ch": cs["n_satisfied_3ch"],
        "LRD_active": lrd,
        "KSFR_active": ksfr,
        "LRD_log10_n_at_z5": p_.get("LRD_log10_n_at_z5"),
        "LRD_loglike_at_median": p_.get("LRD_loglike_at_median"),
        "verdict": (
            f"6-channel fit (KSFR {'active' if ksfr else 'inactive'}, "
            f"LRD {'active' if lrd else 'inactive'})"
        ),
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--nlive", type=int, default=500)
    p.add_argument("--dlogz", type=float, default=0.1)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--ksfr", choices=["on", "off"], default="off",
                   help="Enable KSFR/PCAC channel (default off per v0.5 convention)")
    p.add_argument("--lrd", choices=["on", "off"], default="on",
                   help="Enable LRD channel (default on)")
    args = p.parse_args()

    if args.ksfr == "on":
        set_ksfr_enabled(True)
    if args.lrd == "off":
        set_lrd_enabled(False)

    if args.smoke:
        s = run_hybrid_joint_fit_6ch(nlive=50, dlogz=0.5)
    else:
        s = run_hybrid_joint_fit_6ch(nlive=args.nlive, dlogz=args.dlogz)

    print("\n[T90.63] Hybrid 6ch log Z =", round(s["log_Z"], 3),
          "+/-", round(s["log_Z_err"], 3))
    print("[T90.63] wall =", round(s["wall_seconds"], 1), "s")
    p_ = s["posterior_median_predictions"]
    cs = s["channel_satisfaction_at_median"]
    print(f"[T90.63] Posterior median:")
    print(f"  sigma/m(Cloud-9) = {p_['sigma_m_Cloud9_cm2_per_g']:.3f}")
    print(f"  sigma/m(Galaxy)  = {p_['sigma_m_Galaxy_cm2_per_g']:.3f}")
    print(f"  sigma/m(Bullet)  = {p_['sigma_m_Bullet_cm2_per_g']:.4f}")
    print(f"  sigma/m(v=30)    = {p_['sigma_m_at_v30_cm2_per_g']:.3f} cm^2/g (log10 = {p_['log10_sigma_m_at_v30']:.2f})")
    print(f"  mu_x at median   = {p_['mu_x_at_median']:.3e} mu_N")
    print(f"  m_phi_A at med   = {p_['m_phi_A_MeV_at_median']:.2f} MeV")
    print(f"  in_KSFR_box      = {p_['in_KSFR_box']}")
    print(f"[T90.63] LRD predictions:")
    print(f"  log10(n_LRD at z=5)  = {p_['LRD_log10_n_at_z5']:.2f}")
    print(f"  log10(n_LRD at z=7)  = {p_['LRD_log10_n_at_z7']:.2f}")
    print(f"  log10(n_LRD at z=8.5)= {p_['LRD_log10_n_at_z8.5']:.2f}")
    print(f"  LRD loglike at median= {p_['LRD_loglike_at_median']:.2f}")
    print(f"[T90.63] 3-ch satisfaction: {cs['n_satisfied_3ch']}/3")
    print(f"[T90.63] KSFR enabled: {s['ksfr_enabled']}, LRD enabled: {s['lrd_enabled']}")