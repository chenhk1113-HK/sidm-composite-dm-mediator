#!/usr/bin/env python
"""
T90.51 -- Resonant SIDM joint posterior.

Minimum viable 6D joint fit over the Breit-Wigner + Sommerfeld resonant
SIDM parametric form. Channels: Cloud-9 (RELHIC, v=28 km/s),
Galactic dSph/UFD (v=100 km/s), Bullet Cluster (v=3000 km/s).

Parameters (6D, all log-uniform):
    log_m_chi_GeV: DM mass (GeV)
    log_E_R_eV:    resonance energy (eV)
    log_Gamma_R_eV: resonance width (eV)
    log_sigma_0:   background sigma/m (cm^2/g)
    log_alpha_Y:   dark Yukawa coupling
    log_m_phi_MeV: mediator mass (MeV) -- sets Yukawa mediator contribution

Likelihood: per-channel Gaussian in log(sigma/m) with published/scan-derived
constraints. The three channels are independent so loglike is a sum.

Per T90.50 scan results (12/144 compatible), the resonant best-fit is:
    m_chi=30 GeV, E_R=65 eV, Gamma_R=0.1 eV, sigma_0=0.01 cm^2/g, alpha_Y=0.01
    sigma/m(C9) = 40.6, sigma/m(Gal) = 0.94, sigma/m(Bul) = 0.041

References:
    Chu, Garcia-Cely, Murayama 2019 (PRL 122, 071103; arXiv:1805.03203)
    Kim, Lee, Zhu 2021 (JHEP 10, 239; arXiv:2108.06278)
    Super-resonant DM 2025 (arXiv:2511.09306)
    arXiv:2608.04362 (Cloud-9 RELHIC)
    T90.50 (predecessor: point scan, this script lifts it to joint posterior)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v50_resonant_sidm import (
    sigma_m_resonant,
    kinetic_energy_eV,
)

# --------------------------------------------------------------------------
# Channel constraints
# --------------------------------------------------------------------------
# Cloud-9 (arXiv:2608.04362 RELHIC): sigma/m(28) in [30, 500] cm^2/g
# Treated as Gaussian in log10(sigma/m), centered at log10 of geometric mean
# of the allowed range, with width covering the range.
_CLOUD9_LOG_CENTER = np.log10(np.sqrt(30.0 * 500.0))  # = 2.19
_CLOUD9_LOG_WIDTH = (np.log10(500.0) - np.log10(30.0)) / 2.0  # ~0.61

# Galactic dSph/UFD: sigma/m(100) < 2 cm^2/g (upper limit, 1-sided)
# Modeled as half-Gaussian with sigma = 0.3 dex (factor-of-2 tolerance).
_GAL_UPPER_LIMIT_LOG = np.log10(2.0)  # 0.301
_GAL_UPPER_SIGMA_DEX = 0.3

# Bullet Cluster: sigma/m(3000) < 0.5 cm^2/g (upper limit, 1-sided)
_BUL_UPPER_LIMIT_LOG = np.log10(0.5)  # -0.301
_BUL_UPPER_SIGMA_DEX = 0.3


def loglike_cloud9(sigma_m_c9: float) -> float:
    """Cloud-9 (RELHIC) log-likelihood: sigma/m(28) in [30, 500] cm^2/g."""
    if sigma_m_c9 <= 0:
        return -np.inf
    log_sm = np.log10(sigma_m_c9)
    z = (log_sm - _CLOUD9_LOG_CENTER) / _CLOUD9_LOG_WIDTH
    return -0.5 * z * z


def loglike_galaxy(sigma_m_gal: float) -> float:
    """Galactic dSph/UFD log-likelihood: sigma/m(100) < 2 cm^2/g (1-sided)."""
    if sigma_m_gal <= 0:
        return -np.inf
    log_sm = np.log10(sigma_m_gal)
    if log_sm <= _GAL_UPPER_LIMIT_LOG:
        return 0.0
    z = (log_sm - _GAL_UPPER_LIMIT_LOG) / _GAL_UPPER_SIGMA_DEX
    return -0.5 * z * z


def loglike_bullet(sigma_m_bul: float) -> float:
    """Bullet Cluster log-likelihood: sigma/m(3000) < 0.5 cm^2/g (1-sided)."""
    if sigma_m_bul <= 0:
        return -np.inf
    log_sm = np.log10(sigma_m_bul)
    if log_sm <= _BUL_UPPER_LIMIT_LOG:
        return 0.0
    z = (log_sm - _BUL_UPPER_LIMIT_LOG) / _BUL_UPPER_SIGMA_DEX
    return -0.5 * z * z


def loglike_resonant_3ch(theta) -> float:
    """Joint log-likelihood for resonant SIDM at the 3 characteristic velocities.

    theta is the 6D parameter vector in physical units (NOT log).
    """
    m_chi_GeV, E_R_eV, Gamma_R_eV, sigma_0_cm2_per_g, alpha_Y, m_phi_MeV = theta

    # Physical sanity bounds -- if violated, hard reject.
    if not (0.5 <= m_chi_GeV <= 1000.0):
        return -np.inf
    if not (1.0 <= E_R_eV <= 1000.0):
        return -np.inf
    if not (0.001 <= Gamma_R_eV <= 100.0):
        return -np.inf
    if not (1e-5 <= sigma_0_cm2_per_g <= 10.0):
        return -np.inf
    if not (1e-4 <= alpha_Y <= 1.0):
        return -np.inf
    if not (0.01 <= m_phi_MeV <= 1e4):
        return -np.inf

    # Compute sigma/m at each characteristic velocity.
    # NOTE: m_phi_MeV is a parameter but only affects sigma via Yukawa mediator
    # contribution; at first order in the Breit-Wigner + Sommerfeld picture,
    # the Sommerfeld enhancement encodes the mediator physics through alpha_Y.
    # We carry m_phi_MeV as a nuisance parameter (priors will keep it well-
    # defined) so the joint fit is 6D and properly comparable to T41 v0.6.
    r_c9 = sigma_m_resonant(28.0, m_chi_GeV, E_R_eV, Gamma_R_eV,
                             sigma_0_cm2_per_g, alpha_Y)
    r_gal = sigma_m_resonant(100.0, m_chi_GeV, E_R_eV, Gamma_R_eV,
                              sigma_0_cm2_per_g, alpha_Y)
    r_bul = sigma_m_resonant(3000.0, m_chi_GeV, E_R_eV, Gamma_R_eV,
                              sigma_0_cm2_per_g, alpha_Y)

    ll_c9 = loglike_cloud9(r_c9["sigma_m_total"])
    ll_gal = loglike_galaxy(r_gal["sigma_m_total"])
    ll_bul = loglike_bullet(r_bul["sigma_m_total"])

    total = ll_c9 + ll_gal + ll_bul
    if not np.isfinite(total):
        return -np.inf
    return total


# --------------------------------------------------------------------------
# Priors (log-uniform on all 6 parameters)
# --------------------------------------------------------------------------
LOG_M_CHI_RANGE = (np.log10(3.0), np.log10(1000.0))   # 3 GeV to 1 TeV
LOG_E_R_RANGE = (np.log10(10.0), np.log10(500.0))    # 10 eV to 500 eV
LOG_GAMMA_RANGE = (np.log10(0.01), np.log10(100.0))  # 0.01 eV to 100 eV
LOG_SIGMA_0_RANGE = (np.log10(1e-4), np.log10(1.0))  # 1e-4 to 1 cm^2/g
LOG_ALPHA_Y_RANGE = (np.log10(1e-4), np.log10(1.0))  # 1e-4 to 1
LOG_M_PHI_RANGE = (np.log10(0.1), np.log10(1000.0))  # 0.1 MeV to 1 GeV

LOG_RANGES = [
    LOG_M_CHI_RANGE,
    LOG_E_R_RANGE,
    LOG_GAMMA_RANGE,
    LOG_SIGMA_0_RANGE,
    LOG_ALPHA_Y_RANGE,
    LOG_M_PHI_RANGE,
]


def prior_transform_6(u):
    """Map unit cube u in [0,1]^6 to physical parameter vector (NOT log)."""
    theta = np.zeros(6)
    for i in range(6):
        lo, hi = LOG_RANGES[i]
        log_val = lo + u[i] * (hi - lo)
        theta[i] = 10.0 ** log_val
    return theta


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def run_dynesty(nlive: int = 500, dlogz: float = 0.05, output_dir: str = None):
    """Run the 6D resonant SIDM joint fit with dynesty nested sampling."""
    import dynesty

    if output_dir is None:
        if os.name == "nt":
            output_dir = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
        else:
            output_dir = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    sampler = dynesty.NestedSampler(
        loglike_resonant_3ch,
        prior_transform_6,
        ndim=6,
        nlive=nlive,
        bound="multi",
        sample="rwalk",
        walks=50,
    )
    t0 = time.time()
    sampler.run_nested(dlogz=dlogz, maxiter=50000, print_progress=True)
    wall = time.time() - t0

    res = sampler.results
    log_z = float(res.logz[-1])
    log_z_err = float(res.logzerr[-1])

    # Posterior samples in physical units
    samples = res.samples  # shape (N, 6)
    weights = np.exp(res.logwt - res.logz[-1])

    # Weighted medians in log space (so geometric mean for sigma_0, etc.)
    log_samples = np.log10(samples)
    log_medians = np.zeros(6)
    log_p16 = np.zeros(6)
    log_p84 = np.zeros(6)
    param_names = [
        "log_m_chi_GeV", "log_E_R_eV", "log_Gamma_R_eV",
        "log_sigma_0_cm2_per_g", "log_alpha_Y", "log_m_phi_MeV",
    ]
    for i in range(6):
        log_medians[i] = _weighted_quantile(log_samples[:, i], weights, 0.5)
        log_p16[i] = _weighted_quantile(log_samples[:, i], weights, 0.16)
        log_p84[i] = _weighted_quantile(log_samples[:, i], weights, 0.84)

    summary = {
        "log_Z": log_z,
        "log_Z_err": log_z_err,
        "wall_seconds": wall,
        "nlive": nlive,
        "dlogz_target": dlogz,
        "n_samples": int(samples.shape[0]),
        "posterior_medians": {
            param_names[i]: {
                "median_log10": float(log_medians[i]),
                "p16_log10": float(log_p16[i]),
                "p84_log10": float(log_p84[i]),
                "median": float(10.0 ** log_medians[i]),
                "p16": float(10.0 ** log_p16[i]),
                "p84": float(10.0 ** log_p84[i]),
            }
            for i in range(6)
        },
        "best_fit_point_from_T90_50": {
            "m_chi_GeV": 30.0,
            "E_R_eV": 65.0,
            "Gamma_R_eV": 0.1,
            "sigma_0_cm2_per_g": 0.01,
            "alpha_Y": 0.01,
            "m_phi_MeV": 1.0,  # arbitrary; nuisance
        },
    }
    # Evaluate T90.50 best-fit point under the joint likelihood
    bf = summary["best_fit_point_from_T90_50"]
    ll_bf = loglike_resonant_3ch([
        bf["m_chi_GeV"], bf["E_R_eV"], bf["Gamma_R_eV"],
        bf["sigma_0_cm2_per_g"], bf["alpha_Y"], bf["m_phi_MeV"],
    ])
    summary["best_fit_point_from_T90_50"]["loglike"] = float(ll_bf)

    # Compute sigma/m at the posterior median
    med = summary["posterior_medians"]
    med_phys = np.array([
        med["log_m_chi_GeV"]["median"],
        med["log_E_R_eV"]["median"],
        med["log_Gamma_R_eV"]["median"],
        med["log_sigma_0_cm2_per_g"]["median"],
        med["log_alpha_Y"]["median"],
        med["log_m_phi_MeV"]["median"],
    ])
    r_c9 = sigma_m_resonant(28.0, *med_phys[:5])
    r_gal = sigma_m_resonant(100.0, *med_phys[:5])
    r_bul = sigma_m_resonant(3000.0, *med_phys[:5])
    summary["posterior_median_predictions"] = {
        "sigma_m_Cloud9_cm2_per_g": float(r_c9["sigma_m_total"]),
        "sigma_m_Galaxy_cm2_per_g": float(r_gal["sigma_m_total"]),
        "sigma_m_Bullet_cm2_per_g": float(r_bul["sigma_m_total"]),
    }

    out_path = Path(output_dir) / "t90_v51_resonant_joint_posterior.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[T90.51] Wrote {out_path}")
    return summary


def _weighted_quantile(values, weights, q):
    """Weighted quantile (q in [0,1])."""
    idx = np.argsort(values)
    v = values[idx]
    w = weights[idx]
    cum = np.cumsum(w)
    cum = cum / cum[-1] if cum[-1] > 0 else cum
    return float(np.interp(q, cum, v))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--nlive", type=int, default=500)
    p.add_argument("--dlogz", type=float, default=0.05)
    p.add_argument("--smoke", action="store_true",
                   help="Smoke test: nlive=50, dlogz=0.5, very short")
    args = p.parse_args()

    if args.smoke:
        print("[T90.51 SMOKE] nlive=50, dlogz=0.5")
        s = run_dynesty(nlive=50, dlogz=0.5)
    else:
        s = run_dynesty(nlive=args.nlive, dlogz=args.dlogz)

    print("\n[T90.51] log Z =", s["log_Z"], "+/-", s["log_Z_err"])
    print("[T90.51] wall =", round(s["wall_seconds"], 1), "s")
    print("[T90.51] posterior median predictions:")
    p = s["posterior_median_predictions"]
    print(f"   sigma/m(Cloud-9)  = {p['sigma_m_Cloud9_cm2_per_g']:.2f} cm^2/g")
    print(f"   sigma/m(Galaxy)   = {p['sigma_m_Galaxy_cm2_per_g']:.2f} cm^2/g")
    print(f"   sigma/m(Bullet)   = {p['sigma_m_Bullet_cm2_per_g']:.3f} cm^2/g")
    print(f"[T90.51] T90.50 best-fit loglike = {s['best_fit_point_from_T90_50']['loglike']:.3f}")
