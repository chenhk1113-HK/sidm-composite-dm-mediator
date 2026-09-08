"""
T90 Path C.4.6 (v16) — UV completion of the magnetic-moment operator.

PURPOSE
=======
Identify UV-complete models that generate the magnetic-moment
operator at the LZ-tuned coupling (mu_x = 6.10e-8 mu_N at
m_chi = 1 TeV), then compute the parameter space of each model
that maps to LZ data.

CANDIDATE UV COMPLETIONS
========================
1. **Composite DM (Aranda+ 2016)** — DM is a composite neutral
   baryon of a new SU(3)_D dark color. Magnetic moment arises
   from valence constituents with electric charge.
   Reference: arXiv:1511.02805 (JCAP 03, 2016, 034)

2. **Vector-like fermion loop (Hisano+ 2002 / Agrawal+ 2022)** —
   DM couples to a heavy vector-like fermion psi via a Yukawa;
   loop generates magnetic moment.
   Reference: Hisano unitarity bound, arXiv:hep-ph/0212022
              (PRD 67, 075014)

3. **Dark photon mediation (Fabbrichesi+ 2020)** — DM has
   millicharge under U(1)_dark. Kinetic mixing with SM photon
   generates effective magnetic moment at one-loop.
   Reference: arXiv:2005.01515 (Dark Photon review)

METHOD
======
For each model, compute the magnetic-moment coupling as a
function of the model's free parameters (constituent masses,
mixing angles, etc.). Then find the parameter point that
gives mu_x = 6.10e-8 mu_N at m_chi = 1 TeV.

Add constraints:
  - Unitarity bound (Aranda+ 2016): mu_x * m_chi < 20 m_e
  - Perturbative: mu_x < e / m_chi (i.e. < 2e-3 / m_chi in GeV)

OUTPUT
  - outputs/t90/uv_completion.json
  - Per-model parameter point that reproduces LZ data
  - Cross-check against unitarity + perturbativity bounds

CONSTRAINTS
  - No new dependencies (rule 17/24)
  - Branch-local on wip/tier3-magnetic-moment-LZ
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]


# Physical constants (SI / natural units)
M_E_GEV = 0.51099895e-3  # electron mass in GeV
MU_B_GEV = M_E_GEV        # Bohr magneton in GeV (magnetic moment unit for e)
MU_N_GEV = M_E_GEV / 1836.15267  # nuclear magneton in GeV
ALPHA_EM = 1.0 / 137.03599


# ============================================================================
# Model 1: Composite DM (Aranda+ 2016)
# ============================================================================
def composite_dm_mu_x(
    m_chi_GeV: float,
    m_constituent_GeV: float,
    mu_constituent_mu_B: float,
    r_mass_ratios: tuple = (1.0, 1.0, 1.0),
    state: str = "D5",
) -> dict:
    """Compute the magnetic moment of a composite DM state.

    Per Aranda+ 2016 Eq. 4.1-4.2:
      For octet states (D1-D8):
        mu_D = sum_i c_i * mu_i
      For decuplet states (D*1-D*11):
        mu_D* = sum_i c_i * mu_i

    Coefficients are listed in Eq. 4.1 (octet) and 4.2 (decuplet).
    The constituent magnetic moments mu_i are in units of e*hbar/(2*m_1)
    where m_1 is the lightest constituent mass.

    Args:
      m_chi_GeV: composite DM mass (GeV)
      m_constituent_GeV: lightest constituent mass m_1 (GeV)
      mu_constituent_mu_B: mu_1 in Bohr magnetons
      r_mass_ratios: (m_1/m_1, m_1/m_2, m_1/m_3) = (1, r_12, r_13)
      state: composite state name ('D1', ..., 'D8', 'D*1', ..., 'D*11')

    Returns:
      Dict with mu_DM in mu_B, mu_DM in mu_N, and constituent info
    """
    r12, r13 = r_mass_ratios[1], r_mass_ratios[2]
    # Constituent magnetic moments scaled by mass ratios
    # mu_i / mu_1 = (m_1/m_i) is the standard Dirac scaling
    mu_1 = mu_constituent_mu_B
    mu_2 = mu_1 * r12
    mu_3 = mu_1 * r13

    # Coefficients from Aranda+ 2016 Eq. 4.1 (octet) and 4.2 (decuplet)
    # Encoding the full formula including the 1/3 factor where applicable.
    coefficients = {
        'D1': (4.0/3.0, -1.0/3.0, 0),       # (1/3)(4 mu_1 - mu_2)
        'D2': (-1.0/3.0, 4.0/3.0, 0),       # (1/3)(4 mu_2 - mu_1)
        'D3': (-1.0/3.0, 0, 4.0/3.0),       # (1/3)(4 mu_3 - mu_1)
        'D4': (0, -1.0/3.0, 4.0/3.0),       # (1/3)(4 mu_3 - mu_2)
        'D5': (0, 0, 1),                     # mu_3 (no 1/3 factor!)
        'D6': (2.0/3.0, 2.0/3.0, -1.0/3.0), # (2/3)(mu_1 + mu_2) - (1/3) mu_3
        'D7': (0, 4.0/3.0, -1.0/3.0),       # (1/3)(4 mu_2 - mu_3)
        'D8': (4.0/3.0, 0, -1.0/3.0),       # (1/3)(4 mu_1 - mu_3)
        'D*1': (2, 1, 0),     # 2 mu_1 + mu_2
        'D*2': (1, 2, 0),     # 2 mu_2 + mu_1
        'D*3': (1, 0, 2),     # 2 mu_3 + mu_1
        'D*4': (0, 1, 2),     # 2 mu_3 + mu_2
        'D*6': (1, 1, 1),     # mu_1 + mu_2 + mu_3
        'D*7': (0, 2, 1),     # 2 mu_2 + mu_3
        'D*8': (2, 0, 1),     # 2 mu_1 + mu_3
        'D*9': (3, 0, 0),     # 3 mu_1
        'D*10': (0, 3, 0),    # 3 mu_2
        'D*11': (0, 0, 3),    # 3 mu_3
    }

    if state not in coefficients:
        raise ValueError(f"Unknown state: {state}")

    c1, c2, c3 = coefficients[state]
    # Aranda+ 2016 Eq 4.1 gives explicit formulas:
    #   D1-D4, D6-D8: mu_D = (1/3)(...)
    #   D5: mu_D = mu_3 (no 1/3 factor)
    # The coefficients dict encodes the FULL formula including factor.
    mu_D = c1 * mu_1 + c2 * mu_2 + c3 * mu_3

    return {
        'mu_x_mu_B': mu_D,
        'mu_x_mu_N': mu_D * 1836.15267,
        'm_chi_GeV': m_chi_GeV,
        'm_constituent_GeV': m_constituent_GeV,
        'state': state,
        'c1_c2_c3': (c1, c2, c3),
    }


# ============================================================================
# Model 2: Vector-like fermion loop (Hisano-style unitarity)
# ============================================================================
def vectorlike_fermion_mu_x(
    g_Y: float,
    m_chi_GeV: float,
    M_psi_GeV: float,
) -> dict:
    """Compute the magnetic moment from a vector-like fermion loop.

    Per the standard Dirac magnetic moment calculation, a Yukawa
    coupling g_Y between the DM chi and a vector-like fermion psi
    generates a magnetic moment at one loop:

      mu_x ~ (g_Y^2 * e * m_chi) / (16*pi^2 * M_psi^2)

    In units where the result is in Bohr magnetons (mu_B):
      mu_x / mu_B ~ (g_Y^2 * alpha_em / pi) * (m_chi / M_psi^2) * (hbar c / GeV^-1) / mu_B

    The exact prefactor depends on the chiral structure. For a
    vector-like fermion (chiral-symmetric), the loop integral gives:

      mu_x = (g_Y^2 * e) / (16 * pi^2 * M_psi) * f(m_chi^2 / M_psi^2)

    where f(x) -> 1/3 as x -> 0 (heavy mediator limit).

    Reference: Agrawal+ 2022 (arXiv:2203.07353) Eq. 4.2 for
    a similar calculation.

    Args:
      g_Y: Yukawa coupling (dimensionless)
      m_chi_GeV: DM mass in GeV
      M_psi_GeV: vector-like fermion mass in GeV

    Returns:
      Dict with mu_x in mu_B and mu_N
    """
    # Heavy mediator limit (m_chi << M_psi)
    x = m_chi_GeV / M_psi_GeV
    if x < 1e-3:
        f = 1.0/3.0  # heavy mediator limit
    elif x < 1.0:
        # m_chi < M_psi: standard formula
        f = (1 - x**2) * np.log((1+x)/(1-x)) / (2*x)
    else:
        # m_chi > M_psi: light mediator limit
        # f = (x^2 - 1) * arctan(1/sqrt(x^2-1)) / x
        f = (x**2 - 1) * np.arctan(1.0/np.sqrt(x**2 - 1)) / x

    # Prefactor: g_Y^2 * e / (16*pi^2 * M_psi)
    # In natural units, mu_x in e*hbar/(2*GeV) = 1/M_psi * (1/GeV)
    # Convert to mu_B (e*hbar/(2*m_e))
    prefactor = (g_Y**2 * np.sqrt(4 * np.pi * ALPHA_EM)) / (16 * np.pi**2 * M_psi_GeV)
    mu_x_natural = prefactor * f  # in units of GeV^-1
    # Convert: mu_x_natural * (eV^-1) -> mu_B. 1/m_e (in GeV^-1) = 1/5.11e-4 = 1957
    mu_x_mu_B = mu_x_natural * (1.0 / M_E_GEV)  # dimensionless ratio in mu_B units

    return {
        'mu_x_mu_B': mu_x_mu_B,
        'mu_x_mu_N': mu_x_mu_B * 1836.15267,
        'g_Y': g_Y,
        'm_chi_GeV': m_chi_GeV,
        'M_psi_GeV': M_psi_GeV,
        'loop_function_f': f,
    }


# ============================================================================
# Model 3: Dark photon mediation (Fabbrichesi+ 2020)
# ============================================================================
def dark_photon_mu_x(
    epsilon: float,
    g_D: float,
    m_chi_GeV: float,
    M_A_prime_GeV: float,
) -> dict:
    """Compute the magnetic moment from dark photon mediation.

    Per Fabbrichesi+ 2020 (arXiv:2005.01515) Eq. 1.24:
      The effective magnetic moment from kinetic mixing is:
      mu_x ~ epsilon * g_D * m_chi / M_A'^2

    where epsilon is the kinetic mixing parameter, g_D is the
    dark gauge coupling, and M_A' is the dark photon mass.

    Args:
      epsilon: kinetic mixing parameter (dimensionless, ~1e-4)
      g_D: dark gauge coupling (dimensionless, ~1)
      m_chi_GeV: DM mass in GeV
      M_A_prime_GeV: dark photon mass in GeV

    Returns:
      Dict with mu_x in mu_B and mu_N
    """
    # Prefactor: epsilon * g_D * m_chi / M_A'^2
    # In natural units: epsilon * g_D * m_chi / M_A'^2 has units of 1/GeV
    # Convert to mu_B (1/m_e in GeV^-1)
    mu_x_natural = epsilon * g_D * m_chi_GeV / (M_A_prime_GeV**2)
    mu_x_mu_B = mu_x_natural * (1.0 / M_E_GEV)

    return {
        'mu_x_mu_B': mu_x_mu_B,
        'mu_x_mu_N': mu_x_mu_B * 1836.15267,
        'epsilon': epsilon,
        'g_D': g_D,
        'm_chi_GeV': m_chi_GeV,
        'M_A_prime_GeV': M_A_prime_GeV,
    }


# ============================================================================
# Calibration: find parameters for each model that reproduce LZ data
# ============================================================================
def calibrate_composite_to_lz(target_mu_x_mu_N=6.10e-8, m_chi_GeV=1000.0):
    """Find composite-DM parameters that reproduce LZ mu_x.

    Strategy: fix mass ratios r_12 = r_13 = 1 (degenerate constituents),
    vary the constituent magnetic moment mu_1 to match LZ.
    """
    # For D5 (simplest, mu_D5 = mu_3 = mu_1 with r=1): mu_D = mu_1
    # So we need mu_1 such that mu_D = target
    target_mu_x_mu_B = target_mu_x_mu_N / 1836.15267

    # Try D5 with r_12 = r_13 = 1: mu_D = mu_1
    result = composite_dm_mu_x(
        m_chi_GeV=m_chi_GeV,
        m_constituent_GeV=m_chi_GeV / 3.0,  # rough: 3 constituents, equal share
        mu_constituent_mu_B=target_mu_x_mu_B,
        r_mass_ratios=(1.0, 1.0, 1.0),
        state='D5',
    )
    return result


def calibrate_vectorlike_to_lz(target_mu_x_mu_N=6.10e-8, m_chi_GeV=1000.0,
                                  g_Y=1.0, M_psi_GeV=100.0):
    """Find vector-like fermion parameters that reproduce LZ mu_x.

    Strategy: fix g_Y = 1, vary M_psi to match LZ.
    Start with M_psi >> m_chi (heavy mediator limit).
    """
    target_mu_x_mu_B = target_mu_x_mu_N / 1836.15267

    M_psi = M_psi_GeV
    # If starting point has x ~ 1, jump to safe initial
    if abs(m_chi_GeV - M_psi) / m_chi_GeV < 0.1:
        M_psi = m_chi_GeV * 10  # start heavy

    for _ in range(50):
        result = vectorlike_fermion_mu_x(g_Y, m_chi_GeV, M_psi)
        if result['mu_x_mu_B'] > 1e-30:
            ratio = target_mu_x_mu_B / result['mu_x_mu_B']
            M_psi = M_psi / np.sqrt(ratio)  # mu_x ~ 1/M_psi
        if abs(result['mu_x_mu_B'] - target_mu_x_mu_B) / max(target_mu_x_mu_B, 1e-30) < 1e-6:
            break

    return vectorlike_fermion_mu_x(g_Y, m_chi_GeV, M_psi)


def calibrate_dark_photon_to_lz(target_mu_x_mu_N=6.10e-8, m_chi_GeV=1000.0,
                                  epsilon=1e-4, g_D=1.0, M_A_prime_GeV=100.0):
    """Find dark photon parameters that reproduce LZ mu_x.

    Strategy: fix epsilon, g_D, vary M_A' to match LZ.
    """
    target_mu_x_mu_B = target_mu_x_mu_N / 1836.15267

    M_A_prime = M_A_prime_GeV
    for _ in range(50):
        result = dark_photon_mu_x(epsilon, g_D, m_chi_GeV, M_A_prime)
        if result['mu_x_mu_B'] > 0:
            # mu_x ~ 1/M_A'^2, so M_A' = M_A' * sqrt(mu_x/target)
            ratio = result['mu_x_mu_B'] / target_mu_x_mu_B
            M_A_prime = M_A_prime * np.sqrt(ratio)
        if abs(result['mu_x_mu_B'] - target_mu_x_mu_B) / target_mu_x_mu_B < 1e-6:
            break

    return dark_photon_mu_x(epsilon, g_D, m_chi_GeV, M_A_prime)


# ============================================================================
# Constraints
# ============================================================================
def unitarity_bound(m_chi_GeV: float) -> float:
    """Per Aranda+ 2016 (citing Hisano+ 2002 / Griest-Kamionkowski 1990):
    mu_x * m_chi < 20 m_e (in natural units where m_e ~ mu_B).

    Returns the upper bound on mu_x in mu_B.
    """
    return 20.0 * M_E_GEV / m_chi_GeV


def perturbative_bound(m_chi_GeV: float) -> float:
    """Per Aranda+ 2016: mu_DM < e / m_DM (perturbativity).

    Returns the upper bound on mu_x in mu_B.
    """
    return np.sqrt(4 * np.pi * ALPHA_EM) / m_chi_GeV


def main():
    print("=" * 70)
    print("T90 Path C.4.6 (v16) — UV completion of magnetic-moment DM")
    print("=" * 70)
    print()
    m_chi = 1000.0
    target_mu_x_mu_N = 6.10e-8
    print(f"LZ-tuned parameters: m_chi = {m_chi} GeV, mu_x = {target_mu_x_mu_N:.3e} mu_N")
    print()
    print("Constraints:")
    print(f"  Unitarity (mu_x * m_chi < 20 m_e): mu_x < {unitarity_bound(m_chi):.3e} mu_B")
    print(f"  Perturbativity (mu_x < e/m_chi):     mu_x < {perturbative_bound(m_chi):.3e} mu_B")
    print(f"  LZ-tuned mu_x:                       mu_x = {target_mu_x_mu_N / 1836.15267:.3e} mu_B")
    print(f"  Margin below unitarity: {unitarity_bound(m_chi) / (target_mu_x_mu_N / 1836.15267):.1f}x")
    print()

    # Calibrate each model
    results = {}

    print("Model 1: Composite DM (Aranda+ 2016)")
    print("  Using D5 state (mu_D = mu_3 = mu_1 for r=1)")
    r1 = calibrate_composite_to_lz(target_mu_x_mu_N, m_chi)
    print(f"  Required mu_1 = {r1['mu_x_mu_B']:.3e} mu_B")
    print(f"  Composite mu_D = {r1['mu_x_mu_N']:.3e} mu_N (matches LZ)")
    print(f"  Constituent mass ~{r1['m_constituent_GeV']:.0f} GeV (3-constituent assumption)")
    print()
    results['composite_DM'] = r1

    print("Model 2: Vector-like fermion loop")
    r2 = calibrate_vectorlike_to_lz(target_mu_x_mu_N, m_chi, g_Y=1.0)
    print(f"  Required M_psi = {r2['M_psi_GeV']:.3e} GeV (for g_Y = 1)")
    print(f"  Resulting mu_x = {r2['mu_x_mu_B']:.3e} mu_B = {r2['mu_x_mu_N']:.3e} mu_N")
    print()
    results['vectorlike_fermion'] = r2

    print("Model 3: Dark photon mediation")
    r3 = calibrate_dark_photon_to_lz(target_mu_x_mu_N, m_chi,
                                       epsilon=1e-4, g_D=1.0)
    print(f"  Required M_A' = {r3['M_A_prime_GeV']:.3e} GeV (for epsilon=1e-4, g_D=1)")
    print(f"  Resulting mu_x = {r3['mu_x_mu_B']:.3e} mu_B = {r3['mu_x_mu_N']:.3e} mu_N")
    print()
    results['dark_photon'] = r3

    # Write output
    out_path = _PROJECT_ROOT / "outputs" / "t90" / "uv_completion.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90 Path C.4.6 (v16, UV completion)',
        'm_chi_GeV': m_chi,
        'target_mu_x_mu_N': target_mu_x_mu_N,
        'unitarity_bound_mu_B': unitarity_bound(m_chi),
        'perturbative_bound_mu_B': perturbative_bound(m_chi),
        'target_mu_x_mu_B': target_mu_x_mu_N / 1836.15267,
        'margin_below_unitarity': unitarity_bound(m_chi) / (target_mu_x_mu_N / 1836.15267),
        'models': results,
        'references': [
            'Aranda, Barajas, Cembranos (2016), arXiv:1511.02805, JCAP 03 (2016) 034',
            'Hisano, Matsumoto, Nojiri (2002), arXiv:hep-ph/0212022, PRD 67, 075014',
            'Fabbrichesi, Gabrielli, Lanfranchi (2020), arXiv:2005.01515',
            'Griest, Kamionkowski (1990), PRL 64, 615 (unitarity bound)',
        ],
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()
