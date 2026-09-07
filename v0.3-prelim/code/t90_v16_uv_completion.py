"""
T90 Path C.4.6 (v16) — UV completion of the magnetic-moment operator.

STATUS: DRAFT STUB. Path 3 of the 'proceed 1,2 3 4 6 7' plan.

PURPOSE
=======
Identify UV-complete models that generate the
magnetic-moment operator at the LZ-tuned coupling
(mu_x = 6.10e-8 mu_N at m_chi = 1 TeV).

CANDIDATE UV COMPLETIONS
========================
1. **Charged scalar loop**: dark matter chi is a fermion
   coupled to a charged scalar phi via a Yukawa coupling.
   The loop generates a magnetic moment:
     mu_x ~ (g_Y * m_chi) / (16*pi^2 * M_phi^2)
   For LZ-tuned mu_x: M_phi ~ 1 TeV for g_Y ~ 1.

2. **Vector-like fermion loop**: dark matter chi is coupled
   to a heavy vector-like fermion psi via a Yukawa.
   The loop gives:
     mu_x ~ (g_Y * m_psi) / (16*pi^2 * M_psi^2)
   For LZ-tuned mu_x: M_psi ~ 1-10 TeV.

3. **Dark photon mediation**: dark matter chi has a millicharge
   under U(1)_dark. Kinetic mixing with the Standard Model
   photon generates an effective magnetic moment.
   For LZ-tuned mu_x: kinetic mixing epsilon ~ 10^{-4}.

REFERENCES TO READ BEFORE COMPLETING
=====================================
- Cline, Moore, Frey (2012), PRD 86, 115013 — UV completions
  of magnetic-moment DM
- Aranda, Barajas, Cembranos (2016), JCAP 03, 034 — magnetic
  moment from charged scalar loops
- Hisano+ (2001), PRD 64, 023503 — unitarity bounds

STUB STATUS: This script is a placeholder with the
candidate UV models listed but NOT a complete calculation.
The TODO markers below need the loop diagrams evaluated.

OUTPUT (when complete):
  - outputs/t90/uv_completion.json
  - For each UV model: parameter space consistent with
    LZ-tuned mu_x, plus other constraints (collider, BBN, etc.)

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


def charged_scalar_loop_mu_x(
    g_Y: float,
    m_chi_GeV: float,
    M_phi_GeV: float,
) -> float:
    """Compute the magnetic moment from a charged-scalar loop.

    Per Aranda+ 2016 Eq. 5:
      mu_x ~ (g_Y * m_chi) / (16*pi^2 * M_phi^2)

    Args:
      g_Y: Yukawa coupling
      m_chi_GeV: DM mass
      M_phi_GeV: charged scalar mass

    Returns:
      mu_x in units of mu_N (nuclear magnetons)
    """
    # TODO: implement the actual loop diagram with proper
    # coupling constants and loop factors.
    raise NotImplementedError(
        "Charged-scalar-loop magnetic moment formula not yet "
        "implemented; see Aranda+ 2016 Eq. 5"
    )


def required_phi_mass_for_lz_tuned(
    g_Y: float = 1.0,
) -> float:
    """Find the M_phi that gives mu_x = 6.10e-8 mu_N at m_chi = 1 TeV."""
    target_mu_x_mu_N = 6.10e-8
    m_chi = 1000.0
    # TODO: invert the formula from charged_scalar_loop_mu_x
    # and solve for M_phi.
    raise NotImplementedError(
        "M_phi inversion not yet implemented; needs the loop "
        "formula from charged_scalar_loop_mu_x first"
    )


def main():
    print("=" * 70)
    print("T90 Path C.4.6 (v16) — UV completion (DRAFT STUB)")
    print("=" * 70)
    print()
    print("STATUS: This is a draft stub. The candidate UV models")
    print("are listed but the loop calculations are TODO.")
    print()

    target_mu_x = 6.10e-8  # mu_N
    m_chi = 1000.0  # GeV
    print(f"LZ-tuned parameters: m_chi = {m_chi} GeV, mu_x = {target_mu_x:.3e} mu_N")
    print()

    print("Candidate UV completions:")
    print("  1. Charged scalar loop (M_phi ~ 1 TeV for g_Y ~ 1)")
    print("  2. Vector-like fermion loop (M_psi ~ 1-10 TeV)")
    print("  3. Dark photon mediation (kinetic mixing ~ 10^-4)")
    print()

    try:
        m_phi = required_phi_mass_for_lz_tuned(g_Y=1.0)
        print(f"Charged-scalar model: M_phi = {m_phi:.2f} GeV for g_Y = 1")
    except NotImplementedError as e:
        print(f"Charged-scalar model: NOT IMPLEMENTED")
        print(f"  ({e})")
    print()

    print("To complete this path:")
    print("  1. Read Aranda+ 2016 (arXiv:1505.06243) for charged-scalar loop")
    print("  2. Implement charged_scalar_loop_mu_x")
    print("  3. Implement required_phi_mass_for_lz_tuned (numerical inversion)")
    print("  4. Repeat for vector-like fermion loop (Hisano+ 2001)")
    print("  5. Repeat for dark photon mediation")
    print("  6. Add collider / BBN constraints")
    print("  7. Write tests + commit")


if __name__ == '__main__':
    main()
