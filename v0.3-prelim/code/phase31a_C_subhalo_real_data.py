"""
Phase 31a Test C — Subhalo real data (Euclid Q1 strong-lensing clusters)

Per consider8.docx: Test whether the resonant SIDM posterior median
predicts a number of strong-lensing clusters consistent with the real
14 grade-A clusters observed in Euclid Q1 (arXiv:2503.15330, A&A 711 A33,
Bergamini et al. 2025/2026).

Method:
- Use existing euclid_q1_subhalo_real_data.py Poisson likelihood
- Compute sigma/m at v ~ 500-1000 km/s for Phase 29 resonant median
- Compare predicted N_lenses vs observed 14 grade-A
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v50_resonant_sidm import sigma_m_resonant
from euclid_q1_subhalo_real_data import (
    loglike_euclid_q1_count,
    EUCLID_Q1_GRADE_A_CLUSTERS,
    EUCLID_Q1_TOTAL_AREA_DEG2,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def main():
    # Load Phase 29 results
    phase29_path = RESULTS_DIR / "phase29_full_resonant_joint_fit.json"
    with open(phase29_path) as f:
        phase29 = json.load(f)

    med = phase29["posterior_medians"]
    m_chi = med["m_chi_GeV"]["p50"]
    E_R = med["E_R_eV"]["p50"]
    Gamma_R = med["Gamma_R_eV"]["p50"]
    sigma_0 = med["sigma_0"]["p50"]
    alpha_Y = med["alpha_Y"]["p50"]

    print("=" * 70)
    print("TEST C — Subhalo real data (Euclid Q1)")
    print("=" * 70)
    print()
    print(f"Phase 29 posterior median: m_chi={m_chi:.2f} GeV, E_R={E_R:.2f} eV,")
    print(f"                           Gamma_R={Gamma_R:.3f} eV, sigma_0={sigma_0:.4f}")
    print()

    # Compute sigma/m at cluster velocities (v ~ 500-1000 km/s)
    r_500 = sigma_m_resonant(500, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    r_1000 = sigma_m_resonant(1000, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    print(f"sigma/m at cluster velocities:")
    print(f"  sigma/m(500)  = {r_500['sigma_m_total']:.6f} cm^2/g")
    print(f"  sigma/m(1000) = {r_1000['sigma_m_total']:.6f} cm^2/g")
    print()

    # For the count likelihood, we need sigma_m_0 at V_REF=100 km/s and velocity slope a
    # Effective power-law approximation: sigma/m(v) = sigma_m_0 * (v/100)^(-a)
    # Compute at v=100 and v=500 to extract a
    r_100 = sigma_m_resonant(100, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    sm_100 = r_100["sigma_m_total"]
    sm_500 = r_500["sigma_m_total"]
    sm_1000 = r_1000["sigma_m_total"]

    if sm_100 > 0 and sm_500 > 0:
        # a = (log10(sm_100) - log10(sm_500)) / (log10(500/100))
        a_eff = (np.log10(sm_100) - np.log10(sm_500)) / np.log10(500 / 100)
    else:
        a_eff = 1.5  # default

    print(f"Effective power-law fit (v=100 to v=500):")
    print(f"  sigma/m_0 = {sm_100:.4f}, a = {a_eff:.3f}")
    print()

    # Compute Poisson log-likelihood for the cluster count
    print(f"Euclid Q1: {EUCLID_Q1_GRADE_A_CLUSTERS} grade-A clusters in {EUCLID_Q1_TOTAL_AREA_DEG2} deg^2")
    print()

    ll_resonant = loglike_euclid_q1_count(sm_100, a_eff)
    print(f"Resonant SIDM log-likelihood: {ll_resonant:.3f}")

    # For comparison: pure CDM (sigma_m_0 = 0) gives no suppression
    ll_cdm = loglike_euclid_q1_count(0.0, 1.5)
    print(f"CDM (sigma_m=0) log-likelihood: {ll_cdm:.3f}")
    print()

    delta_ll = ll_resonant - ll_cdm
    print(f"Delta log L (resonant vs CDM): {delta_ll:.3f}")
    print()

    # Verdict
    if delta_ll > -5:
        verdict = "CONSISTENT_WITH_DATA"
        msg = "Resonant SIDM is consistent with Euclid Q1 strong-lensing data"
    elif delta_ll > -20:
        verdict = "MILD_TENSION"
        msg = "Resonant SIDM shows mild tension with Euclid Q1"
    else:
        verdict = "EXCLUDED_BY_DATA"
        msg = "Resonant SIDM is excluded by Euclid Q1 strong-lensing data"

    print(f"VERDICT: {verdict}")
    print(f"  {msg}")

    out = {
        "test": "Phase31a_C_subhalo_real_data",
        "median_params": {
            "m_chi_GeV": m_chi, "E_R_eV": E_R, "Gamma_R_eV": Gamma_R,
            "sigma_0": sigma_0, "alpha_Y": alpha_Y,
        },
        "sigma_m_at_cluster_velocities": {
            "sigma_m_100": sm_100,
            "sigma_m_500": sm_500,
            "sigma_m_1000": sm_1000,
        },
        "effective_power_law": {
            "sigma_m_0": sm_100,
            "a": float(a_eff),
        },
        "log_likelihoods": {
            "resonant": float(ll_resonant),
            "cdm_baseline": float(ll_cdm),
        },
        "delta_log_likelihood": float(delta_ll),
        "euclid_q1_observation": {
            "n_grade_A_clusters": EUCLID_Q1_GRADE_A_CLUSTERS,
            "area_deg2": EUCLID_Q1_TOTAL_AREA_DEG2,
        },
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase31a_C_subhalo_real_data.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())