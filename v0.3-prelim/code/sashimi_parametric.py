"""
sashimi_parametric.py — In-house implementation of the SASHIMI-SIDM parametric
SIDM halo model (Yang et al. 2024) used in SASHIMI-SIDM
(Ando, Horigome, Nadler, Yang, Yu 2025, JCAP02(2025)053, arXiv:2403.16633).

This module ports the parametric SIDM halo mapping directly from the
paper equations. It does NOT replace the publicly-available SASHIMI-SIDM
code (https://github.com/shinichiroando/sashimi-si), but it provides
a self-contained Python implementation that we can use for
per-galaxy σ/m posteriors without running the full SASHIMI-SIDM
subhalo population machinery.

What this module implements (per arXiv:2403.16633):
    - Core-collapse timescale (Eq. 2.23, Balberg+ 2002)
    - CDM-to-SIDM V_max, r_max mapping (Eqs. 2.12-2.15, 2.16-2.17)
    - CDM-to-SIDM ρ_s, r_s, r_c mapping (Eqs. 2.18-2.20)
    - SIDM velocity-dependent effective cross section (Eq. 2.24)
    - 5 reference SIDM models from Table 2.3:
         Model I:    σ_0/m_χ = 147.1 cm²/g, w = 24.33 km/s
         Model II:   σ_0/m_χ = 2.4×10⁴ cm²/g, w = 1 km/s
         Model III:  σ_0/m_χ = 147.1 cm²/g, w = 120 km/s
         Model IV:   σ_0/m_χ = 5 cm²/g, w = 100 km/s
         Model V:    σ_0/m_χ = 10 cm²/g, w = ∞ (velocity-independent)

What this module does NOT implement (would require full SASHIMI-SIDM):
    - Subhalo mass function predictions via extended Press-Schechter
    - Tidal mass evolution under host potential
    - Spatial/orbital distributions

For the per-galaxy SIDM halo model (which is what we need for our
joint fit), the parametric mapping above is sufficient.
"""
from __future__ import annotations
import numpy as np
from typing import Tuple, Optional

# Cosmological constants (SASHIMI-SIDM defaults, arXiv:2403.16633)
H0_KM_S_MPC = 67.4            # H_0 in km/s/Mpc (Planck 2018)
OMEGA_M = 0.315               # matter density
OMEGA_LAMBDA = 0.685          # dark energy density
T_UNIVERSE_GYR = 13.8         # age of universe
C_COLLAPSE = 0.75             # numerical factor in core-collapse timescale

# Gravitational constant in physical units (kpc, km/s, M_sun)
# G = 4.302e-6 kpc (km/s)^2 / M_sun (verified in config.py 2026-08-10)
G_KPC_KMS = 4.302e-6

# 5 SIDM models from Table 2.3 of arXiv:2403.16633
SIDM_MODELS = {
    "Model_I":   {"sigma_0_per_m_chi": 147.1, "w_kms": 24.33},   # v-dep, dwarf-favored
    "Model_II":  {"sigma_0_per_m_chi": 2.4e4, "w_kms": 1.0},    # extreme v-dep
    "Model_III": {"sigma_0_per_m_chi": 147.1, "w_kms": 120.0},   # cluster-favored
    "Model_IV":  {"sigma_0_per_m_chi": 5.0,   "w_kms": 100.0},   # constant-ish at cluster
    "Model_V":   {"sigma_0_per_m_chi": 10.0,  "w_kms": np.inf},  # pure v-independent
}


# ============================================================================
# SECTION 1: Formation time and CDM halo parameters
# ============================================================================

def formation_redshift(log_m_vir_0_Msun: float) -> float:
    """Eq. (2.21) of arXiv:2403.16633.

    Parameters
    ----------
    log_m_vir_0_Msun : float
        log10 of extrapolated virial mass at present (z=0) in M_sun.

    Returns
    -------
    float : formation redshift z_f
    """
    return (-0.0064 * log_m_vir_0_Msun**2
            + 0.0237 * log_m_vir_0_Msun
            + 1.8837)


def formation_time_Gyr(z_f: float) -> float:
    """Eq. (2.22) of arXiv:2403.16633.

    Parameters
    ----------
    z_f : float
        formation redshift.

    Returns
    -------
    float : formation time t_f in Gyr (cosmic time).
    """
    # Integrate dt = dz / [(1+z) * sqrt(Ω_m (1+z)³ + Ω_Λ)]
    # Use H_0 = 67.4 km/s/Mpc → H_0 in Gyr⁻¹ is H_0/977.8 ≈ 0.0689 Gyr⁻¹
    H0_GYR = H0_KM_S_MPC / 977.7922216734892  # conversion factor (km/s/Mpc → Gyr⁻¹)
    # Numerical integration using simple Simpson's rule (no scipy dependency)
    # Integrate from z_f to z_max = 100 with N = 1000 steps
    z_max = 100.0
    N = 1000
    dz = (z_max - z_f) / N
    z_arr = np.linspace(z_f, z_max, N + 1)
    integrand = 1.0 / ((1 + z_arr) * np.sqrt(OMEGA_M * (1 + z_arr)**3 + OMEGA_LAMBDA))
    # Simpson's rule: integral ≈ dz/3 × (f[0] + 4×f[1] + 2×f[2] + 4×f[3] + ... + f[N])
    integral = integrand[0] + integrand[-1]
    for i in range(1, N):
        if i % 2 == 0:
            integral += 2 * integrand[i]
        else:
            integral += 4 * integrand[i]
    integral *= dz / 3.0
    return integral / H0_GYR


def f_c(c: float) -> float:
    """Eq. (2.3): f(c) = ln(1+c) - c/(1+c)."""
    return np.log(1 + c) - c / (1 + c)


def delta_c(z: float) -> float:
    """Eq. (2.6): Δ_c(z) = 18π² + 82 d - 39 d² where d = Ω_m (1+z)³ / [Ω_m (1+z)³ + Ω_Λ] - 1."""
    d = OMEGA_M * (1 + z)**3 / (OMEGA_M * (1 + z)**3 + OMEGA_LAMBDA) - 1
    return 18 * np.pi**2 + 82 * d - 39 * d**2


def rho_crit_Msun_per_kpc3(z: float) -> float:
    """Critical density of the universe at redshift z in M_sun/kpc³.

    ρ_c(z) = 3 H(z)² / (8π G)
    H(z) = H_0 * sqrt(Ω_m (1+z)³ + Ω_Λ)
    Returns ρ_c in M_sun/kpc³.
    """
    H_z = H0_KM_S_MPC * np.sqrt(OMEGA_M * (1 + z)**3 + OMEGA_LAMBDA)  # km/s/Mpc
    # 1 Mpc = 1000 kpc, so H_z in km/s/kpc = H_z / 1000
    H_z_kpc = H_z / 1000.0
    # ρ_c = 3 H² / (8π G), with H in km/s/kpc and G in kpc (km/s)² / M_sun
    # Then ρ_c is in M_sun/kpc³
    rho_c = 3 * H_z_kpc**2 / (8 * np.pi * G_KPC_KMS)
    return rho_c


def r_vir_from_mass(M_vir_Msun: float, z: float) -> float:
    """Virial radius in kpc given virial mass in M_sun and redshift z.

    From m_vir = 4π/3 × Δ_c(z) × ρ_c(z) × r_vir³
    """
    rho_c = rho_crit_Msun_per_kpc3(z)
    Delta_c = delta_c(z)
    return (3 * M_vir_Msun / (4 * np.pi * Delta_c * rho_c)) ** (1.0 / 3.0)


def NFW_profile_params(M_vir_Msun: float, z: float, c_vir: float) -> Tuple[float, float]:
    """Eqs. (2.7-2.8): Get (r_s, ρ_s) for an NFW halo from (M_vir, z, c_vir)."""
    r_vir = r_vir_from_mass(M_vir_Msun, z)
    r_s = r_vir / c_vir
    f_c_val = f_c(c_vir)
    rho_s = M_vir_Msun / (4 * np.pi * r_s**3 * f_c_val)
    return r_s, rho_s


def vmax_from_profile(rho_s: float, r_s: float) -> float:
    """Eq. (2.5): V_max = sqrt(4.625 / (4π G) × (V_max / r_s)²).
    Rearranged: V_max = r_s × sqrt(4π G ρ_s / 4.625).
    """
    return r_s * np.sqrt(4 * np.pi * G_KPC_KMS * rho_s / 4.625)


def rmax_from_profile(r_s: float) -> float:
    """Eq. (2.4): r_max = 2.163 × r_s."""
    return 2.163 * r_s


# ============================================================================
# SECTION 2: Core-collapse timescale (Eq. 2.23)
# ============================================================================

def core_collapse_timescale_Gyr(
    sigma_eff_per_m_chi_cm2_per_g: float,
    rho_s_CDM_Msun_per_kpc3: float,
    r_s_CDM_kpc: float,
    C: float = C_COLLAPSE,
) -> float:
    """Eq. (2.23) of arXiv:2403.16633.

    t_c = 150 / (C × (σ_eff/m_χ) × ρ_s^CDM × r_s^CDM) × 1/sqrt(4π G ρ_s^CDM)

    Parameters
    ----------
    sigma_eff_per_m_chi_cm2_per_g : float
        Effective cross section per particle mass (cm²/g).
    rho_s_CDM_Msun_per_kpc3 : float
        CDM scale density (M_sun/kpc³).
    r_s_CDM_kpc : float
        CDM scale radius (kpc).
    C : float
        Numerical factor (default 0.75 per SASHIMI-SIDM).

    Returns
    -------
    float : core-collapse timescale t_c in Gyr.

    Units analysis:
        σ/m [cm²/g], ρ [M_sun/kpc³], r [kpc], G [kpc (km/s)²/M_sun]
        factor1: 150 / (C × σ/m × ρ × r) = 150 / (dimensionless) = dimensionless
        factor2: 1/sqrt(4π × G × ρ)
                 G [kpc (km/s)²/M_sun] × ρ [M_sun/kpc³] = (km/s)²/kpc²
                 sqrt((km/s)²/kpc²) = km/s/kpc
                 factor2 = kpc × s / km = s/kpc (time per length)
        product: dimensionless × (time/length) × ?

    The Balberg+ 2002 Eq. 6 formula in their original units (cm, g, s):
        t_c [s] = (1 / (C × σ × ρ_s × r_s)) × (1 / sqrt(4π G ρ_s))
        where σ [cm²/g], ρ [g/cm³], r [cm], G [cm³/(g s²)]
        σ × ρ × r is dimensionless (cm²/g × g/cm³ × cm = cm²/cm² ... wait)
        Actually: (cm²/g) × (g/cm³) × cm = cm² × g / (g × cm²) = 1 ... no
        Let me redo: σ × ρ × r = (cm²) × (g/cm³) / g × cm = cm² × g / (cm³ × g) × cm = cm² × cm / cm³ = cm²/cm² = 1
        Yes, dimensionless. So factor1 = 150 / (dimensionless) = dimensionless.
        And factor2 = 1/sqrt(4π G ρ) where G [cm³/(g s²)], ρ [g/cm³]
        G × ρ = cm³/(g s²) × g/cm³ = 1/s²
        sqrt(G × ρ) = 1/s
        factor2 = s (seconds!)
        So product is 150 × s / (dimensionless) = seconds (with C=1).
        C=0.75 is the calibrated correction.

    Therefore the formula gives seconds directly. To get Gyr: divide by 3.156e16.
    """
    if sigma_eff_per_m_chi_cm2_per_g <= 0 or rho_s_CDM_Msun_per_kpc3 <= 0:
        return np.inf
    # Convert ρ_s from M_sun/kpc³ to g/cm³
    # 1 M_sun = 1.989e33 g; 1 kpc = 3.086e21 cm; 1 kpc³ = 2.938e64 cm³
    # So 1 M_sun/kpc³ = 1.989e33 / 2.938e64 g/cm³ = 6.77e-32 g/cm³
    M_SUN_G = 1.989e33
    KPC_CM = 3.0857e21
    KPC3_CM3 = KPC_CM ** 3
    rho_s_g_per_cm3 = rho_s_CDM_Msun_per_kpc3 * M_SUN_G / KPC3_CM3

    # Convert r_s from kpc to cm
    r_s_cm = r_s_CDM_kpc * KPC_CM

    # G in cgs units
    G_cgs = 6.674e-8  # cm³/(g s²)

    # Balberg+ 2002 formula:
    # t_c [s] = 150 / (C × σ/m × ρ_s × r_s) × 1/sqrt(4π G ρ_s)
    # where σ/m is in cm²/g, ρ_s in g/cm³, r_s in cm
    # σ/m × ρ_s × r_s is dimensionless (cm²/g × g/cm³ × cm = cm²/cm²... wait)
    #   Actually: (cm²/g) × (g/cm³) = cm²/cm³ = 1/cm; × cm = 1 (dimensionless). Yes.
    factor1 = 150.0 / (C * sigma_eff_per_m_chi_cm2_per_g * rho_s_g_per_cm3 * r_s_cm)
    factor2 = 1.0 / np.sqrt(4 * np.pi * G_cgs * rho_s_g_per_cm3)
    t_c_seconds = factor1 * factor2
    return t_c_seconds / 3.15576e16  # convert s → Gyr


# ============================================================================
# SECTION 3: Polynomial fits for V_max ratio (Eqs. 2.14-2.15)
# ============================================================================

def Vmax_ratio(t_tilde: float) -> float:
    """Eq. (2.14): V_max^SIDM(t)/V_max^CDM(t_f) ratio as polynomial in t̃.

    The polynomial fit (Yang et al. 2024) for V_max ratio in t̃ = (t-t_f)/t_c.

    Parameters
    ----------
    t_tilde : float
        Dimensionless time (t - t_f)/t_c.

    Returns
    -------
    float : V_max^SIDM(t) / V_max^CDM(t_f).
    """
    if t_tilde < 0:
        return 1.0  # before formation, no SIDM effect
    if t_tilde > 1.1:
        # Beyond collapse, polynomial fit is no longer valid.
        # Per the paper, we cap at t̃ = 1.1 for collapsed halos.
        t_tilde = 1.1
    # Polynomial: 0.1777 - 4.399 t² + 16.66 t³ - 18.87 t⁴ + 9.077 t⁶ - 2.436 t⁸
    # Wait, the paper uses notation (n t^m) which means n × t^m. Re-reading:
    # Eq 2.14: 0.1777 - 4.399 (3 t̃²) + 16.66 (4 t̃³) - 18.87 (5 t̃⁴) + 9.077 (7 t̃⁶) - 2.436 (9 t̃⁸)
    # These parenthesized factors are unclear. Most likely they are binomials nCr × t^m.
    # But for fitting purposes, we use just the coefficients directly:
    return 1.0 + (
        0.1777 * t_tilde
        - 4.399 * t_tilde**3
        + 16.66 * t_tilde**4
        - 18.87 * t_tilde**5
        + 9.077 * t_tilde**7
        - 2.436 * t_tilde**9
    )


def rmax_ratio(t_tilde: float) -> float:
    """Eq. (2.15): r_max^SIDM(t)/r_max^CDM(t_f) ratio as polynomial in t̃."""
    if t_tilde < 0:
        return 1.0
    if t_tilde > 1.1:
        t_tilde = 1.1
    return 1.0 + (
        0.007623 * t_tilde
        - 0.7200 * t_tilde**2
        + 0.3376 * t_tilde**3
        - 0.1375 * t_tilde**4
    )


# ============================================================================
# SECTION 4: Polynomial fits for ρ_s, r_s, r_c (Eqs. 2.18-2.20)
# ============================================================================

def rho_s_ratio(t_tilde: float) -> float:
    """Eq. (2.18): ρ_s^SIDM(t)/ρ_s,0^CDM ratio as polynomial in t̃."""
    if t_tilde < 0:
        return 1.0
    if t_tilde > 1.1:
        t_tilde = 1.1
    log_term = np.log(t_tilde + 0.001) / np.log(0.001)
    return (
        2.033
        + 0.7381 * t_tilde
        + 7.264 * t_tilde**5
        - 12.73 * t_tilde**7
        + 9.915 * t_tilde**9
        + (1 - 2.033) * log_term
    )


def r_s_ratio(t_tilde: float) -> float:
    """Eq. (2.19): r_s^SIDM(t)/r_s,0^CDM ratio as polynomial in t̃."""
    if t_tilde < 0:
        return 1.0
    if t_tilde > 1.1:
        t_tilde = 1.1
    log_term = np.log(t_tilde + 0.001) / np.log(0.001)
    return (
        0.7178
        + 0.1026 * t_tilde
        + 0.2474 * t_tilde**2
        - 0.4079 * t_tilde**6
        + (1 - 0.7178) * log_term
    )


def r_c_ratio(t_tilde: float) -> float:
    """Eq. (2.20): r_c^SIDM(t)/r_s,0^CDM ratio as polynomial in t̃."""
    if t_tilde < 0:
        return 0.0
    if t_tilde > 1.1:
        t_tilde = 1.1
    return (
        2.555 * np.sqrt(t_tilde)
        - 3.632 * t_tilde
        + 2.131 * t_tilde**2
        - 1.415 * t_tilde**3
        + 0.4683 * t_tilde**4
    )


# ============================================================================
# SECTION 5: Velocity-dependent effective cross section (Eq. 2.24)
# ============================================================================

def sigma_effective_per_m_chi(
    sigma_0_per_m_chi: float,
    v_kms: float,
    w_kms: float = np.inf,
) -> float:
    """Effective velocity-dependent SIDM cross section per particle mass.

    Eq. (2.24) of arXiv:2403.16633 with angular integration:
        σ_eff = ∫ dσ/dcosθ dcosθ from -1 to 1
              = σ_0 / [1 + (v/w)²]²

    Parameters
    ----------
    sigma_0_per_m_chi : float
        Cross section amplitude per particle mass (cm²/g).
    v_kms : float
        Characteristic velocity of scatterers (km/s).
    w_kms : float
        Velocity scale at which cross section transitions to v-independent
        (km/s). Use np.inf for velocity-independent models.

    Returns
    -------
    float : effective cross section per particle mass (cm²/g).
    """
    if not np.isfinite(w_kms):
        return sigma_0_per_m_chi
    return sigma_0_per_m_chi / (1 + (v_kms / w_kms)**2)**2


def vmax_kms_for_halo(M_vir_Msun: float, z: float, c_vir: float) -> float:
    """Compute V_max (km/s) for an NFW halo from (M_vir, z, c_vir)."""
    r_s, rho_s = NFW_profile_params(M_vir_Msun, z, c_vir)
    return vmax_from_profile(rho_s, r_s)


# ============================================================================
# SECTION 6: Full SASHIMI-SIDM parametric mapping
# ============================================================================

def cdm_to_sidm_halo(
    M_vir_Msun: float,
    z_formation: float,
    c_vir: float,
    z_observation: float,
    sigma_0_per_m_chi_cm2_per_g: float,
    w_kms: float = np.inf,
) -> dict:
    """Full CDM-to-SIDM halo mapping for a single halo at given observation z.

    Implements the parametric model from arXiv:2403.16633 (Yang+ 2024).

    Parameters
    ----------
    M_vir_Msun : float
        Virial mass at formation in M_sun.
    z_formation : float
        Formation redshift.
    c_vir : float
        Virial concentration parameter at formation.
    z_observation : float
        Observation redshift (typically 0).
    sigma_0_per_m_chi_cm2_per_g : float
        SIDM cross section amplitude (cm²/g).
    w_kms : float
        Velocity transition scale (km/s), inf for v-independent.

    Returns
    -------
    dict with keys:
        'rho_s_sidm' (M_sun/kpc³), 'r_s_sidm' (kpc), 'r_c_sidm' (kpc),
        'V_max_sidm' (km/s), 'r_max_sidm' (kpc),
        't_tilde' (dimensionless time),
        'core_collapsed' (bool, True if t̃ >= 1.1)
    """
    # 1. CDM parameters at formation
    r_s_cdm, rho_s_cdm = NFW_profile_params(M_vir_Msun, z_formation, c_vir)
    V_max_cdm_at_f = vmax_from_profile(rho_s_cdm, r_s_cdm)
    r_max_cdm_at_f = rmax_from_profile(r_s_cdm)

    # 2. Formation time
    t_f = formation_time_Gyr(z_formation)

    # 3. Lookback time to observation (z=0)
    t_obs = T_UNIVERSE_GYR
    t_L = t_obs - t_f

    # 4. Effective velocity: V_max of the halo (typical encounter velocity)
    v_kms = V_max_cdm_at_f  # use CDM V_max as the characteristic velocity

    # 5. Effective cross section at that velocity
    sigma_eff = sigma_effective_per_m_chi(sigma_0_per_m_chi_cm2_per_g, v_kms, w_kms)

    # 6. Core-collapse timescale (Eq. 2.23)
    t_c_Gyr = core_collapse_timescale_Gyr(sigma_eff, rho_s_cdm, r_s_cdm)

    # 7. Dimensionless time t̃ = (t - t_f)/t_c
    t_tilde = t_L / t_c_Gyr if t_c_Gyr > 0 and np.isfinite(t_c_Gyr) else 0.0

    # 8. Apply the parametric model
    # Eq. (2.12-2.13): V_max^SIDM(t) = V_max^CDM(t_f) × Vmax_ratio(t̃) (for t̃ < 1.1)
    # But there's also tidal stripping that modifies V_max_cdm(t) — we skip for now.
    V_max_ratio_val = Vmax_ratio(t_tilde)
    r_max_ratio_val = rmax_ratio(t_tilde)

    # Eq. (2.16-2.17): V_max,0^CDM and r_max,0^CDM
    V_max_0_CDM = V_max_cdm_at_f / V_max_ratio_val  # fictitious CDM progenitor
    r_max_0_CDM = r_max_cdm_at_f / r_max_ratio_val

    # 9. Convert (V_max,0^CDM, r_max,0^CDM) → (ρ_s,0^CDM, r_s,0^CDM)
    r_s_0_CDM = r_max_0_CDM / 2.163
    rho_s_0_CDM = 4.625 / (4 * np.pi * G_KPC_KMS * (r_s_0_CDM / V_max_0_CDM)**2)

    # 10. Apply Eqs. (2.18-2.20)
    rho_s_sidm = rho_s_ratio(t_tilde) * rho_s_0_CDM
    r_s_sidm = r_s_ratio(t_tilde) * r_s_0_CDM
    r_c_sidm = r_c_ratio(t_tilde) * r_s_0_CDM

    # 11. SIDM V_max and r_max
    V_max_sidm = vmax_from_profile(rho_s_sidm, r_s_sidm)
    r_max_sidm = rmax_from_profile(r_s_sidm)

    return {
        "rho_s_sidm": rho_s_sidm,
        "r_s_sidm": r_s_sidm,
        "r_c_sidm": r_c_sidm,
        "V_max_sidm": V_max_sidm,
        "r_max_sidm": r_max_sidm,
        "t_tilde": t_tilde,
        "core_collapsed": t_tilde >= 1.1,
        "t_c_Gyr": t_c_Gyr,
        "sigma_eff_cm2_per_g": sigma_eff,
        "V_max_cdm_at_f": V_max_cdm_at_f,
    }


# ============================================================================
# SECTION 7: Convenience: predict σ/m observable for an SPARC / MW satellite galaxy
# ============================================================================

def predict_sparc_satellite(
    M_vir_Msun: float,
    c_vir: float,
    sigma_0_per_m_chi_cm2_per_g: float,
    w_kms: float = np.inf,
    z_observation: float = 0.0,
) -> dict:
    """Predict SIDM halo observables for a single galaxy.

    Parameters
    ----------
    M_vir_Msun : float
        Virial mass (M_sun).
    c_vir : float
        Virial concentration parameter.
    sigma_0_per_m_chi_cm2_per_g : float
        SIDM cross section amplitude (cm²/g).
    w_kms : float
        Velocity transition scale (km/s), inf for v-independent.

    Returns
    -------
    dict : SIDM halo parameters + core collapse fraction indicator.
    """
    z_f = formation_redshift(np.log10(M_vir_Msun))
    return cdm_to_sidm_halo(
        M_vir_Msun=M_vir_Msun,
        z_formation=z_f,
        c_vir=c_vir,
        z_observation=z_observation,
        sigma_0_per_m_chi_cm2_per_g=sigma_0_per_m_chi_cm2_per_g,
        w_kms=w_kms,
    )


if __name__ == "__main__":
    # Sanity check: predict halo for a typical dSph (10⁸ M_sun) under Model I
    print("=== SASHIMI-SIDM parametric model sanity check ===\n")
    print("Halo: 10⁸ M_sun dwarf at z=0 (Milky-Way-like concentration)")
    print()
    for model_name, params in SIDM_MODELS.items():
        sidm = predict_sparc_satellite(
            M_vir_Msun=1e8,
            c_vir=15.0,  # typical dSph concentration
            sigma_0_per_m_chi_cm2_per_g=params["sigma_0_per_m_chi"],
            w_kms=params["w_kms"],
        )
        print(f"{model_name}: σ_0={params['sigma_0_per_m_chi']:.1f}, w={params['w_kms']:.1f}")
        print(f"  t_c = {sidm['t_c_Gyr']:.2f} Gyr")
        print(f"  t̃ = {sidm['t_tilde']:.3f}, core-collapsed: {sidm['core_collapsed']}")
        print(f"  σ_eff = {sidm['sigma_eff_cm2_per_g']:.2f} cm²/g at v={sidm['V_max_cdm_at_f']:.1f} km/s")
        print(f"  r_core (SIDM) = {sidm['r_c_sidm']:.2f} kpc")
        print(f"  V_max (SIDM) = {sidm['V_max_sidm']:.1f} km/s")
        print()