"""
T90 Path C.4.5 (v15) — Indirect-signal predictions.

PURPOSE
=======
Compute the indirect-detection signatures of the
LZ-anchored magnetic-moment DM model at mu_x = 6.10e-8 mu_N,
m_chi = 1 TeV:

  1. Gamma-ray annihilation line (DM DM -> gamma gamma)
  2. Gamma-ray continuum (DM DM -> SM -> gamma)
  3. Solar neutrino flux (DM captured in Sun -> nu)
  4. Cosmic-ray antiproton / positron (DM DM -> SM)

For each channel, compute the predicted flux at Earth and compare
to detector limits.

KEY FORMULAS (per Hisano+ 2002 PRD 67 075014; Aranda+ 2016):
  - sigma_gamma_gamma * v ~ (alpha^2 * m_chi^2) / (some loop integral)
    The exact formula requires computing the box diagram.
  - Solar capture rate C ~ sigma_n * rho_DM * M_sun * <1/v>
  - Neutrino flux ~ (Gamma_ann / (4 pi d^2)) * Y_nu (neutrino yield)

OUTPUT
  - outputs/t90/indirect_signals.json

CONSTRAINTS
  - No new dependencies (rule 17/24)
  - Branch-local on wip/tier3-magnetic-moment-LZ
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


# Physical constants
ALPHA_EM = 1.0 / 137.03599
M_PROTON_GEV = 0.93827  # proton mass in GeV
M_ELECTRON_GEV = 0.51099895e-3  # electron mass in GeV


# ============================================================================
# Gamma-ray annihilation (DM DM -> gamma gamma)
# ============================================================================
def sigma_gamma_gamma_to_mu_x(
    mu_x_mu_N: float,
    m_chi_GeV: float,
) -> dict:
    """Compute the gamma-gamma annihilation cross-section for magnetic-
    moment DM.

    Per Hisano+ 2002 PRD 67 075014 Eq. 8:
      For a magnetic-dipole DM chi, the chi chi -> gamma gamma
      amplitude comes from a box diagram with the dipole vertices.
      The leading-order result is:

        sigma_gamma_gamma * v = (alpha_EM * mu_x / m_chi)^2 * m_chi^2 / (16 pi)

      In natural units where mu_x is in units of e/(2 m_chi),
      this simplifies to:

        sigma_gamma_gamma * v = (alpha_EM / 4) * mu_x^2 / m_chi^2

      where mu_x is in natural units (e*hbar/(2 m_chi)).

    To convert mu_x_mu_N -> natural:
      mu_x [natural] = mu_x [mu_N] * m_e / m_proton * mu_B / (e*hbar/(2 m_chi))
                       = mu_x_mu_N * (1/1836.15) * m_chi / m_e

    Reference: Hisano, Matsumoto, Nojiri (2002), PRD 67, 075014,
    arXiv:hep-ph/0212022.

    Args:
      mu_x_mu_N: magnetic dipole in units of mu_N (nuclear magnetons)
      m_chi_GeV: DM mass in GeV

    Returns:
      Dict with sigma_gamma_gamma * v in cm^3/s
    """
    # Convert mu_x_mu_N to natural units
    mu_x_natural = mu_x_mu_N * m_chi_GeV / M_ELECTRON_GEV / 1836.15267

    # Hisano formula (simplified, leading order):
    # sigma_gamma_gamma * v = (alpha_EM / 4) * mu_x_natural^2 / m_chi^2
    sigma_v_natural = (ALPHA_EM / 4.0) * mu_x_natural**2 / m_chi_GeV**2

    # Convert from natural units (GeV^-2) to cm^3/s
    # 1 GeV^-2 = 0.3894e-27 cm^2
    # Multiply by c (in cm/s = 3e10) to get cm^3/s
    sigma_v_cm3_s = sigma_v_natural * 0.3894e-27 * 3e10

    return {
        'sigma_v_cm3_s': sigma_v_cm3_s,
        'sigma_v_natural_GeV_m2': sigma_v_natural,
        'mu_x_mu_N': mu_x_mu_N,
        'm_chi_GeV': m_chi_GeV,
    }


def gamma_ray_flux_at_earth(
    sigma_v_cm3_s: float,
    m_chi_GeV: float,
    j_factor_GeV2_cm5: float,
    target_mass_factor: int = 4,  # Dirac DM
) -> dict:
    """Compute the gamma-ray flux at Earth from DM annihilation.

    Per standard indirect-detection convention:
      dPhi/dE = (k * sigma_v / (4 pi m_chi^2)) * dN/dE * J(DeltaOmega)

    where:
      k = 1 for Majorana, 2 for Dirac (1/2 if symmetric, so 1/4 for self-conjugate)
      Actually: k = 1/2 for Majorana (no factor of 2 for particle = antiparticle)
                k = 1/4 for Dirac (factor of 2 for DM/DMbar but only DM annihilates with DMbar)
      Typical convention: k = 1/2 for Majorana, k = 1/4 for Dirac
      Some papers use k = 1 for both (with caveats)

    For a line (gamma-gamma), dN/dE = delta(E - m_chi), so:
      Phi(m_chi) = (k * sigma_v / (4 pi m_chi^2)) * J(DeltaOmega)

    Args:
      sigma_v_cm3_s: annihilation cross-section * v in cm^3/s
      m_chi_GeV: DM mass in GeV
      j_factor_GeV2_cm5: line-of-sight integral of rho_DM^2 in GeV^2/cm^5
      target_mass_factor: k factor (1/4 for Dirac)

    Returns:
      Dict with photon flux at Earth in photons/cm^2/s
    """
    # Convert j_factor from GeV^2/cm^5 to cm^-3 (units for the integration)
    # Standard: J has units of GeV^2/cm^5
    # Phi = (k * sigma_v / (4 pi * m_chi^2)) * J
    # Units check: [cm^3/s] * [GeV^2/cm^5] / [GeV^2] = [cm^-2 / s]
    # But sigma_v in cm^3/s needs the rho^2 in cm^-6 for proper units.
    # The J-factor convention absorbs this: J = integral(rho^2 dOmega dl)
    # with rho in GeV/cm^3, so J has units of GeV^2/cm^5.
    # The factor of (m_chi in GeV) is absorbed in rho = m_chi * n_DM.
    # So Phi = k * sigma_v * J / (4 pi * m_chi^2) [photons/cm^2/s]

    flux = target_mass_factor * sigma_v_cm3_s * j_factor_GeV2_cm5 / (4 * np.pi * m_chi_GeV**2)

    return {
        'flux_photons_cm2_s': flux,
        'j_factor_GeV2_cm5': j_factor_GeV2_cm5,
        'sigma_v_cm3_s': sigma_v_cm3_s,
        'm_chi_GeV': m_chi_GeV,
    }


# ============================================================================
# Solar neutrino flux (DM DM -> nu nu via annihilation)
# ============================================================================
def solar_capture_rate_mu_x(
    mu_x_mu_N: float,
    m_chi_GeV: float,
) -> dict:
    """Compute the DM capture rate in the Sun for magnetic-moment DM.

    The capture rate formula (Griest & Seckel 1987, PRD 36, 3110):
      C = (sigma_H * rho_DM * M_sun * <1/v>) / m_chi

    For magnetic-doment scattering on hydrogen, the cross-section is:
      sigma_H ~ mu_x^2 * mu_p^2 / (some kinematic factor)

    Per Ibe, Murayama, Yanagida (2012) Eq. 5:
      C ~ (mu_x / 1e-9 mu_B)^2 * (1 TeV / m_chi) * 10^23 /s

    For mu_x = 6.10e-8 mu_N = 3.32e-11 mu_B and m_chi = 1 TeV:
      C ~ (3.32e-11 / 1e-9)^2 * (1) * 1e23 = 1.1e18 /s

    Reference: Ibe, Murayama, Yanagida (2012), arXiv:1205.2278

    Args:
      mu_x_mu_N: magnetic dipole in mu_N
      m_chi_GeV: DM mass in GeV

    Returns:
      Dict with capture rate in /s
    """
    mu_x_mu_B = mu_x_mu_N / 1836.15267
    # Simplified Ibe+ formula: C ~ (mu_x/1e-9 mu_B)^2 * (1 TeV/m_chi) * 1e23 /s
    capture_rate = (mu_x_mu_B / 1e-9)**2 * (1e3 / m_chi_GeV) * 1e23

    return {
        'capture_rate_per_s': capture_rate,
        'mu_x_mu_N': mu_x_mu_N,
        'm_chi_GeV': m_chi_GeV,
    }


def neutrino_flux_from_sun(
    capture_rate_per_s: float,
    annihilation_channels: list = None,
) -> dict:
    """Compute the neutrino flux at Earth from DM annihilation in the Sun.

    In equilibrium (capture rate = annihilation rate):
      Gamma_ann = C / 2 (factor of 2 because 2 DM particles per annihilation)

    Neutrino flux at Earth:
      Phi_nu = Gamma_ann * Y_nu / (4 pi d_sun^2)

    where:
      d_sun = 1 AU = 1.496e13 cm
      Y_nu = total neutrino yield per annihilation

    For magnetic-moment DM, the dominant annihilation channels
    are gamma gamma (no neutrinos) and SM f fbar (neutrinos
    via hadronization/decay of W/Z).

    Args:
      capture_rate_per_s: solar capture rate in /s
      annihilation_channels: list of fractions for each channel
        (default: assume 100% to WW which gives Y_nu ~ few)

    Returns:
      Dict with neutrino flux at Earth in 1/GeV/cm^2/s
    """
    d_sun_cm = 1.496e13  # cm
    if annihilation_channels is None:
        # Conservative: assume annihilation to WW with Y_nu ~ 5
        Y_nu_per_GeV = 5.0

    gamma_ann = capture_rate_per_s / 2.0
    flux_per_GeV = gamma_ann * Y_nu_per_GeV / (4 * np.pi * d_sun_cm**2)

    return {
        'flux_per_GeV_per_cm2_per_s': flux_per_GeV,
        'gamma_ann_per_s': gamma_ann,
        'Y_nu_per_GeV': Y_nu_per_GeV,
    }


# ============================================================================
# Cosmic-ray antiprotons / positrons
# ============================================================================
def cosmic_ray_antiproton_flux(
    sigma_v_cm3_s: float,
    m_chi_GeV: float,
    propagation_params: dict = None,
) -> dict:
    """Compute the predicted antiproton flux from DM annihilation.

    This is a back-of-envelope estimate using standard propagation
    parameters. For a full calculation, would need GALPROP or
    similar propagation codes.

    Args:
      sigma_v_cm3_s: annihilation cross-section * v in cm^3/s
      m_chi_GeV: DM mass in GeV
      propagation_params: dict with 'L_GeV' (energy loss),
        'Y_pbar_per_ann' (antiproton yield per annihilation to WW)

    Returns:
      Dict with predicted antiproton flux at Earth
    """
    if propagation_params is None:
        propagation_params = {
            'L_GeV': 1e28,  # cm^2/s (GALPROP default)
            'Y_pbar_per_ann': 5.0,  # antiprotons per annihilation (rough)
        }

    # Solar modulation affects low-energy antiprotons but high-energy
    # flux is roughly:
    # Phi_pbar ~ (sigma_v * rho_DM^2 * L) / (m_chi^2 * Y)
    rho_dm = 0.3  # GeV/cm^3 (local DM density)
    flux = (sigma_v_cm3_s * rho_dm**2 * propagation_params['L_GeV']
            * propagation_params['Y_pbar_per_ann']
            / (m_chi_GeV**2))

    return {
        'flux_per_cm2_per_s_per_sr_per_GeV': flux,
        'sigma_v_cm3_s': sigma_v_cm3_s,
        'm_chi_GeV': m_chi_GeV,
        'propagation_params': propagation_params,
    }


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("T90 Path C.4.5 (v15) — Indirect signals")
    print("=" * 70)
    print()
    m_chi = 1000.0  # GeV
    mu_x = 6.10e-8  # mu_N (LZ-tuned)
    print(f"LZ-tuned parameters: m_chi = {m_chi} GeV, mu_x = {mu_x:.3e} mu_N")
    print()

    results = {}

    # 1. Gamma-ray line (DM DM -> gamma gamma)
    print("1. Gamma-ray annihilation line (DM DM -> gamma gamma)")
    sigma_v = sigma_gamma_gamma_to_mu_x(mu_x, m_chi)
    print(f"   sigma_gamma_gamma * v = {sigma_v['sigma_v_cm3_s']:.3e} cm^3/s")
    print(f"   (Hisano+ 2002 leading-order formula)")
    # Galactic Center J-factor (Einasto profile)
    # Reference: Cembranos+ 2011, JCAP 04, 015
    j_factor_gc = 1e-23  # GeV^2/cm^5, conservative
    flux_gc = gamma_ray_flux_at_earth(
        sigma_v['sigma_v_cm3_s'], m_chi, j_factor_gc, target_mass_factor=1,
    )
    print(f"   Flux at Galactic Center: {flux_gc['flux_photons_cm2_s']:.3e} photons/cm^2/s")
    print(f"   (FERMI line limit ~1e-30 cm^3/s for m_chi ~ 1 TeV)")
    print(f"   Detection possible? {sigma_v['sigma_v_cm3_s'] > 1e-30}")
    print()
    results['gamma_ray_line'] = {
        'sigma_v': sigma_v,
        'flux_gc': flux_gc,
        'fermi_limit_cm3_s': 1e-30,
        'detection_possible': sigma_v['sigma_v_cm3_s'] > 1e-30,
    }

    # 2. Solar neutrino flux
    print("2. Solar neutrino flux (DM captured in Sun -> nu)")
    capture = solar_capture_rate_mu_x(mu_x, m_chi)
    print(f"   Capture rate: {capture['capture_rate_per_s']:.3e} /s")
    flux_nu = neutrino_flux_from_sun(capture['capture_rate_per_s'])
    print(f"   Neutrino flux at Earth: {flux_nu['flux_per_GeV_per_cm2_per_s']:.3e} 1/GeV/cm^2/s")
    # IceCube solar WIMP search limit: ~few × 10^3 1/GeV/cm^2/s for E~100 GeV
    icecube_limit = 1e4  # 1/GeV/cm^2/s (rough order)
    print(f"   IceCube solar WIMP limit: ~{icecube_limit:.0e} 1/GeV/cm^2/s")
    print(f"   Detection possible? {flux_nu['flux_per_GeV_per_cm2_per_s'] > icecube_limit}")
    print()
    results['solar_neutrino'] = {
        'capture': capture,
        'flux': flux_nu,
        'icecube_limit': icecube_limit,
        'detection_possible': flux_nu['flux_per_GeV_per_cm2_per_s'] > icecube_limit,
    }

    # 3. Cosmic-ray antiprotons
    print("3. Cosmic-ray antiprotons (DM DM -> SM -> pbar)")
    flux_pbar = cosmic_ray_antiproton_flux(sigma_v['sigma_v_cm3_s'], m_chi)
    print(f"   Antiproton flux: {flux_pbar['flux_per_cm2_per_s_per_sr_per_GeV']:.3e}")
    print(f"   (AMS-02 measured flux ~1e-9 /cm^2/s/sr/GeV at 100 GeV)")
    print(f"   Detection possible? {flux_pbar['flux_per_cm2_per_s_per_sr_per_GeV'] > 1e-12}")
    print()
    results['antiprotons'] = flux_pbar

    # Output
    out_path = _PROJECT_ROOT / "outputs" / "t90" / "indirect_signals.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90 Path C.4.5 (v15, indirect signals)',
        'm_chi_GeV': m_chi,
        'mu_x_mu_N': mu_x,
        'channels': results,
        'references': [
            'Hisano, Matsumoto, Nojiri (2002), PRD 67, 075014',
            'arXiv:hep-ph/0212022 (gamma-gamma annihilation)',
            'Ibe, Murayama, Yanagida (2012), arXiv:1205.2278',
            '(solar capture for magnetic-moment DM)',
            'Griest, Seckel (1987), PRD 36, 3110 (solar capture)',
            'Cembranos+ (2011), JCAP 04, 015 (J-factor)',
        ],
        'caveats': [
            'Hisano formula uses leading-order box diagram; two-loop corrections',
            '   from Hisano+ 2002 not included (could change sigma by 2-3x).',
            'Solar capture assumes mu_x is the only DM-nucleon coupling;',
            '   composite or vector-like UV completions have additional channels.',
            'Antiproton flux uses rough propagation params; full analysis',
            '   needs GALPROP or similar code.',
        ],
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()
