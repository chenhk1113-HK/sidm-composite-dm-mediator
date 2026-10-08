"""
Phase G13 — Exhaustive σ_m(v) shape search (R88(64))

Goal: Test as many σ_m(v) shapes as feasible to see if ANY breaks the trade-off.

Approach:
- Test 10+ different σ_m(v) functional forms
- For each, compute σ_eff(150) at observation radius
- Check if it satisfies both Sameie+ 2020 (<0.3) and Lei/Wang (>0.1)
- Check all other channels too

Shapes tested:
1. Single resonance (Phase 44 baseline)
2. Two-resonance (Phase G7)
3. Three-resonance (Phase G8)
4. Power-law (no resonance)
5. Exponential cutoff at v=100
6. Step function (high below 100, low above)
7. Inverse function (high at low v, low at high v)
8. Double-bump (narrow at v=28, narrow at v=200, no v=150)
9. Three-peak avoiding v=150 (Phase G13 attempt)
10. Environment-dependent (centrals vs subhalos)
11. Gaussian envelope (smooth, no resonances)
12. Composite (Phase G8 with v=150 peak removed)
"""
from __future__ import annotations
import math
import numpy as np


# Standard observation channels
CHANNELS = [
    # (name, v, r/r_s, threshold_type, threshold_value)
    ("Horigome dSph (v=15, r=6)", 15, 6.0, "<", 0.8),
    ("Fischer&Yu UFD (v=7, r=1)", 7, 1.0, "tau", 1.0),
    ("Cloud-9 inner (v=28, r=0.5)", 28, 0.5, ">", 50),
    ("Cloud-9 V_max (v=31.12, r=0.5)", 31.12, 0.5, ">", 50),
    ("SPARC typical (v=100, r=1.5)", 100, 1.5, "~", 0.19),
    ("Lei/Wang (v=150, r=1.5, central)", 150, 1.5, "range", (0.1, 0.3)),
    ("Sameie+ 2020 (v=150, r=1.5, subhalo)", 150, 1.5, "<", 0.3),
    ("Cluster (v=500, r=1)", 500, 1.0, "<", 0.001),
]


def f_H_sidm2c(r_over_r_s, tau=100.0, cap=0.60):
    """SIDM2c f_H(r) at saturation."""
    return min(0.297 * (cap / 0.297), cap)


def evaluate_shape(sigma_m_func, name):
    """Evaluate a sigma_m(v) function against all channels.

    Uses SIDM2c f_H(r) at saturation (worst case for trade-off).
    """
    results = []
    for ch_name, v, r_obs, thresh_type, thresh_val in CHANNELS:
        # f_H at observation radius (use saturation for centrals; assume same for subhalos)
        f_h = f_H_sidm2c(r_obs)
        # sigma_m at velocity v
        sm_v = sigma_m_func(v)
        # sigma_eff = f_H^2 * sigma_m
        sigma_eff = f_h ** 2 * sm_v

        if thresh_type == "<":
            ok = sigma_eff < thresh_val
        elif thresh_type == ">":
            ok = sigma_eff > thresh_val
        elif thresh_type == "~":
            ok = 0.3 < (sigma_eff / thresh_val) < 3
        elif thresh_type == "range":
            lo, hi = thresh_val
            ok = lo < sigma_eff < hi
        else:
            ok = None  # tau

        results.append((ch_name, v, sigma_eff, ok))

    return results


def shape_1_baseline(v):
    """Phase 44 baseline: single resonance at v=29.4."""
    return 174.0 * math.exp(-((v - 29.4) ** 2) / (2 * 4.4 ** 2))


def shape_2_phase_g7(v):
    """Phase G7: background + Cloud-9 + massive."""
    bg = 0.07 * (100 / v) ** 0.9
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    massive = 5 * math.exp(-((v - 150) ** 2) / 1500)
    return bg + cloud9 + massive


def shape_3_phase_g8(v):
    """Phase G8: three peaks."""
    bg = 0.07 * (100 / v) ** 0.9
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    massive = 5 * math.exp(-((v - 150) ** 2) / 1500)
    ufd = 60 * math.exp(-((v - 10) ** 2) / 12.5)
    return bg + cloud9 + massive + ufd


def shape_4_power_law(v):
    """Pure power-law, no resonances."""
    return 1.0 * (30 / v) ** 1.5


def shape_5_exp_cutoff(v):
    """Exponential cutoff above v=100."""
    if v < 100:
        return 5 * (100 / v) ** 0.9
    else:
        return 5 * (100 / v) ** 0.9 * math.exp(-(v - 100) / 20)


def shape_6_step(v):
    """Step function: high below 100, low above."""
    if v < 100:
        return 10.0
    else:
        return 0.05


def shape_7_inverse(v):
    """Strong v-dependence: high at low v, low at high v."""
    return 100 * math.exp(-v / 30)


def shape_8_double_bump_no_150(v):
    """Peaks at v=28 and v=200, but NOT v=150."""
    bg = 0.05 * (100 / v) ** 1.0
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    far = 2.0 * math.exp(-((v - 200) ** 2) / 500)
    return bg + cloud9 + far


def shape_9_avoid_v150(v):
    """Avoid v=150 entirely: peaks at v=28 and v=100 only."""
    bg = 0.05 * (100 / v) ** 1.0
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    sparc = 2.0 * math.exp(-((v - 100) ** 2) / 200)
    return bg + cloud9 + sparc


def shape_10_env_dependent_central(v):
    """Environment-dependent: central halos have v=150 peak, subhalos don't."""
    bg = 0.07 * (100 / v) ** 0.9
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    massive = 5 * math.exp(-((v - 150) ** 2) / 1500)
    ufd = 60 * math.exp(-((v - 10) ** 2) / 12.5)
    return bg + cloud9 + massive + ufd


def shape_11_env_dependent_subhalo(v):
    """Environment-dependent: subhalos have NO v=150 peak (heavy stripped)."""
    bg = 0.07 * (100 / v) ** 0.9
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    ufd = 60 * math.exp(-((v - 10) ** 2) / 12.5)
    return bg + cloud9 + ufd


def shape_12_smooth_gaussian(v):
    """Smooth Gaussian envelope, no narrow resonances."""
    return 50 * math.exp(-((v - 100) ** 2) / 2000)


def shape_13_composite_no_150(v):
    """Phase G8 with v=150 peak removed."""
    bg = 0.07 * (100 / v) ** 0.9
    cloud9 = 350 * math.exp(-((v - 28) ** 2) / 32)
    ufd = 60 * math.exp(-((v - 10) ** 2) / 12.5)
    return bg + cloud9 + ufd


def shape_14_extreme_narrow(v):
    """Extremely narrow Cloud-9 peak."""
    return 1000 * math.exp(-((v - 29.4) ** 2) / (2 * 1.0 ** 2))


def shape_15_super_broad(v):
    """Super-broad resonance covering all velocities."""
    return 50 * math.exp(-((v - 100) ** 2) / 50000)


def run_phase_g13():
    print("=" * 90)
    print("Phase G13 — Exhaustive σ_m(v) Shape Search (R88(64))")
    print("=" * 90)
    print()
    print("Testing 15 different σ_m(v) shapes against the structural trade-off theorem.")
    print("For each shape, compute σ_eff at observation radius and check all channels.")
    print()

    shapes = [
        ("1. Baseline (single resonance at 29.4)", shape_1_baseline),
        ("2. Phase G7 (background + Cloud-9 + massive)", shape_2_phase_g7),
        ("3. Phase G8 (three peaks)", shape_3_phase_g8),
        ("4. Pure power-law (no resonance)", shape_4_power_law),
        ("5. Exponential cutoff at v=100", shape_5_exp_cutoff),
        ("6. Step function (high<100, low>100)", shape_6_step),
        ("7. Strong inverse (high at low v)", shape_7_inverse),
        ("8. Double-bump, NO v=150 peak", shape_8_double_bump_no_150),
        ("9. Avoid v=150 (peaks at 28, 100)", shape_9_avoid_v150),
        ("10. Central: full Phase G8", shape_10_env_dependent_central),
        ("11. Subhalo: NO v=150 peak", shape_11_env_dependent_subhalo),
        ("12. Smooth Gaussian (no resonances)", shape_12_smooth_gaussian),
        ("13. Composite: Phase G8 minus v=150", shape_13_composite_no_150),
        ("14. Extreme narrow Cloud-9 (σ=1)", shape_14_extreme_narrow),
        ("15. Super-broad resonance", shape_15_super_broad),
    ]

    results_summary = []

    for name, shape_func in shapes:
        print(f"\n--- {name} ---")

        # Get sigma_eff at v=150 for trade-off test
        sigma_eff_150 = f_H_sidm2c(1.5) ** 2 * shape_func(150)

        # Check trade-off at v=150
        lei_ok = 0.1 < sigma_eff_150 < 0.3
        he_ok = sigma_eff_150 < 0.3
        trade_off_satisfied = lei_ok and he_ok

        # Evaluate all channels
        ch_results = evaluate_shape(shape_func, name)

        n_pass = sum(1 for _, _, _, ok in ch_results if ok)

        print(f"  σ_eff(v=150) at observation radius: {sigma_eff_150:.4f}")
        print(f"  Lei/Wang (>0.1): {'PASS' if lei_ok else 'FAIL'}")
        print(f"  Sameie+ 2020 (<0.3): {'PASS' if he_ok else 'FAIL'}")
        print(f"  v=150 trade-off satisfied: {'YES' if trade_off_satisfied else 'NO'}")
        print(f"  Total channels passing: {n_pass}/{len(ch_results)}")

        results_summary.append((name, sigma_eff_150, lei_ok, he_ok, trade_off_satisfied, n_pass))

    print()
    print("=" * 90)
    print("Summary: Which σ_m(v) shapes break the v=150 trade-off?")
    print("=" * 90)
    print()
    print(f"{'Shape':<50} {'σ_eff(150)':<12} {'Lei':<8} {'He+':<8} {'Trade-off':<12} {'Pass'}")
    print("-" * 110)

    n_break = 0
    for name, se, lei, he, trade, n_pass in results_summary:
        trade_str = "BREAKS" if trade else "STANDS"
        lei_str = "PASS" if lei else "FAIL"
        he_str = "PASS" if he else "FAIL"
        if trade:
            n_break += 1
        print(f"{name:<50} {se:<12.4f} {lei_str:<8} {he_str:<8} {trade_str:<12} {n_pass}/{len(CHANNELS)}")

    print()
    print(f"Result: {n_break}/{len(shapes)} shapes break the v=150 trade-off")
    print()

    if n_break == 0:
        print("=" * 90)
        print("Phase G13 verdict (R88(64))")
        print("=" * 90)
        print()
        print("NONE of the 15 tested σ_m(v) shapes break the v=150 trade-off theorem.")
        print()
        print("This includes:")
        print("- Standard SIDM shapes (resonance, power-law, Gaussian)")
        print("- Exotic shapes (step function, exponential cutoff, super-broad)")
        print("- Phase G7/G8 multi-resonance")
        print("- Environment-dependent shapes (centrals vs subhalos)")
        print()
        print("The trade-off theorem is ROBUST across all simple parameterizations.")
        print("Resolution requires either:")
        print("  1. Observation refinement (Direction D)")
        print("  2. Exotic UV construction (specific σ_H(v) that overcomes f_H² bound)")
        print("  3. New physics beyond simple σ_m(v) shapes")
    else:
        print(f"{n_break} shapes break the trade-off. Investigating...")
        for name, se, lei, he, trade, n_pass in results_summary:
            if trade:
                print(f"  {name}: σ_eff(150) = {se:.4f}, {n_pass} channels pass")

    return results_summary


if __name__ == "__main__":
    results = run_phase_g13()
