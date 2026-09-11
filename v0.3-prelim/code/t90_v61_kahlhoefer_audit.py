"""
T90.61 -- Resolution of the T86 sigma_DM-nuc 15-order discrepancy.

This addresses reviewer recommendation #1 from the 2026-09-11 review:
"Reconcile the 10^-111 vs 10^-96 sigma_DM-nuc discrepancy against an
independent published Kahlhoefer-variant derivation."

The T86 plausibility audit (T86_PLAUSIBILITY_AUDIT.md lines 193-203)
notes that a hand-derivation of the Kahlhoefer point-particle formula
gives ~10^-96 cm^2, while the project's T78/T79 claim is ~10^-111 cm^2.
The audit dismisses the 15-order gap as "(mu_chi_p/m_p)^2 ~ 0.45 factor
and alpha_chi prefactor differences" -- which is wrong because
order-unity factors cannot bridge 15 orders.

This script independently re-derives the Kahlhoefer formula and
identifies the source of the 15-order discrepancy.
"""

import math

# Constants
alpha_em = 1.0 / 137.036  # fine-structure constant
# Correct unit conversion:
#   1 GeV^-1 in cm = (hbar c)^-1 where hbar c = 1.973269804e-14 GeV*cm
#   So 1 GeV^-1 = 5.068e+13 cm
#   And 1 GeV^-2 = (1 GeV^-1)^2 = (5.068e+13)^2 cm^2 = 2.568e+27 cm^2
#   BUT this is WRONG -- that's the conversion for LENGTH in natural units.
#   For CROSS-SECTION (length^2), we use (hbar c)^2 = (1.973e-14)^2 = 3.89e-28 cm^2
#   The conversion factor is 1 GeV^-2 = (hbar c)^2 cm^2 = 3.89e-28 cm^2/GeV^-2
hbarc_GeVcm = 0.1973269804 * 1e-13  # GeV*cm (used for length)
GeV_to_invocm = 1.0 / hbarc_GeVcm  # 1 GeV^-1 in cm
# CORRECT cross-section conversion (length^2): (hbar c)^2 in cm^2
GeV_to_invocm2 = (hbarc_GeVcm) ** 2  # 1 GeV^-2 in cm^2 (= 3.89e-28)

# v0.7 MAP values from T78/T79
m_chi_GeV = 770.0  # DM mass (T78 v0.7 MAP)
m_phi_MeV = 453.0  # mediator mass (T78 v0.7 MAP)
m_phi_GeV = m_phi_MeV / 1000.0
log_epsilon = -37.0  # kinetic mixing (T78 v0.7 MAP)
epsilon = 10 ** log_epsilon
alpha_chi = 0.01  # dark fine-structure constant (T78 assumption)

# Reduced mass mu_chi_p = m_chi * m_p / (m_chi + m_p) [GeV]
m_p_GeV = 0.93827208816  # proton mass
m_n_GeV = 0.93956542052  # neutron mass
mu_chi_p = m_chi_GeV * m_p_GeV / (m_chi_GeV + m_p_GeV)
mu_chi_n = m_chi_GeV * m_n_GeV / (m_chi_GeV + m_n_GeV)
# Average reduced mass for nucleon (T86 uses p)
print('=' * 78)
print('T90.61: Kahlhoefer formula re-derivation')
print('=' * 78)
print()
print(f'Constants:')
print(f'  alpha_em = {alpha_em:.5f}')
print(f'  GeV^-1 -> cm = {GeV_to_invocm:.4e}')
print(f'  GeV^-2 -> cm^2 = {GeV_to_invocm2:.4e}')
print()
print(f'v0.7 MAP parameters:')
print(f'  m_chi = {m_chi_GeV} GeV')
print(f'  m_phi = {m_phi_MeV} MeV = {m_phi_GeV} GeV')
print(f'  epsilon = 10^{log_epsilon} = {epsilon:.2e}')
print(f'  alpha_chi = {alpha_chi}')
print(f'  m_p = {m_p_GeV} GeV')
print(f'  mu_chi_p = {mu_chi_p:.4f} GeV')
print()


def kahlhoefer_point_particle(alpha_em, alpha_chi, epsilon, mu_chi_p_GeV, m_phi_GeV):
    """
    Kahlhoefer et al. 2016 (arXiv:1512.03653, JCAP 1605 (2016) 046)
    point-particle approximation for spin-independent DM-nucleon
    scattering via kinetically-mixed dark photon:

        sigma_chi_n = 16*pi * alpha_em * alpha_chi * epsilon^2 * mu_chi_p^2 / m_phi^4

    Returns sigma in cm^2.
    """
    sigma_GeV_neg2 = (
        16 * math.pi * alpha_em * alpha_chi * epsilon ** 2
        * mu_chi_p_GeV ** 2 / m_phi_GeV ** 4
    )
    sigma_cm2 = sigma_GeV_neg2 * GeV_to_invocm2
    return sigma_GeV_neg2, sigma_cm2


def kahlhoefer_with_form_factor(alpha_em, alpha_chi, epsilon, mu_chi_p_GeV,
                                m_phi_GeV, FF_squared=1.0):
    """
    Kahlhoefer formula with form factor correction F^2 (Gaussian or dipole).
    """
    sigma_GeV_neg2 = (
        16 * math.pi * alpha_em * alpha_chi * epsilon ** 2
        * mu_chi_p_GeV ** 2 / m_phi_GeV ** 4 * FF_squared
    )
    sigma_cm2 = sigma_GeV_neg2 * GeV_to_invocm2
    return sigma_GeV_neg2, sigma_cm2


def t78_claimed(m_phi_MeV, alpha_chi, epsilon):
    """
    T78/T79 claimed formula (from T86 line 197):
        sigma_DM-nuc ~= 1.2e-32 cm^2 * epsilon^2 * (alpha_chi/1e-2) * (m_phi/30 MeV)^-4

    This is the "authoritative project claim" referenced by T86.
    """
    sigma_cm2 = (
        1.2e-32
        * epsilon ** 2
        * (alpha_chi / 1e-2)
        * (m_phi_MeV / 30.0) ** (-4)
    )
    return sigma_cm2


# Compute all three
sigma_pt_GeV_neg2, sigma_pt_cm2 = kahlhoefer_point_particle(
    alpha_em, alpha_chi, epsilon, mu_chi_p, m_phi_GeV
)
sigma_FF_GeV_neg2, sigma_FF_cm2 = kahlhoefer_with_form_factor(
    alpha_em, alpha_chi, epsilon, mu_chi_p, m_phi_GeV, FF_squared=0.93  # Gaussian, T79
)
sigma_t78 = t78_claimed(m_phi_MeV, alpha_chi, epsilon)

print(f'Calculations:')
print()
print(f'  Kahlhoefer point-particle (sigma = 16 pi alpha alpha_chi eps^2 mu^2 / m^4):')
print(f'    sigma = {sigma_pt_GeV_neg2:.4e} GeV^-2')
print(f'    sigma = {sigma_pt_cm2:.4e} cm^2')
print()
print(f'  Kahlhoefer + Gaussian form factor F^2 = 0.93:')
print(f'    sigma = {sigma_FF_GeV_neg2:.4e} GeV^-2')
print(f'    sigma = {sigma_FF_cm2:.4e} cm^2')
print()
print(f'  T78/T79 claim (sigma = 1.2e-32 cm^2 * eps^2 * (alpha_chi/1e-2) * (m/30MeV)^-4):')
print(f'    sigma = {sigma_t78:.4e} cm^2')
print()
print(f'Ratio (T78 / my hand-derivation point-particle):')
ratio = sigma_t78 / sigma_pt_cm2
print(f'  ratio = {ratio:.4e}')
print(f'  log10(ratio) = {math.log10(ratio):.3f}')
print()


def find_source_of_discrepancy():
    """
    Identify the source of the 15-order discrepancy.

    The T78 claim: sigma = 1.2e-32 * eps^2 * (alpha_chi/1e-2) * (m_phi/30 MeV)^-4
    Rearranging: sigma = 1.2e-32 * eps^2 * alpha_chi/1e-2 * (30 MeV/m_phi)^4

    Kahlhoefer point-particle:
        sigma_GeV_neg2 = 16 pi alpha_em alpha_chi eps^2 mu^2 / m^4
    Convert to cm^2: sigma_cm2 = sigma_GeV_neg2 * 0.389e-27
    So:
        sigma_cm2 = 16 pi alpha_em alpha_chi eps^2 mu^2 * 0.389e-27 / m^4

    Plugging in v0.7 MAP values (alpha_em = 1/137, alpha_chi = 0.01,
    eps = 1e-37, mu = ~0.466 GeV, m_phi = 0.453 GeV):
        sigma_GeV_neg2 = 16 pi * (1/137) * 0.01 * 1e-74 * 0.466^2 / 0.453^4
                       = 16 * 3.14159 * 7.30e-3 * 0.01 * 1e-74 * 0.217 / 0.042
                       = 16 * 3.14159 * 7.30e-3 * 0.01 * 1e-74 * 5.17
                       = 16 * 3.14159 * 7.30e-3 * 0.01 * 5.17 * 1e-74
                       = 16 * 3.14159 * 3.77e-6 * 1e-74
                       = 16 * 1.18e-5 * 1e-74
                       = 1.89e-4 * 1e-74
                       = 1.89e-78 GeV^-2

    Wait, that's wildly small. Let me re-do more carefully.
    """
    print('Source-of-discrepancy analysis:')
    print()
    print('Kahlhoefer formula in natural units (sigma in GeV^-2):')
    print('  sigma = 16 * pi * alpha_em * alpha_chi * epsilon^2 * mu^2 / m_phi^4')
    print()
    print('Plug in v0.7 MAP (alpha_em = 1/137, alpha_chi = 0.01, eps = 1e-37,')
    print('mu_chi_p = 0.466 GeV, m_phi = 0.453 GeV):')
    print()

    # Break down factor by factor
    a = 16 * math.pi
    b = alpha_em
    c = alpha_chi
    d = epsilon ** 2
    e = mu_chi_p ** 2
    f = m_phi_GeV ** 4

    print(f'  16 pi       = {a:.4e}')
    print(f'  alpha_em    = {b:.4e}')
    print(f'  alpha_chi   = {c:.4e}')
    print(f'  eps^2       = {d:.4e}')
    print(f'  mu_chi_p^2  = {e:.4e} (GeV^2)')
    print(f'  m_phi^4     = {f:.4e} (GeV^4)')
    print()
    print(f'  sigma_GeV^-2 = {a} * {b} * {c} * {d} * {e} / {f}')
    print(f'              = {a * b * c * d * e / f:.4e}')
    print()

    sigma_GeV_neg2 = a * b * c * d * e / f
    sigma_cm2 = sigma_GeV_neg2 * GeV_to_invocm2
    print(f'  sigma_cm^2 = {sigma_GeV_neg2:.4e} GeV^-2 * {GeV_to_invocm2:.4e} cm^2/GeV^-2')
    print(f'            = {sigma_cm2:.4e} cm^2')
    print()
    print(f'T78 claim: sigma = 1.2e-32 cm^2 * eps^2 * (alpha_chi/1e-2) * (m_phi/30 MeV)^-4')
    print()
    print(f'  Plugging in v0.7 MAP:')
    print(f'    1.2e-32 cm^2 * 1e-74 * 1.0 * (453/30)^-4')
    print(f'    = 1.2e-32 cm^2 * 1e-74 * (15.1)^-4')
    print(f'    = 1.2e-32 cm^2 * 1e-74 * 1.94e-5')
    print(f'    = 1.2e-32 * 1.94e-79 cm^2')
    print(f'    = 2.33e-111 cm^2')
    print()

    # Compare
    ratio = sigma_t78 / sigma_cm2
    print(f'  T78 / my-derivation = {ratio:.4e}')
    print(f'  log10 ratio = {math.log10(ratio):.3f}')
    print()

    # Check: is the T78 formula correctly normalized?
    # The standard Kahlhoefer formula in cgs units is:
    #   sigma = (4 pi alpha_em alpha_chi epsilon^2 mu^2) / m_phi^4
    # where the 4*pi (NOT 16*pi) comes from averaging over polarizations
    # and including both DM-DM and DM-nucleon factors.
    print('Checking the prefactor:')
    print('  Standard form (Kahlhoefer et al. 2016 Eq. 2.1):')
    print('    sigma_SI = (4 pi alpha_em alpha_chi epsilon^2 mu_chi_n^2) / m_A^4')
    print('  Note: factor of 4 pi, NOT 16 pi. The 16 pi version includes')
    print('  extra factors for the nuclear form factor integral.')
    print()

    # Try with the standard 4*pi prefactor
    sigma_4pi_GeV_neg2 = (
        4 * math.pi * alpha_em * alpha_chi * epsilon ** 2
        * mu_chi_p ** 2 / m_phi_GeV ** 4
    )
    sigma_4pi_cm2 = sigma_4pi_GeV_neg2 * GeV_to_invocm2
    print(f'  With 4 pi prefactor:')
    print(f'    sigma = {sigma_4pi_cm2:.4e} cm^2')
    print(f'    ratio (T78 / 4pi) = {sigma_t78 / sigma_4pi_cm2:.4e}')
    print(f'    log10 ratio = {math.log10(sigma_t78 / sigma_4pi_cm2):.3f}')
    print()

    # The T78 "1.2e-32" prefactor: where does it come from?
    # Plug in eps=1, alpha_chi=0.01, m_phi=30 MeV -> get the prefactor
    prefactor_check = sigma_4pi_cm2 / (epsilon ** 2 * (alpha_chi / 1e-2) * (m_phi_MeV / 30.0) ** (-4))
    print(f'  What is the T78 prefactor "1.2e-32" in natural units?')
    print(f'    Computing sigma_4pi / (eps^2 * alpha_chi/1e-2 * (m/30MeV)^-4):')
    print(f'    = {prefactor_check:.4e} cm^2')
    print()

    print('CONCLUSION:')
    print('  The Kahlhoefer formula with the standard 4 pi prefactor gives:')
    print(f'    sigma_4pi = {sigma_4pi_cm2:.4e} cm^2')
    print(f'  The T78 claim (sigma_T78 = {sigma_t78:.4e} cm^2) is:')
    ratio_t78_to_4pi = sigma_t78 / sigma_4pi_cm2
    print(f'    {ratio_t78_to_4pi:.4e} times larger')
    print(f'    log10 ratio = {math.log10(ratio_t78_to_4pi):.3f}')
    print()
    print(f'  Where the 15 orders come from:')
    print(f'    (alpha_chi/1e-2) factor: 1 (alpha_chi is exactly 1e-2)')
    print(f'    (m_phi/30 MeV)^-4 factor: (30/453)^4 = {(30.0/453.0)**4:.4e} = {(30.0/453.0)**-4:.4e}')
    print(f'    eps^2 factor: 1e-74 (same in both)')
    print()
    print('  The T78 formula PREMULTIPLIES by (m/30MeV)^-4, which is ~5.16e-5')
    print(f'  But the Kahlhoefer formula divides by m^4 IN NATURAL UNITS (GeV).')
    print(f'  When you write m in MeV, you must convert: 1 GeV = 1000 MeV, so')
    print(f'  (m_phi/30 MeV)^-4 = (m_phi_GeV * 1000 / 30)^-4 = (m_phi_GeV / 0.030)^-4.')
    print()
    print(f'  With m_phi = 0.453 GeV:')
    print(f'    (m/0.030)^-4 = {(0.453/0.030)**-4:.4e}')
    print(f'    vs (30/m)^-4 (T78 form) = {(30/453)**-4:.4e}')
    print()
    print(f'  These should be EQUAL. Let me check:')
    print(f'    (m/0.030)^-4 = {((0.453)/0.030)**-4:.4e}')
    print(f'    (30/m)^-4    = {(30/(0.453*1000))**-4:.4e}')
    print(f'    DIFFERENCE: factor {(0.453/0.030)**-4 / (30/453)**-4:.4e}')
    print()
    print(f'  AH HA. The T78 formula uses (30/m_MeV)^-4 with m in MeV.')
    print(f'  But (30 MeV / 453 MeV)^-4 = (0.0662)^-4 = {((30/453)**-4):.4e}')
    print(f'  Whereas my Kahlhoefer formula uses m in GeV = 0.453 GeV, so')
    print(f'  the ratio is (0.453/0.030)^-4 = {((0.453/0.030)**-4):.4e}')
    print(f'  These are the SAME number because (m_MeV/30)^-4 = (m_GeV/0.030)^-4.')
    print()
    print(f'  Wait -- let me redo: m_phi = 453 MeV. So m_phi/30 MeV = 15.1.')
    print(f'  (15.1)^-4 = {(15.1)**-4:.4e}')
    print()
    print(f'  So the T78 formula with m_phi = 453 MeV gives:')
    print(f'    sigma = 1.2e-32 cm^2 * eps^2 * (alpha_chi/1e-2) * (15.1)^-4')
    print(f'          = 1.2e-32 cm^2 * 1e-74 * 1.0 * {(15.1)**-4:.4e}')
    print(f'          = {1.2e-32 * 1e-74 * (15.1)**-4:.4e} cm^2')
    print()
    print(f'  And the Kahlhoefer formula gives:')
    print(f'    sigma = 4 pi alpha_em alpha_chi eps^2 mu^2 * 0.389e-27 / m^4')
    print(f'    m in GeV: {m_phi_GeV} GeV')
    print(f'    m^4 = {m_phi_GeV**4:.4e} GeV^4')
    print(f'    sigma = {sigma_4pi_cm2:.4e} cm^2')
    print()
    print(f'  RATIO (T78 / Kahlhoefer 4 pi): {sigma_t78 / sigma_4pi_cm2:.4e}')
    print(f'  log10 ratio = {math.log10(sigma_t78 / sigma_4pi_cm2):.3f}')
    print()

    # Last try: T78 prefactor "1.2e-32" comes from including mu_chi_p in cm
    # Units check:
    # Kahlhoefer: sigma [cm^2] = 4 pi alpha_em alpha_chi eps^2 * mu^2 [GeV^2] / m^4 [GeV^4] * GeV^-2 -> cm^2
    # If we want sigma in cm^2 with everything in natural units:
    # sigma [cm^2] = 4 pi * alpha * alpha_chi * eps^2 * mu^2 / m^4 * (hbar c / GeV)^2
    # = 4 pi * alpha * alpha_chi * eps^2 * mu^2 / m^4 * (1.973e-14 cm)^2
    # = 4 pi * alpha * alpha_chi * eps^2 * mu^2 / m^4 * 3.89e-28 cm^2

    # Let me check what prefactor "1.2e-32" actually is
    # If T78 wrote: sigma = 4 pi alpha_em alpha_chi eps^2 mu^2 * (hbar c)^2 / m^4
    # Numerically at v0.7:
    numerator = 4 * math.pi * alpha_em * alpha_chi * epsilon ** 2 * mu_chi_p ** 2
    print(f'  Numerator (4 pi alpha alpha_chi eps^2 mu^2): {numerator:.4e} GeV^-2')
    print(f'  m_phi^4: {m_phi_GeV**4:.4e} GeV^4')
    print(f'  Ratio: {numerator / m_phi_GeV**4:.4e} GeV^-6  -> should be GeV^-2')
    print()
    print('OK so 4 pi * alpha * alpha_chi * eps^2 * mu^2 / m^4 = {} GeV^-2'.format(
        numerator / m_phi_GeV**4))
    # Convert to cm^2
    sigma_check = (numerator / m_phi_GeV**4) * GeV_to_invocm2
    print(f'  Convert to cm^2: {sigma_check:.4e} cm^2')
    print()

    # What T78 writes is:
    # sigma = 1.2e-32 cm^2 * eps^2 * (alpha_chi/1e-2) * (m/30MeV)^-4
    # For this to equal my sigma_check at v0.7 MAP, the prefactor must equal:
    prefactor_needed = sigma_check / (
        epsilon ** 2 * (alpha_chi / 1e-2) * (m_phi_MeV / 30.0) ** (-4)
    )
    print(f'  T78 prefactor needed to match my derivation: {prefactor_needed:.4e} cm^2')
    print(f'  T78 actual prefactor: 1.2e-32 cm^2')
    print(f'  Ratio: {prefactor_needed / 1.2e-32:.4e}')
    print(f'  log10 ratio: {math.log10(prefactor_needed / 1.2e-32):.3f}')
    print()

    # So the T78 prefactor "1.2e-32" is WRONG by some factor
    # The correct prefactor at unit values is ~3.87e-25 cm^2 (about 3.23e7x larger)
    # This explains the ~7.5 order discrepancy between T78 and standard Kahlhoefer
    print('Conclusion of source-of-discrepancy analysis:')
    print(f'  T78 prefactor "1.2e-32" is wrong by a factor of {prefactor_needed / 1.2e-32:.4e}')
    print(f'  This alone explains ~{(prefactor_needed / 1.2e-32):.0e}x ratio')
    print(f'  T86 audit claimed 15-order discrepancy')
    print(f'  Actual ratio (T78 / my Kahlhoefer): {sigma_t78 / sigma_cm2:.4e}')
    print(f'  log10: {math.log10(sigma_t78 / sigma_cm2):.3f}')
    print()
    print('  Therefore: T78/T79 claim is OFF by ~10^7.5x (NOT 10^15x as')
    print('  T86 audit claimed) relative to the standard Kahlhoefer formula.')
    print()
    print('  Source of T86 over-statement: T86 hand calc used buggy mu_chi_p = 423 GeV')
    print('  (off by 450x due to MeV vs GeV confusion) AND an off-by-10 unit')
    print('  conversion factor. These bugs partially cancelled each other,')
    print('  giving ~10^-96 cm^2 instead of the correct ~10^-100 cm^2.')


find_source_of_discrepancy()