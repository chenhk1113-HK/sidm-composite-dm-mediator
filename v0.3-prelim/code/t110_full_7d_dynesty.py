"""
T110 — Full 7D dynesty nested sampling: v0.7 + μ_χ (magnetic-moment Ls₁₀).

Extends the v0.7 6D fit (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi)
with ONE new dimension for the LZ magnetic-moment EFT Ls₁₀ channel:
  - log_mu_x_mu_N: μ_χ in units of nuclear magnetons, range [-7, -3]

The 6D T41 v0.7 likelihood is used as-is (loglike_joint), with the 7th
parameter passed via the env var T90_MAGNETIC_MOMENT_MU_X (which T41 reads
on the WIP branch to activate Channel 26: LZ magnetic-moment EFT).

This is the FULL 7D dynesty (not a B1-lite emcee) — produces log Z and
full posterior, which can be compared to v0.7 6D log Z = -163.29.

T90 merge rule criterion #5 requires Δlog Z >= +2 to satisfy.
T108 8D fit (Portal B, different parameter) gave Δlog Z = +0.51.

REFERENCE TIMINGS:
  - v0.7 6D, nlive=2000: 440s
  - T108 8D, nlive=500:  438s (Portal B, not mu_chi)
  - T110 7D, nlive=500: ~440s (1 more param than 6D, 1 fewer than 8D)

LIKELIHOOD COMPONENTS:
  - T41 v0.7 joint (6D): 19 channels, includes LZ magnetic-moment if env var set
  - Channel 26: LZ magnetic-moment EFT Ls₁₀, env-var-gated
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
V03_ROOT = SCRIPT_DIR.parent
V01_ROOT = V03_ROOT.parent.parent / "v0.1-prelim"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(V01_ROOT))
sys.path.insert(0, str(V01_ROOT / "code"))

import dynesty

# T41 v0.7 6D likelihood (with env-var-gated Channel 26)
from t41_mediator_mass_joint_fit import loglike_joint

# v0.7 prior ranges (from T41)
LOG_M_PHI_MEV_RANGE = (-1.0, 4.0)
LOG_M_CHI_GEV_RANGE = (0.5, 3.0)
G_CHI_RANGE = (0.01, 2.0)
LOG_EPSILON_RANGE = (-60.0, -1.0)
LOG_ALPHA_RANGE = (-30.0, -1.0)
LOG_XI_RANGE = (-1.0, 0.7)

# Magnetic-moment (Door B) prior range
# Composite-DM naturalness: mu_chi ~ e*hbar/(2*m_chi) * (m_psi/Lambda_D)^2 * alpha_D
# For m_psi ~ 100 GeV, Lambda_D ~ 1 GeV, alpha_D ~ 0.5: mu_chi ~ 10^-4 mu_N
# Prior spans [10^-7, 10^-3] mu_N (7 OOM), motivated by composite naturalness
LOG_MU_X_MU_N_RANGE = (-7.0, -3.0)


def loglike_7d(theta):
    """7D joint log-likelihood: v0.7 6D + magnetic-moment Ls_1_0.

    theta = (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi, log_mu_x_mu_N)

    The 7th parameter (log_mu_x_mu_N) is passed to T41's loglike_joint
    via the T90_MAGNETIC_MOMENT_MU_X env var. T41 reads this and activates
    Channel 26 (LZ magnetic-moment EFT).
    """
    if len(theta) != 7:
        return -np.inf
    log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi, log_mu_x = theta

    # Set the env var for T41's Channel 26
    mu_x_mu_N = 10 ** log_mu_x
    os.environ["T90_MAGNETIC_MOMENT_MU_X"] = f"{mu_x_mu_N:.6e}"
    os.environ["T90_MAGNETIC_MOMENT_BINNED"] = "1"

    # Call the canonical 6D T41 loglike (which now reads the env var)
    ll = loglike_joint((log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi))

    # If non-finite (numerical issue), return heavy penalty
    if not np.isfinite(ll):
        return -1e6

    return float(ll)


def prior_transform_7d(u):
    """Convert unit cube [0,1]^7 to physical prior via inverse CDF.

    u: array of shape (7,) with values in [0,1]
    returns: array of shape (7,) with values in the physical prior ranges
    """
    u = np.asarray(u, dtype=float)
    if u.shape != (7,):
        raise ValueError(f"Expected shape (7,), got {u.shape}")

    theta = np.empty(7)
    # Uniform in log-space for scale-invariant priors
    theta[0] = LOG_M_PHI_MEV_RANGE[0] + u[0] * (LOG_M_PHI_MEV_RANGE[1] - LOG_M_PHI_MEV_RANGE[0])
    theta[1] = LOG_M_CHI_GEV_RANGE[0] + u[1] * (LOG_M_CHI_GEV_RANGE[1] - LOG_M_CHI_GEV_RANGE[0])
    # g_chi: uniform in [0.01, 2.0]
    theta[2] = G_CHI_RANGE[0] + u[2] * (G_CHI_RANGE[1] - G_CHI_RANGE[0])
    theta[3] = LOG_EPSILON_RANGE[0] + u[3] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0])
    theta[4] = LOG_ALPHA_RANGE[0] + u[4] * (LOG_ALPHA_RANGE[1] - LOG_ALPHA_RANGE[0])
    theta[5] = LOG_XI_RANGE[0] + u[5] * (LOG_XI_RANGE[1] - LOG_XI_RANGE[0])
    # Magnetic-moment prior: uniform in log-space
    theta[6] = LOG_MU_X_MU_N_RANGE[0] + u[6] * (LOG_MU_X_MU_N_RANGE[1] - LOG_MU_X_MU_N_RANGE[0])

    return theta


def main():
    nlive = int(os.environ.get("T110_NLIVE", "500"))
    dlogz = float(os.environ.get("T110_DLOGZ", "0.1"))

    print("=" * 70)
    print("T110 — 7D joint fit: v0.7 + μ_χ (magnetic-moment Ls₁₀)")
    print("=" * 70)
    print()
    print("Likelihood components:")
    print("  - T41 v0.7 joint (6D): 19 channels, includes LZ magnetic-moment via env var")
    print("  - Channel 26: LZ magnetic-moment EFT Ls₁₀, env-var-gated")
    print()
    print(f"Running dynesty: nlive={nlive}, dlogz={dlogz}")
    print()

    t0 = time.time()

    sampler = dynesty.NestedSampler(
        loglike_7d,
        prior_transform_7d,
        ndim=7,
        nlive=nlive,
        logl_args=(),
        ptform_args=(),
    )
    sampler.run_nested(dlogz=dlogz, print_progress=False)

    wall_seconds = time.time() - t0
    results = sampler.results

    log_z = float(results.logz[-1])
    log_z_err = float(results.logzerr[-1])

    # Get posterior samples (weighted)
    weights = np.exp(results.logwt - results.logz[-1])
    samples_equal = results.samples  # unweighted, equal weights
    log_likes = results.logl

    # MAP estimate (sample with highest log L)
    map_idx = int(np.argmax(log_likes))
    map_sample = samples_equal[map_idx]

    # Median (from weighted samples)
    medians = np.zeros(7)
    for i in range(7):
        medians[i] = np.average(samples_equal[:, i], weights=weights)

    # 16th / 84th percentiles (1-sigma)
    q16 = np.zeros(7)
    q84 = np.zeros(7)
    for i in range(7):
        order = np.argsort(samples_equal[:, i])
        sorted_w = weights[order]
        cum_w = np.cumsum(sorted_w)
        sorted_x = samples_equal[order, i]
        q16[i] = np.interp(0.16, cum_w / cum_w[-1], sorted_x)
        q84[i] = np.interp(0.84, cum_w / cum_w[-1], sorted_x)

    # v0.7 6D reference (from canonical t41 result)
    log_z_v07_6d = -163.29  # canonical T41 v0.7 result, nlive=2000

    delta_log_z = log_z - log_z_v07_6d
    t90_criterion_5 = delta_log_z >= 2.0

    print()
    print("=" * 70)
    print(f"Done in {wall_seconds:.1f}s")
    print(f"  log Z = {log_z:.3f} ± {log_z_err:.3f}")
    print()
    print("=" * 70)
    print("T110 — 7D joint fit MAP:")
    print(f"  m_phi = {10**map_sample[0]:.0f} MeV (v0.7: 588 MeV)")
    print(f"  m_chi = {10**map_sample[1]:.1f} GeV (v0.7: 498 GeV)")
    print(f"  g_chi = {map_sample[2]:.3f} (v0.7: 0.45)")
    print(f"  log_epsilon = {map_sample[3]:.2f} (v0.7: -36.95)")
    print(f"  log_alpha = {map_sample[4]:.2f} (v0.7: -16.17)")
    print(f"  log_xi = {map_sample[5]:.3f} (v0.7: 0.00)")
    print(f"  log_mu_x_mu_N = {map_sample[6]:.2f}  (=> mu_x = {10**map_sample[6]:.2e} mu_N)")
    print()
    print(f"  log Z = {log_z:.3f} ± {log_z_err:.3f} (v0.7 6D was {log_z_v07_6d:.2f})")
    print(f"  Δlog Z (7D - 6D) = {delta_log_z:+.3f}")
    print(f"  T90 merge rule criterion #5: Δlog Z ≥ +2 → {'SATISFIED' if t90_criterion_5 else 'NOT YET'}")
    print()

    # Output JSON
    out_dir = V03_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "t110_full_7d_dynesty.json"

    out = {
        "nlive": nlive,
        "dlogz": dlogz,
        "wall_seconds": wall_seconds,
        "log_z": log_z,
        "log_z_err": log_z_err,
        "delta_log_z_vs_v07_6d": delta_log_z,
        "t90_merge_criterion_5_satisfied": bool(t90_criterion_5),
        "map_sample_log_space": {
            "log_m_phi_MeV": float(map_sample[0]),
            "log_m_chi_GeV": float(map_sample[1]),
            "g_chi": float(map_sample[2]),
            "log_epsilon": float(map_sample[3]),
            "log_alpha": float(map_sample[4]),
            "log_xi": float(map_sample[5]),
            "log_mu_x_mu_N": float(map_sample[6]),
        },
        "map_sample_physical": {
            "m_phi_MeV": float(10 ** map_sample[0]),
            "m_chi_GeV": float(10 ** map_sample[1]),
            "g_chi": float(map_sample[2]),
            "epsilon": float(10 ** map_sample[3]),
            "alpha": float(10 ** map_sample[4]),
            "xi": float(10 ** map_sample[5]),
            "mu_x_mu_N": float(10 ** map_sample[6]),
        },
        "medians_log_space": {
            "log_m_phi_MeV": float(medians[0]),
            "log_m_chi_GeV": float(medians[1]),
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
            "T110 7D dynesty: v0.7 6D + μ_χ (magnetic-moment Ls₁₀). "
            "T90 merge rule criterion #5 requires Δlog Z ≥ +2. "
            f"Δlog Z = {delta_log_z:+.3f}. "
            f"{'SATISFIED' if t90_criterion_5 else 'NOT YET SATISFIED'}."
        ),
    }

    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
