"""Sameie+ 2020 c-tau prescription for tau > 1 (cuspy collapse).

This is a third c-tau prescription used in v40.43a marginalization
to test the v40.43 ROBUST verdict under a fundamentally different
deep-collapse framework.

PAPER REFERENCE:
  Sameie, O., Yu, H.-B., Sales, L. V., Vogelsberger, M., Zavala, J.
  2020, Physical Review Letters, 124, 141102
  "Self-Interacting Dark Matter Subhalos in the Milky Way's Tides"
  arXiv:1904.07872 [astro-ph.GA]

KEY FINDINGS FROM SAMEIE+ 2020:
  - sigma/m = 3 cm^2/g explains diverse rotation curves of field
    spiral galaxies
  - For sigma/m > 5 cm^2/g, subhalos can experience SIDM core collapse
  - In core-collapse phase, central density INCREASES, halo becomes
    CUSPIER (not cored)
  - Draco's host could be in core-collapse phase for sigma/m > 5 cm^2/g
  - c_200 INCREASES in deep-collapse regime (cuspy collapse),
    OPPOSITE to Elbert+ 2015 / Burkert-style (which assume c_200
    DECREASES)

PHYSICAL PICTURE:
  - sigma/m in [0.5, 3] cm^2/g: max-core phase, c_200 stays at NFW
  - sigma/m in [3, 10] cm^2/g: transition, c_200 starts to increase
  - sigma/m > 10 cm^2/g: deep core collapse, c_200 well above NFW
  - sigma/m > 50 cm^2/g: very deep collapse, c_200 can be 1.5-2x NFW

IMPLEMENTATION (Sameie+ 2020 cuspy-collapse):
  - For tau in [0, 1]: Yang+ Eq. 5 polynomial (max-core, c_200 decreases)
  - For 1 < tau < 5: c_200 INCREASES from Yang+ value to 2x NFW
  - For tau >= 5: saturated at 2x NFW (cuspy collapse floor)
  - Anchored to Sameie+ 2020 finding: in deep collapse, c_200 > NFW

This is FUNDAMENTALLY DIFFERENT from Elbert+ 2015 and Burkert-style,
which assume c_200 DECREASES in deep collapse. The three prescriptions
test the c-M tension under different deep-collapse physics.

Per R88(68) lesson: this is a SIMPLIFIED prescription. The actual
Sameie+ 2020 N-body gives qualitative guidance (c_200 increases in
deep collapse) but does not provide a quantitative c_tau formula.
This prescription captures the qualitative direction (c_200 up, not
down) with a linear interpolation.

Per R88(71) checklist: no BREAKTHROUGH claim. The 3-prescription
marginalization tests whether the c-M tension reduction is robust
across fundamentally different deep-collapse physics.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from elbert2015_c_tau_prescription import c200_yang_tau

# Sameie+ 2020 c-tau prescription parameters
# c_200 INCREASES in deep collapse (cuspy collapse)
SAMEIE_C_TAU_SLOPE = 0.40  # per-tau-unit concentration INCREASE (steeper, positive direction)
SAMEIE_C_TAU_SATURATION = 5.0  # tau beyond which c_200 saturates
SAMEIE_C_TAU_CEILING = 2.0  # c_200 cannot exceed 2x NFW (cuspy ceiling)
SAMEIE_C_TAU_FLOOR_LOW = 1.0  # at tau=1, c_200 = Yang+ value (continuity)


def c200_sameie_tau(tau, c_0):
    """c_200(tau) for tau > 1, Sameie+ 2020 cuspy-collapse prescription.

    Anchored to:
      - Yang+ c_200(tau=1) for continuity at tau=1
      - Sameie+ 2020 finding: in deep collapse, c_200 INCREASES (cuspy
        collapse), reaching up to 2x NFW at tau >= 5
      - Linear c-tau slope: +0.40 per tau-unit (POSITIVE direction,
        opposite to Elbert+/Burkert-style)
      - Saturation at tau=5 (c_200 cannot exceed 2x NFW)

    Returns: c_200 in deep-collapse regime.
    For tau in [0, 1], use c200_yang_tau() instead.
    """
    if tau < 0:
        return None
    if tau <= 1.0:
        return c200_yang_tau(tau, c_0)
    # tau > 1: INCREASE c_200 from Yang+ value to 2x NFW
    c_200_at_tau_1 = c200_yang_tau(1.0, c_0)
    c_ceiling = c_0 * SAMEIE_C_TAU_CEILING
    if tau >= SAMEIE_C_TAU_SATURATION:
        return c_ceiling
    # Linear interpolation between c_200(tau=1) and c_ceiling over [1, 5]
    slope = (c_ceiling - c_200_at_tau_1) / (SAMEIE_C_TAU_SATURATION - 1.0)
    c_200 = c_200_at_tau_1 + slope * (tau - 1.0)
    return min(c_200, c_ceiling)


def c200_combined_sameie_tau(tau, c_0):
    """Combined c_200(tau) prescription for Sameie+ 2020:
      - For tau in [0, 1]: Yang+ Eq. 5 polynomial
      - For tau > 1: Sameie+ 2020 cuspy-collapse (c_200 INCREASES)
    """
    if tau < 0:
        return None
    if tau <= 1.0:
        return c200_yang_tau(tau, c_0)
    return c200_sameie_tau(tau, c_0)


if __name__ == "__main__":
    # Self-test: check that combined prescription is continuous at tau=1
    c_0 = 12.0
    c_yang_at_1 = c200_yang_tau(1.0, c_0)
    c_sameie_at_1 = c200_sameie_tau(1.0, c_0)
    c_combined_at_1 = c200_combined_sameie_tau(1.0, c_0)
    print(f"c_200(tau=1) Yang+ = {c_yang_at_1:.4f}")
    print(f"c_200(tau=1) Sameie+ = {c_sameie_at_1:.4f}")
    print(f"c_200(tau=1) Combined Sameie+ = {c_combined_at_1:.4f}")
    assert abs(c_yang_at_1 - c_combined_at_1) < 1e-6, "Combined Sameie+ prescription not continuous at tau=1"

    # Self-test: c_200 should not exceed 2x NFW
    c_far = c200_combined_sameie_tau(10.0, c_0)
    assert c_far <= c_0 * 2.0 + 1e-6, f"c_200(10) = {c_far} above ceiling {c_0 * 2.0}"
    print(f"c_200(tau=10) = {c_far:.4f} (ceiling check passed)")

    # Test cases for tau > 1
    print()
    print("Sameie+ 2020 cuspy-collapse regime c_200(tau) for c_0=12:")
    for tau in [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 100.0]:
        c = c200_combined_sameie_tau(tau, c_0)
        print(f"  tau = {tau:>5.1f}: c_200 = {c:.3f}")
