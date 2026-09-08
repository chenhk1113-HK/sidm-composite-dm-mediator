"""
T110-emcee — 7D emcee joint fit: v0.7 + μ_χ (B1-lite fallback).

Falls back to emcee when the full dynesty 7D fit (T110) cannot
converge due to the LZ magnetic-moment penalty surface.

This is the B1-lite analog of T107 (which was the 8D emcee analog of
T108's 8D dynesty). It produces a MAP estimate and approximate log Z,
but is NOT a proper nested-sampling result.

For the proper nested-sampling result, see t110_full_7d_dynesty.py.

Reference T107 timings: 8D emcee ran in ~5 min with 32 walkers,
2000 steps. T110-emcee should be similar.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
V03_ROOT = SCRIPT_DIR.parent
V01_ROOT = V03_ROOT.parent.parent / "v0.1-prelim"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(V01_ROOT))
sys.path.insert(0, str(V01_ROOT / "code"))

import emcee

from t110_full_7d_dynesty import (
    LOG_M_PHI_MEV_RANGE,
    LOG_M_CHI_GEV_RANGE,
    G_CHI_RANGE,
    LOG_EPSILON_RANGE,
    LOG_ALPHA_RANGE,
    LOG_XI_RANGE,
    LOG_MU_X_MU_N_RANGE,
    loglike_7d,
)


def log_prior_7d(theta):
    """Uniform prior on the 7D box (in log/linear space as defined)."""
    if len(theta) != 7:
        return -np.inf
    log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi, log_mu_x = theta
    if not (LOG_M_PHI_MEV_RANGE[0] <= log_m_phi <= LOG_M_PHI_MEV_RANGE[1]):
        return -np.inf
    if not (LOG_M_CHI_GEV_RANGE[0] <= log_m_chi <= LOG_M_CHI_GEV_RANGE[1]):
        return -np.inf
    if not (G_CHI_RANGE[0] <= g_chi <= G_CHI_RANGE[1]):
        return -np.inf
    if not (LOG_EPSILON_RANGE[0] <= log_eps <= LOG_EPSILON_RANGE[1]):
        return -np.inf
    if not (LOG_ALPHA_RANGE[0] <= log_alpha <= LOG_ALPHA_RANGE[1]):
        return -np.inf
    if not (LOG_XI_RANGE[0] <= log_xi <= LOG_XI_RANGE[1]):
        return -np.inf
    if not (LOG_MU_X_MU_N_RANGE[0] <= log_mu_x <= LOG_MU_X_MU_N_RANGE[1]):
        return -np.inf
    return 0.0


def log_prob_7d(theta):
    """emcee log-probability = log_prior + log_like."""
    lp = log_prior_7d(theta)
    if not np.isfinite(lp):
        return -np.inf
    ll = loglike_7d(theta)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def main():
    nwalkers = int(os.environ.get("T110EMC_NWALKERS", "32"))
    nsteps = int(os.environ.get("T110EMC_NSTEPS", "2000"))
    burn = int(os.environ.get("T110EMC_BURN", "500"))

    print("=" * 70)
    print("T110-emcee — 7D joint fit (B1-lite): v0.7 + μ_χ")
    print("=" * 70)
    print()
    print(f"nwalkers={nwalkers}, nsteps={nsteps}, burn={burn}")
    print()

    # Initialize walkers around v0.7 MAP with log mu_x ~ -5
    rng = np.random.RandomState(42)
    p0 = np.zeros((nwalkers, 7))
    p0[:, 0] = np.log10(588) + 0.1 * rng.randn(nwalkers)
    p0[:, 1] = np.log10(498) + 0.1 * rng.randn(nwalkers)
    p0[:, 2] = 0.45 + 0.05 * rng.randn(nwalkers)
    p0[:, 3] = -36.95 + 0.5 * rng.randn(nwalkers)
    p0[:, 4] = -16.17 + 0.5 * rng.randn(nwalkers)
    p0[:, 5] = 0.0 + 0.05 * rng.randn(nwalkers)
    p0[:, 6] = -5.0 + 0.3 * rng.randn(nwalkers)

    # Clip to prior
    p0[:, 0] = np.clip(p0[:, 0], LOG_M_PHI_MEV_RANGE[0], LOG_M_PHI_MEV_RANGE[1])
    p0[:, 1] = np.clip(p0[:, 1], LOG_M_CHI_GEV_RANGE[0], LOG_M_CHI_GEV_RANGE[1])
    p0[:, 2] = np.clip(p0[:, 2], G_CHI_RANGE[0], G_CHI_RANGE[1])
    p0[:, 3] = np.clip(p0[:, 3], LOG_EPSILON_RANGE[0], LOG_EPSILON_RANGE[1])
    p0[:, 4] = np.clip(p0[:, 4], LOG_ALPHA_RANGE[0], LOG_ALPHA_RANGE[1])
    p0[:, 5] = np.clip(p0[:, 5], LOG_XI_RANGE[0], LOG_XI_RANGE[1])
    p0[:, 6] = np.clip(p0[:, 6], LOG_MU_X_MU_N_RANGE[0], LOG_MU_X_MU_N_RANGE[1])

    t0 = time.time()

    sampler = emcee.EnsembleSampler(nwalkers, 7, log_prob_7d)
    sampler.run_mcmc(p0, nsteps, progress=False)

    wall_seconds = time.time() - t0

    # Get samples after burn-in
    samples = sampler.get_chain(discard=burn, flat=True)
    log_probs = sampler.get_log_prob(discard=burn, flat=True)

    # MAP
    map_idx = int(np.argmax(log_probs))
    map_sample = samples[map_idx]

    # Median
    medians = np.median(samples, axis=0)
    q16 = np.percentile(samples, 16, axis=0)
    q84 = np.percentile(samples, 84, axis=0)

    # Approximate log Z using log-sum-exp on log posterior samples
    # (assumes flat prior; log Z ≈ log(mean) over samples in prior volume)
    # This is a rough estimate, not nested-sampling quality.
    log_post_max = np.max(log_probs)
    log_Z_approx = log_post_max + np.log(np.mean(np.exp(log_probs - log_post_max))) - np.log(len(samples))

    log_z_v07_6d = -163.29
    delta_log_z_approx = log_Z_approx - log_z_v07_6d

    print()
    print("=" * 70)
    print(f"Done in {wall_seconds:.1f}s (emcee, NOT nested sampling)")
    print(f"  Approx log Z = {log_Z_approx:.3f}")
    print()
    print("T110-emcee — 7D joint fit MAP:")
    print(f"  m_phi = {10**map_sample[0]:.0f} MeV (v0.7: 588 MeV)")
    print(f"  m_chi = {10**map_sample[1]:.1f} GeV (v0.7: 498 GeV)")
    print(f"  g_chi = {map_sample[2]:.3f} (v0.7: 0.45)")
    print(f"  log_epsilon = {map_sample[3]:.2f} (v0.7: -36.95)")
    print(f"  log_alpha = {map_sample[4]:.2f} (v0.7: -16.17)")
    print(f"  log_xi = {map_sample[5]:.3f} (v0.7: 0.00)")
    print(f"  log_mu_x_mu_N = {map_sample[6]:.2f}  (=> mu_x = {10**map_sample[6]:.2e} mu_N)")
    print()
    print(f"  Approx log Z (emcee estimate) = {log_Z_approx:.3f}")
    print(f"  Δlog Z (7D - 6D, approx) = {delta_log_z_approx:+.3f}")
    print(f"  ⚠ This is an EMCEE APPROXIMATION, not nested-sampling evidence.")
    print()

    # Output JSON
    out_dir = V03_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "t110_emcee_7d_fallback.json"

    out = {
        "nwalkers": nwalkers,
        "nsteps": nsteps,
        "burn": burn,
        "wall_seconds": wall_seconds,
        "log_z_approx_emcee": log_Z_approx,
        "log_z_err_approx_emcee": float(np.std(log_probs) / np.sqrt(len(log_probs))),
        "delta_log_z_vs_v07_6d_approx": delta_log_z_approx,
        "t90_merge_criterion_5_satisfied_approx": bool(delta_log_z_approx >= 2.0),
        "method": "emcee (NOT nested sampling; this is a B1-lite fallback)",
        "map_sample_physical": {
            "m_phi_MeV": float(10 ** map_sample[0]),
            "m_chi_GeV": float(10 ** map_sample[1]),
            "g_chi": float(map_sample[2]),
            "epsilon": float(10 ** map_sample[3]),
            "alpha": float(10 ** map_sample[4]),
            "xi": float(10 ** map_sample[5]),
            "mu_x_mu_N": float(10 ** map_sample[6]),
        },
        "medians_physical": {
            "m_phi_MeV": float(10 ** medians[0]),
            "m_chi_GeV": float(10 ** medians[1]),
            "g_chi": float(medians[2]),
            "log_epsilon": float(medians[3]),
            "log_alpha": float(medians[4]),
            "log_xi": float(medians[5]),
            "log_mu_x_mu_N": float(medians[6]),
        },
        "q16_log_space": {k: float(q16[i]) for i, k in enumerate(["log_m_phi_MeV", "log_m_chi_GeV", "g_chi", "log_epsilon", "log_alpha", "log_xi", "log_mu_x_mu_N"])},
        "q84_log_space": {k: float(q84[i]) for i, k in enumerate(["log_m_phi_MeV", "log_m_chi_GeV", "g_chi", "log_epsilon", "log_alpha", "log_xi", "log_mu_x_mu_N"])},
        "v07_6d_log_z": log_z_v07_6d,
        "comment": (
            "T110-emcee B1-lite fallback. Uses emcee instead of dynesty "
            "because the full T110 dynesty fit could not converge on the "
            "LZ magnetic-moment penalty surface (sharp -1000 cliff). "
            "MAP and approximate log Z are emcee estimates; not nested-sampling "
            "evidence. For the proper result, see T110_full_7d_dynesty.py "
            "if it can be made to converge."
        ),
    }

    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
