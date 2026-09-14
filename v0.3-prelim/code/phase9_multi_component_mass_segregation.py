"""
Phase 9 — Multi-Component SIDM Mass Segregation: σ/m_observed Spread Test

Tests whether Yang, Fan, Tsai 2025 mass segregation can explain the
σ/m_observed spread seen across SIDM channels at v0.3-prelim:

  Cloud-9 / RELHIC (v=28 km/s, low-mass halos, YOUNG):  σ/m ~ 50 cm²/g
  Galactic cores (v=100 km/s, MW-mass halos, OLD):     σ/m ~ 1 cm²/g
  Bullet Cluster (v=3000 km/s, OLD cluster):            σ/m ~ 0.5 cm²/g
  LZ-like (low-density, v~ 230 km/s, YOUNG):           σ/m ~ 0.065 cm²/g

The hypothesis: in a multi-component SIDM halo (m_H > m_L), the heavy
species sinks to the center over time (gravothermal mass segregation).
OLD halos have heavy-rich centers → high σ/m(observed at center).
YOUNG halos have mixed species → low σ/m(observed at center).

For different halo types (LSB, MW, Cluster) at different evolutionary
stages, the OBSERVED σ/m at the half-light radius varies.

Phase 9 runs gravothermal_two_component for representative halo types
and reports σ/m_observed at the half-light radius.

Halo parameter choices (Yang+ 2025 framework):
  - Dwarf galaxy / LSB:  M_halo ~ 1e9 M_sun, c ~ 15, age ~ 5 Gyr (YOUNG)
  - MW-like:             M_halo ~ 1e12 M_sun, c ~ 12, age ~ 10 Gyr (OLD)
  - Cluster:             M_halo ~ 1e14 M_sun, c ~ 6, age ~ 10 Gyr (OLD)

Parameters (varied):
  - m_H/m_L ratio: 3 (Yang+ 2025 default)
  - g_H = 0.7 (SIDM-required from v0.3-prelim)
  - g_L = 0.7 (same coupling)
  - m_phi_MeV = 100 (v0.3-prelim SIDM MAP value)
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

from t90_v47_gravothermal_fluid import (
    gravothermal_two_component, effective_sigma_m_at_radius,
    nfw_density, nfw_mass, nfw_concentration_to_rho_s,
)
from t40_yukawa_sigma_m import sigma_m_cm2_per_g

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Halo types: (M_halo, c, age_Gyr, name, v_at_rhalf_kms)
HALO_TYPES = [
    {
        "name": "Dwarf/LSB (YOUNG)",
        "M_halo_Msun": 1e9,
        "c": 15.0,
        "age_Gyr": 5.0,
        "v_disp_kms": 30.0,        # Cloud-9 / dSph velocity dispersion
        "observed_sigma_m": 50.0,  # Cloud-9 target
    },
    {
        "name": "MW-like (OLD)",
        "M_halo_Msun": 1e12,
        "c": 12.0,
        "age_Gyr": 10.0,
        "v_disp_kms": 100.0,       # galactic core velocity
        "observed_sigma_m": 1.0,   # T39 MAP value
    },
    {
        "name": "Cluster (OLD)",
        "M_halo_Msun": 1e14,
        "c": 6.0,
        "age_Gyr": 10.0,
        "v_disp_kms": 3000.0,      # Bullet Cluster velocity
        "observed_sigma_m": 0.5,   # Cha+ 2025 limit
    },
]

# v0.3-prelim parameters
M_CHI_H_GEV = 45.0
M_CHI_L_GEV = 15.0   # m_H/m_L = 3
G_CHI_H = 0.7
G_CHI_L = 0.7
M_PHI_MEV = 100.0    # v0.3-prelim SIDM MAP value


def run_halo(halo: dict, age_evolution: bool = True) -> dict:
    """Run gravothermal_two_component for one halo type.

    Returns dict with sigma/m at r_half for both initial and evolved state.
    """
    M_halo = halo["M_halo_Msun"]
    c = halo["c"]
    age = halo["age_Gyr"]

    print(f"\n--- {halo['name']}: M={M_halo:.0e} M_sun, c={c}, age={age} Gyr ---")
    print(f"  v_disp = {halo['v_disp_kms']} km/s, observed σ/m = {halo['observed_sigma_m']} cm²/g")

    # Run gravothermal evolution
    res = gravothermal_two_component(
        M_halo_Msun=M_halo,
        c=c,
        m_chi_H_GeV=M_CHI_H_GEV,
        m_chi_L_GeV=M_CHI_L_GEV,
        g_chi_H=G_CHI_H,
        g_chi_L=G_CHI_L,
        m_phi_MeV=M_PHI_MEV,
        t_final_Gyr=age + 1.0,  # include present day
        n_radial_bins=80,
        n_time_steps=100,
    )

    r_kpc = res["r_kpc"]
    rho_s, r_s, r_vir = nfw_concentration_to_rho_s(M_halo, c)
    # Half-light radius: typically ~0.015-0.05 r_vir for dwarfs, ~0.02-0.05 for MW
    # Use r_half = 0.02 * r_vir as a representative scale
    r_half_kpc = 0.02 * r_vir
    idx_half = np.argmin(np.abs(r_kpc - r_half_kpc))

    # Find time index for the requested age
    t_idx_age = np.argmin(np.abs(res["time_Gyr"] - age))

    # Compute σ/m_observed at r_half for t=0 (initial) and t=age (evolved)
    sigma_m_initial = effective_sigma_m_at_radius(res, idx_half, 0)
    sigma_m_evolved = effective_sigma_m_at_radius(res, idx_half, t_idx_age)

    # Also compute σ/m at center (idx=5) for evolved
    sigma_m_center_evolved = effective_sigma_m_at_radius(res, 5, t_idx_age)

    print(f"  r_vir = {r_vir:.1f} kpc, r_half = {r_half_kpc:.1f} kpc")
    print(f"  σ/m(v={halo['v_disp_kms']}, no seg, r_half): {sigma_m_initial:.3f} cm²/g")
    print(f"  σ/m(v={halo['v_disp_kms']}, age={age} Gyr, r_half): {sigma_m_evolved:.3f} cm²/g")
    print(f"  σ/m(center, age={age} Gyr): {sigma_m_center_evolved:.3f} cm²/g")
    print(f"  observed σ/m from data: {halo['observed_sigma_m']} cm²/g")
    if sigma_m_evolved > 0:
        ratio = halo['observed_sigma_m'] / sigma_m_evolved
        print(f"  ratio observed/model: {ratio:.2f}")

    return {
        "halo": halo["name"],
        "M_halo_Msun": M_halo,
        "c": c,
        "age_Gyr": age,
        "v_disp_kms": halo["v_disp_kms"],
        "r_vir_kpc": r_vir,
        "r_half_kpc": r_half_kpc,
        "observed_sigma_m": halo["observed_sigma_m"],
        "sigma_m_no_segregation": sigma_m_initial,
        "sigma_m_evolved_at_r_half": sigma_m_evolved,
        "sigma_m_evolved_at_center": sigma_m_center_evolved,
        "ratio_observed_to_evolved": halo['observed_sigma_m'] / sigma_m_evolved if sigma_m_evolved > 0 else None,
        "t_seg_Gyr": float(res.get("t_seg", 0.0)),
        "t_coll_H_Gyr": float(res.get("t_coll_H", 0.0)),
    }


def main():
    print("=" * 80)
    print("Phase 9 — Multi-Component SIDM Mass Segregation Test")
    print("=" * 80)
    print(f"Parameters: m_H={M_CHI_H_GEV} GeV, m_L={M_CHI_L_GEV} GeV (ratio=3)")
    print(f"           g_H = g_L = {G_CHI_H}")
    print(f"           m_phi = {M_PHI_MEV} MeV (v0.3-prelim SIDM MAP)")
    print()

    t0 = time.time()
    results = []
    for halo in HALO_TYPES:
        try:
            r = run_halo(halo)
            results.append(r)
        except Exception as e:
            print(f"  ERROR for {halo['name']}: {e}")
            results.append({"halo": halo["name"], "error": str(e)})

    wall = time.time() - t0

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Halo':<25} {'v [km/s]':<10} {'σ/m obs':<12} {'σ/m evolved':<14} {'ratio':<10}")
    for r in results:
        if "error" in r:
            print(f"{r['halo']:<25} {'—':<10} {'—':<12} ERROR: {r['error']}")
        else:
            print(f"{r['halo']:<25} {r['v_disp_kms']:<10.0f} {r['observed_sigma_m']:<12.3f} "
                  f"{r['sigma_m_evolved_at_r_half']:<14.4f} "
                  f"{r['ratio_observed_to_evolved']:<10.2f}")

    print()
    print("Interpretation:")
    print("  - If σ/m_evolved matches σ/m_observed across all halo types → mass segregation works")
    print("  - If σ/m_evolved is constant across halos → no segregation, single-component model needed")
    print("  - The σ/m_observed spread (50 vs 1 vs 0.5) is the target to reproduce")

    out = {
        "test": "Phase9_multi_component_mass_segregation",
        "direction": "Yang, Fan, Tsai 2025 mass segregation test on v0.3-prelim SIDM channels",
        "parameters": {
            "m_H_GeV": M_CHI_H_GEV,
            "m_L_GeV": M_CHI_L_GEV,
            "mass_ratio": 3,
            "g_H": G_CHI_H,
            "g_L": G_CHI_L,
            "m_phi_MeV": M_PHI_MEV,
        },
        "halo_results": results,
        "wall_seconds": wall,
        "conclusion": "see interpretation above",
    }

    out_path = RESULTS_DIR / "phase9_multi_component_mass_segregation.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
