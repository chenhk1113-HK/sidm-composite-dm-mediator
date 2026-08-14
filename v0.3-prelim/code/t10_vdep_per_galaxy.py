#!/usr/bin/env python
"""
T10 — Per-galaxy velocity-dependent SIDM fit for SPARC.

Per peer review (2026-08-10, Long-Term #2):
    "Replace the v0.3 SPARC saturation heuristic with full velocity-dependent
     Burkert re-fits for all 175 SPARC galaxies to eliminate approximation
     bias in joint channel weighting."

Model: V^2(r) = V_Burkert(r; log_rho_c, r_core) where
       r_core = sqrt(sigma/m(v_max))
       sigma/m(v) = sigma/m_0 * (v / v_ref)^(-a)

Parameters (3):
    log_rho_c:  log10(core density in M_sun/kpc^3)
    log_sigma_m_0: log10(cross-section at v_ref in cm^2/g)
    a:          velocity power-law index

For each galaxy:
    - Marginalize over log_rho_c (uniform prior in [2, 10])
    - Get posterior on (log_sigma_m_0, a) via dynesty
    - Save to JSON: {galaxy, log_Z, MAP, posterior samples summary}

v_max is estimated from peak of observed Vobs for each galaxy.
"""
from __future__ import annotations
import sys
import json
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Import shared dependencies
from halo_profiles import V_Burkert, chi2_sparc
from sparc_loader import load_all_sparc
from batch_utils import BatchLogger, CheckpointState, get_batch_paths
from config import V_REF, V_GALAXY, LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ, VDEP_LOG_RHO_RANGE

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sidm_velocity_dependent import sigma_m_effective as sigma_m_at_v


RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def fit_one_vdep(ga, nlive=NLIVE, dlogz=DLOGZ):
    """Per-galaxy v-dep Burkert fit.

    Returns dict with log_Z, MAP, posterior samples summary, wall time.
    """
    t0 = time.time()
    v_max = float(np.max(ga.Vobs))
    if v_max <= 0:
        return {"galaxy": ga.name, "log_Z": float("-inf"), "error": "v_max <= 0"}

    # Define the model
    def loglike(theta):
        log_rho_c, log_sm, a = theta
        sigma_m_v = sigma_m_at_v(10**log_sm, a, v_max)
        if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
            return -np.inf
        r_core = np.sqrt(sigma_m_v)
        halo_V2 = V_Burkert(ga.Rad, 10**log_rho_c, r_core)
        V_total = np.sqrt(ga.Vbar_sq + halo_V2)
        return -0.5 * chi2_sparc(ga, V_total)

    def prior_transform(u):
        return np.array([
            VDEP_LOG_RHO_RANGE[0] + u[0] * (VDEP_LOG_RHO_RANGE[1] - VDEP_LOG_RHO_RANGE[0]),
            LOG_SIGMA_M_RANGE[0] + u[1] * (LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0]),
            A_RANGE[0] + u[2] * (A_RANGE[1] - A_RANGE[0]),
        ])

    import dynesty
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=3, nlive=nlive, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=dlogz, print_progress=False)
    res = sampler.results

    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    log_rho_c = samples[:, 0]
    log_sm = samples[:, 1]
    a = samples[:, 2]

    imap = int(np.argmax(weights))
    log_Z = float(res.logz[-1])

    return {
        "galaxy": ga.name,
        "n_pts": ga.n_pts,
        "v_max_kms": v_max,
        "log_Z": log_Z,
        "log_Z_err": float(res.logzerr[-1]),
        "MAP_log_rho_c": float(log_rho_c[imap]),
        "MAP_log_sigma_m": float(log_sm[imap]),
        "MAP_sigma_m_cm2_per_g": float(10**log_sm[imap]),
        "MAP_a": float(a[imap]),
        "median_log_sigma_m": float(np.percentile(log_sm, 50)),
        "median_sigma_m_cm2_per_g": float(10**np.percentile(log_sm, 50)),
        "p16_sigma_m_cm2_per_g": float(10**np.percentile(log_sm, 16)),
        "p84_sigma_m_cm2_per_g": float(10**np.percentile(log_sm, 84)),
        "median_a": float(np.percentile(a, 50)),
        "n_posterior_samples": int(len(samples)),
        "wall_seconds": float(time.time() - t0),
    }


def main(batch_name: str = "t10_vdep"):
    """Run per-galaxy v-dep fits on all SPARC galaxies with checkpoint/resume."""
    paths = get_batch_paths("v03", batch_name)
    cp = CheckpointState(paths["checkpoint"])
    logger = BatchLogger(paths["log"], batch_name=batch_name)

    data_dir = Path("/home/lamkuenai/dm-sidm-pipeline/v0.1-prelim/data/Rotmod_LTG")
    galaxies = load_all_sparc(data_dir)
    logger.info("batch_start", n_galaxies=len(galaxies), version="v0.3-prelim")

    n_done_before = cp.n_done
    for ga in galaxies:
        if cp.is_done(ga.name):
            logger.debug("skip_done", galaxy=ga.name)
            continue
        if ga.n_pts < 20:
            # Skip low-quality galaxies (consistent with T4 filtering)
            cp.mark_failed(ga.name, error="n_pts < 20")
            logger.warn("skip_low_n", galaxy=ga.name, n_pts=ga.n_pts)
            continue

        cp.mark_pending(ga.name)
        try:
            result = fit_one_vdep(ga)
            cp.mark_done(ga.name, result_summary={
                "log_Z": result["log_Z"],
                "MAP_sigma_m": result["MAP_sigma_m_cm2_per_g"],
                "MAP_a": result["MAP_a"],
                "wall_s": result["wall_seconds"],
            })
            logger.info("fit_complete", **result)
        except Exception as e:
            cp.mark_failed(ga.name, error=str(e))
            logger.error("fit_failed", galaxy=ga.name, error=str(e))

    logger.info("batch_done",
                n_done=cp.n_done, n_failed=cp.n_failed, n_pending=cp.n_pending)
    print(cp.summary())


if __name__ == "__main__":
    main()