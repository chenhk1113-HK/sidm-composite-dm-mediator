#!/usr/bin/env python3
"""
v40.28: 3D Parameter Scan with CORRECTED 20-channel set (Nemotron review feedback)

User directive: data-driven approach within observed data boundaries.
v40.27 review: 16/16 was false positive. Missing lower-bound channels
for dSph core formation. Per Nemotron 120B:
"Typical dSph core formation requires sigma/m > 0.3-0.5 cm^2/g at v~10 km/s"

v40.28:
- Add 4 lower-bound channels for dSph core formation
- Re-run 3D scan (A_SLOPE, sigma_0, sigma_1)
- Find basin that satisfies BOTH upper and lower bounds
- If no basin, document the trade-off
"""
import os
import sys
import math
import numpy as np
import json

_PROJECT = r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator"
sys.path.insert(0, _PROJECT)
sys.path.insert(0, os.path.join(_PROJECT, "v0.3-prelim", "code"))


def sigma_m_flexible(v_kms, a_slope, sigma_0, v_target, sigma_peak, sigma_1):
    background = sigma_0 * (100.0 / v_kms) ** a_slope
    resonance = sigma_peak * math.exp(-0.5 * ((v_kms - v_target) / sigma_1) ** 2)
    return background + resonance


# ============================================================================
# CHANNELS (20 total) — UPPER AND LOWER BOUNDS
# ============================================================================
# Format: (name, v_kms, sigma_m_min, sigma_m_max, source)
CHANNELS = [
    # --- UPPER-BOUND CHANNELS (v40.27 set) ---
    # Cloud-9 anchors
    ("Cloud-9 peak",         29.4,   87.0, 348.0,  "v40.24 canonical"),
    ("Cloud-9 kinematic",    28.0,   87.0, 348.0,  "v40.24 sigma/m(28)=166"),
    # Horigome+ 2025 dSph (upper limit)
    ("Horigome v=10",        10.0,    0.0,   0.8,  "arXiv:2503.13650 w=10"),
    ("Horigome v=15",        15.0,    0.0,   0.8,  "arXiv:2503.13650 w=10"),
    ("Horigome v=20",        20.0,    0.0,   0.8,  "arXiv:2503.13650 w=10"),
    # Cluster constraints
    ("Andrade cluster",     1458.0,   0.0,   0.13, "MNRAS 510, 54"),
    ("O'Donnell",           2090.0,   0.0,   0.613,"arXiv:2508.20179"),
    ("Jee 2026",            1500.0,   0.0,   0.22, "arXiv:2605.00093"),
    ("Gilman 2023",         1000.0,   0.0,   0.5,  "arXiv:2207.13111"),
    # Other channels
    ("SPARC",                100.0,   0.03,  0.5,  "Elbert+ 2015"),
    ("Streams",              300.0,   0.05,  1.0,  "Stream kinematic"),
    ("Bullet",              3000.0,   0.0,   0.1,  "Bullet shock"),
    ("UFD cores obs (S-A 2025)", 15.0, 0.0,   0.5,  "Sánchez Almeida 2025"),
    ("Extreme UFD bound",      5.0,   0.0,   5.0,  "Loose upper"),
    ("LyA forest",            50.0,   0.005, 0.5,  "Rough bound"),
    ("v=500",                500.0,   0.001, 0.1,  "Intermediate"),

    # --- LOWER-BOUND CHANNELS (NEW in v40.28, per Nemotron review) ---
    # dSph core formation (need sigma/m > threshold to form cores)
    # Per Kaplinghat+ 2016, Rocha+ 2013, v19.2-F PAPER V1 DRAFT
    ("dSph core form v=5",    5.0,    0.5,   5.0,  "Kaplinghat 2016, UFD cores"),
    ("dSph core form v=10",  10.0,    0.3,   1.0,  "Rocha 2013, dSph cores"),
    ("dSph core form v=15",  15.0,    0.2,   0.8,  "Kaplinghat 2016, dSph"),
    ("dSph core form v=20",  20.0,    0.1,   0.5,  "Lower velocity scale"),
]


def evaluate(a_slope, sigma_0, sigma_1, v_target=29.4, sigma_peak=174.0,
              verbose=False):
    results = []
    for name, v, lo, hi, src in CHANNELS:
        sm = sigma_m_flexible(v, a_slope, sigma_0, v_target, sigma_peak, sigma_1)
        passed = lo <= sm <= hi
        results.append({
            'name': name, 'v_kms': v, 'sigma_m': sm,
            'min': lo, 'max': hi, 'passed': passed, 'source': src
        })
        if verbose:
            status = "PASS" if passed else "FAIL"
            print(f"  {name:<30s} v={v:>6.1f} sigma/m={sm:>12.4e} range=[{lo}, {hi}] {status}")
    pass_count = sum(1 for r in results if r['passed'])
    return {
        'a_slope': a_slope, 'sigma_0': sigma_0, 'sigma_1': sigma_1,
        'pass_count': pass_count, 'fail_count': len(CHANNELS) - pass_count,
        'total': len(CHANNELS), 'channel_results': results
    }


# ============================================================================
# 3D SCAN
# ============================================================================
def scan_3d(a_range=(0.1, 2.0), a_steps=20,
              s0_range=(0.01, 0.5), s0_steps=20,
              s1_range=(0.5, 6.0), s1_steps=12):
    print("=" * 80)
    print(f"v40.28: 3D scan with 20 channels ({a_steps}x{s0_steps}x{s1_steps} = {a_steps*s0_steps*s1_steps} configs)")
    print("=" * 80)

    a_slopes = np.linspace(*a_range, a_steps)
    sigma_0s = np.linspace(*s0_range, s0_steps)
    sigma_1s = np.linspace(*s1_range, s1_steps)

    results = []
    for a in a_slopes:
        for s0 in sigma_0s:
            for s1 in sigma_1s:
                r = evaluate(a, s0, s1)
                results.append(r)
    results.sort(key=lambda x: -x['pass_count'])
    return results


if __name__ == "__main__":
    # Show what changed
    print("=" * 80)
    print("CHANNEL COMPARISON: v40.27 (16) vs v40.28 (20)")
    print("=" * 80)
    print(f"v40.27 had 16 upper-bound channels.")
    print(f"v40.28 adds 4 lower-bound channels for dSph core formation:")
    print(f"  - dSph core form v=5: need sigma/m in [0.5, 5.0]")
    print(f"  - dSph core form v=10: need sigma/m in [0.3, 1.0]")
    print(f"  - dSph core form v=15: need sigma/m in [0.2, 0.8]")
    print(f"  - dSph core form v=20: need sigma/m in [0.1, 0.5]")
    print()

    # v40.24 baseline
    print("v40.24 baseline (A_SLOPE=1.93, sigma_0=0.052, sigma_1=4.4):")
    r = evaluate(1.93, 0.052, 4.4)
    print(f"  Score: {r['pass_count']}/{r['total']}")
    print("  Failures:")
    for cr in r['channel_results']:
        if not cr['passed']:
            print(f"    {cr['name']}: sigma/m={cr['sigma_m']:.4e} (need [{cr['min']}, {cr['max']}])")
    print()

    # v40.27 winning
    print("v40.27 winning (A_SLOPE=0.300, sigma_0=0.071, sigma_1=1.500):")
    r = evaluate(0.300, 0.071, 1.500)
    print(f"  Score: {r['pass_count']}/{r['total']}")
    print("  Failures:")
    for cr in r['channel_results']:
        if not cr['passed']:
            print(f"    {cr['name']}: sigma/m={cr['sigma_m']:.4e} (need [{cr['min']}, {cr['max']}])")
    print()

    # Run 3D scan
    results = scan_3d(a_steps=20, s0_steps=25, s1_steps=12)
    print(f"Scanned {len(results)} configurations.")

    # Show top
    print()
    print("=" * 80)
    print("TOP 20 (3D scan with 20 channels)")
    print("=" * 80)
    print(f"{'Rank':<5s} {'A_SLOPE':>8s} {'sigma_0':>10s} {'sigma_1':>8s} {'Score':>10s}")
    for i, r in enumerate(results[:20]):
        print(f"{i+1:<5d} {r['a_slope']:>8.3f} {r['sigma_0']:>10.5f} {r['sigma_1']:>8.3f} {r['pass_count']:>5d}/{r['total']}")

    # Distribution
    score_dist = {}
    for r in results:
        s = r['pass_count']
        score_dist[s] = score_dist.get(s, 0) + 1
    print()
    print("Score distribution:")
    for s in sorted(score_dist.keys(), reverse=True):
        print(f"  {s}/{len(CHANNELS)}: {score_dist[s]} configurations ({score_dist[s]/len(results)*100:.1f}%)")

    # Show top config detail
    print()
    print("=" * 80)
    print("TOP CONFIGURATION DETAIL")
    print("=" * 80)
    top = results[0]
    print(f"A_SLOPE = {top['a_slope']:.3f}, sigma_0 = {top['sigma_0']:.5f}, sigma_1 = {top['sigma_1']:.3f}")
    print(f"Score: {top['pass_count']}/{top['total']}")
    print()
    for cr in top['channel_results']:
        status = "PASS" if cr['passed'] else "FAIL"
        print(f"  {cr['name']:<30s} v={cr['v_kms']:>6.1f} sigma/m={cr['sigma_m']:>12.4e} [{cr['min']}, {cr['max']}] {status}")

    # If 20/20 not achieved, find the best trade-off
    if top['pass_count'] < top['total']:
        print()
        print("=" * 80)
        print("TRADE-OFF ANALYSIS")
        print("=" * 80)
        print()
        # Group failures by type
        for cr in top['channel_results']:
            if not cr['passed']:
                if cr['sigma_m'] < cr['min']:
                    print(f"  TOO LOW:  {cr['name']} (sigma/m={cr['sigma_m']:.4e} < {cr['min']})")
                elif cr['sigma_m'] > cr['max']:
                    print(f"  TOO HIGH: {cr['name']} (sigma/m={cr['sigma_m']:.4e} > {cr['max']})")

    # Save top 50 results
    output_path = os.path.join(_PROJECT, "v0.3-prelim", "data", "results",
                                "v40_28_3d_scan.json")
    output = {
        'scan_v40_28': [{
            'a_slope': r['a_slope'], 'sigma_0': r['sigma_0'],
            'sigma_1': r['sigma_1'], 'pass_count': r['pass_count'],
            'failures': [cr['name'] for cr in r['channel_results'] if not cr['passed']]
        } for r in results[:50]]
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nTop 50 results saved to {output_path}")
