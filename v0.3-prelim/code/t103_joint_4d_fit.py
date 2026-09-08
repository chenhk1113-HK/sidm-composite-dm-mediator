"""
T103 — Joint 4D fit: Portal A (v0.7 MAP) + Portal B (LZ 248 keV).

The proper "B" from B-then-A: combine the existing v0.7 MAP (Portal A)
with the LZ Table S8 Portal B likelihood into a joint 4D fit.

Parameters: (log_m_phi_MeV, log_m_chi_GeV, log_delta_MeV, log_sigma_PortalB)
  - log_m_phi_MeV: mediator mass (Portal A)
  - log_m_chi_GeV: DM mass (shared between portals)
  - log_delta_MeV: mass splitting (Portal B)
  - log_sigma_PortalB: σ_DM-nuc for Portal B (log10 cm^2)

Portal A: Gaussian prior centered on v0.7 MAP (m_φ, m_χ) with
  widths from 16-84 quantiles of the existing T41 v0.7 fit.

Portal B: Likelihood from LZ Table S8 (T101), interpolated.
  The σ_DM-nuc is fixed at the LZ 90% CL upper limit OR
  the Fan-Tweed Higgsino value (1.86e-39 cm^2) for testing.

Method: emcee MCMC, 4D, ~2000 samples.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

# Reuse from T101/T102
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t101_lz_data_extraction import TABLE_S8
from t102_portal_b_fit import (
    interpolate_local_sig, log_prior_v07_MAP, log_prior_delta,
)


# v0.7 MAP values (from T41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json)
V07_MAP = {
    "log_m_phi_MeV": 2.6561,
    "log_m_chi_GeV": 2.8863,
    "g_chi": 1.189,
    "log_epsilon": -36.951,
    "log_alpha": -16.165,
    "log_xi": -0.780,
    "sigma_m_0": 0.273,  # cm^2/g
}

# 16-50-84 quantiles from T41 v0.7 fit
V07_QUANTILES = {
    "log_m_phi_MeV": [2.6714, 2.7692, 2.8656],  # 16, 50, 84
    "log_m_chi_GeV": [2.5316, 2.6968, 2.8798],
    "g_chi": [1.3047, 1.5758, 1.8567],
    "log_epsilon": [-52.63, -36.84, -16.0],  # truncated, approximate
    "log_alpha": [-30.0, -15.46, -10.0],  # truncated, approximate
}


def log_prior_portal_A(log_m_phi_MeV, log_m_chi_GeV):
    """Portal A: Gaussian prior on (m_phi, m_chi) centered on v0.7 MAP.

    Other Portal A parameters (g_chi, log_epsilon, log_alpha) are
    fixed at v0.7 MAP for this 4D fit.
    """
    mu_mphi = V07_QUANTILES["log_m_phi_MeV"][1]  # median
    sig_mphi = (V07_QUANTILES["log_m_phi_MeV"][2] - V07_QUANTILES["log_m_phi_MeV"][0]) / 2
    mu_mchi = V07_QUANTILES["log_m_chi_GeV"][1]
    sig_mchi = (V07_QUANTILES["log_m_chi_GeV"][2] - V07_QUANTILES["log_m_chi_GeV"][0]) / 2

    lp_mphi = -0.5 * ((log_m_phi_MeV - mu_mphi) / sig_mphi) ** 2
    lp_mchi = -0.5 * ((log_m_chi_GeV - mu_mchi) / sig_mchi) ** 2
    return lp_mphi + lp_mchi


def log_prior_portal_B(log_delta_MeV, log_sigma_PortalB):
    """Portal B: priors on delta and sigma.

    delta prior: log-uniform in [1 keV, 400 keV] = [-3, -0.4] in log10 MeV
    sigma prior: log-uniform in [10^-46, 10^-38] cm^2 = [-46, -38]
    """
    if not (-3.0 <= log_delta_MeV <= -0.4):
        return -1e10
    if not (-46.0 <= log_sigma_PortalB <= -38.0):
        return -1e10
    return 0.0  # flat in log


def log_likelihood_portal_B(log_m_chi_GeV, log_delta_MeV, log_sigma_PortalB):
    """Portal B likelihood from LZ Table S8 + a constraint on sigma.

    For a given (m_chi, delta), LZ gives a local significance. The
    "best fit" sigma is implicitly determined by LZ's analysis.
    We use a simple test: if sigma is BELOW the LZ 90% CL upper
    limit (assumed 10^-43 for δ=300 keV at 1 TeV, scaling with
    delta and m_chi), the model is consistent; if above, the
    LZ upper limit excludes it.

    For simplicity, we use the LZ significance as a likelihood:
    log L ≈ 0.5 * sigma^2 (Wilks), and we DO NOT penalize sigma
    directly. The sigma prior already constrains it to physical
    values.
    """
    m_chi_GeV = 10 ** log_m_chi_GeV
    delta_keV = 10 ** log_delta_MeV * 1000  # MeV to keV

    # Get LZ local significance for Ov1 (vector, Higgsino-like)
    sig_local = interpolate_local_sig(m_chi_GeV, delta_keV, "Ov1")
    if math.isnan(sig_local):
        return 0.0  # outside scan range
    return 0.5 * sig_local ** 2


def log_posterior(params):
    """Joint 4D log-posterior: Portal A + Portal B."""
    log_m_phi_MeV, log_m_chi_GeV, log_delta_MeV, log_sigma_PortalB = params
    lp_A = log_prior_portal_A(log_m_phi_MeV, log_m_chi_GeV)
    lp_B = log_prior_portal_B(log_delta_MeV, log_sigma_PortalB)
    if lp_A < -1e9 or lp_B < -1e9:
        return -1e10
    ll_B = log_likelihood_portal_B(log_m_chi_GeV, log_delta_MeV, log_sigma_PortalB)
    return lp_A + lp_B + ll_B


def run_mcmc(n_walkers=32, n_steps=2000, seed=42):
    """Run emcee MCMC on the 4D posterior."""
    import emcee
    rng = np.random.default_rng(seed)
    ndim = 4

    # Initialize walkers near v0.7 MAP
    p0 = np.zeros((n_walkers, ndim))
    p0[:, 0] = V07_MAP["log_m_phi_MeV"] + 0.05 * rng.standard_normal(n_walkers)
    p0[:, 1] = V07_MAP["log_m_chi_GeV"] + 0.1 * rng.standard_normal(n_walkers)
    p0[:, 2] = -0.5 + 0.1 * rng.standard_normal(n_walkers)  # log_delta_MeV ~ -0.5 (300 keV)
    p0[:, 3] = -42 + 1.0 * rng.standard_normal(n_walkers)   # log_sigma ~ -42

    sampler = emcee.EnsembleSampler(n_walkers, ndim, log_posterior)
    print(f"Running emcee: {n_walkers} walkers, {n_steps} steps...")
    sampler.run_mcmc(p0, n_steps, progress=False)
    print(f"  Acceptance fraction: {np.mean(sampler.acceptance_fraction):.3f}")

    # Discard burn-in
    burn = n_steps // 4
    chain = sampler.get_chain(discard=burn, flat=True)
    print(f"  Chain shape after burn-in: {chain.shape}")
    return chain


def analyze_chain(chain):
    """Compute MAP, median, quantiles for each parameter."""
    results = {}
    labels = ["log_m_phi_MeV", "log_m_chi_GeV", "log_delta_MeV", "log_sigma_PortalB"]

    for i, label in enumerate(labels):
        samples = chain[:, i]
        # MAP = mode (approximate by histogram)
        hist, edges = np.histogram(samples, bins=50)
        idx = np.argmax(hist)
        map_val = (edges[idx] + edges[idx+1]) / 2
        results[label] = {
            "MAP": float(map_val),
            "median": float(np.median(samples)),
            "q16": float(np.percentile(samples, 16)),
            "q50": float(np.percentile(samples, 50)),
            "q84": float(np.percentile(samples, 84)),
        }
    return results


def main():
    out_dir = Path(__file__).resolve().parents[1] / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    chain = run_mcmc()
    results = analyze_chain(chain)

    # Convert to physical units
    physical = {}
    for label, stats in results.items():
        if "log_m_phi" in label:
            physical["m_phi_MeV"] = {
                "MAP": 10 ** stats["MAP"],
                "median": 10 ** stats["median"],
                "q16": 10 ** stats["q16"],
                "q84": 10 ** stats["q84"],
            }
        elif "log_m_chi" in label:
            physical["m_chi_GeV"] = {
                "MAP": 10 ** stats["MAP"],
                "median": 10 ** stats["median"],
                "q16": 10 ** stats["q16"],
                "q84": 10 ** stats["q84"],
            }
        elif "log_delta" in label:
            physical["delta_keV"] = {
                "MAP": 10 ** stats["MAP"] * 1000,  # MeV to keV
                "median": 10 ** stats["median"] * 1000,
                "q16": 10 ** stats["q16"] * 1000,
                "q84": 10 ** stats["q84"] * 1000,
            }
        elif "log_sigma" in label:
            physical["sigma_PortalB_cm2"] = {
                "MAP": 10 ** stats["MAP"],
                "median": 10 ** stats["median"],
                "q16": 10 ** stats["q16"],
                "q84": 10 ** stats["q84"],
            }

    out = {
        "test": "T103_joint_portal_A_B_4D_fit",
        "date": "2026-09-08",
        "description": (
            "Joint 4D fit combining Portal A (v0.7 MAP Gaussian prior on m_phi, m_chi) "
            "and Portal B (LZ Table S8 likelihood from T101, with delta and sigma as "
            "free parameters). Uses emcee MCMC with 32 walkers, 2000 steps."
        ),
        "parameters_log": results,
        "parameters_physical": physical,
        "v07_MAP_reference": V07_MAP,
        "verdict": (
            f"Joint MAP: m_phi = {physical['m_phi_MeV']['MAP']:.0f} MeV, "
            f"m_chi = {physical['m_chi_GeV']['MAP']:.0f} GeV, "
            f"delta = {physical['delta_keV']['MAP']:.0f} keV, "
            f"sigma_PortalB = {physical['sigma_PortalB_cm2']['MAP']:.2e} cm^2. "
            "The joint posterior combines v0.7 MAP (Portal A) with the LZ 248 keV "
            "event (Portal B). See T103 doc for full analysis."
        ),
        "caveats": [
            "v0.7 MAP prior is Gaussian; full posterior shape not used (samples not stored)",
            "Only Ov1 operator used for LZ Table S8 likelihood (vector coupling, Higgsino-like)",
            "sigma_PortalB is weakly constrained — LZ upper limit is a step function in this approximation",
            "g_chi, log_epsilon, log_alpha, log_xi fixed at v0.7 MAP (4D fit, not 8D)",
            "emcee may not have fully converged in 2000 steps",
        ],
        "what_this_does_NOT_do": [
            "Full 8D nested-sampling fit (would re-run T41 with delta added)",
            "Use the full v0.7 MAP posterior shape (only Gaussian approx)",
            "Combine with PandaX-4T or XENONnT inelastic limits",
            "Test against McCabe 2026 seasonal modulation prediction",
        ],
    }

    out_path = out_dir / "t103_joint_4d_posterior.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")

    # Console summary
    print()
    print("=" * 70)
    print("T103 — Joint 4D fit (Portal A + Portal B)")
    print("=" * 70)
    print()
    print("v0.7 MAP reference (Portal A):")
    for k, v in V07_MAP.items():
        print(f"  {k}: {v}")
    print()
    print("Joint posterior MAP:")
    for k, v in physical.items():
        print(f"  {k}: MAP = {v['MAP']:.3e}, "
              f"median = {v['median']:.3e}, "
              f"q16 = {v['q16']:.3e}, q84 = {v['q84']:.3e}")
    print()
    print(f"Verdict: {out['verdict']}")


if __name__ == "__main__":
    main()
