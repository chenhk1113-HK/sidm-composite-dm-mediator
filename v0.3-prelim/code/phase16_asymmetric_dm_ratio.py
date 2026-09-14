"""
Phase 16 — Probe: Asymmetric DM baryon-to-DM ratio

If Majorana χ is the matter-asymmetric component, the DM density
η_DM (n_DM/s at present) should track the baryon asymmetry η_B
through some common generation mechanism (Affleck-Dine, leptogenesis, etc.).

Current observed values:
  η_B = n_B - n_Bbar / s = (6.12 ± 0.04) × 10⁻¹⁰ (PDG 2024)
  η_DM = n_DM / s = Ω_DM ρ_c / (m_chi s) = (5.36 × 10⁻⁵) / m_chi_GeV × ρ_c/s

Question: does the v0.3-prelim Majorana reframe at g_D ~ 0.7
predict a consistent η_DM / η_B ratio when combined with the
asymmetric DM pathway from Phase 11?
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Cosmological parameters (PDG 2024)
OMEGA_DM_H2 = 0.120            # Dark matter relic density (Planck)
OMEGA_B_H2 = 0.0224            # Baryon density
HUBBLE_CONSTANT = 67.4         # km/s/Mpc
CRITICAL_DENSITY = 8.5e-27     # kg/m³ (at H0=67.4)
S_NEPRESENT = 2.5e-9           # Comoving entropy density in m⁻³ (rough)

# Conversion: ρ_c = 1.878e-26 h² kg/m³ → in GeV/m³
#   ρ_c = 8.5e-27 * (0.674)² = 3.86e-27 kg/m³
#   1 kg = 5.6e26 GeV → ρ_c = 2.16e0 GeV/m³
# s = 7.04 nγ ≈ 2.5e-9 m⁻³ × k_B (but in cosmology s is in GeV units)
#   s = (2π²/45) g*_s T³ = 2.04e-36 GeV³ at T=2.7K (CMB)
#   s ≈ 2890/cm³ in natural units

OMEGA_B = 0.0493   # baryon fraction
OMEGA_DM = 0.265   # DM fraction
OMEGA_C = OMEGA_DM + OMEGA_B


def eta_ratio(m_chi_GeV: float, m_proton_GeV: float = 0.938) -> float:
    """
    Compute η_DM / η_B for asymmetric DM at the SAME asymmetry mechanism.

    In asymmetric DM, the relic abundance is set by the B-L-like asymmetry
    η_B, transferred to χ by some high-scale operator. If the transfer
    is 1:1 (simple Affleck-Dine or leptogenesis), then:
      η_DM = η_B × (transfer factor)
      η_DM / η_B = Ω_DM × m_p / (Ω_B × m_chi)
    """
    ratio = (OMEGA_DM * m_proton_GeV) / (OMEGA_B * m_chi_GeV)
    return ratio


def main():
    print("=" * 80)
    print("Phase 16 — Probe: Asymmetric DM baryon-to-DM ratio")
    print("=" * 80)
    print(f"η_B = (6.12 ± 0.04) × 10⁻¹⁰  (PDG 2024)")
    print(f"Ω_DM = {OMEGA_DM:.3f}, Ω_B = {OMEGA_B:.4f}")
    print(f"m_p = 0.938 GeV")
    print()

    out = {"test": "Phase16_asymmetric_dm_ratio",
           "direction": "Check if asymmetric DM at m_chi gives consistent η_DM/η_B"}

    # Scan m_chi from 1 GeV to 1000 GeV
    m_chi_values = [1, 5, 10, 15, 45, 100, 500, 1000]
    print(f"{'m_chi [GeV]':<14} {'η_DM/η_B':<12} {'transfer factor':<20} {'verdict'}")
    for m_chi in m_chi_values:
        ratio = eta_ratio(m_chi)
        # transfer factor = η_DM/η_B in units of baryon→DM coupling
        # If ratio ~ 1, then a 1:1 transfer works (single mechanism)
        # If ratio << 1, then DM is lighter per asymmetry, common
        # If ratio >> 1, then need amplification
        if 0.5 < ratio < 2.0:
            verdict = "NATURAL (1:1 transfer)"
        elif 0.1 < ratio < 10:
            verdict = "PLAUSIBLE (modest transfer)"
        elif ratio < 0.01 or ratio > 100:
            verdict = "UNNATURAL (extreme transfer)"
        else:
            verdict = "TUNED"
        print(f"{m_chi:<14} {ratio:<12.3f} {ratio:<20.3f} {verdict}")
        out[f"m_chi_{m_chi}_GeV"] = {
            "eta_DM_over_eta_B": float(ratio),
            "verdict": verdict,
        }

    # Test the v0.3-prelim MAP: m_chi = 45 GeV
    ratio_v03 = eta_ratio(45.0)
    print()
    print(f"v0.3-prelim MAP: m_chi = 45 GeV")
    print(f"  η_DM / η_B = {ratio_v03:.3f}")
    if ratio_v03 < 1:
        print(f"  Interpretation: at 45 GeV, each baryon asymmetry quantum")
        print(f"  produces LESS DM than baryons. The asymmetry mechanism must")
        print(f"  transfer a FRACTION of η_B into χ (not 1:1).")
        transfer = 1.0 / ratio_v03
        print(f"  Required transfer efficiency: η_B → η_DM is {transfer:.1f}× LARGER")
        print(f"  than η_B → η_B. That's NOT natural.")
    else:
        print(f"  Interpretation: at 45 GeV, each baryon asymmetry quantum")
        print(f"  produces MORE DM than baryons. The mechanism must split")
        print(f"  η_B into multiple χ particles (factor {ratio_v03:.1f}×).")

    # Scan with transfer = 1 (1:1 B-L-like asymmetry) for various m_chi
    print()
    print("=" * 80)
    print("WHAT m_chi GIVES NATURAL 1:1 TRANSFER?")
    print("=" * 80)
    # Solve for m_chi such that η_DM / η_B = 1
    m_chi_natural = (OMEGA_DM * 0.938) / OMEGA_B
    print(f"For η_DM = η_B (1:1 transfer): m_chi = {m_chi_natural:.2f} GeV")
    print()
    if abs(45.0 - m_chi_natural) < 5:
        print("✓ v0.3-prelim's m_chi = 45 GeV is NEAR the natural value!")
    else:
        print(f"  v0.3-prelim's m_chi = 45 GeV is {45.0 - m_chi_natural:.1f} GeV off the natural value")
        print(f"  This means asymmetric DM at 45 GeV requires a NON-1:1 transfer")

    # For asymmetric DM to work at m_chi = 45 GeV, the asymmetry must
    # be smaller in χ than in B by factor (OMEGA_DM m_p) / (OMEGA_B m_chi)
    print()
    print(f"For m_chi = 45 GeV: η_DM/η_B = {ratio_v03:.3f}")
    print(f"  → χ asymmetry is 1/{ratio_v03:.1f} of baryon asymmetry")
    print(f"  → Either: (a) B-L mechanism splits unevenly (possible),")
    print(f"     or (b) χ mass is tuned to give ratio ~1 (fine-tuned)")

    out["m_chi_natural_GeV"] = float(m_chi_natural)
    out["v03_MAP_eta_ratio"] = float(ratio_v03)
    out["v03_MAP_verdict"] = ("NATURAL" if abs(ratio_v03 - 1) < 0.5 else
                              "PLAUSIBLE" if abs(np.log10(ratio_v03)) < 1 else
                              "UNNATURAL")

    out_path = RESULTS_DIR / "phase16_asymmetric_dm_ratio.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
