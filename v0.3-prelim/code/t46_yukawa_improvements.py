"""T46 — Yukawa improvement survey.

Brainstorm physical mechanisms that could give a > 0 (sigma/m decreasing
with v, the data's preference). Each must be:
  (a) physically motivated
  (b) implementable in <100 lines
  (c) testable against T39's anchor (sigma/m_0 = 1.57)

Candidate improvements:
  1. Sommerfeld enhancement (non-perturbative, attractive)
  2. Form factor (composite DM, finite size)
  3. Pseudo-scalar mediator (spin-0 case)
  4. Multiple mediator spectrum (2+ U(1)'s)
  5. Inelastic + Sommerfeld (combine T43 with #1)
"""
import numpy as np
import sys
sys.path.insert(0, '.')
import t40_yukawa_sigma_m as yukawa


def sommerfeld_factor(v_kms: float, m_phi_MeV: float, m_chi_GeV: float,
                       g_chi: float) -> float:
    """Sommerfeld enhancement factor for attractive Yukawa.

    S(v) = (2*pi*alpha/(2*beta)) / (1 - exp(-2*pi*alpha/(2*beta)))
    where alpha = g_chi^2 / (4*pi) (Yukawa coupling, attractive)
    and beta = m_chi v / (sqrt(2) m_phi) (Moliere parameter).
    """
    alpha = g_chi ** 2 / (4 * np.pi)
    beta = yukawa.beta_phi(v_kms, m_phi_MeV, m_chi_GeV)
    if beta <= 0:
        return 1.0
    x = 2 * np.pi * alpha / (2 * beta)
    if x > 50:  # overflow protection
        return 1000.0  # capped
    S = x / (1 - np.exp(-x))
    return float(S)


def sigma_m_sommerfeld(v_kms: float, m_phi_MeV: float, m_chi_GeV: float,
                        g_chi: float) -> float:
    """sigma/m with Sommerfeld enhancement."""
    sm_yukawa = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)
    S = sommerfeld_factor(v_kms, m_phi_MeV, m_chi_GeV, g_chi)
    return sm_yukawa * S


def sigma_m_form_factor(v_kms: float, m_phi_MeV: float, m_chi_GeV: float,
                          g_chi: float, R_fm: float = 1.0) -> float:
    """sigma/m with composite-DM form factor.

    F^2(q^2) = 1 / (1 + (q R)^2)^2  (dipole form factor)
    where q = m_chi v (3-momentum transfer).
    """
    sm_yukawa = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)
    # Convert q to MeV: m_chi_GeV * v_kms / c (natural units)
    # q = m_chi v, in natural units hbar = c = 1
    # In MeV: q_MeV = m_chi_GeV * 1000 * (v_kms / 299792)
    q_MeV = m_chi_GeV * 1000 * v_kms / 299792.458
    # R_fm in fm, convert to MeV^-1: 1 fm = 1/(197.327 MeV)
    R_MeV_inv = R_fm / 197.327e-13  # 1 fm in MeV^-1 = 1 / 197.327 MeV
    # Hmm, R_fm in fm = R_fm * 1e-13 cm; 1 fm = 1 / 197.327 MeV (hbar c conversion)
    # q R = q_MeV * R_MeV_inv (where R_MeV_inv = R_fm / 197.327)
    qR = q_MeV * (R_fm / 197.327)
    F2 = 1.0 / (1.0 + qR ** 2) ** 2
    return sm_yukawa * F2


def sigma_m_pseudo_scalar(v_kms: float, m_phi_MeV: float, m_chi_GeV: float,
                            g_chi: float) -> float:
    """sigma/m for pseudo-scalar (spin-0) mediator.

    Pseudo-scalar coupling has a different velocity dependence:
    sigma_T ~ (g_chi^2 m_chi^2 v^2) / (16 pi m_phi^4) (linear in v^2)

    For low v, this is suppressed! For high v, it grows.
    Compare to Yukawa (vector): sigma_T ~ (g_chi^4 m_chi^2) / (8 pi m_phi^4)
    which is independent of v at leading order.
    """
    # Use a different prefactor and v-dependence
    # In natural units: sigma_T ~ (g_chi^2 m_chi^2 v^2) / (16 pi m_phi^4)
    # Convert to cm^2 via (hbar c)^2
    m_chi_MeV = m_chi_GeV * 1000.0
    # v in km/s, convert to natural: v/c
    v_over_c = v_kms / 299792.458
    # Prefactor in 1/MeV^2
    prefactor = (g_chi ** 2) * (m_chi_MeV ** 2) * (v_over_c ** 2) / (16 * np.pi * m_phi_MeV ** 4)
    # Convert to cm^2: (hbar c)^2
    sigma_cm2 = prefactor * (197.327e-13) ** 2  # hbar c in MeV*cm
    # Convert to cm^2/g
    sigma_m = sigma_cm2 / m_chi_GeV * (1.0 / 1.7826619e-24)
    return float(sigma_m)


def power_law_slope(sigma_m_func, v_lo: float, v_hi: float, m_phi: float,
                     m_chi: float, g_chi: float, **kwargs) -> float:
    """Compute a = -d log(sigma/m) / d log(v)."""
    s_lo = sigma_m_func(v_lo, m_phi, m_chi, g_chi, **kwargs)
    s_hi = sigma_m_func(v_hi, m_phi, m_chi, g_chi, **kwargs)
    if s_lo <= 0 or s_hi <= 0:
        return -2.0
    return -((np.log10(s_hi) - np.log10(s_lo)) / (np.log10(v_hi) - np.log10(v_lo)))


if __name__ == "__main__":
    print("=" * 80)
    print("T46 — Yukawa improvement survey")
    print("=" * 80)

    # Baseline: simple Yukawa
    print("\n1. Baseline simple Yukawa:")
    print(f"  m_phi=100 MeV, m_chi=40 GeV, g_chi=0.5")
    sm_y = yukawa.sigma_m_cm2_per_g(100.0, 100.0, 40.0, 0.5)
    a_y = yukawa.power_law_slope(100.0, 40.0)
    print(f"  sigma/m_0 = {sm_y:.4e} cm^2/g, a = {a_y:.3f}")

    # Test 1: Sommerfeld
    print("\n2. Sommerfeld enhancement:")
    for m_phi in [10.0, 100.0, 1000.0]:
        for g_chi in [0.1, 0.5, 1.0]:
            sm = sigma_m_sommerfeld(100.0, m_phi, 40.0, g_chi)
            a = power_law_slope(sigma_m_sommerfeld, 50.0, 200.0, m_phi, 40.0, g_chi)
            sm_y = yukawa.sigma_m_cm2_per_g(100.0, m_phi, 40.0, g_chi)
            if sm_y > 0:
                S = sm / sm_y
                print(f"  m_phi={m_phi:>5.0f} MeV, g_chi={g_chi:.1f}: sigma/m = {sm:.4e}, "
                      f"S = {S:.2f}, a = {a:.3f}")

    # Test 2: Form factor
    print("\n3. Form factor (composite DM, R = 1 fm):")
    for m_phi in [10.0, 100.0]:
        for g_chi in [0.5]:
            sm = sigma_m_form_factor(100.0, m_phi, 40.0, g_chi, R_fm=1.0)
            a = power_law_slope(sigma_m_form_factor, 50.0, 200.0, m_phi, 40.0, g_chi, R_fm=1.0)
            sm_y = yukawa.sigma_m_cm2_per_g(100.0, m_phi, 40.0, g_chi)
            F2 = sm / sm_y if sm_y > 0 else 0
            print(f"  m_phi={m_phi:>5.0f} MeV: sigma/m = {sm:.4e}, F^2 = {F2:.4f}, a = {a:.3f}")

    # Test 3: Pseudo-scalar
    print("\n4. Pseudo-scalar (spin-0) mediator:")
    for m_phi in [10.0, 100.0, 1000.0]:
        for g_chi in [0.5, 1.0]:
            sm = sigma_m_pseudo_scalar(100.0, m_phi, 40.0, g_chi)
            a = power_law_slope(sigma_m_pseudo_scalar, 50.0, 200.0, m_phi, 40.0, g_chi)
            sm_y = yukawa.sigma_m_cm2_per_g(100.0, m_phi, 40.0, g_chi)
            print(f"  m_phi={m_phi:>5.0f} MeV, g_chi={g_chi:.1f}: sigma/m = {sm:.4e} "
                  f"(vs Yukawa {sm_y:.4e}), a = {a:.3f}")

    # Test 4: Two-mediator model
    print("\n5. Two-mediator model (m_phi_1, m_phi_2 contributions):")
    # Try m_phi_1 = 10 MeV (steep), m_phi_2 = 1000 MeV (shallow)
    m_phi_1, m_phi_2 = 10.0, 1000.0
    g_chi_1, g_chi_2 = 0.5, 0.5
    for v in [10.0, 50.0, 100.0, 200.0, 500.0]:
        s1 = yukawa.sigma_m_cm2_per_g(v, m_phi_1, 40.0, g_chi_1)
        s2 = yukawa.sigma_m_cm2_per_g(v, m_phi_2, 40.0, g_chi_2)
        # Coherent sum: sigma_tot = sigma_1 + sigma_2 (if uncorrelated)
        s_tot = s1 + s2
        print(f"  v = {v:>5.0f} km/s: sigma_1 = {s1:.4e}, sigma_2 = {s2:.4e}, "
              f"sigma_tot = {s_tot:.4e}")
    a_2 = power_law_slope(lambda v, m1, m2, g: yukawa.sigma_m_cm2_per_g(v, m1, 40.0, g) +
                          yukawa.sigma_m_cm2_per_g(v, m2, 40.0, g), 50.0, 200.0,
                          m_phi_1, m_phi_2, 0.5)
    print(f"  a (50-200 km/s) for two-mediator = {a_2:.3f}")
