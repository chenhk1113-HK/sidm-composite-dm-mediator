#!/usr/bin/env python
"""
T7b — Joint 4-channel fit, velocity-INDEPENDENT cross-section.

Same as T7 but with a = 0 (constant σ/m across all velocity scales).
This is the simpler "1 free parameter" version of the SIDM problem
and corresponds to the standard literature comparison.
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
import numpy as np
import dynesty

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sidm_velocity_dependent import (
    loglike_dsph_published,
    loglike_ufd_published,
    loglike_bullet_cluster_published,
    V_REF, V_UFD, V_CLUSTER,
)

RESULTS_DIR = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.2-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LOG_SIGMA_M_RANGE = (-3.0, 2.5)
NLIVE = 500
DLOGZ = 0.10


def loglike_vindep(log_sm):
    """Joint log L for velocity-independent σ/m, at fixed a=0."""
    if log_sm < LOG_SIGMA_M_RANGE[0] or log_sm > LOG_SIGMA_M_RANGE[1]:
        return -np.inf
    sigma_m_0 = 10**log_sm
    ll = 0.0
    ll += loglike_dsph_published(sigma_m_0, 0.0)
    ll += loglike_ufd_published(sigma_m_0, 0.0)
    ll += loglike_bullet_cluster_published(sigma_m_0, 0.0)
    return ll


def main():
    def loglike(theta):
        return loglike_vindep(theta[0])

    def prior_transform(u):
        return np.array([LOG_SIGMA_M_RANGE[0] + u[0] * (LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0])])

    print(f"[T7b] Running velocity-independent joint 4-channel fit...")
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=1, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0
    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples[:, 0]  # 1D
    weights = np.exp(res.logwt - res.logz[-1])

    imap = int(np.argmax(weights))
    log_sm_MAP = float(samples[imap])
    p16, p50, p84 = np.percentile(samples, [16, 50, 84])
    print(f"  log Z = {log_Z:.3f} +/- {log_Z_err:.3f}  wall = {wall:.1f}s")
    print(f"  MAP: log10(sigma/m) = {log_sm_MAP:.2f}, sigma/m = {10**log_sm_MAP:.3f} cm^2/g")
    print(f"  Median: log10(sigma/m) = {p50:.2f}, sigma/m = {10**p50:.3f} cm^2/g")
    print(f"  68% CI: log10(sigma/m) in [{p16:.2f}, {p84:.2f}]")
    print(f"  Marginal posterior shape:")
    hist, edges = np.histogram(samples, bins=20, weights=weights)
    centers = 0.5 * (edges[:-1] + edges[1:])
    for c, h in zip(centers, hist):
        bar = "#" * int(40 * h / hist.max())
        print(f"    log sigma/m = {c:+5.2f}  p = {h:.3f}  {bar}")

    # Also report at three specific sigma/m values
    print(f"\n  Joint log L at key sigma/m values:")
    for log_sm in [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0]:
        ll = loglike_vindep(log_sm)
        print(f"    log sigma/m = {log_sm:+.2f} (sigma/m={10**log_sm:.2f}): log L = {ll:+.3f}")

    out = {
        "test": "T7b_vindep_4channel",
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": {"log_sigma_m": log_sm_MAP, "sigma_m_cm2_per_g": 10**log_sm_MAP},
        "median_posterior": {
            "log_sigma_m_p16": float(p16),
            "log_sigma_m_p50": float(p50),
            "log_sigma_m_p84": float(p84),
        },
        "wall_seconds": float(wall),
        "n_samples": int(len(samples)),
        "channels": ["Horigome+2025 dSph", "Sanchez-Almeida+2025 UFD", "Cha+2025 Bullet Cluster"],
    }
    out_path = RESULTS_DIR / "t7b_vindep_posterior.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\n  output -> {out_path}")


if __name__ == "__main__":
    main()