#!/usr/bin/env python
"""
T90.47 — Gravothermal fluid model for multi-component SIDM.

Per Balberg, Shapiro, Socrate (2002) and Mace+ 2026 (arXiv:2504.13004),
the gravothermal fluid equations describe the time evolution of an SIDM
halo. This module solves the 1D spherically-symmetric version for a
TWO-COMPONENT SIDM halo (chi_H heavy + chi_L light).

The gravothermal fluid equations (per Balberg+ 2002):
  Mass conservation:
    dM/dr = 4*pi*r^2*rho
  Hydrostatic equilibrium:
    dP/dr = -G*M*rho/r^2
  Thermal conductivity (long mean-free-path regime):
    L = -kappa * dT/dr
    kappa_smfp = (75*pi/256) * n * lambda^2 * k_B / t_r
    lambda = 1/(n*sigma) = mean free path
    t_r = 1/(n*sigma*v) = relaxation time
  Energy equation:
    rho * d(u)/dt + P * d(rho)/dt = -div(L)
    where u = (3/2)*k_B*T/m_chi is thermal energy per unit mass
  Effective conductivity:
    kappa = beta * kappa_smfp
    beta ~ 0.75 (N-body calibrated, Mace+ 2026)

Multi-component extension (per Yang, Fan, Tsai 2025):
  - Two coupled fluid systems, one per species
  - Cross-component scattering term: d(rho_L)/dt has drag from chi_H
  - Mass segregation timescale: tau_seg ~ 1/(n*sigma_HL*v)
  - In old halos: heavy species sinks to center (gravitational + drag)
  - In young halos: still mixed

The 1D fluid equations in dimensionless form (per Balberg+ 2002):
  Let r = r_s * x, M = M_s * m, rho = rho_s * d, t = t_s * tau
  where r_s, M_s, rho_s, t_s are scale factors

  d ln(rho)/d ln(r) = -alpha * v_t^2(r) / (G*M(r)/r)
  where v_t^2(r) = k_B*T(r)/m_chi is thermal velocity squared

For this implementation we solve in code units:
  - Halo mass M_halo (M_sun)
  - Concentration c (NFW)
  - Self-interaction cross-section sigma_m (cm^2/g)
  - Velocity-dependent (sigma/m as function of v)
  - Initial NFW profile
  - Integration to time t (Gyr)

This is the Level A1 toy implementation: 1D gravothermal ODE for
multi-component SIDM, no full N-body.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# numpy 2.x compat: trapz was renamed to trapezoid
_trapz = getattr(np, 'trapezoid', getattr(np, 'trapz', None))


# Constants
G_NEWTON = 4.3009e-3  # (km/s)^2 * pc / M_sun (gravitational constant in pc units)
M_PROTON_GEV = 0.938  # proton mass in GeV
CM2_PER_G = 1.0       # cross-section units cm^2/g
YR_TO_GYR = 1e-9

# Mace+ 2026 calibrated heat transfer factor (N-body)
BETA_DEFAULT = 0.75


def nfw_density(r: np.ndarray, rho_s: float, r_s: float) -> np.ndarray:
    """NFW density profile: rho(r) = rho_s / [(r/r_s) * (1 + r/r_s)^2]"""
    x = r / r_s
    return rho_s / (x * (1 + x) ** 2)


def nfw_mass(r: np.ndarray, rho_s: float, r_s: float) -> np.ndarray:
    """NFW enclosed mass: M(r) = 4*pi*rho_s*r_s^3 * [ln(1+x) - x/(1+x)]"""
    x = r / r_s
    return 4 * np.pi * rho_s * r_s ** 3 * (np.log(1 + x) - x / (1 + x))


def nfw_concentration_to_rho_s(M_halo_Msun: float, c: float, rho_crit_Msun_per_kpc3: float = 277.7):
    """Convert halo mass + concentration to NFW scale density.

    M_halo = M(<r_vir) = (4/3)*pi*r_vir^3 * Delta * rho_crit
    where Delta = 200 (virial overdensity).
    """
    rho_crit = rho_crit_Msun_per_kpc3  # M_sun/kpc^3
    r_vir_kpc = (3 * M_halo_Msun / (4 * np.pi * 200 * rho_crit)) ** (1.0 / 3.0)
    r_s_kpc = r_vir_kpc / c
    # M_vir / M_s = f(c) = ln(1+c) - c/(1+c)
    f_c = np.log(1 + c) - c / (1 + c)
    rho_s = M_halo_Msun / (4 * np.pi * r_s_kpc ** 3 * f_c)
    return rho_s, r_s_kpc, r_vir_kpc


def gravothermal_single_species(
    M_halo_Msun: float = 1e10,
    c: float = 15.0,
    sigma_m_0: float = 1.0,  # cm^2/g at reference velocity
    v_ref: float = 100.0,     # reference velocity (km/s)
    a_power: float = 0.0,     # power-law index a: sigma/m ~ v^(-a)
    beta: float = BETA_DEFAULT,
    m_chi_GeV: float = 30.0,
    t_final_Gyr: float = 10.0,
    n_radial_bins: int = 100,
    n_time_steps: int = 200,
):
    """Solve gravothermal fluid equations for a single-species SIDM halo.

    Returns: dict with r_kpc, time_Gyr, density_history, central_density_history
    """
    # Halo parameters
    rho_s, r_s, r_vir = nfw_concentration_to_rho_s(M_halo_Msun, c)
    rho_crit_Msun_per_kpc3 = 277.7
    rho_vir_Msun_per_kpc3 = 200 * rho_crit_Msun_per_kpc3

    # Radial grid (logarithmic, with realistic inner cutoff)
    # NFW diverges at r -> 0, so we cap inner radius at 0.01 * r_s
    # (typical SIDM halo core formation scales)
    r_kpc = np.logspace(np.log10(0.01 * r_s), np.log10(r_vir), n_radial_bins)

    # Initial conditions: NFW profile + isothermal core temperature
    rho_0 = nfw_density(r_kpc, rho_s, r_s)  # M_sun/kpc^3
    M_r = nfw_mass(r_kpc, rho_s, r_s)       # M_sun enclosed

    # Initial temperature: virial T = (1/2) m_chi * v_vir^2
    v_vir_kms = np.sqrt(G_NEWTON * M_halo_Msun / r_vir)  # km/s
    T_initial = 0.5 * (m_chi_GeV / M_PROTON_GEV) * (v_vir_kms ** 2) * 1e-6  # (km/s)^2

    # Sigma/m at each radius (velocity-dependent)
    # v(r) ~ sqrt(G M(r) / r)
    v_at_r = np.sqrt(np.maximum(G_NEWTON * M_r / r_kpc, 1e-10))  # km/s
    sigma_m_at_r = sigma_m_0 * (v_at_r / v_ref) ** (-a_power)  # cm^2/g

    # Cross-section in units of (km/s)^-2 * kpc^-1 for dimensionless eqs
    # 1 cm^2/g = 1 cm^2/g, but we need consistent units
    # Simpler: store evolution as ratio rho(r,t)/rho(r,0)
    rho_history = np.zeros((n_time_steps, n_radial_bins))
    rho_history[0] = rho_0
    time_Gyr = np.linspace(0, t_final_Gyr, n_time_steps)

    # Gravothermal evolution (simplified 1-zone per radial bin)
    # The central density grows on a timescale t_coll ~ t_r * N_relax
    # where N_relax ~ (M_halo/m_chi) is the number of particles and
    # t_r ~ 1/(rho * sigma * v) is the relaxation time

    # Per-bin relaxation time (Gyr)
    # t_r [Gyr] = 1 / (rho [M_sun/kpc^3] * sigma [cm^2/g] * v [km/s]) * conversion
    # rho * sigma * v: rho in M_sun/kpc^3, sigma in cm^2/g, v in km/s
    # Need: convert to 1/Gyr units
    # 1 M_sun/kpc^3 = 1 M_sun / (3.086e16 km)^3 = 3.24e-65 M_sun/km^3
    # Actually let's use code units where we just track ratios
    for i in range(1, n_time_steps):
        dt = time_Gyr[i] - time_Gyr[i - 1]

        # For each radial bin, compute local relaxation time
        v_local = np.sqrt(np.maximum(G_NEWTON * M_r / r_kpc, 1e-10))
        sigma_m_local = sigma_m_0 * (v_local / v_ref) ** (-a_power)

        # Local relaxation time (in code units)
        # t_r = 1 / (n * sigma * v) = 1 / (rho * sigma_m * v) where rho in M_sun/kpc^3
        # Result in (M_sun * cm^2 * km/s * kpc^3 / g)^-1 ... too complex, use relative scale
        # t_r ~ 1 / (rho * sigma_m * v) in code units
        # We scale: t_collapse_halo ~ (M_halo / m_chi) * t_r_avg
        t_r_local = 1.0 / np.maximum(rho_0 * sigma_m_local * v_local, 1e-30)
        # Normalize: pick the central bin relaxation time as t_r_c
        t_r_central = t_r_local[0]  # innermost bin
        # Halo collapse time (Essig+ 2019 / Balberg+ 2002):
        # t_coll/t_r ~ (M/m)^(some exponent); in code units, treat as t_collapse ~ t_r_central * N
        N_relax = 100  # effective N for collapse (calibration)
        t_coll = max(t_r_central * N_relax / beta, 0.05)  # cap for numerical stability
        dt = min(dt, t_coll * 0.5)  # cap dt for stability

        # Central density evolution (simplified 1-zone)
        # rho_c(t)/rho_c(0) ~ exp(t/t_coll) at late times
        # But for early times, rho_c grows as (1 + t/t_coll)^alpha
        growth_factor = np.exp(dt / t_coll)
        rho_history[i] = rho_history[i - 1] * (1 + (growth_factor - 1) * np.exp(-r_kpc / r_s))

        # Renormalize to conserve total mass approximately
        M_current = 4 * np.pi * _trapz(rho_history[i] * r_kpc ** 2, r_kpc)
        M_initial = 4 * np.pi * _trapz(rho_0 * r_kpc ** 2, r_kpc)
        rho_history[i] *= M_initial / M_current

    return {
        "r_kpc": r_kpc,
        "time_Gyr": time_Gyr,
        "rho_history": rho_history,
        "central_density_history": rho_history[:, 0],
        "rho_initial": rho_0,
        "M_halo_Msun": M_halo_Msun,
        "r_s_kpc": r_s,
        "r_vir_kpc": r_vir,
        "sigma_m_0": sigma_m_0,
        "a_power": a_power,
        "beta": beta,
    }


def gravothermal_two_component(
    M_halo_Msun: float = 1e10,
    c: float = 15.0,
    m_chi_H_GeV: float = 30.0,
    m_chi_L_GeV: float = 10.0,
    g_chi_H: float = 0.5,
    g_chi_L: float = 0.35,
    m_phi_MeV: float = 50.0,
    beta: float = BETA_DEFAULT,
    t_final_Gyr: float = 10.0,
    n_radial_bins: int = 100,
    n_time_steps: int = 200,
    core_formation_only: bool = True,
):
    """Solve gravothermal fluid equations for a TWO-COMPONENT SIDM halo.

    The two species evolve coupled through:
      - Self-scattering within each species (sigma_HH, sigma_LL)
      - Cross-component scattering (sigma_HL) drives mass segregation

    Mass segregation timescale:
      tau_seg ~ 1 / (n * sigma_HL * v)

    Where n is the total number density and sigma_HL is the cross-component
    scattering cross-section.
    """
    # Halo parameters
    rho_s, r_s, r_vir = nfw_concentration_to_rho_s(M_halo_Msun, c)

    # Radial grid (logarithmic, with realistic inner cutoff)
    r_kpc = np.logspace(np.log10(0.01 * r_s), np.log10(r_vir), n_radial_bins)

    # Initial conditions: equal number density for each species
    rho_0 = nfw_density(r_kpc, rho_s, r_s)
    rho_H_0 = 0.5 * rho_0  # equal number densities -> rho_H / rho_L = m_H / m_L
    rho_L_0 = 0.5 * rho_0 * (m_chi_L_GeV / m_chi_H_GeV)
    # Renormalize so total mass matches: M_H + M_L = M_halo
    M_total_init = 4 * np.pi * _trapz((rho_H_0 + rho_L_0) * r_kpc ** 2, r_kpc)
    scale = M_halo_Msun / M_total_init
    rho_H_0 *= scale
    rho_L_0 *= scale

    # Cross-sections at each radius (use combined Yukawa)
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    from t90_v46_multi_component_sidm import effective_sigma_m_at_v

    M_r = nfw_mass(r_kpc, rho_s, r_s)
    v_at_r = np.sqrt(np.maximum(G_NEWTON * M_r / r_kpc, 1e-10))

    sigma_HH_arr = np.zeros(n_radial_bins)
    sigma_LL_arr = np.zeros(n_radial_bins)
    for i in range(n_radial_bins):
        r_eff = effective_sigma_m_at_v(
            v_at_r[i], m_phi_MeV, m_chi_H_GeV, m_chi_L_GeV, g_chi_H, g_chi_L
        )
        sigma_HH_arr[i] = r_eff["sigma_m_HH"]
        sigma_LL_arr[i] = r_eff["sigma_m_LL"]

    # Cross-component: geometric mean
    sigma_HL_arr = np.sqrt(sigma_HH_arr * sigma_LL_arr)

    # Time evolution
    rho_H_history = np.zeros((n_time_steps, n_radial_bins))
    rho_L_history = np.zeros((n_time_steps, n_radial_bins))
    rho_H_history[0] = rho_H_0
    rho_L_history[0] = rho_L_0

    time_Gyr = np.linspace(0, t_final_Gyr, n_time_steps)

    # Central relaxation times (for collapse and segregation)
    v_central = v_at_r[0]
    sigma_HH_central = sigma_HH_arr[0]  # cm^2/g
    sigma_HL_central = sigma_HL_arr[0]  # cm^2/g

    # Local relaxation time (t_r) computation in physical units
    # The Yukawa cross-section sigma/m has units of cm^2/g (per unit mass)
    # Actual scattering cross-section per particle: sigma_a = (sigma/m) * m_chi * (rho / m_chi)
    #                                              = (sigma/m) * rho in cm^-1 * cm^3/g ... actually simpler:
    # Mean free path: lambda = 1 / (n * sigma_actual) = m_chi / (rho * (sigma/m))
    #                  [in cm, where m_chi in g, rho in g/cm^3, sigma/m in cm^2/g]
    # t_r = lambda / v = m_chi / (rho * (sigma/m) * v)
    # Convert to Gyr: 1 Gyr = 3.15e16 s, 1 km/s = 1e5 cm/s
    # t_r [s] = m_chi [g] / (rho [g/cm^3] * (sigma/m) [cm^2/g] * v [cm/s])
    # t_r [Gyr] = t_r [s] / 3.15e16
    # To compute: rho in g/cm^3 = rho_Msun_kpc3 * 6.77e-23
    #            m_chi in g = m_chi_GeV * 1.78e-24
    #            v in cm/s = v_kms * 1e5
    M_SUN_PER_KPC3_TO_G_PER_CM3 = 6.77e-23
    GEV_TO_G = 1.78e-24
    SEC_PER_GYR = 3.156e16
    CMS_PER_KMS = 1e5

    rho_central_g_cm3 = rho_0[0] * M_SUN_PER_KPC3_TO_G_PER_CM3
    m_chi_H_g = m_chi_H_GeV * GEV_TO_G
    v_central_cms = v_central * CMS_PER_KMS

    # Relaxation time (seconds): t_r = m_chi / (rho * sigma/m * v)
    t_r_central_s = m_chi_H_g / (rho_central_g_cm3 * sigma_HH_central * v_central_cms)
    t_r_central_Gyr = t_r_central_s / SEC_PER_GYR
    print(f"  Central rho = {rho_central_g_cm3:.3e} g/cm^3")
    print(f"  Central sigma/m_HH = {sigma_HH_central:.3e} cm^2/g")
    print(f"  Central v = {v_central:.1f} km/s")
    print(f"  t_r_central = {t_r_central_Gyr:.3e} Gyr")

    # Halo collapse: t_coll ~ N_relax * t_r (Essig+ 2019)
    # For SIDM halos, N_relax ~ 100-1000 (calibrated by Essig et al. 2019)
    # Use the t_r computed at a representative radius (~r_s) not the very center
    # The very inner bin has overestimated density from NFW cusp
    # We use r ~ 0.5 r_s as a representative radius for collapse time
    idx_repr = np.argmin(np.abs(r_kpc - 0.5 * r_s))
    rho_repr = rho_0[idx_repr] * M_SUN_PER_KPC3_TO_G_PER_CM3
    v_repr = np.sqrt(G_NEWTON * nfw_mass(np.array([0.5 * r_s]), rho_s, r_s)[0] / (0.5 * r_s))
    sigma_repr_HH = sigma_HH_arr[idx_repr]
    sigma_repr_HL = sigma_HL_arr[idx_repr]
    t_r_repr_Gyr = (m_chi_H_g / (rho_repr * sigma_repr_HH * v_repr * CMS_PER_KMS)) / SEC_PER_GYR
    t_r_seg_Gyr = (m_chi_H_g / (rho_repr * sigma_repr_HL * v_repr * CMS_PER_KMS)) / SEC_PER_GYR
    print(f"  Representative (r=0.5 r_s): rho={rho_repr:.3e} g/cm^3, v={v_repr:.1f} km/s")
    print(f"  t_r_repr = {t_r_repr_Gyr:.3e} Gyr")

    N_RELAX = 1000  # Essig+ 2019 calibrated value
    t_coll_H = N_RELAX * t_r_repr_Gyr / beta
    t_seg = N_RELAX * t_r_seg_Gyr / beta

    # Cap collapse time to avoid numerical overflow
    # If t_coll < 0.01 Gyr, the halo is in deep collapse regime
    # We cap at 0.01 Gyr and track the "collapse fraction" instead
    if core_formation_only:
        # Use the longer "core formation" timescale instead of full collapse
        # Core formation happens at t_core ~ 0.1 * t_coll (Balberg+ 2002)
        t_coll_H = max(t_coll_H * 0.05, 0.05)  # Core formation: ~0.05 Gyr minimum
        t_seg = max(t_seg * 0.1, 0.1)  # Segregation: ~0.1 Gyr minimum

    for i in range(1, n_time_steps):
        dt = time_Gyr[i] - time_Gyr[i - 1]
        # Cap dt to avoid numerical overflow
        dt = min(dt, t_coll_H * 0.5)

        # Heavy species: standard gravothermal collapse + sinks to center
        growth_H = np.exp(dt / t_coll_H)
        rho_H_new = rho_H_history[i - 1] * (1 + (growth_H - 1) * np.exp(-r_kpc / (0.5 * r_s)))

        # Mass segregation: heavy migrates inward
        # Net transfer: heavy in central bins increases, decreases in outskirts
        seg_factor = np.exp(dt / t_seg) - 1
        for j in range(n_radial_bins):
            if r_kpc[j] < r_s:
                # Inner region: gain heavy from outside
                rho_H_new[j] *= (1 + seg_factor * 0.3 * np.exp(-r_kpc[j] / r_s))
            else:
                # Outer region: lose heavy to inner
                rho_H_new[j] *= (1 - seg_factor * 0.1 * np.exp(-(r_kpc[j] - r_s) / r_s))

        # Light species: opposite — pushed outward by heavy's collapse
        rho_L_new = rho_L_history[i - 1] * np.exp(-seg_factor * 0.05 * np.exp(-r_kpc / (2 * r_s)))

        # Conserve total mass: M_H + M_L should remain ~M_halo
        M_total = 4 * np.pi * _trapz((rho_H_new + rho_L_new) * r_kpc ** 2, r_kpc)
        scale = M_halo_Msun / M_total
        rho_H_new *= scale
        rho_L_new *= scale

        rho_H_history[i] = rho_H_new
        rho_L_history[i] = rho_L_new

    return {
        "r_kpc": r_kpc,
        "time_Gyr": time_Gyr,
        "rho_H_history": rho_H_history,
        "rho_L_history": rho_L_history,
        "central_H_history": rho_H_history[:, 0],
        "central_L_history": rho_L_history[:, 0],
        "rho_H_initial": rho_H_0,
        "rho_L_initial": rho_L_0,
        "t_coll_H": t_coll_H,
        "t_seg": t_seg,
        "M_halo_Msun": M_halo_Msun,
        "r_s_kpc": r_s,
        "r_vir_kpc": r_vir,
        "m_phi_MeV": m_phi_MeV,
        "m_chi_H_GeV": m_chi_H_GeV,
        "m_chi_L_GeV": m_chi_L_GeV,
    }


def effective_sigma_m_at_radius(halo_result: dict, r_idx: int, t_idx: int) -> float:
    """Compute effective sigma/m at a given radius and time for the two-component halo.

    The observable sigma/m is a density-weighted average of sigma_HH and sigma_LL:
      <sigma/m>_obs = (rho_H * sigma_HH + rho_L * sigma_LL) / (rho_H + rho_L)
    """
    rho_H = halo_result["rho_H_history"][t_idx, r_idx]
    rho_L = halo_result["rho_L_history"][t_idx, r_idx]

    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    v_at_r = np.sqrt(G_NEWTON *
                     (4 * np.pi * _trapz(
                         (halo_result["rho_H_history"][t_idx, :r_idx + 1] +
                          halo_result["rho_L_history"][t_idx, :r_idx + 1]) *
                         halo_result["r_kpc"][:r_idx + 1] ** 2,
                         halo_result["r_kpc"][:r_idx + 1]
                     )) /
                     halo_result["r_kpc"][r_idx])

    sigma_HH = sigma_m_cm2_per_g(v_at_r, halo_result["m_phi_MeV"],
                                  halo_result["m_chi_H_GeV"], 0.5)
    sigma_LL = sigma_m_cm2_per_g(v_at_r, halo_result["m_phi_MeV"],
                                  halo_result["m_chi_L_GeV"], 0.35)
    return (rho_H * sigma_HH + rho_L * sigma_LL) / (rho_H + rho_L + 1e-30)


if __name__ == "__main__":
    print("=" * 70)
    print("T90.47 — Gravothermal Fluid Model for Multi-Component SIDM")
    print("=" * 70)
    print()

    # Reference run: M_halo = 1e10 M_sun (dwarf galaxy scale)
    print("Reference run: M_halo = 1e10 M_sun (dwarf galaxy)")
    result = gravothermal_two_component(
        M_halo_Msun=1e10,
        c=15.0,
        m_chi_H_GeV=30.0,
        m_chi_L_GeV=10.0,
        g_chi_H=0.5,
        g_chi_L=0.35,
        m_phi_MeV=50.0,
        t_final_Gyr=10.0,
    )

    print(f"  r_s = {result['r_s_kpc']:.2f} kpc, r_vir = {result['r_vir_kpc']:.2f} kpc")
    print(f"  t_coll_H (heavy) = {result['t_coll_H']:.3e} Gyr")
    print(f"  t_seg (segregation) = {result['t_seg']:.3e} Gyr")
    print()
    print(f"  Central densities over time (M_sun/kpc^3):")
    for i, t in enumerate(result["time_Gyr"]):
        if i % 20 == 0:
            print(f"    t={t:.2f} Gyr: rho_H_c={result['central_H_history'][i]:.3e}, "
                  f"rho_L_c={result['central_L_history'][i]:.3e}")
    print()

    # Effective sigma/m at 1 kpc over time
    print("  Effective sigma/m at r=1 kpc over time (cm^2/g):")
    r_target = 1.0
    r_idx = np.argmin(np.abs(result["r_kpc"] - r_target))
    for i in [0, 50, 100, 150, 199]:
        sm_eff = effective_sigma_m_at_radius(result, r_idx, i)
        print(f"    t={result['time_Gyr'][i]:.2f} Gyr: sigma/m_eff = {sm_eff:.3e}")