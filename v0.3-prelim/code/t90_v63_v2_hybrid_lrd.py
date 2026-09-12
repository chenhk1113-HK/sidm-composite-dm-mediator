"""
T90.63 v2 -- Hybrid 10D joint fit with REFINED LRD channel (6 channels).

Replaces the v1 simplified Gaussian per-bin LRD likelihood with the
full UV luminosity function likelihood from t90_v63_lrd_channel_v2.

REFINEMENTS over v1:
- UV LF bins (10 bins across z=4.5-8.5) instead of single n_LRD per z
- Bolometric correction from arXiv:2509.05434 (Lbol/L5100=5, not 10)
- Includes dust attenuation A_V ~ 1 mag (makes M_UV predictions match obs)
- Real M_BH -> M_UV mapping via accretion + bolometric corrections
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dynesty  # type: ignore

from t90_v54_hybrid_sigma_m import sigma_m_hybrid
from t90_v57_hybrid_ksfr import (
    unpack_theta_10,
    loglike_hybrid_5ch,
    prior_transform_10,
    LOG_RANGES_10,
)

# Use v2 channel
from t90_v63_lrd_channel_v2 import (
    loglike_lrd_jiang2026_v2,
    LRD_UVLF_BINS,
    provenance_v2,
)

# ============================================================================
# Channel enable/disable (per project convention)
# ============================================================================

LRD_ENABLED = os.environ.get("T90_LRD_DISABLE", "0") != "1"
KSFR_ENABLED = os.environ.get("T90_KSFR_DISABLE", "1") != "1"  # default off

# ============================================================================
# Bounds (10D: 9 T90 hybrid + mu_x) -- same as T90.57
# ============================================================================

# Reuse T90.57's bounds


def loglike_lrd_for_hybrid(theta_10, enabled=True):
    """
    Compute LRD log-likelihood for the hybrid posterior.

    Uses T90 hybrid's sigma_m(v) at v=30 km/s (representative high-z halo
    virial velocity at z=5-8 where gravothermal collapse operates).
    """
    theta_9, mu_x = unpack_theta_10(theta_10)
    try:
        r_v30 = sigma_m_hybrid(30.0, theta_9)
        sigma_m_v30_cm2_per_g = r_v30["sigma_m_total_cm2_per_g"]
        if sigma_m_v30_cm2_per_g <= 0:
            return -np.inf
        sigma_m_log = math.log10(sigma_m_v30_cm2_per_g)
        return loglike_lrd_jiang2026_v2(sigma_m_log, enabled=enabled)
    except Exception:
        return -np.inf


def loglike_6ch_full(theta_10, lrd_enabled=True):
    """
    Full 6-channel log-likelihood:
      - 5 channels from T90.57 (Cloud-9, Galactic, Bullet, LZ, optional KSFR)
      - LRD channel from t90_v63_lrd_channel_v2
    """
    # 5-channel likelihood (T90.57)
    # Note: KSFR is controlled by env var inside loglike_hybrid_5ch, not kwarg
    ll_5ch = loglike_hybrid_5ch(theta_10)

    # LRD likelihood
    ll_lrd = loglike_lrd_for_hybrid(theta_10, enabled=lrd_enabled)

    if not np.isfinite(ll_5ch) or not np.isfinite(ll_lrd):
        return -np.inf

    return float(ll_5ch + ll_lrd)


def run_dynesty(nlive=500, dlogz=0.1, lrd_enabled=True, ksfr_enabled=False, label=""):
    """Run the dynesty nested sampling for the 6-channel likelihood."""
    sampler = dynesty.NestedSampler(
        loglike_6ch_full,
        prior_transform_10,
        ndim=10,
        nlive=nlive,
        logl_args=({"lrd_enabled": lrd_enabled},),
        sample="rwalk",
    )
    sampler.run_nested(dlogz=dlogz, print_progress=False)
    results = sampler.results
    return results


def summarize(results, label="t90_v63_v2"):
    """Summarize posterior results."""
    log_z_arr = np.atleast_1d(np.asarray(results["logz"]))
    log_z = float(log_z_arr[-1])
    log_z_err_arr = np.atleast_1d(np.asarray(results["logzerr"]))
    log_z_err = float(log_z_err_arr[-1])
    weights = np.exp(np.asarray(results["logwt"]) - log_z)
    samples = np.asarray(results["samples"])

    # Posterior medians and 16/84 percentiles
    medians = np.median(samples, axis=0)
    p16 = np.percentile(samples, 16, axis=0)
    p84 = np.percentile(samples, 84, axis=0)

    # Compute derived quantities at median
    theta_med = medians
    theta_9_med, mu_x_med = unpack_theta_10(theta_med)

    sigma_m_dict = sigma_m_hybrid(30.0, theta_9_med)
    sigma_m_v30 = sigma_m_dict["sigma_m_total_cm2_per_g"]
    sigma_m_c9 = sigma_m_hybrid(1000.0, theta_9_med)["sigma_m_total_cm2_per_g"]
    sigma_m_gal = sigma_m_hybrid(200.0, theta_9_med)["sigma_m_total_cm2_per_g"]
    sigma_m_bul = sigma_m_hybrid(50.0, theta_9_med)["sigma_m_total_cm2_per_g"]

    summary = {
        "label": label,
        "log_Z": float(log_z),
        "log_Z_err": float(log_z_err),
        "n_samples": len(samples),
        "posterior_medians": {
            "log_m_chi_GeV": float(medians[0]),
            "log_m_phi_A_MeV": float(medians[1]),
            "g_chi_A": float(medians[2]),
            "log_m_phi_B_MeV": float(medians[3]),
            "g_chi_B": float(medians[4]),
            "log_E_R_eV": float(medians[5]),
            "log_Gamma_R_eV": float(medians[6]),
            "log_sigma_0": float(medians[7]),
            "log_alpha_Y": float(medians[8]),
            "log_mu_x": float(medians[9]),
        },
        "posterior_p16": {
            f"log_p16_{i}": float(p16[i]) for i in range(10)
        },
        "posterior_p84": {
            f"log_p84_{i}": float(p84[i]) for i in range(10)
        },
        "derived_at_median": {
            "sigma_m_Cloud9_cm2_per_g": float(sigma_m_c9),
            "sigma_m_Galaxy_cm2_per_g": float(sigma_m_gal),
            "sigma_m_Bullet_cm2_per_g": float(sigma_m_bul),
            "sigma_m_v30_cm2_per_g": float(sigma_m_v30),
            "mu_x": float(mu_x_med),
            "m_phi_A_MeV": float(10 ** medians[1]),
        },
        "lrd_enabled": LRD_ENABLED,
        "ksfr_enabled": KSFR_ENABLED,
        "lrds_obs_bins": len(LRD_UVLF_BINS),
        "provenance": provenance_v2(),
    }

    # Print
    print(f"[T90.63 v2] {label}: log Z = {log_z:.3f} +/- {log_z_err:.3f}")
    print(f"  sigma/m(Cloud-9) = {sigma_m_c9:.3f}")
    print(f"  sigma/m(Galaxy)  = {sigma_m_gal:.3f}")
    print(f"  sigma/m(Bullet)  = {sigma_m_bul:.5f}")
    print(f"  sigma/m(v=30)    = {sigma_m_v30:.4f} cm^2/g (log10 = {math.log10(sigma_m_v30):.2f})")
    print(f"  mu_x             = {mu_x_med:.3e} mu_N")
    print(f"  m_phi_A          = {10**medians[1]:.1f} MeV")
    return summary


def main():
    parser = argparse.ArgumentParser(description="T90.63 v2: 6-channel hybrid with refined LRD likelihood")
    parser.add_argument("--smoke", action="store_true", help="Smoke test mode (nlive=50)")
    parser.add_argument("--nlive", type=int, default=500, help="Number of live points")
    parser.add_argument("--dlogz", type=float, default=0.1, help="dlogz convergence criterion")
    parser.add_argument("--lrd", choices=["on", "off"], default="on", help="Enable LRD channel")
    parser.add_argument("--ksfr", choices=["on", "off"], default="off", help="Enable KSFR channel")
    parser.add_argument("--out", default="data/results/t90_v63_v2_hybrid_6ch_joint_posterior.json", help="Output file")
    args = parser.parse_args()

    nlive = 50 if args.smoke else args.nlive
    lrd_enabled = (args.lrd == "on") and LRD_ENABLED
    ksfr_enabled = (args.ksfr == "on") and KSFR_ENABLED
    label = f"T90.63 v2 hybrid 6ch (LRD {args.lrd}, KSFR {args.ksfr})"

    print(f"[T90.63 v2] Running {label}")
    print(f"  nlive = {nlive}, dlogz = {args.dlogz}")
    print(f"  LRD enabled: {lrd_enabled}, KSFR enabled: {ksfr_enabled}")

    t0 = time.time()
    results = run_dynesty(
        nlive=nlive, dlogz=args.dlogz,
        lrd_enabled=lrd_enabled, ksfr_enabled=ksfr_enabled,
        label=label,
    )
    wall = time.time() - t0

    summary = summarize(results, label=label)
    summary["wall_seconds"] = wall

    # Save
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[T90.63 v2] Results saved to {out_path}")
    print(f"[T90.63 v2] Wall time: {wall:.1f}s")


if __name__ == "__main__":
    main()
