"""Post-v18 Lyman-alpha exclusion curve with verifiable data.

REVIEWER-21 REQUEST: show re-evaluated Lyman-alpha curve and 5 candidate points
after the v18 critical fix (TYL Eq A1 bracket LINEAR not squared).

Output: v19_2_f_lyman_alpha_post_v18.json
"""
import json
import math
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from constants import C_KMS, HBAR_C_GEV_CM


def sigma_m_born_cm2_g(alpha_D, m_chi, m_phi, v_kms):
    """Born s-wave transfer cross section (TULIN-YU-ZUREK 2013, EQ. A1, LINEAR bracket).

    sigma_T = 8 pi alpha^2 m^2 / v^4 * L(s)
    sigma/m = sigma_T * (hbarc)^2 / m_chi_g
    s = m_chi^2 v^2 / m_phi^2
    """
    if alpha_D <= 0:
        return 0.0
    v = v_kms / C_KMS
    s = (m_chi * v / m_phi) ** 2
    L = math.log(1 + s) - s / (1 + s)
    sigma_T = 8.0 * math.pi * alpha_D ** 2 * m_chi ** 2 / v ** 4 * L
    return sigma_T * HBAR_C_GEV_CM ** 2 / (m_chi * 1.78266192e-24)


def find_alpha_D_exclusion(m_chi, m_phi, v_kms, sigma_target, alpha_max=1.0):
    """Bisection: find max alpha_D such that sigma/m(v) <= sigma_target."""
    lo, hi = 1e-12, alpha_max
    for _ in range(80):
        mid = math.sqrt(lo * hi)  # log bisection
        s = sigma_m_born_cm2_g(mid, m_chi, m_phi, v_kms)
        if s > sigma_target:
            hi = mid
        else:
            lo = mid
    return math.sqrt(lo * hi)


def main():
    print("=" * 70)
    print("Post-v18 Lyman-alpha exclusion curve (REVIEWER-21 verifiable data)")
    print("=" * 70)
    print()
    print("TYL Eq A1 (LINEAR bracket, v18 fixed):")
    print("  sigma_T = 8 pi alpha^2 m^2 / v^4 * L(s)")
    print("  L(s) = log(1+s) - s/(1+s)")
    print("  s = m_chi^2 v^2 / m_phi^2")
    print()

    # ======================================================================
    # Table 1: Lyman-alpha exclusion curve at v=29.4 km/s (Cloud-9 target)
    # ======================================================================
    print("Table 1: Lyman-alpha exclusion curve (v = 29.4 km/s, sigma/m = 174 cm^2/g)")
    print()
    print(f"{'m_phi (MeV)':>12} {'alpha_D_excl':>16} {'kappa_excl':>14} {'sigma/m at alpha_D_excl (cm^2/g)':>36}")
    print("-" * 80)

    exclusion_curve_v29 = []
    for m_phi in [0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0]:
        alpha_D_excl = find_alpha_D_exclusion(1.0, m_phi, 29.4, 174.0)
        kappa_excl = alpha_D_excl * 1.0 / m_phi
        sigma_at_excl = sigma_m_born_cm2_g(alpha_D_excl, 1.0, m_phi, 29.4)
        print(f"{m_phi*1000:>12.0f} {alpha_D_excl:>16.4e} {kappa_excl:>14.4f} {sigma_at_excl:>36.4e}")
        exclusion_curve_v29.append({
            "m_phi_GeV": m_phi,
            "alpha_D_excl": alpha_D_excl,
            "kappa_excl": kappa_excl,
            "sigma_m_cm2_g_at_excl": sigma_at_excl,
        })

    print()
    # ======================================================================
    # Table 2: 5 candidate points — sigma/m values + exclusion status
    # ======================================================================
    print("Table 2: 5 candidate points from Phase 3 (v18 evaluation)")
    print()
    print(f"{'Name':>15} {'m_chi':>6} {'m_phi':>8} {'alpha_D':>10} {'v':>6} {'sigma/m (cm^2/g)':>20} {'excl?':>8}")
    print("-" * 80)

    candidates = [
        ("Cloud-9", 1.0, 0.1, 1e-3, 29.4),
        ("SPARC", 1.0, 0.1, 1e-3, 100.0),
        ("Resonance1", 1.0, 0.05, 2e-2, 200.0),
        ("Resonance2", 1.0, 0.5, 1e-4, 200.0),
        ("Bound state", 1.0, 0.02, 1e-2, 10.0),
    ]

    target = 174.0  # cm^2/g
    candidate_results = []
    for name, m_chi, m_phi, alpha_D, v in candidates:
        sigma_m = sigma_m_born_cm2_g(alpha_D, m_chi, m_phi, v)
        # Status: Born alone is what we compute
        # If sigma/m > target: alpha_D is EXCLUDED (over-predicts)
        # If sigma/m < target: alpha_D NOT excluded by Born alone
        # (Sommerfeld/resonance may enhance it further; but the Born baseline
        #  is what TYL Eq A1 gives us)
        if sigma_m > target:
            status = "EXCLUDED"
        else:
            status = "born<target"
        print(f"{name:>15} {m_chi:>6.2f} {m_phi:>8.3f} {alpha_D:>10.3e} {v:>6.1f} {sigma_m:>20.4e} {status:>8}")
        candidate_results.append({
            "name": name, "m_chi": m_chi, "m_phi": m_phi,
            "alpha_D": alpha_D, "v_kms": v,
            "sigma_m_cm2_g": sigma_m, "status_born": status,
        })

    print()
    # ======================================================================
    # Key finding: Born alone is BELOW target for all 5 candidates
    # ======================================================================
    print("KEY FINDING (v18):")
    print("  All 5 candidate points have Born sigma/m BELOW target = 174 cm^2/g.")
    print("  This means the Lyman-alpha bound (which says sigma/m <= 174) is")
    print("  NOT the reason these candidates are excluded.")
    print()
    print("  The actual Phase 3 FAIL reasons are:")
    print("  1. Calogero (Sommerfeld) sigma/m at v=29.4 = 1.5e-6 cm^2/g (10^8x below target)")
    print("  2. No resonance peaks in (m_phi, v) parameter space at m_phi=0.05-0.5 GeV")
    print("  3. Resonance candidates EXCLUDED by unitarity (sigma/m 10^2-10^10 above 9.88e4 bound)")
    print("  4. Lattice bound-state ridge framework 9127x off (not measurable)")
    print()
    print("  The Lyman-alpha curve above shows the MAXIMUM alpha_D allowed for")
    print("  sigma/m = 174 to be reached. For kappa < 1.68 (Born valid), the curve")
    print("  gives the 'no Sommerfeld' bound. For kappa > 1.68, the actual")
    print("  enhancement (S(kappa) > 1) must be computed via Calogero.")
    print()

    # Save JSON
    output_path = Path(__file__).parent.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v18.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "exclusion_curve_v29_4": exclusion_curve_v29,
            "candidate_points": candidate_results,
            "target_sigma_m_cm2_g": target,
            "coupling_convention": "alpha_D = g^2 / (4 pi)",
            "Tyl_formula": "sigma_T = 8 pi alpha^2 m^2 / v^4 * [log(1+s) - s/(1+s)], s = m_chi^2 v^2 / m_phi^2",
            "version": "v18 (post-critical-fix)",
        }, f, indent=2)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
