#!/usr/bin/env python3
"""
v40.26: Data-Driven Parameter Scan for v19.2-F (private curiosity project)

User decision (2026-10-17): Path B (multi-resonance exploration), data-driven approach.
The goal: maximize DM conditions covered while staying within observed data boundaries.

Strategy:
1. 2D scan over background parameters (A_SLOPE, sigma_0)
2. For each (A_SLOPE, sigma_0), check all 22+ observational channels
3. Find winning configurations (most channels satisfied)
4. If 2D scan doesn't resolve dSph, extend to 3D (with multi-resonance)
5. Report results honestly
"""
import os
import sys
import json
import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

# Add project code directory to path
_PROJECT = r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator"
sys.path.insert(0, _PROJECT)
sys.path.insert(0, os.path.join(_PROJECT, "v0.3-prelim", "code"))

from constants import ALPHA_D, C_KMS, HBAR_C_GEV_CM, M_CHI_GEV


# ============================================================================
# FLEXIBLE sigma/m(v) FRAMEWORK
# ============================================================================
def sigma_m_flexible(v_kms: float, a_slope: float, sigma_0: float,
                      v_target: float, sigma_peak: float, sigma_1: float,
                      resonance_2: dict = None) -> float:
    """
    Flexible sigma/m(v) = background + N Gaussian resonances.

    Default: 1 resonance (Cloud-9 anchor at v=29.4).
    Optional 2nd resonance via resonance_2 dict.

    Parameters
    ----------
    v_kms : float
        Velocity in km/s
    a_slope : float
        Background velocity slope
    sigma_0 : float
        Background amplitude at v=100 km/s
    v_target : float
        Resonance 1 center
    sigma_peak : float
        Resonance 1 peak amplitude
    sigma_1 : float
        Resonance 1 Gaussian width
    resonance_2 : dict, optional
        Second resonance {v_target, sigma_peak, sigma_1}

    Returns
    -------
    float
        sigma/m in cm^2/g
    """
    # Background (power-law)
    background = sigma_0 * (100.0 / v_kms) ** a_slope

    # Resonance 1
    resonance_1 = sigma_peak * math.exp(-0.5 * ((v_kms - v_target) / sigma_1) ** 2)

    # Optional Resonance 2
    resonance_2_contrib = 0.0
    if resonance_2 is not None:
        r2 = resonance_2
        resonance_2_contrib = r2['sigma_peak'] * math.exp(
            -0.5 * ((v_kms - r2['v_target']) / r2['sigma_1']) ** 2)

    return background + resonance_1 + resonance_2_contrib


# ============================================================================
# CHANNEL CONSTRAINTS (OBSERVED DATA BOUNDARIES)
# ============================================================================
@dataclass
class Channel:
    """An observational channel with v_target and IN BAND range."""
    name: str
    v_kms: float
    sigma_m_min: float  # cm^2/g
    sigma_m_max: float  # cm^2/g
    source: str = ""

    def check(self, sigma_m: float) -> bool:
        return self.sigma_m_min <= sigma_m <= self.sigma_m_max


# Channels from v19.2-F PAPER V1 DRAFT
CHANNELS = [
    # Cloud-9 anchor (resonance)
    Channel("Cloud-9 (resonance peak)", 29.4, 87.0, 348.0,
            "v19.2-F PAPER V1 DRAFT (canonical sigma_peak=174)"),

    # Cloud-9 kinematic (slightly off-peak)
    Channel("Cloud-9 (kinematic)", 28.0, 87.0, 348.0,
            "v19.2-F PAPER V1 DRAFT (sigma/m(28)=166)"),

    # dSph exclusion (Horigome+ 2025)
    Channel("Horigome+ 2025 dSph (v=10, w=10)", 10.0, 0.0, 0.8,
            "arXiv:2503.13650, 95% CL, w=10 km/s"),
    Channel("Horigome+ 2025 dSph (v=15)", 15.0, 0.0, 0.8,
            "arXiv:2503.13650, 95% CL, w=10 km/s"),
    Channel("Horigome+ 2025 dSph (v=20)", 20.0, 0.0, 0.8,
            "arXiv:2503.13650, 95% CL, w=10 km/s"),

    # Cluster constraints
    Channel("Andrade+ 2022 cluster (v=1458)", 1458.0, 0.0, 0.13,
            "MNRAS 510, 54 (Andrade+ 2022)"),
    Channel("O'Donnell+ 2025 (v<2090)", 2090.0, 0.0, 0.613,
            "arXiv:2508.20179, 95% CL"),
    Channel("Jee, Park, Lee 2026 (v=1500)", 1500.0, 0.0, 0.22,
            "arXiv:2605.00093, 68% CL"),
    Channel("Gilman+ 2023 (v=1000)", 1000.0, 0.0, 0.5,
            "arXiv:2207.13111, PRD 107, 103008"),

    # SPARC (rotation curves)
    Channel("SPARC (v=100)", 100.0, 0.03, 0.5,
            "SPARC rotation curves, Elbert+ 2015"),

    # Streams / subhalos
    Channel("Stellar streams (v=300)", 300.0, 0.05, 1.0,
            "Stream kinematic constraints"),

    # Bullet Cluster
    Channel("Bullet Cluster (v=3000)", 3000.0, 0.0, 0.1,
            "Bullet Cluster shock"),

    # UFD cores (Sánchez Almeida+ 2025)
    Channel("UFD cores (v=15, observational)", 15.0, 0.0, 0.5,
            "Sánchez Almeida+ 2025, A&A 704, A210"),

    # Extreme UFD
    Channel("Extreme UFD (v=5)", 5.0, 0.0, 5.0,
            "Loose bound, kinematic estimate"),

    # Lyman-alpha forest (rough)
    Channel("Lyman-alpha forest (v=50)", 50.0, 0.005, 0.5,
            "Rough bound from LyA forest"),

    # Edge of parameter space
    Channel("v=500 (intermediate)", 500.0, 0.001, 0.1,
            "Intermediate velocity scale"),
]


def evaluate_channels(a_slope: float, sigma_0: float,
                       v_target: float = 29.4, sigma_peak: float = 174.0,
                       sigma_1: float = 4.4, resonance_2: dict = None) -> Dict:
    """
    Evaluate all channels for a given parameter configuration.

    Returns
    -------
    Dict with 'pass_count', 'fail_count', 'channel_results', 'sigma_m_values'
    """
    results = []
    sigma_m_values = {}

    for ch in CHANNELS:
        sm = sigma_m_flexible(ch.v_kms, a_slope, sigma_0, v_target, sigma_peak,
                               sigma_1, resonance_2)
        passed = ch.check(sm)
        results.append({
            'name': ch.name,
            'v_kms': ch.v_kms,
            'sigma_m': sm,
            'min': ch.sigma_m_min,
            'max': ch.sigma_m_max,
            'passed': passed
        })
        sigma_m_values[ch.name] = sm

    pass_count = sum(1 for r in results if r['passed'])
    fail_count = len(results) - pass_count

    return {
        'pass_count': pass_count,
        'fail_count': fail_count,
        'total': len(results),
        'channel_results': results,
        'sigma_m_values': sigma_m_values,
        'a_slope': a_slope,
        'sigma_0': sigma_0,
        'v_target': v_target,
        'sigma_peak': sigma_peak,
        'sigma_1': sigma_1,
        'resonance_2': resonance_2,
    }


# ============================================================================
# 2D PARAMETER SCAN: (a_slope, sigma_0)
# ============================================================================
def scan_2d_background(a_slope_range: Tuple[float, float] = (0.5, 2.5),
                        sigma_0_range: Tuple[float, float] = (0.001, 0.2),
                        a_slope_steps: int = 40,
                        sigma_0_steps: int = 40) -> List[Dict]:
    """
    2D scan over (a_slope, sigma_0) with single Cloud-9 resonance.

    Returns list of evaluation results, sorted by pass_count (descending).
    """
    print("=" * 70)
    print("v40.26: 2D PARAMETER SCAN")
    print("=" * 70)
    print(f"Scanning a_slope in [{a_slope_range[0]}, {a_slope_range[1]}], {a_slope_steps} steps")
    print(f"Scanning sigma_0 in [{sigma_0_range[0]}, {sigma_0_range[1]}], {sigma_0_steps} steps")
    print(f"Total configurations: {a_slope_steps * sigma_0_steps}")
    print()

    a_slopes = np.linspace(a_slope_range[0], a_slope_range[1], a_slope_steps)
    sigma_0s = np.linspace(sigma_0_range[0], sigma_0_range[1], sigma_0_steps)

    results = []
    for a in a_slopes:
        for s0 in sigma_0s:
            r = evaluate_channels(a, s0)
            results.append(r)

    # Sort by pass_count (descending), then by fail count
    results.sort(key=lambda x: (-x['pass_count'], x['fail_count']))

    return results


# ============================================================================
# EXTENDED SCAN: 2D background + 2nd resonance parameters
# ============================================================================
def scan_with_2nd_resonance(top_n: int = 5) -> List[Dict]:
    """
    For the top-N winning (a_slope, sigma_0) configurations, try adding
    a 2nd resonance and see if it helps.
    """
    print()
    print("=" * 70)
    print(f"EXTENDED SCAN: 2nd resonance exploration for top {top_n} configurations")
    print("=" * 70)

    # First run the 2D scan
    base_results = scan_2d_background(a_slope_steps=20, sigma_0_steps=20)

    # Take top N
    top_configs = base_results[:top_n]

    extended_results = []
    for base in top_configs:
        a = base['a_slope']
        s0 = base['sigma_0']
        # Try a 2nd resonance with v_target in [5, 20], sigma_peak in [10, 200]
        for v2 in [5, 8, 10, 12, 15, 20]:
            for sp2 in [10, 50, 100, 150, 200]:
                for s1_2 in [2, 4, 6]:
                    r2 = {'v_target': v2, 'sigma_peak': sp2, 'sigma_1': s1_2}
                    r = evaluate_channels(a, s0, resonance_2=r2)
                    r['is_extended'] = True
                    extended_results.append(r)

    extended_results.sort(key=lambda x: (-x['pass_count'], x['fail_count']))
    return extended_results[:20]  # Top 20 extended


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    # Step 1: 2D scan
    print("Running 2D scan (a_slope, sigma_0)...")
    results_2d = scan_2d_background(a_slope_steps=30, sigma_0_steps=30)

    # Show top 10
    print()
    print("=" * 70)
    print("TOP 10 CONFIGURATIONS (2D scan)")
    print("=" * 70)
    print(f"{'Rank':<5s} {'a_slope':>10s} {'sigma_0':>10s} {'Pass':>5s}/{'Total':<5s} {'Failures'}")
    print("-" * 70)
    for i, r in enumerate(results_2d[:10]):
        failures = [cr['name'] for cr in r['channel_results'] if not cr['passed']]
        print(f"{i+1:<5d} {r['a_slope']:>10.3f} {r['sigma_0']:>10.5f} {r['pass_count']:>5d}/{r['total']:<5d} {', '.join(failures[:3])}")

    # Show baseline (v40.24 values)
    print()
    print("=" * 70)
    print("BASELINE (v40.24 values: a_slope=1.93, sigma_0=0.052)")
    print("=" * 70)
    baseline = evaluate_channels(1.93, 0.052)
    print(f"Pass: {baseline['pass_count']}/{baseline['total']}")
    print(f"Failures:")
    for cr in baseline['channel_results']:
        if not cr['passed']:
            print(f"  {cr['name']}: sigma/m = {cr['sigma_m']:.4e} (need [{cr['min']}, {cr['max']}])")

    # Show top config
    print()
    print("=" * 70)
    print("TOP CONFIGURATION DETAIL")
    print("=" * 70)
    top = results_2d[0]
    print(f"a_slope = {top['a_slope']:.3f}, sigma_0 = {top['sigma_0']:.5f}")
    print(f"Pass: {top['pass_count']}/{top['total']}")
    print()
    print(f"{'Channel':<40s} {'sigma/m':>12s} {'Range':>20s} {'Status'}")
    print("-" * 90)
    for cr in top['channel_results']:
        status = "PASS" if cr['passed'] else "FAIL"
        rng = f"[{cr['min']:.3f}, {cr['max']:.3f}]"
        print(f"{cr['name']:<40s} {cr['sigma_m']:>12.4e} {rng:>20s} {status}")

    # Step 2: extended scan with 2nd resonance (if 2D doesn't fully resolve dSph)
    dSph_channels = ['Horigome+ 2025 dSph (v=10, w=10)', 'Horigome+ 2025 dSph (v=15)',
                      'Horigome+ 2025 dSph (v=20)']
    top_dSph_passes = sum(1 for cr in top['channel_results']
                          if cr['name'] in dSph_channels and cr['passed'])

    if top_dSph_passes < 3:
        print()
        print("=" * 70)
        print(f"2D scan did NOT resolve all 3 dSph tensions ({top_dSph_passes}/3).")
        print("Running EXTENDED scan with 2nd resonance...")
        print("=" * 70)
        ext = scan_with_2nd_resonance(top_n=3)
        print()
        print("TOP 5 EXTENDED (with 2nd resonance):")
        for i, r in enumerate(ext[:5]):
            r2 = r.get('resonance_2', {})
            r2_str = f"v2={r2.get('v_target', 'NA')}, sp2={r2.get('sigma_peak', 'NA')}, s1_2={r2.get('sigma_1', 'NA')}" if r2 else "N/A"
            print(f"  #{i+1}: a={r['a_slope']:.3f}, s0={r['sigma_0']:.5f}, "
                  f"2nd_res: {r2_str}, pass={r['pass_count']}/{r['total']}")
    else:
        print()
        print("=" * 70)
        print(f"2D scan RESOLVED all 3 dSph tensions ({top_dSph_passes}/3).")
        print("=" * 70)
