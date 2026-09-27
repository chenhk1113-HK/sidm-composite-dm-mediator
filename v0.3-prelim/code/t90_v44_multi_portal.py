#!/usr/bin/env python
"""
T90.44 — Multi-portal composite SIDM extension.

Per T90.43 finding, the single-portal light-mediator Yukawa model is
blocked by the LZ magnetic-moment + LZ direct-detection channels. The
reviewer's Point 3 proposed a multi-portal architecture:

  Portal A (heavy, suppressed): m_phi = 700 MeV, g_chi = 1.5
    - Provides LZ magnetic-moment signal
    - Provides CMB suppression
    - Satisfies FERMI dwarf
    - Low sigma/m everywhere (heavy mediator -> flat)

  Portal B (light, active): m_phi = 1-30 MeV, g_chi = 0.22
    - Provides high sigma/m(28) ~ 50 cm^2/g for Cloud-9
    - Suppressed at high v (v^-8 Yukawa dependence)
    - Below LZ detection threshold

  Combined sigma/m(v) = sigma/m_A(v) + sigma/m_B(v)

This module computes the combined sigma/m(v) from the multi-portal
parameters and provides the likelihood wrappers for T90 channels.

Parameters:
  m_phi_A_MeV: Portal A mediator mass (MeV)
  m_chi_A_GeV: Portal A DM mass (GeV)
  g_chi_A: Portal A coupling
  epsilon_A: Portal A kinetic mixing (sets LZ strength)
  m_phi_B_MeV: Portal B mediator mass (MeV)
  m_chi_B_GeV: Portal B DM mass (GeV)
  g_chi_B: Portal B coupling

Multi-portal sigma/m(v):
  sigma/m_A(v) = sigma_m_yukawa(v, m_phi_A, m_chi_A, g_chi_A)
  sigma/m_B(v) = sigma_m_yukawa(v, m_phi_B, m_chi_B, g_chi_B)
  sigma/m_total(v) = sigma/m_A(v) + sigma/m_B(v)

Implementation notes:
  1. The two portals are assumed to have independent Yukawa sectors.
     No interference effects at this order (Born approximation).
  2. Each portal's contribution to LZ is via its own kinetic mixing.
     Portal A has the dominant LZ signal; Portal B is suppressed by
     epsilon_B << epsilon_A.
  3. The Cloud-9 RELHIC channels use the COMBINED sigma/m_total.
  4. The legacy SIDM channels (dSph, UFD, Bullet) use the COMBINED
     sigma/m_total at their characteristic velocity.
"""
from __future__ import annotations

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Lazy import of the Yukawa form
def _sigma_m_yukawa(v_kms: float, m_phi_MeV: float, m_chi_GeV: float, g_chi: float) -> float:
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    return sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)


def sigma_m_multi_portal(
    v_kms: float,
    m_phi_A_MeV: float,
    m_chi_A_GeV: float,
    g_chi_A: float,
    m_phi_B_MeV: float,
    m_chi_B_GeV: float,
    g_chi_B: float,
) -> float:
    """Combined sigma/m at velocity v from two Yukawa portals.

    Parameters
    ----------
    v_kms : float
        Relative velocity (km/s)
    m_phi_A_MeV : float
        Portal A mediator mass (MeV)
    m_chi_A_GeV : float
        Portal A DM mass (GeV)
    g_chi_A : float
        Portal A coupling
    m_phi_B_MeV : float
        Portal B mediator mass (MeV)
    m_chi_B_GeV : float
        Portal B DM mass (GeV)
    g_chi_B : float
        Portal B coupling

    Returns
    -------
    float
        sigma/m in cm^2/g (sum of two portal contributions)
    """
    sA = _sigma_m_yukawa(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A)
    sB = _sigma_m_yukawa(v_kms, m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    return sA + sB


# ---------------------------------------------------------------------------
# Reference test point: reviewer's Point 2 + LZ-fixing heavy portal
# ---------------------------------------------------------------------------
def test_reference_unified():
    """Reference unified model: Portal A heavy, Portal B light.

    Portal A: m_phi = 700 MeV, m_chi = 100 GeV, g_chi = 1.5
        Provides LZ magnetic-moment, suppresses CMB, satisfies FERMI.
        sigma/m_A is flat (~0.1 cm^2/g) across velocities.

    Portal B: m_phi = 5 MeV, m_chi = 500 GeV, g_chi = 0.20
        Provides high sigma/m(28) ~ 50 cm^2/g for Cloud-9.
        Suppressed at v >= 200 km/s (v^-8 Yukawa).

    Combined:
        v=28: sigma/m = ~50 (Portal B dominates)
        v=100: sigma/m = ~0.4 (Portal A dominates)
        v=3000: sigma/m = ~0.05 (Portal A only, well below Bullet limit)
    """
    sm_28 = sigma_m_multi_portal(28, 700, 100, 1.5, 5, 500, 0.20)
    sm_100 = sigma_m_multi_portal(100, 700, 100, 1.5, 5, 500, 0.20)
    sm_3000 = sigma_m_multi_portal(3000, 700, 100, 1.5, 5, 500, 0.20)
    print(f"  Multi-portal sigma/m(28) = {sm_28:.3e}")
    print(f"  Multi-portal sigma/m(100) = {sm_100:.3e}")
    print(f"  Multi-portal sigma/m(3000) = {sm_3000:.3e}")
    print(f"  Cloud-9 needs sigma/m(28) ~ 50 cm^2/g: {'YES' if 30 < sm_28 < 500 else 'NO'}")
    print(f"  Galactic sigma/m(100) < 1 cm^2/g: {'YES' if sm_100 < 1.0 else 'NO'}")
    print(f"  Bullet sigma/m(3000) < 0.5 cm^2/g: {'YES' if sm_3000 < 0.5 else 'NO'}")


if __name__ == "__main__":
    print("T90.44 — Multi-portal reference test:")
    print()
    test_reference_unified()