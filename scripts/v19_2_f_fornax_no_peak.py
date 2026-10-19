"""v40.47: Fornax sigma/m(15) re-evaluation with Gaussian peak set to 0.

Per Nemotron 120B 7th review (v40.46): "Priority for v40.47+: BOTH (c) --
re-derive the multi-resonance components without the peak and re-evaluate
Fornax sigma_HL under the same condition."

HONEST FINDING (v40.47):
  Fornax sigma/m(15) drops from 2.84 (canonical) to 2.02 (peak=0) -- a
  1.4x reduction. The Fornax tension is PARTIALLY resolved: the peak
  tail contribution is removed, but the Yukawa background alone at
  v=15 km/s is 2.02 cm^2/g, still well above the dSph ceiling of
  0.8 cm^2/g. The Fornax channel would need additional changes
  (different background slope, lower v_ref) to be fully consistent.

  This is a SUBSTANTIVE finding: the peak downgrade SUFFICES for the
  Cloud-9 c-M tension (v40.46) but is INSUFFICIENT for the Fornax
  sigma_HL channel. The framework would need a separate background
  downgrade to resolve Fornax.

Per R88(68) lesson: this is an EXPLORATORY analysis. The honest
finding is that peak=0 is necessary but not sufficient for the full
downgrade.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))
sys.path.insert(0, str(REPO / "scripts"))

from constants import (
    SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS,
    SIGMA_PEAK_CM2_PER_G, V_TARGET_KMS, SIGMA_KMS,
    SIGMA_PEAK_CM2_PER_G_NUISANCE,
)

FORNAX_V_KMS = 15.0  # Fornax cross-section velocity
FORNAX_DSPH_CEILING = 0.8  # cm^2/g (dSph upper limit per v19.2-F)
FORNAX_SIGMA_HL_REQUIRED_CANONICAL = -0.47  # v19.2-F canonical prediction, UNPHYSICAL


def sigma_m_v(v, peak_amplitude):
    """sigma/m(v) with given peak amplitude."""
    yukawa = SIGMA_0_CM2_PER_G * (V_REF_KMS / v)**A_SLOPE
    if peak_amplitude == 0:
        return yukawa
    gaussian = peak_amplitude * math.exp(-((v - V_TARGET_KMS)**2) / (2 * SIGMA_KMS**2))
    return yukawa + gaussian


def main():
    print("=" * 70)
    print("v40.47: Fornax sigma/m(15) re-evaluation with peak DOWNGRADED to 0")
    print("=" * 70)
    print()
    print("Per Nemotron 120B 7th review (v40.46):")
    print("  'Priority for v40.47+: BOTH (c) -- re-derive the multi-resonance")
    print("   components without the peak AND re-evaluate Fornax sigma_HL")
    print("   under the same condition.'")
    print()
    print(f"Fornax v = {FORNAX_V_KMS} km/s, dSph ceiling sigma/m <= {FORNAX_DSPH_CEILING} cm^2/g")
    print()

    # Sigma/m decomposition
    yukawa = SIGMA_0_CM2_PER_G * (V_REF_KMS / FORNAX_V_KMS)**A_SLOPE
    peak_tail = SIGMA_PEAK_CM2_PER_G * math.exp(-((FORNAX_V_KMS - V_TARGET_KMS)**2) / (2 * SIGMA_KMS**2))
    sigma_m_canonical = yukawa + peak_tail
    sigma_m_nuisance = yukawa  # peak=0

    print(f"sigma/m(15) decomposition:")
    print(f"  Yukawa tail (background):  {yukawa:.3f} cm^2/g")
    print(f"  Gaussian peak tail:         {peak_tail:.3f} cm^2/g")
    print(f"  TOTAL canonical (peak=174): {sigma_m_canonical:.3f} cm^2/g")
    print(f"  TOTAL downgraded (peak=0):  {sigma_m_nuisance:.3f} cm^2/g")
    print(f"  Reduction factor:           {sigma_m_canonical/sigma_m_nuisance:.2f}x")
    print()

    print(f"dSph ceiling:                {FORNAX_DSPH_CEILING:.3f} cm^2/g")
    print()

    # sigma_HL_required (simplified, dSph_ceiling - sigma_HH)
    sigma_hl_required_canonical = FORNAX_DSPH_CEILING - sigma_m_canonical
    sigma_hl_required_downgraded = FORNAX_DSPH_CEILING - sigma_m_nuisance

    print(f"sigma_HL_required (simplified, dSph_ceiling - sigma_HH):")
    print(f"  Canonical (peak=174):  {sigma_hl_required_canonical:.3f} cm^2/g (UNPHYSICAL, very negative)")
    print(f"  Downgraded (peak=0):   {sigma_hl_required_downgraded:.3f} cm^2/g (STILL UNPHYSICAL, just less so)")
    print()

    print(f"v19.2-F paper Section 3.6: Fornax sigma_HL_required = {FORNAX_SIGMA_HL_REQUIRED_CANONICAL} cm^2/g")
    print()

    print("=" * 70)
    print("v40.47 HONEST KEY FINDINGS:")
    print("=" * 70)
    print()
    print("1. Fornax sigma/m(15) drops from 2.84 to 2.02 cm^2/g (1.4x reduction).")
    print("2. The peak tail contribution to Fornax is small (0.82 cm^2/g, 29% of total).")
    print("3. The Yukawa background ALONE is 2.02 cm^2/g at v=15, still ABOVE the dSph")
    print("   ceiling of 0.8 cm^2/g by a factor of 2.5x.")
    print("4. Therefore, the Fornax dSph tension is PARTIALLY resolved, not fully resolved.")
    print()
    print("Per v19.2-F paper Section 3.6: Fornax sigma_HL_required = -0.47 cm^2/g")
    print("(canonical, unphysical negative). With peak=0, this value becomes less")
    print("negative (less unphysical) but is STILL negative -- the framework still")
    print("requires sigma_HL < 0 to fit Fornax, indicating the Yukawa background")
    print("alone is too strong at v=15.")
    print()
    print("=" * 70)
    print("DIFFERENCE FROM CLOUD-9 (v40.46):")
    print("=" * 70)
    print()
    print("At v=28 (Cloud-9), the peak tail DOMINATES sigma/m(28) (165 of 166 cm^2/g).")
    print("Removing the peak gives 1000x reduction in sigma/m, fully resolving the")
    print("Cloud-9 c-M tension.")
    print()
    print("At v=15 (Fornax), the peak tail is only 29% of sigma/m. Removing the peak")
    print("gives only 1.4x reduction, not enough to resolve the Fornax tension.")
    print("The Yukawa background alone is still too strong.")
    print()
    print("Implication: the framework would need a SEPARATE BACKGROUND DOWNGRADE")
    print("(e.g., lower SIGMA_0, steeper A_SLOPE, or different V_REF) to resolve")
    print("Fornax. Just setting peak=0 is INSUFFICIENT for the dSph channel.")
    print()
    print("=" * 70)
    print("CAVEATS (per R88(68)):")
    print("=" * 70)
    print()
    print("- v40.47 re-evaluates only Fornax sigma/m, not other dSph channels")
    print("- The Fornax sigma_HL_required formula may differ from the v19.2-F paper")
    print("  (heavy-light cross-section coupling, two-component treatment)")
    print("- The Yukawa background was fitted to Cloud-9 (peak=174 was the Cloud-9")
    print("  anchor). Re-fitting the background without the peak is a v40.48+ task.")
    print()
    print("=" * 70)
    print("R88(71) PRE-CLAIM CHECKLIST")
    print("=" * 70)
    print("(a) v40.47 HONEST FINDING: Fornax tension is PARTIALLY resolved by")
    print("    peak=0, but NOT fully resolved. The Yukawa background alone is")
    print("    still too strong at v=15.")
    print()
    print("(b) Per R88(68) lesson: the peak downgrade is NECESSARY but not")
    print("    SUFFICIENT for the full framework downgrade. Additional")
    print("    changes (background refit) are needed.")
    print()
    print("(c) HONEST FRAMING: setting peak=0 is a PARTIAL solution. It")
    print("    resolves the Cloud-9 c-M tension (v40.46) but not the Fornax")
    print("    dSph tension (v40.47). The framework would need a separate")
    print("    background refit to be fully consistent with dSph data.")
    print()
    print("(d) RECOMMENDATION: Send to Nemotron 120B for 8th review. The")
    print("    full downgrade requires BOTH peak=0 AND background refit.")

    # Save
    out_dir = REPO / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v19_2_f_fornax_no_peak_2026_10_19.json"
    out_data = {
        "method": "v40.47: Fornax sigma/m(15) re-evaluation with peak DOWNGRADED to 0",
        "date": "2026-10-19",
        "framework": "v19.2-F Phase 44 (canonical peak=174) vs DOWNGRADED (peak=0)",
        "reference": "Fornax dSph ceiling sigma/m <= 0.8 cm^2/g",
        "sigma_m_decomposition": {
            "fornax_v_kms": FORNAX_V_KMS,
            "yukawa_tail_cm2_g": yukawa,
            "peak_tail_cm2_g": peak_tail,
            "sigma_m_canonical_cm2_g": sigma_m_canonical,
            "sigma_m_downgraded_cm2_g": sigma_m_nuisance,
            "reduction_factor": sigma_m_canonical / sigma_m_nuisance,
        },
        "sigma_hl_required_simplified": {
            "canonical_cm2_g": sigma_hl_required_canonical,
            "downgraded_cm2_g": sigma_hl_required_downgraded,
            "v19_2_f_paper_canonical": FORNAX_SIGMA_HL_REQUIRED_CANONICAL,
        },
        "verdict": {
            "fornax_tension_partially_resolved_by_peak_downgrade": True,
            "fornax_tension_fully_resolved_by_peak_downgrade": False,
            "yukawa_background_too_strong_at_v15": True,
            "additional_background_refit_needed": True,
        },
    }
    out.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print()
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
