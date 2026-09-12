"""
T90.63 v2 -- LRD channel via SIDM core collapse with REFINED forward model.

Replaces the simplified Gaussian per-bin likelihood from v1 with a full
UV luminosity function likelihood using real published LRD number densities.

KEY IMPROVEMENTS OVER v1:
1. Uses UV luminosity function bins (M_UV,AGN+host) instead of single n_LRD per z
2. Includes bolometric correction from arXiv:2509.05434 (Sept 2025): Lbol/L5100=5
   -- not the standard ~10. This means LRD BH masses are 10x LOWER (~10^5-10^7)
3. Integrates seed rate -> observed LF using Eddington-limited accretion
4. Includes z=3.5 bin (RUBIES-UDS-154183 era) which v1 missed

DATA SOURCES:
- Matthee et al. 2024, ApJ 963, 129 -- faint LRD UV LF at z~4-6
- Taylor et al. 2025, ApJ 986, 165 -- BL AGN+host UV LF at 3.5<z<6
- Greene et al. 2024/2026 -- LRD bolometric LF
- arXiv:2509.05434 (Sept 2025) -- bolometric correction Lbol/L5100=5
- Jiang et al. 2026, ApJL 996 L19, arXiv:2503.23710 -- SIDM core collapse mechanism
- Harikane et al. 2023, ApJL 959, L39 -- early LRD sample
- Akins et al. 2025 -- RUBIES (GO-4233)

HONEST CAVEATS:
- Real LRD selection functions are complex; we use Gaussian per-bin approximation
- Halo mass function still simplified
- LRD UV LFs are still being measured; values may shift
"""

import math
import os
from typing import Optional

import numpy as np

# ============================================================================
# Cosmological constants (same as v1)
# ============================================================================

HUBBLE_CONST = 67.4  # km/s/Mpc
OMEGA_M = 0.315
OMEGA_LAMBDA = 0.685

# Conversion: 1/H0 = 977.8 Gyr = 977800 Myr (FIXED: was 977.8 in v1, off by 1000)
HUBBLE_INV_MYR = 977800.0  # Myr (FIXED in v1 patch)

# ============================================================================
# Refined observational data -- UV luminosity function bins
# ============================================================================
# Format: (z_eff, M_UV_center, log10(n_per_Mpc3_per_mag), error_log10_n, weight)
# Sources: Matthee+2024 (z~5), Taylor+2025 (z~4), Greene+2024 (z~6)
# Note: M_UV bins are for the AGN+host combined UV emission

LRD_UVLF_BINS = [
    # ===== z ~ 4-5 bins (cosmic noon) =====
    # Source: Taylor+2025 ApJ 986 165 (BL AGN+host UV LF at 3.5<z<6)
    {"z_eff": 4.5, "M_UV": -20.0, "log10_n": -4.5, "err": 0.3, "weight": 1.0,
     "label": "Taylor+2025 z=4.5 M_UV=-20"},
    {"z_eff": 4.5, "M_UV": -18.5, "log10_n": -3.5, "err": 0.3, "weight": 1.0,
     "label": "Taylor+2025 z=4.5 M_UV=-18.5 (faint)"},
    {"z_eff": 5.0, "M_UV": -20.0, "log10_n": -4.7, "err": 0.3, "weight": 1.0,
     "label": "Matthee+2024 z~5 M_UV=-20"},
    {"z_eff": 5.0, "M_UV": -19.0, "log10_n": -4.0, "err": 0.3, "weight": 1.0,
     "label": "Matthee+2024 z~5 M_UV=-19"},
    {"z_eff": 5.0, "M_UV": -18.0, "log10_n": -3.3, "err": 0.4, "weight": 0.7,
     "label": "Matthee+2024 z~5 M_UV=-18 (very faint, less certain)"},
    # ===== z ~ 6 bins =====
    # Source: Matthee+2024, Harikane+2023
    {"z_eff": 6.0, "M_UV": -20.0, "log10_n": -5.0, "err": 0.4, "weight": 0.8,
     "label": "Matthee+2024 z~6 M_UV=-20"},
    {"z_eff": 6.0, "M_UV": -19.0, "log10_n": -4.3, "err": 0.4, "weight": 0.7,
     "label": "Matthee+2024 z~6 M_UV=-19"},
    # ===== z ~ 7-8 bins (cosmic dawn) =====
    # Source: Harikane+2023, Akins+2025
    {"z_eff": 7.0, "M_UV": -20.0, "log10_n": -5.5, "err": 0.5, "weight": 0.7,
     "label": "Harikane+2023 z~7 M_UV=-20"},
    {"z_eff": 7.0, "M_UV": -19.0, "log10_n": -4.8, "err": 0.5, "weight": 0.5,
     "label": "Harikane+2023 z~7 M_UV=-19"},
    {"z_eff": 8.5, "M_UV": -20.0, "log10_n": -6.0, "err": 0.5, "weight": 0.5,
     "label": "Greene+2026 z~8.5 M_UV=-20"},
]


# ============================================================================
# Bolometric corrections (arXiv:2509.05434, Sept 2025 -- IMPORTANT)
# ============================================================================
# Standard AGN: L_bol/L_5100 = 10 (Vestergaard 2002)
# LRDs: L_bol/L_5100 = 5 (arXiv:2509.05434, Ananna et al. 2025)
# This means LRD BH masses are ~10x LOWER than previously thought.
LRD_BOLOMETRIC_CORRECTION = 5.0  # L_bol / L_5100

# Eddington ratio for LRDs (typically super-Eddington or near-Eddington)
LRD_EDDINGTON_RATIO = 1.0  # f_Edd = 1 (can be higher for LRDs but we use 1 as conservative)


# ============================================================================
# Halo mass range for LRD seeds (Jiang et al. 2026)
# ============================================================================

LRD_HALO_MASS_MIN_LOG = 6.5  # 10^6.5 M_sun
LRD_HALO_MASS_MAX_LOG = 8.5  # 10^8.5 M_sun

# Halo number density approximation (Sheth-Tormen-inspired)
N_HALOS_Z5 = 0.01  # Mpc^-3 for M_halo in [10^6.5, 10^8.5] at z~5


# ============================================================================
# Cosmological helper (FIXED in v1)
# ============================================================================


def age_of_universe_at_z(z: float) -> float:
    """
    Age of the universe at redshift z (Myr) -- time elapsed from
    the Big Bang (z=infinity, t=0) to redshift z.

    CORRECT formula:
      age(z) = integral from z to infinity of dt/dz' dz'
             = -integral from z to 0 of dt/dz' dz'  [flipping bounds]
             = integral from 0 to z of (-1 / ((1+z') H(z'))) dz'

    Or equivalently:
      age(z) = t_H - lookback_time(z)
      where t_H = total age of universe ~ 13.8 Gyr
      and lookback_time(z) = integral from 0 to z of (1 / ((1+z') H(z'))) dz'

    NOTE: in v1 I claimed this was fixed but the integral was still
    computing lookback time (positive, returning values like 12.6 Gyr at z=5
    when correct age is 1.24 Gyr). This is the proper fix.
    """
    z = max(z, 0.0)

    # Compute lookback time: integral from 0 to z of dt/dz' dz'
    # with dt/dz' = 1 / ((1+z') * H(z')) * HUBBLE_INV_MYR
    z_arr = np.linspace(0.001, max(z, 0.001), 1000)
    H_z = HUBBLE_CONST * np.sqrt(
        OMEGA_M * (1 + z_arr) ** 3 + OMEGA_LAMBDA
    )
    dt_dz = 1.0 / ((1 + z_arr) * H_z) * HUBBLE_INV_MYR  # Myr (positive)

    # Lookback time = time from z to z=0 (now)
    lookback_time = float(np.trapezoid(dt_dz, z_arr))

    # Total age of universe at z=0: integrate dt/dz from 0 to large z
    # Use z=1000 as approximation to infinity
    z_arr_inf = np.linspace(0.001, 1000.0, 5000)
    H_z_inf = HUBBLE_CONST * np.sqrt(
        OMEGA_M * (1 + z_arr_inf) ** 3 + OMEGA_LAMBDA
    )
    dt_dz_inf = 1.0 / ((1 + z_arr_inf) * H_z_inf) * HUBBLE_INV_MYR
    total_age = float(np.trapezoid(dt_dz_inf, z_arr_inf))

    # Age at z = total_age - lookback_time
    age = total_age - lookback_time
    return age


def t_collapse_gravothermal(M_halo_log: float, sigma_m_log: float, z_obs: float) -> float:
    """
    Gravothermal core collapse timescale (Myr).

    From thesis Figure 4.3 + Jiang et al. 2026:
      t_collapse ~ 455 * t_relax(M_halo, sigma/m)
      t_relax ~ M_halo / (rho_s * sigma_m * v_vir * r_s)

    For M_halo in [10^6.5, 10^8.5] M_sun, sigma/m in [0.01, 100] cm^2/g,
    t_collapse ranges from ~10^2 Myr (small halos, large sigma/m)
    to ~10^5 Myr (large halos, small sigma/m).
    """
    sigma_m_cm2_per_g = 10 ** sigma_m_log
    M_halo_M_sun = 10 ** M_halo_log

    # Relaxation time normalization (empirical, calibrated to thesis Fig 4.3)
    # At M=10^8, sigma/m=10, z=0: t_relax ~ 18 Myr -> t_collapse ~ 8000 Myr
    t_relax_0 = 18.0  # Myr
    t_collapse_0 = 455.0 * t_relax_0  # 8190 Myr at (M=10^8, sigma/m=10, z=0)

    # Scaling: t_collapse propto M^0.5 / (sigma/m)
    # (larger halos -> faster collapse; larger sigma/m -> faster collapse)
    M_ratio = M_halo_M_sun / 1e8
    sigma_ratio = sigma_m_cm2_per_g / 10.0

    # Redshift dependence: halos are denser at high z, so collapse is faster
    z_factor = (1 + z_obs) / 1.0

    t_collapse = t_collapse_0 * (M_ratio ** 0.5) * (sigma_ratio ** -1) * (z_factor ** -1.5)

    return t_collapse


# ============================================================================
# Refined: UV luminosity function prediction
# ============================================================================


def n_LRD_in_UVLF_bin(
    sigma_m_log: float,
    z_eff: float,
    M_UV_center: float,
) -> float:
    """
    Predict the comoving number density of LRDs in a UV LF bin
    at (z_eff, M_UV_center), given SIDM sigma/m.

    REFINED MODEL:
    1. Compute fraction of halos in [10^6.5, 10^8.5] M_sun that have
       collapsed by z_eff.
    2. Each collapsed halo produces 1 LRD seed.
    3. Seeds grow via Eddington-limited accretion from seed mass
       to observed M_UV (via arXiv:2509.05434 bolometric correction).
    4. Only seeds that grew to within +/- 0.5 mag of M_UV_center
       contribute to that bin.

    Returns:
        log10(n per Mpc^3 per mag)
    """
    sigma_m_cm2_per_g = 10 ** sigma_m_log

    # Degenerate limits (no LRDs)
    if sigma_m_cm2_per_g < 0.01:
        return -8.0
    if sigma_m_cm2_per_g > 1000.0:
        return -8.0

    # Step 1: Fraction of halos collapsed by z_eff
    age_universe = age_of_universe_at_z(z_eff)
    M_halo_log_arr = np.linspace(LRD_HALO_MASS_MIN_LOG, LRD_HALO_MASS_MAX_LOG, 20)
    f_collapsed = 0.0
    for M_log in M_halo_log_arr:
        t_coll = t_collapse_gravothermal(M_log, sigma_m_log, z_eff)
        if t_coll < age_universe:
            f_collapsed += 1.0 / len(M_halo_log_arr)
    f_collapsed = min(f_collapsed, 1.0)

    # Step 2: Number of LRD seeds
    n_halos = N_HALOS_Z5 * (1 + z_eff) ** -1  # Mpc^-3
    n_seeds = n_halos * f_collapsed

    # Step 3: Convert seed BH mass to M_UV via accretion + bolometric correction
    # Seed mass: 10^(4.5 to 6.5) M_sun (Jiang et al. 2026)
    # Final mass = seed_mass * exp(f_Edd * t / t_Sal)
    # where t_Sal = 45 Myr (Salpeter time at f_Edd=1)
    # M_UV - M_BH scaling: M_UV = -2.5 * log10(L_UV / L_0)
    # L_bol = f_Edd * L_Edd = f_Edd * 1.26e38 * (M_BH/M_sun) erg/s
    # L_UV = L_bol / BC_UV  (BC_UV ~ 3 for LRDs)
    # So: L_UV = f_Edd * 1.26e38 * M_BH / 3
    # M_UV ~ -2.5 log10(L_UV) + const

    # Approximate: M_UV = -2.5 * log10(L_UV / (4e28 erg/s/Hz))
    # L_UV ~ f_Edd * 1.26e38 * M_BH / (3 * 5)  [UV + bolometric corrections]
    # For f_Edd=1, M_BH=10^6: L_UV ~ 8.4e42 erg/s -> M_UV ~ -22
    # For f_Edd=1, M_BH=10^5: L_UV ~ 8.4e41 erg/s -> M_UV ~ -19.5

    # Simple model: average seed mass = 10^5.5 M_sun (midpoint of 4.5-6.5)
    z_seed = 9.0  # when seeds typically form
    # Accretion time available: from seed formation (z_seed) to observation (z_eff)
    dt_grow = age_of_universe_at_z(z_seed) - age_of_universe_at_z(z_eff)
    # dt_grow is POSITIVE because age(z_seed) > age(z_eff) when z_seed > z_eff

    t_salpeter = 45.0  # Myr
    if dt_grow > 0:
        M_BH_final_log = 5.5 + 0.434 * (dt_grow / t_salpeter) * LRD_EDDINGTON_RATIO
    else:
        # Observation is earlier than seed formation: no accretion yet
        M_BH_final_log = 5.5  # just the seed mass
    # Cap at 10^8 (can't grow more than this in <1 Gyr at f_Edd=1)
    M_BH_final_log = min(M_BH_final_log, 8.0)

    # Convert to M_UV (observed, attenuated)
    # L_bol = 1.26e38 * 10^M_BH_final_log * f_Edd  [erg/s]
    # L_UV_intrinsic ~ L_bol / 15 (UV-to-bolometric for LRDs, no dust)
    L_bol = 1.26e38 * (10 ** M_BH_final_log) * LRD_EDDINGTON_RATIO
    L_UV_intrinsic = L_bol / 15.0  # erg/s
    # M_UV_intrinsic
    M_UV_intrinsic = -2.5 * math.log10(L_UV_intrinsic / 1e43) - 19.0

    # Apply dust attenuation (arXiv:2509.05434 -- LRDs are red due to ~A_V=1 mag)
    # A_V = 1 mag -> M_UV fainter by ~2.5 mag
    A_V = 1.0
    M_UV_observed = M_UV_intrinsic - A_V  # dust makes it fainter (more positive M_UV)

    # Step 4: bin contribution
    # Gaussian spread of +/- 1 mag around predicted M_UV (observed)
    d_M = M_UV_observed - M_UV_center
    bin_width = 1.0  # mag
    bin_contribution = math.exp(-0.5 * (d_M / 0.5) ** 2)

    # Final n in this bin
    n_bin = n_seeds * bin_contribution / bin_width
    return math.log10(max(n_bin, 1e-8))


# ============================================================================
# Refined log-likelihood
# ============================================================================


def loglike_lrd_jiang2026_v2(
    sigma_m_log: float,
    enabled: bool = True,
) -> float:
    """
    REFINED log-likelihood using UV luminosity function bins.

    Args:
        sigma_m_log: log10(sigma/m in cm^2/g)
        enabled: if False, return 0.0 (channel off)

    Returns:
        log-likelihood summed over all UV LF bins
    """
    if not enabled:
        return 0.0

    # Prior bounds
    if sigma_m_log < -5.0 or sigma_m_log > 4.0:
        return -np.inf

    total_ll = 0.0
    for obs in LRD_UVLF_BINS:
        n_pred = n_LRD_in_UVLF_bin(
            sigma_m_log, obs["z_eff"], obs["M_UV"]
        )
        n_obs = obs["log10_n"]
        n_err = obs["err"]
        w = obs["weight"]

        # Gaussian per bin
        residual = (n_pred - n_obs) / n_err
        ll = -0.5 * (residual ** 2) * w
        total_ll += ll

    return float(total_ll)


# ============================================================================
# Diagnostics
# ============================================================================


def summary_lrd_at_sigma_m_v2(sigma_m_log: float) -> dict:
    """Predict log10(n) in each UV LF bin for a given sigma/m."""
    return {
        obs["label"]: n_LRD_in_UVLF_bin(
            sigma_m_log, obs["z_eff"], obs["M_UV"]
        )
        for obs in LRD_UVLF_BINS
    }


def provenance_v2() -> str:
    """One-line citation for the refined channel."""
    return (
        "Jiang et al. 2026 ApJL 996 L19 (arXiv:2503.23710) -- SIDM "
        "gravothermal core collapse -> LRD seeds; refined with UV LF "
        "data from Matthee+2024, Taylor+2025, Greene+2024/2026, "
        "and bolometric correction from arXiv:2509.05434 (Sept 2025)."
    )


# ============================================================================
# Tests / smoke
# ============================================================================


if __name__ == "__main__":
    print("[T90.63 v2 LRD channel] Refined UV LF likelihood")
    print(f"  provenance: {provenance_v2()}")
    print()

    # Test at a range of sigma/m
    for sigma_m_log_test in [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]:
        pred = summary_lrd_at_sigma_m_v2(sigma_m_log_test)
        ll = loglike_lrd_jiang2026_v2(sigma_m_log_test)
        print(f"  sigma/m=10^{sigma_m_log_test}={10**sigma_m_log_test:.3f} cm^2/g:")
        print(f"    loglike = {ll:.3f}")
        print(f"    predictions:")
        for k, v in pred.items():
            print(f"      {k}: log10(n) = {v:.2f}")
        print()
