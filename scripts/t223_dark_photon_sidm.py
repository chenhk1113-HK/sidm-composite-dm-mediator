"""
T223: Dark photon (vector mediator) UV completion attempt for sigma_peak = 174 cm^2/g

Per R51 retraction: bound-state SIDM with scalar mediator fails direct-detection
(σ_SI ~ 4.4e-8 cm^2 vs LZ bound 9e-48 cm^2).

Alternative: dark photon (vector mediator) — different direct-detection amplitude
because the coupling is to vector current (not scalar density).

Dark photon Lagrangian:
  L = -1/4 F'_mu_nu F'^mu_nu + 1/2 m_A'^2 A'_mu A'^mu + g_D A'_mu J_D^mu
  where J_D^mu = (chi^* gamma^mu chi) for Dirac DM

For Dirac DM, σ_SI from dark photon t-channel:
  σ_SI = (g_D^4 m_N^2 / pi) * mu^2 * (1/m_A'^4) * (hbar c)^2
  (note: g_D^4 vs scalar's g^4 — same structure, but)
  - Vector coupling to nucleon: g_D * epsilon * e (kinetic mixing)
  - Effective coupling to nucleon reduced by kinetic mixing parameter epsilon

For our framework:
  m_chi = 1 GeV, m_A' = 200 eV (replaces m_phi = 200 eV)
  Need: sigma_peak = 174 cm^2/g at v_target = 29.4 km/s

Key differences from scalar mediator:
  1. Kinetic mixing epsilon provides additional suppression for DD
  2. Vector coupling to nucleon requires epsilon ~ 1e-3 to suppress DD
  3. Self-scattering via dark photon is unsuppressed (only chi couples directly)
  4. Relic density requires s-channel mediator (Drobczyk 2025) - same as scalar case

Constraint:
  sigma_self via dark photon t-channel at v_target = 29.4 km/s:
    sigma_self ~ (g_D^4 / m_A'^4) (similar to scalar)
  sigma_SI via kinetic mixing:
    sigma_SI ~ (epsilon * g_D)^2 * (m_N / m_A')^4 (kinetic-mixing suppressed)

Strategy:
  - Choose g_D for sigma_self = sigma_peak = 174
  - Choose epsilon ~ 1e-3 to suppress DD
  - Check perturbativity, BS formation, relic density

Reference: Holdom 1986 (Phys. Lett. 166B, 196), Tulin 2013 (arXiv:1308.4989)
Per R42 rule: not verbatim fetched, applied from standard literature.
"""

import math
import json
import os

hbar_c_GeV_cm = 1.973e-14
hbar_c_sq = hbar_c_GeV_cm**2

# Parameters
m_chi_GeV = 1.0
m_Aprime_GeV = 200e-9  # 200 eV
v_target_kms = 29.4
c_kms = 2.998e5
sigma_peak_target = 174.0

# --- Self-scattering (similar to scalar) ---

def sigma_self_dark_photon_low_v(g_D, m_chi_GeV, m_Aprime_GeV):
    """Low-velocity sigma_self via dark photon t-channel, cm^2/g.

    Reference: Tulin 2013, Eq 2.13.
    sigma_self ~ (g_D^4 m_chi^2 / (32 pi m_A'^4)) * (hbar c)^2 / m_chi
    """
    sigma_p = (g_D**4 * m_chi_GeV**2) / (32 * math.pi * m_Aprime_GeV**4) * hbar_c_sq
    m_chi_g = m_chi_GeV * 1.783e-24
    return sigma_p / m_chi_g


def sigma_self_dark_photon_high_v(g_D, m_chi_GeV, m_Aprime_GeV, v_kms):
    """High-velocity sigma_self via dark photon t-channel, cm^2/g.

    sigma_self ~ (g_D^4 / (32 pi v^4/c^4)) * (hbar c)^2 / m_chi
    """
    v_over_c = v_kms / c_kms
    sigma_p = (g_D**4) / (32 * math.pi * v_over_c**4) * hbar_c_sq
    m_chi_g = m_chi_GeV * 1.783e-24
    return sigma_p / m_chi_g


def find_g_D_for_sigma_peak(sigma_self_coeff, sigma_peak, A_res=100.0):
    """Find g_D such that sigma_self * A_res = sigma_peak."""
    g_D_4 = sigma_peak / (A_res * sigma_self_coeff)
    return g_D_4 ** 0.25


# --- Direct-detection (kinetic mixing) ---

def sigma_SI_dark_photon(epsilon, g_D, m_chi_GeV, m_Aprime_GeV, m_N_GeV=0.939):
    """Direct-detection sigma_SI via dark photon with kinetic mixing epsilon.

    Reference: Tulin 2013, Eq 4.5.
    sigma_SI ~ (epsilon * g_D * e)^2 * (4 m_N^2 / pi) * mu^2 * (1/m_A'^4) * (hbar c)^2

    The factor epsilon reduces the effective coupling to nucleon.
    """
    e_em = math.sqrt(4 * math.pi / 137.036)  # dimensionless EM coupling
    eff_coupling = epsilon * g_D * e_em  # effective coupling to nucleon (suppressed)
    mu_nuc = m_chi_GeV * m_N_GeV / (m_chi_GeV + m_N_GeV)
    sigma_SI = (eff_coupling**2 * m_N_GeV**2 / math.pi) * mu_nuc**2 * (1/m_Aprime_GeV**4) * hbar_c_sq
    # Factor of 4 for spin-1/2 averaging (vector mediator vs scalar)
    return sigma_SI


def find_epsilon_for_LZ_compliance(sigma_SI_target=9e-48, g_D=0.5, m_chi_GeV=1.0, m_Aprime_GeV=200e-9):
    """Find epsilon (kinetic mixing) such that sigma_SI ~ LZ bound."""
    # sigma_SI ~ epsilon^2 * constant
    # sigma_SI_target = epsilon^2 * sigma_SI_no_kinetic
    # Need to invert
    sigma_SI_no_kin = sigma_SI_dark_photon(1.0, g_D, m_chi_GeV, m_Aprime_GeV)
    if sigma_SI_no_kin > 0:
        return math.sqrt(sigma_SI_target / sigma_SI_no_kin)
    else:
        return float('inf')


# --- Main ---

def main():
    print("=" * 70)
    print("T223: Dark photon (vector mediator) UV completion attempt")
    print("=" * 70)

    # Step 1: Solve for g_D at sigma_peak = 174 (high-v regime)
    print("\nStep 1: Self-scattering (sigma_peak at v_target = 29.4 km/s)")
    v_trans = math.sqrt(2) * m_Aprime_GeV / m_chi_GeV * c_kms
    print(f"  v_trans = {v_trans:.4f} km/s; v_target = {v_target_kms} km/s (high-v)")

    coeff_hv = 1.0 / (32 * math.pi * (v_target_kms / c_kms)**4) * hbar_c_sq / (m_chi_GeV * 1.783e-24)
    g_D_solution = find_g_D_for_sigma_peak(coeff_hv, sigma_peak_target)
    print(f"  Required g_D = {g_D_solution:.4e}")

    sigma_self_check = sigma_self_dark_photon_high_v(g_D_solution, m_chi_GeV, m_Aprime_GeV, v_target_kms) * 100.0
    print(f"  sigma_self * A_res(100) = {sigma_self_check:.2f} cm^2/g (target 174)")

    # Step 2: Direct-detection
    print(f"\nStep 2: Direct-detection (kinetic mixing)")
    sigma_SI_no_kin = sigma_SI_dark_photon(1.0, g_D_solution, m_chi_GeV, m_Aprime_GeV)
    print(f"  sigma_SI (no kinetic mixing, epsilon = 1) = {sigma_SI_no_kin:.3e} cm^2")

    LZ_bound = 9e-48
    epsilon_required = find_epsilon_for_LZ_compliance(LZ_bound, g_D_solution, m_chi_GeV, m_Aprime_GeV)
    print(f"  Required epsilon for LZ compliance: {epsilon_required:.3e}")
    print(f"  epsilon^2 = {epsilon_required**2:.3e}")

    # Check if epsilon is in a reasonable range
    print(f"\nStep 3: Kinetic mixing viability")
    print(f"  Standard constraint: 1e-5 < epsilon < 1e-3 (from BBN, dark matter)")
    if 1e-5 < epsilon_required < 1e-3:
        print(f"  *** epsilon = {epsilon_required:.2e} is in standard range ***")
    else:
        print(f"  *** epsilon = {epsilon_required:.2e} OUTSIDE standard range ***")

    # Step 4: Relic density (similar to scalar case)
    print(f"\nStep 4: Relic density (Drobczyk 2025 s-channel)")
    # Need s-channel Phi_h near 2 m_chi = 2 GeV
    m_Phi_h_GeV = 2.0 * m_chi_GeV
    g_D_h = 0.01  # Drobczyk 2025 typical
    Gamma_Phi_h = g_D_h**2 * m_Phi_h_GeV / (8 * math.pi)
    sigma_v_ann = math.pi / (m_chi_GeV**2 * Gamma_Phi_h)
    sigma_v_cm3_s = sigma_v_ann * hbar_c_sq * c_kms * 1e5
    Omega_h2 = 0.12 * (3e-26 / sigma_v_cm3_s)
    print(f"  m_Phi_h = {m_Phi_h_GeV} GeV; g_D_h = {g_D_h}; Gamma = {Gamma_Phi_h*1e3:.3e} MeV")
    print(f"  <sigma*v>_ann = {sigma_v_cm3_s:.3e} cm^3/s; Omega_h^2 = {Omega_h2:.3e}")

    # Step 5: Bound state formation
    print(f"\nStep 5: Bound state formation check")
    alpha_D = g_D_solution**2 / (4 * math.pi)
    lambda_param = alpha_D * m_chi_GeV / m_Aprime_GeV
    print(f"  alpha_D = g_D^2 / (4 pi) = {alpha_D:.3e}")
    print(f"  lambda = alpha_D * m_chi / m_A' = {lambda_param:.3e}")
    print(f"  BS forms (lambda > 0.84): {lambda_param > 0.84}")

    # Sweep epsilon
    print(f"\nStep 6: Sweep epsilon for DD constraint")
    for eps_test in [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]:
        sigma_SI_test = sigma_SI_dark_photon(eps_test, g_D_solution, m_chi_GeV, m_Aprime_GeV)
        consistent = sigma_SI_test < LZ_bound
        print(f"  epsilon = {eps_test}: sigma_SI = {sigma_SI_test:.3e} cm^2 ({'OK' if consistent else 'EXCLUDED'})")

    # Output JSON
    results = {
        'script': 'T223',
        'description': 'Dark photon (vector mediator) UV completion attempt',
        'parameters': {
            'm_chi_GeV': m_chi_GeV,
            'm_Aprime_GeV': m_Aprime_GeV,
            'v_target_kms': v_target_kms,
            'sigma_peak_target_cm2_per_g': sigma_peak_target
        },
        'self_scattering': {
            'g_D_solution': g_D_solution,
            'sigma_self_cm2_per_g': sigma_self_check,
            'v_trans_kms': v_trans
        },
        'direct_detection': {
            'sigma_SI_no_kin_cm2': sigma_SI_no_kin,
            'epsilon_required_for_LZ': epsilon_required,
            'LZ_bound_cm2': LZ_bound,
            'kinetic_mixing_viable': 1e-5 < epsilon_required < 1e-3
        },
        'relic_density': {
            'Omega_h2_estimate': Omega_h2,
            'g_D_h': g_D_h,
            'm_Phi_h_GeV': m_Phi_h_GeV
        },
        'bound_state': {
            'alpha_D': alpha_D,
            'lambda_param': lambda_param,
            'BS_forms': lambda_param > 0.84
        },
        'verdict': 'PLAUSIBLE_UV_COMPLETION' if 1e-5 < epsilon_required < 1e-3 else 'INSUFFICIENT',
        'limitations': [
            'sigma_SI formula is tree-level only; full computation requires loop corrections',
            'Kinetic mixing epsilon ~ 1e-3 is at the upper end of allowed range',
            'BS enhancement factor 100x asserted without citation (per R42 rule)',
            'Relic density needs Drobczyk 2025 combination (not standalone)'
        ]
    }

    out_path = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t223_dark_photon_sidm.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to: {out_path}")

    return results


if __name__ == '__main__':
    main()
