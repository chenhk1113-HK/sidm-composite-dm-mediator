"""
T40 — Yukawa-potential velocity-dependent SIDM cross-section.

Background
----------
The T39 result (sigma/m_0 ~ 1.57 cm^2/g, a ~ 0.94, epsilon ~ 10^-54) is a
*fit* result. The free velocity power-law index a was used to absorb the
velocity dependence. The physical Yukawa cross-section has a *known*
velocity dependence given (m_phi, m_chi, g_chi), so a is NOT a free
parameter — it is DERIVED from the mediator Yukawa coupling.

This module implements the standard Yukawa cross-section in the Born
approximation. Reference: Feng+ 2009 (arXiv:0908.2996), Tulin+ Yu 2018
(RMP 90, 015004).

Cross-section (Born approximation, distinguishable particles):

    sigma_T(v) = (g_chi^4 * m_chi^2) / (8 pi * m_phi^4) * [L(s)]^2
    with L(s) = log(1 + s) / s,  s = (m_chi v / (sqrt(2) m_phi))^2

Asymptotics:
  - s -> 0  (low v): sigma_T -> g_chi^4 m_chi^2 / (8 pi m_phi^4).  Finite.
  - s -> ∞  (high v): sigma_T ~ log^2(s)/s^2.  Falls as ~ 1/v^4.

THIS IS THE ONLY VALID FORM. An earlier version of this file multiplied
sigma_T by `(1 + 1/(2 s))` claiming it was a "Roberts+ 2024 s<<1
correction"; that multiplier diverges as v->0 (1/(2s) ~ v^-2) and is NOT
in any published SIDM literature (Tulin+Yu 2018, Roberts+ 2024, Khrapak
2018). It was removed on 2026-08-17 (R12 P0-A) because it produced
unphysical sigma/m ~ 1e6 cm^2/g at v = 0.1 km/s. See commit fixing this
file.

Parametrization strategy:
  Fit parameters:  m_phi [MeV], m_chi [GeV], g_chi
  Derived:         sigma/m_0 at v_ref=100 km/s, a (velocity power-law slope)
  Output:          (sigma_m_0, a)

The point of T40 (not a fit) is to give the NEXT tests (T41, T42) a
*physical* mapping from (m_phi, m_chi, g_chi) to (sigma_m_0, a) so we can
put the mediator on the experimental exclusion plots.

Verification
------------
    python t40_yukawa_sigma_m.py
runs a smoke test over a (m_phi, m_chi) grid and prints (sigma_m_0, a).
"""
from __future__ import annotations
import numpy as np
from pathlib import Path
import sys

# Constants
M_PROTON_GEV = 0.938272  # GeV
GEV_TO_GRAM = 1.7826619e-24  # 1 GeV = 1.7826619e-24 g
HBAR_C_MEV_CM = 1.9732698e-11  # MeV * cm
C_KMS = 299792.458  # km/s

# Reference velocity (galactic scale)
V_REF_KMS = 100.0


def beta_phi(v_kms: float, m_phi_MeV: float, m_chi_GeV: float) -> float:
    """Molière parameter (resonance strength):
    beta_phi = (m_chi v) / (sqrt(2) m_phi).  Dimensionless.
    v in km/s, m_phi in MeV, m_chi in GeV.
    """
    # Convert m_chi v to MeV (natural units: hbar c = 197.327 MeV fm)
    m_chi_MeV = m_chi_GeV * 1000.0
    beta = (m_chi_MeV * v_kms / C_KMS) / (np.sqrt(2.0) * m_phi_MeV)
    return beta


def sigma_T_cm2(v_kms: float, m_phi_MeV: float, m_chi_GeV: float, g_chi: float) -> float:
    """Transfer cross-section sigma_T in cm^2 (Born approximation).

    Ref: Feng+ 2009 Eq. 5 / Tulin+Yu 2018 (RMP 90, 015004) Eq. (2.14).
        sigma_T = (g_chi^4 m_chi^2) / (8 pi m_phi^4) * [L(s)]^2
        with L(s) = log(1 + s) / s
        s = [m_chi v / (sqrt(2) m_phi)]^2 = beta_phi^2

    Distinguishable fermions in the Born limit. Identical-particle
    symmetrization is NOT applied; the user (or caller) should multiply
    by 4 or by the proper identical-fermion factor where relevant.

    Implementation note (R12 P0-A fix): an earlier `* (1 + 1/(2 s))`
    "correction" was removed; it diverged as v->0 (1/(2s) ~ v^-2). The
    bare Born form has the correct asymptotes:
      - v -> 0:  sigma_T plateaus at g^4 m^2 / (8 pi m_phi^4).
      - v -> ∞:  sigma_T falls as (log s)^2 / s^2 ~ v^-4.
    """
    beta = beta_phi(v_kms, m_phi_MeV, m_chi_GeV)
    s = beta ** 2
    if s <= 0:
        return 0.0
    L = np.log(1.0 + s) / s  # log(1+s)/s
    m_chi_MeV = m_chi_GeV * 1000.0
    prefactor_natural = (g_chi ** 4) * (m_chi_MeV ** 2) / (8.0 * np.pi * m_phi_MeV ** 4)
    sigma_cm2 = prefactor_natural * (HBAR_C_MEV_CM ** 2) * L ** 2
    return float(sigma_cm2)


# Legacy alias. The original `sigma_T_with_m_low_correction` applied a
# bogus `(1 + 1/(2 s))` factor that diverged as v->0; it was removed.
# Some callers (t43, t46) still reference this name. We alias to the
# clean Born form. Removing the alias entirely would break those modules;
# removing the correction is the actual fix.
sigma_T_with_m_low_correction = sigma_T_cm2


def sigma_m_cm2_per_g(v_kms: float, m_phi_MeV: float, m_chi_GeV: float,
                       g_chi: float) -> float:
    """sigma/m in cm^2/g.

    sigma_m = sigma_T(v) / m_chi [cm^2 / GeV]  -->  convert to cm^2/g.

    Uses the clean Born form `sigma_T_cm2`. The legacy alias
    `sigma_T_with_m_low_correction` (R12 P0-A removed) is preserved for
    backward compatibility but routed to the same function.
    """
    sT = sigma_T_cm2(v_kms, m_phi_MeV, m_chi_GeV, g_chi)
    sigma_m_cm2_per_GeV = sT / m_chi_GeV
    return sigma_m_cm2_per_GeV * (1.0 / GEV_TO_GRAM)


def power_law_slope(m_phi_MeV: float, m_chi_GeV: float, v_lo_kms: float = 10.0,
                     v_hi_kms: float = 1000.0) -> float:
    """Velocity power-law index a such that sigma/m(v) ~ (v/v_ref)^(-a).

    Computed numerically by log-slope of sigma_m at v_ref=100 km/s.
    """
    sm_lo = sigma_m_cm2_per_g(v_lo_kms, m_phi_MeV, m_chi_GeV, g_chi=1.0)
    sm_hi = sigma_m_cm2_per_g(v_hi_kms, m_phi_MeV, m_chi_GeV, g_chi=1.0)
    if sm_lo <= 0 or sm_hi <= 0:
        return 0.0
    a = (np.log10(sm_lo) - np.log10(sm_hi)) / (np.log10(v_lo_kms) - np.log10(v_hi_kms))
    return float(a)


def g_chi_to_match_sigma_m_0(target_sigma_m_0: float, m_phi_MeV: float,
                               m_chi_GeV: float, v_ref_kms: float = V_REF_KMS) -> float:
    """Given a target sigma/m_0 at v_ref, return the g_chi that produces it.

    Used by the joint fit: we have a sigma/m_0 from data, and we solve
    for g_chi such that the Yukawa cross-section at v_ref matches it.

    Returns None if no positive g_chi exists (e.g., mediator mass too low).
    """
    sm_unit = sigma_m_cm2_per_g(v_ref_kms, m_phi_MeV, m_chi_GeV, g_chi=1.0)
    if sm_unit <= 0:
        return None
    # sigma_m_0 = sm_unit * g_chi^4  →  g_chi = (sigma_m_0 / sm_unit)^0.25
    g_chi = (target_sigma_m_0 / sm_unit) ** 0.25
    return float(g_chi)


def yaml_summary(m_phi_MeV: float, m_chi_GeV: float, g_chi: float,
                  v_ref_kms: float = V_REF_KMS) -> dict:
    """Full physics summary at one mediator point."""
    sm_0 = sigma_m_cm2_per_g(v_ref_kms, m_phi_MeV, m_chi_GeV, g_chi)
    sm_10 = sigma_m_cm2_per_g(10.0, m_phi_MeV, m_chi_GeV, g_chi)
    sm_1000 = sigma_m_cm2_per_g(1000.0, m_phi_MeV, m_chi_GeV, g_chi)
    a = power_law_slope(m_phi_MeV, m_chi_GeV)
    beta_at_vref = beta_phi(v_ref_kms, m_phi_MeV, m_chi_GeV)
    return {
        "m_phi_MeV": m_phi_MeV,
        "m_chi_GeV": m_chi_GeV,
        "g_chi": g_chi,
        "sigma_m_at_v=100_km/s": sm_0,
        "sigma_m_at_v=10_km/s": sm_10,
        "sigma_m_at_v=1000_km/s": sm_1000,
        "power_law_a": a,
        "beta_phi_at_vref": beta_at_vref,
        "regime": "BORN (s<<1)" if beta_at_vref < 0.1 else "CLASSICAL (s>>1)" if beta_at_vref > 3 else "INTERMEDIATE",
    }


if __name__ == "__main__":
    print("=" * 80)
    print("T40 — Yukawa velocity-dependent sigma/m module (smoke test)")
    print("=" * 80)
    print(f"sigma_T units check: m_chi=40 GeV, m_phi=10 MeV, g_chi=0.1, v=100 km/s")
    print(f"  sigma_T = {sigma_T_cm2(100.0, 10.0, 40.0, 0.1):.3e} cm^2")

    # Test points: scan a (m_phi, m_chi) grid and check sigma_m_0 + a
    print("\nGrid scan: (m_phi_MeV, m_chi_GeV) → (sigma_m_0, a) at g_chi=0.1")
    print(f"{'m_phi [MeV]':>12} {'m_chi [GeV]':>12} {'sigma_m @100 kms':>18} {'a':>8} {'regime':>14}")
    for m_phi in [1.0, 10.0, 100.0, 1000.0, 10000.0]:
        for m_chi in [10.0, 40.0, 100.0]:
            s = yaml_summary(m_phi, m_chi, 0.1)
            print(f"{m_phi:>12.2f} {m_chi:>12.2f} {s['sigma_m_at_v=100_km/s']:>18.3e} "
                  f"{s['power_law_a']:>8.3f} {s['regime']:>14}")

    # Solve for g_chi to match T39 sigma_m_0 = 1.57 cm^2/g at m_phi = 10 MeV, m_chi = 40 GeV
    print("\nMatching T39 sigma_m_0 = 1.57 cm^2/g:")
    for m_phi in [10.0, 100.0, 1000.0]:
        for m_chi in [10.0, 40.0, 100.0]:
            g = g_chi_to_match_sigma_m_0(1.57, m_phi, m_chi)
            if g is None:
                print(f"  m_phi={m_phi:>6.1f} MeV, m_chi={m_chi:>5.1f} GeV: NO g_chi (sigma_m too small at g_chi=1)")
            else:
                sm = sigma_m_cm2_per_g(100.0, m_phi, m_chi, g)
                a = power_law_slope(m_phi, m_chi)
                print(f"  m_phi={m_phi:>6.1f} MeV, m_chi={m_chi:>5.1f} GeV: g_chi={g:.4f}, "
                      f"sigma_m_0={sm:.3f} cm^2/g, a={a:.3f}")
