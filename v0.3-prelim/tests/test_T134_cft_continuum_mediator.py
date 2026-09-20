"""
T134 — CFT 2021 framework verification test.

Catches: deviation from continuum-mediated SIDM scaling in Born regime.

CFT 2021 prediction (arXiv:2102.05674, Eq. 6.14):
  σ_T ~ v^(-4α) in Born (high velocity) regime

For α = 0.25 (matching our data): σ_T ~ v^(-1.0)

This test:
  1. Verifies low-v (UFD/dSph) slope matches α_γ = -4α ≈ -1.0
  2. Verifies inferred α is in [0.20, 0.30] (matches CFT 2021 framework)
  3. This protects against data drift that would invalidate the
     continuum-mediated UV completion candidate

If someone changes the phenomenology to give α_γ outside [-1.2, -0.8],
this test will fail and they'll know CFT 2021 no longer applies.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import numpy as np
import pytest
import json


def test_low_v_slope_matches_cft_alpha_0_25():
    """
    Low-v (UFD/dSph) data should fit CFT 2021's Born regime prediction
    with α ∈ [0.20, 0.30] (matches continuum-mediated framework).
    """
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "results", "sigma_m_phase44.json"
    )
    with open(data_path) as f:
        data = json.load(f)

    # Extract low-v data (v < 30 km/s, excluding Cloud-9)
    velocities = []
    sigma_over_m = []
    for k, v in data.items():
        if k.startswith('v') and isinstance(v, (int, float)):
            v_str = k.split('_')[0]
            v_val = float(v_str[1:])
            if v_val < 30 and 'Cloud-9' not in k:
                velocities.append(v_val)
                sigma_over_m.append(v)

    log_v = np.log10(velocities)
    log_s = np.log10(sigma_over_m)
    slope, _ = np.polyfit(log_v, log_s, 1)

    # CFT prediction: slope = -4α, α = 0.25 → slope = -1.0
    # Inferred α = |slope| / 4
    alpha_inferred = abs(slope) / 4

    print(f"\nLow-v slope: {slope:.4f}")
    print(f"Inferred α (CFT bulk mass): {alpha_inferred:.4f}")
    print(f"CFT target α = 0.25")

    # α must be in [0.20, 0.30] for CFT 2021 framework to apply
    assert 0.20 <= alpha_inferred <= 0.30, (
        f"Inferred α = {alpha_inferred:.3f}, outside CFT 2021 framework range "
        f"[0.20, 0.30]. Low-v slope changed — continuum-mediated UV completion "
        f"may no longer apply."
    )


def test_cft_alpha_matches_slope_relation():
    """
    If CFT 2021 is the correct UV completion, the slope-relation
    slope(σ/m) = -4α must hold. For our data: α ≈ 0.246 ± 0.01.
    """
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "results", "sigma_m_phase44.json"
    )
    with open(data_path) as f:
        data = json.load(f)

    # All non-Cloud-9 data
    velocities = []
    sigma_over_m = []
    for k, v in data.items():
        if k.startswith('v') and isinstance(v, (int, float)):
            v_str = k.split('_')[0]
            v_val = float(v_str[1:])
            if 'Cloud-9' not in k:
                velocities.append(v_val)
                sigma_over_m.append(v)

    log_v = np.log10(velocities)
    log_s = np.log10(sigma_over_m)
    slope, _ = np.polyfit(log_v, log_s, 1)
    alpha = abs(slope) / 4

    # Theoretical CFT value
    alpha_theory = 0.25
    # Empirical CFT value from our data
    alpha_empirical = 0.246

    # Match within tolerance
    deviation = abs(alpha - alpha_theory)
    print(f"\nα (theory) = {alpha_theory:.3f}")
    print(f"α (data) = {alpha:.3f}")
    print(f"Deviation from theory: {deviation:.4f}")

    # Must be within 10% of theoretical
    assert deviation < 0.025, (
        f"CFT 2021 framework requires α within 10% of 0.25. "
        f"Current α = {alpha:.4f}, deviation = {deviation:.4f}."
    )


def test_high_v_regime_needs_intermediate_data():
    """
    The high-v regime (v > 30 km/s) has only 2 data points, which is
    insufficient to fully verify CFT 2021's classical regime prediction.

    This test serves as a reminder that we need intermediate data points
    at v ≈ 178 and 430 km/s (the missing KK resonance peaks).
    """
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "results", "sigma_m_phase44.json"
    )
    with open(data_path) as f:
        data = json.load(f)

    high_v_count = sum(
        1 for k, v in data.items()
        if k.startswith('v') and isinstance(v, (int, float))
        and float(k.split('_')[0][1:]) > 30
    )

    print(f"\nHigh-v data points (v > 30 km/s): {high_v_count}")
    print("CFT 2021 classical regime verification needs more points")
    print("Missing: v ≈ 178 km/s (n=3 KK peak), v ≈ 430 km/s (n=4 KK peak)")

    # Just a reminder test — not a strict assertion
    # If we ever get more data points, this will remind us to update
    if high_v_count < 4:
        print("NOTE: high-v regime undersampled for CFT verification")


if __name__ == '__main__':
    test_low_v_slope_matches_cft_alpha_0_25()
    print()
    test_cft_alpha_matches_slope_relation()
    print()
    test_high_v_regime_needs_intermediate_data()
    print()
    print("All T134 tests PASSED")