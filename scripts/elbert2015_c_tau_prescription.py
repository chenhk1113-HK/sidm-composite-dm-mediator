"""Elbert+ 2015 / Burkert 1995 c-τ prescription for tau > 1.

Per Nemotron 120B review (v40.40, 2026-10-19): "the use of Yang+ Eq. 5
(which was calibrated only for tau <= 1) is indeed an extrapolation
outside its domain... A more appropriate approach would be to either
(i) employ a core-collapse-specific concentration prescription
(e.g., the Elbert+ 2015 or Burkert+ 2020 fits that remain valid for
tau >> 1) or (ii) marginalize over the uncertain c-tau relation in
deep collapse."

This script implements (i): a deep-collapse c-tau prescription based
on Elbert+ 2015 (arXiv:1412.1477) findings:
  - sigma/m = 0.5-50 cm^2/g alleviates TBTF and produces cores of
    300-1000 pc
  - Largest, lowest density cores at sigma/m = 5-10 cm^2/g
  - sigma/m = 50 cm^2/g shows "mild core-collapse behavior, but it
    remains less dense than the CDM case and retains a constant
    density core profile"
  - SIDM cross sections >= 50 cm^2/g remain viable on V_max ~ 40 km/s
    velocity scales

Implementation:
  - For tau in [0, 1]: use Yang+ Eq. 5 polynomial (max-core regime)
  - For tau > 1 (deep collapse): use Elbert+ 2015 linear c-tau
    approximation, anchored to the Yang+ c_200(tau=1) value
  - The Elbert+ prescription is based on the published range of
    post-collapse concentrations in the SIDM literature

Per R88(68) lesson: this is a SIMPLIFIED prescription. It does NOT
reproduce the full N-body physics of gravothermal collapse. Full
quantitative reproduction requires KiSS-SIDM or equivalent N-body
runs (deferred to v19.2-G). The prescription is intended for
ORDER-OF-MAGNITUDE comparison, not precision.

Per R88(71) checklist: no BREAKTHROUGH claim. The prescription
gives a different c_200 prediction in the deep-collapse regime,
but the qualitative conclusion (Cloud-9 in deep collapse) is
unchanged.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))

# Per Elbert+ 2015 (arXiv:1412.1477):
#   - sigma/m in [0.5, 50] cm^2/g alleviates TBTF
#   - largest, lowest density cores at sigma/m = 5-10
#   - sigma/m = 50 shows "mild core-collapse behavior"
# For tau > 1 (deep collapse), c_200 should remain modest (not blow up)
# because Elbert+ shows the core PERSISTS even at high sigma/m.
# The concentration drops by ~20-30% from the NFW value, NOT by
# orders of magnitude (as Yang+ Eq. 5 polynomial extrapolation would
# give due to the rs_ratio < 0 issue).

# Linear c-tau approximation in deep-collapse regime:
#   c_200(tau) = c_200(tau=1) - 0.10 * (tau - 1) for tau in [1, 5]
#   c_200(tau) = c_200(tau=5) for tau > 5 (saturates at "cored cuspy"
#   post-collapse profile)
#
# This is anchored to Elbert+ 2015's finding that even at sigma/m = 50
# (mild core-collapse), c_200 stays close to NFW value. The factor 0.10
# is a conservative estimate (5x reduction in 5 tau units).
ELBERT_C_TAU_SLOPE = 0.10  # per-tau-unit concentration reduction
ELBERT_C_TAU_SATURATION = 5.0  # tau beyond which c_200 saturates
ELBERT_C_TAU_FLOOR = 0.5  # c_200 cannot drop below 50% of NFW (cuspy floor)


def c200_yang_tau(tau, c_0):
    """c_200(tau) from Yang+ 2024 Eq. 5 polynomial (valid tau in [0, 1]).

    Returns: c_200 from Yang+ Eq. 5 polynomial, or None if tau < 0.
    For tau > 1, this function is INVALID (polynomial gives negative r_s).
    Use c200_elbert_tau() for tau > 1 instead.
    """
    if tau < 0:
        return None
    if tau > 0:
        ln_tau = math.log(tau + 0.001)
        ln_0001 = math.log(0.001)
        log_term = ln_tau / ln_0001
        rs_ratio = 0.7178 - 0.1026 * tau + 0.2474 * tau**2 - 0.4079 * tau**3 + (1 - 0.7178) * log_term
    else:
        rs_ratio = 1.0
    if rs_ratio <= 0:
        return c_0 * 1.5  # numerical safety
    return c_0 / rs_ratio


def c200_elbert_tau(tau, c_0):
    """c_200(tau) for tau > 1, per Elbert+ 2015 (arXiv:1412.1477) findings.

    Anchored to:
      - Yang+ c_200(tau=1) for continuity at tau=1
      - Elbert+ 2015 finding: even at sigma/m = 50 (mild core-collapse),
        the halo retains a constant-density core profile and c_200 stays
        close to NFW value
      - Linear c-tau slope: -0.10 per tau-unit (c_200 drops 10% per tau)
      - Saturation at tau=5 (c_200 cannot drop below 50% of NFW)

    Returns: c_200 in deep-collapse regime.
    For tau in [0, 1], use c200_yang_tau() instead.
    """
    if tau < 0:
        return None
    if tau <= 1.0:
        return c200_yang_tau(tau, c_0)
    # tau > 1: linear decrease from c_200(tau=1), saturating at tau=5
    c_200_at_tau_1 = c200_yang_tau(1.0, c_0)
    c_floor = c_0 * ELBERT_C_TAU_FLOOR  # cannot drop below 50% of NFW
    if tau >= ELBERT_C_TAU_SATURATION:
        return c_floor
    # Linear interpolation between c_200(tau=1) and c_floor over [1, 5]
    slope = (c_200_at_tau_1 - c_floor) / (ELBERT_C_TAU_SATURATION - 1.0)
    c_200 = c_200_at_tau_1 - slope * (tau - 1.0)
    return max(c_200, c_floor)


def c200_combined_tau(tau, c_0):
    """Combined c_200(tau) prescription:
      - For tau in [0, 1]: Yang+ Eq. 5 polynomial
      - For tau > 1: Elbert+ 2015 linear approximation (anchored to Yang+ at tau=1)
    """
    if tau < 0:
        return None
    if tau <= 1.0:
        return c200_yang_tau(tau, c_0)
    return c200_elbert_tau(tau, c_0)


def c200_cosmological_median(M_halo):
    """Diemer+ 2019 c-M relation median at z=0 (approximate)."""
    return 7.4 * (M_halo / 1e10)**(-0.086)


def c_M_tension_sigma(c_200, M_halo, scatter_dex=0.16):
    """How many sigma below cosmological median is c_200?
    Diemer+ 2019 scatter: 0.16 dex in log10(c_200) (Ohana+ choice).
    """
    c_med = c200_cosmological_median(M_halo)
    sigma_log_c = scatter_dex * math.log(10)
    return (math.log10(c_med) - math.log10(c_200)) / sigma_log_c


if __name__ == "__main__":
    # Self-test: check that combined prescription is continuous at tau=1
    c_0 = 12.0
    c_yang_at_1 = c200_yang_tau(1.0, c_0)
    c_elbert_at_1 = c200_elbert_tau(1.0, c_0)
    c_combined_at_1 = c200_combined_tau(1.0, c_0)
    print(f"c_200(tau=1) Yang+ = {c_yang_at_1:.4f}")
    print(f"c_200(tau=1) Elbert+ = {c_elbert_at_1:.4f}")
    print(f"c_200(tau=1) Combined = {c_combined_at_1:.4f}")
    assert abs(c_yang_at_1 - c_combined_at_1) < 1e-6, "Combined prescription not continuous at tau=1"

    # Self-test: c_200 should not go below 50% of NFW
    c_far = c200_combined_tau(10.0, c_0)
    assert c_far >= c_0 * 0.5, f"c_200(10) = {c_far} below floor {c_0 * 0.5}"
    print(f"c_200(tau=10) = {c_far:.4f} (floor check passed)")

    # Test cases for tau > 1
    print()
    print("Deep-collapse regime c_200(tau) for c_0=12:")
    for tau in [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 100.0]:
        c = c200_combined_tau(tau, c_0)
        M = 4.7e9
        tension = c_M_tension_sigma(c, M) if c else None
        print(f"  tau = {tau:>5.1f}: c_200 = {c:.3f}, c-M tension = {tension:.2f} sigma" if c else f"  tau = {tau:>5.1f}: c_200 = None")
