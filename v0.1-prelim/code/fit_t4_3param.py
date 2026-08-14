#!/usr/bin/env python
"""
T4 single-galaxy fit with Υ_d (stellar mass-to-light) marginalization.

SPARC publishes Vdisk, Vbul at M/L = 1 (solMass/solLum). The TRUE stellar
M/L is uncertain, especially at [3.6] micron (typically Υ_d ~ 0.5-1.5
from stellar population synthesis, but can be 0.1-10 in extreme cases).

Standard convention (Lelli+ 2016c, Li+ 2020):
    Vdisk^2 (true) = Υ_d * Vdisk^2 (published)
    Vbul^2 (true)  = Υ_b * Vbul^2 (published)
    Vbar^2 (true) = Υ_d * Vdisk^2 + Υ_b * Vbul^2 + (Vgas * 1.33)^2

For v0.1-final we marginalize only over Υ_d (disk); we fix Υ_b = 1.4
(bulge, standard value from stellar populations).

Prior on Υ_d: log-uniform in [0.1, 10] (broad, weakly informative).

Free parameters per fit:
    NFW:     (log_rho_s, log_r_s, log_Υ_d)
    Burkert: (log_rho_c, log_r_c, log_Υ_d)

Output: same JSON shape as T1/T2 but with Υ_d marginalization.
"""
from __future__ import annotations
import sys
import time
import json
from pathlib import Path

import numpy as np
import dynesty

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sparc_loader import load_one_sparc
from halo_profiles import (
    V_NFW, V_Burkert,
    NFW_LOG_RHO_S_RANGE, NFW_LOG_R_S_RANGE,
    BURKERT_LOG_RHO_C_RANGE, BURKERT_LOG_R_C_RANGE,
    chi2_sparc,
)

DATA_DIR = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.1-prelim/data")
RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.1-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Standard values
XI_B_FIXED = 1.4  # bulge M/L at [3.6] (Lelli+ 2016c standard)
XI_D_LOG_RANGE = (-1.0, 1.0)  # log10(XI_d) in [0.1, 10]

NLIVE = 200
DLOGZ = 0.10

PROFILES_3P = {
    "NFW":     (V_NFW,     NFW_LOG_RHO_S_RANGE,     NFW_LOG_R_S_RANGE),
    "Burkert": (V_Burkert, BURKERT_LOG_RHO_C_RANGE,  BURKERT_LOG_R_C_RANGE),
}


def vbar_sq_with_XI(ga, log_XI_d: float) -> np.ndarray:
    """Baryonic V^2 with Υ_d scaling applied to disk component."""
    XI_d = 10**log_XI_d
    return XI_d * ga.Vdisk**2 + XI_B_FIXED * ga.Vbul**2 + (ga.Vgas * 1.33)**2


def fit_one_galaxy_3p(gal_name: str, profile_name: str, nlive: int = NLIVE) -> dict:
    if profile_name not in PROFILES_3P:
        raise ValueError(f"Unknown profile {profile_name}")
    halo_fn, range1, range2 = PROFILES_3P[profile_name]
    ga = load_one_sparc(DATA_DIR, gal_name)
    print(f"[T4 fit {gal_name} {profile_name}] loaded {ga}")

    def loglike(theta):
        log_rho, log_r, log_XI_d = theta
        # Prior on halo
        if not (range1[0] <= log_rho <= range1[1]):
            return -np.inf
        if not (range2[0] <= log_r <= range2[1]):
            return -np.inf
        # Prior on XI_d (log-uniform)
        if not (XI_D_LOG_RANGE[0] <= log_XI_d <= XI_D_LOG_RANGE[1]):
            return -np.inf
        rho, r_scale = 10**log_rho, 10**log_r
        Vbar_sq = vbar_sq_with_XI(ga, log_XI_d)
        halo_V2 = halo_fn(ga.Rad, rho, r_scale)
        V_total = np.sqrt(Vbar_sq + halo_V2)
        return -0.5 * float(np.sum(((ga.Vobs - V_total) / np.maximum(ga.errV, 1e-3))**2))

    def prior_transform(u):
        return np.array([
            range1[0] + u[0] * (range1[1] - range1[0]),
            range2[0] + u[1] * (range2[1] - range2[0]),
            XI_D_LOG_RANGE[0] + u[2] * (XI_D_LOG_RANGE[1] - XI_D_LOG_RANGE[0]),
        ])

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike,
        prior_transform=prior_transform,
        ndim=3,
        nlive=nlive,
        bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    theta_map = samples[imap]

    # chi^2 at MAP (with Υ_d at MAP)
    rho_map, r_map, log_XI_d_map = theta_map
    Vbar_sq_map = vbar_sq_with_XI(ga, log_XI_d_map)
    V_total_map = np.sqrt(Vbar_sq_map + halo_fn(ga.Rad, 10**rho_map, 10**r_map))
    chi2_at_map = chi2_sparc(ga, V_total_map)
    chi2_red = chi2_at_map / max(ga.n_pts - 3, 1)

    out = {
        "galaxy": gal_name,
        "profile": profile_name,
        "n_pts": int(ga.n_pts),
        "n_params": 3,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "chi2_at_MAP": chi2_at_map,
        "chi2_reduced_at_MAP": chi2_red,
        "theta_MAP": {
            "log_param1": float(theta_map[0]),
            "log_param2": float(theta_map[1]),
            "log_XI_d":   float(theta_map[2]),
        },
        "posterior_summary": {
            "log_param1_median": float(np.median(samples[:, 0])),
            "log_param2_median": float(np.median(samples[:, 1])),
            "log_XI_d_median":   float(np.median(samples[:, 2])),
            "log_XI_d_std":       float(np.std(samples[:, 2])),
        },
        "n_samples": int(samples.shape[0]),
        "wall_seconds": float(wall),
        "nlive": int(nlive),
        "dlogz_target": float(DLOGZ),
        "test": "T4_3param",
    }
    out_path = RESULTS_DIR / f"t4_fit_{gal_name}_{profile_name}.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"[T4 {gal_name} {profile_name}] log Z = {log_Z:.3f} +/- {log_Z_err:.3f}"
          f"  XI_d_MAP = {10**log_XI_d_map:.2f}  chi2_red = {chi2_red:.2f}  "
          f"wall = {wall:.1f}s")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: fit_4t.py <gal_name> <profile>")
        sys.exit(1)
    fit_one_galaxy_3p(sys.argv[1], sys.argv[2])