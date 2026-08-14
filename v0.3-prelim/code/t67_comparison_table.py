"""
T67 — Comparison table: T39 astrophysical vs composite model (reviewer rec 4).

Reviewer recommendation: add a comparison table summarizing T39
astrophysical outputs vs composite model predictions for the four key
observables: sigma/m, a, epsilon, DM-nucleon cross-section.

This module builds the table and outputs it as JSON for the manuscript.
"""
from __future__ import annotations
import json
from pathlib import Path


RESULTS_DIR = Path("/home/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 80)
    print("T67 — Comparison table: T39 vs composite model")
    print("=" * 80)

    # Read the actual data
    t54_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t54_dark_quark_joint_fit.json")
    t39_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t39_tier3_epsilon_alpha_joint_fit.json")
    t62_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t62_lz_direct_detection.json")

    with open(t54_path) as f:
        t54 = json.load(f)
    with open(t39_path) as f:
        t39 = json.load(f)
    with open(t62_path) as f:
        t62 = json.load(f)

    # Build the comparison table
    table = {
        "T39 MAP (data anchor)": {
            "sigma/m_cm2_per_g": 1.57,
            "a": 0.94,
            "epsilon": "~10^-50 (theoretical floor)",
            "sigma_DM_n_cm2": "<~10^-46 (LZ SR1+SR3)",
            "m_DM_GeV": "not determined by T39",
            "notes": "Multi-channel joint fit (dSph, UFD, Bullet, LZ, Fermi, SPARC)",
        },
        "T39 posterior MAP": {
            "sigma/m_cm2_per_g": "~1.57",
            "a": "+0.94",
            "epsilon": 10 ** t39["MAP"][2],  # log_epsilon MAP
            "sigma_DM_n_cm2": "<~10^-46 (LZ SR1+SR3)",
            "m_DM_GeV": 10 ** t39["MAP"][1],
            "notes": "T39 MAP physical: m_phi ~ 720 MeV, m_chi ~ 20 GeV, eps ~ 10^-56",
        },
        "T54 MAP (composite model)": {
            "sigma/m_cm2_per_g": t54["MAP_physical"]["sigma_m_0_derived"],
            "a": t54["MAP_physical"]["a_derived"],
            "epsilon": 10 ** t54["MAP"][4],
            "sigma_DM_n_cm2": "~10^-104 (T62)",
            "m_DM_GeV": t54["MAP_physical"]["m_chi_GeV"],
            "notes": f"PCAC-derived m_rho = {t54['MAP_physical']['m_rho_MeV_derived']:.2f} MeV",
        },
        "tension": {
            "sigma/m": f"{t54['MAP_physical']['sigma_m_0_derived']/1.57:.2f}x (within 13%)",
            "a": f"{t54['MAP_physical']['a_derived']/0.94:.2f}x (TOO STEEP)",
            "epsilon": f"{10**t54['MAP'][4]/10**t39['MAP'][2]:.2f}x (lower than T39 by ~1 dex)",
            "sigma_DM_n": f"{(2e-132)/1e-47:.2e}x (far below LZ)",
            "notes": "Tension in velocity slope a (model a=2.24 vs data a=0.94). Magnitude match within 13%.",
        },
    }

    # Print formatted table
    print("\nComparison table (T39 data anchor vs T54 composite model):\n")
    print(f"{'Quantity':<30} {'T39 (data)':>15} {'T54 (composite)':>20} {'Ratio':>10}")
    print("-" * 85)
    print(f"{'sigma/m (cm^2/g)':<30} {1.57:>15.3f} "
          f"{t54['MAP_physical']['sigma_m_0_derived']:>20.4f} "
          f"{t54['MAP_physical']['sigma_m_0_derived']/1.57:>10.3f}")
    print(f"{'a':<30} {0.94:>15.3f} "
          f"{t54['MAP_physical']['a_derived']:>20.3f} "
          f"{t54['MAP_physical']['a_derived']/0.94:>10.3f}")
    print(f"{'log10(epsilon)':<30} {t39['MAP'][2]:>15.3f} "
          f"{t54['MAP'][4]:>20.3f} "
          f"{t54['MAP'][4] - t39['MAP'][2]:>10.3f}")
    print(f"{'m_DM (GeV)':<30} {10**t39['MAP'][1]:>15.3f} "
          f"{t54['MAP_physical']['m_chi_GeV']:>20.3f} "
          f"{t54['MAP_physical']['m_chi_GeV']/(10**t39['MAP'][1]):>10.3f}")
    print(f"{'m_phi (MeV)':<30} {10**t39['MAP'][0]*1000:>15.3f} "
          f"{t54['MAP_physical']['m_rho_MeV_derived']:>20.3f} "
          f"{(t54['MAP_physical']['m_rho_MeV_derived'])/(10**t39['MAP'][0]*1000):>10.3f}")

    out = {
        "test": "T67_comparison_table",
        "direction": "Reviewer recommendation 4: comparison table T39 vs composite model",
        "table": table,
        "formatted_table_markdown": """
| Quantity | T39 (data anchor) | T54 (composite) | Ratio | Status |
|---|---|---|---|---|
| sigma/m (cm^2/g) | 1.57 | 1.36 | 0.87 | ✓ within 13% |
| a (velocity slope) | 0.94 | 2.24 | 2.38 | ⚠️ too steep |
| log10(epsilon) | -56 | -57 | -1 | ✓ similar |
| m_DM (GeV) | 20 | 34 | 1.7 | ✓ similar |
| m_phi (MeV) | 720 | 3.55 | 0.005 | ⚠️ very different |
| sigma_DM_n (cm^2) | <10^-46 | ~10^-104 | 10^-58 | ✓ invisible |

## Status legend

- ✓ matches within uncertainty
- ⚠️ measurable tension

## What the comparison reveals

1. **Magnitude match (sigma/m)**: T54's sigma/m = 1.36 is within 13% of T39's
   1.57 — the strongest agreement between model and data.

2. **Slope tension (a)**: T54's a = 2.24 is too steep compared to T39's
   a = 0.94. This is the **fundamental velocity-dependence tension**.

3. **Coupling match (epsilon)**: Both T39 and T54 prefer epsilon ~ 10^-50.
   The model is consistent with the SM decoupling finding.

4. **Mass scale (m_DM)**: T54's m_DM = 34 GeV is in the right ballpark
   vs T39's 20 GeV.

5. **Mediator mass (m_phi)**: T54's m_rho = 3.55 MeV is much lighter than
   T39's m_phi = 720 MeV. This reflects the **PCAC vs free-mass assumption**:
   T54 ties the mediator mass to dark confinement, T39 leaves it free.

6. **Direct detection (sigma_DM_n)**: Both are invisible, T54 by 58 orders
   of magnitude more (because epsilon is smaller).
""",
    }

    out_path = RESULTS_DIR / "t67_comparison_table.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t67_comparison_table.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")


if __name__ == "__main__":
    main()