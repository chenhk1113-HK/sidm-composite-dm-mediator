"""
sashimi_per_galaxy.py — Per-galaxy σ/m posterior using SASHIMI-SIDM.

Per peer review (2026-08-10, Long-Term #2):
    "Replace the v0.3 SPARC saturation heuristic with full velocity-
     dependent fits on each of the 175 SPARC galaxies, using the
     publicly-available SASHIMI-SIDM code (arXiv:2403.16633) as the
     forward model."

What this module does:
    For each SPARC galaxy (or MW satellite), use the SASHIMI-SIDM
    parametric halo model to compute the predicted V_max(r) rotation
    curve for a given σ/m_0. Then compare to the observed rotation
    curve (from rotmod files). This gives a per-galaxy χ² for each
    (σ/m_0, a) pair, which we then marginalize over galaxy properties
    to get a joint σ/m posterior.

This is the in-house re-implementation of T10 — now using the
SASHIMI-SIDM parametric forward model rather than the saturation
heuristic.

References:
    - Ando, Horigome, Nadler, Yang, Yu 2025, JCAP02(2025)053,
      arXiv:2403.16633 (SASHIMI-SIDM)
    - Yang et al. 2024 (parametric SIDM model)
    - SPARC database (Lelli, McGaugh, Schombert 2016)
"""
from __future__ import annotations
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

from sashimi_parametric import (
    NFW_profile_params,
    vmax_from_profile,
    sigma_effective_per_m_chi,
    core_collapse_timescale_Gyr,
    Vmax_ratio,
    rmax_ratio,
    rho_s_ratio,
    r_s_ratio,
    r_c_ratio,
    formation_redshift,
    formation_time_Gyr,
    cdm_to_sidm_halo,
    T_UNIVERSE_GYR,
)


def V_SIDM(r_kpc: np.ndarray, rho_s_sidm: float, r_s_sidm: float, r_c_sidm: float,
            beta: float = 4.0, G_kpc_kms_Msun: float = 4.302e-6) -> np.ndarray:
    """SIDM rotation curve V²(r) for the parametric density profile.

    The SASHIMI-SIDM density profile (Eq. 2.11):
        ρ(r) = ρ_s / [(r^β + r_c^β)^(1/β) / r_s] / (r/r_s + 1)²

    For β = 4, this is a softened isothermal core (for r << r_c) attached
    to an NFW outer profile (for r >> r_c).

    To compute V²(r), integrate the density:
        M(<r) = 4π ∫₀^r ρ(r') r'² dr'
        V²(r) = G × M(<r) / r

    Parameters
    ----------
    r_kpc : np.ndarray
        Radii at which to evaluate V² (kpc).
    rho_s_sidm : float
        SIDM scale density (M_sun/kpc³).
    r_s_sidm : float
        SIDM scale radius (kpc).
    r_c_sidm : float
        Core radius (kpc).
    beta : float
        Profile steepness parameter (default 4 per SASHIMI-SIDM).
    G_kpc_kms_Msun : float
        Newton's constant in kpc (km/s)² / M_sun.

    Returns
    -------
    np.ndarray : V²(r) in (km/s)².
    """
    if r_c_sidm <= 0 or rho_s_sidm <= 0 or r_s_sidm <= 0:
        return np.zeros_like(r_kpc)

    r = np.asarray(r_kpc, dtype=float)
    # Dimensionless radius
    x = r / r_s_sidm
    # Numerator of the density at r (without ρ_s)
    num = np.power(r**beta + r_c_sidm**beta, 1.0 / beta)
    # Full density: ρ_s × r_s / num × 1/(x+1)²
    rho = rho_s_sidm * r_s_sidm / num / (x + 1)**2

    # Compute M(<r) by cumulative integration (trapezoidal)
    # Use finer integration grid for better accuracy
    r_fine = np.concatenate([
        np.linspace(0.001 * r_s_sidm, r_s_sidm, 100),
        np.linspace(r_s_sidm, r.max() * 1.1, 500) if r.max() > r_s_sidm else np.array([r.max()])
    ])
    r_fine = r_fine[r_fine <= r.max() * 1.5]
    x_fine = r_fine / r_s_sidm
    num_fine = np.power(r_fine**beta + r_c_sidm**beta, 1.0 / beta)
    rho_fine = rho_s_sidm * r_s_sidm / num_fine / (x_fine + 1)**2
    # Cumulative mass M(<r) = 4π ∫₀^r ρ(r') r'² dr' via trapezoid
    integrand_fine = 4 * np.pi * rho_fine * r_fine**2
    M_enclosed_fine = np.zeros_like(r_fine)
    M_enclosed_fine[1:] = np.cumsum(0.5 * (integrand_fine[1:] + integrand_fine[:-1]) *
                                     np.diff(r_fine))

    # Interpolate M(<r) at the requested radii
    M_at_r = np.interp(r, r_fine, M_enclosed_fine)

    # V²(r) = G × M(<r) / r
    # Handle r=0 safely
    V_squared = np.where(r > 0, G_kpc_kms_Msun * M_at_r / r, 0.0)
    return V_squared


def predict_rotation_curve_sashimi(
    r_kpc: np.ndarray,
    M_vir_Msun: float,
    c_vir: float,
    sigma_0_per_m_chi_cm2_per_g: float,
    w_kms: float = np.inf,
) -> np.ndarray:
    """Predict V²(r) for a SPARC galaxy using the SASHIMI-SIDM parametric model.

    Parameters
    ----------
    r_kpc : np.ndarray
        Radii at which to evaluate V² (kpc).
    M_vir_Msun : float
        Virial mass of the halo (M_sun).
    c_vir : float
        Virial concentration parameter.
    sigma_0_per_m_chi_cm2_per_g : float
        SIDM cross section amplitude (cm²/g).
    w_kms : float
        Velocity transition scale (km/s), inf for v-independent.

    Returns
    -------
    np.ndarray : V²(r) in (km/s)².
    """
    sidm = predict_sparc_satellite_compat(
        M_vir_Msun=M_vir_Msun,
        c_vir=c_vir,
        sigma_0_per_m_chi_cm2_per_g=sigma_0_per_m_chi_cm2_per_g,
        w_kms=w_kms,
    )
    return V_SIDM(
        r_kpc,
        rho_s_sidm=sidm["rho_s_sidm"],
        r_s_sidm=sidm["r_s_sidm"],
        r_c_sidm=sidm["r_c_sidm"],
    )


def predict_sparc_satellite_compat(
    M_vir_Msun: float,
    c_vir: float,
    sigma_0_per_m_chi_cm2_per_g: float,
    w_kms: float = np.inf,
    z_observation: float = 0.0,
) -> dict:
    """Wrapper around sashimi_parametric.cdm_to_sidm_halo for clarity."""
    z_f = formation_redshift(np.log10(M_vir_Msun))
    return cdm_to_sidm_halo(
        M_vir_Msun=M_vir_Msun,
        z_formation=z_f,
        c_vir=c_vir,
        z_observation=z_observation,
        sigma_0_per_m_chi_cm2_per_g=sigma_0_per_m_chi_cm2_per_g,
        w_kms=w_kms,
    )


def chi2_per_galaxy(
    r_obs: np.ndarray,
    V2_obs: np.ndarray,
    V2_err: np.ndarray,
    M_vir_Msun: float,
    c_vir: float,
    sigma_0_per_m_chi_cm2_per_g: float,
    w_kms: float = np.inf,
) -> float:
    """Compute χ² for one galaxy given SIDM parameters.

    Parameters
    ----------
    r_obs : np.ndarray
        Observed radii (kpc).
    V2_obs : np.ndarray
        Observed V² (km/s)².
    V2_err : np.ndarray
        V² uncertainties (km/s)².
    M_vir_Msun, c_vir : float
        Halo properties for this galaxy.
    sigma_0_per_m_chi_cm2_per_g, w_kms : float
        SIDM parameters.

    Returns
    -------
    float : χ² = Σ [(V²_obs - V²_pred) / V²_err]²
    """
    V2_pred = predict_rotation_curve_sashimi(
        r_obs, M_vir_Msun, c_vir,
        sigma_0_per_m_chi_cm2_per_g, w_kms,
    )
    chi2 = np.sum(((V2_obs - V2_pred) / V2_err)**2)
    return chi2


def load_sparc_galaxy(rotmod_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load a SPARC rotmod file.

    Returns
    -------
    (r_kpc, V_obs_kms, V_err_kms)
    """
    data = np.loadtxt(rotmod_path)
    r = data[:, 0]   # kpc
    V = data[:, 1]   # km/s (observed rotation velocity)
    V_err = data[:, 2]  # km/s (uncertainty)
    V2 = V**2
    # Error propagation: σ(V²) = 2 V σ(V)
    V2_err = 2 * V * V_err
    return r, V2, V2_err


if __name__ == "__main__":
    # Quick demo with a synthetic galaxy
    print("=== sashimi_per_galaxy.py demo ===\n")
    # Synthetic MW-like galaxy: V_max ~ 220 km/s, scale radius ~ 10 kpc
    r_test = np.array([1.0, 3.0, 5.0, 10.0, 15.0, 20.0])
    M_vir = 1e12  # M_sun (MW mass)
    c_vir = 12.0
    for sigma_0 in [1.0, 10.0, 100.0]:
        V2_pred = predict_rotation_curve_sashimi(
            r_test, M_vir, c_vir, sigma_0, w_kms=np.inf,
        )
        V_kms = np.sqrt(V2_pred)
        print(f"σ_0 = {sigma_0:>6.1f} cm²/g: V(r=10) = {V_kms[3]:.1f} km/s, V_max ≈ {V_kms.max():.1f}")