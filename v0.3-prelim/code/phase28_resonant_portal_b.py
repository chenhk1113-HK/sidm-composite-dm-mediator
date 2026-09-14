"""
Phase 28 — Resonant Portal B Diagnostic (consider7 Option B)

The reviewer's consider7.docx Option B recommends replacing pure Yukawa
for Portal B with a resonance peaked near v ~ 25-30 km/s.

T90.50 resonant SIDM already implements Breit-Wigner + Sommerfeld.
The key question: can a resonance simultaneously satisfy:
  - Cloud-9: sigma/m(28) >= 30
  - SPARC: sigma/m(100) < 0.5
  - Euclid: sigma/m(150) < 0.10

Phase 28 scans (E_R, Gamma_R) for resonances and checks velocity dependence.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v50_resonant_sidm import sigma_m_resonant, kinetic_energy_eV

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 70)
    print("Phase 28 — Resonant SIDM Diagnostic (Option B from consider7.docx)")
    print("=" * 70)
    print()
    print("Question: Can a resonance at v ~ 25-30 km/s simultaneously")
    print("satisfy Cloud-9, SPARC, and Euclid subhalo?")
    print()

    # Baseline parameters from T90.51 best fit
    # (m_chi=30 GeV, E_R=65 eV, Gamma_R=0.1 eV, sigma_0=0.01, alpha_Y=0.001)
    m_chi_GeV = 30.0
    sigma_0 = 0.01
    alpha_Y = 0.001

    # Compute kinetic energy at Cloud-9 velocity
    E_28 = kinetic_energy_eV(28, m_chi_GeV)
    print(f"At v=28 km/s, m_chi=30 GeV: E_CM = {E_28:.2f} eV (resonance target)")
    print()

    # Scan over (E_R, Gamma_R)
    print("=" * 70)
    print("Scan: (E_R, Gamma_R) combinations")
    print("=" * 70)
    print()

    # E_R should be near E_28 ~ 65 eV for resonance to be at v=28
    E_R_grid = [10, 30, 50, 65, 80, 100, 200, 500, 1000]  # eV
    Gamma_R_grid = [0.01, 0.1, 1.0, 10.0, 100.0]  # eV

    results = []
    n_tested = 0

    for E_R in E_R_grid:
        for Gamma_R in Gamma_R_grid:
            n_tested += 1
            r_28 = sigma_m_resonant(28, m_chi_GeV, E_R, Gamma_R, sigma_0, alpha_Y)
            r_100 = sigma_m_resonant(100, m_chi_GeV, E_R, Gamma_R, sigma_0, alpha_Y)
            r_150 = sigma_m_resonant(150, m_chi_GeV, E_R, Gamma_R, sigma_0, alpha_Y)

            sm_28 = r_28["sigma_m_total"]
            sm_100 = r_100["sigma_m_total"]
            sm_150 = r_150["sigma_m_total"]

            cloud9_ok = sm_28 >= 30
            sparc_ok = sm_100 < 0.5
            euclid_ok = sm_150 < 0.10

            if cloud9_ok and sparc_ok and euclid_ok:
                results.append({
                    "E_R_eV": E_R,
                    "Gamma_R_eV": Gamma_R,
                    "sigma_m_28": sm_28,
                    "sigma_m_100": sm_100,
                    "sigma_m_150": sm_150,
                })

    print(f"Tested {n_tested} (E_R, Gamma_R) combinations")
    print(f"Found {len(results)} satisfying Cloud-9 + SPARC + Euclid simultaneously")
    print()

    if results:
        print("Top 5 configurations (best Cloud-9 fit):")
        results.sort(key=lambda x: -x["sigma_m_28"])
        print(f"  {'E_R':>8}  {'Gamma_R':>8}  {'sm(28)':>10}  {'sm(100)':>10}  {'sm(150)':>10}")
        for r in results[:5]:
            print(f"  {r['E_R_eV']:8.2f}  {r['Gamma_R_eV']:8.3f}  "
                  f"{r['sigma_m_28']:10.3f}  {r['sigma_m_100']:10.4f}  "
                  f"{r['sigma_m_150']:10.5f}")
    else:
        # Show the best partial fits
        print("Best partial fits (Cloud-9 satisfied, others may fail):")
        all_fits = []
        for E_R in E_R_grid:
            for Gamma_R in Gamma_R_grid:
                r_28 = sigma_m_resonant(28, m_chi_GeV, E_R, Gamma_R, sigma_0, alpha_Y)
                r_100 = sigma_m_resonant(100, m_chi_GeV, E_R, Gamma_R, sigma_0, alpha_Y)
                r_150 = sigma_m_resonant(150, m_chi_GeV, E_R, Gamma_R, sigma_0, alpha_Y)
                all_fits.append({
                    "E_R_eV": E_R,
                    "Gamma_R_eV": Gamma_R,
                    "sigma_m_28": r_28["sigma_m_total"],
                    "sigma_m_100": r_100["sigma_m_total"],
                    "sigma_m_150": r_150["sigma_m_total"],
                })
        all_fits.sort(key=lambda x: -x["sigma_m_28"])
        print(f"  {'E_R':>8}  {'Gamma_R':>8}  {'sm(28)':>10}  {'sm(100)':>10}  {'sm(150)':>10}")
        for r in all_fits[:10]:
            print(f"  {r['E_R_eV']:8.2f}  {r['Gamma_R_eV']:8.3f}  "
                  f"{r['sigma_m_28']:10.3f}  {r['sigma_m_100']:10.4f}  "
                  f"{r['sigma_m_150']:10.5f}")

    print()

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    if len(results) > 0:
        verdict = "FOUND_CONFIGURATIONS"
        print(f"  {len(results)} (E_R, Gamma_R) combinations satisfy all 3 channels!")
    else:
        verdict = "NO_CONFIGURATION_FOUND"
        print("  No (E_R, Gamma_R) satisfies Cloud-9 + SPARC + Euclid simultaneously.")
        print()
        print("  The resonance can be sharp enough to drop sigma/m at v=100-150,")
        print("  but the OFF-RESONANT background sigma/m (sigma_0 * Sommerfeld)")
        print("  is too high. Reducing sigma_0 also reduces the on-resonance peak.")
        print()
        print("  To fix this would require either:")
        print("    - Stronger velocity suppression in the background (non-Sommerfeld)")
        print("    - Multiple narrow resonances to cancel off-resonance background")
        print("    - Negative background cross-section (not physical)")

    out = {
        "test": "Phase28_resonant_portal_b",
        "baseline": {
            "m_chi_GeV": m_chi_GeV,
            "sigma_0_cm2_per_g": sigma_0,
            "alpha_Y": alpha_Y,
            "E_CM_at_v28_eV": E_28,
        },
        "scan": {
            "n_tested": n_tested,
            "n_satisfying_all_3": len(results),
        },
        "best_configs": results[:10] if results else [],
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase28_resonant_portal_b.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
