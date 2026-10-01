"""
T226: Corrected direct-detection with proper (hbar c)^2 units and v->0 cutoff

Per proposalcomment.docx fourth-pass reviewer (2026-10-01):
R53 had a dimensional error - used (hbar c)^4 instead of (hbar c)^2.
Also R53's v->0 divergence wasn't handled.

This script fixes both.

Standard scalar-mediated SI cross section in long-range limit (m_phi << q):
  sigma_SI = (g_chi^2 * g_N^2 * mu^2) / (4 pi * q^4) * (hbar c)^2

Where g_N is the effective nucleon coupling (g_N m_N / v_EW at nucleon vertex).

The key fix: replace hbar_c_4 with hbar_c_sq, and add proper v->0 cutoff.

Numerical: take g_chi ~ 3e-3, m_phi = 200 eV, q ~ 0.7 MeV at v = 220 km/s.
Standard scalar nEDM-like amplitude gives sigma_SI ~ 1e-26 cm^2 (per reviewer),
which is ~20 orders above LZ. This is the actual constraint.

The reviewer's check (1/sqrt(2) factor from BW, full integral with cutoff) gives
the "real" number.

Let me also handle the v->0 divergence properly:
- DM velocity distribution: Maxwell-Boltzmann with v_0 = 220 km/s, v_esc = 550 km/s
- Lower cutoff: v_min ~ 0 (or detector threshold ~ 10 km/s)
- For sigma_SI ~ v^-4, the integral diverges as v -> 0

This is a real physical issue: light mediators give divergent cross section
at low velocity. Standard handling: introduce form factor F(q) or velocity
cutoff at detector threshold (~10 km/s).

For sigma_SI ~ (g^2 m_N / q^2)^2 where q = 2 mu v:
  sigma_SI ~ (g^2 m_N / (2 mu v))^2 = g^4 m_N^2 / (4 mu^2 v^2)
  This diverges as v -> 0

The MB-weighted cross section:
  <sigma_SI> ~ int v * f(v) * sigma_SI(v) dv / int v * f(v) dv
  ~ int v * v^2 * exp(-v^2/v_0^2) * (1/v^2) dv / int v * v^2 * exp(-v^2/v_0^2) dv
  ~ int v * exp(-v^2/v_0^2) dv / int v * v^2 * exp(-v^2/v_0^2) dv
  ~ v_0 / (v_0^2) ~ 1/v_0 (logarithmic divergence)

So velocity-averaged sigma_SI is FINITE (logarithmically) but dominated by
the low-v tail. With v_min = 10 km/s cutoff:
  <sigma_SI> ~ log(v_0/v_min) * (g^4 m_N^2 / (4 mu^2 * v_0^3))
  ~ log(220/10) * (g^4 m_N^2 / (4 mu^2 * v_0^3))
  ~ 3.1 * (g^4 m_N^2 / (4 mu^2 * v_0^3))
"""

import math
import json
import os

hbar_c_sq = (1.973e-14)**2
c_kms = 2.998e5
m_chi = 1.0
m_phi_GeV = 200e-9  # 200 eV
v_target_kms = 29.4
FWHM_kms = 4.4
A_res = 100.0
sigma_peak = 174.0
m_N = 0.939
mu_nuc = m_chi * m_N / (m_chi + m_N)
LZ_bound = 9e-48


def find_g_chi():
    coeff = 1.0 / (32 * math.pi * (v_target_kms/c_kms)**4) * hbar_c_sq / (m_chi * 1.783e-24)
    return (sigma_peak / (A_res * coeff))**0.25


def BW(v):
    return (FWHM_kms/2)**2 / ((v - v_target_kms)**2 + (FWHM_kms/2)**2)


def sigma_self_at_v(v):
    return sigma_peak * BW(v)


def q_at_v(v):
    return 2 * mu_nuc * (v / c_kms) * 1000  # MeV


# CORRECTED: Use (hbar c)^2, not (hbar c)^4
# Standard scalar-mediated SI cross section in long-range limit:
def sigma_SI_long_range_proper(g_chi, v, g_N=None):
    """Proper sigma_SI with correct units.

    sigma_SI = (g_chi^2 * g_N^2 * mu^2) / (4 pi * q^4) * (hbar c)^2

    For Yukawa-type coupling, g_chi couples to chi chi and g_N couples to nucleon.
    In our simple model: g_chi = g_N (same coupling).
    """
    if g_N is None:
        g_N = g_chi
    q_GeV = q_at_v(v) * 1e-3
    return (g_chi**2 * g_N**2 * mu_nuc**2) / (4 * math.pi * q_GeV**4) * hbar_c_sq


def maxwell_boltzmann(v, v_0=220):
    return v**2 * math.exp(-v**2 / v_0**2)


def velocity_average_with_cutoff(func, v_min=10.0, v_0=220, v_esc=550, n_points=2000):
    """Compute velocity-averaged with explicit v_min cutoff."""
    v_arr = [v_min + (v_esc - v_min) * i / n_points for i in range(n_points + 1)]
    num = 0
    den = 0
    for i in range(n_points):
        v_mid = (v_arr[i] + v_arr[i+1]) / 2
        dv = v_arr[i+1] - v_arr[i]
        f_v = maxwell_boltzmann(v_mid, v_0)
        # DD rate ~ sigma(v) * v (flux factor) * f(v)
        weighted = func(v_mid) * v_mid * f_v * dv
        weight = v_mid * f_v * dv
        num += weighted
        den += weight
    return num / den if den > 0 else 0


def main():
    print("=" * 70)
    print("T226: PROPERLY CORRECTED DD with (hbar c)^2 and v_min cutoff")
    print("=" * 70)

    g_chi = find_g_chi()
    print(f"\ng_chi = {g_chi:.4e}")

    # Step 1: Single-velocity sigma_SI (proper formula)
    print(f"\nStep 1: sigma_SI at single velocities (PROPER units)")
    print(f"  {'v (km/s)':<12} {'q (MeV)':<12} {'sigma_SI (cm^2)':<22} {'Ratio to LZ'}")
    for v_test in [10, 30, 100, 220, 300, 550]:
        q = q_at_v(v_test)
        sigma_SI = sigma_SI_long_range_proper(g_chi, v_test)
        ratio = sigma_SI / LZ_bound
        consistent = "OK" if sigma_SI < LZ_bound else "EXCLUDED"
        print(f"  {v_test:<12} {q:<12.3f} {sigma_SI:<22.3e} {ratio:<8.3e} ({consistent})")

    # Step 2: Velocity-averaged with v_min = 10 km/s cutoff
    print(f"\nStep 2: Velocity-averaged sigma_SI (v_min = 10 km/s)")
    sigma_SI_avg = velocity_average_with_cutoff(lambda v: sigma_SI_long_range_proper(g_chi, v), v_min=10.0)
    print(f"  Velocity-averaged sigma_SI = {sigma_SI_avg:.3e} cm^2")
    print(f"  Ratio to LZ = {sigma_SI_avg / LZ_bound:.3e}")
    if sigma_SI_avg < LZ_bound:
        print(f"  *** LZ COMPLIANT by factor {LZ_bound / sigma_SI_avg:.2e} ***")
    else:
        print(f"  *** EXCLUDED by factor {sigma_SI_avg / LZ_bound:.2e} ***")

    # Step 3: Sweep v_min cutoff
    print(f"\nStep 3: Velocity-averaged sigma_SI vs v_min cutoff")
    print(f"  {'v_min (km/s)':<14} {'sigma_SI (cm^2)':<22} {'Ratio to LZ'}")
    for v_min in [1.0, 5.0, 10.0, 50.0, 100.0]:
        sigma_v_min = velocity_average_with_cutoff(lambda v: sigma_SI_long_range_proper(g_chi, v), v_min=v_min)
        ratio = sigma_v_min / LZ_bound
        print(f"  {v_min:<14.1f} {sigma_v_min:<22.3e} {ratio:<8.3e}")

    # Step 4: Sweep g_N (nucleon coupling)
    print(f"\nStep 4: Sensitivity to g_N (nucleon coupling)")
    print(f"  {'g_N/g_chi':<14} {'sigma_SI (cm^2)':<22} {'Ratio to LZ'}")
    for ratio_g in [0.001, 0.01, 0.1, 1.0, 10.0]:
        g_N = ratio_g * g_chi
        sigma_SI_test = velocity_average_with_cutoff(lambda v: sigma_SI_long_range_proper(g_chi, v, g_N=g_N), v_min=10.0)
        ratio = sigma_SI_test / LZ_bound
        print(f"  {ratio_g:<14.3f} {sigma_SI_test:<22.3e} {ratio:<8.3e}")

    # Output JSON
    results = {
        'script': 'T226',
        'description': 'Corrected DD with proper (hbar c)^2 and v_min cutoff (per R54 reviewer)',
        'corrections_from_T225': [
            'Replace (hbar c)^4 with (hbar c)^2 (R53 dimensional error)',
            'Add v_min = 10 km/s cutoff to handle v->0 divergence',
            'Add explicit g_N coupling (was implicit g_N = g_chi)'
        ],
        'g_chi': g_chi,
        'sigma_SI_single_v_at_220': sigma_SI_long_range_proper(g_chi, 220),
        'sigma_SI_velocity_averaged_vmin10': sigma_SI_avg,
        'LZ_bound': LZ_bound,
        'ratio_to_LZ': sigma_SI_avg / LZ_bound,
        'verdict': 'EXCLUDED' if sigma_SI_avg > LZ_bound else 'LZ_COMPLIANT',
        'verdict_R53': 'LZ_COMPLIANT (WRONG due to (hbar c)^4 dimensional error)',
        'R53_status': 'DOWNGRADED FURTHER - dimensional error made number too small',
        'R54_reviewer_note': (
            'R53 used (hbar c)^4 which is dimensionally wrong (units GeV^4 cm^4 instead of cm^2). '
            'Correct formula uses (hbar c)^2. Corrected sigma_SI ~ 1e-25 to 1e-26 cm^2, '
            'which is 20+ orders above LZ. The framework IS excluded by LZ at m_phi = 200 eV.'
        )
    }

    out_path = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t226_proper_dd.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to: {out_path}")

    print("\n" + "=" * 70)
    print("CONCLUSION (T226, PROPERLY CORRECTED):")
    print("=" * 70)
    print("R53 had a dimensional error: used (hbar c)^4 instead of (hbar c)^2.")
    print("Corrected sigma_SI at v = 220 km/s with proper units is ~10^-26 cm^2,")
    print("which is ~20 orders above LZ bound 9e-48 cm^2.")
    print()
    print("This confirms the reviewer's check: the 'LZ compliant' conclusion")
    print("in R53 was based on a dimensional error in the formula.")
    print()
    print("The actual status:")
    print("- R51-R52: '40 orders above LZ' (overestimated due to wrong propagator)")
    print("- R53: '5e4 below LZ' (underestimated due to dimensional error)")
    print("- T226: ~20 orders above LZ (correct)")
    print()
    print("Per reviewer: 'roughly 15-25 orders above LZ for m_phi = 200 eV.")
    print("That's still a real constraint, but it's a constraint and not a")
    print("no-go theorem, which is exactly what I suggested downgrading to")
    print("two rounds ago.'")


if __name__ == '__main__':
    main()
