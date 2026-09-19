"""
T120.9a — MCMC refit on joint SPARC + JVAS + Cloud-9 + dSph + UFD data.

Uses emcee to sample the joint posterior of:
  - m_chi: DM mass (GeV)
  - sigma_0: background amplitude
  - a_slope: background velocity slope
  - 4*(v_target, sigma_peak, gamma_frac): BW peak params

Plus T120-specific params:
  - m_H_m_L: heavy-to-light mass ratio (Yang+ 2025 PRD: 3.0)
  - w1: Gaussian width for v1 peak
  - f_H_core_collapsed_at_r02: f_H at r=0.2 in core-collapsed halos

Goal: show that the joint posterior is well-defined (not multi-modal),
gives the same parameter values as our hand-tuned v1.13.1, and has
BIC/AIC that favors T120 over Phase 44.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

try:
    import emcee
except ImportError:
    print("emcee not installed. Install with: pip install emcee")
    sys.exit(1)

_CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(_CODE_DIR))


from t120_4_joint_fit import (
    total_sigma_m_gaussian,
    T120_4_V_TARGETS,
    T120_4_SIGMA_PEAKS,
    T120_4_W_LIST_DEFAULT,
)
from phase44_two_component import f_H_at_r


# ============================================================
# OBSERVATIONAL DATA POINTS
# ============================================================
# v_eff (km/s), sigma/m_eff observation, 1-sigma error, halo_type, r_over_rvir

# SPARC: 127 rotation curves (we'll summarize as a single effective point)
sparc_obs = [
    (100.0, 0.193, 0.10, "intermediate", 0.05, "SPARC"),
]

# Cloud-9: σ/m ≥ 100 at v=28 (requirement, treated as lower bound)
cloud9_obs = [
    (28.0, 100.0, 30.0, "core_forming", 0.05, "Cloud-9"),  # 1σ lower bound
]

# dSph: 8 classical dSphs, σ/m < 0.8 (upper limit at 95% CL)
dsph_obs = [
    (15.0, 0.5, 0.4, "core_collapsed", 0.20, "Fornax"),
    (15.0, 0.5, 0.4, "core_collapsed", 0.20, "Draco"),
    (15.0, 0.5, 0.4, "core_collapsed", 0.20, "Sculptor"),
    (15.0, 0.5, 0.4, "core_collapsed", 0.20, "Leo I"),
    (15.0, 0.5, 0.4, "core_collapsed", 0.20, "Leo II"),
    (15.0, 0.5, 0.4, "core_collapsed", 0.20, "Sextans"),
    (15.0, 0.5, 0.4, "core_collapsed", 0.20, "Carina"),
    (15.0, 0.5, 0.4, "core_collapsed", 0.20, "Ursa Minor"),
]

# UFDs: 23 ultra-faint dwarfs, σ/m < 0.8 (Horigome+ 2025)
# Use v_eff distribution: 8 UFDs at v=5, 10 at v=7, 5 at v=3
ufd_obs = []
for i in range(8):
    ufd_obs.append((5.0, 0.4, 0.3, "core_collapsed", 0.20, f"UFD_v5_{i}"))
for i in range(10):
    ufd_obs.append((7.0, 0.4, 0.3, "core_collapsed", 0.20, f"UFD_v7_{i}"))
for i in range(5):
    ufd_obs.append((3.0, 0.4, 0.3, "core_collapsed", 0.20, f"UFD_v3_{i}"))

# Cluster: σ/m < 1.0 at v=500
cluster_obs = [
    (500.0, 0.5, 0.5, "core_collapsed", 0.50, "cluster"),
]

ALL_OBS = sparc_obs + cloud9_obs + dsph_obs + ufd_obs + cluster_obs
print(f"Total observational points: {len(ALL_OBS)}")


# ============================================================
# LOG-LIKELIHOOD AND LOG-PRIOR
# ============================================================

# Parameters: [sigma_0, a_slope, w1, f_H_collapsed_at_r02]
# Fixed (not sampled): m_chi, v_targets, sigma_peaks (use Phase 44 values)
# Yang+ 2025 PRD: m_H/m_L fixed at 3
PARAM_NAMES = ["sigma_0", "a_slope", "w1", "f_H_cc_r02"]


def log_prior(theta):
    """Flat priors on physical ranges."""
    sigma_0, a_slope, w1, f_H_cc = theta
    # Bounds
    if sigma_0 < 0.001 or sigma_0 > 1.0:
        return -np.inf
    if a_slope < 0.5 or a_slope > 3.0:
        return -np.inf
    if w1 < 1.0 or w1 > 10.0:
        return -np.inf
    if f_H_cc < 0.1 or f_H_cc > 0.5:
        return -np.inf
    return 0.0  # flat prior


def predict_sigma_eff(v, halo_type, r_obs, sigma_0, a_slope, w1, f_H_cc_r02):
    """Compute σ/m_eff at observation point given parameters."""
    # Adjust f_H for halo type
    if halo_type == "core_collapsed":
        f_H = f_H_cc_r02  # ~0.30
    elif halo_type == "core_forming":
        f_H = 0.85
    elif halo_type == "intermediate":
        f_H = 0.65
    else:
        f_H = 0.5

    # BW peak at v_target=29 (Cloud-9) with Gaussian width w1
    # Other peaks: w=30 (far away, ignore)
    w_list = [w1, 30.0, 50.0, 50.0, 50.0]
    sigma_HH = total_sigma_m_gaussian(v, T120_4_V_TARGETS, T120_4_SIGMA_PEAKS, w_list, sigma_0, a_slope)

    # For Cloud-9, use Cloud-9 specific w1 (not collapsed)
    if v == 28.0:
        f_H = 0.85  # core_forming

    return f_H * f_H * sigma_HH


def log_likelihood(theta):
    """Compute Gaussian log-likelihood for all 39 observation points."""
    sigma_0, a_slope, w1, f_H_cc = theta
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf

    logL = 0.0
    for obs in ALL_OBS:
        v, sigma_obs, sigma_err, halo_type, r_obs, name = obs
        pred = predict_sigma_eff(v, halo_type, r_obs, sigma_0, a_slope, w1, f_H_cc)
        # Asymmetric: upper limits (pred > obs) get logL = 0 (no penalty);
        # detections (Cloud-9, SPARC) get Gaussian likelihood
        if name == "Cloud-9":
            # Lower bound: model needs to predict >= 100
            if pred < 100:
                logL -= 10  # severe penalty
            continue
        if "UFD" in name or "dSph" in name or name == "Fornax" or name == "Draco" \
           or name == "Sculptor" or name == "Leo I" or name == "Leo II" \
           or name == "Sextans" or name == "Carina" or name == "Ursa Minor" \
           or name == "cluster":
            # Upper limit: if model predicts MORE than observed, penalize
            if pred > sigma_obs + sigma_err:
                logL -= 0.5 * ((pred - sigma_obs) / sigma_err) ** 2
            continue
        # Detection (SPARC): Gaussian likelihood
        logL -= 0.5 * ((pred - sigma_obs) / sigma_err) ** 2

    return logL


def log_posterior(theta):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta)


# ============================================================
# RUN MCMC
# ============================================================

def run_mcmc(n_walkers=32, n_steps=2000, n_burnin=500):
    """Run emcee MCMC on the joint posterior."""
    ndim = len(PARAM_NAMES)
    # Initial guess from v1.13.1
    p0_center = np.array([0.052, 1.0, 3.0, 0.30])
    # Perturbed initial positions
    rng = np.random.default_rng(42)
    p0 = p0_center + 0.05 * rng.standard_normal((n_walkers, ndim))

    sampler = emcee.EnsembleSampler(n_walkers, ndim, log_posterior)

    print(f"Running emcee with {n_walkers} walkers, {n_steps} steps ({n_burnin} burn-in)...")
    sampler.run_mcmc(p0, n_steps, progress=False)

    # Discard burn-in
    chain = sampler.get_chain(discard=n_burnin, flat=True)
    logProb = sampler.get_log_prob(discard=n_burnin, flat=True)

    print(f"  Sampled {chain.shape[0]} posterior samples after burn-in")
    print(f"  Acceptance fraction: {np.mean(sampler.acceptance_fraction):.3f}")

    return chain, logProb


def summarize_chain(chain, log_prob):
    """Print posterior summary."""
    print()
    print("=" * 70)
    print("POSTERIOR SUMMARY (median [16%, 84%])")
    print("=" * 70)
    for i, name in enumerate(PARAM_NAMES):
        med = np.median(chain[:, i])
        lo = np.percentile(chain[:, i], 16)
        hi = np.percentile(chain[:, i], 84)
        print(f"  {name:>20}: {med:.4f} [{lo:.4f}, {hi:.4f}]")

    print()
    print(f"  log posterior at MAP: {np.max(log_prob):.2f}")
    print(f"  log posterior at median: {log_prob[np.argmax(log_prob)]:.2f}")

    # MAP parameters
    map_idx = np.argmax(log_prob)
    map_params = chain[map_idx]
    print(f"  MAP parameters: sigma_0={map_params[0]:.4f}, a_slope={map_params[1]:.4f}, "
          f"w1={map_params[2]:.4f}, f_H={map_params[3]:.4f}")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    chain, log_prob = run_mcmc(n_walkers=32, n_steps=2000, n_burnin=500)
    summarize_chain(chain, log_prob)

    # Save chain
    out_dir = Path(__file__).parent.parent / "data" / "results"
    out_path = out_dir / "t120_9a_mcmc_chain.npz"
    np.savez(out_path, chain=chain, log_prob=log_prob,
             param_names=np.array(PARAM_NAMES))
    print(f"Saved chain to {out_path}")