#!/usr/bin/env python
"""
T12 — Joint fit with all 6 channels (including arXiv:2510.11006 lens subhalo).

Re-runs T8-style joint fit but with Channel 6 (gravitational-lensing substructure,
PRL 2026) added. Compares the 5-channel vs 6-channel posteriors.

The key question: does adding the PRL 2026 lens substructure constraint shift
the σ/m posterior? At subhalo velocities (V_max ~ 10 km/s), the constraint
peaks at σ/m_eff ~ 50 cm²/g. For our pipeline's σ/m_0 (at V_REF=100 km/s),
this maps to log10(σ/m_0) + a = 1.7 (peak).
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
import numpy as np
import dynesty

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from config import LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ

sys.path.insert(0, str(Path(__file__).resolve().parent))
from channels_v03 import (
    loglike_dsph_v03, loglike_ufd_v03, loglike_bullet_v03,
)
from sidm_velocity_dependent import sigma_m_effective
from channels_extended import loglike_lens_subhalo


RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")


def loglike_5channel(sigma_m_0, a):
    return (loglike_dsph_v03(sigma_m_0, a) +
            loglike_ufd_v03(sigma_m_0, a) +
            loglike_bullet_v03(sigma_m_0, a))


def loglike_6channel(sigma_m_0, a):
    return (loglike_dsph_v03(sigma_m_0, a) +
            loglike_ufd_v03(sigma_m_0, a) +
            loglike_bullet_v03(sigma_m_0, a) +
            loglike_lens_subhalo(sigma_m_0, a))


def run_fit(label, loglike_fn):
    print(f"[T12 {label}] ...")

    def loglike(theta):
        return loglike_fn(10**theta[0], theta[1])

    def prior_transform(u):
        return np.array([
            LOG_SIGMA_M_RANGE[0] + u[0] * (LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0]),
            A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
        ])

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=2, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    log_sm = samples[:, 0]
    a = samples[:, 1]

    p16_sm, p50_sm, p84_sm = np.percentile(log_sm, [16, 50, 84])
    p16_a, p50_a, p84_a = np.percentile(a, [16, 50, 84])

    print(f"  log Z={log_Z:.3f}  median σ/m_0={10**p50_sm:.2f}  "
          f"68% CI=[{10**p16_sm:.2f}, {10**p84_sm:.2f}]  a={p50_a:.2f}  wall={wall:.1f}s")

    return {
        "label": label,
        "log_Z": log_Z,
        "median_log_sigma_m_0": p50_sm,
        "median_sigma_m_0": 10**p50_sm,
        "p16_sigma_m_0": 10**p16_sm,
        "p84_sigma_m_0": 10**p84_sm,
        "median_a": p50_a,
        "p16_a": p16_a,
        "p84_a": p84_a,
        "wall_seconds": wall,
    }


def main():
    print("=== T12: 5-channel vs 6-channel comparison ===\n")
    res_5ch = run_fit("5-channel (no lens)", loglike_5channel)
    res_6ch = run_fit("6-channel (with lens subhalo)", loglike_6channel)

    print(f"\n=== Comparison ===")
    print(f"{'':25} {'5-channel':<15} {'6-channel':<15} {'Δ':<10}")
    for key in ["log_Z", "median_sigma_m_0", "median_a"]:
        v5 = res_5ch[key]
        v6 = res_6ch[key]
        if isinstance(v5, float):
            print(f"{key:<25} {v5:<15.3f} {v6:<15.3f} {v6-v5:<10.3f}")

    out = {
        "test": "T12_6channel_with_lens_subhalo",
        "res_5channel": res_5ch,
        "res_6channel": res_6ch,
        "channel_6_citation": "arXiv:2510.11006 (Yang, Yang, Yu et al. 2026, PRL)",
        "channel_6_constraint": "log10(σ/m_eff at v=10 km/s) ~ 1.7 ± 0.3 dex",
        "interpretation": "Adding Channel 6 (lens substructure) tests whether the gravothermal "
                          "collapse regime is consistent with the new PRL 2026 observations.",
    }
    out_path = RESULTS_DIR / "t12_6channel_with_lens.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\noutput -> {out_path}")


if __name__ == "__main__":
    main()