"""
Phase 9b — Multi-Component SIDM Mass Segregation (Corrected)

Phase 9 used σ/m at local escape velocity which is 1000s km/s — way
above Yukawa Born validity. Phase 9b fixes this by computing σ/m at
the HALO VELOCITY DISPERSION (v_disp), which is what observations
actually probe (dSph v~30, MW v~100, cluster v~3000).

The hypothesis: in a multi-component SIDM halo (m_H > m_L), the heavy
species sinks to the center over time. The OBSERVED σ/m_measured at
the half-light radius reflects the DENSITY-WEIGHTED mixture of heavy
and light species there.

For YOUNG halos (dSph, LSB), segregation hasn't completed → mixed
species → σ/m_obs reflects average σ/m.

For OLD halos (MW, cluster), segregation is complete → heavy-rich
center, light-rich outskirts. The HALF-LIGHT radius is the "transition
zone" → σ/m_obs reflects mixed species but biased toward heavy.

Phase 9b tests whether mass segregation can reproduce the σ/m_observed
spread at v_disp:
  - Cloud-9 (v=30, age=5): σ/m_obs = 50 cm²/g (or so, depending on M_halo)
  - Galactic cores (v=100, age=10): σ/m_obs = 1 cm²/g
  - Bullet (v=3000, age=10): σ/m_obs = 0.5 cm²/g

Approach: Run gravothermal_two_component for each halo, then at the
HALF-LIGHT radius, compute σ/m at the HALO'S v_disp (not local v_escape).
The density-weighting between H and L species gives σ/m_obs.
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
    gravothermal_two_component,
    nfw_density, nfw_mass, nfw_concentration_to_rho_s,
)
from t40_yukawa_sigma_m import sigma_m_cm2_per_g

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Halo types: (M_halo, c, age_Gyr, name, v_disp_kms, sigma_m_observed)
HALO_TYPES = [
    {"name": "Dwarf/LSB (YOUNG)", "M_halo_Msun": 1e9, "c": 15.0, "age_Gyr": 5.0,
     "v_disp_kms": 30.0, "observed_sigma_m": 30.0},
    {"name": "MW-like (OLD)", "M_halo_Msun": 1e12, "c": 12.0, "age_Gyr": 10.0,
     "v_disp_kms": 100.0, "observed_sigma_m": 1.0},
    {"name": "Cluster (OLD)", "M_halo_Msun": 1e14, "c": 6.0, "age_Gyr": 10.0,
     "v_disp_kms": 3000.0, "observed_sigma_m": 0.5},
]

# v0.3-prelim parameters
M_CHI_H_GEV = 45.0
M_CHI_L_GEV = 15.0   # m_H/m_L = 3
G_CHI = 0.7          # same coupling for both
M_PHI_MEV = 100.0    # v0.3-prelim SIDM MAP value


def sigma_m_observed_at_halo(halo: dict, m_phi_MeV: float, g_chi: float) -> dict:
    """
    Compute σ/m_observed at the half-light radius using v_disp (not v_escape).

    At each halo, the gravitational evolution produces density profiles
    rho_H(r) and rho_L(r). At the half-light radius r_half:
      - The OBSERVED σ/m is the density-weighted mixture:
        sigma_m_obs(r_half) = (rho_H * sigma_H(v_disp) + rho_L * sigma_L(v_disp))
                              / (rho_H + rho_L)
      - sigma_H(v) = sigma_m_cm2_per_g(v, m_phi, m_H, g)
      - sigma_L(v) = sigma_m_cm2_per_g(v, m_phi, m_L, g)

    Time evolution: at t=0 (initial), rho_H = rho_L everywhere (mixed).
    At t=age, mass segregation has moved heavy inward (in inner region)
    and pushed light outward (in outer region).
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
        g_chi_H=G_CHI,
        g_chi_L=G_CHI,
        m_phi_MeV=m_phi_MeV,
        t_final_Gyr=age + 1.0,
        n_radial_bins=80,
        n_time_steps=100,
    )

    r_kpc = res["r_kpc"]
    rho_s, r_s, r_vir = nfw_concentration_to_rho_s(M_halo, c)
    # Half-light radius: 0.02 * r_vir (representative)
    r_half_kpc = 0.02 * r_vir
    idx_half = np.argmin(np.abs(r_kpc - r_half_kpc))

    # Find time index for the requested age
    t_idx_age = np.argmin(np.abs(res["time_Gyr"] - age))

    # Compute σ/m at v_disp (NOT local v_escape) for each species
    v_disp = halo["v_disp_kms"]
    sigma_H_v = sigma_m_cm2_per_g(v_disp, m_phi_MeV, M_CHI_H_GEV, g_chi)
    sigma_L_v = sigma_m_cm2_per_g(v_disp, m_phi_MeV, M_CHI_L_GEV, g_chi)

    # Density-weighted mixture at r_half, initial state (mixed)
    rho_H_init = res["rho_H_initial"][idx_half]
    rho_L_init = res["rho_L_initial"][idx_half]
    f_H_init = rho_H_init / (rho_H_init + rho_L_init) if (rho_H_init + rho_L_init) > 0 else 0.5
    sigma_m_no_seg = f_H_init * sigma_H_v + (1 - f_H_init) * sigma_L_v

    # Evolved state
    rho_H_ev = res["rho_H_history"][t_idx_age, idx_half]
    rho_L_ev = res["rho_L_history"][t_idx_age, idx_half]
    f_H_ev = rho_H_ev / (rho_H_ev + rho_L_ev) if (rho_H_ev + rho_L_ev) > 0 else 0.5
    sigma_m_evolved = f_H_ev * sigma_H_v + (1 - f_H_ev) * sigma_L_v

    print(f"  r_vir = {r_vir:.1f} kpc, r_half = {r_half_kpc:.1f} kpc")
    print(f"  σ_H(v_disp) = {sigma_H_v:.3f} cm²/g")
    print(f"  σ_L(v_disp) = {sigma_L_v:.3f} cm²/g")
    print(f"  f_H(r_half, t=0):    {f_H_init:.3f}")
    print(f"  f_H(r_half, t=age):  {f_H_ev:.3f}")
    print(f"  σ/m_obs (no seg):    {sigma_m_no_seg:.4f} cm²/g")
    print(f"  σ/m_obs (evolved):   {sigma_m_evolved:.4f} cm²/g")
    print(f"  σ/m_obs (data):      {halo['observed_sigma_m']} cm²/g")
    if sigma_m_evolved > 0:
        ratio = halo['observed_sigma_m'] / sigma_m_evolved
        print(f"  ratio data/evolved:  {ratio:.2f}")

    return {
        "halo": halo["name"],
        "M_halo_Msun": M_halo,
        "c": c,
        "age_Gyr": age,
        "v_disp_kms": v_disp,
        "r_vir_kpc": float(r_vir),
        "r_half_kpc": float(r_half_kpc),
        "observed_sigma_m": halo["observed_sigma_m"],
        "sigma_H_at_v_disp": float(sigma_H_v),
        "sigma_L_at_v_disp": float(sigma_L_v),
        "f_H_at_r_half_initial": float(f_H_init),
        "f_H_at_r_half_evolved": float(f_H_ev),
        "sigma_m_no_segregation": float(sigma_m_no_seg),
        "sigma_m_evolved": float(sigma_m_evolved),
        "ratio_data_to_evolved": float(halo['observed_sigma_m'] / sigma_m_evolved) if sigma_m_evolved > 0 else None,
    }


def main():
    print("=" * 80)
    print("Phase 9b — Multi-Component SIDM σ/m_observed Spread Test (CORRECTED)")
    print("=" * 80)
    print(f"Parameters: m_H={M_CHI_H_GEV} GeV, m_L={M_CHI_L_GEV} GeV, g_H=g_L={G_CHI}")
    print(f"           m_phi={M_PHI_MEV} MeV (v0.3-prelim SIDM MAP)")
    print(f"           σ/m evaluated at v_disp (not local escape velocity)")
    print()

    t0 = time.time()
    results = []
    for halo in HALO_TYPES:
        try:
            r = sigma_m_observed_at_halo(halo, M_PHI_MEV, G_CHI)
            results.append(r)
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({"halo": halo["name"], "error": str(e)})

    wall = time.time() - t0

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Halo':<25} {'v [km/s]':<10} {'σ/m obs':<12} {'σ/m evol':<12} {'ratio':<10}")
    for r in results:
        if "error" in r:
            print(f"{r['halo']:<25} {'—':<10} {'—':<12} ERROR: {r['error']}")
        else:
            print(f"{r['halo']:<25} {r['v_disp_kms']:<10.0f} {r['observed_sigma_m']:<12.3f} "
                  f"{r['sigma_m_evolved']:<12.4f} {r['ratio_data_to_evolved']:<10.2f}")

    # Interpretation
    print()
    print("Interpretation:")
    successful = [r for r in results if "error" not in r]
    if successful:
        evolved_vals = [r["sigma_m_evolved"] for r in successful]
        observed_vals = [r["observed_sigma_m"] for r in successful]
        if all(v > 0 for v in evolved_vals):
            # Spread of σ/m_evolved
            spread_evolved = max(evolved_vals) / min(evolved_vals)
            spread_observed = max(observed_vals) / min(observed_vals)
            print(f"  σ/m_evolved spread: {spread_evolved:.2f}×")
            print(f"  σ/m_observed spread: {spread_observed:.2f}×")
            if spread_evolved >= spread_observed * 0.5:
                print(f"  ✓ Mass segregation reproduces the observed σ/m spread")
            else:
                print(f"  ✗ Mass segregation INSUFFICIENT to explain the σ/m spread")
                print(f"  Additional mechanism needed (multi-portal, m_phi variation, etc.)")

    out = {
        "test": "Phase9b_multi_component_mass_segregation_vdisp",
        "direction": "Yang+ 2025 mass segregation at v_disp (corrected from v_escape)",
        "parameters": {
            "m_H_GeV": M_CHI_H_GEV,
            "m_L_GeV": M_CHI_L_GEV,
            "mass_ratio": 3,
            "g_H": G_CHI,
            "g_L": G_CHI,
            "m_phi_MeV": M_PHI_MEV,
        },
        "halo_results": results,
        "wall_seconds": wall,
    }

    out_path = RESULTS_DIR / "phase9b_mass_segregation_vdisp.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
