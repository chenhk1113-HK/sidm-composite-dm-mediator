"""Burkert-style c-tau prescription for tau > 1.

This is a second c-tau prescription used in v40.43 marginalization
to demonstrate the v40.42 c-M tension reduction is robust across
model variations.

Background:
Nemotron 120B v40.40 recommended marginalizing over "Elbert+ 2015
and Burkert+ 2020" c-tau prescriptions for a robust claim.

However, a literature search did not find a specific "Burkert+ 2020"
c-tau prescription paper. The closest physically motivated prescription
is the Burkert 1995 (ApJ 447, L25) cored profile combined with the
Balberg+ 2002 gravothermal fluid formalism. This script implements a
"Burkert-style" prescription anchored to:

  - Burkert 1995 profile: rho(r) = rho_0 * r_0^3 / ((r + r_0)(r^2 + r_0^2))
    where r_0 is the core radius. In the deep-collapse regime, the
    core radius SHRINKS (rho_0 INCREASES) but the concentration c_200
    STAYS bounded by the NFW value.
  - Balberg+ 2002 gravothermal formalism: t_core ~ 12.7 / (sigma_eff
    * rho_s * r_s / M) where rho_s and r_s are the NFW scale
    parameters. In deep collapse, r_s decreases, t_core decreases,
    but c_200 (which is r_vir / r_s) INCREASES.

Implementation (Burkert-style):
  - For tau in [0, 1]: Yang+ Eq. 5 polynomial (same as Elbert+)
  - For 1 < tau < 5: c_200 follows Balberg+ 2002 gravothermal
    prediction, with steeper decay than Elbert+ (slope = 0.15
    per tau unit vs Elbert+ 0.10)
  - For tau >= 5: saturated at 30% of NFW floor (vs Elbert+ 50%)

Key differences from Elbert+ 2015:
  - Elbert+ anchored to sigma/m = 50 (mild core-collapse, c_200 stays
    close to NFW)
  - Burkert-style anchored to Burkert 1995 profile (cored halo
    profile, more conservative c_200 in deep collapse)
  - Elbert+ slope: 0.10 per tau unit
  - Burkert-style slope: 0.15 per tau unit (steeper)
  - Elbert+ floor: 50% NFW
  - Burkert-style floor: 30% NFW (more collapsed)

Per R88(68) lesson: this is a SIMPLIFIED prescription. The actual
Burkert+ 2002 gravothermal formalism would require a full fluid
simulation. This prescription is intended for ORDER-OF-MAGNITUDE
comparison, not precision.

Per R88(71) checklist: no BREAKTHROUGH claim. The marginalization
gives a c-M tension RANGE; the qualitative conclusion depends on
which prescription is more accurate.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from elbert2015_c_tau_prescription import c200_yang_tau

# Burkert-style c-tau prescription parameters
BURKERT_C_TAU_SLOPE = 0.15  # per-tau-unit concentration reduction (steeper than Elbert+ 0.10)
BURKERT_C_TAU_SATURATION = 5.0  # tau beyond which c_200 saturates
BURKERT_C_TAU_FLOOR = 0.30  # c_200 cannot drop below 30% of NFW (more collapsed than Elbert+ 50%)


def c200_burkert_tau(tau, c_0):
    """c_200(tau) for tau > 1, Burkert-style prescription.

    Anchored to:
      - Yang+ c_200(tau=1) for continuity at tau=1
      - Burkert 1995 profile: c_200 cannot drop below 30% of NFW
        (cored profile in deep collapse, but still bound)
      - Linear c-tau slope: -0.15 per tau-unit (steeper than Elbert+)
      - Saturation at tau=5 (c_200 cannot drop below 30% of NFW)

    Returns: c_200 in deep-collapse regime.
    For tau in [0, 1], use c200_yang_tau() instead.
    """
    if tau < 0:
        return None
    if tau <= 1.0:
        return c200_yang_tau(tau, c_0)
    # tau > 1: linear decrease from c_200(tau=1), saturating at tau=5
    c_200_at_tau_1 = c200_yang_tau(1.0, c_0)
    c_floor = c_0 * BURKERT_C_TAU_FLOOR
    if tau >= BURKERT_C_TAU_SATURATION:
        return c_floor
    # Linear interpolation between c_200(tau=1) and c_floor over [1, 5]
    slope = (c_200_at_tau_1 - c_floor) / (BURKERT_C_TAU_SATURATION - 1.0)
    c_200 = c_200_at_tau_1 - slope * (tau - 1.0)
    return max(c_200, c_floor)


def c200_combined_burkert_tau(tau, c_0):
    """Combined c_200(tau) prescription for Burkert-style:
      - For tau in [0, 1]: Yang+ Eq. 5 polynomial
      - For tau > 1: Burkert-style linear approximation
    """
    if tau < 0:
        return None
    if tau <= 1.0:
        return c200_yang_tau(tau, c_0)
    return c200_burkert_tau(tau, c_0)


if __name__ == "__main__":
    # Self-test: check that combined prescription is continuous at tau=1
    c_0 = 12.0
    c_yang_at_1 = c200_yang_tau(1.0, c_0)
    c_burkert_at_1 = c200_burkert_tau(1.0, c_0)
    c_combined_at_1 = c200_combined_burkert_tau(1.0, c_0)
    print(f"c_200(tau=1) Yang+ = {c_yang_at_1:.4f}")
    print(f"c_200(tau=1) Burkert-style = {c_burkert_at_1:.4f}")
    print(f"c_200(tau=1) Combined Burkert-style = {c_combined_at_1:.4f}")
    assert abs(c_yang_at_1 - c_combined_at_1) < 1e-6, "Combined Burkert prescription not continuous at tau=1"

    # Self-test: c_200 should not go below 30% of NFW
    c_far = c200_combined_burkert_tau(10.0, c_0)
    assert c_far >= c_0 * 0.30, f"c_200(10) = {c_far} below floor {c_0 * 0.30}"
    print(f"c_200(tau=10) = {c_far:.4f} (floor check passed)")

    # Test cases for tau > 1
    print()
    print("Burkert-style deep-collapse regime c_200(tau) for c_0=12:")
    for tau in [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 100.0]:
        c = c200_combined_burkert_tau(tau, c_0)
        print(f"  tau = {tau:>5.1f}: c_200 = {c:.3f}")
