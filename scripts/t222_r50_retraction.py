"""
T222: Numerical RETRACTION of R50 bound-state SIDM UV derivation

Per numerical verification (T220 + T221):
  1. R50's g_chi = 5.98e-6 is WRONG - actual is 2.93e-3 (corrected for high-v regime)
  2. R50's claim "no bound state forms" is WRONG - with corrected g_chi, lambda = 3.4 > 0.84
  3. Bound state DOES form with E_B ~ 5 eV
  4. Relic density match found at g_chi_h ~ 1e-2 (Omega_h^2 ~ 0.78, off by factor ~7)
  5. Direct-detection sigma_SI = 4.4e-8 cm^2 (using proper amplitude) - WAY above LZ bound
  6. sigma_SI ~ 6.5e-24 cm^2 (using T221 approximate amplitude) - also above LZ bound

The fundamental problem: with m_phi = 200 eV and sigma_peak = 174 cm^2/g,
the direct-detection cross-section is constrained to be HUGE due to 1/m_phi^4
propagator enhancement. Standard solutions (inelastic DM) conflict with the
v_resonance = 29.4 km/s requirement.

This means R50's UV derivation does NOT work. The sigma_peak = 174 cm^2/g is NOT
derivable from a simple single-Yukawa + bound-state Breit-Wigner model.

Per proposalcomment.docx second-pass reviewer's recommendation:
  "If the UV derivation is possible: do it. One dedicated effort, not a bundle
   cycle. If it succeeds, the paper has a prediction. If it fails, the paper
   has a negative result about a class of dark-sector models."

T220-T222 show that the bound-state SIDM UV completion FAILS. This is a NEGATIVE
RESULT that should be added to the paper's no-go catalogue.

The framework's sigma_peak = 174 cm^2/g remains UNANCHORED. Per the paper's
honest framing (§3 R47 retraction), this is the state of the project.
"""

import math
import json
import os

# Re-do the calculations with PROPER amplitudes

hbar_c_GeV_cm = 1.973e-14
hbar_c_sq = hbar_c_GeV_cm**2

m_chi_GeV = 1.0
m_phi_GeV = 200e-9
v_target_kms = 29.4
FWHM_kms = 4.4
A_res = 100.0
sigma_peak_target = 174.0
c_kms = 2.998e5

# Corrected g_chi for high-v regime
g_chi = 2.9339e-3

alpha = g_chi**2 / (4 * math.pi)
lambda_param = alpha * m_chi_GeV / m_phi_GeV

print("=" * 70)
print("T222: NUMERICAL RETRACTION OF R50 BOUND-STATE SIDM UV DERIVATION")
print("=" * 70)

# Direct-detection - PROPER amplitude (Fitzpatrick et al. 2013 JCAP)
print("\nDirect-detection with PROPER amplitude (tree-level t-channel exchange):")
print("Reference: Fitzpatrick et al. 2013, arXiv:1203.3542 (Eq 2.7)")

m_N_GeV = 0.939
mu_nuc = m_chi_GeV * m_N_GeV / (m_chi_GeV + m_N_GeV)
# sigma_SI (tree-level, no form factor) per Fitzpatrick et al. 2013:
# sigma_SI = (4 alpha_chi m_N^2 / pi) * mu^2 * (1/m_phi^4) * (hbar c)^2
sigma_SI_proper = (4 * alpha * m_N_GeV**2 / math.pi) * mu_nuc**2 * (1/m_phi_GeV**4) * hbar_c_sq
print(f"  sigma_SI (proper) = {sigma_SI_proper:.3e} cm^2")

# LZ / XENONnT bound
LZ_bound = 9e-48
print(f"  LZ/XENONnT bound: {LZ_bound:.3e} cm^2")
ratio = sigma_SI_proper / LZ_bound
print(f"  Ratio sigma_SI / LZ_bound = {ratio:.3e}")
if ratio > 1:
    print(f"  *** EXCLUDED: sigma_SI is {ratio:.1e} above LZ bound ***")
    print(f"  Need to reduce sigma_SI by factor {1/ratio:.3e}")

# Solutions:
print("\nPossible solutions:")
print("  1. Inelastic DM (delta >> keV) - but conflicts with v_resonance = 29.4 km/s")
print("  2. Pseudoscalar mediator - reduces sigma_SI by ~v^2/m_chi^2 ~ 1e-3")
print("  3. Form factor suppression at finite q (only for very light mediator)")
print("  4. Different UV completion (NOT bound-state SIDM)")

# Inelastic DM check
print("\nInelastic DM check (Tucker-Smith & Weiner 2001):")
print("  For v_resonance = 29.4 km/s, E_B = m_chi v_resonance^2 / 2 ~ 4.8 eV")
print("  Inelastic splitting delta ~ 5 eV: NO direct-detection suppression")
print("  Inelastic splitting delta ~ 100 keV: full suppression but v_resonance ~ 3000 km/s")
print("  => Inelastic DM cannot satisfy both")

# Pseudo-scalar mediator check
print("\nPseudo-scalar mediator check (vector vs pseudoscalar coupling):")
print("  For pseudoscalar, sigma_SI reduced by ~ (v_N / m_phi)^2 ~ (10 km/s / 200 eV)^2")
v_N_kms = 10.0
v_N_over_c = v_N_kms / c_kms
sigma_SI_pseudo = sigma_SI_proper * v_N_over_c**2 / (m_phi_GeV / m_chi_GeV)**2
print(f"  v_N / c = {v_N_over_c:.3e}")
print(f"  sigma_SI (pseudoscalar estimate) = {sigma_SI_pseudo:.3e} cm^2")
if sigma_SI_pseudo < LZ_bound:
    print(f"  *** PSEUDOSCALAR WORKS! sigma_SI < LZ bound ***")
else:
    print(f"  *** Pseudoscalar still excludes, need smaller g_chi or larger m_phi ***")

# Form factor check
print("\nForm factor check (finite-q suppression):")
print("  For m_phi ~ 200 eV, finite-q suppression is ~ q^2 / m_phi^2 ~ (10 MeV)^2 / (200 eV)^2")
print("  = 100 / 4e-14 ~ 2.5e15 (huge enhancement, not suppression!)")
print("  => Form factor makes it WORSE, not better")

# Conclusion
print("\n" + "=" * 70)
print("CONCLUSION (T222):")
print("=" * 70)
print("R50's bound-state SIDM UV derivation DOES NOT WORK for direct-detection.")
print("The sigma_peak = 174 cm^2/g at m_phi = 200 eV requires g_chi = 2.93e-3,")
print("which gives sigma_SI ~ 4.4e-8 cm^2 - WAY above LZ bound.")
print("Inelastic DM solution conflicts with v_resonance = 29.4 km/s requirement.")
print("Pseudo-scalar / form factor solutions are insufficient.")
print("")
print("RETRACTION OF R50:")
print("  - The 'plausible UV completion' claim does NOT survive numerical check")
print("  - sigma_peak = 174 cm^2/g is NOT derivable from bound-state SIDM")
print("  - This is a NEGATIVE RESULT that should be added to the no-go catalogue")
print("")
print("Per proposalcomment.docx reviewer:")
print("  'If the UV derivation is possible: do it... If it fails, the paper has")
print("   a negative result about a class of dark-sector models.'")
print("")
print("T220-T222 IS the negative result. sigma_peak = 174 cm^2/g is unanchored.")
print("Framework remains a 'catalog of features that need UV derivation'.")

# Output JSON
results = {
    'script': 'T222',
    'description': 'Numerical RETRACTION of R50 bound-state SIDM UV derivation',
    'R50_overclaim': 'sigma_peak = 174 cm^2/g achievable via bound-state SIDM at g_chi ~ 6e-6',
    'R50_correction': {
        'g_chi_corrected': 2.93e-3,
        'reason': 'v_target = 29.4 km/s >> v_trans = 0.085 km/s (high-v regime)',
        'bound_state_forms': True,
        'lambda_param': lambda_param,
        'E_B_eV': 4.8
    },
    'direct_detection_check': {
        'sigma_SI_proper_cm2': sigma_SI_proper,
        'LZ_bound_cm2': LZ_bound,
        'excluded': sigma_SI_proper > LZ_bound,
        'exclusion_factor': ratio
    },
    'inelastic_DM_check': {
        'compatible_with_v_resonance': False,
        'reason': 'v_resonance = 29.4 km/s requires E_B ~ 5 eV (delta ~ eV), but DD suppression needs delta ~ 100 keV'
    },
    'pseudoscalar_check': {
        'sigma_SI_estimate_cm2': sigma_SI_pseudo,
        'works': sigma_SI_pseudo < LZ_bound
    },
    'form_factor_check': {
        'improves_DD': False,
        'reason': 'Finite-q enhancement, not suppression, for superlight mediator'
    },
    'verdict': 'R50_RETRACTED',
    'no_go_added': 'Bound-state SIDM with v_resonance = 29.4 km/s (R50 retracted)',
    'new_no_go_six': {
        'id': 'No-go #6',
        'description': 'Bound-state SIDM UV derivation fails direct-detection',
        'mechanism': 'm_phi ~ 200 eV requires g_chi ~ 3e-3 for sigma_peak = 174; gives sigma_SI ~ 4e-8 cm^2 >> LZ bound',
        'inelastic_DM_does_not_save': True,
        'pseudoscalar_insufficient': True
    },
    'next_steps': [
        'v19.2-D: explicit dark photon mediator (vector, not scalar) for DD compatibility',
        'v19.2-D: pseudo-Dirac splitting at keV scale for inelastic DD suppression (but conflicts with v_resonance)',
        'v19.2-D: explore COMPLETELY DIFFERENT UV mechanism (geometric mass ladder, hidden gauge, etc.)'
    ]
}

out_path = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t222_r50_retraction.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {out_path}")
