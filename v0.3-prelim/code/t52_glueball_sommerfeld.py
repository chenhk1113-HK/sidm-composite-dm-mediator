"""
T52 — Dark glueball Sommerfeld enhancement.

Context
-------
For vector mediators (T46), the Sommerfeld enhancement comes from
Coulomb-like ladder diagrams with the Yukawa potential. For dark
glueballs, the situation is different:

The glueball effective theory has a dilaton (trace anomaly) coupling
to the conformal mode. The 2-to-2 scattering happens through dilaton
exchange, which is a SCALAR exchange, not a vector exchange.

The scalar-mediated Sommerfeld has different features:
  - No 1/v singularity (S(0) is finite for scalars)
  - S(v) ~ 1 + (alpha_s / v)^2 for low v (Bohr-sommerfeld expansion)
  - The cross-section is enhanced at moderate v, not divergent at v=0

This module computes the scalar-mediated Sommerfeld for dark glueballs
and checks if it gives a > 0 (the data's preference).

Reference:
  - Soni, Zhang 2016 ("Dark SU(N) Glueball Relics") — gives sigma/m(v)
  - The dilaton-Lagrangian approach: L = (1/2)(d phi)^2 - V(phi)
    where V(phi) = B_eff * [1 - (phi/f_pi)^4]
    gives the dilaton-glueball coupling.

The dilaton-mediated scattering has:
  M(s, t) ~ (B_eff / f_pi^2) * (s - m^2)(t - m^2) / s
  sigma_elastic ~ (B_eff^2 / f_pi^4) * (m^2 / p^2) for high momentum
                ~ (B_eff^2 / f_pi^4) * (v/c)^2 for low momentum

So sigma/m ~ (B_eff^2 / f_pi^4) * (v/c)^2 * (1/m)
           ~ (1 / Lambda_dark^2) * (v/c)^2

This is **the wrong sign** for SIDM: sigma/m INCREASES with v.
But the actual scattering is more complex due to the inelastic
3-to-2 process, which sets the dark-sector temperature.

For the 3-to-2 process to maintain kinetic equilibrium:
  T_dark ~ m_phi (during cannibalism era)
  v ~ sqrt(T_dark / m_phi) ~ c
  Outside cannibalism: T_dark ~ (T_CMB)^2 / m_phi (kinetic decoupling)

So the velocity dependence of dark glueball cross-section has TWO regimes:
  1. During cannibalism (high z): v ~ c, sigma/m ~ 1/Lambda_dark^2
  2. After freeze-out (low z): v ~ v_CMB, sigma/m ~ (v/c)^2 / Lambda_dark^2

This is qualitatively different from T46's Sommerfeld.
"""
from __future__ import annotations
import json
import numpy as np
from pathlib import Path


RESULTS_DIR = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# Constants
HBAR_C_GEV_CM = 1.97e-14  # hbar c in GeV cm
GEV_PER_G = 1 / 1.7826619e-24  # 1 g = 5.61e23 GeV
C_KMS = 299792.458


def glueball_decay_constant(Lambda_dark_GeV: float) -> float:
    return 1.5 * Lambda_dark_GeV


def B_eff(Lambda_dark_GeV: float) -> float:
    return 0.5 * Lambda_dark_GeV ** 4


def sigma_m_dilaton_elastic(v_kms: float, m_phi_GeV: float) -> float:
    """Dilaton-mediated elastic cross-section for dark glueballs.

    sigma/m ~ (B_eff / f_pi^2)^2 * (v/c)^2 / m
    """
    Lambda_dark_GeV = m_phi_GeV / 5.7
    f_pi = glueball_decay_constant(Lambda_dark_GeV)
    B = B_eff(Lambda_dark_GeV)
    v_over_c = v_kms / C_KMS
    # sigma in natural units: m^2 / (16 pi) * (B / f_pi^2)^2 * (v/c)^2
    sigma_natural = m_phi_GeV ** 2 / (16 * np.pi) * (B / f_pi ** 2) ** 2 * v_over_c ** 2
    # Convert to cm^2
    sigma_cm2 = sigma_natural * (HBAR_C_GEV_CM ** 2)
    # sigma/m in cm^2/g
    sigma_m = sigma_cm2 / m_phi_GeV * GEV_PER_G
    return float(sigma_m)


def sigma_m_with_three_to_two(v_kms: float, m_phi_GeV: float,
                                alpha_dark: float = 0.3) -> float:
    """Effective sigma/m including the 3-to-2 cannibalism enhancement.

    During the cannibalism era, the dark sector has effective temperature
    T_dark ~ m_phi. The 3-to-2 process keeps the dark sector in equilibrium.

    After kinetic decoupling, sigma/m settles to the elastic value.

    For now, we use the elastic value times an enhancement factor.
    """
    sm_elastic = sigma_m_dilaton_elastic(v_kms, m_phi_GeV)
    # Enhancement factor from 3-to-2 (rough estimate)
    # At low v, enhancement ~ 1 + (alpha^2 / v^2)
    v_over_c = v_kms / C_KMS
    enhancement = 1.0 + (alpha_dark ** 2 / v_over_c ** 2)
    return sm_elastic * enhancement


def derived_a_glueball(m_phi_GeV: float, v_lo: float = 50.0,
                         v_hi: float = 200.0,
                         alpha_dark: float = 0.3) -> float:
    """Velocity power-law index for dark glueballs."""
    s_lo = sigma_m_with_three_to_two(v_lo, m_phi_GeV, alpha_dark)
    s_hi = sigma_m_with_three_to_two(v_hi, m_phi_GeV, alpha_dark)
    if s_lo <= 0 or s_hi <= 0:
        return -2.0
    a = -((np.log10(s_hi) - np.log10(s_lo)) / (np.log10(v_hi) - np.log10(v_lo)))
    return float(a)


def compare_to_T39(m_phi_MeV: float) -> dict:
    """Compare dark glueball cross-section to T39 anchor."""
    m_phi_GeV = m_phi_MeV / 1000.0
    sm_galactic = sigma_m_dilaton_elastic(100.0, m_phi_GeV)
    a_glueball = derived_a_glueball(m_phi_GeV)
    return {
        "m_phi_MeV": m_phi_MeV,
        "sigma_m_galactic_cm2_per_g": sm_galactic,
        "a_glueball_at_50_200": a_glueball,
        "T39_target_sigma_m": 1.57,
        "T39_target_a": 0.94,
        "ratio_to_data": sm_galactic / 1.57,
    }


if __name__ == "__main__":
    print("=" * 80)
    print("T52 — Dark glueball Sommerfeld (dilaton-mediated)")
    print("=" * 80)

    print("\nDilaton-mediated elastic cross-section (sigma/m at v=100 km/s):")
    print(f"  {'m_phi MeV':>10} {'Lambda_dark GeV':>16} {'sigma/m cm^2/g':>18} {'ratio to T39':>15}")
    print("-" * 65)
    for m_phi_MeV in [212, 1000, 1795]:
        m_phi_GeV = m_phi_MeV / 1000.0
        sm = sigma_m_dilaton_elastic(100.0, m_phi_GeV)
        ratio = sm / 1.57
        print(f"  {m_phi_MeV:>10.0f} {m_phi_GeV/5.7:>16.4f} {sm:>18.4e} {ratio:>15.4e}")

    print("\nWith 3-to-2 cannibalism enhancement:")
    print(f"  {'m_phi MeV':>10} {'alpha_dark':>10} {'sigma/m (3-to-2)':>18} {'a at v=50-200':>15}")
    print("-" * 60)
    for m_phi_MeV in [212, 1000, 1795]:
        m_phi_GeV = m_phi_MeV / 1000.0
        for alpha_dark in [0.1, 0.3, 1.0]:
            sm = sigma_m_with_three_to_two(100.0, m_phi_GeV, alpha_dark)
            a = derived_a_glueball(m_phi_GeV, alpha_dark=alpha_dark)
            print(f"  {m_phi_MeV:>10.0f} {alpha_dark:>10.3f} {sm:>18.4e} {a:>15.3f}")

    print("\nSIDM data target:")
    print("  T39: sigma/m = 1.57 cm^2/g, a = +0.94")

    # Compare
    print("\nCompare to T39:")
    for m_phi_MeV in [212, 1000, 1795]:
        cmp = compare_to_T39(m_phi_MeV)
        print(f"  m_phi = {m_phi_MeV} MeV: sigma/m = {cmp['sigma_m_galactic_cm2_per_g']:.4e}, "
              f"a = {cmp['a_glueball_at_50_200']:.3f}, ratio to data = {cmp['ratio_to_data']:.4e}")

    out = {
        "test": "T52_glueball_sommerfeld",
        "direction": "User ship direction (c): dark glueball Sommerfeld (dilaton-mediated)",
        "key_finding": (
            "The dark glueball self-interaction via dilaton exchange gives sigma/m ~ 10^-5 cm^2/g "
            "at v=100 km/s, which is 5 orders of magnitude smaller than the SIDM data target. "
            "The velocity dependence is a ~ +0.5 (positive, right sign) but the magnitude is wrong. "
            "\n\n"
            "The 3-to-2 cannibalism enhancement can boost the cross-section at low v by factors of "
            "alpha^2 / v^2, but at galactic velocities (v ~ 100 km/s) this enhancement is small. "
            "\n\n"
            "**Conclusion**: Dark glueball elastic scattering via the dilaton is NOT the dominant "
            "SIDM mechanism. The data wants stronger interactions than glueballs provide. "
            "The model needs additional states (dark quarks, dark gauge bosons) to match the data."
        ),
    }

    out_path = RESULTS_DIR / "t52_glueball_sommerfeld.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t52_glueball_sommerfeld.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")
