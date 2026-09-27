"""
T107 — Full 8D joint fit: v0.7 MAP + δ + σ_PortalB.

Extends the 6D v0.7 MAP (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha,
log_xi) with two new dimensions for the LZ 248 keV Portal B:
  - log_delta_keV: inelastic mass splitting δ in [1, 1000] keV
  - log_sigma_PortalB: σ_DM-nuc for Portal B in [10^-48, 10^-39] cm²

Method: emcee MCMC (fast, 8D), starting from v0.7 MAP.
  - 64 walkers × 4000 steps = 256,000 post-burn-in samples
  - Gaussian priors on v0.7 parameters (16-84 widths)
  - LZ Table S8 likelihood for Portal B (from T101/T102)
  - DIAMX combined likelihood for PandaX-4T + XENONnT (from T106)

This is a "B1-lite": uses MCMC instead of full dynesty nested
sampling. Trades some precision for ~1000× speedup.

Expected wall time: 30-60 seconds (vs 4-10 hours for full dynesty).
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np


# v0.7 MAP values (from T41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json)
V07_MAP = {
    "log_m_phi_MeV": 2.770,
    "log_m_chi_GeV": 2.697,
    "g_chi": 1.576,
    "log_epsilon": -36.84,
    "log_alpha": -15.46,
    "log_xi": -0.798,
}

# 16-50-84 quantiles (approximate from v0.7)
V07_QUANTILES = {
    "log_m_phi_MeV": [2.671, 2.770, 2.866],
    "log_m_chi_GeV": [2.532, 2.697, 2.880],
    "g_chi": [1.305, 1.576, 1.857],
    "log_epsilon": [-52.63, -36.84, -16.0],
    "log_alpha": [-30.0, -15.46, -10.0],
    "log_xi": [-1.0, -0.798, 0.0],
}

# LZ Table S8 (T101)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t101_lz_data_extraction import TABLE_S8
from t102_portal_b_fit import interpolate_local_sig

# DIAMX best-fit (T106)
DIAMX_BEST_FIT = {
    "m_chi_GeV": 60.0,
    "delta_keV": 130.0,
    "sigma_local": {"LZ": 2.3, "PandaX-4T": 2.6, "XENONnT": 3.5},
    "uncertainties_1sigma": {"m_chi_GeV": 30.0, "delta_keV": 30.0},
}

PARAM_LABELS = [
    "log_m_phi_MeV", "log_m_chi_GeV", "g_chi",
    "log_epsilon", "log_alpha", "log_xi",
    "log_delta_keV", "log_sigma_PortalB",
]
N_PARAMS = len(PARAM_LABELS)


def log_prior_v07_gaussians(p):
    """Gaussian priors on v0.7 parameters + flat priors on δ, σ_PortalB."""
    lp = 0.0
    for i, label in enumerate(PARAM_LABELS[:6]):
        mu = V07_QUANTILES[label][1]
        sig = (V07_QUANTILES[label][2] - V07_QUANTILES[label][0]) / 2
        z = (p[i] - mu) / sig
        lp += -0.5 * z**2
    # Flat priors on δ and σ_PortalB
    # log_delta_keV in [0, 3] → δ in [1, 1000] keV
    if not (0.0 <= p[6] <= 3.0):
        return -1e10
    # log_sigma_PortalB in [-48, -39] → σ in [10^-48, 10^-39] cm²
    if not (-48.0 <= p[7] <= -39.0):
        return -1e10
    return lp


def log_likelihood_lz_portal_b(p):
    """LZ Table S8 likelihood at (m_chi, delta)."""
    m_chi_GeV = 10 ** p[1]
    delta_keV = 10 ** p[6]
    sig_local = interpolate_local_sig(m_chi_GeV, delta_keV, "Ov1")
    if math.isnan(sig_local):
        return 0.0
    # Wilks-style: log L = 0.5 * sigma^2
    return 0.5 * sig_local ** 2


def log_likelihood_diamx(p):
    """DIAMX combined likelihood (LZ + PandaX-4T + XENONnT) at (m_chi, delta)."""
    m_chi_GeV = 10 ** p[1]
    delta_keV = 10 ** p[6]
    d_mchi = (m_chi_GeV - DIAMX_BEST_FIT["m_chi_GeV"]) / DIAMX_BEST_FIT["uncertainties_1sigma"]["m_chi_GeV"]
    d_delta = (delta_keV - DIAMX_BEST_FIT["delta_keV"]) / DIAMX_BEST_FIT["uncertainties_1sigma"]["delta_keV"]
    z2 = d_mchi**2 + d_delta**2
    # Sum of squared significances
    total_sig2 = sum(s**2 for s in DIAMX_BEST_FIT["sigma_local"].values())
    return 0.5 * total_sig2 - 0.5 * z2


def log_posterior(p):
    """Joint 8D log-posterior."""
    lp = log_prior_v07_gaussians(p)
    if lp < -1e9:
        return -1e10
    ll_lz = log_likelihood_lz_portal_b(p)
    ll_diamx = log_likelihood_diamx(p)
    return lp + ll_lz + ll_diamx


def run_mcmc(n_walkers=64, n_steps=4000, seed=42):
    """Run emcee MCMC on the 8D posterior."""
    import emcee
    rng = np.random.default_rng(seed)

    # Initialize walkers near v0.7 MAP
    p0 = np.zeros((n_walkers, N_PARAMS))
    for i, label in enumerate(PARAM_LABELS[:6]):
        mu = V07_QUANTILES[label][1]
        sig = (V07_QUANTILES[label][2] - V07_QUANTILES[label][0]) / 4
        p0[:, i] = mu + sig * rng.standard_normal(n_walkers)
    # Initial delta near 297 keV (log ~ 2.47)
    p0[:, 6] = 2.47 + 0.2 * rng.standard_normal(n_walkers)
    # Initial sigma_PortalB near 10^-43
    p0[:, 7] = -43 + 1.0 * rng.standard_normal(n_walkers)

    sampler = emcee.EnsembleSampler(n_walkers, N_PARAMS, log_posterior)
    print(f"Running emcee: {n_walkers} walkers × {n_steps} steps on 8D posterior...")
    t0 = time.time()
    sampler.run_mcmc(p0, n_steps, progress=False)
    wall = time.time() - t0
    accept = float(np.mean(sampler.acceptance_fraction))
    print(f"  Acceptance: {accept:.3f}, wall time: {wall:.1f}s")

    # Discard burn-in
    burn = n_steps // 4
    chain = sampler.get_chain(discard=burn, flat=True)
    print(f"  Chain shape after burn-in: {chain.shape}")
    return chain, wall, accept


def analyze_chain(chain):
    """Compute MAP, median, 16-50-84 quantiles for each parameter."""
    results = {}
    for i, label in enumerate(PARAM_LABELS):
        samples = chain[:, i]
        # MAP via histogram mode
        hist, edges = np.histogram(samples, bins=50)
        idx = int(np.argmax(hist))
        map_val = float((edges[idx] + edges[idx+1]) / 2)
        results[label] = {
            "MAP": map_val,
            "median": float(np.median(samples)),
            "q16": float(np.percentile(samples, 16)),
            "q50": float(np.percentile(samples, 50)),
            "q84": float(np.percentile(samples, 84)),
        }
        # Also store physical units for some params
        if label == "log_delta_keV":
            results[label]["delta_keV_MAP"] = 10 ** map_val
            results[label]["delta_keV_median"] = 10 ** float(np.median(samples))
        elif label == "log_sigma_PortalB":
            results[label]["sigma_cm2_MAP"] = 10 ** map_val
            results[label]["sigma_cm2_median"] = 10 ** float(np.median(samples))
        elif label == "log_m_chi_GeV":
            results[label]["m_chi_GeV_MAP"] = 10 ** map_val
            results[label]["m_chi_GeV_median"] = 10 ** float(np.median(samples))
        elif label == "log_m_phi_MeV":
            results[label]["m_phi_MeV_MAP"] = 10 ** map_val
            results[label]["m_phi_MeV_median"] = 10 ** float(np.median(samples))
    return results


def main():
    out_dir = Path(__file__).resolve().parents[1] / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    chain, wall, accept = run_mcmc()
    results = analyze_chain(chain)

    # Compare to T103 and T106
    t103_MAP = {"m_chi_GeV": 483.0, "delta_keV": 295.0, "sigma_cm2": 10**-45.9}
    t106_best = DIAMX_BEST_FIT

    t107_MAP = {
        "m_chi_GeV": results["log_m_chi_GeV"]["m_chi_GeV_MAP"],
        "delta_keV": results["log_delta_keV"]["delta_keV_MAP"],
        "sigma_cm2": results["log_sigma_PortalB"]["sigma_cm2_MAP"],
        "m_phi_MeV": results["log_m_phi_MeV"]["m_phi_MeV_MAP"],
    }

    # Distance from T103
    d_t103_mchi = abs(math.log10(t107_MAP["m_chi_GeV"]) - math.log10(t103_MAP["m_chi_GeV"]))
    d_t103_delta = abs(math.log10(t107_MAP["delta_keV"]) - math.log10(t103_MAP["delta_keV"]))
    d_t103 = math.sqrt(d_t103_mchi**2 + d_t103_delta**2)

    # Distance from DIAMX
    d_diamx_mchi = abs(math.log10(t107_MAP["m_chi_GeV"]) - math.log10(t106_best["m_chi_GeV"]))
    d_diamx_delta = abs(math.log10(t107_MAP["delta_keV"]) - math.log10(t106_best["delta_keV"]))
    d_diamx = math.sqrt(d_diamx_mchi**2 + d_diamx_delta**2)

    print()
    print("=" * 70)
    print("T107 — 8D joint fit MAP:")
    print(f"  m_phi = {t107_MAP['m_phi_MeV']:.0f} MeV (v0.7: {10**V07_MAP['log_m_phi_MeV']:.0f} MeV)")
    print(f"  m_chi = {t107_MAP['m_chi_GeV']:.0f} GeV (v0.7: {10**V07_MAP['log_m_chi_GeV']:.0f} GeV)")
    print(f"  delta = {t107_MAP['delta_keV']:.1f} keV (T103: {t103_MAP['delta_keV']:.0f} keV, DIAMX: {t106_best['delta_keV']:.0f} keV)")
    print(f"  sigma_PortalB = {t107_MAP['sigma_cm2']:.2e} cm² (T103: {t103_MAP['sigma_cm2']:.2e} cm²)")
    print()
    print(f"  Distance from T103 (m_chi, delta) in log space: {d_t103:.2f}")
    print(f"  Distance from DIAMX (m_chi, delta) in log space: {d_diamx:.2f}")
    print()
    if d_diamx < 0.5:
        verdict = "T107 MAP is CONSISTENT with DIAMX (endothermic preference)"
    elif d_t103 < d_diamx:
        verdict = f"T107 MAP is CLOSER to T103 than to DIAMX (m_chi still ~500 GeV)"
    else:
        verdict = f"T107 MAP is CLOSER to DIAMX than to T103 (lighter mass preferred)"
    print(f"VERDICT: {verdict}")

    out = {
        "test": "T107_full_8d_joint_fit",
        "date": "2026-09-08",
        "description": (
            "Full 8D joint fit: 6 v0.7 parameters + (log_delta_keV, "
            "log_sigma_PortalB) using emcee MCMC with Gaussian priors "
            "on v0.7 and LZ Table S8 + DIAMX combined likelihood."
        ),
        "method": "emcee 8D MCMC, Gaussian priors on v0.7, LZ + DIAMX likelihood",
        "v07_MAP_prior_centers": V07_MAP,
        "DIAMX_best_fit": DIAMX_BEST_FIT,
        "mcmc_params": {
            "n_walkers": 64,
            "n_steps": 4000,
            "burn_in": 1000,
            "n_samples_post_burn": 192000,
        },
        "wall_time_seconds": wall,
        "acceptance_fraction": accept,
        "MAP_8d": t107_MAP,
        "all_parameter_results": results,
        "comparison": {
            "T103_MAP": t103_MAP,
            "DIAMX_best_fit": t106_best,
            "distance_log10_from_T103": d_t103,
            "distance_log10_from_DIAMX": d_diamx,
        },
        "verdict": verdict,
        "caveats": [
            "emcee is MCMC, not nested sampling; no log Z estimate",
            "Gaussian priors on v0.7, not full posterior — may overweight v0.7 region",
            "DIAMX likelihood is a 2D Gaussian approximation, not full profile likelihood",
            "Result depends on Gaussian prior widths; loose priors → broader MAP",
            "B1-lite: full 8D dynesty would take 4-10 hours and is not done here",
        ],
    }

    out_path = out_dir / "t107_full_8d_joint.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    main()
