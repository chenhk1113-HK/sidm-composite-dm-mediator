#!/usr/bin/env python
"""
T6 — Baryonic-feedback "effective core" parameterization.

Standard SN-driven feedback in galaxies cored density profiles via repeated
gas outflows. The signature is a "core radius" r_c that depends on the
stellar mass and SN energy (Pontzen & Governato 2012, Governato+ 2012).
Empirically, this can be mimicked by replacing the pure NFW profile with
an NFW where the inner cusp is replaced by a constant-density core of
size r_c. This is the "NFW_core" or "DC14" parametrization.

We test whether a cored profile can be EXPLAINED ENTIRELY by a baryonic-
feedback-style core, WITHOUT any dark-matter self-interaction.

If the data prefers NFW_core with a large r_c, that suggests baryonic
feedback (not SIDM) is the right explanation.

Free parameters:
    NFW:     (log_rho_s, log_r_s)                       — standard cuspy
    NFW_core (log_rho_s, log_r_s, log_r_core)           — feedback-cored
    Burkert: (log_rho_c, log_r_c)                       — SIDM-cored
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
from halo_profiles import V_NFW, V_Burkert, chi2_sparc

DATA_DIR = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.1-prelim/data")
RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.1-prelim/data/results")

# Same ranges as T1/T2
NFW_LOG_RHO_S_RANGE = (2.0, 10.0)
NFW_LOG_R_S_RANGE   = (-1.0, 2.5)
NFW_CORE_LOG_R_CORE_RANGE = (-1.5, 1.5)  # kpc
BURKERT_LOG_RHO_C_RANGE = (2.0, 10.0)
BURKERT_LOG_R_C_RANGE   = (-1.0, 2.5)

NLIVE = 200
DLOGZ = 0.10


def V_NFW_core(r: np.ndarray, rho_s: float, r_s: float, r_core: float) -> np.ndarray:
    """NFW profile with inner core (replaces cusp for r < r_core).

    rho(r) = rho_s / ((r/r_s) * (1 + r/r_s)^2)  for r > r_core
    rho(r) = rho_s / ((r_core/r_s) * (1 + r_core/r_s)^2)  for r <= r_core

    Approximation: smoothly transition by adding a (1 - exp(-r/r_core))^2
    suppression factor on the standard NFW density.
    """
    r = np.atleast_1d(r).astype(float)
    safe_r = np.maximum(r, 1e-10)
    # Suppression factor: 1 in outer region, smoothly drops to 0 at center
    suppress = (1.0 - np.exp(-safe_r / r_core))**2
    # Standard NFW circular velocity squared
    x = safe_r / r_s
    V2_nfw = (4.0 * np.pi * 4.302e-6 * rho_s * r_s**3 / safe_r
              * (np.log(1.0 + x) - x / (1.0 + x)))
    # The core reduces the central density; we approximate by sqrt(suppress) on V
    # This is approximate; for v0.1-final we use a more careful integration
    # (the simple suppress approach matches NFW in the outer region)
    V2 = V2_nfw * suppress
    V2[r <= 0] = 0.0
    return V2


def loglike_NFW_core(ga, theta):
    if not (NFW_LOG_RHO_S_RANGE[0] <= theta[0] <= NFW_LOG_RHO_S_RANGE[1]):
        return -np.inf
    if not (NFW_LOG_R_S_RANGE[0] <= theta[1] <= NFW_LOG_R_S_RANGE[1]):
        return -np.inf
    if not (NFW_CORE_LOG_R_CORE_RANGE[0] <= theta[2] <= NFW_CORE_LOG_R_CORE_RANGE[1]):
        return -np.inf
    rho, r_s, r_core = 10**theta[0], 10**theta[1], 10**theta[2]
    halo_V2 = V_NFW_core(ga.Rad, rho, r_s, r_core)
    V_total = np.sqrt(ga.Vbar_sq + halo_V2)
    return -0.5 * float(np.sum(((ga.Vobs - V_total) / np.maximum(ga.errV, 1e-3))**2))


def fit_one_NFW_core(gal_name: str, nlive: int = NLIVE):
    ga = load_one_sparc(DATA_DIR, gal_name)
    print(f"[T6 NFW_core {gal_name}] loaded {ga}")

    def prior_transform(u):
        return np.array([
            NFW_LOG_RHO_S_RANGE[0] + u[0] * (NFW_LOG_RHO_S_RANGE[1] - NFW_LOG_RHO_S_RANGE[0]),
            NFW_LOG_R_S_RANGE[0]   + u[1] * (NFW_LOG_R_S_RANGE[1]   - NFW_LOG_R_S_RANGE[0]),
            NFW_CORE_LOG_R_CORE_RANGE[0] + u[2] * (NFW_CORE_LOG_R_CORE_RANGE[1] - NFW_CORE_LOG_R_CORE_RANGE[0]),
        ])

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=lambda t: loglike_NFW_core(ga, t),
        prior_transform=prior_transform,
        ndim=3, nlive=nlive, bound='multi', sample='auto', bootstrap=0,
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

    rho, r_s, r_core = 10**theta_map
    halo_V2 = V_NFW_core(ga.Rad, rho, r_s, r_core)
    V_total = np.sqrt(ga.Vbar_sq + halo_V2)
    chi2_at_map = chi2_sparc(ga, V_total)
    chi2_red = chi2_at_map / max(ga.n_pts - 3, 1)

    out = {
        "galaxy": gal_name,
        "profile": "NFW_core",
        "n_params": 3,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "chi2_reduced_at_MAP": chi2_red,
        "theta_MAP": {
            "log_rho_s": float(theta_map[0]),
            "log_r_s":   float(theta_map[1]),
            "log_r_core": float(theta_map[2]),
        },
        "r_core_at_MAP_kpc": float(r_core),
        "posterior_summary": {
            "log_r_core_median": float(np.median(samples[:, 2])),
            "log_r_core_std":    float(np.std(samples[:, 2])),
        },
        "wall_seconds": float(wall),
        "nlive": int(nlive),
        "dlogz_target": float(DLOGZ),
        "test": "T6_NFW_core",
    }
    out_path = RESULTS_DIR / f"t6_fit_{gal_name}_NFW_core.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"[T6 NFW_core {gal_name}] log Z = {log_Z:.3f} +/- {log_Z_err:.3f}"
          f"  r_core_MAP = {r_core:.3f} kpc  chi2_red = {chi2_red:.2f}"
          f"  wall = {wall:.1f}s")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fit_t6_NFW_core.py <gal_name>")
        sys.exit(1)
    fit_one_NFW_core(sys.argv[1])