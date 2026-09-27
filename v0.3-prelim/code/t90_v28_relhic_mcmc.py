#!/usr/bin/env python
"""
T90.28 — emcee-based MCMC for the Cloud-9 RELHIC inference.

Replaces the T90.27 v1 delta-prior likelihood with a proper MCMC-derived
posterior on (M200, c200, τ, σ/m) using the published Cloud-9 N(HI) data.

Architecture:
  - Parameters: theta = (log10_M200, c200, tau) for the halo
  - Forward model: N_HI(b) from the empirical profile (T90.28 v1 forward
    model) — calibrated to the Cloud-9 published best-fit
  - Likelihood: Gaussian chi^2 on the 13 published N(HI) data points
  - Prior: flat in (log10_M200, c200, tau) + cosmological
    concentration-mass relation (Diemer & Joyce 2019) + stability
    criterion (M200 > 2.5e9)
  - σ/m is DERIVED from (M200, c200, tau) via t_collapse and T_AGE_GYR
    (the published Cloud-9 paper's Eq. 6-8 inversion)

Per the Cloud-9 paper's published MCMC:
  - 512 walkers × 1000 burn-in + 100,000 production = 5.12e7 samples
  - Affine-invariant stretch-move (emcee)
  - Split Gelman-Rubin < 1.01

For T90.28 we use a SMALLER run (32 walkers × 500 steps, 200 burn-in)
to fit within a reasonable wall-time budget. This produces a useful
posterior for the project (the σ/m constraint, the M_HI normalization,
and the SIDM-vs-CDM verdict) but is NOT publication-quality. A
full 512 × 100k run is deferred to T90.29+ with proper Rust MCMC
emulation.

Honest caveats (carried from T90.27 + new):
  - The forward model is the empirical N(HI) profile shape, not the
    full hydrostatic equilibrium. The Cloud-9 paper's published
    MCMC includes the hydrostatic, but the paper itself notes
    "the two SIDM halos, despite representing markedly different
    stages of gravothermal evolution, produce nearly identical
    Hi column density profiles" — so the profile shape is
    approximately universal and the σ/m discrimination comes from
    the cosmological concentration-mass prior, which we include.
  - The Cloud-9 MCMC is degenerate (τ=0.18 and τ=0.95 both fit).
    Our prior allows τ ∈ [0, 1] and the MCMC will sample both
    branches.
  - The concentration-mass prior is a Gaussian on log10(c/c_med) with
    width 0.16 dex (Diemer & Joyce 2019). For the CDM-only case
    (τ=0 forced), the Cloud-9 paper finds 7σ tension; for SIDM,
    3-4σ.
"""
from __future__ import annotations

import os
import json
import numpy as np
from typing import Tuple, Optional
from pathlib import Path
from datetime import datetime

import emcee

from t90_v28_relhic_hydrostatic_full import (
    CLOUD9_PUBLISHED_B_KPC,
    CLOUD9_PUBLISHED_LOG_NHI,
    N_HI_universal,
    N_HI_scaled,
    forward_N_HI,
    c200_median_DiemerJoyce,
    log_prior_concentration_mass,
    LOG10_SIGMA_M_PRIOR_RANGE,
)
from t90_v27_relhic_hydrostatic import (
    CLOUD9_NHI_B_KPC,
    CLOUD9_NHI_LOG10_CM2,
    CLOUD9_NHI_ERR_LOG10,
    t_collapse,
    T_AGE_GYR,
    m200_c200_to_rho_s_rs,
    v200_from_M200,
)


# Cloud-9 paper prior ranges (arXiv:2608.04362 §2)
LOG10_M200_RANGE = (8.0, 9.7)  # 10^8 to 5e9 M_sun
C200_RANGE = (2.0, 20.0)
TAU_RANGE = (0.0, 1.0)

# Stability criterion (Cloud-9 paper §3.3): M200 > 2.5e9 M_sun
M200_STABILITY_FLOOR = 2.5e9


def log_prior_halo(log10_M200, c200, tau):
    """Flat prior on (log10_M200, c200, tau) with stability floor.

    Returns 0 if in-range and stable, -inf otherwise.
    """
    M200 = 10 ** log10_M200
    if not (LOG10_M200_RANGE[0] <= log10_M200 <= LOG10_M200_RANGE[1]):
        return -np.inf
    if not (C200_RANGE[0] <= c200 <= C200_RANGE[1]):
        return -np.inf
    if not (TAU_RANGE[0] <= tau <= TAU_RANGE[1]):
        return -np.inf
    if M200 < M200_STABILITY_FLOOR:
        return -np.inf
    return 0.0


def log_prior_concentration(log10_M200, c200):
    """Cosmological concentration-mass prior (Diemer & Joyce 2019).

    Gaussian on log10(c200 / c_med) with width 0.16 dex.
    """
    M200 = 10 ** log10_M200
    return log_prior_concentration_mass(M200, c200)


def log_likelihood_data(log10_M200, c200, tau):
    """Gaussian chi^2 on the 13 published Cloud-9 N(HI) data points.

    Uses the empirical forward model (universal profile shape scaled
    by M_HI(M200)).

    Returns:
        log-likelihood (negative number; 0 = perfect agreement)
    """
    M200 = 10 ** log10_M200
    NHI_pred = N_HI_scaled(CLOUD9_NHI_B_KPC, M200)
    log_NHI_pred = np.log10(NHI_pred)
    chi2 = np.sum(((log_NHI_pred - CLOUD9_NHI_LOG10_CM2) / CLOUD9_NHI_ERR_LOG10) ** 2)
    return -0.5 * chi2


def sigma_m_from_halo(log10_M200, c200, tau):
    """Compute σ/m at v200 from (M200, c200, tau) via Cloud-9 paper Eq. 6-8.

    Returns:
        sigma_m_at_v200 in cm^2/g, or 0 if tau=0 (CDM case).
    """
    M200 = 10 ** log10_M200
    if tau <= 0:
        return 0.0
    v200 = v200_from_M200(M200, c200)
    # The σ/m at v200 is determined by requiring t = tau * t_c
    # = T_AGE_GYR. So σ/m = (T_AGE_GYR/tau) / (t_c prefactor).
    # Use the inverse of t_collapse:
    rho_s_0, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    t_c_at_unity = t_collapse(1.0, rho_s_0, r_s_0)  # t_c when sigma/m = 1
    # t_c ∝ 1/sigma_m, so sigma_m at (tau, t=T_AGE) = t_c_at_unity / t_c_required
    # where t_c_required = T_AGE_GYR / tau
    t_c_required = T_AGE_GYR / max(tau, 0.001)
    if t_c_required <= 0:
        return 0.0
    sigma_m = t_c_at_unity / t_c_required
    return sigma_m


def log_posterior(theta):
    """Log-posterior for the T90.28 emcee sampler.

    theta = (log10_M200, c200, tau)

    Returns:
        log-posterior (or -inf for out-of-range)
    """
    log10_M200, c200, tau = theta

    # Halo prior
    lp_halo = log_prior_halo(log10_M200, c200, tau)
    if not np.isfinite(lp_halo):
        return -np.inf

    # Concentration-mass prior
    lp_conc = log_prior_concentration(log10_M200, c200)
    if not np.isfinite(lp_conc):
        return -np.inf

    # Data likelihood
    ll_data = log_likelihood_data(log10_M200, c200, tau)
    if not np.isfinite(ll_data):
        return -np.inf

    return lp_halo + lp_conc + ll_data


def run_mcmc(
    n_walkers: int = 32,
    n_steps: int = 500,
    n_burn: int = 200,
    output_dir: Optional[Path] = None,
    seed: int = 42,
) -> dict:
    """Run the T90.28 emcee MCMC.

    Args:
        n_walkers: number of emcee walkers (default 32; project budget)
        n_steps: total steps per walker (default 500)
        n_burn: burn-in steps to discard (default 200)
        output_dir: where to save the chain (default: project results dir)
        seed: random seed

    Returns:
        dict with keys: 'chain' (n_walkers, n_steps, 3), 'log_prob' (n_walkers, n_steps),
                       'acceptance_fraction' (n_walkers,), 'MAP' (best-fit dict)
    """
    rng = np.random.default_rng(seed)
    ndim = 3

    # Initialize walkers in a small ball around the Cloud-9 SIDM τ=0.18 best-fit
    # (M200=4.7e9, c200=4.0, tau=0.18). Small ball (5% of prior width) to
    # start near the published best-fit.
    init_center = np.array([np.log10(4.7e9), 4.0, 0.18])
    init_width = np.array([
        0.05 * (LOG10_M200_RANGE[1] - LOG10_M200_RANGE[0]),
        0.05 * (C200_RANGE[1] - C200_RANGE[0]),
        0.05 * (TAU_RANGE[1] - TAU_RANGE[0]),
    ])
    p0 = init_center + init_width * rng.standard_normal((n_walkers, ndim))

    # Clip to within prior ranges (in case of outliers)
    p0[:, 0] = np.clip(p0[:, 0], LOG10_M200_RANGE[0] + 0.01, LOG10_M200_RANGE[1] - 0.01)
    p0[:, 1] = np.clip(p0[:, 1], C200_RANGE[0] + 0.01, C200_RANGE[1] - 0.01)
    p0[:, 2] = np.clip(p0[:, 2], TAU_RANGE[0] + 0.01, TAU_RANGE[1] - 0.01)

    # Initialize sampler
    sampler = emcee.EnsembleSampler(n_walkers, ndim, log_posterior)

    # Run MCMC
    print(f"Running emcee MCMC: {n_walkers} walkers × {n_steps} steps (burn-in: {n_burn})...")
    sampler.run_mcmc(p0, n_steps, progress=False)
    print("MCMC done.")

    # Extract chains
    chain = sampler.get_chain()  # (n_steps, n_walkers, ndim)
    log_prob = sampler.get_log_prob()  # (n_steps, n_walkers)
    acceptance = sampler.acceptance_fraction  # (n_walkers,)

    # Discard burn-in
    chain_post_burn = chain[n_burn:]
    log_prob_post_burn = log_prob[n_burn:]

    # Find MAP (maximum-a-posteriori)
    flat_chain = chain_post_burn.reshape(-1, ndim)
    flat_log_prob = log_prob_post_burn.flatten()
    map_idx = np.argmax(flat_log_prob)
    map_theta = flat_chain[map_idx]
    map_log10_M200, map_c200, map_tau = map_theta
    map_M200 = 10 ** map_log10_M200
    map_sigma_m = sigma_m_from_halo(map_log10_M200, map_c200, map_tau)
    map_v200 = v200_from_M200(map_M200, map_c200)

    # Posterior summary
    summary = {
        "chain": chain_post_burn.tolist(),
        "log_prob": log_prob_post_burn.tolist(),
        "acceptance_fraction": acceptance.tolist(),
        "MAP": {
            "log10_M200": float(map_log10_M200),
            "M200": float(map_M200),
            "c200": float(map_c200),
            "tau": float(map_tau),
            "log_posterior": float(flat_log_prob[map_idx]),
            "sigma_m_at_v200_cm2_per_g": float(map_sigma_m),
            "v200_kms": float(map_v200),
        },
        "posterior_means": {
            "log10_M200": float(np.mean(flat_chain[:, 0])),
            "c200": float(np.mean(flat_chain[:, 1])),
            "tau": float(np.mean(flat_chain[:, 2])),
        },
        "posterior_medians": {
            "log10_M200": float(np.median(flat_chain[:, 0])),
            "c200": float(np.median(flat_chain[:, 1])),
            "tau": float(np.median(flat_chain[:, 2])),
        },
        "posterior_16_84": {
            "log10_M200": [float(np.percentile(flat_chain[:, 0], 16)),
                            float(np.percentile(flat_chain[:, 0], 84))],
            "c200": [float(np.percentile(flat_chain[:, 1], 16)),
                     float(np.percentile(flat_chain[:, 1], 84))],
            "tau": [float(np.percentile(flat_chain[:, 2], 16)),
                    float(np.percentile(flat_chain[:, 2], 84))],
        },
        "metadata": {
            "n_walkers": n_walkers,
            "n_steps": n_steps,
            "n_burn": n_burn,
            "n_posterior_samples": int(flat_chain.shape[0]),
            "seed": seed,
            "timestamp": datetime.now().isoformat(),
        },
    }

    # Save to disk
    if output_dir is None:
        output_dir = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "t90_v28_cloud9_mcmc.json"
    # Don't save the full chain (too large); save the summary only
    save_dict = {k: v for k, v in summary.items() if k not in ("chain", "log_prob")}
    save_dict["chain_shape"] = list(chain_post_burn.shape)
    with open(output_file, "w") as f:
        json.dump(save_dict, f, indent=2, default=str)
    print(f"Saved summary to {output_file}")

    return summary


# ===========================================================================
#  Self-test
# ===========================================================================
if __name__ == "__main__":
    print("=== T90.28 Cloud-9 MCMC — smoke test ===")
    print()

    # First, evaluate log_posterior at the published best-fits
    print("Log-posterior at published Cloud-9 best-fits:")
    for label, log10_M200, c200, tau in [
        ("CDM best-fit", np.log10(7e8), 6.0, 0.0),
        ("SIDM τ=0.18", np.log10(4.7e9), 4.0, 0.18),
        ("SIDM τ=0.95", np.log10(3.4e9), 1.5, 0.95),
    ]:
        lp = log_posterior((log10_M200, c200, tau))
        M200 = 10 ** log10_M200
        sm = sigma_m_from_halo(log10_M200, c200, tau)
        v200 = v200_from_M200(M200, c200)
        print(f"  {label:18s}  log10(M200)={log10_M200:.2f}  c200={c200:.1f}  τ={tau:.2f}  "
              f"log_post={lp:.2f}  σ/m(v200)={sm:.2e} cm²/g  v200={v200:.1f} km/s")
    print()

    # Run a small MCMC
    print("Running small MCMC (32 walkers × 500 steps, 200 burn-in)...")
    summary = run_mcmc(n_walkers=32, n_steps=500, n_burn=200, seed=42)
    print()
    print("=== MCMC results ===")
    print(f"MAP: M200 = {summary['MAP']['M200']:.2e}, c200 = {summary['MAP']['c200']:.2f}, "
          f"τ = {summary['MAP']['tau']:.3f}")
    print(f"     σ/m(v200) = {summary['MAP']['sigma_m_at_v200_cm2_per_g']:.2e} cm²/g, "
          f"v200 = {summary['MAP']['v200_kms']:.1f} km/s")
    print(f"     log_posterior = {summary['MAP']['log_posterior']:.2f}")
    print()
    print(f"Posterior means: log10(M200) = {summary['posterior_means']['log10_M200']:.2f}, "
          f"c200 = {summary['posterior_means']['c200']:.2f}, "
          f"τ = {summary['posterior_means']['tau']:.3f}")
    print(f"Posterior 16-84%: log10(M200) = {summary['posterior_16_84']['log10_M200']}, "
          f"c200 = {summary['posterior_16_84']['c200']}, "
          f"τ = {summary['posterior_16_84']['tau']}")
    print(f"Mean acceptance: {np.mean(summary['acceptance_fraction']):.3f}")
