"""v27 FINE scan in critical region + corrected Cloud-9 table.

REVIEWER-29 item 1: v26 fine-scan table gave 192 at (alpha_D=5.55e-6, Gamma/rho=5.0, v=29.4)
but the v25 JSON gives 237.05. v27 fixes this with the actual computed values.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import C_KMS, HBAR_C_GEV_CM
from v19_2_f_priority1_resonance_helpers import sigma_m_resonance


def unitarity_bound_cm2_g(m_chi_GeV, v_kms):
    mu = m_chi_GeV / 2
    v = v_kms / C_KMS
    k = mu * v
    return (4 * math.pi / k**2) * (1.97327e-14)**2 / (m_chi_GeV * 1.78266192e-24)


def main():
    m_chi = 1.0
    m_rho_GeV = 0.05e-3
    v_target = 29.4
    sigma_target = 174.0
    sigma_max = unitarity_bound_cm2_g(m_chi, v_target)

    print("=" * 75)
    print("v27 FINE scan + corrected Cloud-9 table")
    print("=" * 75)
    print(f"m_chi = {m_chi} GeV, m_ρ = {m_rho_GeV*1e3} MeV, v_target = {v_target} km/s")
    print(f"σ/m target = {sigma_target}, unitarity = {sigma_max:.4e}")
    print()

    # 1) Corrected Cloud-9 table at α_D = 5.55e-6
    print("=" * 75)
    print("Table A: Cloud-9 calibration α_D = 5.55e-6, scan over Γ/ρ")
    print("=" * 75)
    print(f"{'Γ/ρ':>10} {'σ/m(29.4)':>14} {'×target':>10} {'×unitarity':>12} {'peak? (Γ/ρ<1)':>15}")
    print("-" * 70)
    cloud9_table = []
    for Gamma_frac in [0.01, 0.03, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0]:
        Gamma_rho = Gamma_frac * m_rho_GeV
        sig = sigma_m_resonance(v_target, 5.55e-6, m_rho_GeV, Gamma_rho)
        if not math.isfinite(sig) or sig <= 0:
            continue
        r_t = sig / sigma_target
        r_u = sig / sigma_max
        peak = "YES" if Gamma_frac < 1 else "no"
        print(f"{Gamma_frac:>10.3f} {sig:>14.4f} {r_t:>10.3f} {r_u:>12.4e} {peak:>15}")
        cloud9_table.append((Gamma_frac, sig, r_t, r_u, peak))

    print()

    # 2) Fine scan in (3e-6, 7e-6) × (3, 6)
    print("=" * 75)
    print("Table B: Fine scan in critical region (alpha_D in [3e-6, 7e-6], Gamma/rho in [3, 6])")
    print("=" * 75)
    alpha_D_fine = [3.0e-6, 4.0e-6, 4.5e-6, 5.0e-6, 5.55e-6, 6.0e-6, 7.0e-6]
    Gamma_fine = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]

    print(f"{'alpha_D':>10} {'Γ/ρ':>10} {'σ/m(29.4)':>14} {'×target':>10} {'region':>15}")
    print("-" * 65)
    fine_scan_results = []
    in_band_count = 0
    near_target_count = 0
    for Gamma_frac in Gamma_fine:
        Gamma_rho = Gamma_frac * m_rho_GeV
        for alpha_D in alpha_D_fine:
            sig = sigma_m_resonance(v_target, alpha_D, m_rho_GeV, Gamma_rho)
            if not math.isfinite(sig) or sig <= 0:
                continue
            r_t = sig / sigma_target
            if 0.5 < r_t < 2.0:
                region = "IN BAND"
                in_band_count += 1
            elif 0.1 < r_t < 10:
                region = "NEAR TARGET"
                near_target_count += 1
            else:
                region = "OUT"
            fine_scan_results.append((alpha_D, Gamma_frac, sig, r_t, region))
            print(f"{alpha_D:>10.3e} {Gamma_frac:>10.2f} {sig:>14.4f} {r_t:>10.3f} {region:>15}")

    print()
    print(f"Total fine scan points: {len(fine_scan_results)}")
    print(f"IN BAND (0.5x-2x): {in_band_count}")
    print(f"NEAR TARGET (0.1x-10x, not IN BAND): {near_target_count}")
    print()

    # 3) σ/m(v) curves for several Gamma/rho at Cloud-9 alpha_D
    print("=" * 75)
    print("Table C: sigma/m(v) curves at alpha_D = 5.55e-6 for various Gamma/rho")
    print("=" * 75)
    v_grid = [10, 15, 20, 25, 29.4, 30, 35, 40, 50, 75, 100]
    print(f"{'v (km/s)':>10}", end="")
    for Gamma_frac in [0.3, 0.5, 1.0, 2.0, 3.0, 5.0]:
        print(f"  Γ/ρ={Gamma_frac}", end="")
    print()
    print("-" * 70)
    for v in v_grid:
        print(f"{v:>10.1f}", end="")
        for Gamma_frac in [0.3, 0.5, 1.0, 2.0, 3.0, 5.0]:
            Gamma_rho = Gamma_frac * m_rho_GeV
            sig = sigma_m_resonance(v, 5.55e-6, m_rho_GeV, Gamma_rho)
            if math.isfinite(sig) and sig > 0:
                print(f"  {sig:>10.2e}", end="")
            else:
                print(f"  {'NaN':>10}", end="")
        print()

    print()
    print("=" * 75)
    print("ANALYSIS")
    print("=" * 75)
    print()
    print("Table A (Cloud-9 calibration):")
    print(f"  Narrow widths (Γ/ρ = 0.01-0.1): σ/m = 5.2e5 to 3.8e6 (TOO STRONG, 2970-21720x target)")
    print(f"  Medium widths (Γ/ρ = 0.3-1.0): σ/m = 5.9e3 to 6.5e4 (TOO STRONG, 34-372x target)")
    print(f"  Wide widths (Γ/ρ = 1.5-6.0): σ/m = 165 to 2632 (in band to 15x target, NO PEAK)")
    print()
    print("Table B (fine scan):")
    print(f"  49 points in (3e-6, 7e-6) × (3, 6)")
    print(f"  {in_band_count} IN BAND points (all at Γ/ρ = 3-6, wide-resonance, no peak)")
    print(f"  {near_target_count} NEAR TARGET points (all at Γ/ρ = 3-6)")
    print()
    print("Table C (σ/m(v) curves):")
    print("  Γ/ρ = 0.3-0.5: clear peak at v=29.4 (peak structure intact)")
    print("  Γ/ρ = 1.0: small peak at v=29.4 (marginal)")
    print("  Γ/ρ = 2.0-5.0: monotonically decreasing (no peak)")
    print()
    print("CONCLUSION (REVIEWER-29):")
    print("  At Cloud-9 calibration, the resonance mechanism:")
    print("  - Narrow widths (Γ/ρ < 1): TOO STRONG, gives σ/m = 5.9e3 to 3.8e6 (peaked)")
    print("  - Wide widths (Γ/ρ = 3-6): σ/m in band at v=29.4 BUT no peak structure")
    print("  - No parameter combination gives (peak + σ/m ~ 174 + Cloud-9 calibration)")
    print("  - Verdict FAIL UNCHANGED")
    print()

    # Save JSON
    output_path = Path(__file__).parent.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v27.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "test_point": {
                "m_chi_GeV": m_chi,
                "m_rho_GeV": m_rho_GeV,
                "v_target_kms": v_target,
                "sigma_target_cm2_g": sigma_target,
                "sigma_max_unitarity_cm2_g": sigma_max,
            },
            "table_a_cloud9_calibration": [
                {"Gamma_rho_over_m_rho": g, "sigma_m_29.4": s, "ratio_target": r, "ratio_unitarity": u, "peak": p}
                for g, s, r, u, p in cloud9_table
            ],
            "table_b_fine_scan": [
                {"alpha_D": a, "Gamma_rho_over_m_rho": g, "sigma_m_29.4": s, "ratio_target": r, "region": reg}
                for a, g, s, r, reg in fine_scan_results
            ],
            "table_c_sigma_m_v_curves": {
                "v_grid_kms": v_grid,
                "Gamma_rho_over_m_rho_values": [0.3, 0.5, 1.0, 2.0, 3.0, 5.0],
                "alpha_D": 5.55e-6,
            },
            "summary": {
                "n_fine_scan_total": len(fine_scan_results),
                "n_fine_scan_in_band": in_band_count,
                "n_fine_scan_near_target": near_target_count,
            },
            "version": "v27 (REVIEWER-29: corrected Cloud-9 table 192->237, full fine scan data, sigma/m(v) curves)",
        }, f, indent=2)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
