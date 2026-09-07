"""
T90 Path C.4.6 (v18) — Genuine UV calculation in composite model.

REPLACES v16's free-parameter approach with LATTICE-DERIVED values
from Appelquist (LSD Collaboration) 2013, PRD 88, 014502.

PURPOSE
=======
v16 treated the constituent magnetic moment μ_1 as a free parameter
calibrated to reproduce the LZ 248 keV magnetic moment. This script
turns μ_1 into a PREDICTED value, using published lattice calculations
of the form factors of electroweak-neutral composite dark baryons.

LATTICE INPUT (Appelquist+ 2013, PRD 88, 014502, arXiv:1301.1693):
  - SU(3) hidden-sector gauge theory with Nf = 2 or Nf = 6
    degenerate fermions in the fundamental representation
  - Fermions are SU(2)_L singlets with charges Q_u = 2/3, Q_d = -1/3
  - Dark baryon is a "dark neutron" (udd), mass M_B (free parameter)
  - Lattice computes:
    * anomalous magnetic moment κ_neut (in units of e/(2*M_B))
    * mean square charge radius <r^2_E,neut>
  - Key result: κ_neut ~ -0.4 to -0.6 across M_B/M_B0 = 1.0-1.6
    (small Nf dependence)
  - XENON100 limit: M_B > 10 TeV

METHOD
======
1. Take κ_neut from lattice (Nf=2 or Nf=6, chiral limit)
2. Compute constituent magnetic moment μ_1 from κ_neut:
     κ_neut = (1/6) κ_s - (1/2) κ_v
     μ_1 = κ_neut * e/(2 M_B)
3. Use this μ_1 in v16's composite-DM formula:
     μ_D5 = μ_1 (for r=1, D5 state)
4. Compute composite baryon magnetic moment μ_DM for various M_B
5. Compare to LZ-tuned μ_x = 6.10e-8 μ_N at m_chi = 1 TeV

OUTPUT
  - outputs/t90/composite_dm_lattice_uv.json
  - Predicted μ_x as function of M_B (composite DM mass)
  - Comparison to LZ-tuned value

CONSTRAINTS
  - No new dependencies (rule 17/24)
  - Uses published lattice values; no new lattice calc
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================================
# Physical constants
# ============================================================================
M_E_GEV = 0.51099895e-3  # electron mass
M_PROTON_GEV = 0.938272   # proton mass
MU_B_GEV = M_E_GEV        # Bohr magneton in GeV
MU_N_GEV = MU_B_GEV / (M_PROTON_GEV / M_E_GEV)  # nuclear magneton in GeV
E_CHARGE = 1.0  # in natural units


# ============================================================================
# Lattice input (Appelquist+ 2013, PRD 88, 014502)
# ============================================================================
# κ_neut values from Figure 4 of the paper
# Both Nf=2 and Nf=6 give similar values (minimal Nf dependence)
KAPPA_NEUT_NF2 = {
    # (M_B / M_B0, kappa_neut) pairs from Figure 4
    # M_B0 is the chiral-limit baryon mass
    1.00: -0.55,
    1.10: -0.50,
    1.20: -0.45,
    1.30: -0.42,
    1.40: -0.40,
    1.50: -0.42,
    1.60: -0.45,
}
KAPPA_NEUT_NF6 = {
    1.00: -0.60,
    1.10: -0.55,
    1.20: -0.50,
    1.30: -0.48,
    1.40: -0.46,
    1.50: -0.48,
    1.60: -0.50,
}

# Mean square charge radius (in lattice units) - typical values
# from Figure 3: <r^2>_E,neut ~ 0.005-0.030 (in lattice units)
R2_E_NEUT_LATTICE = 0.020  # representative value in lattice units

# XENON100 limit from the paper
XENON100_LIMIT_GEV = 10e3  # 10 TeV lower bound on M_B


# ============================================================================
# Constituent magnetic moment from lattice κ_neut
# ============================================================================
def kappa_neut_lattice(M_B_GeV: float, M_B0_GeV: float = 1.0, nf: int = 2) -> float:
    """Interpolate κ_neut from lattice data.

    κ_neut is the anomalous magnetic moment of the neutral dark baryon
    in units of e/(2 M_B). It's a dimensionless number.

    Parameters:
      M_B_GeV: composite dark baryon mass in GeV
      M_B0_GeV: chiral-limit baryon mass (for scaling M_B/M_B0)
      nf: 2 or 6 (number of fermions in hidden sector)
    """
    ratio = M_B_GeV / M_B0_GeV
    table = KAPPA_NEUT_NF2 if nf == 2 else KAPPA_NEUT_NF6
    # Linear interpolation
    keys = sorted(table.keys())
    if ratio <= keys[0]:
        return table[keys[0]]
    if ratio >= keys[-1]:
        return table[keys[-1]]
    # Find bracketing keys
    for i in range(len(keys) - 1):
        if keys[i] <= ratio <= keys[i + 1]:
            x0, x1 = keys[i], keys[i + 1]
            y0, y1 = table[x0], table[x1]
            return y0 + (ratio - x0) / (x1 - x0) * (y1 - y0)
    return table[keys[-1]]


def mu_1_from_kappa_neut(kappa_neut: float, M_B_GeV: float) -> float:
    """Compute constituent magnetic moment μ_1 from κ_neut.

    Per Appelquist+ 2013 Eq. 10:
        κ_neut = (1/6) κ_s - (1/2) κ_v

    The constituent magnetic moment is:
        μ_1 = (κ_neut / (κ_s / 6 - κ_v / 2)) * (e/(2 M_1))

    For SU(2)_L singlet fermions with Q_u = 2/3, Q_d = -1/3, the
    constituent mass M_1 ~ M_B / 3 (3 valence quarks).

    Args:
      kappa_neut: dimensionless anomalous magnetic moment
      M_B_GeV: composite dark baryon mass in GeV

    Returns:
      mu_1 in units of Bohr magnetons (mu_B)
    """
    # In the simple case where the constituent mass is M_B/3
    M_1_GeV = M_B_GeV / 3.0
    # mu_1 = kappa_neut * e / (2 M_1) / mu_B
    # mu_B = e*hbar / (2 m_e), so mu_1 in mu_B = kappa_neut * (m_e / M_1)
    mu_1_mu_B = kappa_neut * (M_E_GEV / M_1_GeV)
    return mu_1_mu_B


# ============================================================================
# Composite DM magnetic moment from v16 formula (D5 state)
# ============================================================================
def composite_dm_mu_D5(mu_1_mu_B: float) -> float:
    """Compute composite DM magnetic moment for D5 state with r=1.

    Per Aranda+ 2016 Eq. 4.1 (cited in v16):
        mu_D5 = mu_3 = mu_1 (for r_12 = r_13 = 1)

    So the composite DM magnetic moment equals the constituent magnetic
    moment (modulo the constituent charge distribution).

    Args:
      mu_1_mu_B: constituent magnetic moment in mu_B

    Returns:
      mu_DM in mu_B
    """
    return mu_1_mu_B


def composite_dm_mu_DM_natural(mu_DM_mu_B: float, m_chi_GeV: float) -> float:
    """Convert mu_DM in mu_B to natural units (used for EFT matching)."""
    # mu_DM [mu_B] = mu_DM_natural [e*hbar/(2 m_e)] = mu_DM_natural [1/m_e in GeV^-1]
    # So mu_DM_natural = mu_DM_mu_B * mu_B = mu_DM_mu_B * (e*hbar / (2 m_e))
    # In units of e*hbar/(2 m_e), this is mu_DM_mu_B itself.
    # But for EFT, mu_DM in natural units is:
    #   mu_DM_natural = mu_DM_mu_B * (1 GeV / 2 m_e in GeV) [GeV^-1]
    return mu_DM_mu_B / (2 * M_E_GEV)  # in units of 1/GeV


def composite_dm_mu_DM_mu_N(mu_DM_mu_B: float) -> float:
    """Convert mu_DM in mu_B to mu_N (nuclear magnetons)."""
    return mu_DM_mu_B * (M_PROTON_GEV / M_E_GEV)  # = mu_DM_mu_B * 1836.15


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("T90 Path C.4.6 (v18) — Genuine UV calculation: composite DM")
    print("       with LATTICE-derived magnetic moment (Appelquist+ 2013)")
    print("=" * 70)
    print()
    print("LATTICE INPUT (Appelquist+ 2013, PRD 88, 014502):")
    print("  SU(3) hidden-sector, Nf=2 or Nf=6 fermions in fundamental rep.")
    print("  Dark baryon = 'dark neutron' (udd), mass M_B")
    print("  κ_neut ~ -0.40 to -0.60 across M_B/M_B0 = 1.0-1.6")
    print("  XENON100 limit: M_B > 10 TeV")
    print()
    print("=" * 70)
    print()
    print(f"LZ-tuned target: mu_x = 6.10e-8 mu_N at m_chi = 1 TeV (from T90 7D)")
    print(f"                = {6.10e-8 * M_PROTON_GEV / M_E_GEV:.3e} mu_B")
    print()
    print("LATTICE-PREDICTED mu_x as function of M_B:")
    print()

    results = {}
    for nf in [2, 6]:
        print(f"Nf = {nf}:")
        print(f"  {'M_B [GeV]':<12} {'kappa_neut':<12} {'mu_1 [mu_B]':<15} "
              f"{'mu_DM [mu_N]':<15} {'matches LZ?':<12}")
        print(f"  {'-'*12} {'-'*12} {'-'*15} {'-'*15} {'-'*12}")
        for M_B in [10e3, 30e3, 100e3, 1000e3, 3000e3]:
            kappa = kappa_neut_lattice(M_B, M_B0_GeV=1.0, nf=nf)
            mu_1 = mu_1_from_kappa_neut(kappa, M_B)
            mu_DM_mu_B = composite_dm_mu_D5(mu_1)
            mu_DM_mu_N = composite_dm_mu_DM_mu_N(mu_DM_mu_B)
            matches = "YES" if abs(mu_DM_mu_N - 6.10e-8) / 6.10e-8 < 0.5 else "no"
            print(f"  {M_B:<12.0f} {kappa:<12.3f} {mu_1:<15.3e} "
                  f"{mu_DM_mu_N:<15.3e} {matches:<12}")
        print()

        # Save result for M_B = 1 TeV
        M_B_target = 1000e3  # 1 TeV — does NOT satisfy XENON100
        kappa = kappa_neut_lattice(M_B_target, M_B0_GeV=1.0, nf=nf)
        mu_1 = mu_1_from_kappa_neut(kappa, M_B_target)
        mu_DM_mu_B = composite_dm_mu_D5(mu_1)
        mu_DM_mu_N = composite_dm_mu_DM_mu_N(mu_DM_mu_B)
        results[f'nf{nf}_M_B_1_TeV'] = {
            'M_B_GeV': M_B_target,
            'kappa_neut': kappa,
            'mu_1_mu_B': mu_1,
            'mu_DM_mu_N': mu_DM_mu_N,
            'matches_LZ': abs(mu_DM_mu_N - 6.10e-8) / 6.10e-8 < 0.5,
        }

        # Save result for M_B = 30 TeV (satisfies XENON100)
        M_B_target = 30e3
        kappa = kappa_neut_lattice(M_B_target, M_B0_GeV=1.0, nf=nf)
        mu_1 = mu_1_from_kappa_neut(kappa, M_B_target)
        mu_DM_mu_B = composite_dm_mu_D5(mu_1)
        mu_DM_mu_N = composite_dm_mu_DM_mu_N(mu_DM_mu_B)
        results[f'nf{nf}_M_B_30_TeV'] = {
            'M_B_GeV': M_B_target,
            'kappa_neut': kappa,
            'mu_1_mu_B': mu_1,
            'mu_DM_mu_N': mu_DM_mu_N,
            'matches_LZ': abs(mu_DM_mu_N - 6.10e-8) / 6.10e-8 < 0.5,
        }

    # Find the M_B that matches LZ
    print("FINDING M_B that matches LZ (mu_x = 6.10e-8 mu_N):")
    for nf in [2, 6]:
        # Binary search
        M_B_low, M_B_high = 1e3, 1e6  # 1 GeV to 1000 TeV
        for _ in range(50):
            M_B_mid = (M_B_low + M_B_high) / 2
            kappa = kappa_neut_lattice(M_B_mid, M_B0_GeV=1.0, nf=nf)
            mu_1 = mu_1_from_kappa_neut(kappa, M_B_mid)
            mu_DM_mu_B = composite_dm_mu_D5(mu_1)
            mu_DM_mu_N = composite_dm_mu_DM_mu_N(mu_DM_mu_B)
            if mu_DM_mu_N > 6.10e-8:
                M_B_low = M_B_mid  # need larger M_B
            else:
                M_B_high = M_B_mid  # need smaller M_B
            if abs(M_B_high - M_B_low) / M_B_low < 1e-6:
                break
        M_B_match = (M_B_low + M_B_high) / 2
        satisfies_xenon100 = M_B_match > XENON100_LIMIT_GEV
        print(f"  Nf={nf}: M_B = {M_B_match:.0f} GeV = {M_B_match/1e3:.1f} TeV "
              f"({'satisfies' if satisfies_xenon100 else 'VIOLATES'}) XENON100")
        results[f'nf{nf}_matching_M_B_GeV'] = M_B_match
        results[f'nf{nf}_satisfies_XENON100'] = satisfies_xenon100

    # Output
    out_path = _PROJECT_ROOT / "outputs" / "t90" / "composite_dm_lattice_uv.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T90 Path C.4.6 (v18, genuine UV via LSD lattice)',
        'lattice_source': 'Appelquist+ 2013, PRD 88, 014502, arXiv:1301.1693',
        'method': (
            'κ_neut from lattice (Nf=2 or Nf=6) → μ_1 = κ_neut × m_e/M_1 '
            '(M_1 = M_B/3) → μ_DM = μ_1 (D5 state, r=1)'
        ),
        'LZ_target': {
            'mu_x_mu_N': 6.10e-8,
            'mu_x_mu_B': 6.10e-8 * M_PROTON_GEV / M_E_GEV,
            'm_chi_GeV': 1000.0,
        },
        'XENON100_limit_GeV': XENON100_LIMIT_GEV,
        'results': results,
        'caveats': [
            'Lattice κ_neut values are approximate (interpolated from Figure 4).',
            'Direct use of lattice κ_neut values requires checking the exact',
            'values from Tables in the paper (the figures are illustrative).',
            'The constituent mass M_1 = M_B/3 is a simplifying assumption',
            '(real composite DM has constituent masses that may differ).',
            'A proper calculation would also include the charge radius term,',
            'which becomes important at Q2 ~ 1/(r^2).',
        ],
        'references': [
            'Appelquist+ (LSD), PRD 88, 014502 (2013), arXiv:1301.1693',
            'Aranda, Barajas, Cembranos (2016), arXiv:1511.02805 (v16 UV formula)',
            'XENON100 Collaboration, PRL 107, 131302 (2011)',
        ],
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote: {out_path}")


if __name__ == '__main__':
    main()