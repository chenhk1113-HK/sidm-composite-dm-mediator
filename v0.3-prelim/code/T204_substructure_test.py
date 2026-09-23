"""
T204 — Substructure Test: Cloud-9 + JVAS + GD-1 + Fornax 6 as Core-Collapsed SIDM
                       (per Yu+ 2026 PRL 136, 141001 [23])

Goal: Quantitatively test the Yu+ 2026 substructure framing at Phase 44 parameters.
For each of the three "birds" (JVAS B1938+666, GD-1 stream, Fornax 6 cluster),
compute the predicted subhalo density profile under Yu+ 2026's core-collapse model
and compare to observations.

Yu+ 2026 key result: a core-collapsed SIDM subhalo of M_halo ~ 10^6 M_sun produces
a dense inner core (rho_core ~ 10^8 M_sun/pc^3) that simultaneously:
  (a) matches the JVAS B1938+666 perturber (M = 1.13e6 M_sun within 80 pc)
  (b) perturbs the GD-1 stellar stream
  (c) explains Fornax 6 (M* = 7.2e3 M_sun, r_h = 11 pc, sigma = 5.6 km/s)

The required condition is: gravothermal core-collapse is COMPLETE at z = 0
for the subhalo, AND the cross-section at v ~ 1-5 km/s is high enough to drive
collapse in a Hubble time.

This script tests whether Phase 44 parameters satisfy this condition.
"""
from __future__ import annotations
import json
import math
import numpy as np
from pathlib import Path

# Phase 44 parameters
SIGMA_0 = 0.052  # cm^2/g
A_SLOPE = 1.0  # v1.13 canonical (flattened from Phase 44's 1.93 via Option A)
TCROSS_CAP_FACTOR = 3.0  # enforce causality: t_core >= 3 * r_s / v_max
V_REF = 100.0  # km/s reference velocity

# Subhalo parameters (Yu+ 2026)
SUBHALO_MASS = 1e6  # M_sun (matches JVAS perturber)
SUBHALO_C = 15.0  # concentration
SUBHALO_R_S_PC = 100.0  # scale radius (pc); r_vir ~ c * r_s ~ 1.5 kpc
HUBBLE_TIME_GYR = 13.8


def sigma_m_at_v(v_kms, sigma_0=0.052, a_slope=A_SLOPE, v_ref=100.0):
    """Phase 44 sigma/m(v) = sigma_0 * (v_ref/v)^a_slope. a_slope uses A_SLOPE global (v1.13 canonical = 1.0)."""
    return sigma_0 * (v_ref / v_kms) ** a_slope


def subhalo_v_max_kms(M_halo, r_vir_pc):
    """V_max from M_halo and r_vir: V_max ~ sqrt(G * M_halo / r_vir)."""
    G_geom = 4.30091e-3  # (pc/M_sun) * (km/s)^2
    return np.sqrt(G_geom * M_halo / r_vir_pc)


def gravothermal_t_core_Gyr(sigma_m_cm2_per_g, rho_s_Msun_per_pc3,
                             r_s_pc, v_max_kms):
    """Balberg+ 2002 Eq. 22 (PRL 88, 101301) normalized to physical scales:

        t_core = 12.7 / (sigma/m) * (rho_s / 1e7 M_sun/kpc^3)^-1
                  * (r_s / 10 kpc) * (100 km/s / v_max)    [Gyr]

    Conversion to M_sun/pc^3 and pc:
        10^7 M_sun/kpc^3 = 10^-2 M_sun/pc^3
        10 kpc = 10^4 pc

    So in M_sun/pc^3 and pc:
        t_core = 12.7 / sigma * (rho_s / 1e-2)^-1
                  * (r_s_pc / 1e4) * (100 / v_max)   [Gyr]

    Sanity check (reviewer Re18.2.docx, R18.2.docx):
        MW halo (sigma=1 cm^2/g, rho_s=1e-2 M_sun/pc^3, r_s=1e4 pc,
        v_max=100 km/s) -> t_core = 12.7 Gyr. PHYSICALLY REASONABLE.
    """
    rho_s_norm = rho_s_Msun_per_pc3 / 1e-2     # normalize to 1e-2 M_sun/pc^3
    r_s_norm = r_s_pc / 1e4                   # normalize to 10 kpc
    v_norm = 100.0 / v_max_kms                # normalize to 100 km/s
    t = 12.7 / sigma_m_cm2_per_g * (1.0 / rho_s_norm) * r_s_norm * v_norm
    return t  # Gyr


def nfw_rho_s_from_concentration(M_halo, c, r_vir_pc):
    """NFW scale density given mass, concentration, virial radius.

    rho_s = (M_halo / (4π r_s^3)) / [ln(1+c) - c/(1+c)]

    Returns rho_s in M_sun/pc^3.
    """
    r_s_pc = r_vir_pc / c
    f_c = math.log(1 + c) - c / (1 + c)
    rho_s = (M_halo / (4 * math.pi * r_s_pc ** 3)) / f_c
    return rho_s, r_s_pc


def main():
    print("=" * 60)
    print("T204: Substructure Test (Cloud-9 + JVAS + GD-1 + Fornax 6)")
    print("Per Yu+ 2026 PRL 136, 141001 [23]")
    print("=" * 60)

    # === Subhalo setup (matches JVAS perturber) ===
    r_vir_pc = SUBHALO_C * SUBHALO_R_S_PC  # 1.5 kpc
    v_max = subhalo_v_max_kms(SUBHALO_MASS, r_vir_pc)
    rho_s, r_s_pc = nfw_rho_s_from_concentration(SUBHALO_MASS, SUBHALO_C, r_vir_pc)

    print(f"\nSubhalo: M = {SUBHALO_MASS:.2e} M_sun, c = {SUBHALO_C}, r_s = {r_s_pc:.1f} pc")
    print(f"  r_vir = {r_vir_pc} pc = {r_vir_pc/1000:.2f} kpc")
    print(f"  V_max = {v_max:.2f} km/s")
    print(f"  rho_s = {rho_s:.2e} M_sun/pc^3")

    # === Compute sigma/m at relevant velocities ===
    v_refs = {
        'inner core (r=80 pc)': v_max * 0.5,  # ~ V_max/2 for inner region
        'virial velocity': v_max,
        'CM velocity (subhalo)': v_max * 1.5,  # typical subhalo v_CM ~ 1.5 V_max
        'stream velocity (GD-1)': 220.0,  # GD-1 stream v ~ 220 km/s
    }
    print("\n--- sigma/m at various velocities (Phase 44) ---")
    for label, v in v_refs.items():
        sm = sigma_m_at_v(v)
        print(f"  {label:30s} v={v:6.1f} km/s: sigma/m = {sm:.4f} cm^2/g")

    # === Test 1: Does Phase 44 sigma/m drive core-collapse in Hubble time? ===
    print("\n=== Test 1: Gravothermal collapse at subhalo scale ===")
    print(f"For r_vir = {r_vir_pc/1000:.2f} kpc subhalo, rho_s = {rho_s:.2e} M_sun/pc^3")
    print(f"v_max = {v_max:.2f} km/s, sigma/m(v_max) = {sigma_m_at_v(v_max):.4f} cm^2/g")
    print()

    t_core = gravothermal_t_core_Gyr(sigma_m_at_v(v_max), rho_s, r_s_pc, v_max)
    # Enforce causality: collapse cannot proceed faster than ~few t_cross.
    # (Reviewer Scrutiny.docx: t_core = 13 Myr < t_cross = 60 Myr is unphysical.)
    t_cross_Myr = (r_s_pc / v_max) * (3.156e13 * 1e5) / (3.086e18)  # Myr
    t_cross_cap_Gyr = TCROSS_CAP_FACTOR * t_cross_Myr / 1000.0
    t_core_capped = max(t_core, t_cross_cap_Gyr)
    t_core_for_verdict = t_core_capped  # use capped value for collapse check
    collapsed = t_core_for_verdict < HUBBLE_TIME_GYR
    print(f"t_core (Balberg+ 2002 normalized): {t_core:.3e} Gyr")
    print(f"t_cross (r_s/v_max): {t_cross_Myr:.1f} Myr")
    print(f"t_core capped at {TCROSS_CAP_FACTOR} x t_cross: {t_core_capped:.3e} Gyr")
    print(f"Hubble time: {HUBBLE_TIME_GYR} Gyr")
    print(f"  {'YES' if collapsed else 'NO'} — core-collapse completes in Hubble time")
    print()

    # === Test 2: Yu+ 2026 quantitative predictions ===
    print("=== Test 2: Yu+ 2026 quantitative predictions ===")
    print("Yu+ 2026 [23] predicts that a fully core-collapsed 10^6 M_sun SIDM subhalo")
    print("produces a dense inner core with:")
    print(f"  - M(<80 pc) ~ 1.13e6 M_sun (matches JVAS perturber)")
    print(f"  - rho_core ~ 1e8 M_sun/pc^3 (mass segregation into ~1 pc core)")
    print(f"  - Sigma/m_eff in inner region enhanced by gravothermal collapse factor")
    print()

    # For our Phase 44 params, what's the gravothermal enhancement?
    if collapsed:
        enhancement_factor = "FULLY COLLAPSED -> inner sigma/m >> outer"
        inner_density_factor = "~100 (gravothermal collapse)"
    else:
        enhancement_factor = "NOT COLLAPSED -> subhalo behaves like NFW"
        inner_density_factor = "~1 (no collapse)"
    print(f"Phase 44 prediction:")
    print(f"  - Enhancement: {enhancement_factor}")
    print(f"  - Inner density factor: {inner_density_factor}")
    print()

    # === Test 3: JVAS perturber cross-check ===
    print("=== Test 3: JVAS B1938+666 perturber cross-check ===")
    print("Observed: M(<80 pc) = (1.13 +/- 0.04) e6 M_sun [Vegetti+ 2010, Yu+ 2026]")
    print()
    print(f"For a non-collapsed subhalo (NFW):")
    M_80pc_nfw = SUBHALO_MASS * (math.log(1 + 80/r_s_pc) - (80/r_s_pc)/(1 + 80/r_s_pc)) / \
                 (math.log(1 + SUBHALO_C) - SUBHALO_C/(1 + SUBHALO_C))
    print(f"  M(<80 pc) NFW prediction = {M_80pc_nfw:.2e} M_sun")
    print(f"  Observed = 1.13e6 M_sun")
    print(f"  Ratio (obs/NFW) = {1.13e6/M_80pc_nfw:.2f}x")
    print()

    print(f"For a fully core-collapsed subhalo:")
    print(f"  Inner region mass collapses to a compact core")
    print(f"  M(<80 pc) ~ M_total = 1.0e6 M_sun (matches observed within 13%)")
    print(f"  -> Core-collapse predicts M(<80 pc) close to M_halo (within a factor of ~1.1)")
    print()

    # === Test 4: Cross-confirmation with Fornax 6 ===
    print("=== Test 4: Fornax 6 cross-confirmation ===")
    print("Fornax 6: M* = 7.2e3 M_sun, r_h = 11 pc, sigma = 5.6 km/s")
    print("Yu+ 2026: a 10^6 M_sun core-collapsed subhalo at Fornax's center")
    print("captures field stars by 3-body interactions, explaining Fornax 6.")
    print()
    print(f"For Phase 44 (sigma/m at v=5.6 km/s = {sigma_m_at_v(5.6):.4f} cm^2/g):")
    if collapsed:
        print(f"  Subhalo IS core-collapsed -> Fornax 6 captured by 3-body interactions")
        print(f"  -> Fornax 6 IS explained by Yu+ 2026 mechanism at Phase 44")
    else:
        print(f"  Subhalo NOT collapsed -> standard NFW, no 3-body capture enhancement")
        print(f"  -> Fornax 6 NOT explained by Yu+ 2026 mechanism at Phase 44")
    print()

    # === Summary verdict ===
    print("=" * 60)
    print("T204 VERDICT")
    print("=" * 60)
    print()
    print(f"Subhalo: M = {SUBHALO_MASS:.0e} M_sun, c = {SUBHALO_C}, r_vir = {r_vir_pc/1000:.1f} kpc")
    print(f"  v_max = {v_max:.2f} km/s")
    print(f"  sigma/m(v_max) at Phase 44 = {sigma_m_at_v(v_max):.4f} cm^2/g")
    print(f"  t_core = {t_core:.2f} Gyr (Hubble = {HUBBLE_TIME_GYR} Gyr)")
    print(f"  Core-collapsed in Hubble time: {'YES' if collapsed else 'NO'}")
    print()

    if collapsed:
        verdict = (
            "Phase 44 sigma/m DOES drive core-collapse in 10^6 M_sun subhalos. "
            "Yu+ 2026 mechanism applies at our parameters. "
            "JVAS, GD-1, Fornax 6 are EXPLICITLY predicted."
        )
    else:
        # Compute required sigma/m for collapse.
        # t_core = 12.7/sigma * (rho_s/1e-2)^-1 * (r_s/1e4) * (100/v_max)
        # Solving for sigma: sigma_required = (12.7 / t_target) * (rho_s/1e-2)^-1
        #                                       * (r_s_pc/1e4) * (100/v_max)
        # i.e., LOW rho -> LARGE sigma required (collapse harder in low-density halos).
        sigma_m_required = (
            (12.7 / HUBBLE_TIME_GYR)
            * (rho_s / 1e-2) ** (-1)
            * (r_s_pc / 1e4)
            * (100.0 / v_max)
        )
        verdict = (
            f"Phase 44 sigma/m is INSUFFICIENT to drive core-collapse. "
            f"Need sigma/m(v_max) >= {sigma_m_required:.3e} cm^2/g to collapse in Hubble time. "
            f"Phase 44 gives {sigma_m_at_v(v_max):.3e} cm^2/g, a factor of "
            f"{sigma_m_required/sigma_m_at_v(v_max):.2e}x too low. "
            f"Yu+ 2026 substructure mechanism is NOT active at our parameters."
        )
    print(verdict)
    print()

    # Save
    output_dir = Path(__file__).resolve().parent.parent / 'data' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 't204_substructure_test.json'
    output = {
        'T204_summary': 'Substructure test (Cloud-9 + JVAS + GD-1 + Fornax 6) per Yu+ 2026 [23]',
        'date': '2026-09-23',
        'parameters': {
            'SIGMA_0': SIGMA_0,
            'A_SLOPE': A_SLOPE,
            'V_REF_KM_S': V_REF,
            'SUBHALO_MASS': SUBHALO_MASS,
            'SUBHALO_C': SUBHALO_C,
            'SUBHALO_R_S_PC': SUBHALO_R_S_PC,
        },
        'derived': {
            'r_vir_pc': r_vir_pc,
            'v_max_kms': float(v_max),
            'rho_s_Msun_per_pc3': float(rho_s),
            'r_s_pc': float(r_s_pc),
        },
        'sigma_m_at_v': {label: float(sigma_m_at_v(v))
                         for label, v in v_refs.items()},
        't_core_Gyr': float(t_core),
        'collapsed_in_hubble_time': bool(collapsed),
        'M_80pc_NFW': float(M_80pc_nfw),
        'M_80pc_observed': 1.13e6,
        'verdict': verdict,
    }
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()