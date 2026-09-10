#!/usr/bin/env python
"""
T90.48 — Parameter scan to find Cloud-9 compatible multi-component SIDM.

Per the user request: explore the (m_phi, g_chi, M_halo, m_chi_H, m_chi_L)
parameter space to find regions where the gravothermal fluid model
produces sigma/m_observable > 30 cm^2/g at v=28 km/s (Cloud-9 requirement).

Strategy:
1. Scan over m_phi (mediator mass): 5-100 MeV
2. Scan over g_chi (coupling): 0.3-1.5
3. Scan over M_halo (halo mass): 1e8 - 1e10 M_sun
4. Scan over m_chi_H (heavy species mass): 10-100 GeV
5. Scan over mass ratio m_H/m_L: 2-5

For each point, run the gravothermal fluid simulation and compute:
- sigma/m_observable at v=28 km/s (Cloud-9 channel)
- sigma/m_observable at v=100 km/s (Galactic)
- sigma/m_observable at v=3000 km/s (Bullet)

Find points where all three constraints are satisfied.

Output:
- JSON file with all parameter combinations
- Print Cloud-9-compatible regions to stdout
- Plot-ready data (optional)
"""
from __future__ import annotations

import json
import numpy as np
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v47_gravothermal_fluid import (
    gravothermal_two_component,
    effective_sigma_m_at_radius,
    _trapz,
)
from t90_v46_multi_component_sidm import effective_sigma_m_at_v

# Cloud-9, Galactic, Bullet targets
SIGMA_M_CLOUD9_TARGET = 50.0  # cm^2/g, range 30-500
SIGMA_M_GALAXY_MAX = 2.0      # cm^2/g, SPARC upper limit
SIGMA_M_BULLET_MAX = 0.5      # cm^2/g, Cha+ 2025

# Channel velocities
V_CLOUD9 = 28.0      # km/s
V_GALAXY = 100.0     # km/s
V_BULLET = 3000.0    # km/s

# Scan grid (manageable for one session)
SCAN_GRID = {
    "m_phi_MeV": [5.0, 10.0, 20.0, 50.0, 100.0],          # 5 points
    "g_chi": [0.3, 0.5, 0.8, 1.0, 1.2, 1.5],              # 6 points
    "M_halo_Msun": [1e8, 1e9, 1e10],                      # 3 points (dwarf scale)
    "m_chi_H_GeV": [10.0, 30.0, 100.0],                  # 3 points
    "mass_ratio": [2.0, 3.0, 5.0],                        # 3 points
}


def evaluate_point(
    m_phi_MeV: float,
    g_chi: float,
    M_halo_Msun: float,
    m_chi_H_GeV: float,
    mass_ratio: float,
    t_final_Gyr: float = 5.0,
) -> dict:
    """Evaluate sigma/m at all three velocities for one parameter point.

    Returns dict with sigma/m values and Cloud-9/Bullet/Galaxy status.
    """
    m_chi_L_GeV = m_chi_H_GeV / mass_ratio

    # Use the gravothermal fluid model to get the density profile
    try:
        halo = gravothermal_two_component(
            M_halo_Msun=M_halo_Msun,
            c=15.0,
            m_chi_H_GeV=m_chi_H_GeV,
            m_chi_L_GeV=m_chi_L_GeV,
            g_chi_H=g_chi,
            g_chi_L=g_chi * 0.8,  # light species has slightly weaker coupling
            m_phi_MeV=m_phi_MeV,
            t_final_Gyr=t_final_Gyr,
            n_radial_bins=50,
            n_time_steps=50,
            core_formation_only=True,
        )
    except Exception as e:
        return {"error": str(e)}

    # Compute sigma/m at v=28, 100, 3000 using the effective_sigma_m_at_v function
    # This is the "static" estimate using both species contributions
    sm_cloud9 = effective_sigma_m_at_v(
        V_CLOUD9, m_phi_MeV, m_chi_H_GeV, m_chi_L_GeV, g_chi, g_chi * 0.8
    )["effective"]

    sm_galaxy = effective_sigma_m_at_v(
        V_GALAXY, m_phi_MeV, m_chi_H_GeV, m_chi_L_GeV, g_chi, g_chi * 0.8
    )["effective"]

    sm_bullet = effective_sigma_m_at_v(
        V_BULLET, m_phi_MeV, m_chi_H_GeV, m_chi_L_GeV, g_chi, g_chi * 0.8
    )["effective"]

    return {
        "m_phi_MeV": m_phi_MeV,
        "g_chi": g_chi,
        "M_halo_Msun": M_halo_Msun,
        "m_chi_H_GeV": m_chi_H_GeV,
        "m_chi_L_GeV": m_chi_L_GeV,
        "mass_ratio": mass_ratio,
        "sigma_m_Cloud9": sm_cloud9,
        "sigma_m_Galaxy": sm_galaxy,
        "sigma_m_Bullet": sm_bullet,
        "Cloud9_OK": 30 < sm_cloud9 < 500,
        "Galaxy_OK": sm_galaxy < SIGMA_M_GALAXY_MAX,
        "Bullet_OK": sm_bullet < SIGMA_M_BULLET_MAX,
        "all_OK": (30 < sm_cloud9 < 500) and (sm_galaxy < SIGMA_M_GALAXY_MAX) and (sm_bullet < SIGMA_M_BULLET_MAX),
    }


def run_parameter_scan():
    """Run the full parameter scan."""
    print("=" * 70)
    print("T90.48 — Cloud-9 Parameter Scan for Multi-Component SIDM")
    print("=" * 70)
    print()
    print(f"Scan grid:")
    for k, v in SCAN_GRID.items():
        print(f"  {k}: {v}")
    print()
    total_points = 1
    for v in SCAN_GRID.values():
        total_points *= len(v)
    print(f"Total points: {total_points}")
    print()

    results = []
    compatible = []
    t_start = time.time()

    for m_phi in SCAN_GRID["m_phi_MeV"]:
        for g_chi in SCAN_GRID["g_chi"]:
            for M_halo in SCAN_GRID["M_halo_Msun"]:
                for m_chi_H in SCAN_GRID["m_chi_H_GeV"]:
                    for ratio in SCAN_GRID["mass_ratio"]:
                        r = evaluate_point(
                            m_phi, g_chi, M_halo, m_chi_H, ratio
                        )
                        results.append(r)
                        if r.get("all_OK", False):
                            compatible.append(r)
                        if len(results) % 50 == 0:
                            elapsed = time.time() - t_start
                            print(f"  {len(results)}/{total_points} points evaluated ({elapsed:.1f}s elapsed, "
                                  f"{len(compatible)} Cloud-9 compatible)")

    elapsed = time.time() - t_start
    print()
    print(f"Scan complete: {len(results)} points in {elapsed:.1f}s")
    print(f"  Cloud-9 compatible points: {len(compatible)} / {len(results)} "
          f"({100*len(compatible)/len(results):.1f}%)")
    print()

    # Top 10 by Cloud-9 sigma/m
    sorted_by_cloud9 = sorted(results, key=lambda r: -r.get("sigma_m_Cloud9", 0))
    print("Top 10 points by sigma/m(Cloud-9):")
    for r in sorted_by_cloud9[:10]:
        print(f"  m_phi={r['m_phi_MeV']:6.1f} MeV, g={r['g_chi']:.2f}, "
              f"M_halo={r['M_halo_Msun']:.0e}, m_H={r['m_chi_H_GeV']:.0f} GeV, "
              f"ratio={r['mass_ratio']:.1f}: sm(C9)={r['sigma_m_Cloud9']:.2e}, "
              f"sm(Gal)={r['sigma_m_Galaxy']:.2e}, sm(Bul)={r['sigma_m_Bullet']:.2e}, "
              f"all={'YES' if r['all_OK'] else 'no'}")

    print()
    if compatible:
        print(f"Cloud-9 COMPATIBLE POINTS (sigma/m(C9) in 30-500 AND sigma/m(Gal)<2 AND sigma/m(Bul)<0.5):")
        for r in compatible[:10]:
            print(f"  m_phi={r['m_phi_MeV']:6.1f} MeV, g={r['g_chi']:.2f}, "
                  f"M_halo={r['M_halo_Msun']:.0e}, m_H={r['m_chi_H_GeV']:.0f} GeV, "
                  f"ratio={r['mass_ratio']:.1f}: sm(C9)={r['sigma_m_Cloud9']:.2e}")
    else:
        print("NO Cloud-9 compatible points found in this scan.")
        print()
        print("Closest to Cloud-9 (sigma/m(C9) > 1):")
        close = [r for r in results if r.get("sigma_m_Cloud9", 0) > 1]
        for r in sorted(close, key=lambda r: -r["sigma_m_Cloud9"])[:5]:
            print(f"  m_phi={r['m_phi_MeV']:6.1f} MeV, g={r['g_chi']:.2f}, "
                  f"sm(C9)={r['sigma_m_Cloud9']:.2e}, sm(Gal)={r['sigma_m_Galaxy']:.2e}, "
                  f"sm(Bul)={r['sigma_m_Bullet']:.2e}")

    return results, compatible


if __name__ == "__main__":
    results, compatible = run_parameter_scan()

    # Save to JSON
    out_path = Path("v0.3-prelim/data/results/t90_v48_parameter_scan.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "scan_grid": SCAN_GRID,
            "n_total": len(results),
            "n_compatible": len(compatible),
            "results": results,
            "compatible": compatible,
        }, f, indent=2, default=str)
    print()
    print(f"Results saved to {out_path}")