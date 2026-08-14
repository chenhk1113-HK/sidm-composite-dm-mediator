#!/usr/bin/env python
"""
T1/T2 single-galaxy dynesty fit for one SPARC galaxy + one halo profile.

Usage:
    python fit_single_galaxy.py <gal_name> <profile>
    where profile in {NFW, Burkert}

Output: data/fit_<gal>_<profile>.json with log Z, posterior samples,
chi^2 at MAP, etc.

Following WIMpy conventions:
    - dynesty nested sampling (nlive=200, dlogz=0.10 = v4b baseline)
    - uniform priors on log-space halo params
    - JSON output with log Z ± uncertainty
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
    V_NFW, V_Burkert, log_prior_NFW, log_prior_Burkert,
    loglike_profile, chi2_sparc,
)

DATA_DIR = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.1-prelim/data")
RESULTS_DIR = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# dynesty config (matches WIMpy v4b baseline)
NLIVE = 200
DLOGZ = 0.10

PROFILES = {
    "NFW":     (V_NFW,     log_prior_NFW),
    "Burkert": (V_Burkert, log_prior_Burkert),
}


def fit_one_galaxy(gal_name: str, profile_name: str, nlive: int = NLIVE) -> dict:
    if profile_name not in PROFILES:
        raise ValueError(f"Unknown profile {profile_name}; choose from {list(PROFILES)}")
    halo_fn, log_prior_fn = PROFILES[profile_name]
    ga = load_one_sparc(DATA_DIR, gal_name)
    print(f"[fit {gal_name} {profile_name}] loaded {ga}")

    def loglike(theta):
        return loglike_profile(ga, theta, halo_fn, log_prior_fn)

    def prior_transform(u):
        # Map unit cube to log-uniform prior
        from halo_profiles import (
            NFW_LOG_RHO_S_RANGE, NFW_LOG_R_S_RANGE,
            BURKERT_LOG_RHO_C_RANGE, BURKERT_LOG_R_C_RANGE,
        )
        if profile_name == "NFW":
            lo = NFW_LOG_RHO_S_RANGE
            ls = NFW_LOG_R_S_RANGE
        else:
            lo = BURKERT_LOG_RHO_C_RANGE
            ls = BURKERT_LOG_R_C_RANGE
        return np.array([lo[0] + u[0] * (lo[1] - lo[0]),
                        ls[0] + u[1] * (ls[1] - ls[0])])

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike,
        prior_transform=prior_transform,
        ndim=2,
        nlive=nlive,
        bound='multi',  # standard for nested sampling
        sample='auto',
        bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples  # shape (n_samples, 2)
    weights = np.exp(res.logwt - res.logz[-1])
    # MAP estimate (highest-weight sample)
    imap = int(np.argmax(weights))
    theta_map = samples[imap]

    # Chi^2 at MAP
    rho_map, r_map = 10**theta_map[0], 10**theta_map[1]
    V_total = np.sqrt(ga.Vbar_sq + halo_fn(ga.Rad, rho_map, r_map))
    chi2_at_map = chi2_sparc(ga, V_total)
    chi2_red = chi2_at_map / max(ga.n_pts - 2, 1)

    out = {
        "galaxy": gal_name,
        "profile": profile_name,
        "n_pts": int(ga.n_pts),
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "chi2_at_MAP": chi2_at_map,
        "chi2_reduced_at_MAP": chi2_red,
        "theta_MAP": {"log_param1": float(theta_map[0]), "log_param2": float(theta_map[1])},
        "posterior_summary": {
            "log_param1_median": float(np.median(samples[:, 0])),
            "log_param2_median": float(np.median(samples[:, 1])),
            "log_param1_std":    float(np.std(samples[:, 0])),
            "log_param2_std":    float(np.std(samples[:, 1])),
        },
        "n_samples": int(samples.shape[0]),
        "wall_seconds": float(wall),
        "nlive": int(nlive),
        "dlogz_target": float(DLOGZ),
    }
    out_path = RESULTS_DIR / f"fit_{gal_name}_{profile_name}.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"[fit {gal_name} {profile_name}] log Z = {log_Z:.3f} +/- {log_Z_err:.3f}"
          f"  chi2_red = {chi2_red:.2f}  wall = {wall:.1f}s  -> {out_path.name}")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: fit_single_galaxy.py <gal_name> <profile>")
        print("Example: fit_single_galaxy.py CamB NFW")
        sys.exit(1)
    fit_one_galaxy(sys.argv[1], sys.argv[2])