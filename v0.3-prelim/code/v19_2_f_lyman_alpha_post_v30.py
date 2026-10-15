"""v30 CORRECTED extended alpha_D scan + full data.

REVIEWER-32 item 1 (HIGH): v29 §7 Gamma/rho=5.0 table had values off by
factor 183 from correct alpha_D^2 scaling. v30 fixes with actually computed values.
Also embeds the script for independent verification (REVIEWER-32 item 1, 6).
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import C_KMS, HBAR_C_GEV_CM
from v19_2_f_priority1_resonance_helpers import sigma_m_resonance


# === Fixed physical parameters (REVIEWER-32 item 4) ===
M_CHI_GEV = 1.0          # dark matter mass
M_RHO_GEV = 0.05e-3      # dark rho mass (50 keV, v_res = 29.98 km/s)
M_PHI_GEV = 200e-9       # NOT used in resonance (Yukawa m = m_rho)
V_TARGET_KMS = 29.4
SIGMA_TARGET = 174.0     # cm^2/g


def unitarity_bound(m_chi_GeV, v_kms):
    """sigma_max = 4 pi / k^2 (Born-unitarity, velocity-dependent)."""
    mu = m_chi_GeV / 2
    v = v_kms / C_KMS
    k = mu * v
    return (4 * math.pi / k**2) * HBAR_C_GEV_CM**2 / (m_chi_GeV * 1.78266192e-24)


def main():
    sigma_max = unitarity_bound(M_CHI_GEV, V_TARGET_KMS)
    print("=" * 75)
    print("v30 CORRECTED extended alpha_D scan")
    print("=" * 75)
    print()
    print("FIXED PHYSICAL PARAMETERS (REVIEWER-32 item 4):")
    print(f"  m_chi (dark matter)        = {M_CHI_GEV} GeV")
    print(f"  m_rho (dark rho meson)     = {M_RHO_GEV*1e3} MeV")
    print(f"  v_resonance                = {C_KMS * M_RHO_GEV / (M_CHI_GEV/2):.4f} km/s")
    print(f"  v_target                   = {V_TARGET_KMS} km/s")
    print(f"  sigma/m target             = {SIGMA_TARGET} cm^2/g")
    print(f"  sigma/m unitarity at v={V_TARGET_KMS} = {sigma_max:.4e} cm^2/g")
    print()
    print("Coupling convention: alpha_D = g^2/(4 pi) [LOCKED]")
    print()

    # Full alpha_D scan at multiple Gamma/rho
    results = {}
    for Gamma_frac in [0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]:
        Gamma_rho = Gamma_frac * M_RHO_GEV
        scan = []
        for alpha_D in [1e-10, 1e-8, 1e-7, 3e-7, 1e-6, 3e-6, 5.55e-6, 1e-5,
                        3e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e+0]:
            sig = sigma_m_resonance(V_TARGET_KMS, alpha_D, M_RHO_GEV, Gamma_rho)
            if math.isfinite(sig) and sig > 0:
                r_t = sig / SIGMA_TARGET
                if 0.5 < r_t < 2.0:
                    region = "IN BAND"
                elif 0.1 < r_t < 10.0:
                    region = "NEAR TARGET"
                else:
                    region = "OUT"
                scan.append((alpha_D, sig, r_t, region))
        results[Gamma_frac] = scan

    # Print each Gamma/rho table
    for Gamma_frac, scan in results.items():
        print(f"Gamma/rho={Gamma_frac}:")
        print(f'{"alpha_D":>12} {"sigma/m":>14} {"x target":>10} {"region":>15}')
        for alpha_D, sig, r_t, region in scan:
            print(f"  {alpha_D:>10.2e} {sig:>14.4e} {r_t:>10.3e} {region:>15}")
        print()

    # Identify IN BAND at Cloud-9 calibration for each Gamma/rho
    print("=" * 75)
    print("IN BAND points at Cloud-9 calibration (alpha_D = 5.55e-6):")
    print("=" * 75)
    print(f'{"Gamma/rho":>10} {"sigma/m":>14} {"x target":>10} {"IN BAND?":>10}')
    for Gamma_frac, scan in results.items():
        # Find the entry closest to alpha_D = 5.55e-6
        for alpha_D, sig, r_t, region in scan:
            if abs(alpha_D - 5.55e-6) < 1e-7:
                print(f'{Gamma_frac:>10.2f} {sig:>14.4e} {r_t:>10.3e} {region:>10}')
                break

    # Verify alpha_D^2 scaling
    print()
    print("=" * 75)
    print("alpha_D^2 scaling verification (at Gamma/rho=5.0):")
    print("=" * 75)
    Gamma_frac = 5.0
    Gamma_rho = Gamma_frac * M_RHO_GEV
    ref_sig = None
    ref_alpha = None
    for alpha_D in [1e-10, 1e-7, 1e-6, 1e-5, 5.55e-6, 1e-4, 1e-3, 1e-2, 1e-1]:
        sig = sigma_m_resonance(V_TARGET_KMS, alpha_D, M_RHO_GEV, Gamma_rho)
        if ref_sig is None and abs(alpha_D - 1e-5) < 1e-9:
            ref_sig = sig
            ref_alpha = alpha_D
        if ref_sig is not None and abs(alpha_D - ref_alpha) > 1e-9:
            predicted = ref_sig * (alpha_D / ref_alpha) ** 2
            ratio = sig / predicted
            print(f"  alpha_D={alpha_D:.2e}: actual={sig:.4e}, predicted={predicted:.4e}, ratio={ratio:.6f}")

    # Save JSON
    output_path = Path(__file__).parent.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v30.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "fixed_parameters": {
                "m_chi_GeV": M_CHI_GEV,
                "m_rho_GeV": M_RHO_GEV,
                "v_resonance_kms": C_KMS * M_RHO_GEV / (M_CHI_GEV / 2),
                "v_target_kms": V_TARGET_KMS,
                "sigma_target_cm2_g": SIGMA_TARGET,
                "sigma_max_unitarity_cm2_g": sigma_max,
                "coupling_convention": "alpha_D = g^2/(4 pi), LOCKED",
            },
            "alpha_D_grid": [1e-10, 1e-8, 1e-7, 3e-7, 1e-6, 3e-6, 5.55e-6, 1e-5,
                              3e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e+0],
            "Gamma_rho_over_m_rho_grid": [0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "all_scan_results": {
                str(Gamma_frac): [
                    {"alpha_D": a, "sigma_m_29.4": s, "ratio_target": r, "region": reg}
                    for a, s, r, reg in scan
                ]
                for Gamma_frac, scan in results.items()
            },
            "version": "v30 (REVIEWER-32 corrected alpha_D^2 scaling, embedded code)",
        }, f, indent=2)
    print()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
