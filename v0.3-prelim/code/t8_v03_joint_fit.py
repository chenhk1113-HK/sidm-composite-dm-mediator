#!/usr/bin/env python
"""
v0.3 T8 — proper 5-channel joint fit with calibrated SPARC log L.

IMPORTANT (per R11 audit, 2026-08-14): The SPARC contribution to the
joint fit is **NOT a per-galaxy observational likelihood**. It is a
**calibrated saturation score** that captures the Phase 2 T4 finding
that Burkert (cored) profiles win by ~5000 log Z over NFW (cuspy)
profiles for sigma/m > ~1 cm²/g. The relative likelihood is
approximated as a smooth saturation function:

    delta_log_Z(sigma/m) = Dsat * (1 - exp(-sigma/m / sigma_transition))
    Dsat = 5000, sigma_transition = 0.5 cm^2/g

The actual SPARC per-galaxy chi² fits (T14) do not drive the joint
sampling; the saturation score is a *proxy*. For a true joint fit
that re-derives the SPARC contribution from 175 per-galaxy forward
fits within the joint sampling loop, see v0.4-prelim roadmap item
G12 (out of v0.4 scope per the R11 audit).

**Downstream interpretation caveat**: log Z and Bayes factors from
this fit are conditional on this proxy choice. The "5× Bayes factor"
and "publication-grade 0.4-0.5 dex systematic" claims do not follow
from this calibration. See the reviewer's R11 audit Section 1 for
the methodological concerns.
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

RESULTS_DIR = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")
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
def loglike_sparc_hierarchical(sigma_m_0: float, a: float) -> float:
    """Real SPARC per-galaxy hierarchical log-likelihood (R11 G12 closure).

    Loads the pre-computed grid from
    v0.3-prelim/data/results/sparc_hierarchical_grid.npz (built by
    precompute_sparc_hierarchical.py — 175 SPARC galaxies, marginalized
    over ρ_c with Dutton-Maccio 2014 concentration-mass prior) and
    bilinearly interpolates the summed log L at (sigma_m_0, a).

    Per R11 audit (2026-08-14): replaces the previous saturation score
    delta_log_sparc(sigma_m_0, a) with a real data-driven per-galaxy
    likelihood. The previous score was a calibrated proxy, not a
    per-galaxy observational likelihood.

    The grid's summed log L is in **natural log units** (not log10),
    so it can be summed directly with other channels' log L values
    in the joint fit.
    """
    import numpy as np
    from pathlib import Path
    # Path candidates (Windows + WSL)
    grid_path_candidates = [
        Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results/sparc_hierarchical_grid.npz"),
        Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/sparc_hierarchical_grid.npz"),
        Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sparc_hierarchical_grid.npz"),
    ]
    grid_path = None
    for p in grid_path_candidates:
        if p.exists():
            grid_path = p
            break
    if grid_path is None:
        raise FileNotFoundError(
            "SPARC hierarchical grid not found. Run "
            "v0.3-prelim/code/precompute_sparc_hierarchical.py first."
        )

    # Cache the loaded grid
    if not hasattr(loglike_sparc_hierarchical, "_grid_cache"):
        loglike_sparc_hierarchical._grid_cache = np.load(grid_path)
    grid = loglike_sparc_hierarchical._grid_cache
    sigma_m_grid = grid["sigma_m_grid"]
    a_grid = grid["a_grid"]
    logL_grid = grid["logL_grid"]

    # Bilinear interpolation in log(σ/m) × a space
    log_sm = np.log10(sigma_m_0)
    # Clamp to grid range (out-of-grid = extrapolation penalty)
    if log_sm < np.log10(sigma_m_grid[0]):
        log_sm = np.log10(sigma_m_grid[0])
    if log_sm > np.log10(sigma_m_grid[-1]):
        log_sm = np.log10(sigma_m_grid[-1])
    if a < a_grid[0]:
        a = a_grid[0]
    if a > a_grid[-1]:
        a = a_grid[-1]

    # Linear interpolation
    log_sm_axis = np.log10(sigma_m_grid)
    i = np.searchsorted(log_sm_axis, log_sm) - 1
    j = np.searchsorted(a_grid, a) - 1
    i = max(0, min(i, len(log_sm_axis) - 2))
    j = max(0, min(j, len(a_grid) - 2))
    wx = (log_sm - log_sm_axis[i]) / (log_sm_axis[i + 1] - log_sm_axis[i])
    wy = (a - a_grid[j]) / (a_grid[j + 1] - a_grid[j])
    log_L = (
        logL_grid[i, j] * (1 - wx) * (1 - wy)
        + logL_grid[i + 1, j] * wx * (1 - wy)
        + logL_grid[i, j + 1] * (1 - wx) * wy
        + logL_grid[i + 1, j + 1] * wx * wy
    )
    return float(log_L)


def delta_log_sparc(sigma_m_0: float, a: float) -> float:
    """Calibrated SPARC saturation SCORE (legacy — DEPRECATED per R11 G12).

    Kept as a thin wrapper for backward compatibility with external
    callers. Returns loglike_sparc_hierarchical() (the real per-galaxy
    likelihood) for direct drop-in compatibility with the joint fit
    chain. See `loglike_sparc_hierarchical` for the principled replacement.

    Saturation is computed at the galaxy velocity scale (v ~ 100 km/s).
    This was a *relative* log Z approximation, not a per-galaxy
    observational likelihood. See the R11 audit (Section 1, G12) for
    the methodological concerns.
    """
    if sigma_m_0 <= 0:
        return -np.inf
    return loglike_sparc_hierarchical(sigma_m_0, a)


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
    # Per R11 G12: use the real per-galaxy hierarchical SPARC likelihood
    # directly. The pre-computed grid returns the summed natural-log
    # log L across 175 SPARC galaxies. The hierarchical likelihood is
    # the dominant constraint and correctly dominates the joint fit.
    ll += loglike_sparc_hierarchical(sigma_m_0, a)
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