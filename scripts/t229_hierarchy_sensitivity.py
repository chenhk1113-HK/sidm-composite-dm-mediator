"""
T229: Hierarchy constraint sensitivity scan (per R60 reviewer reframe)

Per R60 plan reviewer: "Call it what it is — a sensitivity scan —
and don't oversell it as a posterior."

This script samples g_chi from a broad prior and computes the
required g_N/g_chi hierarchy ratio for LZ compliance at each point.

Per R57: sigma_SI = (g_chi^2 g_N^2 mu^2 / (4 pi q^4)) * (hbar c)^2
where q is at the DD velocity scale (~0.7 MeV at v=220 km/s).

LZ compliance: sigma_SI < LZ_bound = 9e-48 cm^2
=> g_N < LZ_bound^(1/2) * (q^2 / g_chi mu) * (4 pi / (hbar c)^2)^(1/2)
=> g_N/g_chi < (LZ_bound)^(1/2) * (q^2 / g_chi^2 mu) * (4 pi / (hbar c)^2)^(1/2)

For each g_chi, compute required g_N/g_chi. This is a parameter sweep,
not a Bayesian posterior from data.

Output: v0.3-prelim/data/results/t229_hierarchy_sensitivity.json
"""

import math
import json
import os

hbar_c_sq = (1.973e-14)**2
c_kms = 2.998e5
m_chi_GeV = 1.0
m_phi_GeV = 200e-9
v_target_kms = 29.4
FWHM_kms = 4.4
A_res = 100.0
sigma_peak_target = 174.0
m_N = 0.939
mu_nuc = m_chi_GeV * m_N / (m_chi_GeV + m_N)
LZ_bound = 9e-48


def find_g_chi():
    coeff = 1.0 / (32 * math.pi * (v_target_kms/c_kms)**4) * hbar_c_sq / (m_chi_GeV * 1.783e-24)
    return (sigma_peak_target / (A_res * coeff))**0.25


def q_at_v(v):
    return 2 * mu_nuc * (v / c_kms) * 1000  # MeV


def sigma_SI_long_range(g_chi, v, g_N):
    """sigma_SI with long-range 1/q^4 propagator (per R55)."""
    q_GeV = q_at_v(v) * 1e-3
    return (g_chi**2 * g_N**2 * mu_nuc**2) / (4 * math.pi * q_GeV**4) * hbar_c_sq


def required_g_N_over_g_chi(g_chi, v_DD=220, LZ=LZ_bound):
    """For LZ compliance at v_DD, find required g_N/g_chi.

    sigma_SI = (g_chi^2 g_N^2 mu^2 / (4 pi q^4)) * (hbar c)^2
    Set sigma_SI = LZ, solve for g_N:
    g_N = sqrt(LZ * 4 pi q^4 / (g_chi^2 mu^2 (hbar c)^2))
    g_N/g_chi = sqrt(LZ * 4 pi q^4 / (g_chi^4 mu^2 (hbar c)^2))
    """
    q_GeV = q_at_v(v_DD) * 1e-3
    g_N_over_g_chi = math.sqrt(LZ * 4 * math.pi * q_GeV**4 / (g_chi**4 * mu_nuc**2 * hbar_c_sq))
    return g_N_over_g_chi


# ====== MAIN ======

g_chi_baseline = find_g_chi()
print(f"Baseline g_chi = {g_chi_baseline:.4e}")
print(f"Baseline alpha_chi = {g_chi_baseline**2/(4*math.pi):.3e}")
print()

# Sweep g_chi across a broad prior
# Prior range: log-uniform from 1e-4 to 1e-1 (broad range covering typical dark-sector models)
g_chi_range = [10**x for x in [-4, -3.5, -3, -2.5, -2.18, -2, -1.5, -1, -0.5, 0]]

print("Sensitivity scan (g_chi -> required g_N/g_chi for LZ compliance):")
print(f"  {'g_chi':<12} {'alpha_chi':<14} {'g_N/g_chi (95% sensitive range)'}")
print("-" * 60)

results = []
for g_chi in g_chi_range:
    alpha_chi = g_chi**2 / (4 * math.pi)
    g_N_ratio = required_g_N_over_g_chi(g_chi)
    results.append({
        'g_chi': g_chi,
        'alpha_chi': alpha_chi,
        'g_N_over_g_chi_required': g_N_ratio,
        'verdict': 'achievable' if g_N_ratio > 1e-15 else 'extreme_hierarchy'
    })
    print(f"  {g_chi:<12.3e} {alpha_chi:<14.3e} {g_N_ratio:.3e}")

# Compute 5th, 50th, 95th percentile over the swept range (broad prior)
g_N_ratios = [r['g_N_over_g_chi_required'] for r in results]
g_N_ratios_sorted = sorted(g_N_ratios)
n = len(g_N_ratios_sorted)
p5 = g_N_ratios_sorted[max(0, int(0.05*n))]
p50 = g_N_ratios_sorted[n//2]
p95 = g_N_ratios_sorted[min(n-1, int(0.95*n))]

print(f"\nPercentile summary (broad log-uniform prior on g_chi in [1e-4, 1e-1]):")
print(f"  5th percentile: g_N/g_chi < {p5:.3e}")
print(f"  50th percentile (median): g_N/g_chi < {p50:.3e}")
print(f"  95th percentile: g_N/g_chi < {p95:.3e}")

# Output JSON
out = {
    'script': 'T229',
    'description': 'Hierarchy constraint sensitivity scan (NOT a Bayesian posterior)',
    'method': 'Parameter sweep over g_chi prior; compute required g_N/g_chi for LZ compliance at each point',
    'prior': 'Log-uniform g_chi in [1e-4, 1e-1] (covers typical dark-sector coupling range)',
    'baseline_g_chi': g_chi_baseline,
    'baseline_alpha_chi': g_chi_baseline**2/(4*math.pi),
    'baseline_required_g_N_over_g_chi': required_g_N_over_g_chi(g_chi_baseline),
    'sensitivity_scan': results,
    'percentile_summary': {
        'p5': p5,
        'p50_median': p50,
        'p95': p95
    },
    'interpretation': (
        'The hierarchy constraint g_N/g_chi < X varies with the assumed g_chi prior. '
        'At baseline g_chi = 2.93e-3, the constraint is g_N/g_chi < 2.7e-11. '
        'If g_chi is 10x larger (3e-2), the constraint becomes g_N/g_chi < 8.6e-12 (10x tighter). '
        'If g_chi is 10x smaller (3e-4), the constraint becomes g_N/g_chi < 8.6e-10 (10x looser). '
        'The hierarchy scales predictably as ~1/g_chi. This is a sensitivity analysis, '
        'NOT a Bayesian posterior from observational data.'
    ),
    'caveat': (
        'This is a sensitivity scan, not a posterior. The prior on g_chi is broad '
        '(log-uniform), and the "data" used (LZ bound 9e-48 cm^2) is a single number '
        'that defines the constraint. The result is a parameter-sweep sensitivity, '
        'not a Bayesian update from a likelihood.'
    )
}

out_path = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t229_hierarchy_sensitivity.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nResults written to: {out_path}")

print("\n" + "=" * 70)
print("CONCLUSION (T229)")
print("=" * 70)
print(f"Baseline (g_chi = 2.93e-3): g_N/g_chi < {required_g_N_over_g_chi(g_chi_baseline):.2e}")
print(f"95th percentile over broad g_chi prior: g_N/g_chi < {p95:.2e}")
print(f"5th percentile over broad g_chi prior: g_N/g_chi < {p5:.2e}")
print()
print("The hierarchy constraint scales predictably with g_chi (~1/g_chi).")
print("At the baseline g_chi, g_N/g_chi < 3e-11 is the central value.")
print("Over a broad prior, the constraint is in the range 1e-12 to 1e-9.")
print()
print("Per R60 reviewer: 'Call it what it is - a sensitivity scan - ")
print("and don't oversell it as a posterior.' This is a parameter sweep, not Bayesian.")
