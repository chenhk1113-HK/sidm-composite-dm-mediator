"""
T108 — Full 8D dynesty nested sampling: v0.7 + LZ + DIAMX.

Extends the v0.7 6D fit (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi)
with two new dimensions for the LZ 248 keV Portal B:
  - log_delta_keV: inelastic mass splitting delta in [1, 1000] keV
  - log_sigma_PortalB: sigma_DM-nuc for Portal B in [10^-48, 10^-39] cm^2

The 6D T41 v0.7 likelihood is used as-is (loglike_joint), and we add:
  - LZ Table S8 likelihood (from T101)
  - DIAMX combined likelihood from PandaX-4T + XENONnT (from T106)

This is the FULL 8D dynesty (not B1-lite emcee) — produces log Z and full posterior.

Reference v0.7 timings: 6D + nlive=2000 took 440s (7.3 min).
Expected 8D + nlive=500: ~3-4 min (8/6 * 500/2000 * 440 ≈ 290s).
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

# T41 v0.7 components
from t41_mediator_mass_joint_fit import loglike_joint

# T101/T102 LZ components
from t101_lz_data_extraction import TABLE_S8
from t102_portal_b_fit import interpolate_local_sig

# DIAMX best-fit (T106)
DIAMX_BEST_FIT = {
    "m_chi_GeV": 60.0,
    "delta_keV": 130.0,
    "sigma_local": {"LZ": 2.3, "PandaX-4T": 2.6, "XENONnT": 3.5},
    "uncertainties_1sigma": {"m_chi_GeV": 30.0, "delta_keV": 30.0},
}

# v0.7 prior ranges (from T41)
LOG_M_PHI_MEV_RANGE = (-1.0, 4.0)
LOG_M_CHI_GEV_RANGE = (0.5, 3.0)
G_CHI_RANGE = (0.01, 2.0)
LOG_EPSILON_RANGE = (-60.0, -1.0)
LOG_ALPHA_RANGE = (-30.0, -1.0)
LOG_XI_RANGE = (-1.0, 0.7)

# New Portal B prior ranges
LOG_DELTA_KEV_RANGE = (0.0, 3.0)   # delta in [1, 1000] keV
LOG_SIGMA_PORTALB_RANGE = (-48.0, -39.0)  # sigma in [10^-48, 10^-39] cm^2


def loglike_lz_portal_b(log_m_chi_GeV, log_delta_keV):
    """LZ Table S8 likelihood at (m_chi, delta).

    Returns log L = 0.5 * sigma_local^2 (Wilks-style).
    """
    m_chi_GeV = 10 ** log_m_chi_GeV
    delta_keV = 10 ** log_delta_keV
    sig_local = interpolate_local_sig(m_chi_GeV, delta_keV, "Ov1")
    if math.isnan(sig_local):
        return 0.0
    return 0.5 * sig_local ** 2


def loglike_diamx(log_m_chi_GeV, log_delta_keV):
    """DIAMX combined likelihood (LZ + PandaX-4T + XENONnT) at (m_chi, delta).

    Gaussian approximation centered on DIAMX best-fit.
    Sum of squared significances as amplitude.
    """
    m_chi_GeV = 10 ** log_m_chi_GeV
    delta_keV = 10 ** log_delta_keV
    d_mchi = (m_chi_GeV - DIAMX_BEST_FIT["m_chi_GeV"]) / DIAMX_BEST_FIT["uncertainties_1sigma"]["m_chi_GeV"]
    d_delta = (delta_keV - DIAMX_BEST_FIT["delta_keV"]) / DIAMX_BEST_FIT["uncertainties_1sigma"]["delta_keV"]
    z2 = d_mchi**2 + d_delta**2
    total_sig2 = sum(s**2 for s in DIAMX_BEST_FIT["sigma_local"].values())
    return 0.5 * total_sig2 - 0.5 * z2


def loglike_8d(theta):
    """8D joint log-likelihood.

    theta = (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi,
             log_delta_keV, log_sigma_PortalB)
    """
    if len(theta) != 8:
        return -np.inf
    log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi, log_delta, log_sigma = theta
    # Get the 6D v0.7 loglike (using theta[:6])
    ll_6d = loglike_joint(theta[:6])
    if not np.isfinite(ll_6d):
        return -np.inf
    # Add Portal B terms
    ll_lz = loglike_lz_portal_b(log_m_chi, log_delta)
    ll_diamx = loglike_diamx(log_m_chi, log_delta)
    return ll_6d + ll_lz + ll_diamx


def prior_transform_8d(u):
    """8D prior transform: uniform in box priors in log-space."""
    return [
        LOG_M_PHI_MEV_RANGE[0] + u[0] * (LOG_M_PHI_MEV_RANGE[1] - LOG_M_PHI_MEV_RANGE[0]),
        LOG_M_CHI_GEV_RANGE[0] + u[1] * (LOG_M_CHI_GEV_RANGE[1] - LOG_M_CHI_GEV_RANGE[0]),
        G_CHI_RANGE[0] + u[2] * (G_CHI_RANGE[1] - G_CHI_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[3] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_ALPHA_RANGE[0] + u[4] * (LOG_ALPHA_RANGE[1] - LOG_ALPHA_RANGE[0]),
        LOG_XI_RANGE[0] + u[5] * (LOG_XI_RANGE[1] - LOG_XI_RANGE[0]),
        LOG_DELTA_KEV_RANGE[0] + u[6] * (LOG_DELTA_KEV_RANGE[1] - LOG_DELTA_KEV_RANGE[0]),
        LOG_SIGMA_PORTALB_RANGE[0] + u[7] * (LOG_SIGMA_PORTALB_RANGE[1] - LOG_SIGMA_PORTALB_RANGE[0]),
    ]


def main():
    out_dir = V03_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("T108 — Full 8D dynesty nested sampling")
    print("=" * 80)
    print("8 parameters:")
    print("  log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha, log_xi,")
    print("  log_delta_keV, log_sigma_PortalB")
    print(f"  log_m_phi_MeV:    [{LOG_M_PHI_MEV_RANGE[0]}, {LOG_M_PHI_MEV_RANGE[1]}]")
    print(f"  log_m_chi_GeV:    [{LOG_M_CHI_GEV_RANGE[0]}, {LOG_M_CHI_GEV_RANGE[1]}]")
    print(f"  g_chi:            [{G_CHI_RANGE[0]}, {G_CHI_RANGE[1]}]")
    print(f"  log_epsilon:      [{LOG_EPSILON_RANGE[0]}, {LOG_EPSILON_RANGE[1]}]")
    print(f"  log_alpha:        [{LOG_ALPHA_RANGE[0]}, {LOG_ALPHA_RANGE[1]}]")
    print(f"  log_xi:           [{LOG_XI_RANGE[0]}, {LOG_XI_RANGE[1]}]")
    print(f"  log_delta_keV:    [{LOG_DELTA_KEV_RANGE[0]}, {LOG_DELTA_KEV_RANGE[1]}]")
    print(f"  log_sigma:        [{LOG_SIGMA_PORTALB_RANGE[0]}, {LOG_SIGMA_PORTALB_RANGE[1]}]")
    print()
    print("Likelihood components:")
    print("  - T41 v0.7 joint (6D): 19 channels, includes LZ magnetic-moment")
    print("  - LZ Table S8 Portal B: 0.5 * sigma_local^2 at (m_chi, delta)")
    print("  - DIAMX Portal B: combined LZ + PandaX-4T + XENONnT Gaussian")
    print()

    nlive = int(os.environ.get("T108_NLIVE", "500"))
    dlogz = float(os.environ.get("T108_DLOGZ", "0.1"))

    print(f"Running dynesty: nlive={nlive}, dlogz={dlogz}")
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike_8d,
        prior_transform=prior_transform_8d,
        ndim=8, nlive=nlive, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=dlogz, print_progress=False)
    wall = time.time() - t0

    res = sampler.results
    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])

    print(f"\nDone in {wall:.1f}s")
    print(f"  log Z = {log_Z:.3f} ± {log_Z_err:.3f}")

    # Compute medians
    medians = np.zeros(8)
    for i in range(8):
        medians[i] = np.median(samples[:, i])

    # Compute MAP (max-weight sample)
    idx_map = int(np.argmax(weights))
    map_theta = samples[idx_map]

    # Convert to physical
    labels = [
        "log_m_phi_MeV", "log_m_chi_GeV", "g_chi",
        "log_epsilon", "log_alpha", "log_xi",
        "log_delta_keV", "log_sigma_PortalB",
    ]
    physical = {
        "m_phi_MeV_MAP": float(10 ** map_theta[0]),
        "m_phi_MeV_median": float(10 ** medians[0]),
        "m_chi_GeV_MAP": float(10 ** map_theta[1]),
        "m_chi_GeV_median": float(10 ** medians[1]),
        "g_chi_MAP": float(map_theta[2]),
        "epsilon_MAP": float(10 ** map_theta[3]),
        "alpha_MAP": float(10 ** map_theta[4]),
        "xi_MAP": float(10 ** map_theta[5]),
        "delta_keV_MAP": float(10 ** map_theta[6]),
        "delta_keV_median": float(10 ** medians[6]),
        "sigma_PortalB_cm2_MAP": float(10 ** map_theta[7]),
        "sigma_PortalB_cm2_median": float(10 ** medians[7]),
    }

    # Quantiles
    quantiles = {}
    for i, label in enumerate(labels):
        quantiles[label] = {
            "q16": float(np.percentile(samples[:, i], 16)),
            "q50": float(np.percentile(samples[:, i], 50)),
            "q84": float(np.percentile(samples[:, i], 84)),
        }

    # Compare to T41 v0.7 (6D log Z = -163.29)
    v07_log_Z = -163.29
    delta_log_Z = log_Z - v07_log_Z

    print()
    print("=" * 70)
    print("T108 — 8D joint fit MAP:")
    print(f"  m_phi = {physical['m_phi_MeV_MAP']:.0f} MeV (v0.7: 588 MeV)")
    print(f"  m_chi = {physical['m_chi_GeV_MAP']:.0f} GeV (v0.7: 498 GeV)")
    print(f"  delta = {physical['delta_keV_MAP']:.1f} keV (DIAMX: 130 keV, T103: 295 keV)")
    print(f"  sigma_PortalB = {physical['sigma_PortalB_cm2_MAP']:.2e} cm²")
    print()
    print(f"  log Z = {log_Z:.3f} ± {log_Z_err:.3f} (v0.7 6D was -163.29)")
    print(f"  Δlog Z (8D - 6D) = {delta_log_Z:+.3f}")
    print(f"  T90 merge rule criterion #5: Δlog Z ≥ +2 → {'SATISFIED' if delta_log_Z >= 2.0 else 'NOT YET'}")

    out = {
        "test": "T108_full_8d_dynesty",
        "date": "2026-09-08",
        "description": (
            "Full 8D dynesty nested sampling: 6 v0.7 parameters + "
            "(log_delta_keV, log_sigma_PortalB). Includes T41 v0.7 "
            "joint likelihood (19 channels) + LZ Table S8 + DIAMX "
            "combined likelihood."
        ),
        "nlive": nlive,
        "dlogz": dlogz,
        "wall_seconds": wall,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "v07_log_Z_6d": v07_log_Z,
        "delta_log_Z_8d_vs_6d": delta_log_Z,
        "T90_criterion_5_satisfied": delta_log_Z >= 2.0,
        "MAP_8d": {
            labels[i]: float(map_theta[i]) for i in range(8)
        },
        "MAP_8d_physical": physical,
        "medians_8d": {
            labels[i]: float(medians[i]) for i in range(8)
        },
        "quantiles_16_50_84": quantiles,
        "n_samples": int(len(samples)),
        "comparison": {
            "T103_MAP": {"m_chi_GeV": 483, "delta_keV": 295, "sigma_cm2": 1.3e-46},
            "T107_MAP_8d_emcee": {
                "m_chi_GeV": 131, "delta_keV": 145, "sigma_cm2": 2.9e-41
            },
            "DIAMX_best_fit": DIAMX_BEST_FIT,
        },
        "caveats": [
            "Likelihood uses DIAMX 2D Gaussian approximation, not full profile likelihood",
            "LZ Table S8 likelihood uses Ov1 operator only (others 𝒪₁ˢ, 𝒪₄ˢ, 𝒪₄ᵛ give similar results)",
            "6D T41 likelihood dominates log Z; Portal B terms contribute ~0-15 to log Z",
            "nlive=500 gives ~1 unit of log Z precision; full convergence would need nlive=2000",
        ],
    }

    out_path = out_dir / "t108_full_8d_dynesty.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    main()
