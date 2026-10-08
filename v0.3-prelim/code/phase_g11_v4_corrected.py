"""
Phase G11 v4 — Cosmological Halo Population Synthesis (R88(63), CORRECTED)

The v1/v2/v3 implementations had a critical bug:
- Used sigma_eff = f_H^2 * sigma_m(v_target) where v_target was fixed at 29.4 km/s
- This applied Phase 44's high sigma_m (174 cm^2/g) to all halos
- In reality, each halo's sigma_m depends on its V_max, not on v_target

This v4 uses PROPER per-halo calculations:
- V_max from NFW profile (concentration-dependent)
- sigma_m(V_max) from Phase G8 three-peak model
- sigma_eff = f_H^2 * sigma_m(V_max)
- rho_eff from NFW inner density (concentration-dependent)
- t_c from Yang+ 2024 with proper sigma_eff and rho_eff

This gives realistic tau diversity across the constrained halo sample.
"""
from __future__ import annotations
import math
import numpy as np


OMEGA_M = 0.315
HUBBLE_H = 0.674


def dutton_maccio_2014_concentration(M_200, z=0.0):
    M_pivot = 2e12 / HUBBLE_H
    M_200_h = M_200 * HUBBLE_H
    log_c = math.log10(7.40) + (-0.091) * math.log10(M_200_h / M_pivot) + (-0.69) * math.log10(1 + z)
    return 10 ** log_c


def v_max_nfw(M_200, c_200):
    """NFW V_max from M_200 and c_200.

    V_max occurs at r_max = 2.163 * r_s for NFW.
    """
    G = 4.302e-6  # kpc (km/s)^2 / M_sun
    R_200 = (G * M_200 / (100 * HUBBLE_H ** 2)) ** (1.0 / 3.0)
    r_s = R_200 / c_200
    r_max = 2.163 * r_s

    # Enclosed mass at r_max
    x = 2.163
    M_enc = M_200 * (math.log(1 + x) - x / (1 + x)) / (math.log(1 + c_200) - c_200 / (1 + c_200))

    return math.sqrt(G * M_enc / r_max)


def sigma_m_phase_g8(v):
    """Phase G8 sigma/m(v) — three-peak model."""
    background = 0.07 * (100 / v) ** 0.9
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    massive = 5 * math.exp(-((v - 150) ** 2) / 1500)
    ufd = 60 * math.exp(-((v - 10) ** 2) / 12.5)
    return background + cloud9 + massive + ufd


def rho_eff_nfw(M_200, c_200, r_over_rs=0.5):
    """NFW inner density at r/r_s.

    rho(r) = rho_s * (r/r_s)^(-1) * (1 + r/r_s)^(-2)
    rho_s from M_200 and c_200.
    """
    rho_crit = 2.775e11 * HUBBLE_H ** 2  # M_sun/Mpc^3
    rho_s = (200 * rho_crit * c_200 ** 3) / (3 * (math.log(1 + c_200) - c_200 / (1 + c_200)))

    # rho at r/r_s
    x = r_over_rs
    rho_r = rho_s * x ** (-1) * (1 + x) ** (-2)

    # Convert to M_sun/pc^3 (1 Mpc^3 = 10^9 pc^3)
    rho_r_pc = rho_r * 1e-9
    return rho_r_pc


def gravothermal_tau(M_200, c_200, f_H=0.297):
    """Compute tau = t_observed / t_c using per-halo V_max and rho_eff.

    Returns tau, V_max, sigma_m_vmax, sigma_eff, t_c.
    """
    V_max = v_max_nfw(M_200, c_200)
    sigma_m_vmax = sigma_m_phase_g8(V_max)
    sigma_eff = f_H ** 2 * sigma_m_vmax
    rho_eff_pc = rho_eff_nfw(M_200, c_200, r_over_rs=0.5)

    if rho_eff_pc <= 0 or sigma_eff <= 0:
        return 1e10, V_max, sigma_m_vmax, sigma_eff, 1e10

    # Yang+ 2024 t_c (with sigma_eff in cm^2/g and rho_eff in M_sun/pc^3)
    t_c = 28.7 * (7.1 / sigma_eff) * (0.04 / rho_eff_pc)

    # Time observed (age of universe since formation)
    # Assume formation redshift ~ 2-3 for dwarf halos, ~ 0.5 for cluster-scale
    z_form = max(0.5, 5.0 * (M_200 / 1e12) ** (-0.2))
    t_observed = 13.8 * (1 - 0.5)  # rough: 6.9 Gyr since typical formation

    tau = t_observed / t_c if t_c > 0 else 1e10
    return tau, V_max, sigma_m_vmax, sigma_eff, t_c


def f_H_sidm2c(r_over_r_s, tau, cap=0.60):
    """SIDM2c f_H(r) with tau_seg = 100 (realistic for full halo population)."""
    if tau <= 0:
        return 0.297
    tau_seg = 100.0
    concentration = 1 + (cap / 0.297 - 1) * (1 - math.exp(-tau / tau_seg))
    return 0.297 * concentration


def run_phase_g11_v4():
    print("=" * 90)
    print("Phase G11 v4 — Cosmological Halo Population Synthesis (R88(63), CORRECTED)")
    print("=" * 90)
    print()
    print("Bug fixes from v1-v3:")
    print("  v1-v3 used sigma_eff = f_H^2 * sigma_m(v_target) where v_target = 29.4 fixed")
    print("  v4 uses sigma_eff = f_H^2 * sigma_m(V_max) per halo (correct)")
    print()
    print("Per-halo calculations:")
    print("  V_max from NFW (concentration-dependent)")
    print("  sigma_m(V_max) from Phase G8 three-peak model")
    print("  rho_eff from NFW inner density at 0.5 r_s")
    print("  t_c from Yang+ 2024 with proper sigma_eff and rho_eff")
    print()

    log_masses = np.linspace(7, 12, 50)
    masses = 10 ** log_masses

    results = []
    for M in masses:
        c = dutton_maccio_2014_concentration(M)
        tau, V_max, sm, se, t_c = gravothermal_tau(M, c)

        # Compute f_H at observation radius (1.5 r_s)
        f_h = f_H_sidm2c(1.5, tau)

        # Compute sigma_eff at v=150
        se_150 = f_h ** 2 * sigma_m_phase_g8(150)

        results.append({
            "M_200": M,
            "log_M": math.log10(M),
            "c_200": c,
            "V_max": V_max,
            "sigma_m_vmax": sm,
            "sigma_eff_vmax": se,
            "t_c": t_c,
            "tau": tau,
            "f_H_15rs": f_h,
            "sigma_eff_150": se_150,
        })

    # Print
    print(f"{'log(M)':<10} {'c':<8} {'V_max':<10} {'sigma_m':<12} {'sigma_eff':<12} {'rho_eff':<12} {'t_c(Gyr)':<12} {'tau':<10}")
    print("-" * 90)
    for r in results:
        rho_eff = rho_eff_nfw(r["M_200"], r["c_200"])
        print(f"{r['log_M']:<10.2f} {r['c_200']:<8.2f} {r['V_max']:<10.2f} {r['sigma_m_vmax']:<12.4f} {r['sigma_eff_vmax']:<12.4f} {rho_eff:<12.4f} {r['t_c']:<12.2f} {r['tau']:<10.4f}")

    # Statistics
    taus = [r["tau"] for r in results]
    ses = [r["sigma_eff_150"] for r in results]
    fhs = [r["f_H_15rs"] for r in results]

    tau_min = min(taus)
    tau_max = max(taus)
    tau_range = tau_max / tau_min if tau_min > 0 else float("inf")
    se_range = max(ses) / min(ses) if min(ses) > 0 else float("inf")
    fh_range = max(fhs) / min(fhs) if min(fhs) > 0 else float("inf")

    print()
    print("=" * 90)
    print("Phase diversity statistics")
    print("=" * 90)
    print()
    print(f"tau range:       {tau_min:.4f} to {tau_max:.4f}, diversity = {tau_range:.2f}x")
    print(f"f_H range:       {min(fhs):.4f} to {max(fhs):.4f}, diversity = {fh_range:.2f}x")
    print(f"sigma_eff range: {min(ses):.4f} to {max(ses):.4f}, diversity = {se_range:.2f}x")
    print()

    if tau_range >= 2.0:
        print(f"SUCCESS: tau diversity = {tau_range:.2f}x (>= 2x)")
    else:
        print(f"FAILURE: tau diversity = {tau_range:.2f}x (< 2x)")

    if se_range >= 2.0:
        print(f"SUCCESS: sigma_eff diversity = {se_range:.2f}x (>= 2x)")
    else:
        print(f"FAILURE: sigma_eff diversity = {se_range:.2f}x (< 2x)")

    # Map constrained halos
    channels = [
        ("Fornax dSph", 1e8),
        ("Sculptor dSph", 1e8),
        ("Draco dSph", 1e8),
        ("Boötes I UFD", 5e7),
        ("Cloud-9 host", 5e9),
        ("MW-mass host (SPARC)", 1e12),
        ("Cluster (A1689)", 1e15),
    ]

    print()
    print("=" * 90)
    print("Constrained halos mapped to corrected tau values")
    print("=" * 90)
    print()
    print(f"{'Channel':<28} {'M_200':<12} {'tau':<10} {'f_H':<10} {'sigma_eff(150)':<16} {'He+':<8} {'Lei'}")
    print("-" * 95)

    constrained_tau = []
    constrained_fH = []
    constrained_se = []

    for name, M in channels:
        idx = np.argmin(np.abs(np.array(masses) - M))
        r = results[idx]
        tau = r["tau"]
        f_h = r["f_H_15rs"]
        se = r["sigma_eff_150"]

        constrained_tau.append(tau)
        constrained_fH.append(f_h)
        constrained_se.append(se)

        he_status = "PASS" if se < 0.3 else f"FAIL({se/0.3:.1f}x)"
        lei_status = "PASS" if se > 0.1 else "FAIL"

        print(f"{name:<28} {M:<12.2e} {tau:<10.4f} {f_h:<10.4f} {se:<16.4f} {he_status:<8} {lei_status}")

    # Statistics for constrained halos only
    c_tau_range = max(constrained_tau) / min(constrained_tau) if min(constrained_tau) > 0 else float("inf")
    c_se_range = max(constrained_se) / min(constrained_se) if min(constrained_se) > 0 else float("inf")

    print()
    print("=" * 90)
    print("Path 3 v4 verdict (R88(63))")
    print("=" * 90)
    print()
    print(f"Constrained halo tau range: {min(constrained_tau):.4f} to {max(constrained_tau):.4f}")
    print(f"Constrained halo tau diversity: {c_tau_range:.2f}x")
    print(f"Constrained halo sigma_eff range: {min(constrained_se):.4f} to {max(constrained_se):.4f}")
    print(f"Constrained halo sigma_eff diversity: {c_se_range:.2f}x")
    print()

    if c_tau_range >= 2.0 and c_se_range >= 2.0:
        print("SUCCESS: Path 3 breaks trade-off theorem")
        verdict = "SUCCESS"
    elif c_tau_range >= 2.0 and c_se_range < 2.0:
        print("PARTIAL/FAILURE: tau diversity exists but sigma_eff diversity insufficient")
        print("This CONFIRMS the structural trade-off theorem from a different angle")
        verdict = "PARTIAL — confirms trade-off"
    else:
        print(f"FAILURE: tau diversity = {c_tau_range:.2f}x < 2x")
        verdict = "FAILURE"

    print()
    return results, verdict, c_tau_range, c_se_range


if __name__ == "__main__":
    results, verdict, tau_div, se_div = run_phase_g11_v4()
    print()
    print("Final R88(63) verdict:", verdict)
    print(f"  Constrained halo tau diversity: {tau_div:.2f}x")
    print(f"  Constrained halo sigma_eff diversity: {se_div:.2f}x")
