"""
Phase 31a Test H — Cluster vs dwarf core-size evolution

Per consider8.docx: The resonant model predicts extreme velocity dependence
(sigma/m(28)=29 vs sigma/m(1000)=0.0006). This should manifest as:
  - Large cores in dwarf galaxies (v ~ 30 km/s)
  - CDM-like cores in clusters (v ~ 1000 km/s)

Compare predicted core sizes to observations:
  - Dwarf galaxies (e.g., Fornax, Sculptor): r_c ~ 0.5-1 kpc
  - Clusters (e.g., A1689): r_c ~ CDM-like (small)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v50_resonant_sidm import sigma_m_resonant
from t95_v02_option2_core_size import (
    kaplinghat_core_radius,
    nfw_scale_density,
    M_200_REF,
    C_200_REF,
    R_200_KPC,
    G_NEWTON_KPC_KMS_MSUN,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def v0_for_halo(M_200_Msun, r_200_kpc):
    """Characteristic velocity v_0 = sqrt(G M_200 / r_200)."""
    return np.sqrt(G_NEWTON_KPC_KMS_MSUN * M_200_Msun / r_200_kpc)


def predict_core_size_at_v0(v_0_kms, sigma_m_at_v0, m_chi_GeV):
    """Predict core size for a halo with characteristic velocity v_0."""
    # Use MW-like halo parameters as reference
    rho_s = nfw_scale_density(M_200_REF, C_200_REF, R_200_KPC)
    r_s = R_200_KPC / C_200_REF
    return kaplinghat_core_radius(sigma_m_at_v0, m_chi_GeV, rho_s, r_s)


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
    print("TEST H — Cluster vs dwarf core-size evolution")
    print("=" * 70)
    print()
    print(f"Phase 29 posterior median: m_chi={m_chi:.2f} GeV")
    print()

    # Dwarf galaxies (M_200 ~ 10^9 M_sun, r_200 ~ 30 kpc, v_0 ~ 30 km/s)
    # Fornax-like: M_200 = 4e9 M_sun, r_200 = 50 kpc, v_0 ~ 30 km/s
    # Sculptor-like: M_200 = 1e9 M_sun, r_200 = 30 kpc, v_0 ~ 25 km/s

    # MW-like: M_200 = 1e12 M_sun, r_200 = 200 kpc, v_0 ~ 220 km/s
    # Cluster-like: M_200 = 1e15 M_sun, r_200 = 1500 kpc, v_0 ~ 1100 km/s

    halos = [
        # (name, M_200_Msun, r_200_kpc)
        ("Fornax-like dwarf", 4e9, 50),
        ("Sculptor-like UFD", 1e9, 30),
        ("Milky Way", 1e12, 200),
        ("A1689-like cluster", 1e15, 1500),
    ]

    print(f"{'Halo':25s}  {'v_0 (km/s)':>10}  {'sigma/m':>10}  {'r_c (kpc)':>10}")
    print("-" * 70)

    results = []
    for name, M_200, r_200 in halos:
        v_0 = v0_for_halo(M_200, r_200)
        r = sigma_m_resonant(v_0, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
        sm_v0 = r["sigma_m_total"]
        r_c = predict_core_size_at_v0(v_0, sm_v0, m_chi)
        print(f"{name:25s}  {v_0:10.1f}  {sm_v0:10.4f}  {r_c:10.4f}")
        results.append({
            "name": name, "M_200_Msun": M_200, "r_200_kpc": r_200,
            "v_0_kms": float(v_0), "sigma_m_v0": float(sm_v0),
            "core_radius_kpc": float(r_c),
        })
    print()

    # Compare to observations
    print("Comparison to observations:")
    print("  Fornax dwarf core: r_c ~ 0.5-1 kpc (observed)")
    print("  Sculptor UFD core: r_c ~ 0.3-0.5 kpc (observed)")
    print("  MW core: r_c ~ 5-20 kpc (controversial; CDM cuspy ~ 0)")
    print("  Cluster cores: CDM-like (cuspy), r_c < 10 kpc")
    print()

    # Verdicts
    for r in results:
        if "dwarf" in r["name"] or "UFD" in r["name"]:
            obs = "0.3-1 kpc"
            if r["core_radius_kpc"] > 5:
                verdict = "OVERSHOOT_DWARF_CORES"
            elif r["core_radius_kpc"] > 1:
                verdict = "MILD_OVERSHOOT"
            else:
                verdict = "CONSISTENT"
        elif "MW" in r["name"]:
            verdict = "MW_TEST"  # MW is controversial
        else:
            # Cluster: should be CDM-like (small cores)
            if r["core_radius_kpc"] > 10:
                verdict = "CLUSTER_OVERSHOOT"
            else:
                verdict = "CONSISTENT"
        r["verdict"] = verdict

    # Summary
    n_overshoot = sum(1 for r in results if "OVERSHOOT" in r["verdict"])
    n_consistent = sum(1 for r in results if r["verdict"] == "CONSISTENT")

    print("Verdicts:")
    for r in results:
        sym = "✓" if r["verdict"] == "CONSISTENT" else ("~" if "MILD" in r["verdict"] else "✗")
        print(f"  {sym} {r['name']:25s}: {r['verdict']} (r_c={r['core_radius_kpc']:.3f} kpc)")
    print()

    if n_overshoot >= 2:
        agg = "OVERSHOOTS_DWARF_CORES"
        msg = "Resonant model predicts LARGER dwarf cores than observed"
    elif n_overshoot == 1:
        agg = "MILD_OVERSHOOT"
        msg = "Resonant model mildly overshoots one halo scale"
    else:
        agg = "CONSISTENT_WITH_OBS"
        msg = "Resonant model core size predictions consistent"

    print(f"AGGREGATE: {agg}")
    print(f"  {msg}")

    out = {
        "test": "Phase31a_H_core_size",
        "median_params": {
            "m_chi_GeV": m_chi, "E_R_eV": E_R, "Gamma_R_eV": Gamma_R,
            "sigma_0": sigma_0, "alpha_Y": alpha_Y,
        },
        "halo_predictions": results,
        "n_overshoot": n_overshoot,
        "n_consistent": n_consistent,
        "aggregate": agg,
    }

    out_path = RESULTS_DIR / "phase31a_H_core_size.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())