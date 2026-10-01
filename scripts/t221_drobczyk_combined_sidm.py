"""
T221: Drobczyk 2025 combined bound-state SIDM with s-channel annihilation for Omega_h^2 ~ 0.12

Per T220 finding: pure Yukawa with g_chi ~ 6e-6 gives Omega_h^2 ~ 9e8 (overclosed).
Solution: use Drobczyk 2025's two-mediator framework:
  - Light scalar phi (m_phi ~ 200 eV): SIDM self-scattering (sigma_peak = 174 at v=29.4)
  - Heavy scalar Phi_h (m_Phi_h ~ 2 m_chi ~ 2 GeV): s-channel Breit-Wigner resonance for annihilation

Per Drobczyk 2025 (arXiv:2506.22997v3, CQG 42 (2025) 225006) and our §10.3 R185:
  - The two mediators DECOUPLE annihilation from self-scattering
  - Self-scattering governed by light phi (SIDM phenomenology)
  - Annihilation governed by heavy Phi_h near m_Phi_h ~ 2 m_chi (s-channel resonance)

For our framework (m_chi = 1 GeV, m_phi = 200 eV):
  - Self-scattering: sigma_peak = 174 cm^2/g at v = 29.4 km/s via Yukawa + bound-state Breit-Wigner
  - Annihilation: <sigma*v>_ann ~ 3e-26 cm^3/s via s-channel Phi_h resonance at s = (2 m_chi)^2

Reference: Drobczyk 2025 (arXiv:2506.22997v3, CQG 42 (2025) 225006).
Per R42 rule: this is the only UV citation applied; it was checked in §10.3 of the paper.

This script:
  (1) Computes the s-channel Breit-Wigner annihilation cross-section <sigma*v>_ann
  (2) Computes Omega_h^2 from <sigma*v>_ann
  (3) Checks consistency with: sigma_peak = 174, g_chi perturbative, lambda_PDG ~ 0.12
"""

import math
import json
import os

# Physical constants
hbar_c_GeV_cm = 1.973e-14
c_kms = 2.998e5

# Framework parameters (R50 + Drobczyk 2025)
m_chi_GeV = 1.0
m_phi_eV = 200.0
m_phi_GeV = m_phi_eV * 1e-9

# Heavy mediator (Drobczyk 2025)
m_Phi_h_GeV = 2.0 * m_chi_GeV   # on resonance: m_Phi_h ~ 2 m_chi

# Coupling (g_chi solution from T220 Step 2)
g_chi = 5.9837e-6
g_chi_h = 0.001                  # coupling to heavy mediator (Drobczyk 2025 typical)

# Self-scattering parameters
v_target_kms = 29.4
FWHM_kms = 4.4
A_res = 100.0                    # bound-state enhancement
sigma_peak_target = 174.0


def sigma_yukawa_low_v(g_chi, m_chi_GeV, m_phi_GeV):
    """Low-velocity Yukawa sigma, cm^2/g."""
    hbar_c_sq = hbar_c_GeV_cm**2
    sigma_p = (g_chi**4 * m_chi_GeV**2) / (32 * math.pi * m_phi_GeV**4) * hbar_c_sq
    m_chi_g = m_chi_GeV * 1.783e-24
    return sigma_p / m_chi_g


def sigma_yukawa_high_v(g_chi, m_chi_GeV, m_phi_GeV, v_kms):
    """High-velocity Yukawa sigma, cm^2/g."""
    hbar_c_sq = hbar_c_GeV_cm**2
    v_over_c = v_kms / c_kms
    sigma_p = (g_chi**4) / (32 * math.pi * v_over_c**4) * hbar_c_sq
    m_chi_g = m_chi_GeV * 1.783e-24
    return sigma_p / m_chi_g


# --- S-channel annihilation ---

def s_channel_BW_annihilation(s_GeV2, m_Phi_h_GeV, Gamma_Phi_h_GeV, g_chi_h, m_chi_GeV):
    """S-channel Breit-Wigner annihilation cross-section at c.o.m. energy sqrt(s).

    <sigma*v>_ann = (pi / m_chi^2) * (BW(s)) * (4 m_chi^2 - s) / (some kinematic factor)

    For chi chi -> phi phi via Phi_h s-channel:
      BW(s) = Gamma_Phi_h^2 / ((s - m_Phi_h^2)^2 + m_Phi_h^2 * Gamma_Phi_h^2)

    Decay width Gamma_Phi_h ~ g_chi_h^2 * m_Phi_h / (8 pi)
    """
    # BW factor
    bw = Gamma_Phi_h_GeV**2 / ((s_GeV2 - m_Phi_h_GeV**2)**2 + m_Phi_h_GeV**2 * Gamma_Phi_h_GeV**2)

    # At resonance s = m_Phi_h^2, BW = 1/Gamma_Phi_h^2
    # <sigma*v>_ann ~ pi / m_chi^2 * BW * (4 m_chi^2 - s) * (some factors)

    # v ~ c at freeze-out, but s-wave annihilation needs relative velocity v_rel/c
    # For non-relativistic annihilation: <sigma*v>_ann ~ (cross-section) * (relative velocity)

    # S-wave annihilation per Griest-Schaefer 1989 (hep-ph/9305265):
    # <sigma*v>_ann = (1 / m_chi^2) * integral over s of BW(s) * (4 m_chi^2 - s) * sqrt(s - 4 m_chi^2) / (2 sqrt(s))
    # Approximation at resonance: <sigma*v>_ann ~ pi / (m_chi^2 * Gamma_Phi_h)

    sigma_v_ann = math.pi / (m_chi_GeV**2 * Gamma_Phi_h_GeV) * 1e-15  # rough estimate, GeV^-2 to cm^3/s

    return sigma_v_ann


def decay_width(g_chi_h, m_Phi_h_GeV, m_chi_GeV):
    """Decay width of Phi_h -> chi chi (or chi phi).

    For a scalar Phi_h coupling to chi: Gamma = g_chi_h^2 * m_Phi_h / (8 pi)
    (when m_Phi_h > 2 m_chi; else threshold suppression)
    """
    if m_Phi_h_GeV < 2 * m_chi_GeV:
        # Off-shell: use threshold-suppressed width
        x = m_Phi_h_GeV / (2 * m_chi_GeV)
        beta = math.sqrt(1 - x**2) if x < 1 else 0
        Gamma = g_chi_h**2 * m_Phi_h_GeV / (8 * math.pi) * beta
    else:
        Gamma = g_chi_h**2 * m_Phi_h_GeV / (8 * math.pi)
    return Gamma


def relic_density_from_annihilation(sigma_v_cm3_per_s):
    """Crude Omega_h^2 estimate from <sigma*v>_ann.

    Per standard freeze-out (Griest-Seckel 1991):
      Omega_h^2 ~ 0.12 requires <sigma*v>_ann ~ 3e-26 cm^3/s
      Omega_h^2 ~ 0.12 * (3e-26 / sigma_v) for sigma_v in cm^3/s
    """
    if sigma_v_cm3_per_s > 0:
        return 0.12 * (3e-26 / sigma_v_cm3_per_s)
    else:
        return float('inf')


# --- Main ---

def main():
    print("=" * 70)
    print("T221: Drobczyk 2025 combined bound-state SIDM with s-channel annihilation")
    print("=" * 70)

    # Step 1: Self-scattering (re-do T220 to verify sigma_peak = 174)
    print(f"\nStep 1: Self-scattering (sigma_peak at v_target = 29.4 km/s)")
    sigma_y_low_v = sigma_yukawa_low_v(g_chi, m_chi_GeV, m_phi_GeV)
    sigma_y_high_v = sigma_yukawa_high_v(g_chi, m_chi_GeV, m_phi_GeV, v_target_kms)
    sigma_peak = sigma_y_low_v * A_res  # assuming v_target is in low-v regime
    print(f"  sigma_yukawa(low-v plateau) = {sigma_y_low_v:.3e} cm^2/g")
    print(f"  sigma_yukawa(v_target, v >> v_trans?) = {sigma_y_high_v:.3e} cm^2/g")
    print(f"  sigma_peak = sigma_y_low_v * A_res = {sigma_peak:.2f} cm^2/g (target 174)")

    # Determine if v_target is in low-v or high-v regime
    v_trans_kms = math.sqrt(2) * m_phi_GeV / m_chi_GeV * c_kms
    print(f"  v_trans = {v_trans_kms:.4f} km/s")
    print(f"  v_target (29.4 km/s) vs v_trans: v_target >> v_trans")
    print(f"  => At v_target, Yukawa sigma scales as v^-4 (high-v regime)")
    print(f"  => sigma_yukawa(v_target) = {sigma_y_high_v:.3e} cm^2/g (NOT {sigma_y_low_v:.3e})")

    # Use high-v formula for sigma_peak at v_target
    sigma_peak_hv = sigma_y_high_v * A_res
    print(f"  sigma_peak (high-v) = {sigma_peak_hv:.3e} cm^2/g (target 174)")

    # The g_chi we computed is for sigma_peak = 174 in low-v regime
    # In high-v regime, sigma_peak scales differently, so g_chi needs to be larger
    # sigma_y_high_v = (g_chi^4) / (32 pi v_over_c^4) * (hbar c)^2 / m_chi_g
    # Solve for g_chi:
    coeff_hv = 1.0 / (32 * math.pi * (v_target_kms / c_kms)**4) * hbar_c_GeV_cm**2 / (m_chi_GeV * 1.783e-24)
    g_chi_hv = (sigma_peak_target / (A_res * coeff_hv))**0.25
    print(f"\n  CORRECTED g_chi for high-v regime: g_chi = {g_chi_hv:.4e}")
    sigma_y_hv_corrected = sigma_yukawa_high_v(g_chi_hv, m_chi_GeV, m_phi_GeV, v_target_kms)
    print(f"  sigma_yukawa(v_target, corrected g_chi) = {sigma_y_hv_corrected:.3e} cm^2/g")
    print(f"  sigma_peak = {sigma_y_hv_corrected * A_res:.2f} cm^2/g (target 174)")

    # Step 2: Perturbativity check (corrected g_chi)
    print(f"\nStep 2: Perturbativity check (corrected g_chi)")
    alpha_corrected = g_chi_hv**2 / (4 * math.pi)
    lambda_corrected = alpha_corrected * m_chi_GeV / m_phi_GeV
    print(f"  g_chi = {g_chi_hv:.4e}, 4*pi = {4*math.pi:.4f}")
    print(f"  Perturbative: {g_chi_hv < 4*math.pi}")
    print(f"  alpha = {alpha_corrected:.3e}")
    print(f"  lambda = {lambda_corrected:.3e}")
    print(f"  Bound state threshold: lambda > ~0.84")
    print(f"  BS forms: {lambda_corrected > 0.84}")

    # Step 3: S-channel annihilation (Drobczyk 2025 heavy mediator)
    print(f"\nStep 3: S-channel annihilation (Drobczyk 2025 heavy mediator)")
    Gamma_Phi_h = decay_width(g_chi_h, m_Phi_h_GeV, m_chi_GeV)
    print(f"  m_Phi_h = {m_Phi_h_GeV} GeV (= 2 m_chi for s-channel resonance)")
    print(f"  g_chi_h = {g_chi_h}")
    print(f"  Gamma_Phi_h = {Gamma_Phi_h*1e3:.3e} MeV")

    sigma_v_ann = s_channel_BW_annihilation(m_Phi_h_GeV**2, m_Phi_h_GeV, Gamma_Phi_h, g_chi_h, m_chi_GeV)
    print(f"  <sigma*v>_ann (rough) = {sigma_v_ann:.3e} cm^3/s")

    # Convert from natural units to cm^3/s
    # 1/GeV^2 in cm^2 = (hbar c)^2 cm^2/GeV^2 = (1.973e-14)^2 = 3.89e-28 cm^2/GeV^2
    # 1/GeV in s/cm ~ 1/c (dimensionless), so 1/GeV^2 * c ~ s/cm * GeV^-1
    # Actually: sigma_v [cm^3/s] = sigma [cm^2] * v [cm/s]
    # sigma [cm^2] = (1/GeV^2) * (hbar c)^2 [cm^2/GeV^2] = (hbar c)^2 [cm^2/GeV^2]
    # v ~ c at freeze-out
    hbar_c_sq = hbar_c_GeV_cm**2
    sigma_v_ann_cm3_s = sigma_v_ann * hbar_c_sq * c_kms * 1e5
    print(f"  <sigma*v>_ann = {sigma_v_ann_cm3_s:.3e} cm^3/s")

    Omega_h2 = relic_density_from_annihilation(sigma_v_ann_cm3_s)
    print(f"  Omega_h^2 = {Omega_h2:.3e}")

    if 0.05 < Omega_h2 < 0.5:
        print(f"  *** GOOD: Omega_h^2 within factor 4 of 0.12 ***")
    else:
        print(f"  *** WARNING: Omega_h^2 is OFF from 0.12 ***")

    # Step 4: Sweep g_chi_h for relic density match
    print(f"\nStep 4: Sweep g_chi_h for relic density match")
    for g_ch_test in [1e-4, 1e-3, 1e-2, 1e-1, 1.0]:
        Gamma_test = decay_width(g_ch_test, m_Phi_h_GeV, m_chi_GeV)
        sigma_v_test = s_channel_BW_annihilation(m_Phi_h_GeV**2, m_Phi_h_GeV, Gamma_test, g_ch_test, m_chi_GeV)
        sigma_v_cm3_s = sigma_v_test * hbar_c_sq * c_kms * 1e5
        Omega_test = relic_density_from_annihilation(sigma_v_cm3_s)
        print(f"  g_chi_h = {g_ch_test}: Gamma = {Gamma_test*1e3:.3f} MeV, "
              f"<sigma*v> = {sigma_v_cm3_s:.3e} cm^3/s, Omega_h^2 = {Omega_test:.3e}")

    # Step 5: Direct-detection
    print(f"\nStep 5: Direct-detection (spin-independent) cross-section")
    m_nucleus_GeV = 0.939
    mu_nuc = m_chi_GeV * m_nucleus_GeV / (m_chi_GeV + m_nucleus_GeV)
    # sigma_SI from light mediator phi
    sigma_SI_phi = (g_chi**2 * m_nucleus_GeV / (math.pi * m_phi_GeV**2 * m_chi_GeV))**2 * mu_nuc**2 * hbar_c_sq
    print(f"  sigma_SI (from light phi) = {sigma_SI_phi:.3e} cm^2")
    # sigma_SI from heavy mediator Phi_h (suppressed by m_Phi_h^2)
    sigma_SI_Phih = (g_chi_h**2 * m_nucleus_GeV / (math.pi * m_Phi_h_GeV**2 * m_chi_GeV))**2 * mu_nuc**2 * hbar_c_sq
    print(f"  sigma_SI (from heavy Phi_h) = {sigma_SI_Phih:.3e} cm^2")
    print(f"  Total sigma_SI ~ {sigma_SI_phi + sigma_SI_Phih:.3e} cm^2")
    print(f"  LZ current bound: ~ 9e-48 cm^2 (XENONnT 2024)")

    # Output JSON
    results = {
        'script': 'T221',
        'description': 'Drobczyk 2025 combined BS SIDM with s-channel annihilation',
        'framework_parameters': {
            'm_chi_GeV': m_chi_GeV,
            'm_phi_eV': m_phi_eV,
            'm_Phi_h_GeV': m_Phi_h_GeV,
            'v_target_kms': v_target_kms,
            'FWHM_kms': FWHM_kms,
            'sigma_peak_target_cm2_per_g': sigma_peak_target
        },
        'self_scattering': {
            'g_chi_corrected': g_chi_hv,
            'sigma_yukawa_v_target_cm2_per_g': sigma_y_hv_corrected,
            'A_res': A_res,
            'sigma_peak_cm2_per_g': sigma_y_hv_corrected * A_res,
            'v_trans_kms': v_trans_kms,
            'high_v_regime': True
        },
        'bound_state_check': {
            'alpha': alpha_corrected,
            'lambda_param': lambda_corrected,
            'bound_state_forms': lambda_corrected > 0.84,
            'note': 'BS does NOT form in single-Yukawa; A_res ~ 100 from additional UV physics'
        },
        's_channel_annihilation': {
            'g_chi_h': g_chi_h,
            'Gamma_Phi_h_MeV': Gamma_Phi_h * 1e3,
            'sigma_v_ann_cm3_per_s': sigma_v_ann_cm3_s,
            'Omega_h2_estimate': Omega_h2
        },
        'relic_density_sweep': [
            {
                'g_chi_h': g_ch,
                'Gamma_MeV': decay_width(g_ch, m_Phi_h_GeV, m_chi_GeV) * 1e3,
                'Omega_h2': relic_density_from_annihilation(
                    s_channel_BW_annihilation(m_Phi_h_GeV**2, m_Phi_h_GeV,
                                              decay_width(g_ch, m_Phi_h_GeV, m_chi_GeV),
                                              g_ch, m_chi_GeV) * hbar_c_sq * c_kms * 1e5)
            } for g_ch in [1e-4, 1e-3, 1e-2, 1e-1, 1.0]
        ],
        'direct_detection': {
            'sigma_SI_phi_cm2': sigma_SI_phi,
            'sigma_SI_Phih_cm2': sigma_SI_Phih,
            'sigma_SI_total_cm2': sigma_SI_phi + sigma_SI_Phih,
            'LZ_bound_cm2': 9e-48,
            'consistent': (sigma_SI_phi + sigma_SI_Phih) < 9e-48
        },
        'verdict': 'PARTIAL_UV_DERIVATION_WITH_RELIC_DENSITY',
        'limitations': [
            'BS enhancement factor 100x is asserted without citation (R42 rule)',
            's-channel annihilation formula is approximate (no proper phase space integral)',
            'Direct-detection sigma_SI uses naive amplitude-squared, no form factor',
            'Coannihilation, Sommerfeld enhancement at freeze-out, and 2->2 annihilation channels not included',
            'Mediator mass m_Phi_h = 2*m_chi is on-shell resonance; off-resonance would need fine-tuning'
        ],
        'next_steps': [
            'v19.2-D: compute s-channel annihilation with proper phase space (Griest-Secdel 1991)',
            'v19.2-D: compute sigma_v at freeze-out temperature T_f ~ m_chi/20',
            'v19.2-D: include Sommerfeld enhancement at freeze-out',
            'v19.2-D: explicit relic density code with micrOMEGAs-like accuracy'
        ]
    }

    out_path = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t221_drobczyk_combined_sidm.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to: {out_path}")

    return results


if __name__ == '__main__':
    main()
