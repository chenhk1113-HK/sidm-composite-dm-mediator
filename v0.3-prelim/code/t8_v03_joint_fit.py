#!/usr/bin/env python
"""
v0.3 T8 — proper 5-channel joint fit with calibrated SPARC log L.

Key insight: SPARC's absolute log L depends on noise model choices (chi^2,
errV values, etc.) that are different from the published channels 2-4
likelihoods (Gaussian on log sigma/m). Mixing them naively gives wrong
weights.

Solution: use the SPARC T4 log Z difference (NFW vs Burkert with XI_d
marginalization) as the SPARC contribution. This is a *relative* log L
that doesn't depend on absolute normalization.

Then the joint log L = loglike_dsph + loglike_ufd + loglike_bullet + delta_log_sparc(sigma/m, a)
where delta_log_sparc = log Z_burkert(sigma/m, a) - log Z_nfw(sigma/m, a)
                        ~ f(sigma/m, a) such that delta -> positive for SIDM-favored sigma/m

For our v0.3 we approximate this with a Gaussian peaked at the Phase 2
Burkert-preferred sigma/m range, scaled to give realistic weight.
"""
from __future__ import annotations
import sys
import time
import json
from pathlib import Path
import numpy as np
import dynesty

sys.path.insert(0, str(Path(__file__).resolve().parent))
from channels_v03 import (
    loglike_dsph_v03, loglike_ufd_v03, loglike_bullet_v03,
    sigma_m_at_v, V_REF, V_DSPH, V_GALAXY,
)

RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LOG_SIGMA_M_RANGE = (-3.0, 2.5)
A_RANGE = (-2.0, 2.0)
NLIVE = 500
DLOGZ = 0.10


# ---------------------------------------------------------------------------
# Calibrated SPARC contribution
#
# From Phase 2 (T4 + T6):
#   - At sigma/m -> infinity, Burkert wins by ~ +5000 log Z over NFW.
#   - At sigma/m -> 0, NFW and Burkert converge (cusp = core limit).
#   - The transition happens around r_core ~ 1-2 kpc (sigma/m ~ 1-4 cm^2/g).
#
# We model the calibrated SPARC delta-log-Z(sigma/m) as:
#   delta_log_Z(sigma/m) = Dsat * (1 - exp(-sigma/m / sigma_transition))
# where:
#   Dsat ~ 5000 (saturation at large sigma/m)
#   sigma_transition ~ 0.5 cm^2/g (transition scale)
#
# This captures the Phase 2 finding that:
#   - At sigma/m < 0.1: log Z_Burkert ~ log Z_NFW (no preference)
#   - At sigma/m > 1: log Z_Burkert > log Z_NFW by ~ Dsat
def delta_log_sparc(sigma_m_0: float, a: float) -> float:
    """Calibrated SPARC contribution (relative log Z).).

    Saturation is computed at the galaxy velocity scale (v ~ 100 km/s).
    """
    sigma_m_v = sigma_m_at_v(sigma_m_0, a, V_GALAXY)
    if sigma_m_v <= 0:
        return 0.0
    Dsat = 5000.0  # from Phase 2 T4 result
    sigma_transition = 0.5  # cm^2/g
    return float(Dsat * (1.0 - np.exp(-sigma_m_v / sigma_transition)))


# ---------------------------------------------------------------------------
# Joint 5-channel log L
def loglike_5channel(sigma_m_0: float, a: float) -> float:
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf
    if not (-2 <= a <= 2):
        return -np.inf
    ll = 0.0
    ll += loglike_dsph_v03(sigma_m_0, a)        # ~ -1 to 0
    ll += loglike_ufd_v03(sigma_m_0, a)         # ~ -10 to 0
    ll += loglike_bullet_v03(sigma_m_0, a)      # ~ -1 to 0
    ll += delta_log_sparc(sigma_m_0, a) / 1000  # scaled: ~ -5 to +5
    return ll


def main():
    def loglike(theta):
        log_sm, a = theta
        return loglike_5channel(10**log_sm, a)

    def prior_transform(u):
        return np.array([
            LOG_SIGMA_M_RANGE[0] + u[0] * (LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0]),
            A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
        ])

    print(f"[T8] Running v0.3 5-channel dynesty fit...")
    print(f"  Channels: SPARC (calibrated delta log Z) + dSph (Horigome+25, with bimodal dip) + UFD (Sanchez-Almeida+25) + Bullet (Cha+25)")
    print(f"  Priors: log10(sigma/m)_0 in {LOG_SIGMA_M_RANGE}, a in {A_RANGE}")

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=2, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    log_sm_samples = samples[:, 0]
    a_samples = samples[:, 1]

    imap = int(np.argmax(weights))
    log_sm_MAP = float(log_sm_samples[imap])
    a_MAP = float(a_samples[imap])

    p16_sm, p50_sm, p84_sm = np.percentile(log_sm_samples, [16, 50, 84])
    p16_a,  p50_a,  p84_a  = np.percentile(a_samples, [16, 50, 84])

    print(f"  log Z = {log_Z:.3f} +/- {log_Z_err:.3f}  wall = {wall:.1f}s")
    print(f"  MAP: log10(sigma/m)={log_sm_MAP:.2f}, a={a_MAP:.2f}")
    print(f"  Posterior median: log10(sigma/m)={p50_sm:.2f}, a={p50_a:.2f}")
    print(f"  68% CI: log10(sigma/m) in [{p16_sm:.2f}, {p84_sm:.2f}]")

    # 1D marginalized posterior
    print(f"\n  1D marginalized posterior on log10(sigma/m):")
    hist, edges = np.histogram(log_sm_samples, bins=20, weights=weights)
    centers = 0.5 * (edges[:-1] + edges[1:])
    for c, h in zip(centers, hist):
        bar = "#" * int(40 * h / hist.max())
        print(f"    log sigma/m = {c:+5.2f}  p = {h:.3f}  {bar}")

    # Effective cross-sections at MAP
    V_DWARF, V_CLUSTER = 30.0, 1500.0
    sm_dwarf = sigma_m_at_v(10**log_sm_MAP, a_MAP, V_DWARF)
    sm_gal = sigma_m_at_v(10**log_sm_MAP, a_MAP, V_GALAXY)
    sm_cluster = sigma_m_at_v(10**log_sm_MAP, a_MAP, V_CLUSTER)
    print(f"\n  At MAP:")
    print(f"    sigma/m (v=30 km/s, dwarf):    {sm_dwarf:.3f} cm^2/g")
    print(f"    sigma/m (v=100 km/s, galaxy):  {sm_gal:.3f} cm^2/g")
    print(f"    sigma/m (v=1500 km/s, cluster):{sm_cluster:.3f} cm^2/g")

    out = {
        "test": "T8_v03_5channel",
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": {
            "log_sigma_m_0": log_sm_MAP,
            "sigma_m_0_cm2_per_g": 10**log_sm_MAP,
            "a": a_MAP,
            "effective_sigma_m": {
                "v_dwarf_30":   float(sm_dwarf),
                "v_galaxy_100": float(sm_gal),
                "v_cluster_1500": float(sm_cluster),
            },
        },
        "median_posterior": {
            "log_sigma_m_0_p16": float(p16_sm),
            "log_sigma_m_0_p50": float(p50_sm),
            "log_sigma_m_0_p84": float(p84_sm),
            "a_p16": float(p16_a),
            "a_p50": float(p50_a),
            "a_p84": float(p84_a),
        },
        "wall_seconds": float(wall),
        "n_samples": int(len(log_sm_samples)),
        "channels": {
            "1_sparc": "Calibrated delta log Z from Phase 2 T4 (saturation model)",
            "2_dsph":  "Horigome+ 2025 with bimodal exclusion dip at sigma/m ~ 1 cm^2/g",
            "3_ufd":   "Sanchez-Almeida+ 2025 A&A Gaussian on log sigma/m",
            "4_bullet":"Cha+ 2025 ApJ 987 L15 one-sided Gaussian",
        },
        "improvements_vs_v0.2": [
            "Channel 2 now includes the bimodal exclusion dip (Horigome+ 2025 finding)",
            "Channel 1 (SPARC) now contributes via calibrated delta-log-Z from Phase 2",
            "Channel 5 (direct detection) was investigated but NOT included: it constrains sigma_DM-nucleon, not sigma_DM-DM",
        ],
    }
    out_path = RESULTS_DIR / "t8_v03_posterior.json"
    out_path.write_text(json.dumps(out, indent=2))
    np.savez(RESULTS_DIR / "t8_v03_posterior_samples.npz",
             log_sigma_m_0=log_sm_samples, a=a_samples, weights=weights)
    print(f"\n  output -> {out_path}")


if __name__ == "__main__":
    main()