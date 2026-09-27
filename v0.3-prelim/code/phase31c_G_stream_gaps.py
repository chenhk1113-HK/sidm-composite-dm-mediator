"""
Phase 31c — Stellar stream gap predictions

Per consider8.docx Test G: Do predicted subhalo encounters match the
observed gap statistics in stellar streams like Pal 5 and GD-1?

Method:
- Subhalo encounter rate is proportional to subhalo mass function
- SIDM suppresses substructure below a threshold mass set by sigma/m
- Map sigma_m at stream velocity (v ~ 200-400 km/s) to subhalo suppression
- Compare predicted vs observed gap densities

For Phase 29 median: sigma/m(200) = 0.013, sigma/m(300) = 0.005
This is VERY LOW — predicts minimal subhalo disruption
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v50_resonant_sidm import sigma_m_resonant

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def subhalo_suppression_factor(sigma_m_cm2_per_g, m_chi_GeV):
    """Estimate suppression of subhalo mass function from SIDM.

    Following Benson+ 2024 / He + 2024 simplified model:
    - Subhalos below cutoff mass M_cut are evaporated
    - M_cut ~ sigma_m × rho_s × r_s^2 / m_chi
    - Suppression factor = exp(-(M_cut / M_subhalo)^alpha)

    For sigma/m = 0.01 cm^2/g (Phase 29 at v=200):
      In dwarf host: M_cut ~ 10^6 M_sun (significant)
      In MW host: M_cut ~ 10^7 M_sun
    So subhalos <10^7 M_sun are partially suppressed.

    This is the OPPOSITE of CDM (which has full substructure down to Earth-mass).
    """
    # Rough scaling: M_cut ~ 10^7 M_sun for sigma/m ~ 0.01, m_chi ~ 10 GeV
    # Following Kaplinghat+ 2020 / He+ 2024
    M_cut_base = 1e7  # M_sun
    # M_cut ~ sigma/m^1.5 × (1/m_chi)^0.5 (rough scaling)
    M_cut = M_cut_base * (sigma_m_cm2_per_g / 0.01) ** 1.5 * (10.0 / m_chi_GeV) ** 0.5
    return M_cut


def stream_gap_density(sigma_m_cm2_per_g, m_chi_GeV, stream_velocity_kms=250):
    """Predict gap density per unit length along a stellar stream.

    Following Erkal+ 2016 + Carlberg+ 2012:
    - Gap formation rate ~ ρ_subhalo × σ_encounter × v_rel
    - ρ_subhalo suppressed if M_subhalo < M_cut(sigma_m)

    Returns: expected number of gaps per 10 kpc
    """
    M_cut = subhalo_suppression_factor(sigma_m_cm2_per_g, m_chi_GeV)

    # Reference: CDM predicts ~0.5 gaps per 10 kpc in Pal 5 (Erkal+ 2017)
    # SIDM with sigma/m = 0.01 cm^2/g suppresses by factor of ~10 (subhalos <10^7 M_sun gone)
    # So expected: ~0.05 gaps per 10 kpc

    if M_cut > 1e8:
        suppression = 0.1  # 90% reduction
    elif M_cut > 1e7:
        suppression = 0.05  # 95% reduction
    elif M_cut > 1e6:
        suppression = 0.02  # 98% reduction
    else:
        suppression = 0.5  # 50% reduction

    cdm_gap_density = 0.5  # gaps per 10 kpc in CDM (Carlberg+ 2012)
    predicted_gap_density = cdm_gap_density * suppression

    return predicted_gap_density, M_cut, suppression


def main():
    phase29 = json.load(open(RESULTS_DIR / "phase29_full_resonant_joint_fit.json"))
    med = phase29["posterior_medians"]
    m_chi = med["m_chi_GeV"]["p50"]
    E_R = med["E_R_eV"]["p50"]
    Gamma_R = med["Gamma_R_eV"]["p50"]
    sigma_0 = med["sigma_0"]["p50"]
    alpha_Y = med["alpha_Y"]["p50"]

    print("=" * 70)
    print("PHASE 31c — Stellar stream gap predictions")
    print("=" * 70)
    print()
    print(f"Phase 29 median: m_chi = {m_chi:.2f} GeV, E_R = {E_R:.2f} eV, Gamma_R = {Gamma_R:.3f} eV")
    print()

    # Compute sigma/m at stream velocities (200-400 km/s)
    stream_velocities = [150, 200, 250, 300, 400]
    print(f"{'v_stream (km/s)':>15}  {'sigma/m (cm^2/g)':>18}  {'M_cut (M_sun)':>15}  {'Gap density (/10kpc)':>22}")
    print("-" * 80)

    gap_predictions = []
    for v in stream_velocities:
        r = sigma_m_resonant(v, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
        sm = r["sigma_m_total"]
        gap_dens, M_cut, suppression = stream_gap_density(sm, m_chi, v)
        print(f"{v:15d}  {sm:18.6f}  {M_cut:15.2e}  {gap_dens:22.4f}")
        gap_predictions.append({
            "v_stream_kms": v,
            "sigma_m_cm2_per_g": sm,
            "M_cut_Msun": M_cut,
            "gap_density_per_10kpc": gap_dens,
            "suppression_factor": suppression,
        })
    print()

    # Compare to observations
    print("Observational references (Carlberg+ 2012, Erkal+ 2017):")
    print("  Pal 5: ~ 0.2-0.5 gaps per 10 kpc")
    print("  GD-1:  ~ 5-15 gaps total in ~10 kpc stream length")
    print()

    avg_gap_density = np.mean([g["gap_density_per_10kpc"] for g in gap_predictions])
    print(f"Phase 29 predicted average gap density: {avg_gap_density:.4f} per 10 kpc")
    print()

    # Verdict
    if avg_gap_density < 0.05:
        verdict = "TOO_FEW_GAPS"
        msg = "Resonant SIDM predicts 10-100x FEWER gaps than observed"
    elif avg_gap_density < 0.15:
        verdict = "FEWER_GAPS_THAN_OBSERVED"
        msg = "Resonant SIDM predicts somewhat fewer gaps than observed"
    elif avg_gap_density > 1.5:
        verdict = "TOO_MANY_GAPS"
        msg = "Resonant SIDM predicts MORE gaps than observed"
    else:
        verdict = "CONSISTENT_WITH_STREAMS"
        msg = "Resonant SIDM gap predictions consistent with Pal 5/GD-1"

    print(f"VERDICT: {verdict}")
    print(f"  {msg}")

    out = {
        "test": "Phase31c_G_stream_gaps",
        "median_params": {
            "m_chi_GeV": m_chi, "E_R_eV": E_R, "Gamma_R_eV": Gamma_R,
            "sigma_0": sigma_0, "alpha_Y": alpha_Y,
        },
        "gap_predictions": gap_predictions,
        "avg_gap_density": float(avg_gap_density),
        "observation_references": {
            "Pal_5_gaps_per_10kpc": [0.2, 0.5],
            "GD-1_total_gaps": [5, 15],
        },
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase31c_G_stream_gaps.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())