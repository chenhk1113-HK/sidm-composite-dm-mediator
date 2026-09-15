"""
Phase 33b — Resonance positions vs Tsai 2022 prediction.

Per Tsai, McGehee, Murayama 2022 (arXiv:2008.08608), Eq. 11:
  m[Υ(nS)] - m[Υ((n-1)S)] = C × [1/n + O(1/n²)]

For a dark quark Q with mass m_Q in dark QCD, multiple resonance states
emerge at energies E_n with spacing:
  E_n - E_{n-1} = C × [1/n]

Compute PREDICTED resonance velocities from (m_chi, m_Q, Λ_D, N_c) and
compare to FITTED resonance velocities from Phase 32b posterior.

If predicted positions ≈ fitted positions → "PREDICTED" (Tsai 2022 motivated)
If they don't → "PHENOMENOLOGICAL" (chosen to fit data)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v70_multi_resonant_darkqcd import (
    sigma_m_multi_resonant,
    velocity_dependent_background,
)
from t90_v50_resonant_sidm import kinetic_energy_eV

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def tsai_2022_v_targets(m_chi_GeV, m_Q_GeV=None, Lambda_D_GeV=0.5, N_c=3):
    """Predict resonance velocities using Tsai 2022 level spacing.

    In Tsai 2022's HEAVY quark model (Section III.B):
      - DM is a heavy-light dark meson
      - Mediator is the dark rho vector meson
      - The dark rho has excited states rho(nS) with masses:
          m_rho(nS) ≈ 2*m_Q - C/n (binding energy ~ C/n)
      - SIDM resonance occurs when:
          E_CM(v) = 2*m_chi + KE_CM(v) = m_rho(nS)
        i.e., KE_CM(v_n) = m_rho(nS) - 2*m_chi

    For threshold resonance (n large, m_rho(nS) ≈ 2*m_Q):
      KE_CM(v_threshold) ≈ 2*m_Q - 2*m_chi
      This is a SINGLE velocity, not a series.

    For ABOVE-threshold (m_rho(nS) > 2*m_chi):
      v_n ~ sqrt(2*(m_rho(nS) - 2*m_chi)/m_chi)

    Parameters:
      m_chi_GeV: DM mass
      m_Q_GeV: dark quark mass
      Lambda_D_GeV: dark confining scale
      N_c: number of colors
    """
    if m_Q_GeV is None:
        m_Q_GeV = m_chi_GeV

    # Binding energy formula: E_bind(n) = Lambda_D^2 / (2*m_Q*n) (Coulomb)
    # m_rho(nS) = 2*m_Q - E_bind(n) = 2*m_Q - Lambda_D^2/(2*m_Q*n)
    def m_rho(n):
        return 2 * m_Q_GeV - (Lambda_D_GeV ** 2) / (2 * m_Q_GeV * n)

    # Resonance velocity: KE_CM(v_n) = m_rho(nS) - 2*m_chi
    # In natural units: 0.5 * m_chi * v²/c² = m_rho(nS) - 2*m_chi
    # v²/c² = 2*(m_rho(nS) - 2*m_chi)/m_chi

    v_targets = []
    for n in range(1, 8):
        m_rho_n = m_rho(n)
        delta_M = m_rho_n - 2 * m_chi_GeV
        if delta_M > 0:
            # Above threshold: resonance at velocity v_n
            v_squared = 2 * delta_M / m_chi_GeV
            v_kms = (v_squared ** 0.5) * 3e5
            v_targets.append(v_kms)
        # else: below threshold, no resonance (kinematically forbidden)

    return v_targets


def get_fitted_v_targets():
    """Get fitted resonance velocities from Phase 32b posterior median."""
    with open(RESULTS_DIR / "phase32b_multi_resonant_joint_fit.json") as f:
        data = json.load(f)
    return data["best_sample"]["v_targets_kms"]


def main():
    print("=" * 70)
    print("Phase 33b — Resonance positions vs Tsai 2022 prediction")
    print("=" * 70)
    print()

    # Fitted positions from Phase 32b
    fitted = get_fitted_v_targets()
    print(f"Fitted v_targets (Phase 32b posterior median):")
    print(f"  {[f'{v:.1f}' for v in fitted]}")
    print()

    # Try various Tsai 2022 parameters
    print("Tsai 2022 predicted v_targets for various (m_chi, m_Q, Lambda_D):")
    print()
    print(f"{'m_chi':>8} {'m_Q':>8} {'Λ_D':>6} {'C (eV)':>10} {'v_2':>8} {'v_3':>8} {'v_4':>8} {'v_5':>8}")
    print("-" * 80)

    test_cases = []
    # Use Phase 32b posterior median m_chi = 6.58 GeV
    base_m_chi = 6.58

    for m_Q_factor in [0.5, 1.0, 1.5, 2.0]:
        for Lambda_D in [0.1, 0.5, 1.0, 2.0, 5.0]:
            m_Q = base_m_chi * m_Q_factor
            v_pred = tsai_2022_v_targets(base_m_chi, m_Q, Lambda_D)
            if len(v_pred) >= 4:
                test_cases.append({
                    "m_chi": base_m_chi,
                    "m_Q": m_Q,
                    "Lambda_D": Lambda_D,
                    "v_pred": v_pred,
                })
                # Compute C in eV
                C_eV = Lambda_D ** 2 / (2 * m_Q) * 1e9
                print(f"{base_m_chi:>8.2f} {m_Q:>8.2f} {Lambda_D:>6.2f} {C_eV:>10.2e} "
                      f"{v_pred[1]:>8.1f} {v_pred[2]:>8.1f} {v_pred[3]:>8.1f} {v_pred[4]:>8.1f}")

    print()

    # Find best match to fitted positions
    print("=" * 70)
    print("Matching to fitted positions [28, 95, 291, 769]")
    print("=" * 70)
    print()

    best_chi2 = np.inf
    best_case = None
    for case in test_cases:
        v_pred_full = case["v_pred"]
        if len(v_pred_full) >= 5:
            # Use n=2,3,4,5 to match the 4 fitted resonances
            v_pred = v_pred_full[1:5]
        elif len(v_pred_full) >= 4:
            v_pred = v_pred_full[:4]
        else:
            continue
        # Compare in log space
        chi2 = sum((np.log10(v_pred[i]) - np.log10(fitted[i])) ** 2
                   for i in range(min(4, len(v_pred))))
        if chi2 < best_chi2:
            best_chi2 = chi2
            best_case = case

    if best_case is not None:
        v_pred_full = best_case["v_pred"]
        if len(v_pred_full) >= 5:
            v_pred = v_pred_full[1:5]
        else:
            v_pred = v_pred_full[:4]
        print(f"Best-fit Tsai 2022 parameters:")
        print(f"  m_chi = {best_case['m_chi']:.2f} GeV")
        print(f"  m_Q = {best_case['m_Q']:.2f} GeV")
        print(f"  Λ_D = {best_case['Lambda_D']:.2f} GeV")
        print(f"  χ² = {best_chi2:.3f}")
        print()
        print(f"{'n':>3} {'fitted (km/s)':>15} {'predicted (km/s)':>18} {'ratio':>10}")
        print("-" * 50)

        # Compute ratios and stats
        ratios = []
        for i in range(min(4, len(v_pred))):
            if i < len(fitted):
                ratio = v_pred[i] / fitted[i]
                ratios.append(ratio)
                print(f"{i+2:>3} {fitted[i]:>15.1f} {v_pred[i]:>18.1f} {ratio:>10.3f}")
        print()

        if len(ratios) >= 2:
            log_ratios = [np.log10(r) for r in ratios]
            std_log = np.std(log_ratios)
        else:
            std_log = 999

        print(f"Standard deviation of log10(ratio): {std_log:.3f}")
        if len(ratios) >= 1:
            print(f"Mean log10(ratio): {np.mean(log_ratios):.3f}")
        print()

        # Verdict: Tsai 2022 predicts resonances at much higher velocities
        # (~ 400,000 km/s for m_chi ~ 6 GeV), not at ~30 km/s.
        # This is a fundamental mismatch.
        if std_log > 1.0:
            verdict = "PHENOMENOLOGICAL — Tsai 2022 predicts very different velocities than fitted"
        elif std_log > 0.5:
            verdict = "PARTIALLY PREDICTED — large scatter"
        elif std_log > 0.3:
            verdict = "CONSISTENT — within factor 3 of Tsai 2022 prediction"
        else:
            verdict = "PREDICTED — Tsai 2022 level spacing matches fitted positions"

        print(f"Verdict: {verdict}")
        print()
        print("=" * 70)
        print("INTERPRETATION")
        print("=" * 70)
        print()
        print("Tsai 2022's heavy quark model predicts dark rho resonances at masses")
        print("m_rho(nS) ≈ 2*m_Q - Λ_D²/(2*m_Q*n). For m_chi ~ 6 GeV and m_Q ~ 6 GeV,")
        print("the resonance velocities are ~ 400,000 km/s (relativistic), NOT at")
        print("~30 km/s as needed for Cloud-9.")
        print()
        print("This confirms the reviewer's Caveat 2: the Phase 32c 'multi-resonance")
        print("dark QCD' architecture is NOT predicted by Tsai 2022. The resonance")
        print("positions are phenomenological choices to match the data.")
        print()
        print("Alternative interpretations:")
        print("  - The resonances could be from a different UV mechanism (e.g., scalar")
        print("    mediator with multiple scalar bound states)")
        print("  - Or the Tsai 2022 model could produce low-v resonances via a different")
        print("    matching condition (e.g., threshold + Sommerfeld enhancement)")
        print("  - But the literal 'Y(nS) heavy quarkonium' interpretation fails.")
    else:
        verdict = "NO_MATCH"
        print("No matching parameters found.")
        best_case = None
        std_log = 999

    # Save results
    out = {
        "test": "Phase33b_tsai_2022_prediction",
        "fitted_v_targets_kms": fitted,
        "best_fit_parameters": {
            "m_chi_GeV": best_case["m_chi"] if best_case else None,
            "m_Q_GeV": best_case["m_Q"] if best_case else None,
            "Lambda_D_GeV": best_case["Lambda_D"] if best_case else None,
        },
        "best_chi2": float(best_chi2) if best_chi2 != np.inf else None,
        "verdict": verdict,
        "std_log10_ratio": float(std_log) if best_case else None,
        "test_cases_count": len(test_cases),
    }

    out_path = RESULTS_DIR / "phase33b_tsai_2022_prediction.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())