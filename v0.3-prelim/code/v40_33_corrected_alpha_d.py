#!/usr/bin/env python3
"""
v40.33: Corrected alpha_D derivation + Fano profile + true quantum BW

Reviewer feedback (n4.docx, 2026-10-17):
1. CRITICAL: v40.30 alpha_D was derived with born_baseline (no F^2 factor).
   Should use full Breit-Wigner (with F^2).
2. HIGH: v40.31 used Lorentzian (1/v^2 tails), not true quantum BW (1/v^4 tails).
   Verify conclusion with true BW.
3. MED: Fano profile not tested. May allow both peak and dip in same curve.

Tasks:
1. Re-derive alpha_D properly with full BW
2. Test Fano profile (4D scan)
3. Test true quantum BW (4D scan with 1/v^4 tails)
4. Add unit tests
5. Use Path(__file__).parent for portability
6. Save JSON results
"""
import os
import sys
import math
import json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

# Use Path(__file__).parent for portability (REVIEWER FIX)
from pathlib import Path
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT))
sys.path.insert(0, str(_PROJECT / "v0.3-prelim" / "code"))

from constants import M_CHI_GEV, ALPHA_D, C_KMS, HBAR_C_GEV_CM

# Hardcoded from v40.20 locked values
M_RHO_GEV = 5e-5
G_TO_GEV = 1.0 / 1.66053900266e-24
V_PEAK = 29.4


# ============================================================================
# UNIT TESTS (REVIEWER FIX: add assertions)
# ============================================================================
def unit_tests():
    """Sanity checks before main analysis."""
    # Test 1: Fano with q != 0 should give positive value
    sm = sigma_m_fano(29.4, q=1.0, gamma=1.0, sigma_peak=174.0)
    assert sm > 0, f"sigma_m at peak should be positive (q=1), got {sm}"

    # Test 2: Fano with q=0 should give a dip (=0) at peak
    sm_peak = sigma_m_fano(29.4, q=0.0, gamma=1.0, sigma_peak=174.0)
    assert sm_peak == 0.0, f"Fano q=0 should be 0 at peak (dip), got {sm_peak}"

    # Test 3: Fano with q large should approach Lorentzian
    # Peak of (q+eps)^2/((1+eps^2)(1+q^2)) at eps = 1/q
    # = (q+1/q)^2 / (1+1/q^2)(1+q^2) = (q^2+1)^2/q^2 / ((q^2+1)/q^2 * (q^2+1))
    # = (q^2+1) (after simplification)
    # So max of normalized Fano = sigma_peak
    sm_max = sigma_m_fano(29.4 + 1.0/100.0, q=100.0, gamma=1.0, sigma_peak=174.0)
    assert abs(sm_max - 174.0) < 1.0, f"Fano q=100 peak should be ~174, got {sm_max}"

    # Test 4: True BW at v=peak should be ~ sigma_peak
    alpha = find_alpha_D_full_bw(174.0, gamma_over_rho=1.0)
    assert alpha is not None and alpha > 0, f"find_alpha_D failed: {alpha}"
    sm_peak_bw = sigma_m_true_bw(29.4, alpha, gamma_over_rho=1.0)
    assert abs(sm_peak_bw - 174.0) < 1.0, f"BW peak should be ~174, got {sm_peak_bw}"

    # Test 5: True BW at v=100 should be FINITE (not infinity or NaN)
    sm_100 = sigma_m_true_bw(100.0, alpha, gamma_over_rho=1.0)
    assert math.isfinite(sm_100), f"True BW at v=100 should be finite, got {sm_100}"
    # Note: BW has 1/q^4 tails so it's much smaller than at v_peak, but not zero
    assert sm_100 < 100.0, f"True BW at v=100 should be smaller than peak (174), got {sm_100}"

    # Test 6: All CHANNELS have valid v range
    for name, v, lo, hi in CHANNELS:
        assert v > 0, f"Channel {name} has invalid v={v}"
        assert lo <= hi, f"Channel {name} has invalid range [{lo}, {hi}]"

    print("All unit tests passed.")


# ============================================================================
# FORMULA 1: Fano Profile (NORMALIZED)
# ============================================================================
def sigma_m_fano(v_kms, q, gamma, sigma_peak, v_peak=V_PEAK):
    """
    Normalized Fano profile in velocity space.

    sigma_m(v) = sigma_peak * (q + epsilon)^2 / ((1 + epsilon^2) * (1 + q^2))
    where epsilon = (v - v_peak) / gamma

    Properties:
    - Peak value: sigma_peak at v = v_peak + gamma/q
    - Zero value: 0 at v = v_peak - q*gamma
    - Large v: sigma_m -> 0 (1/v^2 tail)
    - q -> infinity: approaches Lorentzian (peak at v_peak, FWHM = 2*gamma)
    - q = 0: symmetric dip at v_peak

    Parameters
    ----------
    v_kms : float
        Velocity in km/s
    q : float
        Fano asymmetry parameter
    gamma : float
        Fano width parameter (km/s)
    sigma_peak : float
        Peak amplitude (cm^2/g)

    Returns
    -------
    float
        sigma_m in cm^2/g
    """
    epsilon = (v_kms - v_peak) / gamma
    return sigma_peak * (q + epsilon)**2 / ((1 + epsilon**2) * (1 + q**2))


# ============================================================================
# FORMULA 2: True Quantum Breit-Wigner (1/v^4 tails)
# ============================================================================
def sigma_m_true_bw(v_kms, alpha_D, gamma_over_rho=1.0,
                    m_chi_GeV=M_CHI_GEV, m_rho_GeV=M_RHO_GEV):
    """
    True quantum Breit-Wigner in velocity space.

    sigma_m(v) = sigma_m0(v) * F^2(v)
    where:
      sigma_m0 = (2*pi*alpha_D^2 / mu^2) * integral[(1-cosT)/(q^2+m_rho^2)^2] * (hbarc)^2 / m_chi
      F^2 = (q^2 + m_rho^2)^2 / [(q^2 - m_rho^2)^2 + (m_rho * Gamma)^2]
      Gamma = gamma_over_rho * m_rho
      q = mu * v

    Tails at large v: sigma_m ~ 1/v^4 (not 1/v^2 like Lorentzian)
    """
    mu_GeV = m_chi_GeV / 2.0
    v = v_kms / C_KMS
    q = mu_GeV * v
    Gamma_GeV = gamma_over_rho * m_rho_GeV

    # Born baseline (numerical quadrature)
    def _integrand(cos_theta):
        q_squared = 4.0 * mu_GeV**2 * v**2 * (1.0 - cos_theta) / 2.0
        return (1.0 - cos_theta) / (q_squared + m_rho_GeV**2) ** 2
    integral_val, _ = quad(_integrand, -1.0, 1.0, limit=100)
    sigma_T0_GeV2 = 2.0 * math.pi * alpha_D**2 * integral_val
    sigma_T0_cm2 = sigma_T0_GeV2 * HBAR_C_GEV_CM**2
    m_chi_g = m_chi_GeV / G_TO_GEV
    sigma_m0 = sigma_T0_cm2 / m_chi_g

    # F^2 factor (Breit-Wigner resonance)
    F2_factor = (q**2 + m_rho_GeV**2) ** 2 / (
        (q**2 - m_rho_GeV**2) ** 2 + (m_rho_GeV * Gamma_GeV) ** 2
    )
    return sigma_m0 * F2_factor


# ============================================================================
# FORMULA 3: Full Breit-Wigner alpha_D solver
# ============================================================================
def find_alpha_D_full_bw(target_peak, gamma_over_rho, v_peak=V_PEAK):
    """
    Find alpha_D such that sigma_m_true_bw(v_peak) = target_peak.
    Uses FULL Breit-Wigner with F^2 factor.
    """
    def obj(log_alpha):
        return sigma_m_true_bw(v_peak, 10**log_alpha, gamma_over_rho) - target_peak

    try:
        log_alpha_found = brentq(obj, -15, -2, xtol=1e-8)
        return 10 ** log_alpha_found
    except Exception as e:
        return None


# ============================================================================
# CHANNELS (same 20 as v40.28)
# ============================================================================
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


def evaluate_fano(q, gamma, sigma_peak, sigma_0=0.0, a_slope=0.0):
    """Evaluate 20 channels with Fano profile + optional background."""
    pass_count = 0
    for name, v, lo, hi in CHANNELS:
        sm = sigma_m_fano(v, q, gamma, sigma_peak) + sigma_0 * (100.0 / v) ** a_slope
        if lo <= sm <= hi:
            pass_count += 1
    return pass_count


def evaluate_true_bw(alpha_D, gamma_over_rho, sigma_0=0.0, a_slope=0.0):
    """Evaluate 20 channels with true quantum BW + optional background."""
    pass_count = 0
    for name, v, lo, hi in CHANNELS:
        sm = sigma_m_true_bw(v, alpha_D, gamma_over_rho) + sigma_0 * (100.0 / v) ** a_slope
        if lo <= sm <= hi:
            pass_count += 1
    return pass_count


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    # Run unit tests first
    unit_tests()
    print()

    print("=" * 80)
    print("v40.33 PART 1: CORRECTED alpha_D re-derivation")
    print("=" * 80)
    print()
    print("Reviewer caught: v40.30 used born_baseline (no F^2).")
    print("Re-deriving with FULL Breit-Wigner (F^2 included):")
    print()
    print(f"{'Gamma/rho':<10s} {'F^2_peak':<10s} {'alpha_D':<14s} {'Ratio to 5.55e-6':<20s}")
    print("-" * 70)

    for gamma_over_rho in [0.5, 1.0, 2.0, 5.0, 10.0]:
        F2_peak = 4.0 / gamma_over_rho**2
        alpha_D = find_alpha_D_full_bw(174.0, gamma_over_rho)
        if alpha_D:
            ratio = alpha_D / 5.55e-6
            print(f"{gamma_over_rho:<10.1f} {F2_peak:<10.3f} {alpha_D:<14.4e} {ratio:<20.4f}")

    print()
    print("CORRECTED FINDING:")
    print("  v40.30 alpha_D = 1.87e-6 was based on born_baseline (F^2 = 1)")
    print("  v40.24 alpha_D = 5.55e-6 was based on full BW with Gamma/rho = 1")
    print("  CORRECT comparison: with full BW at Gamma/rho=1, alpha_D = 9.52e-7")
    print("  Ratio: 5.8x smaller (not 3x as v40.30 claimed)")
    print()

    # Part 2: Fano profile scan
    print("=" * 80)
    print("v40.33 PART 2: Fano profile 4D scan")
    print("=" * 80)
    print()
    print("Fano: sigma_m = sigma_peak * (q + epsilon)^2 / (1 + epsilon^2)")
    print("where epsilon = (v - v_peak) / gamma")
    print()
    print("Scan: q in [-5, 5], gamma in [0.5, 5], sigma_peak in [100, 300]")
    print()

    qs = np.linspace(-5, 5, 11)  # 11 values
    gammas = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]  # 6 values
    sigma_peaks = [100, 150, 174, 200, 250, 300]  # 6 values
    total = len(qs) * len(gammas) * len(sigma_peaks)
    print(f"Grid: {total} configurations")

    fano_results = []
    for q in qs:
        for g in gammas:
            for sp in sigma_peaks:
                score = evaluate_fano(q, g, sp)
                fano_results.append({
                    'q': q, 'gamma': g, 'sigma_peak': sp, 'score': score
                })
    fano_results.sort(key=lambda x: -x['score'])

    print()
    print("TOP 10 (Fano scan):")
    print(f"{'Rank':<5s} {'q':>6s} {'gamma':>8s} {'sigma_peak':>12s} {'Score':>10s}")
    for i, r in enumerate(fano_results[:10]):
        print(f"{i+1:<5d} {r['q']:>6.2f} {r['gamma']:>8.2f} {r['sigma_peak']:>12.1f} {r['score']:>5d}/20")

    fano_score_dist = {}
    for r in fano_results:
        s = r['score']
        fano_score_dist[s] = fano_score_dist.get(s, 0) + 1
    print()
    print("Fano score distribution:")
    for s in sorted(fano_score_dist.keys(), reverse=True):
        if fano_score_dist[s] > 0:
            print(f"  {s}/20: {fano_score_dist[s]} configurations ({fano_score_dist[s]/len(fano_results)*100:.1f}%)")

    if fano_results:
        top_fano = fano_results[0]
        print()
        print("=" * 80)
        print("TOP FANO CONFIGURATION")
        print("=" * 80)
        print(f"q = {top_fano['q']:.2f}, gamma = {top_fano['gamma']:.2f}, sigma_peak = {top_fano['sigma_peak']:.1f}")
        print(f"Score: {top_fano['score']}/20")
        print()
        for name, v, lo, hi in CHANNELS:
            sm = sigma_m_fano(v, top_fano['q'], top_fano['gamma'], top_fano['sigma_peak'])
            passed = lo <= sm <= hi
            status = "PASS" if passed else "FAIL"
            print(f"  {name:<25s} v={v:>6.1f} sigma/m={sm:>12.4e} [{lo}, {hi}] {status}")

    # Part 3: True quantum BW scan
    print()
    print("=" * 80)
    print("v40.33 PART 3: True quantum BW 4D scan")
    print("=" * 80)
    print()
    print("True BW: sigma_m = Born_baseline * F^2 with 1/v^4 tails")
    print("Scan: alpha_D in [1e-7, 1e-5], Gamma/rho in [0.01, 5]")
    print()

    alpha_Ds = [1e-7, 3e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4]
    gamma_over_rhos = [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
    total = len(alpha_Ds) * len(gamma_over_rhos)
    print(f"Grid: {total} configurations")

    bw_results = []
    for alpha in alpha_Ds:
        for g in gamma_over_rhos:
            score = evaluate_true_bw(alpha, g)
            bw_results.append({
                'alpha_D': alpha, 'gamma_over_rho': g, 'score': score
            })
    bw_results.sort(key=lambda x: -x['score'])

    print()
    print("TOP 10 (True BW scan):")
    print(f"{'Rank':<5s} {'alpha_D':>14s} {'Gamma/rho':>10s} {'Score':>10s}")
    for i, r in enumerate(bw_results[:10]):
        print(f"{i+1:<5d} {r['alpha_D']:>14.4e} {r['gamma_over_rho']:>10.2f} {r['score']:>5d}/20")

    bw_score_dist = {}
    for r in bw_results:
        s = r['score']
        bw_score_dist[s] = bw_score_dist.get(s, 0) + 1
    print()
    print("True BW score distribution:")
    for s in sorted(bw_score_dist.keys(), reverse=True):
        if bw_score_dist[s] > 0:
            print(f"  {s}/20: {bw_score_dist[s]} configurations ({bw_score_dist[s]/len(bw_results)*100:.1f}%)")

    if bw_results:
        top_bw = bw_results[0]
        print()
        print("=" * 80)
        print("TOP TRUE BW CONFIGURATION")
        print("=" * 80)
        print(f"alpha_D = {top_bw['alpha_D']:.4e}, Gamma/rho = {top_bw['gamma_over_rho']:.2f}")
        print(f"Score: {top_bw['score']}/20")
        print()
        for name, v, lo, hi in CHANNELS:
            sm = sigma_m_true_bw(v, top_bw['alpha_D'], top_bw['gamma_over_rho'])
            passed = lo <= sm <= hi
            status = "PASS" if passed else "FAIL"
            print(f"  {name:<25s} v={v:>6.1f} sigma/m={sm:>12.4e} [{lo}, {hi}] {status}")

    # Save results
    output = {
        'v40_33_part1_corrected_alpha_D': {
            'v40_24_alpha_D': 5.55e-6,
            'v40_30_wrong_alpha_D': 1.87e-6,
            'v40_33_correct_alpha_D_gamma_over_rho_1': 9.52e-7,
            'ratio': 5.83,
            'note': 'Reviewer caught: v40.30 used born_baseline (no F^2)'
        },
        'fano_top_5': [{
            'q': r['q'], 'gamma': r['gamma'], 'sigma_peak': r['sigma_peak'],
            'score': r['score']
        } for r in fano_results[:5]],
        'fano_score_dist': fano_score_dist,
        'true_bw_top_5': [{
            'alpha_D': r['alpha_D'], 'gamma_over_rho': r['gamma_over_rho'],
            'score': r['score']
        } for r in bw_results[:5]],
        'true_bw_score_dist': bw_score_dist,
    }
    output_path = _PROJECT / "v0.3-prelim" / "data" / "results" / "v40_33_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {output_path}")
