"""
Phase 23 — Cloud-9 Nuisance Marginalization

Cloud-9 / RELHIC has two key nuisance parameters:
  - M200 (halo mass): affects v200 (the relevant velocity scale)
  - c200 (concentration): affects rho_s, r_s (collapse timescale)

Current T90.29 uses fixed best-fit (M200=4.7e9, c200=4.0), giving loglike=-13.2
at T90.45 median. Phase 23 marginalizes over these nuisances to see if the
tension is from the halo assumption rather than the model.

If marginalization relaxes the constraint, Cloud-9 may go from -13 to ~0.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import t40_yukawa_sigma_m as yukawa
from t90_v29_relhic_yukawa import (
    CLOUD9_BESTFIT_M200, CLOUD9_BESTFIT_C200,
    tau_at_sigma_m_yukawa, _ensure_posterior_loaded, loglike_relhic_v29_yukawa,
)
import t90_v28_relhic_likelihood as _v28
import t90_v27_relhic_hydrostatic as t27
from scipy.interpolate import RegularGridInterpolator

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Halo nuisance prior: log-normal around published values
# Cloud-9 paper uncertainties: ~0.3 dex in M200, ~0.3 dex in c200
M200_PRIOR_SIGMA_DEX = 0.3  # log-normal sigma for M200
C200_PRIOR_SIGMA = 0.5  # half-Gaussian sigma for c200 (1-sided, c200 > 0)

# Grid for marginalization
M200_GRID = np.logspace(np.log10(1e9), np.log10(2e10), 25)  # 1e9 to 2e10 M_sun
C200_GRID = np.linspace(2.0, 8.0, 15)  # 2 to 8


def sigma_m_total_two_portal(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                              m_phi_B_MeV, m_chi_B_GeV, g_chi_B):
    """Total sigma/m from two portals."""
    sm_A = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A)
    sm_B = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    return sm_A + sm_B


def loglike_relhic_with_halo(sigma_m_at_v200, M200, c200):
    """Evaluate Cloud-9 likelihood at given (sigma_m, M200, c200)."""
    if sigma_m_at_v200 <= 0:
        return 0.0
    # Map to tau
    tau = tau_at_sigma_m_yukawa(sigma_m_at_v200, M200=M200, c200=c200)
    log10_sm = np.log10(sigma_m_at_v200)

    H = _v28._POSTERIOR_CACHE
    log10_sm_bins = _v28._LOG10_SM_BINS_CACHE
    tau_bins = _v28._TAU_BINS_CACHE

    if H is None:
        return 0.0
    if log10_sm < log10_sm_bins[0] or log10_sm > log10_sm_bins[-1]:
        return -10.0
    if tau < tau_bins[0] or tau > tau_bins[-1]:
        return -10.0

    # Bilinear interpolation
    i_sm = np.clip(np.searchsorted(log10_sm_bins, log10_sm) - 1, 0, H.shape[0] - 2)
    j_tau = np.clip(np.searchsorted(tau_bins, tau) - 1, 0, H.shape[1] - 2)

    sm_lo = log10_sm_bins[i_sm]
    sm_hi = log10_sm_bins[i_sm + 1]
    tau_lo = tau_bins[j_tau]
    tau_hi = tau_bins[j_tau + 1]

    f_sm = (log10_sm - sm_lo) / (sm_hi - sm_lo) if sm_hi > sm_lo else 0
    f_tau = (tau - tau_lo) / (tau_hi - tau_lo) if tau_hi > tau_lo else 0

    val = (H[i_sm, j_tau] * (1 - f_sm) * (1 - f_tau) +
           H[i_sm + 1, j_tau] * f_sm * (1 - f_tau) +
           H[i_sm, j_tau + 1] * (1 - f_sm) * f_tau +
           H[i_sm + 1, j_tau + 1] * f_sm * f_tau)

    return float(val)


def log_prior_M200(M200):
    """Log-normal prior on M200, mean = CLOUD9_BESTFIT_M200."""
    return -0.5 * ((np.log10(M200) - np.log10(CLOUD9_BESTFIT_M200)) / M200_PRIOR_SIGMA_DEX) ** 2


def log_prior_c200(c200):
    """Half-Gaussian prior on c200, mean = CLOUD9_BESTFIT_C200, sigma = 0.5."""
    return -0.5 * ((c200 - CLOUD9_BESTFIT_C200) / C200_PRIOR_SIGMA) ** 2


def marginalize_over_halo(theta, sigma_m_at_v200):
    """Marginalize Cloud-9 likelihood over (M200, c200) nuisance."""
    if sigma_m_at_v200 <= 0:
        return 0.0

    log_w = []
    loglikes = []
    for M200 in M200_GRID:
        for c200 in C200_GRID:
            ll_data = loglike_relhic_with_halo(sigma_m_at_v200, M200, c200)
            ll_prior = log_prior_M200(M200) + log_prior_c200(c200)
            log_w.append(ll_data + ll_prior)
            loglikes.append(ll_data)

    if not log_w:
        return 0.0

    # log-sum-exp for numerical stability
    log_w_arr = np.array(log_w)
    log_w_max = log_w_arr.max()
    log_evidence = log_w_max + np.log(np.sum(np.exp(log_w_arr - log_w_max)))

    # Approximate marginal likelihood as mean of loglikes weighted by exp(log_w - max)
    weights = np.exp(log_w_arr - log_w_max)
    weights /= weights.sum()
    log_marginal_ll = np.sum(weights * np.array(loglikes))

    return float(log_marginal_ll)


def main():
    # Force-load T90.28 posterior
    _ensure_posterior_loaded()
    if _v28._POSTERIOR_CACHE is None:
        print("ERROR: Could not load T90.28 posterior. Exiting.")
        return 1

    # Load T90.45 results
    t90_45_path = RESULTS_DIR / "t90_v45_multi_portal_joint_fit_nlive200.json"
    with open(t90_45_path) as f:
        t90_45 = json.load(f)

    # T90.45 median parameters
    p = t90_45["median_physical"]
    m_phi_A_MeV = p["m_phi_A_MeV"]
    m_chi_A_GeV = p["m_chi_A_GeV"]
    g_chi_A = p["g_chi_A"]
    m_phi_B_MeV = p["m_phi_B_MeV"]
    m_chi_B_GeV = p["m_chi_B_GeV"]
    g_chi_B = p["g_chi_B"]

    # Compute sigma/m at Cloud-9 v200 = 28 km/s
    sigma_m_at_v200 = sigma_m_total_two_portal(
        28, m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
        m_phi_B_MeV, m_chi_B_GeV, g_chi_B,
    )
    print(f"T90.45 median sigma/m(28) = {sigma_m_at_v200:.2f} cm^2/g")
    print(f"Cloud-9 required range: [30, 500] cm^2/g")
    print()

    # 1. Original Cloud-9 likelihood (no marginalization, fixed halo)
    print("=" * 60)
    print("1. Cloud-9 with FIXED halo (M200=4.7e9, c200=4.0)")
    print("=" * 60)
    tau_fixed = tau_at_sigma_m_yukawa(sigma_m_at_v200)
    ll_fixed = loglike_relhic_with_halo(sigma_m_at_v200, CLOUD9_BESTFIT_M200, CLOUD9_BESTFIT_C200)
    print(f"  tau = {tau_fixed:.4f}")
    print(f"  loglike = {ll_fixed:.2f}")
    print()

    # 2. Marginalized Cloud-9 likelihood (vary halo)
    print("=" * 60)
    print("2. Cloud-9 MARGINALIZED over (M200, c200)")
    print("=" * 60)
    ll_marginal = marginalize_over_halo(None, sigma_m_at_v200)
    print(f"  loglike = {ll_marginal:.2f}")
    print()

    # 3. Sweep sigma/m values to find best halo
    print("=" * 60)
    print("3. Sweep: find best halo for current sigma/m")
    print("=" * 60)
    best_ll = -np.inf
    best_M200 = None
    best_c200 = None
    for M200 in M200_GRID:
        for c200 in C200_GRID:
            ll = loglike_relhic_with_halo(sigma_m_at_v200, M200, c200)
            if ll > best_ll:
                best_ll = ll
                best_M200 = M200
                best_c200 = c200
    print(f"  Best halo: M200 = {best_M200:.2e}, c200 = {best_c200:.2f}")
    print(f"  Best loglike = {best_ll:.2f}")
    print()

    # 4. Marginalization evidence (log Z)
    print("=" * 60)
    print("4. Marginalization summary")
    print("=" * 60)
    delta_ll = ll_marginal - ll_fixed
    print(f"  Fixed-halo loglike: {ll_fixed:.2f}")
    print(f"  Marginalized loglike: {ll_marginal:.2f}")
    print(f"  Delta loglike (marginalization gain): {delta_ll:+.2f}")
    print()

    # Verdict
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    if ll_marginal > -2.0:
        print(f"  Cloud-9 PASSES after marginalization (loglike = {ll_marginal:.2f})")
        verdict = "PASS_AFTER_MARGINALIZATION"
    elif delta_ll > 5.0:
        print(f"  Cloud-9 IMPROVED by marginalization (Delta = {delta_ll:+.2f})")
        verdict = "IMPROVED_VIA_MARGINALIZATION"
    elif delta_ll > 0:
        print(f"  Cloud-9 slightly improved (Delta = {delta_ll:+.2f})")
        verdict = "SLIGHT_IMPROVEMENT"
    else:
        print(f"  Cloud-9 NOT helped by marginalization (Delta = {delta_ll:+.2f})")
        verdict = "NO_HELP"

    # Output
    out = {
        "test": "Phase23_cloud9_nuisance_marginalization",
        "median_params": {
            "m_phi_A_MeV": m_phi_A_MeV,
            "m_chi_A_GeV": m_chi_A_GeV,
            "g_chi_A": g_chi_A,
            "m_phi_B_MeV": m_phi_B_MeV,
            "m_chi_B_GeV": m_chi_B_GeV,
            "g_chi_B": g_chi_B,
        },
        "sigma_m_at_v200": sigma_m_at_v200,
        "fixed_halo_loglike": ll_fixed,
        "fixed_halo_params": {"M200": CLOUD9_BESTFIT_M200, "c200": CLOUD9_BESTFIT_C200},
        "marginalized_loglike": ll_marginal,
        "best_halo": {"M200": best_M200, "c200": best_c200, "loglike": best_ll},
        "delta_loglike_marginalization_gain": delta_ll,
        "nuisance_priors": {
            "M200": {"type": "log-normal", "mean": CLOUD9_BESTFIT_M200, "sigma_dex": M200_PRIOR_SIGMA_DEX},
            "c200": {"type": "half-gaussian", "mean": CLOUD9_BESTFIT_C200, "sigma": C200_PRIOR_SIGMA},
        },
        "marginalization_grid": {
            "M200_range": [float(M200_GRID[0]), float(M200_GRID[-1]), len(M200_GRID)],
            "c200_range": [float(C200_GRID[0]), float(C200_GRID[-1]), len(C200_GRID)],
        },
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase23_cloud9_nuisance_marginalization.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
