"""
Phase G11 v2 — Cosmological merger histories (R88(60), Path 3) — refined

The v1 showed tau diversity exists but f_H saturates at 0.95 cap.
This version tests a less saturating SIDM2c profile to see if
tau diversity can produce differentiated sigma_eff outcomes.

Key change: f_H cap reduced from 0.95 to 0.60 (more physical for Phase 44).
This forces f_H to vary with tau in the meaningful range.
"""
from __future__ import annotations
import math
import numpy as np


OMEGA_M = 0.315
OMEGA_LAMBDA = 0.685
HUBBLE_H = 0.674
F_H_INITIAL = 0.297


def dutton_maccio_2014_concentration(M_200, z=0.0):
    M_pivot = 2e12 / HUBBLE_H
    M_200_h = M_200 * HUBBLE_H
    log_c = math.log10(7.40) + (-0.091) * math.log10(M_200_h / M_pivot) + (-0.69) * math.log10(1 + z)
    return 10 ** log_c


def v_max_nfw(M_200, c_200):
    G = 4.302e-6
    R_200 = (G * M_200 / (100 * HUBBLE_H ** 2)) ** (1.0/3.0)
    r_max = 2.163 * R_200 / c_200
    x = 2.163
    M_enc = M_200 * (math.log(1 + x) - x / (1 + x)) / (math.log(1 + c_200) - c_200 / (1 + c_200))
    return math.sqrt(G * M_enc / r_max)


def sigma_m_phase_g8(v):
    background = 0.07 * (100 / v) ** 0.9
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    massive = 5 * math.exp(-((v - 150) ** 2) / 1500)
    ufd = 60 * math.exp(-((v - 10) ** 2) / 12.5)
    return background + cloud9 + massive + ufd


def gravothermal_phase_tau(M_200, c_200):
    rho_crit = 2.775e11 * HUBBLE_H ** 2
    rho_s = (200 * rho_crit * c_200 ** 3) / (3 * (math.log(1 + c_200) - c_200 / (1 + c_200)))
    rho_eff_pc = rho_s * 0.01 * 1e-9
    V_max = v_max_nfw(M_200, c_200)
    sigma_m_vmax = sigma_m_phase_g8(V_max)
    sigma_eff = F_H_INITIAL ** 2 * sigma_m_vmax
    t_c = 28.7 * (7.1 / sigma_eff) * (0.04 / rho_eff_pc) if rho_eff_pc > 0 else 1e10
    tau = 13.8 / t_c
    return tau, V_max, sigma_eff


def f_H_sidm2c_v2(r_over_r_s, tau, cap=0.60):
    """Refined SIDM2c with smaller cap and stronger tau dependence."""
    if tau <= 0:
        return F_H_INITIAL
    tau_seg = 0.3  # shorter segregation timescale
    concentration = 1 + (cap/F_H_INITIAL - 1) * (1 - math.exp(-tau / tau_seg))
    return F_H_INITIAL * concentration


def run_phase_g11_v2():
    print("=" * 90)
    print("Phase G11 v2 — Cosmological Halo Population Synthesis (R88(60), Path 3 refined)")
    print("=" * 90)
    print()
    print("Refinement: SIDM2c f_H(r) cap reduced to 0.60 (from 0.95)")
    print("This allows tau-dependent differentiation of f_H across halos.")
    print()

    log_masses = np.linspace(7, 12, 50)
    masses = 10 ** log_masses

    results = []
    for M in masses:
        c = dutton_maccio_2014_concentration(M)
        tau, V_max, sigma_eff = gravothermal_phase_tau(M, c)
        results.append({
            "M_200": M,
            "log_M": math.log10(M),
            "c_200": c,
            "V_max": V_max,
            "sigma_eff": sigma_eff,
            "tau": tau,
            "f_H": f_H_sidm2c_v2(1.5, tau, cap=0.60),
        })

    # Compute sigma_eff(150) for each halo
    for r in results:
        r["sigma_eff_150"] = r["f_H"] ** 2 * sigma_m_phase_g8(150)

    # Print table
    print(f"{'log(M)':<10} {'M_200':<12} {'c':<8} {'V_max':<10} {'tau':<10} {'f_H(1.5r_s)':<14} {'sigma_eff(150)'}")
    print("-" * 90)
    for r in results:
        print(f"{r['log_M']:<10.2f} {r['M_200']:<12.2e} {r['c_200']:<8.2f} {r['V_max']:<10.2f} {r['tau']:<10.4f} {r['f_H']:<14.4f} {r['sigma_eff_150']:.4f}")

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
    print("Constrained halos (v2 with cap=0.60)")
    print("=" * 90)
    print()
    print(f"{'Channel':<28} {'tau':<10} {'f_H':<10} {'sigma_eff(150)':<16} {'He+ (<0.3)':<14} {'Lei (>0.1)'}")
    print("-" * 90)

    constrained_taus = []
    constrained_f_H = []
    constrained_se = []

    for name, M in channels:
        idx = np.argmin(np.abs(np.array(masses) - M))
        r = results[idx]
        tau = r["tau"]
        f_h = f_H_sidm2c_v2(1.5, tau, cap=0.60)
        se = f_h ** 2 * sigma_m_phase_g8(150)

        constrained_taus.append(tau)
        constrained_f_H.append(f_h)
        constrained_se.append(se)

        he_status = "PASS" if se < 0.3 else f"FAIL({se/0.3:.1f}x)"
        lei_status = "PASS" if se > 0.1 else "FAIL"
        print(f"{name:<28} {tau:<10.4f} {f_h:<10.4f} {se:<16.4f} {he_status:<14} {lei_status}")

    # Statistics
    tau_div = max(constrained_taus) / min(constrained_taus) if min(constrained_taus) > 0 else float("inf")
    fh_div = max(constrained_f_H) / min(constrained_f_H) if min(constrained_f_H) > 0 else float("inf")
    se_div = max(constrained_se) / min(constrained_se) if min(constrained_se) > 0 else float("inf")

    print()
    print("=" * 90)
    print("Path 3 v2 verdict (R88(60))")
    print("=" * 90)
    print()
    print(f"τ diversity:      {tau_div:.2f}×")
    print(f"f_H diversity:    {fh_div:.2f}×")
    print(f"σ_eff diversity:  {se_div:.2f}×")
    print()

    if se_div >= 2.0:
        print(f"✓ Path 3 SUCCESSFULLY breaks trade-off:")
        print(f"  sigma_eff diversity {se_div:.2f}x breaks the uniform He+/Lei constraint")
        print(f"  Different halos map to different sigma_eff(150)")
        verdict = "SUCCESS"
    elif tau_div >= 2.0 and se_div < 2.0:
        print(f"⚠ Path 3 PARTIAL: tau diversity {tau_div:.2f}x but sigma_eff diversity {se_div:.2f}x")
        print(f"  Phase diversity exists but doesn't break trade-off")
        print(f"  SIDM2c f_H profile is too uniform across tau range")
        verdict = "PARTIAL"
    else:
        print(f"✗ Path 3 FAILURE: tau diversity {tau_div:.2f}x")
        verdict = "FAILURE"

    print()
    return results, verdict, tau_div, se_div


if __name__ == "__main__":
    results, verdict, tau_div, se_div = run_phase_g11_v2()
    print(f"Final: {verdict}, tau_div={tau_div:.2f}x, se_div={se_div:.2f}x")
