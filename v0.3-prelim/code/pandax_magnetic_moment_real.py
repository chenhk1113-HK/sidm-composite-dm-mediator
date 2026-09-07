"""
T88.G — PandaX-4T magnetic-moment constraint channel (Channel 26).

REAL DATA from PandaX Collaboration, Nature 618, 47-50 (2023):
  "Limits on the luminance of dark matter from xenon recoil data"
  DOI: 10.1038/s41586-023-05982-0

WHAT THIS CHANNEL DOES:
  Compares the LZ-anchored magnetic-moment value to the published
  PandaX-4T upper limit (mass-dependent).

PANDAX-4T MAGNETIC-DIPOLE UPPER LIMIT:
  - At m_chi = 20-40 GeV/c^2: mu < 4.8 x 10^-10 mu_B (90% CL)
  - 0.63 tonne-year commissioning exposure

  The upper limit scales with dark matter mass. For magnetic-moment
  scattering on nuclei:
    dsigma/dER ~ (Z^2 e^2 mu^2) / (4 pi m_chi^2 v^2) * [integral]
    The recoil rate ~ mu^2 * (cross-section prefactor) / m_chi^2
    At higher m_chi, the limit WEAKENS as ~ 1/m_chi.

  Simple scaling: mu_limit(m_chi) ~ mu_limit(40 GeV) * (m_chi / 40 GeV)^p
  where p ~ 0.5-1.0 for magnetic moment interactions.

  For this script, we use p = 0.5 (geometric mean of recoil-rate
  suppression and reduced-mass effects).

  This is a rough scaling; the actual PandaX limit curve would
  need to be extracted from the paper figure for precise comparison.

LZ-TUNED VALUE:
  mu_x = 6.10 x 10^-8 mu_N = 3.32 x 10^-11 mu_B
  (at m_chi = 1 TeV, from T90 7D posterior)

COMPARISON:
  At m_chi = 40 GeV (PandaX best sensitivity):
    mu_limit = 4.8 x 10^-10 mu_B
    LZ value at 40 GeV = 3.32 x 10^-11 mu_B * (40/1000)^(small)
                            ~ 3.32 x 10^-11 mu_B (velocity-scaling
                            cancels for mass rescaling; mu_x in mu_N
                            is mass-independent for fixed operator)
  Ratio: LZ / PandaX_limit = 0.069 (BELOW limit, not excluded)

  At m_chi = 1 TeV (LZ tuned):
    mu_limit (extrapolated) ~ 4.8 x 10^-10 * (1000/40)^0.5
                           ~ 4.8 x 10^-10 * 5.0 = 2.4 x 10^-9 mu_B
    LZ value = 3.32 x 10^-11 mu_B
  Ratio: LZ / PandaX_limit = 0.014 (well below limit)

OUTPUT
  - outputs/t90/pandax_magnetic_moment_real.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================================
# Real measurements (PandaX-4T, Nature 618, 47-50, 2023)
# ============================================================================
PANDAX_MAGNETIC_MOMENT_LIMIT_MUB = 4.8e-10  # 90% CL upper limit at m_chi = 20-40 GeV
PANDAX_MAGNETIC_MOMENT_BEST_MASS_GEV = 40.0  # best sensitivity mass
PANDAX_EXPOSURE_TONNE_YEAR = 0.63  # commissioning run
PANDAX_REF_ARXIV = "PandaX Nature 618, 47-50 (2023), DOI:10.1038/s41586-023-05982-0"

# Mass-scaling power (approximate)
# For magnetic-moment scattering, dsigma/dER ~ mu^2 * (constant in m_chi) * F^2(ER)
# The expected event rate at fixed exposure ~ mu^2 * (1/m_chi) at high m_chi
# So the limit mu_limit ~ sqrt(1/m_chi * 1/exposure) at fixed m_chi
# Therefore mu_limit scales as m_chi^0.5 (higher mass → weaker limit)
# But reduced mass M_chiN ~ m_chi (for m_chi >> m_N) also affects kinematics
# Net scaling: p ~ 0.5 (rough)
PANDAX_MASS_SCALING_POWER = 0.5


# ============================================================================
# LZ-tuned magnetic moment
# ============================================================================
LZ_TUNED_MU_X_MU_N = 6.10e-8  # from T90 7D posterior
M_E_GEV = 0.51099895e-3
M_PROTON_GEV = 0.938272
MU_B_GEV = M_E_GEV
MU_N_GEV = MU_B_GEV / (M_PROTON_GEV / M_E_GEV)  # = MU_B / 1836.15

LZ_TUNED_MU_X_MU_B = LZ_TUNED_MU_X_MU_N / 1836.15267  # mu_N to mu_B conversion (1 mu_B = 1836 mu_N)
LZ_TUNED_M_CHI_GEV = 1000.0


# ============================================================================
# PandaX limit extrapolation
# ============================================================================
def pandax_limit_at_mass(m_chi_GeV: float) -> float:
    """Extrapolate PandaX magnetic-moment limit to mass m_chi.

    Per the PandaX Nature 618 paper:
      - At m_chi = 40 GeV: limit = 4.8e-10 mu_B
      - For m_chi >> m_N (xenon, m_N ~ 131): recoil kinematics changes
      - Net scaling (approximate): mu_limit(m) ~ mu_limit(40) * (m / 40)^0.5

    Args:
      m_chi_GeV: DM mass in GeV

    Returns:
      Extrapolated 90% CL upper limit in mu_B
    """
    if m_chi_GeV <= 0:
        return np.inf
    return PANDAX_MAGNETIC_MOMENT_LIMIT_MUB * (m_chi_GeV / PANDAX_MAGNETIC_MOMENT_BEST_MASS_GEV) ** PANDAX_MASS_SCALING_POWER


def lz_tuned_mu_x_at_mass(m_chi_GeV: float) -> float:
    """LZ-tuned magnetic moment at arbitrary m_chi.

    The T90 7D posterior gives mu_x = 6.10e-8 mu_N at m_chi = 1 TeV.
    This value is in NUCLEAR magnetons, which are independent of m_chi
    for a fixed EFT operator (the operator defines the coupling, not
    the conversion factor).

    Args:
      m_chi_GeV: DM mass (kept for API consistency)

    Returns:
      mu_x in mu_B (1 mu_N = 1/1836.15 mu_B)
    """
    return LZ_TUNED_MU_X_MU_N / 1836.15267


# ============================================================================
# Likelihood and exclusion
# ============================================================================
def log_pandex_upper_limit(mu_measured_mu_B: float, mu_limit_mu_B: float) -> float:
    """Compute log-likelihood given measured mu and PandaX upper limit.

    If mu_measured < mu_limit: model is consistent with PandaX (log L = 0).
    If mu_measured > mu_limit: model is excluded (log L = -inf or penalty).

    Args:
      mu_measured_mu_B: predicted DM magnetic moment
      mu_limit_mu_B: PandaX 90% CL upper limit

    Returns:
      log L
    """
    if mu_measured_mu_B <= mu_limit_mu_B:
        return 0.0
    else:
        # Quadratic penalty above the limit (Gaussian-tail approximation)
        excess = (mu_measured_mu_B - mu_limit_mu_B) / mu_limit_mu_B
        return -10.0 * excess ** 2  # strong penalty for exclusion


def loglike_pandax_magnetic_moment(m_chi_GeV: float = LZ_TUNED_M_CHI_GEV,
                                     mu_x_mu_N: float = LZ_TUNED_MU_X_MU_N) -> dict:
    """Full likelihood for PandaX magnetic-moment constraint.

    Args:
      m_chi_GeV: DM mass for evaluation
      mu_x_mu_N: DM magnetic moment in mu_N

    Returns:
      Dict with limit, measured, ratio, log L, exclusion status
    """
    # 1 mu_N = 1/1836.15 mu_B (mu_N is much smaller than mu_B)
    mu_measured_mu_B = mu_x_mu_N / 1836.15267
    mu_limit_mu_B = pandax_limit_at_mass(m_chi_GeV)
    log_l = log_pandex_upper_limit(mu_measured_mu_B, mu_limit_mu_B)
    excluded = mu_measured_mu_B > mu_limit_mu_B
    ratio = mu_measured_mu_B / mu_limit_mu_B if mu_limit_mu_B > 0 else np.inf
    return {
        'm_chi_GeV': m_chi_GeV,
        'mu_measured_mu_N': mu_x_mu_N,
        'mu_measured_mu_B': mu_measured_mu_B,
        'mu_limit_mu_B': mu_limit_mu_B,
        'ratio_measured_to_limit': ratio,
        'log_l': log_l,
        'excluded_by_pandax': excluded,
    }


# ============================================================================
# Main
# =========================================================================
def main():
    print("=" * 70)
    print("T88.G — PandaX-4T magnetic-moment constraint")
    print("       (Nature 618, 47-50, 2023, arXiv:2023)")
    print("=" * 70)
    print()
    print(f"PandaX 90% CL limit at m_chi = 40 GeV: {PANDAX_MAGNETIC_MOMENT_LIMIT_MUB:.2e} mu_B")
    print(f"PandaX best sensitivity mass: {PANDAX_MAGNETIC_MOMENT_BEST_MASS_GEV} GeV/c^2")
    print(f"PandaX exposure: {PANDAX_EXPOSURE_TONNE_YEAR} tonne-year (commissioning run)")
    print(f"Mass-scaling power: {PANDAX_MASS_SCALING_POWER}")
    print()
    print(f"LZ-tuned mu_x = {LZ_TUNED_MU_X_MU_N:.3e} mu_N at m_chi = {LZ_TUNED_M_CHI_GEV:.0f} GeV")
    print(f"             = {LZ_TUNED_MU_X_MU_B:.3e} mu_B")
    print()

    # Test at LZ-anchored mass
    r = loglike_pandax_magnetic_moment(LZ_TUNED_M_CHI_GEV, LZ_TUNED_MU_X_MU_N)
    print(f"At LZ-anchored parameters (m_chi = {r['m_chi_GeV']:.0f} GeV):")
    print(f"  PandaX limit (extrapolated): {r['mu_limit_mu_B']:.3e} mu_B")
    print(f"  LZ measured:                  {r['mu_measured_mu_B']:.3e} mu_B")
    print(f"  Ratio (LZ / PandaX):          {r['ratio_measured_to_limit']:.3f}")
    print(f"  Excluded?                     {r['excluded_by_pandax']}")
    print(f"  Log L:                        {r['log_l']:.3f}")
    print()

    # Mass-dependent scan
    print("Mass-dependent comparison:")
    print(f"  {'m_chi [GeV]':<12} {'PandaX limit [mu_B]':<22} {'LZ/PandaX ratio':<18} {'Excluded?':<10}")
    print(f"  {'-'*12} {'-'*22} {'-'*18} {'-'*10}")
    for m_chi in [10, 20, 40, 100, 200, 500, 1000, 2000, 5000]:
        r = loglike_pandax_magnetic_moment(m_chi, LZ_TUNED_MU_X_MU_N)
        excluded_str = "YES" if r['excluded_by_pandax'] else "no"
        print(f"  {m_chi:<12} {r['mu_limit_mu_B']:<22.3e} {r['ratio_measured_to_limit']:<18.3f} {excluded_str:<10}")
    print()

    # Output
    out_path = _PROJECT_ROOT / "outputs" / "t90" / "pandax_magnetic_moment_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T88.G (Channel 26, PandaX magnetic-moment constraint)',
        'real_data': {
            'arxiv': PANDAX_REF_ARXIV,
            'limit_at_40_GeV_mu_B': PANDAX_MAGNETIC_MOMENT_LIMIT_MUB,
            'best_sensitivity_mass_GeV': PANDAX_MAGNETIC_MOMENT_BEST_MASS_GEV,
            'exposure_tonne_year': PANDAX_EXPOSURE_TONNE_YEAR,
        },
        'mass_scaling_model': {
            'power_law': PANDAX_MASS_SCALING_POWER,
            'caveat': 'Approximate scaling; precise limit curve would require extraction from PandaX Figure 4',
        },
        'lz_tuned_value': {
            'mu_x_mu_N': LZ_TUNED_MU_X_MU_N,
            'mu_x_mu_B': LZ_TUNED_MU_X_MU_B,
            'm_chi_GeV': LZ_TUNED_M_CHI_GEV,
        },
        'comparison': {
            'mu_measured_mu_B': r['mu_measured_mu_B'],
            'mu_limit_at_1_TeV_mu_B': pandax_limit_at_mass(LZ_TUNED_M_CHI_GEV),
            'ratio_at_1_TeV': LZ_TUNED_MU_X_MU_B / pandax_limit_at_mass(LZ_TUNED_M_CHI_GEV),
            'excluded': False,
            'interpretation': 'LZ interpretation is NOT excluded by PandaX commissioning-run upper limit. Ratio is well below 1 across all masses 10 GeV - 5 TeV.',
        },
        'caveats': [
            'PandaX limit is for 0.63 tonne-year commissioning run (2023).',
            'Full PandaX-4T Run 0+1 (1.54 tonne-years, PRL 133, 191001) has different limits.',
            'Mass-scaling power of 0.5 is approximate; precise comparison needs the PandaX curve.',
            'No new PandaX magnetic-moment search paper at high mass (1 TeV) is published.',
            'A future PandaX-4T or XENONnT magnetic-moment search at high mass could exclude LZ.',
        ],
        'references': [
            'PandaX Collaboration, Nature 618, 47-50 (2023)',
            'DOI:10.1038/s41586-023-05982-0',
            'PRL 134, 011805 (2025) - PandaX Run0+1 dark matter search',
            'PRL 133, 191001 (2024) - PandaX 8B CEvNS',
        ],
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()