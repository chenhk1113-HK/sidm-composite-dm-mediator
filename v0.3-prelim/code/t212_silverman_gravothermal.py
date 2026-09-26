"""
T212 — Gravothermal cascade at Silverman+ 2026 parameters.

Silverman+ 2026 (arXiv:2606.02566, Fermilab-PUB-26-0348-T) finds that
gravothermal collapse proceeds at sigma/m = 70 cm^2/g in M_halo ~ 10^10
M_sun halos with QUIESCENT merger histories. 3 of 6 halos collapse.

This is a major Path B3 candidate I missed. Re-evaluate t_core at
Cloud-9 host-halo parameters (M_halo = 5e9 M_sun, sigma/m = 70 cm^2/g)
to see if gravothermal cascade can run.

Balberg+ 2002 Eq. 22:
t_core = 12.7 / sigma_m * (rho_s / 1e-2)^-1 * (r_s / 1e4) * (100/v_max) Gyr

where sigma_m is in cm^2/g, rho_s in M_sun/pc^3, r_s in pc, v_max in km/s.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import sys
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

# Use T208 Balberg formula
from T208_path_b_cloud9_host_halo_gravothermal import (
    gravothermal_t_core_Gyr as balberg_t_core_Gyr,
    nfw_r_vir_pc, nfw_rho_s_from_concentration, v_max_from_M_c,
    V_REF,
)

def t_cross_Gyr_from_r_vir_vmax(r_vir_pc, v_max_kms):
    """Halo crossing time: t_cross = r_vir / v_max in Gyr."""
    # r_vir in pc, v_max in km/s
    # pc / (km/s) = 3.0857e13 s
    # Gyr = 3.1557e16 s
    return (r_vir_pc / v_max_kms * 3.0857e13) / 3.1557e16


def evaluate(params):
    M = params["M_halo"]
    c = params["c"]
    sigma_m = params["sigma_m"]
    r_vir = nfw_r_vir_pc(M)
    rho_s, r_s = nfw_rho_s_from_concentration(M, c, r_vir)
    v_max = v_max_from_M_c(M, c, r_vir)
    t_core = balberg_t_core_Gyr(sigma_m, rho_s, r_s, v_max)
    t_cross = t_cross_Gyr_from_r_vir_vmax(r_vir, v_max)
    return {
        "M_halo_M_sun": M,
        "c": c,
        "v_max_km_s": v_max,
        "r_vir_pc": r_vir,
        "r_s_pc": r_s,
        "rho_s_M_sun_pc3": rho_s,
        "sigma_m_cm2_g": sigma_m,
        "t_core_Gyr": t_core,
        "t_cross_Gyr": t_cross,
        "t_core_over_Hubble": t_core / 13.8,
        "t_core_over_t_cross": t_core / t_cross,
        "phase_runs": t_core < 13.8,
        "causality_ok": t_core > 3.0 * t_cross,
    }

# Silverman+ 2026 parameters
SILVERMAN_PARAMS = {
    "M_halo": 1e10,        # M_sun (their m10 host halos)
    "c": 12.0,             # typical NFW concentration at this mass
    "sigma_m": 70.0,       # cm^2/g at v_max
    "v_max": 35.0,         # km/s (typical for M=10^10 halo with c=12)
}

# Cloud-9 host halo
CLOUD9_HOST = {
    "M_halo": 5e9,
    "c": 12.0,
    "sigma_m": 70.0,       # Silverman's value
    "v_max": None,         # compute from NFW
}


def main():
    print("=" * 80)
    print("T212 Gravothermal at Silverman+ 2026 parameters")
    print("=" * 80)

    print("\n--- Silverman+ 2026 fiducial: M=10^10 M_sun, sigma/m=70 cm^2/g ---")
    r1 = evaluate(SILVERMAN_PARAMS)
    for k, v in r1.items():
        print(f"  {k}: {v}")

    print("\n--- Cloud-9 host halo at sigma/m=70 cm^2/g ---")
    r2 = evaluate(CLOUD9_HOST)
    for k, v in r2.items():
        print(f"  {k}: {v}")

    print("\n--- What sigma/m does gravothermal NEED to collapse at Cloud-9 host? ---")
    # Find sigma_threshold such that t_core = Hubble
    sigma_threshold_5e9 = None
    for sigma in [0.052, 1.0, 10.0, 50.0, 70.0, 100.0, 150.0, 200.0, 500.0]:
        params = {"M_halo": 5e9, "c": 12.0, "sigma_m": sigma, "v_max": None}
        r = evaluate(params)
        marker = " <-- threshold" if r["t_core_over_Hubble"] < 1.0 and (sigma_threshold_5e9 is None) else ""
        if r["t_core_over_Hubble"] < 1.0 and sigma_threshold_5e9 is None:
            sigma_threshold_5e9 = sigma
        print(f"  sigma/m = {sigma:6.1f} cm^2/g: t_core = {r['t_core_Gyr']:7.2f} Gyr, t_core/t_Hubble = {r['t_core_over_Hubble']:6.2f}{marker}")

    # Same for 1e10 (Silverman+ mass)
    print("\n--- At Silverman+ M=10^10 M_sun halo ---")
    sigma_threshold_1e10 = None
    for sigma in [0.052, 1.0, 10.0, 50.0, 70.0, 100.0, 150.0, 200.0, 500.0]:
        params = {"M_halo": 1e10, "c": 12.0, "sigma_m": sigma, "v_max": None}
        r = evaluate(params)
        marker = " <-- threshold" if r["t_core_over_Hubble"] < 1.0 and (sigma_threshold_1e10 is None) else ""
        if r["t_core_over_Hubble"] < 1.0 and sigma_threshold_1e10 is None:
            sigma_threshold_1e10 = sigma
        print(f"  sigma/m = {sigma:6.1f} cm^2/g: t_core = {r['t_core_Gyr']:7.2f} Gyr, t_core/t_Hubble = {r['t_core_over_Hubble']:6.2f}{marker}")

    print(f"\nThreshold sigma/m for t_core = Hubble:")
    print(f"  At M_halo = 5e9 M_sun (Cloud-9 host): {sigma_threshold_5e9} cm^2/g")
    print(f"  At M_halo = 1e10 M_sun (Silverman+): {sigma_threshold_1e10} cm^2/g")

    # Save
    results = {
        "silverman_fiducial": r1,
        "cloud9_host_at_sigma70": r2,
        "threshold_5e9_cm2_g": sigma_threshold_5e9,
        "threshold_1e10_cm2_g": sigma_threshold_1e10,
    }
    out_path = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t212_silverman_gravothermal.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()