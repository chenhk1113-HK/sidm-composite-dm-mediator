"""
T90 Path C.4.5 (v15) — Indirect-signal predictions.

STATUS: DRAFT STUB. Path 4 of the 'proceed 1,2 3 4 6 7' plan.

PURPOSE
=======
Compute the indirect-detection signatures of the
LZ-anchored magnetic-moment DM model:
  - Gamma-ray annihilation spectrum (FERMI, HESS, CTA)
  - Neutrino flux (IceCube, Super-K, Hyper-K)
  - Cosmic-ray antiproton/positron flux (PAMELA, AMS-02)

For each channel, compute the predicted flux at the
LZ-tuned parameters (m_chi = 1 TeV, mu_x = 6.10e-8 mu_N).

WHY THIS MATTERS
================
Direct-detection limits (PandaX-4T, DARWIN) test the
DM-nucleon coupling. Indirect-detection limits test the
DM-DM coupling (annihilation cross-section). A model that
survives direct-detection limits can still be excluded by
indirect-detection limits if the annihilation cross-section
is large.

KEY OBSERVATION
===============
Magnetic-moment DM has s-wave annihilation suppressed
(Goldstone + chiral). The leading annihilation channel is
into photons via one-loop diagrams. This is qualitatively
different from WIMP-annihilation-via-weak-currents.

REFERENCES TO READ BEFORE COMPLETING
=====================================
- Hisano, Matsumoto, Nojiri (2001) — unitarity bounds on
  magnetic-moment DM
- Ibe, Murayama, Yanagida (2012) — wide-velocity-range
  magnetic-moment DM
- Leane (2020) — dark matter indirect detection review

STUB STATUS: This script is a placeholder with the
right structure but NOT a complete implementation.
The TODO markers below need physics implementation.

OUTPUT (when complete):
  - outputs/t90/indirect_signals.json
  - Predicted fluxes per channel, compared to detector limits

CONSTRAINTS:
  - No new dependencies (rule 17/24)
  - Branch-local on wip/tier3-magnetic-moment-LZ
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))


def annihilation_cross_section_to_gammas(m_chi_GeV: float, mu_x_mu_N: float) -> float:
    """Compute the annihilation cross-section to 2 photons for
    magnetic-moment DM.

    The leading diagram is a box diagram with the magnetic
    dipole coupling. Per Hisano+ 2001, the cross-section is:

    sigma_gamma_gamma * v ~ (mu_x^4 * m_chi^2) / (4*pi) * (alpha_em)^2 * ...

    TODO: implement the actual formula with the correct
    loop factors and coupling constants.

    Args:
      m_chi_GeV: DM mass in GeV
      mu_x_mu_N: magnetic dipole in nuclear magnetons

    Returns:
      Cross-section * v in cm^3/s
    """
    # TODO: implement
    raise NotImplementedError(
        "annihilation cross-section to gammas not yet implemented; "
        "see Hisano+ 2001 for the loop-level calculation"
    )


def gamma_ray_flux_at_earth(
    m_chi_GeV: float,
    sigma_v: float,
    j_factor: float,
) -> float:
    """Compute the predicted gamma-ray flux at Earth from DM
    annihilation in the Galactic Center.

    Args:
      m_chi_GeV: DM mass
      sigma_v: annihilation cross-section * v (cm^3/s)
      j_factor: line-of-sight integral of rho^2 (GeV^2/cm^5)

    Returns:
      Photon flux at Earth (photons/cm^2/s)
    """
    # Flux = (sigma_v / (4*pi * m_chi^2)) * j_factor
    return (sigma_v / (4 * np.pi * m_chi_GeV**2)) * j_factor


def neutrino_flux_at_icecube(
    m_chi_GeV: float,
    sigma_v: float,
    j_factor_sun: float,
) -> float:
    """Compute the predicted neutrino flux from DM captured
    in the Sun.

    TODO: implement the capture+annihilation equilibrium
    calculation. The Sun's gravitational capture rate for
    magnetic-moment DM is non-trivially different from
    SI/SID capture rates.

    Returns:
      Neutrino flux at IceCube (1/GeV/cm^2/s)
    """
    raise NotImplementedError(
        "Solar capture + annihilation neutrino flux not yet "
        "implemented; needs Ibe+ 2012 capture formalism"
    )


def main():
    print("=" * 70)
    print("T90 Path C.4.5 (v15) — Indirect signals (DRAFT STUB)")
    print("=" * 70)
    print()
    print("STATUS: This is a draft stub. The structure is correct but")
    print("the physics calculations are TODO. See the docstring for")
    print("references to read before completing.")
    print()

    m_chi = 1000.0  # GeV
    mu_x = 6.10e-8  # mu_N (LZ-tuned)

    print(f"LZ-tuned parameters: m_chi = {m_chi} GeV, mu_x = {mu_x:.3e} mu_N")
    print()

    # Try the gamma-ray flux calculation (will raise NotImplementedError)
    try:
        sigma_v = annihilation_cross_section_to_gammas(m_chi, mu_x)
        j_factor_gc = 1e-23  # GeV^2/cm^5, conservative for GC
        flux_gc = gamma_ray_flux_at_earth(m_chi, sigma_v, j_factor_gc)
        print(f"Gamma-ray flux at GC: {flux_gc:.3e} photons/cm^2/s")
    except NotImplementedError as e:
        print(f"Gamma-ray flux: NOT IMPLEMENTED")
        print(f"  ({e})")
    print()

    print("Output (when complete):")
    print("  outputs/t90/indirect_signals.json")
    print()
    print("To complete this path:")
    print("  1. Read Hisano+ 2001 (arXiv:hep-ph/0012200)")
    print("  2. Implement annihilation_cross_section_to_gammas")
    print("  3. Implement neutrino_flux_at_icecube (uses Ibe+ 2012)")
    print("  4. Compare to FERMI, HESS, CTA, IceCube limits")
    print("  5. Write tests + commit")


if __name__ == '__main__':
    main()
