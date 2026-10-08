"""
Phase G19 - Direction D Verification: sigma_m(150) direct computation
====================================================================

R88(78): Caught a numerical error in Direction D's initial analysis.

This module computes Phase 44 sigma/m(v=150) directly and verifies
the framework's actual prediction against Lei/Wang observations.

THE KEY COMPUTATION
-------------------
Phase 44 sigma/m(v) = background + resonance
where:
  background = a_slope * sigma_0 * (v_ref / v)^a_slope
  resonance = sigma_peak * exp(-0.5 * ((v - v_target) / sigma_kms)^2)

With Phase 44 parameters:
  v_target = 29.4 km/s  (Cloud-9 resonance, NOT v=150)
  sigma_peak = 174 cm^2/g
  sigma_kms = 4.4 (Gaussian width)
  a_slope = 1.93 (background power-law)
  sigma_0 = 0.052 cm^2/g
  v_ref = 100 km/s

At v = 150 km/s:
  resonance = 174 * exp(-0.5 * ((150-29.4)/4.4)^2)
            = 174 * exp(-375.6)
            = ~ 0 (essentially zero, v=150 is 27 sigma from v_target)
  background = 1.93 * 0.052 * (100/150)^1.93
             = 0.046 cm^2/g

So sigma_m(150) = 0 + 0.046 = 0.046 cm^2/g (BACKGROUND ONLY)

THE LEI/WANG OBSERVATION
------------------------
Lei+ Wang 2024 measures sigma_eff(v=150) for massive galaxy cores:
  0.1 < sigma_eff(150) < 0.3 cm^2/g (centrals)

THE FRAMEWORK PREDICTION
------------------------
With Phase G7 f_H segregation (f_H_cen = 0.6, f_H_sub = 0.05):
  sigma_eff(150, central) = (0.6)^2 * 0.046 = 0.36 * 0.046 = 0.0165 cm^2/g
  sigma_eff(150, subhalo) = (0.05)^2 * 0.046 = 0.0025 * 0.046 = 0.000115 cm^2/g

VERDICT
-------
sigma_eff(150, central) = 0.0165 < 0.1 (Lei/Wang lower bound)
                          --> FRAMEWORK FAILS Lei/Wang by factor 6

R88(56) §9.17a is correct: the v=150 trade-off is REAL.
The framework cannot explain the Lei/Wang observation at v=150.

R88(71) PRE-CLAIM CHECKLIST
---------------------------
(1) Does this contradict R88(56)? NO. It CONFIRMS R88(56).
(2) Parameters physical? YES (Phase 44 standard parameters).
(3) n_params vs n_channels? N/A (no new parameters).
(4) Correct microphysical model? YES. Direct computation of Phase 44.

This is a CLEAN NEGATIVE result, not a fitting exercise.
The v=150 trade-off stands.
"""
import numpy as np

# Phase 44 parameters (from R88(56) SSoT)
V_TARGET_KMS = 29.4  # Cloud-9 resonance, NOT v=150
SIGMA_PEAK_CM2_PER_G = 174.0
SIGMA_KMS = 4.4
A_SLOPE = 1.93
SIGMA_0_CM2_PER_G = 0.052
V_REF_KMS = 100.0


def sigma_m(v_kms: float) -> float:
    """Phase 44 sigma/m(v) - direct computation."""
    background = A_SLOPE * SIGMA_0_CM2_PER_G * (V_REF_KMS / v_kms) ** A_SLOPE
    resonance = SIGMA_PEAK_CM2_PER_G * np.exp(-0.5 * ((v_kms - V_TARGET_KMS) / SIGMA_KMS) ** 2)
    return background + resonance


def sigma_eff(v_kms: float, f_h: float) -> float:
    """Observable sigma_eff with heavy fraction f_h."""
    return f_h ** 2 * sigma_m(v_kms)


def main():
    print("=" * 70)
    print("Phase G19: Direction D Verification (R88(78))")
    print("=" * 70)
    print()
    print("Direct computation of Phase 44 sigma/m(v=150) and comparison")
    print("with Lei/Wang observations.")
    print()

    # Compute sigma_m at key velocities
    print("=" * 70)
    print("Phase 44 sigma/m(v) at key velocities")
    print("=" * 70)
    for v in [10, 15, 28, 29.4, 50, 100, 150, 200, 300, 500, 1000]:
        sig = sigma_m(v)
        resonance = SIGMA_PEAK_CM2_PER_G * np.exp(-0.5 * ((v - V_TARGET_KMS) / SIGMA_KMS) ** 2)
        background = A_SLOPE * SIGMA_0_CM2_PER_G * (V_REF_KMS / v) ** A_SLOPE
        print(f"  v = {v:6.1f}: sigma_m = {sig:.4f}  (resonance = {resonance:.4e}, "
              f"background = {background:.4f})")
    print()

    # Critical computation: v=150
    print("=" * 70)
    print("CRITICAL: sigma_m(150) for Lei/Wang test")
    print("=" * 70)
    v = 150.0
    sig_150 = sigma_m(v)
    print(f"  sigma_m(150) = {sig_150:.4f} cm^2/g")
    print()
    print("  This is the BACKGROUND power-law tail at v=150.")
    print("  The Gaussian resonance at v_target=29.4 contributes ~0 (27 sigma away).")
    print()

    # Phase G7 framework prediction at v=150
    print("=" * 70)
    print("Phase G7 framework prediction at v=150")
    print("=" * 70)
    f_H_cen = 0.6  # Phase G7 central heavy fraction
    f_H_sub = 0.05  # Phase G7 subhalo heavy fraction

    sig_eff_cen = sigma_eff(v, f_H_cen)
    sig_eff_sub = sigma_eff(v, f_H_sub)

    print(f"  f_H_cen = 0.6 (Phase G7): sigma_eff(150, central) = {sig_eff_cen:.4f} cm^2/g")
    print(f"  f_H_sub = 0.05 (Phase G7): sigma_eff(150, subhalo) = {sig_eff_sub:.6f} cm^2/g")
    print()

    # Lei/Wang comparison
    print("=" * 70)
    print("Comparison with Lei/Wang observation")
    print("=" * 70)
    print(f"  Lei/Wang range: 0.1 < sigma_eff(150) < 0.3 cm^2/g (centrals)")
    print(f"  Framework prediction (centrals): {sig_eff_cen:.4f} cm^2/g")
    print()

    if sig_eff_cen < 0.1:
        print(f"  VERDICT: Framework FAILS Lei/Wang (factor {0.1/sig_eff_cen:.1f} below lower bound)")
    elif sig_eff_cen > 0.3:
        print(f"  VERDICT: Framework PASSES Lei/Wang (above upper bound)")
    else:
        print(f"  VERDICT: Framework is in Lei/Wang range (PASS)")

    print()
    print("=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print()
    print("Phase 44 sigma_m(150) = 0.046 cm^2/g (background only).")
    print("Phase G7 sigma_eff(150, central) = 0.0165 cm^2/g.")
    print("Lei/Wang lower bound = 0.1 cm^2/g.")
    print()
    print("The framework FAILS Lei/Wang at v=150 by factor 6.")
    print()
    print("R88(56) §9.17a is correct: the v=150 trade-off is REAL.")
    print("No parameter tuning, no framework change, no observation refinement")
    print("can break this trade-off within the current framework.")
    print()
    print("The structural trade-off theorem stands.")


if __name__ == "__main__":
    main()
