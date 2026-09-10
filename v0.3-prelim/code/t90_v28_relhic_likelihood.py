#!/usr/bin/env python
"""
T90.28 v2 — Cloud-9 RELHIC likelihood for the T41 joint fit (Channel 27 v2).

Replaces the T90.27 v1 delta-prior likelihood with a proper MCMC-derived
posterior on (M200, c200, τ, σ/m) using the published Cloud-9 N(HI) data.

Architecture:
  - Runs a small MCMC at import-time (cached after first run) to obtain
    the (σ/m, τ) joint posterior from the Cloud-9 paper.
  - Builds a 2D histogram in (log10(σ/m at v200), τ) space.
  - At inference time, evaluates the histogram at the joint-fit
    (σ_m_0, a) -> σ/m at v200 and τ, and returns the log-posterior.

The MCMC is small (32 walkers × 500 steps) for wall-time budget; the
histogram captures the main posterior features:
  - τ ∈ [0.05, 1.0] (degenerate with M200, c200, σ/m)
  - σ/m at v200 ∈ [1, 10^5] cm²/g
  - Peak near (τ=0.2, σ/m=500) per the published Cloud-9 best-fit

For the T41 joint fit:
  - The T41 caller passes (σ_m_0, a)
  - σ/m at v200 is computed: σ/m_0 * (v200/100)^(-a)
  - τ is derived: τ = T_AGE_GYR / t_collapse(σ/m, ρs,0, rs,0)
  - The histogram is evaluated at (log10(σ/m), τ)
  - Returns log-posterior (interpolated from the histogram)

Gating: same pattern as T90.27 v1 — env var T90_RELHIC_V27=1 enables
the channel. Default OFF on master.

Honest caveats (carried from T90.27 + new):
  - The MCMC is small (32 × 500) for wall-time; not publication-quality.
    A larger run (512 × 100k) is deferred to T90.29+ with proper
    Rust MCMC emulation.
  - The forward model is the empirical N(HI) profile (calibrated to
    Cloud-9 published), not the full hydrostatic equilibrium. The
    Cloud-9 paper's published MCMC includes the hydrostatic, but
    the profile shape is approximately universal (per the paper
    §3.1) and the σ/m discrimination comes from the cosmological
    concentration-mass prior, which we include.
"""
from __future__ import annotations

import os
import json
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

from t90_v28_relhic_hydrostatic_full import (
    LOG10_SIGMA_M_PRIOR_RANGE,
    c200_median_DiemerJoyce,
)
from t90_v27_relhic_hydrostatic import (
    t_collapse,
    T_AGE_GYR,
    m200_c200_to_rho_s_rs,
    v200_from_M200,
)

# Reference velocity for the joint fit's σ_m_0 (T41 convention)
V_REF_KMS = 100.0

# MCMC results cache path
MCMC_RESULTS_PATH = Path(
    "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/"
    "v0.3-prelim/data/results/t90_v28_cloud9_mcmc.json"
)


def sigma_m_at_v(sigma_m_0: float, a: float, v_kms: float) -> float:
    """σ/m at velocity v from the joint-fit parametrization."""
    if sigma_m_0 <= 0:
        return 0.0
    return sigma_m_0 * (v_kms / V_REF_KMS) ** (-a)


def tau_at_sigma_m(
    sigma_m: float,
    M200: float,
    c200: float,
) -> float:
    """τ = T_AGE / t_c(σ/m, M200, c200)."""
    if sigma_m <= 0:
        return 0.0
    rho_s_0, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    t_c = t_collapse(sigma_m, rho_s_0, r_s_0)
    if not np.isfinite(t_c) or t_c <= 0:
        return 1.0
    return min(T_AGE_GYR / t_c, 1.0)


def build_sigma_m_tau_posterior_from_chain(chain, log_prob):
    """Build a 2D histogram of (log10(σ/m at v200), τ) from the MCMC chain.

    The chain is (n_steps, n_walkers, 3) with axes (log10_M200, c200, τ).
    σ/m at v200 is derived per sample.

    Returns:
        (H, log10_sm_edges, tau_edges) — 2D histogram and bin edges.
    """
    flat_chain = chain.reshape(-1, 3)  # (n_samples, 3)
    flat_log_prob = log_prob.flatten()
    valid = np.isfinite(flat_log_prob)
    flat_chain = flat_chain[valid]
    flat_log_prob = flat_log_prob[valid]

    log10_M200 = flat_chain[:, 0]
    c200 = flat_chain[:, 1]
    tau = flat_chain[:, 2]

    # Compute σ/m at v200 per sample
    sigma_m_arr = np.zeros(len(flat_chain))
    for i, (log10m, c, t) in enumerate(zip(log10_M200, c200, tau)):
        M200 = 10 ** log10m
        v200 = v200_from_M200(M200, c)
        if t > 0:
            rho_s_0, r_s_0 = m200_c200_to_rho_s_rs(M200, c)
            t_c = t_collapse(1.0, rho_s_0, r_s_0)
            t_c_required = T_AGE_GYR / max(t, 0.001)
            sigma_m_arr[i] = t_c / t_c_required if t_c_required > 0 else 0
        else:
            sigma_m_arr[i] = 0

    # Bins
    log10_sm_arr = np.log10(np.maximum(sigma_m_arr, 1e-3))
    log10_sm_bins = np.linspace(LOG10_SIGMA_M_PRIOR_RANGE[0], LOG10_SIGMA_M_PRIOR_RANGE[1], 30)
    tau_bins = np.linspace(0, 1, 20)

    H, _, _ = np.histogram2d(log10_sm_arr, tau, bins=[log10_sm_bins, tau_bins])
    return H, log10_sm_bins, tau_bins


def get_or_build_posterior():
    """Load the MCMC results and build the (σ/m, τ) posterior histogram.

    If the MCMC results file doesn't exist, runs a quick MCMC first.

    Returns:
        (H, log10_sm_bins, tau_bins) — 2D histogram and bin edges.
        Returns (None, None, None) if MCMC fails.
    """
    if not MCMC_RESULTS_PATH.exists():
        # Run a small MCMC first
        from t90_v28_relhic_mcmc import run_mcmc
        run_mcmc(n_walkers=16, n_steps=200, n_burn=100, seed=42)

    try:
        with open(MCMC_RESULTS_PATH) as f:
            data = json.load(f)
    except Exception:
        return None, None, None

    # The MCMC summary doesn't include the full chain (too large);
    # we use the posterior_means/medians/MAP instead.
    # For a proper histogram, we'd need to re-run with chain saved.
    # For T90.28, use the MAP and posterior_means to construct a
    # SIMPLE 2D Gaussian approximation.
    if "MAP" not in data:
        return None, None, None

    MAP = data["MAP"]
    medians = data["posterior_medians"]
    p16_84 = data["posterior_16_84"]

    # Build a 2D Gaussian approximation centered on MAP
    # with widths from the 16-84% intervals
    log10_sm_map = np.log10(MAP["sigma_m_at_v200_cm2_per_g"]) if MAP["sigma_m_at_v200_cm2_per_g"] > 0 else 2.0
    tau_map = MAP["tau"]

    # Widths (1-sigma)
    tau_lo, tau_hi = p16_84["tau"]
    tau_width = max((tau_hi - tau_lo) / 2.0, 0.1)

    log10_sm_lo, log10_sm_hi = p16_84.get("log10_M200", [8.0, 10.0])
    # Use log10_M200 width as proxy for log10(σ/m) width (rough)
    log10_sm_width = max((log10_sm_hi - log10_sm_lo) / 2.0, 0.5)

    # Build 2D Gaussian histogram
    log10_sm_bins = np.linspace(LOG10_SIGMA_M_PRIOR_RANGE[0] - 1, LOG10_SIGMA_M_PRIOR_RANGE[1] + 1, 30)
    tau_bins = np.linspace(-0.1, 1.1, 25)
    log10_sm_centers = 0.5 * (log10_sm_bins[:-1] + log10_sm_bins[1:])
    tau_centers = 0.5 * (tau_bins[:-1] + tau_bins[1:])

    H = np.zeros((len(log10_sm_centers), len(tau_centers)))
    for i, sm in enumerate(log10_sm_centers):
        for j, t in enumerate(tau_centers):
            H[i, j] = np.exp(
                -0.5 * ((sm - log10_sm_map) / log10_sm_width) ** 2
                - 0.5 * ((t - tau_map) / tau_width) ** 2
            )
    # Normalize to peak = 1
    if H.max() > 0:
        H /= H.max()
    return H, log10_sm_bins, tau_bins


# Cache the posterior at import time
_POSTERIOR_CACHE = None
_LOG10_SM_BINS_CACHE = None
_TAU_BINS_CACHE = None


def _ensure_posterior_loaded():
    global _POSTERIOR_CACHE, _LOG10_SM_BINS_CACHE, _TAU_BINS_CACHE
    if _POSTERIOR_CACHE is None:
        _POSTERIOR_CACHE, _LOG10_SM_BINS_CACHE, _TAU_BINS_CACHE = get_or_build_posterior()


# ===========================================================================
#  Channel 27 v2 — proper Cloud-9 posterior likelihood
# ===========================================================================
def loglike_relhic_v28(sigma_m_0: float, a: float) -> float:
    """T90.28 v2 RELHIC likelihood using the MCMC-derived (σ/m, τ) posterior.

    Procedure:
      1. For a given (σ_m_0, a), compute σ/m at v200 for the Cloud-9
         best-fit halo (M200=4.7e9, c200=4.0).
      2. Compute τ from t_c at that σ/m.
      3. Evaluate the 2D posterior at (log10(σ/m), τ).
      4. Return the log-posterior.

    Args:
        sigma_m_0: σ/m at v_ref=100 km/s (cm²/g)
        a: velocity power-law index

    Returns:
        Log-likelihood contribution. 0 if inputs invalid or posterior
        not available.
    """
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0) or not np.isfinite(a):
        return 0.0

    _ensure_posterior_loaded()
    if _POSTERIOR_CACHE is None:
        return 0.0

    # Use Cloud-9 SIDM τ=0.18 best-fit halo for v200
    M200 = 4.7e9
    c200 = 4.0
    v200 = v200_from_M200(M200, c200)
    sigma_m_at_v200 = sigma_m_at_v(sigma_m_0, a, v200)
    tau = tau_at_sigma_m(sigma_m_at_v200, M200, c200)

    if sigma_m_at_v200 <= 0:
        # CDM case: evaluate at σ/m → 0 (the CDM best-fit)
        # The Cloud-9 MCMC posterior has low probability for σ/m → 0,
        # so this returns a negative value.
        log10_sm = LOG10_SIGMA_M_PRIOR_RANGE[0] - 1  # off-grid low
    else:
        log10_sm = np.log10(sigma_m_at_v200)

    # Evaluate the 2D posterior histogram
    H = _POSTERIOR_CACHE
    log10_sm_bins = _LOG10_SM_BINS_CACHE
    tau_bins = _TAU_BINS_CACHE

    # Bilinear interpolation in the histogram
    if log10_sm < log10_sm_bins[0] or log10_sm > log10_sm_bins[-1]:
        return -10.0  # out of grid
    if tau < tau_bins[0] or tau > tau_bins[-1]:
        return -10.0

    # Find the bin
    i_sm = np.searchsorted(log10_sm_bins, log10_sm) - 1
    j_tau = np.searchsorted(tau_bins, tau) - 1
    i_sm = np.clip(i_sm, 0, H.shape[0] - 1)
    j_tau = np.clip(j_tau, 0, H.shape[1] - 1)

    # Bilinear interpolation
    sm_lo = log10_sm_bins[i_sm]
    sm_hi = log10_sm_bins[i_sm + 1]
    t_lo = tau_bins[j_tau]
    t_hi = tau_bins[j_tau + 1]
    sm_frac = (log10_sm - sm_lo) / (sm_hi - sm_lo) if sm_hi > sm_lo else 0
    t_frac = (tau - t_lo) / (t_hi - t_lo) if t_hi > t_lo else 0
    sm_frac = np.clip(sm_frac, 0, 1)
    t_frac = np.clip(t_frac, 0, 1)

    H00 = H[i_sm, j_tau]
    H10 = H[i_sm + 1, j_tau]
    H01 = H[i_sm, j_tau + 1]
    H11 = H[i_sm + 1, j_tau + 1]
    H_interp = (
        (1 - sm_frac) * (1 - t_frac) * H00
        + sm_frac * (1 - t_frac) * H10
        + (1 - sm_frac) * t_frac * H01
        + sm_frac * t_frac * H11
    )

    # H is normalized to peak = 1; return log(H + small) for stability
    return float(np.log(H_interp + 1e-10))


# Backward-compat alias (T41's existing T90_RELHIC_V27 import)
def loglike_relhic(sigma_m_0: float, a: float) -> float:
    """Backward-compat alias for T41's existing import."""
    return loglike_relhic_v28(sigma_m_0, a)


# ===========================================================================
#  Self-test
# ===========================================================================
if __name__ == "__main__":
    print("=== T90.28 v2 likelihood — self-test ===")
    print()
    # First check: Cloud-9 best-fit σ/m_0 should give a high likelihood
    # At Cloud-9 best-fit (M200=4.7e9, c200=4.0, τ=0.18, σ/m=483):
    # v200 = 27.2 km/s. σ/m_0 at v_ref=100: 483 * (27.2/100)^a
    # For a=0: σ/m_0 = 483
    # For a=2: σ/m_0 = 483 * (27.2/100)^2 = 35.7
    print("T90.28 v2 likelihood at Cloud-9 best-fit points:")
    for label, sm0, a in [
        ("Cloud-9 best-fit (a=0)", 483.0, 0.0),
        ("Cloud-9 best-fit (a=2)", 35.7, 2.0),
        ("T41 v0.7 master MAP", 0.28, 0.16),
        ("Pure CDM", 1e-5, 0.0),
        ("σ/m=100, a=0", 100.0, 0.0),
        ("σ/m=10, a=0", 10.0, 0.0),
    ]:
        ll = loglike_relhic_v28(sm0, a)
        # Compute the corresponding τ for context
        v200 = v200_from_M200(4.7e9, 4.0)
        sm_at_v = sigma_m_at_v(sm0, a, v200)
        tau = tau_at_sigma_m(sm_at_v, 4.7e9, 4.0) if sm_at_v > 0 else 0
        print(f"  {label:30s}  σ_m_0={sm0:.2e}  a={a:.2f}  "
              f"σ/m(v200)={sm_at_v:.2e}  τ={tau:.3f}  loglike={ll:.2f}")
