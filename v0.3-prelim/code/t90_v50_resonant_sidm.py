#!/usr/bin/env python
"""
T90.50 — Resonant Self-Interacting Dark Matter (RSIDM).

Per the user request, implement resonant SIDM with Breit-Wigner +
Sommerfeld enhancement. This is the most promising framework to
resolve the Cloud-9 vs Galactic tension.

References:
  Chu, Garcia-Cely, Murayama 2019 (PRL 122, 071103; arXiv:1805.03203)
  Kim, lee, Zhu 2021 (JHEP 10, 239; arXiv:2108.06278)
  Super-resonant DM 2025 (arXiv:2511.09306)
  Kamada 2023 (review slides)

Physics:
  Two contributions to sigma/m(v):
  1. Non-resonant background: sigma_0 (constant)
  2. Resonant piece: Breit-Wigner form
     sigma_res(v) = pi * S * (hbar c / E)^2 * (Gamma^2/4) / [(E - E_R)^2 + Gamma^2/4]
     where:
       E(v) = (m_chi / 4) * v^2  in CM frame (identical particles)
       E_R = resonance energy
       Gamma = width
       S = spin degeneracy factor (1/2 for spin-1/2 identical fermions)
  3. Sommerfeld enhancement at low v:
     S_somm(v) ~ pi*alpha/v_rel for Yukawa potential
     Enhances sigma at low v multiplicatively

  Combined:
  sigma_total(v) = sigma_0 * S_somm(v) + sigma_res(v)
  sigma/m = sigma_total(v) / m_chi_in_grams

Key insight for Cloud-9:
  At RELHIC v=28 km/s, m_chi=30 GeV:
    E(28) = (30 GeV / 4) * (28e5 cm/s / 3e10 cm/s)^2 = 6.5e1 eV = 65 eV
  So E_R ~ 65 eV puts resonance at Cloud-9 velocity
  At v=100: E = 830 eV (12x above resonance, sigma ~10^-3 of peak)
  At v=3000: E = 750 keV (10^4 above resonance, sigma ~10^-8 of peak)

Parameters:
  m_chi_GeV: DM mass (GeV)
  E_R_eV: resonance energy (eV)
  Gamma_R_eV: resonance width (eV)
  sigma_0_cm2_per_g: non-resonant background cross-section (cm^2/g)
  alpha_Y: dark Yukawa coupling (for Sommerfeld)
"""
from __future__ import annotations

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Physical constants
C_KMS = 2.998e5  # km/s
HBAR_C_KEV_CM = 1.973e-11  # hbar*c in keV*cm


def kinetic_energy_eV(v_kms: float, m_chi_GeV: float) -> float:
    """Compute CM frame kinetic energy in eV.

    For identical particles: E = (m_chi/2)/2 * v^2 = m_chi/4 * v^2
    """
    v_over_c = v_kms / C_KMS
    # E [GeV] = m_chi [GeV] * v^2/c^2 / 4
    E_GeV = m_chi_GeV * v_over_c ** 2 / 4.0
    return E_GeV * 1e9  # GeV -> eV


def sommerfeld_enhancement(v_kms: float, alpha_Y: float) -> float:
    """Sommerfeld enhancement factor for Yukawa potential.

    S(v) ~ pi*alpha/v for v/c << alpha (low-velocity regime)
    S(v) ~ 1 + O(alpha/v) for v/c >> alpha (perturbative)
    """
    v_over_c = v_kms / C_KMS
    if v_over_c < alpha_Y:
        return np.pi * alpha_Y / max(v_over_c, 1e-10)
    else:
        return 1.0 + np.pi * alpha_Y / v_over_c


def breit_wigner_sigma_cm2(
    v_kms: float,
    m_chi_GeV: float,
    E_R_eV: float,
    Gamma_eV: float,
    spin_factor: float = 0.5,
) -> float:
    """Breit-Wigner resonance cross-section in cm^2.

    sigma_BW = pi * S * (hbar c / E)^2 * (Gamma^2/4) / [(E-E_R)^2 + Gamma^2/4]

    At resonance: sigma_peak = pi * S * (hbar c / E_R)^2
    """
    E_eV = kinetic_energy_eV(v_kms, m_chi_GeV)

    # Convert hbar*c to eV*cm
    HC_eV_CM = HBAR_C_KEV_CM * 1e3  # 1.973e-8 eV*cm

    # Breit-Wigner formula
    numerator = np.pi * spin_factor * (HC_eV_CM / max(E_eV, 1e-10)) ** 2 * (Gamma_eV ** 2) / 4.0
    denominator = (E_eV - E_R_eV) ** 2 + (Gamma_eV ** 2) / 4.0

    sigma_cm2 = numerator / denominator
    return sigma_cm2


def sigma_m_resonant(
    v_kms: float,
    m_chi_GeV: float,
    E_R_eV: float,
    Gamma_R_eV: float,
    sigma_0_cm2_per_g: float,
    alpha_Y: float = 0.01,
) -> dict:
    """Compute total sigma/m with Breit-Wigner + Sommerfeld + background.

    Returns sigma_background, sigma_resonant, sigma_total, sigma/m, S_somm
    """
    # Sommerfeld enhancement
    S_somm = sommerfeld_enhancement(v_kms, alpha_Y)

    # Background (sigma_0 * Sommerfeld)
    sigma_background_cm2_per_g = sigma_0_cm2_per_g * S_somm

    # Resonant
    sigma_resonant_cm2 = breit_wigner_sigma_cm2(v_kms, m_chi_GeV, E_R_eV, Gamma_R_eV)

    # Convert sigma_resonant to per-mass units
    # sigma/m where m is DM particle mass in grams
    m_chi_g = m_chi_GeV * 1.783e-27 * 1e3  # GeV -> kg -> g
    sigma_resonant_per_m = sigma_resonant_cm2 / m_chi_g  # cm^2/g

    # Total
    sigma_m_total = sigma_background_cm2_per_g + sigma_resonant_per_m

    return {
        "sigma_background_cm2_per_g": sigma_background_cm2_per_g,
        "sigma_resonant_cm2": sigma_resonant_cm2,
        "sigma_resonant_per_m": sigma_resonant_per_m,
        "sigma_m_total": sigma_m_total,
        "S_sommerfeld": S_somm,
        "E_eV": kinetic_energy_eV(v_kms, m_chi_GeV),
    }


def evaluate_resonant_point(
    m_chi_GeV: float,
    E_R_eV: float,
    Gamma_R_eV: float,
    sigma_0_cm2_per_g: float,
    alpha_Y: float = 0.01,
) -> dict:
    """Evaluate sigma/m at Cloud-9, Galactic, Bullet velocities."""
    v_cloud9 = 28.0
    v_galaxy = 100.0
    v_bullet = 3000.0

    r_c9 = sigma_m_resonant(v_cloud9, m_chi_GeV, E_R_eV, Gamma_R_eV, sigma_0_cm2_per_g, alpha_Y)
    r_gal = sigma_m_resonant(v_galaxy, m_chi_GeV, E_R_eV, Gamma_R_eV, sigma_0_cm2_per_g, alpha_Y)
    r_bul = sigma_m_resonant(v_bullet, m_chi_GeV, E_R_eV, Gamma_R_eV, sigma_0_cm2_per_g, alpha_Y)

    return {
        "m_chi_GeV": m_chi_GeV,
        "E_R_eV": E_R_eV,
        "Gamma_R_eV": Gamma_R_eV,
        "sigma_0_cm2_per_g": sigma_0_cm2_per_g,
        "alpha_Y": alpha_Y,
        "sigma_m_Cloud9": r_c9["sigma_m_total"],
        "sigma_m_Galaxy": r_gal["sigma_m_total"],
        "sigma_m_Bullet": r_bul["sigma_m_total"],
        "S_somm_C9": r_c9["S_sommerfeld"],
        "E_C9_eV": r_c9["E_eV"],
        "Cloud9_OK": 30 < r_c9["sigma_m_total"] < 500,
        "Galaxy_OK": r_gal["sigma_m_total"] < 2.0,
        "Bullet_OK": r_bul["sigma_m_total"] < 0.5,
        "all_OK": (30 < r_c9["sigma_m_total"] < 500)
                  and (r_gal["sigma_m_total"] < 2.0)
                  and (r_bul["sigma_m_total"] < 0.5),
    }


def run_resonant_scan():
    """Scan E_R and Gamma_R to find Cloud-9 compatible points."""
    print("=" * 70)
    print("T90.50 — Resonant SIDM Parameter Scan (CORRECTED)")
    print("=" * 70)
    print()
    print("Target: resonance at Cloud-9 velocity (v=28 km/s)")
    print("E_R scale: ~65 eV for m_chi=30 GeV (CM frame KE at v=28)")
    print()

    # Reference: m_chi=30 GeV, E_R=65 eV (corrected)
    m_chi = 30.0

    print("Reference point: m_chi=30 GeV, E_R=65 eV, Gamma_R=1 eV, sigma_0=0.01")
    r_ref = evaluate_resonant_point(m_chi, 65.0, 1.0, 0.01, 0.01)
    print(f"  sigma/m(C9) = {r_ref['sigma_m_Cloud9']:.3e}")
    print(f"  sigma/m(Gal) = {r_ref['sigma_m_Galaxy']:.3e}")
    print(f"  sigma/m(Bul) = {r_ref['sigma_m_Bullet']:.3e}")
    print(f"  all_OK = {r_ref['all_OK']}")
    print()

    # Scan over E_R (in eV) and Gamma_R
    E_R_scan = [30.0, 50.0, 65.0, 100.0, 200.0, 500.0]  # eV
    Gamma_R_scan = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0]  # eV
    sigma_0_scan = [0.001, 0.01, 0.1, 0.5]  # cm^2/g

    print(f"{'E_R(eV)':10s} {'Gamma(eV)':10s} {'sigma_0':10s} {'C9':12s} {'Gal':12s} {'Bul':12s} {'OK':6s}")
    print("-" * 90)
    compatible = []
    for E_R in E_R_scan:
        for Gamma_R in Gamma_R_scan:
            for sig_0 in sigma_0_scan:
                r = evaluate_resonant_point(m_chi, E_R, Gamma_R, sig_0)
                if r["all_OK"]:
                    compatible.append(r)
                    print(f"{E_R:<10.1f} {Gamma_R:<10.2f} {sig_0:<10.4f} "
                          f"{r['sigma_m_Cloud9']:<12.2e} {r['sigma_m_Galaxy']:<12.2e} "
                          f"{r['sigma_m_Bullet']:<12.2e} {'YES':<6s}")
                elif r["sigma_m_Cloud9"] > 10 and r["sigma_m_Galaxy"] < 10:
                    print(f"{E_R:<10.1f} {Gamma_R:<10.2f} {sig_0:<10.4f} "
                          f"{r['sigma_m_Cloud9']:<12.2e} {r['sigma_m_Galaxy']:<12.2e} "
                          f"{r['sigma_m_Bullet']:<12.2e} {'close':<6s}")

    print()
    print(f"Cloud-9 compatible points: {len(compatible)}")
    if compatible:
        print()
        print("Top compatible points:")
        for r in compatible[:10]:
            print(f"  E_R={r['E_R_eV']:.1f} eV, Gamma_R={r['Gamma_R_eV']:.2f} eV, "
                  f"sigma_0={r['sigma_0_cm2_per_g']:.4f}: "
                  f"sm(C9)={r['sigma_m_Cloud9']:.2e}, sm(Gal)={r['sigma_m_Galaxy']:.2e}, "
                  f"sm(Bul)={r['sigma_m_Bullet']:.2e}")

    return compatible


if __name__ == "__main__":
    compatible = run_resonant_scan()