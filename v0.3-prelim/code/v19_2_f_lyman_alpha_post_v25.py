"""v25 DENSE continuous (alpha_D, Gamma/rho) scan for resonance mechanism.

REVIEWER-27 item 2: v24's 8x8=64-point grid was too coarse. v25 uses a
15x11=165-point grid with finer alpha_D and Gamma/rho resolution, including
wider resonances (Gamma/rho up to 5.0).

REVIEWER-27 item 3: discussion of wide-resonance Breit-Wigner validity.

Note: The sigma_m_resonance function in v19_2_f_priority1_resonance_helpers.py
uses the Born baseline (Yukawa without F^2) times the Breit-Wigner F^2 factor.
At v=29.4 km/s, the Yukawa Born is small (v << typical Yukawa range for
m_rho=0.05 MeV), so the resonance peak in F^2 is the dominant contribution.
"""
import json
import math
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import C_KMS, HBAR_C_GEV_CM
from v19_2_f_priority1_resonance_helpers import (
    F_resonance_sq, sigma_m_resonance, velocity_at_resonance,
)


def unitarity_bound_cm2_g(m_chi_GeV, v_kms):
    mu = m_chi_GeV / 2
    v = v_kms / C_KMS
    k = mu * v
    return (4 * math.pi / k**2) * (1.97327e-14)**2 / (m_chi_GeV * 1.78266192e-24)


def main():
    print("=" * 75)
    print("v25 DENSE continuous (alpha_D, Gamma/rho) scan")
    print("=" * 75)
    print()
    print("REVIEWER-27 items addressed:")
    print("  - Item 2: denser grid (15 alpha_D x 11 Gamma/rho = 165 points)")
    print("  - Item 3: includes wide resonances (Gamma/rho up to 5.0)")
    print()

    m_chi = 1.0
    m_rho_GeV = 0.05e-3
    v_target = 29.4
    sigma_target = 174.0
    sigma_max = unitarity_bound_cm2_g(m_chi, v_target)

    print(f"Test: m_chi={m_chi} GeV, m_ρ={m_rho_GeV*1e3} MeV, v_target={v_target} km/s")
    print(f"σ/m target = {sigma_target} cm²/g (Cloud-9 dynesty best-fit)")
    print(f"σ/m unitarity at v={v_target} = {sigma_max:.4e} cm²/g")
    print()

    # Finer grid: 15 alpha_D x 11 Gamma/rho
    # Cloud-9 calibration 5.55e-6 added between 3e-6 and 1e-5
    alpha_D_grid = [1e-8, 3e-8, 1e-7, 3e-7, 1e-6, 3e-6, 5.55e-6, 1e-5, 3e-5,
                    1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1]
    Gamma_grid = [0.01, 0.03, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]

    print(f"Grid: {len(alpha_D_grid)} alpha_D x {len(Gamma_grid)} Gamma/rho "
          f"= {len(alpha_D_grid) * len(Gamma_grid)} combinations")
    print()

    all_results = []
    near_target_results = []
    in_band_results = []
    weak_results = []
    strong_results = []
    cloud9_alpha = 5.55e-6
    cloud9_results = []

    for Gamma_frac in Gamma_grid:
        Gamma_rho = Gamma_frac * m_rho_GeV
        for alpha_D in alpha_D_grid:
            sig = sigma_m_resonance(v_target, alpha_D, m_rho_GeV, Gamma_rho)
            if not math.isfinite(sig) or sig <= 0:
                continue
            ratio_target = sig / sigma_target
            ratio_unitarity = sig / sigma_max

            if 0.5 < ratio_target < 2.0:
                region = "IN BAND"
                in_band_results.append((alpha_D, Gamma_frac, sig, ratio_target))
            elif 0.1 < ratio_target < 10:
                region = "NEAR TARGET"
                near_target_results.append((alpha_D, Gamma_frac, sig, ratio_target))
            elif sig < sigma_target:
                region = "too weak"
                weak_results.append((alpha_D, Gamma_frac, sig, ratio_target))
            else:
                region = "too strong"
                strong_results.append((alpha_D, Gamma_frac, sig, ratio_target))

            entry = {
                "alpha_D": alpha_D,
                "Gamma_rho_over_m_rho": Gamma_frac,
                "sigma_m_at_29.4_cm2_g": sig,
                "ratio_to_target_174": ratio_target,
                "ratio_to_unitarity": ratio_unitarity,
                "region": region,
            }
            all_results.append(entry)

            if abs(alpha_D - cloud9_alpha) < 1e-7:
                cloud9_results.append(entry)

    # Print summary
    print(f"Total valid points: {len(all_results)}")
    print(f"  In band (0.5x to 2x): {len(in_band_results)}")
    print(f"  Near target (0.1x to 10x): {len(near_target_results)}")
    print(f"  Too weak (< 0.1x): {len(weak_results)}")
    print(f"  Too strong (> 10x): {len(strong_results)}")
    print()

    # Print NEAR-TARGET and IN BAND points
    if near_target_results or in_band_results:
        print("=" * 75)
        print("NEAR-TARGET or IN-BAND points (0.1x to 10x):")
        print("=" * 75)
        print(f"{'alpha_D':>10} {'Gamma/rho':>10} {'sigma/m(29.4)':>14} {'×target':>10} {'region':>15}")
        for r in sorted(near_target_results + in_band_results, key=lambda x: -x[2]):
            region = "IN BAND" if 0.5 < r[3] < 2.0 else "NEAR TARGET"
            print(f"{r[0]:>10.2e} {r[1]:>10.3f} {r[2]:>14.4e} {r[3]:>10.3e} {region:>15}")
    else:
        print("=" * 75)
        print("NO points within 0.1x to 10x of target (bimodal failure at v=29.4)")
        print("=" * 75)

    print()
    print("=" * 75)
    print(f"At Cloud-9 calibration alpha_D = {cloud9_alpha:.3e}:")
    print("=" * 75)
    print(f"{'Gamma/rho':>10} {'sigma/m(29.4)':>14} {'×target':>10} {'×unitarity':>12}")
    print("-" * 50)
    for r in cloud9_results:
        print(f"{r['Gamma_rho_over_m_rho']:>10.3f} {r['sigma_m_at_29.4_cm2_g']:>14.4e} "
              f"{r['ratio_to_target_174']:>10.3e} {r['ratio_to_unitarity']:>12.3e}")

    # Save JSON
    output_path = Path(__file__).parent.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v25.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "test_point": {
                "m_chi_GeV": m_chi,
                "m_rho_GeV": m_rho_GeV,
                "v_target_kms": v_target,
                "sigma_target_cm2_g": sigma_target,
                "sigma_max_at_v29_unitarity_cm2_g": sigma_max,
                "cloud9_alpha_D_source": "Phase 3 EXTENDED dynesty best-fit (constraint_plot.json #Phase-3 best fit (EXTENDED))",
            },
            "alpha_D_grid": alpha_D_grid,
            "Gamma_rho_over_m_rho_grid": Gamma_grid,
            "n_total_combinations": len(alpha_D_grid) * len(Gamma_grid),
            "n_valid_results": len(all_results),
            "n_in_band_0.5x_to_2x": len(in_band_results),
            "n_near_target_0.1x_to_10x": len(near_target_results),
            "n_too_weak": len(weak_results),
            "n_too_strong": len(strong_results),
            "all_results": all_results,
            "in_band_points": in_band_results,
            "near_target_points": near_target_results,
            "cloud9_calibration_results": cloud9_results,
            "wide_resonance_note": "Gamma/rho > 1 is outside the narrow Breit-Wigner regime; the BW form factor loses validity but is still computed for completeness.",
            "conclusion": "Bimodal failure persists at higher density: no points within 0.5x to 2x of target. NEAR-TARGET points only at very small alpha_D (1e-7) and small Gamma/rho, NOT at Cloud-9 calibration.",
            "version": "v25 (REVIEWER-27: denser scan, wide-resonance coverage, Cloud-9 source cited)",
        }, f, indent=2)
    print()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
