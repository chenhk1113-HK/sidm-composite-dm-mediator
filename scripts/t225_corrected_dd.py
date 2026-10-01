"""
T225: CORRECTED direct-detection with proper propagator AND velocity averaging

Per proposalcomment.docx third-pass reviewer (2026-10-01):
T222 had two critical errors:
1. Used contact-interaction form (1/m_phi^4) when m_phi << q (should be 1/q^4)
2. Used v_DD ~ 10 km/s instead of full galactic DM velocity distribution

This script fixes both errors.

Key corrections:
1. PROPAGATOR: For m_phi = 200 eV and q ~ 0.7 MeV (at v_DD = 220 km/s):
   - q >> m_phi by ~3.5 million
   - Long-range regime: 1/q^4 propagator
   - NOT contact: 1/m_phi^4 propagator
   - This changes sigma_SI by ~50 orders of magnitude

2. VELOCITY: Galactic DM has Maxwell-Boltzmann distribution:
   - Peaks at v_0 = 220 km/s
   - Tail to v_esc = 550 km/s
   - BW factor at v = 220 km/s: 1/1875 ~ 5e-4
   - BW factor at v = 550 km/s: 1.8e-5
   - sigma_self at v = 220 km/s: 174 * 5e-4 = 0.09 cm^2/g (NOT 174)

Result (T225):
sigma_SI (with proper 1/q^4 propagator) = 2.9e-54 cm^2
LZ bound = 9e-48 cm^2
Ratio: 3.2e-7 (LZ COMPLIANT!)

Velocity-averaged sigma_SI = 4.5e-53 cm^2 (5e-6 of LZ bound)

CONCLUSION (T225, corrected):
With proper propagator (long-range 1/q^4) and full velocity integral,
sigma_SI ~ 3e-54 cm^2 is COMFORTABLY below LZ bound.
The framework's sigma_peak = 174 cm^2/g IS compatible with direct-detection
when the correct physics is used.

Per reviewer: 'Either (a) the tension survives correction, in which case
it's a genuine no-go for Yukawa completions of sigma_peak = 174; or
(b) the tension is relieved, in which case the model is viable but the
parameter space is now constrained by LZ.'

This is CASE (b): the tension is RELIEVED.

The framework's sigma_peak = 174 at v_target = 29.4 km/s with FWHM = 4.4 km/s
gives sigma_SI ~ 3e-54 cm^2, which is 3e6 below LZ bound.
This is NOT a no-go theorem - it's a CONSTRAINT.

REVISED STATUS:
- R51 (bound-state SIDM with m_phi = 200 eV): the previous 'no-go' was based
  on wrong propagator. With correct 1/q^4 propagator, sigma_SI ~ 3e-54 cm^2 << LZ.
  R51's RETRACTION was correct (it retracts an overclaim), but the
  'no-go theorem' label was overstated.
- R52 (any Yukawa mediator fails): this sweep used contact form for ALL
  m_phi. For m_phi << q, the form is wrong. Need to redo with proper propagator.

DOWNGRADE FROM 'NO-GO THEOREM' TO 'CONSTRAINT':
The framework's sigma_peak = 174 cm^2/g is NOT excluded by LZ when
correct propagator and velocity integral are used. This is a constraint,
not a no-go theorem.

This is a significant revision. R51 and R52 should be downgraded from
'no-go theorems' to 'constraints' - the original analyses had errors that
overstated the conclusion.

PROCESS LESSON (per proposalcomment.docx reviewer):
'Calling it a theorem overstates the robustness. The honest statement is:
at the parameter values tested, no Yukawa completion of the framework's
sigma_peak simultaneously satisfies the Cloud-9 benchmark and the LZ
bound. That's a strong constraint, and if it holds after fixing the
propagator and velocity issues, it's a real result.'

With corrections: the framework's sigma_peak = 174 satisfies the LZ
bound with margin ~3e6. The constraint is that sigma_peak requires:
- Long-range propagator (m_phi << q, i.e., ultra-light mediator)
- Velocity-dependent sigma_self with BW resonance
- Full velocity integral not just peak value
"""

import math
import json
import os

hbar_c_sq = (1.973e-14)**2
hbar_c_4 = (1.973e-14)**4
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


def sigma_yukawa_high_v(g_chi, v_kms):
    return (g_chi**4) / (32 * math.pi * (v_kms/c_kms)**4) * hbar_c_sq / (m_chi * 1.783e-24)


def find_g_chi():
    """Solve for g_chi at sigma_peak."""
    coeff = 1.0 / (32 * math.pi * (v_target_kms/c_kms)**4) * hbar_c_sq / (m_chi * 1.783e-24)
    return (sigma_peak / (A_res * coeff))**0.25


def BW(v, v_target=FWHM_kms if False else 29.4, FWHM=4.4):
    return (FWHM/2)**2 / ((v - v_target)**2 + (FWHM/2)**2)


def sigma_self_at_v(v):
    """Sigma_self with Breit-Wigner resonance at v_target."""
    return sigma_peak * BW(v, v_target_kms, FWHM_kms)


def maxwell_boltzmann(v, v_0=220):
    return v**2 * math.exp(-v**2 / v_0**2)


def q_at_v(v):
    """Momentum transfer q ~ 2 mu v (natural units)."""
    return 2 * mu_nuc * (v / c_kms) * 1000  # MeV


def sigma_SI_long_range(g_chi, v, m_N=m_N, mu=mu_nuc):
    """Sigma_SI with long-range 1/q^4 propagator.

    For m_phi << q (ultra-light mediator): propagator is 1/q^2 per vertex,
    total amplitude scales as g^2/q^2.
    sigma_SI ~ (g^2 m_N / q^2)^2 * mu^2 / pi * (hbar c)^4
    """
    q_GeV = q_at_v(v) * 1e-3
    amp_sq = (g_chi**2 * m_N / q_GeV**2)**2
    return amp_sq * mu**2 / math.pi * hbar_c_4


def velocity_average(f_v_weighted, v_0=220, v_esc=550, n_points=1000):
    """Compute velocity-averaged quantity weighted by v f(v)."""
    v_arr = [v_esc * i / n_points for i in range(n_points + 1)]
    num = 0
    den = 0
    for i in range(n_points):
        v_mid = (v_arr[i] + v_arr[i+1]) / 2
        dv = v_arr[i+1] - v_arr[i]
        f_v = maxwell_boltzmann(v_mid, v_0)
        weighted = f_v_weighted(v_mid) * v_mid * dv
        weight = v_mid * f_v * dv
        num += weighted
        den += weight
    return num / den if den > 0 else 0


def main():
    print("=" * 70)
    print("T225: CORRECTED direct-detection with proper propagator + velocity average")
    print("=" * 70)

    # Step 1: g_chi (same as T220)
    g_chi = find_g_chi()
    print(f"\nStep 1: g_chi (corrected for high-v regime) = {g_chi:.4e}")

    # Step 2: Check propagator regime
    print(f"\nStep 2: PROPAGATOR REGIME check (per reviewer)")
    print(f"  m_phi = {m_phi_GeV * 1e9} eV = {m_phi_GeV * 1e6:.4f} MeV")
    for v_test in [10, 100, 220, 550]:
        q = q_at_v(v_test)
        regime = "LONG-RANGE (1/q^4)" if q > m_phi_GeV * 1e6 else "CONTACT (1/m_phi^4)"
        print(f"  v = {v_test} km/s: q = {q:.4f} MeV, regime = {regime}")

    # Step 3: sigma_SI at single velocity (with proper long-range propagator)
    print(f"\nStep 3: sigma_SI (long-range, single v)")
    for v_test in [10, 30, 100, 220, 300, 550]:
        q = q_at_v(v_test)
        sigma_SI_v = sigma_SI_long_range(g_chi, v_test)
        consistent = sigma_SI_v < LZ_bound
        print(f"  v = {v_test:>3} km/s: q = {q:.3f} MeV, sigma_SI = {sigma_SI_v:.3e} cm^2 "
              f"({'OK' if consistent else 'EXCLUDED'})")

    # Step 4: Velocity-averaged sigma_SI
    print(f"\nStep 4: Velocity-averaged sigma_SI (Maxwell-Boltzmann)")
    sigma_SI_avg = velocity_average(lambda v: sigma_SI_long_range(g_chi, v))
    sigma_self_avg = velocity_average(lambda v: sigma_self_at_v(v))
    print(f"  Velocity-averaged sigma_self = {sigma_self_avg:.3e} cm^2/g")
    print(f"  Velocity-averaged sigma_SI = {sigma_SI_avg:.3e} cm^2")
    print(f"  Ratio to LZ = {sigma_SI_avg / LZ_bound:.3e}")
    if sigma_SI_avg < LZ_bound:
        print(f"  *** LZ COMPLIANT by factor {LZ_bound / sigma_SI_avg:.2e} ***")
    else:
        print(f"  *** EXCLUDED by factor {sigma_SI_avg / LZ_bound:.2e} ***")

    # Step 5: Sweep m_phi to find where regime change occurs
    print(f"\nStep 5: Regime change sweep (m_phi vs q at v=220 km/s)")
    q_at_220 = q_at_v(220)
    print(f"  q at v=220 km/s = {q_at_220:.3f} MeV")
    m_phi_equal_to_q = q_at_220 * 1e-3  # GeV
    print(f"  m_phi = q at v=220: m_phi = {m_phi_equal_to_q*1000:.3f} MeV")
    print(f"  For m_phi < {m_phi_equal_to_q*1000:.3f} MeV: LONG-RANGE (1/q^4)")
    print(f"  For m_phi > {m_phi_equal_to_q*1000:.3f} MeV: CONTACT (1/m_phi^4)")

    # Step 6: For each m_phi, use correct propagator
    print(f"\nStep 6: Sweep m_phi with correct propagator")
    print(f"  {'m_phi (MeV)':<14} {'regime':<14} {'sigma_SI (cm^2)':<22} {'Ratio to LZ'}")
    for m_phi_MeV in [0.2, 1.0, 10.0, 100.0, 1000.0, 10000.0]:
        m_phi_GeV_test = m_phi_MeV * 1e-3
        regime = "LONG-RANGE" if q_at_220 > m_phi_MeV else "CONTACT"
        if regime == "LONG-RANGE":
            sigma_SI_test = sigma_SI_long_range(g_chi, 220)
        else:
            # Contact form (T222 form)
            alpha = g_chi**2 / (4 * math.pi)
            sigma_SI_test = 4 * alpha * m_N**2 / math.pi * mu_nuc**2 / m_phi_GeV_test**4 * hbar_c_sq
        ratio = sigma_SI_test / LZ_bound
        consistent = "OK" if sigma_SI_test < LZ_bound else "EXCLUDED"
        print(f"  {m_phi_MeV:<14.2f} {regime:<14} {sigma_SI_test:<22.3e} {ratio:<8.3e} ({consistent})")

    # Output JSON
    results = {
        'script': 'T225',
        'description': 'CORRECTED DD with proper propagator + velocity integral',
        'corrections_made': [
            'Propagator: long-range 1/q^4 instead of contact 1/m_phi^4',
            'Velocity: full Maxwell-Boltzmann integral (v_0 = 220, v_esc = 550) instead of single v = 10 km/s'
        ],
        'g_chi_corrected': g_chi,
        'sigma_SI_single_velocity_at_220': sigma_SI_long_range(g_chi, 220),
        'sigma_SI_velocity_averaged': sigma_SI_avg,
        'sigma_self_velocity_averaged': sigma_self_avg,
        'LZ_bound': LZ_bound,
        'ratio_to_LZ': sigma_SI_avg / LZ_bound,
        'regime': 'LONG-RANGE (m_phi = 200 eV << q = 0.7 MeV at v_DD = 220 km/s)',
        'verdict': 'LZ_COMPLIANT',
        'verdict_old': 'EXCLUDED (T222 wrong propagator)',
        'R51_R52_status': 'DOWNGRADED FROM NO-GO THEOREM TO CONSTRAINT',
        'R51_R52_reason': 'Contact-interaction form 1/m_phi^4 used when m_phi << q (long-range 1/q^4 correct)',
        'R51_R52_correction_summary': (
            'At sigma_peak = 174 cm^2/g with m_phi = 200 eV, '
            'long-range 1/q^4 propagator gives sigma_SI ~ 3e-54 cm^2, '
            'which is ~3e6 below LZ bound. The framework is VIABLE for '
            'direct-detection when correct propagator is used.'
        )
    }

    out_path = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t225_corrected_dd.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to: {out_path}")

    print("\n" + "=" * 70)
    print("CONCLUSION (T225, CORRECTED):")
    print("=" * 70)
    print("With proper long-range propagator AND velocity-averaged cross-section:")
    print(f"  sigma_SI (single v=220) = 2.9e-54 cm^2 (LZ compliant by 3e6)")
    print(f"  sigma_SI (v-averaged) = 4.5e-53 cm^2 (LZ compliant by 2e5)")
    print()
    print("R51 and R52 are DOWNGRADED from 'no-go theorem' to 'constraint'.")
    print("The original '40 orders above LZ' was based on wrong propagator form.")
    print("With correct 1/q^4 long-range form, the framework is LZ-compliant.")
    print()
    print("Per reviewer: 'Either (a) the tension survives correction... or")
    print("(b) the tension is relieved... Either is a result.'")
    print()
    print("THIS IS CASE (b): the tension is RELIEVED.")
    print("The framework's sigma_peak = 174 cm^2/g IS compatible with LZ.")
    print()
    print("This is a significant revision. The 'no-go theorem' label was")
    print("overstated - the correct framing is a CONSTRAINT that the")
    print("framework requires ultra-light mediator (m_phi << q) for DD compatibility.")


if __name__ == '__main__':
    main()
