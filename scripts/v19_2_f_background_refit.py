"""v40.48: Background refit (Yukawa parameters without the peak).

Per Nemotron 120B 8th review (v40.47): "The Yukawa background (sigma_0=0.052,
a=1.93, v_ref=100) was fitted to the Cloud-9 point *with* the peak
present, so its parameters are biased when the peak is removed. A
dedicated background refit (v40.48+) that varies sigma_0, a_slope,
and/or v_ref while keeping peak=0 is the logical next action to bring
the Yukawa contribution at v=15 km/s below the 0.8 cm^2/g limit."

REVIEWED BY (v40.48): Nemotron 3 Ultra 550B (UPGRADED from 120B)

Goal: refit the Yukawa background (sigma_0, a_slope, v_ref) with
peak=0, such that:
  1. Cloud-9 sigma/m(28) is bounded (e.g., sigma/m(28) ~ 0.5 cm^2/g
     or some target value, not too high)
  2. Fornax sigma/m(15) < 0.8 cm^2/g (dSph ceiling)
  3. SPARC sigma/m(100) ~ 0.05 cm^2/g (rotation-curve inner cores)

Three knobs:
  - sigma_0 (overall amplitude at v_ref)
  - a_slope (velocity power-law index)
  - v_ref (reference velocity)

Strategy: parameter sweep over (sigma_0, a_slope, v_ref) with peak=0.
For each triple, check if constraints (Cloud-9, Fornax, SPARC) are
satisfied.

Per R88(68) honest framing: this is an EXPLORATORY parameter sweep,
not a formal Bayesian fit. The goal is to find ANY parameter triple
that satisfies the constraints, not to find the best triple.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))
sys.path.insert(0, str(REPO / "scripts"))

# Observational constraints (target values)
TARGETS = {
    "cloud9_v_kms": 28.0,  # Cloud-9 V_max
    "cloud9_sigma_m_max": 1.0,  # Cloud-9 sigma/m(28) should be BOUNDED (not 165)
    "cloud9_sigma_m_ideal": 0.5,  # Ideal target (Yukawa-only, no peak)
    "fornax_v_kms": 15.0,  # Fornax v
    "fornax_sigma_m_max": 0.8,  # dSph ceiling
    "sparc_v_kms": 100.0,  # SPARC v
    "sparc_sigma_m_max": 0.1,  # SPARC inner core upper limit
}


def sigma_m_yukawa(v, sigma_0, a_slope, v_ref):
    """Yukawa-only sigma/m(v) (no Gaussian peak)."""
    return sigma_0 * (v_ref / v)**a_slope


def evaluate_triple(sigma_0, a_slope, v_ref):
    """Evaluate a (sigma_0, a_slope, v_ref) triple against constraints.

    Returns: dict with sigma/m at Cloud-9, Fornax, SPARC, and pass/fail.
    """
    sm_cloud9 = sigma_m_yukawa(TARGETS["cloud9_v_kms"], sigma_0, a_slope, v_ref)
    sm_fornax = sigma_m_yukawa(TARGETS["fornax_v_kms"], sigma_0, a_slope, v_ref)
    sm_sparc = sigma_m_yukawa(TARGETS["sparc_v_kms"], sigma_0, a_slope, v_ref)
    passes = {
        "cloud9_ok": sm_cloud9 < TARGETS["cloud9_sigma_m_max"],
        "fornax_ok": sm_fornax < TARGETS["fornax_sigma_m_max"],
        "sparc_ok": sm_sparc < TARGETS["sparc_sigma_m_max"],
    }
    return {
        "sigma_0": sigma_0,
        "a_slope": a_slope,
        "v_ref": v_ref,
        "sigma_m_cloud9": sm_cloud9,
        "sigma_m_fornax": sm_fornax,
        "sigma_m_sparc": sm_sparc,
        "all_ok": all(passes.values()),
        "passes": passes,
    }


def main():
    print("=" * 70)
    print("v40.48: Background refit (Yukawa parameters without the peak)")
    print("=" * 70)
    print()
    print("Per Nemotron 3 Ultra 550B 8th review (v40.47):")
    print("  'A dedicated background refit (v40.48+) that varies sigma_0,")
    print("   a_slope, and/or v_ref while keeping peak=0 is the logical")
    print("   next action to bring the Yukawa contribution at v=15 km/s")
    print("   below the 0.8 cm^2/g limit.'")
    print()
    print("REVIEWER: Nemotron 3 Ultra 550B (UPGRADED from 120B, per user directive 2026-10-19)")
    print()
    print("TARGETS (observational constraints):")
    print(f"  Cloud-9 (v=28):  sigma/m < {TARGETS['cloud9_sigma_m_max']} cm^2/g (bounded, no peak)")
    print(f"  Fornax (v=15):   sigma/m < {TARGETS['fornax_sigma_m_max']} cm^2/g (dSph ceiling)")
    print(f"  SPARC (v=100):   sigma/m < {TARGETS['sparc_sigma_m_max']} cm^2/g (rotation-curve inner core)")
    print()

    # Parameter sweep
    sigma_0_grid = [0.01, 0.03, 0.052, 0.1, 0.3]
    a_slope_grid = [1.5, 1.93, 2.5, 3.0, 4.0]
    v_ref_grid = [50.0, 100.0, 150.0]

    results = []
    for sigma_0 in sigma_0_grid:
        for a_slope in a_slope_grid:
            for v_ref in v_ref_grid:
                r = evaluate_triple(sigma_0, a_slope, v_ref)
                results.append(r)

    # Print top results (sorted by all_ok, then by Fornax sigma/m ascending)
    passing = [r for r in results if r["all_ok"]]
    print(f"Total parameter combinations: {len(results)}")
    print(f"Combinations satisfying all 3 constraints: {len(passing)}")
    print()

    if len(passing) > 0:
        print("Passing combinations (sorted by Fornax sigma/m ascending):")
        print(f"{'sigma_0':>10} {'a_slope':>8} {'v_ref':>8} {'sigma/m(28)':>12} {'sigma/m(15)':>12} {'sigma/m(100)':>12}")
        print("-" * 80)
        for r in sorted(passing, key=lambda x: x["sigma_m_fornax"])[:10]:
            print(f"{r['sigma_0']:>10.3f} {r['a_slope']:>8.2f} {r['v_ref']:>8.1f} {r['sigma_m_cloud9']:>10.4f}  {r['sigma_m_fornax']:>10.4f}  {r['sigma_m_sparc']:>10.4f}")
    else:
        print("NO passing combinations found! The constraints are mutually")
        print("exclusive under the Yukawa power-law form.")
        print()
        print("Examples (Fornax sigma/m is always > dSph ceiling at any combo):")
        # Show 5 best (smallest Fornax sigma/m)
        best = sorted(results, key=lambda x: x["sigma_m_fornax"])[:5]
        for r in best:
            print(f"  sigma_0={r['sigma_0']}, a_slope={r['a_slope']}, v_ref={r['v_ref']}: "
                  f"Fornax sigma/m = {r['sigma_m_fornax']:.3f} (vs ceiling 0.8)")

    print()
    print("=" * 70)
    print("v40.48 INTERPRETATION:")
    print("=" * 70)
    print()
    if len(passing) > 0:
        print("Some parameter combinations SATISFY all 3 constraints with peak=0.")
        print("This means the framework CAN be self-consistent with a Yukawa-only")
        print("sigma/m(v) form, provided the background parameters are refit.")
        print()
        # Find the best (lowest Fornax sigma/m while keeping Cloud-9 bounded)
        best = sorted(passing, key=lambda x: x["sigma_m_fornax"])[0]
        print(f"RECOMMENDED BACKGROUND: sigma_0 = {best['sigma_0']}, "
              f"a_slope = {best['a_slope']}, v_ref = {best['v_ref']}")
        print(f"  sigma/m(28) Cloud-9 = {best['sigma_m_cloud9']:.4f} cm^2/g")
        print(f"  sigma/m(15) Fornax  = {best['sigma_m_fornax']:.4f} cm^2/g (must be < 0.8)")
        print(f"  sigma/m(100) SPARC  = {best['sigma_m_sparc']:.4f} cm^2/g (must be < 0.1)")
    else:
        print("No parameter combination satisfies all 3 constraints.")
        print("This means the Yukawa power-law form is INSUFFICIENT to fit all")
        print("observations simultaneously -- additional physics (e.g., a different")
        print("velocity dependence, like Rutherford/Moller scattering) is needed.")
        print()
        print("Per Nemotron 3 Ultra 550B 8th review:")
        print("  'a higher a is often preferable if one wishes to preserve the Cloud-9")
        print("   normalization, but a joint refit of sigma_0 and a (or v_ref) should")
        print("   be explored to avoid degrading fits to other dSphs.'")
        print()
        print("The v40.48 sweep shows that a Yukawa-only power-law is NOT flexible")
        print("enough to fit Fornax AND SPARC AND Cloud-9 simultaneously. This")
        print("suggests the framework needs either (a) a different velocity dependence")
        print("form (e.g., Rutherford/Moller), or (b) per-channel background parameters.")

    print()
    print("=" * 70)
    print("R88(71) PRE-CLAIM CHECKLIST")
    print("=" * 70)
    print("(a) v40.48 explores whether the background refit can satisfy all 3")
    print("    constraints with peak=0.")
    print()
    print("(b) Per R88(68) lesson: this is an EXPLORATORY parameter sweep, not")
    print("    a formal fit. The result either finds a valid parameter space")
    print("    or shows that additional physics is needed.")
    print()
    print("(c) HONEST FRAMING: if no passing combination is found, the Yukawa")
    print("    power-law form is INSUFFICIENT and additional physics is needed.")
    print("    This is a STRUCTURAL finding about the framework, not a tunable.")
    print()
    print("(d) RECOMMENDATION: Send to Nemotron 3 Ultra 550B for 9th review.")

    # Save
    out_dir = REPO / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v19_2_f_background_refit_2026_10_19.json"
    out_data = {
        "method": "v40.48: Background refit (Yukawa parameters without peak)",
        "date": "2026-10-19",
        "framework": "v19.2-F Phase 44, peak DOWNGRADED to 0 (per v40.46)",
        "reviewer": "Nemotron 3 Ultra 550B (UPGRADED from 120B)",
        "targets": TARGETS,
        "parameter_grids": {
            "sigma_0_grid": sigma_0_grid,
            "a_slope_grid": a_slope_grid,
            "v_ref_grid": v_ref_grid,
        },
        "total_combinations": len(results),
        "passing_combinations": len(passing),
        "best_passing": passing[0] if len(passing) > 0 else None,
        "best_failed": best if len(passing) == 0 else None,
    }
    out.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print()
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
