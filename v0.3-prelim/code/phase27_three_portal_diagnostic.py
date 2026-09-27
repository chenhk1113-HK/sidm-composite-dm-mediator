"""
Phase 27 — Three-Portal Architecture Diagnostic (consider7 Option A)

The reviewer's consider7.docx Option A recommends adding a third portal
(Portal C, m_phi_C ~ few-hundred MeV) to suppress sigma/m at v=100-150
km/s while keeping Portal B for Cloud-9.

Phase 27 tests this architecture via parameter scan:
- Keep T90.45 multi-portal (Portal A + Portal B) as fixed baseline
- Add Portal C with intermediate mass (200-500 MeV)
- Scan (g_chi_C, m_phi_C, m_chi_C) to find configurations that satisfy:
  - Cloud-9: sigma/m(28) >= 30 (Portal B must dominate at low v)
  - SPARC: sigma/m(100) <= 0.5 (Portal C must cancel at v=100)
  - Euclid: sigma/m(150) <= 0.10 (Portal A heavy, no contribution)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import t40_yukawa_sigma_m as yukawa

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def sigma_m_three_portal(v_kms,
                          m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                          m_phi_B_MeV, m_chi_B_GeV, g_chi_B,
                          m_phi_C_MeV, m_chi_C_GeV, g_chi_C):
    """Total sigma/m from three portals (additive Yukawa).

    NOTE: Portal C with the SAME SIGN as Portal A would add to sigma/m.
    For SPARC cancellation, we need Portal C to SUBTRACT or be very small
    at v=100. Since Yukawa is always positive, true cancellation requires
    destructive interference in the amplitude (not the cross-section).

    This implementation is a heuristic: we test whether adding a third
    portal contribution can shift sigma/m at intermediate velocities.
    A proper quantum-mechanical treatment would require amplitude-level
    interference, which is beyond this scan.
    """
    sm_A = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A)
    sm_B = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    sm_C = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_C_MeV, m_chi_C_GeV, g_chi_C)
    # Simple additive (no destructive interference in this approximation)
    return sm_A + sm_B + sm_C


def main():
    # Load T90.45 results for Portal A + B baseline
    t90_45_path = RESULTS_DIR / "t90_v45_multi_portal_joint_fit_nlive200.json"
    with open(t90_45_path) as f:
        t90_45 = json.load(f)

    p = t90_45["median_physical"]
    m_phi_A = p["m_phi_A_MeV"]
    m_chi_A = p["m_chi_A_GeV"]
    g_chi_A = p["g_chi_A"]
    m_phi_B = p["m_phi_B_MeV"]
    m_chi_B = p["m_chi_B_GeV"]
    g_chi_B = p["g_chi_B"]

    print("=" * 70)
    print("Phase 27 — Three-Portal Architecture Diagnostic")
    print("=" * 70)
    print(f"\nBaseline (T90.45 median, 2 portals):")
    print(f"  Portal A: m_phi_A={m_phi_A:.1f} MeV, m_chi_A={m_chi_A:.2f} GeV, g_chi_A={g_chi_A:.3f}")
    print(f"  Portal B: m_phi_B={m_phi_B:.2f} MeV, m_chi_B={m_chi_B:.1f} GeV, g_chi_B={g_chi_B:.3f}")
    print()

    # 1. Baseline 2-portal sigma/m values
    sm_A_28 = yukawa.sigma_m_cm2_per_g(28, m_phi_A, m_chi_A, g_chi_A)
    sm_B_28 = yukawa.sigma_m_cm2_per_g(28, m_phi_B, m_chi_B, g_chi_B)
    sm_A_100 = yukawa.sigma_m_cm2_per_g(100, m_phi_A, m_chi_A, g_chi_A)
    sm_B_100 = yukawa.sigma_m_cm2_per_g(100, m_phi_B, m_chi_B, g_chi_B)
    sm_A_150 = yukawa.sigma_m_cm2_per_g(150, m_phi_A, m_chi_A, g_chi_A)
    sm_B_150 = yukawa.sigma_m_cm2_per_g(150, m_phi_B, m_chi_B, g_chi_B)

    print("Baseline 2-portal sigma/m values:")
    print(f"  sm(28)  = sm_A + sm_B = {sm_A_28:.3f} + {sm_B_28:.3f} = {sm_A_28 + sm_B_28:.3f}")
    print(f"  sm(100) = sm_A + sm_B = {sm_A_100:.3f} + {sm_B_100:.3f} = {sm_A_100 + sm_B_100:.3f}")
    print(f"  sm(150) = sm_A + sm_B = {sm_A_150:.4f} + {sm_B_150:.4f} = {sm_A_150 + sm_B_150:.4f}")
    print()

    # 2. Honest assessment: ADDITIVE portals can't CANCEL sigma/m
    #    Because Yukawa cross-section is always positive.
    #    Adding Portal C will ALWAYS INCREASE sigma/m at every velocity.
    print("=" * 70)
    print("HONEST PHYSICS CHECK: Can Portal C reduce sigma/m at v=100-150?")
    print("=" * 70)
    print()
    print("Yukawa cross-section is ALWAYS POSITIVE.")
    print("Adding a third portal contribution ALWAYS INCREASES sigma/m(v).")
    print()
    print("For SPARC/Euclid cancellation, we would need:")
    print("  - DESTRUCTIVE INTERFERENCE in the scattering amplitude (not cross-section)")
    print("  - Or a NEGATIVE contribution (not physical for Yukawa)")
    print()
    print("Conclusion: A third additive Yukawa portal CANNOT suppress sigma/m")
    print("at v=100-150 while keeping high sigma/m at v=28.")
    print()

    # 3. Demonstrate with scan
    print("=" * 70)
    print("Scan: Does ANY Portal C reduce sm(100) below baseline?")
    print("=" * 70)
    print()
    print("Scanning Portal C over (m_phi_C, g_chi_C)...")
    print()

    baseline_sm100 = sm_A_100 + sm_B_100  # ~3.91 cm^2/g
    baseline_sm150 = sm_A_150 + sm_B_150  # ~1.33 cm^2/g

    found_sm100_lower = False
    found_sm150_lower = False

    m_phi_C_grid = [100, 200, 300, 500, 700, 1000]  # MeV
    g_chi_C_grid = [0.1, 0.3, 0.5, 1.0, 1.5, 2.0]
    m_chi_C_grid = [0.5, 5.0, 50.0, 500.0]  # GeV

    best_sm100 = baseline_sm100
    best_sm150 = baseline_sm150
    best_cfg = None

    n_tested = 0
    n_sm100_lower = 0
    n_sm150_lower = 0

    for m_phi_C in m_phi_C_grid:
        for g_chi_C in g_chi_C_grid:
            for m_chi_C in m_chi_C_grid:
                n_tested += 1
                # Compute total sigma/m with this Portal C added
                sm_28_total = sigma_m_three_portal(
                    28, m_phi_A, m_chi_A, g_chi_A,
                    m_phi_B, m_chi_B, g_chi_B,
                    m_phi_C, m_chi_C, g_chi_C,
                )
                sm_100_total = sigma_m_three_portal(
                    100, m_phi_A, m_chi_A, g_chi_A,
                    m_phi_B, m_chi_B, g_chi_B,
                    m_phi_C, m_chi_C, g_chi_C,
                )
                sm_150_total = sigma_m_three_portal(
                    150, m_phi_A, m_chi_A, g_chi_A,
                    m_phi_B, m_chi_B, g_chi_B,
                    m_phi_C, m_chi_C, g_chi_C,
                )

                if sm_100_total < baseline_sm100:
                    n_sm100_lower += 1
                if sm_150_total < baseline_sm150:
                    n_sm150_lower += 1

                if sm_100_total < best_sm100:
                    best_sm100 = sm_100_total
                    best_sm150 = sm_150_total
                    best_cfg = (m_phi_C, m_chi_C, g_chi_C, sm_28_total, sm_100_total, sm_150_total)

    print(f"Tested {n_tested} Portal C configurations")
    print(f"  Configs reducing sm(100): {n_sm100_lower}/{n_tested}")
    print(f"  Configs reducing sm(150): {n_sm150_lower}/{n_tested}")
    print()
    if best_cfg:
        m_phi_C, m_chi_C, g_chi_C, sm28, sm100, sm150 = best_cfg
        print(f"Best (lowest sm(100)) Portal C: m_phi_C={m_phi_C} MeV, m_chi_C={m_chi_C} GeV, g_chi_C={g_chi_C}")
        print(f"  sm(28)  = {sm28:.3f} cm^2/g (baseline: {sm_A_28+sm_B_28:.3f})")
        print(f"  sm(100) = {sm100:.3f} cm^2/g (baseline: {baseline_sm100:.3f})")
        print(f"  sm(150) = {sm150:.4f} cm^2/g (baseline: {baseline_sm150:.4f})")
    print()

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    if n_sm100_lower == 0 and n_sm150_lower == 0:
        verdict = "ADDITIVE_PORTAL_C_CANNOT_REDUCE_SIGMA_M"
        print("  ADDITIVE 3-portal architecture CANNOT suppress sigma/m at v=100-150")
        print("  while keeping high sigma/m at v=28 (Cloud-9).")
        print()
        print("  This is because Yukawa cross-sections are always positive.")
        print("  Adding a third portal ALWAYS increases sigma/m at every velocity.")
        print()
        print("  To get destructive interference (sigma/m reduction), one would")
        print("  need to compute the FULL scattering amplitude with portal mixing,")
        print("  not just the incoherent sum of cross-sections.")
    else:
        verdict = "PARTIAL_REDUCTION_FOUND"
        print(f"  {n_sm100_lower} configs reduce sm(100), {n_sm150_lower} reduce sm(150)")
        print("  But these reductions are modest (Yukawa always positive).")

    out = {
        "test": "Phase27_three_portal_diagnostic",
        "baseline_2portal": {
            "sigma_m_28": sm_A_28 + sm_B_28,
            "sigma_m_100": baseline_sm100,
            "sigma_m_150": baseline_sm150,
        },
        "scan": {
            "n_tested": n_tested,
            "n_sm100_lower": n_sm100_lower,
            "n_sm150_lower": n_sm150_lower,
        },
        "best_config": {
            "m_phi_C_MeV": best_cfg[0] if best_cfg else None,
            "m_chi_C_GeV": best_cfg[1] if best_cfg else None,
            "g_chi_C": best_cfg[2] if best_cfg else None,
            "sigma_m_28": best_cfg[3] if best_cfg else None,
            "sigma_m_100": best_cfg[4] if best_cfg else None,
            "sigma_m_150": best_cfg[5] if best_cfg else None,
        } if best_cfg else None,
        "verdict": verdict,
        "honest_physics_note": (
            "Yukawa cross-sections are always positive. Adding a third "
            "additive portal contribution always INCREASES sigma/m. To "
            "get destructive interference (sigma/m reduction at intermediate "
            "velocities), one needs amplitude-level treatment with portal "
            "mixing, not incoherent cross-section sum."
        ),
    }

    out_path = RESULTS_DIR / "phase27_three_portal_diagnostic.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
