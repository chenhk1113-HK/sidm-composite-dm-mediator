#!/usr/bin/env python3
"""
v40.27: 3D Parameter Scan (A_SLOPE, sigma_0, sigma_1) - private curiosity project

User decision (2026-10-17): Path B (multi-resonance exploration), data-driven approach.
v40.26 found: 2D scan (A_SLOPE, sigma_0) caps at 13/16 channels. Failures at v=15, v=20
are due to Cloud-9 resonance tail, not background. Need to scan sigma_1 too.

This v40.27: 3D scan over (A_SLOPE, sigma_0, sigma_1) to test if narrower
Cloud-9 resonance can resolve the dSph tension at v=15, v=20.
"""
import os
import sys
import math
import numpy as np
import json
from dataclasses import dataclass, asdict

_PROJECT = r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator"
sys.path.insert(0, _PROJECT)
sys.path.insert(0, os.path.join(_PROJECT, "v0.3-prelim", "code"))


def sigma_m_flexible(v_kms, a_slope, sigma_0, v_target, sigma_peak, sigma_1,
                     resonance_2=None):
    background = sigma_0 * (100.0 / v_kms) ** a_slope
    resonance_1 = sigma_peak * math.exp(-0.5 * ((v_kms - v_target) / sigma_1) ** 2)
    r2_contrib = 0.0
    if resonance_2 is not None:
        r2 = resonance_2
        r2_contrib = r2['sigma_peak'] * math.exp(
            -0.5 * ((v_kms - r2['v_target']) / r2['sigma_1']) ** 2)
    return background + resonance_1 + r2_contrib


@dataclass
class Channel:
    name: str
    v_kms: float
    sigma_m_min: float
    sigma_m_max: float
    source: str = ""


CHANNELS = [
    Channel("Cloud-9 peak", 29.4, 87.0, 348.0, "PAPER V1 DRAFT canonical"),
    Channel("Cloud-9 kinematic", 28.0, 87.0, 348.0, "sigma/m(28)=166"),
    Channel("Horigome v=10", 10.0, 0.0, 0.8, "arXiv:2503.13650 w=10"),
    Channel("Horigome v=15", 15.0, 0.0, 0.8, "arXiv:2503.13650 w=10"),
    Channel("Horigome v=20", 20.0, 0.0, 0.8, "arXiv:2503.13650 w=10"),
    Channel("Andrade cluster", 1458.0, 0.0, 0.13, "MNRAS 510, 54"),
    Channel("O'Donnell", 2090.0, 0.0, 0.613, "arXiv:2508.20179"),
    Channel("Jee 2026", 1500.0, 0.0, 0.22, "arXiv:2605.00093"),
    Channel("Gilman 2023", 1000.0, 0.0, 0.5, "arXiv:2207.13111"),
    Channel("SPARC", 100.0, 0.03, 0.5, "Elbert+ 2015"),
    Channel("Streams", 300.0, 0.05, 1.0, "Stream kinematic"),
    Channel("Bullet", 3000.0, 0.0, 0.1, "Bullet shock"),
    Channel("UFD cores obs", 15.0, 0.0, 0.5, "Sánchez Almeida 2025"),
    Channel("Extreme UFD", 5.0, 0.0, 5.0, "Loose bound"),
    Channel("LyA forest", 50.0, 0.005, 0.5, "Rough bound"),
    Channel("v=500", 500.0, 0.001, 0.1, "Intermediate scale"),
]


def evaluate(a_slope, sigma_0, sigma_1, v_target=29.4, sigma_peak=174.0,
              resonance_2=None):
    results = []
    for ch in CHANNELS:
        sm = sigma_m_flexible(ch.v_kms, a_slope, sigma_0, v_target, sigma_peak,
                              sigma_1, resonance_2)
        passed = ch.sigma_m_min <= sm <= ch.sigma_m_max
        results.append({
            'name': ch.name, 'v_kms': ch.v_kms, 'sigma_m': sm,
            'min': ch.sigma_m_min, 'max': ch.sigma_m_max, 'passed': passed
        })
    pass_count = sum(1 for r in results if r['passed'])
    return {
        'a_slope': a_slope, 'sigma_0': sigma_0, 'sigma_1': sigma_1,
        'pass_count': pass_count, 'fail_count': len(CHANNELS) - pass_count,
        'total': len(CHANNELS), 'channel_results': results,
        'resonance_2': resonance_2
    }


def scan_3d(a_slope_range=(0.3, 2.0), a_steps=20,
              sigma_0_range=(0.01, 0.3), s0_steps=20,
              sigma_1_range=(0.5, 6.0), s1_steps=12):
    print("=" * 70)
    print("v40.27: 3D PARAMETER SCAN (A_SLOPE, sigma_0, sigma_1)")
    print("=" * 70)
    print(f"Scanning a_slope in {a_slope_range} ({a_steps} steps)")
    print(f"Scanning sigma_0 in {sigma_0_range} ({s0_steps} steps)")
    print(f"Scanning sigma_1 in {sigma_1_range} ({s1_steps} steps)")
    total = a_steps * s0_steps * s1_steps
    print(f"Total configurations: {total}")
    print()

    a_slopes = np.linspace(*a_slope_range, a_steps)
    sigma_0s = np.linspace(*sigma_0_range, s0_steps)
    sigma_1s = np.linspace(*sigma_1_range, s1_steps)

    results = []
    counter = 0
    for a in a_slopes:
        for s0 in sigma_0s:
            for s1 in sigma_1s:
                r = evaluate(a, s0, s1)
                results.append(r)
                counter += 1
                if counter % 1000 == 0:
                    print(f"  Progress: {counter}/{total} ({counter/total*100:.0f}%)")

    results.sort(key=lambda x: (-x['pass_count'], x['fail_count']))

    print()
    print(f"Scan complete. {len(results)} configurations tested.")
    return results


def scan_with_multi_resonance(top_n=5):
    """For top-N 3D configs, try adding a 2nd resonance to fix v=20."""
    print()
    print("=" * 70)
    print("EXTENDED: 2nd resonance exploration for top configs")
    print("=" * 70)

    # Quick 3D scan
    base = scan_3d(a_steps=12, s0_steps=12, s1_steps=8)

    # Find configs that pass Horigome v=10 but FAIL v=15 or v=20
    candidates = []
    for r in base[:50]:
        dsph = {cr['name']: cr for cr in r['channel_results']
                if 'Horigome' in cr['name']}
        if (dsph.get('Horigome v=10', {}).get('passed', False) and
            not (dsph.get('Horigome v=15', {}).get('passed', False) and
                 dsph.get('Horigome v=20', {}).get('passed', False))):
            candidates.append(r)
    candidates = candidates[:top_n]
    print(f"Candidates for 2nd resonance exploration: {len(candidates)}")

    extended = []
    for c in candidates:
        a, s0, s1 = c['a_slope'], c['sigma_0'], c['sigma_1']
        # Try 2nd resonance at v=10, 15, 20 with various amplitudes
        for v2 in [10, 15, 20]:
            for sp2 in [50, 100, 200]:
                r2 = {'v_target': v2, 'sigma_peak': sp2, 'sigma_1': 3.0}
                r = evaluate(a, s0, s1, resonance_2=r2)
                extended.append(r)

    extended.sort(key=lambda x: (-x['pass_count'], x['fail_count']))
    return extended[:10]


if __name__ == "__main__":
    # 3D scan
    results = scan_3d()
    print()
    print("=" * 70)
    print("TOP 20 (3D scan)")
    print("=" * 70)
    print(f"{'Rank':<5s} {'a_slope':>8s} {'sigma_0':>10s} {'sigma_1':>8s} {'Pass':>5s}/{'Total':<5s}")
    for i, r in enumerate(results[:20]):
        print(f"{i+1:<5d} {r['a_slope']:>8.3f} {r['sigma_0']:>10.5f} {r['sigma_1']:>8.3f} {r['pass_count']:>5d}/{r['total']:<5d}")

    # Show top config detail
    print()
    print("=" * 70)
    print("TOP CONFIGURATION")
    print("=" * 70)
    top = results[0]
    print(f"a_slope = {top['a_slope']:.3f}, sigma_0 = {top['sigma_0']:.5f}, sigma_1 = {top['sigma_1']:.3f}")
    print(f"Pass: {top['pass_count']}/{top['total']}")
    print()
    print(f"{'Channel':<30s} {'sigma/m':>12s} {'Range':>20s} {'Status'}")
    for cr in top['channel_results']:
        status = "PASS" if cr['passed'] else "FAIL"
        print(f"  {cr['name']:<28s} {cr['sigma_m']:>12.4e} [{cr['min']:.3f}, {cr['max']:.3f}] {status}")

    # If 16/16 not achieved, try multi-resonance
    if top['pass_count'] < top['total']:
        print()
        print("=" * 70)
        print("3D scan did not achieve 16/16. Running multi-resonance extension...")
        print("=" * 70)
        ext = scan_with_multi_resonance()
        print()
        print("TOP 10 EXTENDED (with 2nd resonance):")
        for i, r in enumerate(ext[:10]):
            r2 = r.get('resonance_2', {})
            r2_str = (f"v2={r2.get('v_target')}, sp2={r2.get('sigma_peak')}, s1_2={r2.get('sigma_1')}"
                      if r2 else "N/A")
            print(f"  #{i+1}: a={r['a_slope']:.3f}, s0={r['sigma_0']:.5f}, s1={r['sigma_1']:.3f}, "
                  f"2nd: {r2_str}, pass={r['pass_count']}/{r['total']}")
    else:
        print()
        print("=" * 70)
        print(f"3D scan ACHIEVED {top['pass_count']}/{top['total']}!")
        print("=" * 70)

    # Save results to JSON
    output = {
        'scan_3d': [{
            'a_slope': r['a_slope'], 'sigma_0': r['sigma_0'],
            'sigma_1': r['sigma_1'], 'pass_count': r['pass_count'],
            'failures': [cr['name'] for cr in r['channel_results'] if not cr['passed']]
        } for r in results[:50]]
    }
    output_path = os.path.join(_PROJECT, "v0.3-prelim", "data", "results",
                                "v40_27_3d_scan.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nTop 50 results saved to {output_path}")
