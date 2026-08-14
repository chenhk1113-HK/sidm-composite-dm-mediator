#!/usr/bin/env python
"""
T5 FULL — SIDM mock-data validation at scale.

The classical SIDM prediction is that a cored profile (Burkert-like) has a
core radius that depends on the velocity scale (v_max) and the cross-section:

    r_core = (sigma/m)^0.5 * (4 pi G rho_s)^{-0.25} * v_max^{0.5}
            (approximate, Robertson+ 2021 Eq. 4)

For a galactic-scale test, fix sigma/m and generate 175 mock rotation
curves from the SPARC baryonic templates, with noise that matches the
real data. Then fit both NFW (cuspy, 2-param) and Burkert (cored, 2-param)
and check whether the Burkert fit recovers the injected sigma/m via
the r_core -> sigma/m conversion.

If recovery works: the pipeline is sharp enough to detect SIDM at
galactic scales.
If recovery fails: the SIDM-baryon degeneracy is so strong that even
known-injected SIDM looks like NFW.

Usage:
    python t5_full_mock_validation.py
"""
from __future__ import annotations
import sys
import time
import json
from pathlib import Path

import numpy as np
import dynesty

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sparc_loader import load_all_sparc
from halo_profiles import V_NFW, V_Burkert, chi2_sparc

DATA_DIR = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.1-prelim/data")
RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.1-prelim/data/results")

NFW_LOG_RHO_S_RANGE = (2.0, 10.0)
NFW_LOG_R_S_RANGE   = (-1.0, 2.5)
BURKERT_LOG_RHO_C_RANGE = (2.0, 10.0)
BURKERT_LOG_R_C_RANGE   = (-1.0, 2.5)

NLIVE = 200
DLOGZ = 0.10

# Robertson+ 2021 Eq. 4 approximation (galactic scale)
#   r_core [kpc] ≈ 1.05 * (sigma/m)^{1/2} * (v_max/100 km/s)^{1/2} * (rho_s/10^7)^{-1/4}
# At our scales (v_max ~ 100 km/s, rho_s ~ 10^7), we can use the simpler form:
#   r_core = 1 kpc * sqrt(sigma/m / 1 cm^2/g)
# This is the practical "sigma/m ~ 1 cm^2/g gives ~ 1 kpc core" rule of thumb.
def sigma_over_m_from_core(r_core_kpc: float) -> float:
    """Inverse of r_core = sqrt(sigma/m / 1 cm^2/g) * 1 kpc."""
    return r_core_kpc**2  # sigma/m in cm^2/g, r_core in kpc

def r_core_from_sigma_over_m(sigma_over_m: float) -> float:
    return np.sqrt(sigma_over_m)


def gen_mock_galaxy(ga, true_sigma_over_m: float, noise_sigma: float, seed: int):
    """Generate a mock rotation curve.

    If sigma/m = 0: pure NFW (cuspy) with rho_s, r_s from a typical SPARC galaxy.
    If sigma/m > 0: SIDM (Burkert) with rho_c, r_core set by the Robertson+ rule of thumb.
    """
    rng = np.random.default_rng(seed)
    if true_sigma_over_m <= 0:
        # CDM: pure NFW with typical parameters
        rho_s = 1e7
        r_s = 10.0  # 10 kpc, typical large-galaxy scale radius
        halo_V2 = V_NFW(ga.Rad, rho_s, r_s)
        model = "CDM-NFW"
        r_core_true = 0.0
    else:
        # SIDM: Burkert
        r_core = r_core_from_sigma_over_m(true_sigma_over_m)
        rho_c = 10**7.5
        halo_V2 = V_Burkert(ga.Rad, rho_c, r_core)
        model = f"SIDM-Burkert(sigma_m={true_sigma_over_m})"
        r_core_true = r_core
    V_total = np.sqrt(ga.Vbar_sq + halo_V2)
    V_sim = V_total + rng.normal(0, noise_sigma, size=len(ga.Rad))
    from sparc_loader import SPARCGalaxy
    g_sim = SPARCGalaxy(
        name=f"mock_{ga.name}",
        rad=ga.Rad.copy(),
        vobs=V_sim,
        errv=np.full_like(ga.Vobs, noise_sigma),
        vgas=ga.Vgas.copy(),
        vdisk=ga.Vdisk.copy(),
        vbul=ga.Vbul.copy(),
        sbdisk=ga.SBdisk.copy(),
        sbbul=ga.SBbul.copy(),
    )
    return g_sim, r_core_true, model


def fit_one_mock(g_sim, profile: str):
    halo_fn = V_NFW if profile == "NFW" else V_Burkert
    range1 = NFW_LOG_RHO_S_RANGE if profile == "NFW" else BURKERT_LOG_RHO_C_RANGE
    range2 = NFW_LOG_R_S_RANGE if profile == "NFW" else BURKERT_LOG_R_C_RANGE

    def loglike(theta):
        if not (range1[0] <= theta[0] <= range1[1]):
            return -np.inf
        if not (range2[0] <= theta[1] <= range2[1]):
            return -np.inf
        rho, r = 10**theta[0], 10**theta[1]
        V2 = halo_fn(g_sim.Rad, rho, r)
        V_total = np.sqrt(g_sim.Vbar_sq + V2)
        return -0.5 * float(np.sum(((g_sim.Vobs - V_total) / g_sim.errV)**2))

    def pt(u):
        return np.array([range1[0] + u[0] * (range1[1] - range1[0]),
                        range2[0] + u[1] * (range2[1] - range2[0])])

    sampler = dynesty.NestedSampler(loglikelihood=loglike, prior_transform=pt,
                                    ndim=2, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0)
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    theta_map = samples[imap]
    # Posterior median for r_core (Burkert) or r_s (NFW)
    post_med = np.median(samples, axis=0)
    return {
        "log_Z": float(res.logz[-1]),
        "log_Z_err": float(res.logzerr[-1]),
        "theta_MAP": theta_map.tolist(),
        "post_med_r": float(10**post_med[1]),  # in kpc
        "n_samples": int(samples.shape[0]),
    }


def main():
    galaxies = load_all_sparc(DATA_DIR)
    print(f"[T5 full] loaded {len(galaxies)} galaxies")

    # Test at three different sigma/m values to test recovery at varying strength
    SIGMA_OVER_M_VALUES = [0.0, 0.5, 2.0]  # cm^2/g (0 = CDM baseline)
    NOISE_SIGMA = 5.0  # km/s, realistic for outer points
    SEED = 20260810

    summary = {
        "n_galaxies": len(galaxies),
        "sigma_over_m_values": SIGMA_OVER_M_VALUES,
        "noise_sigma_kms": NOISE_SIGMA,
        "seed": SEED,
        "results_per_sigma": {},
    }

    for sigma_m in SIGMA_OVER_M_VALUES:
        print(f"\n=== sigma/m = {sigma_m} cm^2/g (r_core ~ {r_core_from_sigma_over_m(sigma_m):.2f} kpc) ===")
        per_gal_results = []
        for i, ga in enumerate(galaxies):
            g_sim, r_core_true, model = gen_mock_galaxy(ga, sigma_m, NOISE_SIGMA, SEED + i)
            r_nfw = fit_one_mock(g_sim, "NFW")
            r_bur = fit_one_mock(g_sim, "Burkert")
            # Recovered r_core from Burkert fit
            r_core_recovered = r_bur["post_med_r"]
            sigma_m_recovered = sigma_over_m_from_core(r_core_recovered)
            per_gal_results.append({
                "galaxy": ga.name,
                "true_sigma_m": sigma_m,
                "true_r_core": r_core_true,
                "NFW_log_Z": r_nfw["log_Z"],
                "Burkert_log_Z": r_bur["log_Z"],
                "delta_log_Z_B_minus_N": r_bur["log_Z"] - r_nfw["log_Z"],
                "recovered_r_core_kpc": r_core_recovered,
                "recovered_sigma_m_cm2_per_g": sigma_m_recovered,
            })
            if i % 20 == 0:
                print(f"  [{sigma_m}] {i}/{len(galaxies)}  gal={ga.name}  "
                      f"Δlog Z = {r_bur['log_Z'] - r_nfw['log_Z']:.2f}  "
                      f"recovered r_c = {r_core_recovered:.2f} (truth {r_core_true:.2f})  "
                      f"sigma/m recovered = {sigma_m_recovered:.2f}")
        # Aggregate
        deltas = np.array([r["delta_log_Z_B_minus_N"] for r in per_gal_results])
        sigmas_recovered = np.array([r["recovered_sigma_m_cm2_per_g"] for r in per_gal_results])
        summary["results_per_sigma"][f"sigma_m={sigma_m}"] = {
            "true_sigma_m": sigma_m,
            "true_r_core_kpc": r_core_from_sigma_over_m(sigma_m),
            "n_galaxies": len(per_gal_results),
            "median_delta_log_Z_B_minus_N": float(np.median(deltas)),
            "fraction_Burkert_preferred": float(np.mean(deltas > 0)),
            "median_recovered_sigma_m": float(np.median(sigmas_recovered)),
            "fraction_recovered_in_factor_3": float(np.mean(
                (sigmas_recovered > sigma_m / 3) & (sigmas_recovered < sigma_m * 3)
            )) if sigma_m > 0 else None,
        }

    out_path = RESULTS_DIR / "t5_full_mock_validation.json"
    out_path.write_text(json.dumps(summary, indent=2))

    print("\n=== T5 FULL MOCK VALIDATION SUMMARY ===")
    for sigma_key, res in summary["results_per_sigma"].items():
        print(f"  {sigma_key}: median Δlog Z = {res['median_delta_log_Z_B_minus_N']:.2f}, "
              f"Burkert wins {100*res['fraction_Burkert_preferred']:.0f}%, "
              f"recovered sigma/m = {res['median_recovered_sigma_m']:.2f} (true {res['true_sigma_m']})")
    print(f"\n  output -> {out_path}")


if __name__ == "__main__":
    main()