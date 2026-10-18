#!/usr/bin/env python3
"""
v40.31: Unified formula - phenomenological Breit-Wigner with free amplitude

User directive: Find a unified formula that bridges the v40.24 Breit-Wigner
and v40.28 Gaussian frameworks.

HYPOTHESIS:
The v40.30 finding was that the v19.2-F has two sigma_m formulas:
1. Full Breit-Wigner (F^2 factor): alpha_D = 5.55e-6 gives peak 5,918
2. Paper canonical (Gaussian): sigma_peak = 174 (set independently)

UNIFIED FORMULA:
sigma_m(v) = sigma_0 * (100/v)^A_SLOPE         (phenomenological background)
           + sigma_peak * Gamma^2 / (4(v-v_peak)^2 + Gamma^2)  (Breit-Wigner peak)

This is a "phenomenological Breit-Wigner" with:
- Free amplitude (sigma_peak) - matches the v40.28 parameterization
- Free width (Gamma) - this is the new parameter
- Phenomenological background - matches the v40.28 background
- Bounded by physics: sigma_peak = Born_baseline(alpha_D) sets the connection
  to the dark coupling (so alpha_D = 1.87e-6 from v40.30)

The Gaussian (v40.28) is a special case of the Breit-Wigner when Gamma is small
(Breit-Wigner -> delta function for Gamma -> 0, with area conserved).

ADVANTAGE: The Breit-Wigner has physical motivation (Tsai 2022 dark-QCD with
narrow resonances). The v40.28 Gaussian was phenomenological; this brings back
the UV connection.

TASKS:
1. Build unified formula
2. Scan 4D (A_SLOPE, sigma_0, sigma_peak, Gamma) for 20/20 channels
3. Compare to v40.28 Gaussian (sigma_1 = 1.5)
4. Verify alpha_D = 1.87e-6 reproduces sigma_peak = 174
"""
import os
import sys
import math
import json
import numpy as np

_PROJECT = r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator"
sys.path.insert(0, _PROJECT)
sys.path.insert(0, os.path.join(_PROJECT, "v0.3-prelim", "code"))

# Hardcoded from v40.20 locked values
M_RHO_GEV = 5e-5
V_PEAK = 29.4
G_TO_GEV = 1.0 / 1.66053900266e-24
C_KMS = 2.998e5
HBAR_C_GEV_CM = 1.97327e-14


def sigma_m_unified(v_kms, a_slope, sigma_0, sigma_peak, gamma, v_peak=V_PEAK):
    """
    Unified formula: phenomenological background + Breit-Wigner peak.

    sigma_m(v) = sigma_0 * (100/v)^A_SLOPE
                + sigma_peak * Gamma^2 / (4(v - v_peak)^2 + Gamma^2)
    """
    background = sigma_0 * (100.0 / v_kms) ** a_slope
    # Breit-Wigner (symmetric form, velocity-space)
    bw = sigma_peak * gamma**2 / (4.0 * (v_kms - v_peak)**2 + gamma**2)
    return background + bw


# Channels (same as v40.28, 20 channels)
CHANNELS = [
    ("Cloud-9 peak",         29.4,   87.0, 348.0),
    ("Cloud-9 kinematic",    28.0,   87.0, 348.0),
    ("Horigome v=10",        10.0,    0.0,   0.8),
    ("Horigome v=15",        15.0,    0.0,   0.8),
    ("Horigome v=20",        20.0,    0.0,   0.8),
    ("Andrade cluster",     1458.0,   0.0,   0.13),
    ("O'Donnell",           2090.0,   0.0,   0.613),
    ("Jee 2026",            1500.0,   0.0,   0.22),
    ("Gilman 2023",         1000.0,   0.0,   0.5),
    ("SPARC",                100.0,   0.03,  0.5),
    ("Streams",              300.0,   0.05,  1.0),
    ("Bullet",              3000.0,   0.0,   0.1),
    ("UFD cores obs",        15.0,    0.0,   0.5),
    ("Extreme UFD bound",     5.0,    0.0,   5.0),
    ("LyA forest",            50.0,   0.005, 0.5),
    ("v=500",                500.0,   0.001, 0.1),
    ("dSph core v=5",         5.0,    0.5,   5.0),
    ("dSph core v=10",       10.0,    0.3,   1.0),
    ("dSph core v=15",       15.0,    0.2,   0.8),
    ("dSph core v=20",       20.0,    0.1,   0.5),
]


def evaluate(a_slope, sigma_0, sigma_peak, gamma):
    pass_count = 0
    for name, v, lo, hi in CHANNELS:
        sm = sigma_m_unified(v, a_slope, sigma_0, sigma_peak, gamma)
        if lo <= sm <= hi:
            pass_count += 1
    return pass_count


if __name__ == "__main__":
    print("=" * 80)
    print("v40.31: Unified formula - phenomenological Breit-Wigner")
    print("=" * 80)
    print()
    print("Unified formula:")
    print("  sigma_m(v) = sigma_0 * (100/v)^A_SLOPE")
    print("              + sigma_peak * Gamma^2 / (4(v - v_peak)^2 + Gamma^2)")
    print()
    print("This bridges v40.24 (Breit-Wigner) and v40.28 (Gaussian).")
    print()

    # Test: v40.28 Gaussian equivalent
    # v40.28 had: A_SLOPE=0.4, sigma_0=0.153, sigma_peak=174, sigma_1=1.5 (Gaussian)
    # For equivalent Breit-Wigner FWHM: BW_FWHM = 2*Gamma, Gauss_FWHM = 2.355*sigma_1
    # So Gamma_equivalent = 2.355*sigma_1/2 = 1.18*sigma_1
    print("=" * 80)
    print("TEST 1: Equivalent Breit-Wigner for v40.28 Gaussian")
    print("=" * 80)
    print(f"v40.28 Gaussian: sigma_1 = 1.5, equivalent Breit-Wigner Gamma = {1.18 * 1.5:.3f}")
    sigma_1_eq_gamma = 1.18 * 1.5
    score_equivalent = evaluate(0.4, 0.153, 174, sigma_1_eq_gamma)
    print(f"Score with equivalent Gamma = {sigma_1_eq_gamma:.3f}: {score_equivalent}/20")
    print()

    # Test: narrower Gamma
    print("=" * 80)
    print("TEST 2: Narrower Gamma to suppress dSph tails")
    print("=" * 80)
    print(f"Testing: A_SLOPE=0.4, sigma_0=0.153, sigma_peak=174, varying Gamma")
    print()
    print(f"{'Gamma':<10s} {'Score':>10s} {'sigma_m(20)':>15s} {'sigma_m(15)':>15s} {'sigma_m(10)':>15s}")
    for gamma in [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]:
        score = evaluate(0.4, 0.153, 174, gamma)
        sm_20 = sigma_m_unified(20, 0.4, 0.153, 174, gamma)
        sm_15 = sigma_m_unified(15, 0.4, 0.153, 174, gamma)
        sm_10 = sigma_m_unified(10, 0.4, 0.153, 174, gamma)
        print(f"{gamma:<10.3f} {score:>10d} {sm_20:>15.4e} {sm_15:>15.4e} {sm_10:>15.4e}")
    print()

    # 4D scan to find optimal parameters
    print("=" * 80)
    print("TEST 3: 4D scan (A_SLOPE, sigma_0, sigma_peak, Gamma)")
    print("=" * 80)

    a_slopes = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    sigma_0s = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    sigma_peaks = [100, 150, 174, 200, 250, 300]
    gammas = [0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]

    total = len(a_slopes) * len(sigma_0s) * len(sigma_peaks) * len(gammas)
    print(f"Grid: {total} configurations")

    results = []
    for a in a_slopes:
        for s0 in sigma_0s:
            for sp in sigma_peaks:
                for g in gammas:
                    score = evaluate(a, s0, sp, g)
                    results.append({
                        'a_slope': a, 'sigma_0': s0,
                        'sigma_peak': sp, 'gamma': g,
                        'score': score
                    })

    results.sort(key=lambda x: -x['score'])
    print()
    print("TOP 20 (4D scan with Breit-Wigner formula):")
    print(f"{'Rank':<5s} {'A_SLOPE':>8s} {'sigma_0':>10s} {'sigma_peak':>10s} {'Gamma':>8s} {'Score':>10s}")
    for i, r in enumerate(results[:20]):
        print(f"{i+1:<5d} {r['a_slope']:>8.3f} {r['sigma_0']:>10.5f} {r['sigma_peak']:>10.1f} {r['gamma']:>8.3f} {r['score']:>5d}/20")

    # Score distribution
    score_dist = {}
    for r in results:
        s = r['score']
        score_dist[s] = score_dist.get(s, 0) + 1
    print()
    print("Score distribution:")
    for s in sorted(score_dist.keys(), reverse=True):
        print(f"  {s}/20: {score_dist[s]} configurations ({score_dist[s]/len(results)*100:.1f}%)")

    # Show top config
    if results:
        top = results[0]
        print()
        print("=" * 80)
        print("TOP CONFIGURATION (unified Breit-Wigner)")
        print("=" * 80)
        print(f"A_SLOPE = {top['a_slope']:.3f}")
        print(f"sigma_0 = {top['sigma_0']:.5f}")
        print(f"sigma_peak = {top['sigma_peak']:.1f}")
        print(f"Gamma = {top['gamma']:.3f}")
        print(f"Score: {top['score']}/20")
        print()
        print("Channel-by-channel check:")
        for name, v, lo, hi in CHANNELS:
            sm = sigma_m_unified(v, top['a_slope'], top['sigma_0'],
                                  top['sigma_peak'], top['gamma'])
            passed = lo <= sm <= hi
            status = "PASS" if passed else "FAIL"
            print(f"  {name:<25s} v={v:>6.1f} sigma/m={sm:>12.4e} [{lo}, {hi}] {status}")

    # Comparison to v40.28
    print()
    print("=" * 80)
    print("COMPARISON: v40.28 (Gaussian) vs v40.31 (Breit-Wigner)")
    print("=" * 80)
    print()
    print("v40.28 Gaussian: 30/6,000 = 0.5% basin at 20/20")
    bw_20 = score_dist.get(20, 0)
    print(f"v40.31 Breit-Wigner: {bw_20}/{total} = {bw_20/total*100:.1f}% at 20/20")
    if bw_20 > 30:
        print(f"  -> Breit-Wigner basin is {bw_20 - 30} larger than Gaussian")
    elif bw_20 > 0:
        print(f"  -> Breit-Wigner basin is {30 - bw_20} smaller than Gaussian")
    else:
        print(f"  -> No 20/20 basin in Breit-Wigner formula")

    # Save results
    output_path = os.path.join(_PROJECT, "v0.3-prelim", "data", "results",
                                "v40_31_unified.json")
    output = {
        'scan_v40_31': [{
            'a_slope': r['a_slope'], 'sigma_0': r['sigma_0'],
            'sigma_peak': r['sigma_peak'], 'gamma': r['gamma'],
            'score': r['score']
        } for r in results[:50]]
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nTop 50 results saved to {output_path}")
