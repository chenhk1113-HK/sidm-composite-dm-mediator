"""
T110.1A — Near-threshold RSIDM parameter mapping.

Per Chu, Garcia-Cely, Murayama 2019 (PRL 122, 071103), Eq. 2:

    sigma(v) = sigma_0 + 4*pi*S / (m_red * E(v)) * Gamma(v)^2/4 / [(E(v) - E(v_R))^2 + Gamma(v)^2/4]

where:
  E(v) = (1/2) m_red v^2 = (1/4) m_chi v^2 (for equal-mass, reduced mass = m_chi/2)
  v_R is the resonance velocity, defined by E(v_R) = m_R - 2*m_chi
        (i.e., the dark photon mass m_R is close to 2*m_chi for near-threshold)
  Gamma(v) = m_R * gamma * v^(2L+1), L = 0 (S-wave) or 1 (P-wave)
  gamma ~ O(1) coupling parameter
  S = (2*J_R + 1) / (2*J_DM + 1)^2  (symmetry factor; ~1 for typical models)

The detuning parameter is:
    delta = m_R / m_chi - 2  (= v_R^2 / 4 from kinematics)

For "near-threshold" we need delta << 1 (or delta < 0, i.e., bound state).
The cross-section rises sharply with v in this regime.

This module maps parameter space (m_chi, delta, gamma, sigma_0) to sigma/m(v)
and identifies regions satisfying:
  Cloud-9: sigma/m(v=28) >= 100 cm^2/g
  dSph:    sigma/m(v=30) < 0.2 cm^2/g
  SPARC:   sigma/m(v=100) in [0.05, 0.5] cm^2/g

NOTE: This is T110.1A — literature + parameter mapping. No multi-channel fit yet.
That comes in T110.3.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass


@dataclass
class RSIDMParams:
    """Near-threshold RSIDM parameters."""
    m_chi_GeV: float  # DM mass
    delta: float  # m_R/m_chi - 2 (detuning; < 0 for below-threshold)
    gamma: float  # coupling ~ O(1)
    sigma_0: float  # background cross-section in cm^2/g
    L: int = 0  # orbital angular momentum (0 = S-wave, 1 = P-wave)
    S: float = 1.0  # symmetry factor


def v_R_from_delta(delta: float, m_chi_GeV: float) -> float:
    """Compute resonance velocity v_R from detuning delta = m_R/m_chi - 2.

    Kinematics: E(v_R) = m_R - 2*m_chi = delta * m_chi
    E(v) = (1/2) m_red v^2 = (1/4) m_chi v^2  [for equal mass]
    So (1/4) m_chi v_R^2 = delta * m_chi
        v_R^2 = 4 * delta
        v_R = 2 * sqrt(delta)  (in natural units, v in c)

    But we want v in km/s. For m_chi ~ GeV:
    E_R = delta * m_chi * c^2  (in eV if m_chi in GeV)
    v_R^2 = 4 * E_R / m_chi (in c^2 units)
        v_R = c * sqrt(4 * delta) = 2 * c * sqrt(delta)

    For delta = 10^-7 and m_chi ~ 0.5-10 GeV, v_R ~ 10-100 km/s.
    """
    if delta <= 0:
        return 0.0  # below-threshold (bound state)
    c_km_s = 2.998e5  # c in km/s
    return 2 * c_km_s * np.sqrt(delta)


def gamma_v(v_kms: float, m_R_GeV: float, gamma_coupling: float, L: int) -> float:
    """Width Gamma(v) = m_R * gamma * v^(2L+1) (Chu+ Eq. 4).

    Note: v is in natural units here. Need to be careful about units.
    For L=0: Gamma(v) = m_R * gamma (constant in v)
    For L=1: Gamma(v) = m_R * gamma * v^2 (P-wave suppression at low v)
    """
    # m_R in natural units (GeV); v in units of c
    return m_R_GeV * gamma_coupling * v_kms ** (2 * L + 1)


def sigma_m_near_threshold(
    v_kms: float,
    p: RSIDMParams,
) -> float:
    """Compute sigma/m(v) for near-threshold RSIDM (Chu+ Eq. 2).

    sigma(v) = sigma_0 + (4*pi*S / (m_red * E(v))) * (Gamma(v)^2 / 4) / [(E(v) - E(v_R))^2 + Gamma(v)^2/4]

    Then convert sigma(v) [in natural units] to sigma/m [in cm^2/g].

    Args:
        v_kms: relative velocity in km/s
        p: RSIDMParams

    Returns:
        sigma/m in cm^2/g
    """
    # Kinematics
    c = 2.998e5  # km/s
    v_c = v_kms / c  # v in units of c
    m_chi_eV = p.m_chi_GeV * 1e9  # m_chi in eV
    m_red_GeV = p.m_chi_GeV / 2.0  # reduced mass for equal-mass scattering
    m_R_GeV = p.m_chi_GeV * (2.0 + p.delta)  # resonance mass

    # Energy in CM frame
    E_eV = 0.5 * m_red_GeV * 1e9 * v_c ** 2  # in eV
    E_R_eV = p.delta * m_chi_eV  # E(v_R) = delta * m_chi * c^2

    # Width
    Gamma_eV = gamma_v(v_c, m_R_GeV, p.gamma, p.L) * 1e9  # in eV
    Gamma_half = Gamma_eV / 2.0

    # Resonance term (Chu+ Eq. 2)
    # sigma_res = 4*pi*S / (m_red * E) * (Gamma/2)^2 / [(E - E_R)^2 + (Gamma/2)^2]
    if E_eV <= 0:
        return p.sigma_0
    sigma_res_natural = (
        4 * np.pi * p.S / (m_red_GeV * E_eV / 1e9)  # m_red in GeV, E in GeV
        * Gamma_half ** 2
        / ((E_eV - E_R_eV) ** 2 + Gamma_half ** 2)
    )
    # Convert natural units (1/GeV^2) to cm^2/g
    # 1 GeV^-2 = (hbar*c)^2 fm^2 = 0.197^2 fm^2 = 0.0389 fm^2
    # 1 fm^2 = 1e-26 cm^2
    # So 1 GeV^-2 = 3.89e-28 cm^2
    sigma_res_cm2_per_g = sigma_res_natural * 3.89e-28 / (p.m_chi_GeV * 1.783e-24)

    return p.sigma_0 + sigma_res_cm2_per_g


def find_parameters_for_cloud9_dsph(
    m_chi_GeV: float = 0.5,
    cloud9_v: float = 28.0,
    cloud9_target: float = 100.0,
    dsph_v: float = 30.0,
    dsph_limit: float = 0.2,
) -> dict:
    """Find parameters that satisfy Cloud-9 + dSph simultaneously.

    Returns dict with best (delta, gamma, sigma_0) and resulting sigma/m curve.
    """
    # Scan delta from 10^-8 to 10^-5 (v_R from ~6 to ~190 km/s)
    deltas = np.logspace(-8, -5, 30)
    gammas = np.logspace(-4, -1, 20)
    sigma_0s = np.logspace(-3, 1, 20)

    best = None
    best_score = float("inf")

    for delta in deltas:
        v_R = v_R_from_delta(delta, m_chi_GeV)
        if v_R < 5 or v_R > 100:
            continue  # outside interesting range
        for gamma in gammas:
            for sigma_0 in sigma_0s:
                p = RSIDMParams(m_chi_GeV=m_chi_GeV, delta=delta, gamma=gamma, sigma_0=sigma_0)
                sm_cloud9 = sigma_m_near_threshold(cloud9_v, p)
                sm_dsph = sigma_m_near_threshold(dsph_v, p)
                sm_sparc = sigma_m_near_threshold(100.0, p)

                # Score: prefer to satisfy all 3 constraints
                score = 0
                if sm_cloud9 < cloud9_target:
                    score += (cloud9_target - sm_cloud9) / cloud9_target
                if sm_dsph > dsph_limit:
                    score += (sm_dsph - dsph_limit) / dsph_limit
                if not (0.05 <= sm_sparc <= 0.5):
                    score += abs(np.log10(sm_sparc / 0.2))

                if score < best_score:
                    best_score = score
                    best = {
                        "delta": delta,
                        "v_R": v_R,
                        "gamma": gamma,
                        "sigma_0": sigma_0,
                        "sm_cloud9": sm_cloud9,
                        "sm_dsph": sm_dsph,
                        "sm_sparc": sm_sparc,
                        "score": score,
                    }

    return best


if __name__ == "__main__":
    # Parameter scan
    print("T110.1A — Near-threshold RSIDM parameter scan")
    print("=" * 70)
    print()
    print("Looking for parameters satisfying:")
    print("  Cloud-9: sigma/m(v=28) >= 100 cm^2/g")
    print("  dSph:    sigma/m(v=30) < 0.2 cm^2/g  (Horigome+ 2025)")
    print("  SPARC:   sigma/m(v=100) in [0.05, 0.5] cm^2/g")
    print()

    for m_chi in [0.5, 1.0, 5.0, 10.0]:
        print(f"\n--- m_chi = {m_chi} GeV ---")
        best = find_parameters_for_cloud9_dsph(m_chi_GeV=m_chi)
        if best is None:
            print("  No solution found in scan range")
            continue
        print(f"  Best fit:")
        print(f"    delta = {best['delta']:.2e}  (v_R = {best['v_R']:.1f} km/s)")
        print(f"    gamma = {best['gamma']:.2e}")
        print(f"    sigma_0 = {best['sigma_0']:.2e} cm^2/g")
        print(f"    sigma/m(v=28)  = {best['sm_cloud9']:.2f} cm^2/g  (need >= 100)")
        print(f"    sigma/m(v=30)  = {best['sm_dsph']:.4f} cm^2/g  (need < 0.2)")
        print(f"    sigma/m(v=100) = {best['sm_sparc']:.4f} cm^2/g  (need 0.05-0.5)")
        print(f"    Score: {best['score']:.3f}")
