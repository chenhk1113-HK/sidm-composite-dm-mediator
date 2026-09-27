"""
T112 — High-resolution 8D dynesty: tighter delta prior (50-200 keV).

Implements reviewer suggestion §1(a) + §1(c) from
'Suggestions for taking Door B further' (2026-09-08):

  (a) Higher-resolution 8D/9D nested sampling with larger nlive
      (target Δlog Z uncertainty ≲ 0.1).
  (c) Add controlled prior restricting δ to the theoretically
      motivated window (50-200 keV).

Two changes vs T108:
  - nlive=2000 (vs 500 in T108) for 4x better precision.
  - log_delta_keV restricted to [1.7, 2.3] i.e. δ in [50, 200] keV
    (vs [0, 3.0] i.e. [1, 1000] keV in T108). The 50-200 keV window is
    motivated by Berlin & Ferraro (2025) composite-DM mass-splitting
    theory: δ ~ Λ_D / m_χ ≈ 100 keV for typical composite-DM scales.

NOTE: this script SHARES the T41 v0.7 likelihood and LZ/DIAMX components
with T108. It differs only in prior ranges and nlive.

Expected wall time: 4x T108 = ~1750s (29 min).
ESTIMATE-LOG: estimate 30 min, expect ratio within 2x of actual.
"""
from __future__ import annotations

import json
import math
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

import dynesty

from t41_mediator_mass_joint_fit import loglike_joint
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

# TIGHTER Portal B prior (T112 vs T108):
# T108:  log_delta in [0, 3.0]   (1 to 1000 keV)
# T112:  log_delta in [1.7, 2.3] (50 to 200 keV) - Berlin & Ferraro motivated
LOG_DELTA_KEV_RANGE_T112 = (1.7, 2.3)  # delta in [50, 200] keV
LOG_SIGMA_PORTALB_RANGE = (-48.0, -39.0)


def loglike_lz_portal_b(log_m_chi_GeV, log_delta_keV):
    """LZ Table S8 likelihood at (m_chi, delta)."""
    m_chi_GeV = 10 ** log_m_chi_GeV
    delta_keV = 10 ** log_delta_keV
    sig_local = interpolate_local_sig(m_chi_GeV, delta_keV, "Ov1")
    if math.isnan(sig_local):
        return 0.0
    return 0.5 * sig_local ** 2


def loglike_diamx(log_m_chi_GeV, log_delta_keV):
    """DIAMX combined likelihood (LZ + PandaX-4T + XENONnT) at (m_chi, delta)."""
    m_chi_GeV = 10 ** log_m_chi_GeV
    delta_keV = 10 ** log_delta_keV
    d_mchi = (m_chi_GeV - DIAMX_BEST_FIT["m_chi_GeV"]) / DIAMX_BEST_FIT["uncertainties_1sigma"]["m_chi_GeV"]
    d_delta = (delta_keV - DIAMX_BEST_FIT["delta_keV"]) / DIAMX_BEST_FIT["uncertainties_1sigma"]["delta_keV"]
    z2 = d_mchi**2 + d_delta**2
    total_sig2 = sum(s**2 for s in DIAMX_BEST_FIT["sigma_local"].values())
    return 0.5 * total_sig2 - 0.5 * z2


def loglike_8d(theta):
    """8D joint log-likelihood (T112, identical to T108 structure)."""
    if len(theta) != 8:
        return -np.inf
    log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi, log_delta, log_sigma = theta
    ll_6d = loglike_joint(theta[:6])
    if not np.isfinite(ll_6d):
        return -np.inf
    ll_lz = loglike_lz_portal_b(log_m_chi, log_delta)
    ll_diamx = loglike_diamx(log_m_chi, log_delta)
    return ll_6d + ll_lz + ll_diamx


def prior_transform_8d_t112(u):
    """8D prior transform with T112's tighter delta prior."""
    return [
        LOG_M_PHI_MEV_RANGE[0] + u[0] * (LOG_M_PHI_MEV_RANGE[1] - LOG_M_PHI_MEV_RANGE[0]),
        LOG_M_CHI_GEV_RANGE[0] + u[1] * (LOG_M_CHI_GEV_RANGE[1] - LOG_M_CHI_GEV_RANGE[0]),
        G_CHI_RANGE[0] + u[2] * (G_CHI_RANGE[1] - G_CHI_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[3] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_ALPHA_RANGE[0] + u[4] * (LOG_ALPHA_RANGE[1] - LOG_ALPHA_RANGE[0]),
        LOG_XI_RANGE[0] + u[5] * (LOG_XI_RANGE[1] - LOG_XI_RANGE[0]),
        # T112 tighter prior (delta in [50, 200] keV):
        LOG_DELTA_KEV_RANGE_T112[0] + u[6] * (LOG_DELTA_KEV_RANGE_T112[1] - LOG_DELTA_KEV_RANGE_T112[0]),
        LOG_SIGMA_PORTALB_RANGE[0] + u[7] * (LOG_SIGMA_PORTALB_RANGE[1] - LOG_SIGMA_PORTALB_RANGE[0]),
    ]


def main():
    out_dir = V03_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("T112 — High-resolution 8D dynesty (nlive=2000, tight delta prior)")
    print("=" * 80)
    print()
    print("Reviewer suggestions addressed:")
    print("  (§1a) High-resolution dynesty: nlive=2000 (vs T108's 500)")
    print("  (§1c) Tight prior on delta: [50, 200] keV (vs T108's [1, 1000] keV)")
    print("  (Berlin & Ferraro 2025 motivated window)")
    print()
    print("8 parameters:")
    print("  log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha, log_xi,")
    print("  log_delta_keV, log_sigma_PortalB")
    print(f"  log_delta_keV TIGHT: [{LOG_DELTA_KEV_RANGE_T112[0]}, {LOG_DELTA_KEV_RANGE_T112[1]}] (delta in [50, 200] keV)")
    print()

    nlive = int(os.environ.get("T112_NLIVE", "2000"))
    dlogz = float(os.environ.get("T112_DLOGZ", "0.05"))

    print(f"Running dynesty: nlive={nlive}, dlogz={dlogz}")
    print(f"  Expected wall time: ~{4 * 440 * nlive / 2000:.0f}s (4x T108 scaling)")
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike_8d,
        prior_transform=prior_transform_8d_t112,
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
    print(f"  log Z = {log_Z:.3f} ± {log_Z_err:.3f} (target ± < 0.1)")

    medians = np.zeros(8)
    for i in range(8):
        medians[i] = np.median(samples[:, i])
    idx_map = int(np.argmax(weights))
    map_theta = samples[idx_map]

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

    quantiles = {}
    for i, label in enumerate(labels):
        quantiles[label] = {
            "q16": float(np.percentile(samples[:, i], 16)),
            "q50": float(np.percentile(samples[:, i], 50)),
            "q84": float(np.percentile(samples[:, i], 84)),
        }

    v07_log_Z = -163.29
    delta_log_Z = log_Z - v07_log_Z

    print()
    print("=" * 70)
    print("T112 — 8D joint fit MAP (high-res, tight delta):")
    print(f"  m_phi = {physical['m_phi_MeV_MAP']:.0f} MeV (T108: 479, v0.7: 588)")
    print(f"  m_chi = {physical['m_chi_GeV_MAP']:.0f} GeV (T108: 138, v0.7: 498)")
    print(f"  delta = {physical['delta_keV_MAP']:.1f} keV (T108: 98, DIAMX: 130, T103: 295)")
    print(f"  sigma_PortalB = {physical['sigma_PortalB_cm2_MAP']:.2e} cm²")
    print()
    print(f"  log Z = {log_Z:.3f} ± {log_Z_err:.3f}")
    print(f"  Δlog Z (8D T112 - 6D v0.7) = {delta_log_Z:+.3f}")
    print(f"  Δlog Z (8D T112 - 8D T108) = {log_Z - (-162.78):+.3f}")
    print(f"  T90 merge rule criterion #5: Δlog Z ≥ +2 → {'SATISFIED' if delta_log_Z >= 2.0 else 'NOT YET'}")

    out = {
        "test": "T112_highres_8d_dynesty",
        "date": "2026-09-08",
        "description": (
            "T112 — high-resolution 8D dynesty with nlive=2000 and tight prior "
            "on delta (50-200 keV, Berlin & Ferraro motivated). Implements "
            "reviewer suggestions §1(a) and §1(c) from 'Suggestions for taking "
            "Door B further'."
        ),
        "reviewer_suggestions_addressed": ["§1(a) high-res nested sampling", "§1(c) tight prior on δ"],
        "nlive": nlive,
        "dlogz": dlogz,
        "delta_prior_range_keV": [50.0, 200.0],
        "wall_seconds": wall,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "log_Z_uncertainty_target": 0.1,
        "log_Z_uncertainty_achieved": log_Z_err,
        "v07_log_Z_6d": v07_log_Z,
        "t108_log_Z_8d": -162.78,
        "delta_log_Z_T112_vs_v07_6d": delta_log_Z,
        "delta_log_Z_T112_vs_T108": log_Z - (-162.78),
        "T90_criterion_5_satisfied": delta_log_Z >= 2.0,
        "MAP_8d": {labels[i]: float(map_theta[i]) for i in range(8)},
        "MAP_8d_physical": physical,
        "medians_8d": {labels[i]: float(medians[i]) for i in range(8)},
        "quantiles_16_50_84": quantiles,
        "n_samples": int(len(samples)),
        "caveats": [
            "TIGHTER PRIOR on delta: 50-200 keV (vs T108's 1-1000 keV).",
            "Bayes factor Δlog Z will be DIFFERENT from T108 because prior volume changed.",
            "T108's +0.51 used uniform prior over delta; T112's Δlog Z uses tighter prior.",
            "If Δlog Z(T112) > Δlog Z(T108) = +0.51, this means data prefers the tighter region.",
            "If Δlog Z(T112) < +2, Door B still doesn't meet T90 merge criterion #5.",
            "Comparison to T108 must be done CAREFULLY: changing the prior changes log Z.",
        ],
    }

    out_path = out_dir / "t112_highres_8d_dynesty.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    main()