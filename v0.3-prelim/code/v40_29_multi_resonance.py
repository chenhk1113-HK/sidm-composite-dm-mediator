#!/usr/bin/env python3
"""
v40.29: Multi-resonance extension (Tsai 2022) to widen the Goldilocks zone

User directive: Try Option B - add 2nd narrow resonance to widen the v40.28
Goldilocks zone. If successful, review and consider Option A (re-derive alpha_D).

Tsai 2022 dark-QCD predicts MULTIPLE narrow resonances at velocity scales
m[Y(nS)] ~ 2 m_DM. The v40.28 single-resonance model has a 0.5% Goldilocks
zone. A 2nd resonance at v~10-20 km/s could provide the dSph cross-section
WITHOUT requiring A_SLOPE~0.4 (the v40.28 constraint).

Tasks:
1. Build 2-resonance sigma/m(v) model
2. Scan v_target_2 in [3, 25] km/s, sigma_peak_2 in [10, 500] cm^2/g
3. For each (A_SLOPE, sigma_0, sigma_1, v_target_2, sigma_peak_2, sigma_1_2)
   check 20 channels
4. Find basin size vs v40.28 (single resonance)
5. Report whether multi-resonance widens the Goldilocks zone
"""
import os
import sys
import math
import numpy as np
import json

_PROJECT = r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator"
sys.path.insert(0, _PROJECT)
sys.path.insert(0, os.path.join(_PROJECT, "v0.3-prelim", "code"))


def sigma_m_multi(v_kms, a_slope, sigma_0, v_target, sigma_peak, sigma_1,
                    v_target_2=None, sigma_peak_2=None, sigma_1_2=None):
    """
    2-resonance sigma/m(v) model.
    sigma/m(v) = sigma_0 * (100/v)^a_slope
                + sigma_peak * exp(-(v-v_target)^2 / (2*sigma_1^2))
                + sigma_peak_2 * exp(-(v-v_target_2)^2 / (2*sigma_1_2^2))
    """
    background = sigma_0 * (100.0 / v_kms) ** a_slope
    res_1 = sigma_peak * math.exp(-0.5 * ((v_kms - v_target) / sigma_1) ** 2)
    res_2 = 0.0
    if v_target_2 is not None and sigma_peak_2 is not None and sigma_1_2 is not None:
        res_2 = sigma_peak_2 * math.exp(-0.5 * ((v_kms - v_target_2) / sigma_1_2) ** 2)
    return background + res_1 + res_2


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


def evaluate(a_slope, sigma_0, sigma_1, v_target_2=None, sigma_peak_2=None,
              sigma_1_2=None):
    pass_count = 0
    for name, v, lo, hi in CHANNELS:
        sm = sigma_m_multi(v, a_slope, sigma_0, 29.4, 174, sigma_1,
                             v_target_2, sigma_peak_2, sigma_1_2)
        if lo <= sm <= hi:
            pass_count += 1
    return pass_count


if __name__ == "__main__":
    print("=" * 80)
    print("v40.29: Multi-resonance (Tsai 2022) to widen Goldilocks zone")
    print("=" * 80)
    print()
    print("Strategy: Fix Cloud-9 (v=29.4, sigma_peak=174, sigma_1=1.5)")
    print("Add 2nd resonance at v_target_2 in [3, 25] km/s")
    print("Vary: A_SLOPE, sigma_0 (background), v_target_2, sigma_peak_2, sigma_1_2")
    print()

    # Test 1: v40.28 winning config WITHOUT 2nd resonance (baseline)
    v40_28_score = evaluate(0.4, 0.153, 1.5)
    print(f"v40.28 baseline (no 2nd resonance): {v40_28_score}/20")
    print()

    # Test 2: Add 2nd resonance at various positions
    # Try v_target_2 in [5, 10, 15, 20], sigma_peak_2 in [10, 50, 100, 200, 300, 500]
    # For each, find best A_SLOPE and sigma_0

    # Quick test: scan 2nd resonance params
    print("=" * 80)
    print("TEST: 2nd resonance parameter exploration")
    print("=" * 80)
    print("Holding (A_SLOPE=0.4, sigma_0=0.153, sigma_1=1.5) FIXED, varying 2nd peak")
    print()
    print(f"{'v_target_2':<12s} {'sigma_peak_2':>12s} {'sigma_1_2':>10s} {'Score':>10s}")
    print("-" * 60)

    best_with_2nd = []
    for v2 in [5, 7, 10, 12, 15, 18, 20, 25]:
        for sp2 in [10, 30, 50, 100, 150, 200, 300]:
            for s1_2 in [1.0, 2.0, 3.0, 5.0]:
                score = evaluate(0.4, 0.153, 1.5, v2, sp2, s1_2)
                if score >= 18:
                    best_with_2nd.append((score, v2, sp2, s1_2))
                    print(f"{v2:<12} {sp2:>12} {s1_2:>10.1f} {score:>5d}/20")

    # Now do a wider scan: vary all 6 params
    print()
    print("=" * 80)
    print("WIDE SCAN: 6D (A_SLOPE, sigma_0, v_target_2, sigma_peak_2, sigma_1_2)")
    print("=" * 80)

    a_slopes = np.linspace(0.2, 1.5, 8)  # 8 values
    sigma_0s = np.linspace(0.05, 0.4, 8)  # 8 values
    v_target_2s = [5, 10, 15, 20]  # 4 values
    sigma_peak_2s = [50, 100, 200, 400]  # 4 values
    sigma_1_2s = [1.0, 2.0, 4.0]  # 3 values

    total = 8 * 8 * 4 * 4 * 3
    print(f"Grid size: {total} configurations")
    print(f"  A_SLOPE: {a_slopes[0]:.2f} to {a_slopes[-1]:.2f} ({len(a_slopes)} steps)")
    print(f"  sigma_0: {sigma_0s[0]:.3f} to {sigma_0s[-1]:.3f} ({len(sigma_0s)} steps)")
    print(f"  v_target_2: {v_target_2s}")
    print(f"  sigma_peak_2: {sigma_peak_2s}")
    print(f"  sigma_1_2: {sigma_1_2s}")
    print()

    results = []
    counter = 0
    for a in a_slopes:
        for s0 in sigma_0s:
            for v2 in v_target_2s:
                for sp2 in sigma_peak_2s:
                    for s1_2 in sigma_1_2s:
                        score = evaluate(a, s0, 1.5, v2, sp2, s1_2)
                        results.append({
                            'a_slope': a, 'sigma_0': s0, 'v_target_2': v2,
                            'sigma_peak_2': sp2, 'sigma_1_2': s1_2,
                            'score': score
                        })
                        counter += 1
                        if counter % 500 == 0:
                            print(f"  Progress: {counter}/{total}")

    results.sort(key=lambda x: -x['score'])
    print()
    print(f"Scan complete. {len(results)} configurations tested.")

    # Show top 20
    print()
    print("=" * 80)
    print(f"TOP 20 (6D multi-resonance scan)")
    print("=" * 80)
    print(f"{'Rank':<5s} {'A_SLOPE':>8s} {'sigma_0':>10s} {'v_target_2':>10s} {'sigma_peak_2':>12s} {'sigma_1_2':>10s} {'Score':>10s}")
    for i, r in enumerate(results[:20]):
        print(f"{i+1:<5d} {r['a_slope']:>8.3f} {r['sigma_0']:>10.5f} {r['v_target_2']:>10.1f} {r['sigma_peak_2']:>12.1f} {r['sigma_1_2']:>10.1f} {r['score']:>5d}/20")

    # Score distribution
    score_dist = {}
    for r in results:
        s = r['score']
        score_dist[s] = score_dist.get(s, 0) + 1
    print()
    print("Score distribution:")
    for s in sorted(score_dist.keys(), reverse=True):
        print(f"  {s}/20: {score_dist[s]} configurations ({score_dist[s]/len(results)*100:.1f}%)")

    # Comparison to v40.28 (single resonance)
    print()
    print("=" * 80)
    print("COMPARISON: v40.28 (single) vs v40.29 (multi-resonance)")
    print("=" * 80)
    print()
    print(f"v40.28 single resonance basin (0.5% of 6000): 30 configurations pass 20/20")
    print(f"v40.29 multi-resonance: {score_dist.get(20, 0)} configurations pass 20/20 out of {len(results)}")
    print()
    if score_dist.get(20, 0) > 30:
        print(f"  -> v40.29 has {score_dist.get(20, 0) - 30} more 20/20 configs than v40.28")
        print(f"  -> Multi-resonance DOES widen the Goldilocks zone")
    else:
        print(f"  -> Multi-resonance does NOT widen the Goldilocks zone")
        print(f"  -> v40.28 single-resonance is optimal")

    # Show top config
    print()
    print("=" * 80)
    print("TOP CONFIGURATION (multi-resonance)")
    print("=" * 80)
    top = results[0]
    print(f"A_SLOPE = {top['a_slope']:.3f}")
    print(f"sigma_0 = {top['sigma_0']:.5f}")
    print(f"Cloud-9: v_target=29.4, sigma_peak=174, sigma_1=1.5")
    print(f"2nd peak: v_target_2={top['v_target_2']}, sigma_peak_2={top['sigma_peak_2']}, sigma_1_2={top['sigma_1_2']}")
    print(f"Score: {top['score']}/20")
    print()
    print("Channel-by-channel check:")
    for name, v, lo, hi in CHANNELS:
        sm = sigma_m_multi(v, top['a_slope'], top['sigma_0'], 29.4, 174, 1.5,
                             top['v_target_2'], top['sigma_peak_2'], top['sigma_1_2'])
        passed = lo <= sm <= hi
        status = "PASS" if passed else "FAIL"
        print(f"  {name:<25s} v={v:>6.1f} sigma/m={sm:>12.4e} [{lo}, {hi}] {status}")

    # Save results
    output_path = os.path.join(_PROJECT, "v0.3-prelim", "data", "results",
                                "v40_29_multi_resonance.json")
    output = {
        'scan_v40_29': [{
            'a_slope': r['a_slope'], 'sigma_0': r['sigma_0'],
            'v_target_2': r['v_target_2'], 'sigma_peak_2': r['sigma_peak_2'],
            'sigma_1_2': r['sigma_1_2'], 'score': r['score']
        } for r in results[:50]]
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nTop 50 results saved to {output_path}")
