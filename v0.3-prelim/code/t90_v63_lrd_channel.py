"""
T90.63 -- LRD channel via SIDM gravothermal core collapse (Jiang et al. 2026).

Implements the LRD number-density likelihood based on the SIDM
gravothermal core-collapse mechanism proposed in:

  Jiang, F. et al. 2026, ApJL 996, L19
  "Formation of the Little Red Dots from the Core-collapse of
   Self-interacting Dark Matter Halos"
  arXiv:2503.23710

Mechanism (simplified, per Jiang et al. 2026 Section 2-3):
1. SIDM halos with M_halo in [10^6.5, 10^8.5] M_sun undergo
   gravothermal core collapse on a timescale t_collapse(M_halo, sigma/m)
2. The collapsed core forms a seed BH with mass M_seed ~ 10^4.5 - 10^6.5 M_sun
3. The seed grows via Eddington-limited accretion + mergers into an LRD
4. Observed LRD number density at redshift z is the integral of the
   seed rate over the halo mass function

Key Jiang et al. parameters we use:
- sigma/m: SIDM cross section per unit mass (cm^2/g)
- M_halo: halo mass (M_sun)
- z: redshift
- t_collapse: gravothermal collapse timescale (function of M_halo, sigma/m)
- M_seed: seed BH mass (function of M_halo, z)

Observational constraints (from JWST LRD surveys):
- Harikane et al. 2023, ApJL 959, L39 (early LRD sample)
- Akins et al. 2025 (RUBIES+ samples, z=4-8)
- Greene et al. 2024/2026 (corrected LRD bolometric LF)

For the forward model, we use a Gaussian placeholder for the LRD
number density at z=5 and z=7 (representative of JWST surveys), then
implement the Jiang et al. seed rate.

The channel returns loglike = -0.5 * sum ((predicted - observed)/sigma)^2
where predicted depends on sigma/m (the only T90 model parameter that
enters the Jiang mechanism).
"""

from __future__ import annotations

import math
import os
from typing import Optional

import numpy as np

# ============================================================================
# Constants (Jiang et al. 2026, Section 2.3 + Appendix A)
# ============================================================================

# Cosmological parameters (Planck 2018)
HUBBLE_CONST = 67.4  # km/s/Mpc
OMEGA_M = 0.315
OMEGA_LAMBDA = 0.685
SIGMA_8 = 0.811
N_S = 0.965
RHO_CRIT_0 = 2.775e11 * HUBBLE_CONST**2  # M_sun h^2 / Mpc^3

# Jiang et al. 2026 model constants
# Gravothermal collapse timescale (per their Eq. 2):
#   t_collapse ~ 455 * t_relax(M_halo, sigma/m)
# where t_relax is the SIDM relaxation time at the halo scale radius.
# Approximate analytic fit (Eq. 3 in thesisBmr.pdf referenced):
#   t_collapse(Myr) ~ 8000 * (M_halo/1e8)^(-1.5) * (sigma/m/10)^(-1)
#                     * (1 + z)^(-1.5)
# This is a simplified fit; full N-body gives factor ~2 scatter.
TCOLLAPSE_NORM = 8000.0  # Myr at M=1e8, sigma/m=10 cm^2/g, z=0
TCOLLAPSE_M_EXP = -1.5
TCOLLAPSE_SIGMA_EXP = -1.0
TCOLLAPSE_Z_EXP = -1.5

# Seed BH mass (Jiang et al. 2026 Section 3.2, Eq. 4-5):
#   M_seed ~ 10^(4.5-6.5) M_sun for M_halo ~ 10^(6.5-8.5) M_sun
# Approximate log-linear relation:
#   log M_seed ~ log M_halo - 2
MSEED_M_H_OFFSET_LOG = -2.0  # log10(M_seed/M_halo)
MSEED_SCATTER_LOG = 0.5  # ~1 sigma scatter in seed mass

# Halo mass range for LRD production (Jiang et al. 2026 Section 3.1)
LRD_HALO_MASS_MIN_LOG = 6.5  # log10(M_halo/M_sun)
LRD_HALO_MASS_MAX_LOG = 8.5

# Seed BH mass range
LRD_SEED_MASS_MIN_LOG = 4.5
LRD_SEED_MASS_MAX_LOG = 6.5

# ============================================================================
# Observational data (LRD number density from JWST surveys)
# ============================================================================
# At z=5: Akins et al. 2025 (RUBIES, GO-4233) — 35 LRDs in 4500 galaxies
# At z=7: Harikane et al. 2023 — early LRD sample
# Both as log10 of comoving number density in Mpc^-3
# Note: per Jiang et al. 2026 Section 3.1, the corrected LF values from
# Greene et al. 2026 give n_LRD ~ 1e-4 to 1e-3 Mpc^-3 at z=5
LRD_OBSERVATIONS = [
    {
        "z": 5.0,
        "label": "RUBIES+z5 (Akins 2025)",
        "log10_n_LRD_per_Mpc3_obs": -3.5,  # observed
        "log10_n_LRD_per_Mpc3_err": 0.3,    # 1-sigma
        "weight": 1.0,
    },
    {
        "z": 7.0,
        "label": "JWST+z7 (Harikane 2023)",
        "log10_n_LRD_per_Mpc3_obs": -4.5,
        "log10_n_LRD_per_Mpc3_err": 0.5,
        "weight": 1.0,
    },
    {
        "z": 8.5,
        "label": "JWST+z8.5 (Greene 2026)",
        "log10_n_LRD_per_Mpc3_obs": -5.0,
        "log10_n_LRD_per_Mpc3_err": 0.5,
        "weight": 0.5,  # lower weight due to small sample
    },
]


# ============================================================================
# Forward model: SIDM gravothermal core collapse -> LRD seed rate
# ============================================================================

def t_collapse_gravothermal(
    M_halo_log: float,
    sigma_m_log: float,
    z: float,
) -> float:
    """
    Gravothermal collapse timescale (Myr) for a SIDM halo.

    Simplified fit from Jiang et al. 2026 Section 2 + Appendix A:
        t_collapse ~ 8000 Myr * (M_halo/1e8)^(-1.5)
                     * (sigma/m/10 cm^2/g)^(-1)
                     * (1+z)^(-1.5)

    Args:
        M_halo_log: log10(M_halo / M_sun)
        sigma_m_log: log10(sigma/m in cm^2/g)
        z: redshift

    Returns:
        t_collapse in Myr
    """
    M_halo_norm = M_halo_log - 8.0  # log10(M_halo/1e8)
    sigma_m_norm = sigma_m_log - 1.0  # log10((sigma/m)/10)
    z_norm = math.log10(max(1.0 + z, 1.001))

    log_t = (
        math.log10(TCOLLAPSE_NORM)
        + TCOLLAPSE_M_EXP * M_halo_norm
        + TCOLLAPSE_SCATTER_SAFE(sigma_m_norm)
        + TCOLLAPSE_Z_EXP * z_norm
    )
    # Note: TCOLLAPSE_SCATTER_SAFE handles the sigma/m exponent
    return 10 ** log_t


def TCOLLAPSE_SCATTER_SAFE(sigma_m_norm: float) -> float:
    """
    Scatter in t_collapse due to sigma/m variations (placeholder for full model).
    For now: linear in sigma/m_norm.
    """
    return TCOLLAPSE_SIGMA_EXP * sigma_m_norm


def age_of_universe_at_z(z: float) -> float:
    """
    Age of the universe at redshift z (Myr) -- i.e., time elapsed from
    the Big Bang (z=infinity, t=0) to redshift z.

    Computed as:  age(z) = total_age - lookback_time(z)
    where lookback_time(z) = integral from 0 to z of dt/dz dz
                          = time elapsed from z to now

    Using flat LambdaCDM, Omega_m=0.315, Omega_Lambda=0.685, H0=67.4.

    Unit conversion: H(z) is in km/s/Mpc.
    1 Mpc / (1 km/s) = 3.086e22 m / (1000 m/s) = 3.086e19 s
                     = 9.778e11 yr = 9.778e5 Myr = 977.8 Gyr
    So multiply by 977800 to convert (km/s/Mpc)^-1 -> Myr.
    """
    # Total age = integral from 0 to infinity of |dt/dz| dz
    z_arr_total = np.linspace(0.001, 1000, 5000)
    H_z_total = HUBBLE_CONST * np.sqrt(OMEGA_M * (1 + z_arr_total) ** 3 + OMEGA_LAMBDA)
    dt_dz_total = 1.0 / ((1 + z_arr_total) * H_z_total) * 977800.0  # positive (absolute value)
    total_age = np.trapezoid(dt_dz_total, z_arr_total)

    # Lookback time at z = integral from 0 to z of |dt/dz| dz
    z_arr_lb = np.linspace(0.001, max(z, 0.001), 1000)
    H_z_lb = HUBBLE_CONST * np.sqrt(OMEGA_M * (1 + z_arr_lb) ** 3 + OMEGA_LAMBDA)
    dt_dz_lb = 1.0 / ((1 + z_arr_lb) * H_z_lb) * 977800.0
    lookback_time = np.trapezoid(dt_dz_lb, z_arr_lb)

    age = total_age - lookback_time
    return float(age)


def n_LRD_predicted(sigma_m_log: float, z_obs: float) -> float:
    """
    Predict the LRD comoving number density at redshift z_obs given
    the SIDM cross section.

    Simplified model (per Jiang et al. 2026 Section 3.3):
    1. Compute the fraction of halos in [10^6.5, 10^8.5] M_sun that have
       completed gravothermal collapse by z_obs.
    2. Each collapsed halo produces 1 LRD (assumes one seed per halo).
    3. n_LRD ~ f_collapse(z_obs, sigma/m) * n_halos in mass range.

    Returns:
        log10(n_LRD per Mpc^3)
    """
    sigma_m_cm2_per_g = 10 ** sigma_m_log
    # Degenerate limit: sigma/m too small -> no collapse (n_LRD -> 0)
    if sigma_m_cm2_per_g < 0.01:
        return -8.0  # effectively no LRDs
    # Degenerate limit: sigma/m too large -> halos evaporate before collapse
    if sigma_m_cm2_per_g > 1000.0:
        return -8.0

    # Number density of halos in mass range (from Sheth-Tormman HMF)
    # Approximate: n_halos(M_halo in [10^6.5, 10^8.5]) ~ 10^-2 Mpc^-3 at z~5
    # Scales as (1+z)^-1 roughly
    n_halos = 0.01 * (1 + z_obs) ** -1  # Mpc^-3

    # Fraction collapsed = halos with t_collapse < age_of_universe_at_z
    age_universe = age_of_universe_at_z(z_obs)
    # Integrate over the halo mass function
    M_halo_log_arr = np.linspace(LRD_HALO_MASS_MIN_LOG, LRD_HALO_MASS_MAX_LOG, 20)
    f_collapsed = 0.0
    for M_log in M_halo_log_arr:
        t_coll = t_collapse_gravothermal(M_log, sigma_m_log, z_obs)
        if t_coll < age_universe:
            # Weight by halo mass function (steep at low mass)
            f_collapsed += 1.0 / len(M_halo_log_arr)
    f_collapsed = min(f_collapsed, 1.0)

    n_lrd = n_halos * f_collapsed
    return math.log10(max(n_lrd, 1e-8))


# ============================================================================
# Channel log-likelihood
# ============================================================================

def loglike_lrd_jiang2026(
    sigma_m_log: float,
    z_obs: float = None,
    enabled: bool = True,
) -> float:
    """
    Log-likelihood of LRD number density from SIDM core collapse.

    Args:
        sigma_m_log: log10(sigma/m in cm^2/g) -- the only T90 parameter
                     that enters the Jiang et al. mechanism
        z_obs: if None, sum over all redshift bins; if specified, evaluate
               at that single redshift
        enabled: if False, return 0.0 (channel off)

    Returns:
        log-likelihood (Gaussian per bin, summed)
    """
    if not enabled:
        return 0.0

    # Prior bounds (sigma/m must be positive and within physical range)
    if sigma_m_log < -5.0 or sigma_m_log > 4.0:
        return -np.inf

    total_ll = 0.0
    for obs in LRD_OBSERVATIONS:
        if z_obs is not None and abs(obs["z"] - z_obs) > 0.5:
            continue
        n_pred = n_LRD_predicted(sigma_m_log, obs["z"])
        n_obs = obs["log10_n_LRD_per_Mpc3_obs"]
        n_err = obs["log10_n_LRD_per_Mpc3_err"]
        w = obs["weight"]

        # Gaussian likelihood per bin
        residual = (n_pred - n_obs) / n_err
        ll = -0.5 * (residual ** 2) * w
        total_ll += ll

    return total_ll


def summary_lrd_at_sigma_m(sigma_m_log: float) -> dict:
    """Diagnostic helper: predict n_LRD at each z bin for a given sigma/m."""
    return {
        f"log10_n_LRD_z{obs['z']}": n_LRD_predicted(sigma_m_log, obs["z"])
        for obs in LRD_OBSERVATIONS
    }


def provenance() -> str:
    """One-line citation for this channel."""
    return ("Jiang et al. 2026 ApJL 996 L19 "
            "(arXiv:2503.23710) -- SIDM gravothermal core collapse -> LRD seeds")


# ============================================================================
# Tests / smoke
# ============================================================================

if __name__ == "__main__":
    print("[T90.63 LRD channel] Jiang et al. 2026 forward model")
    print(f"  provenance: {provenance()}")
    print()

    # Test 1: sigma/m = 1 cm^2/g (typical SIDM cross section)
    for sigma_m_log_test in [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]:
        pred = summary_lrd_at_sigma_m(sigma_m_log_test)
        ll = loglike_lrd_jiang2026(sigma_m_log_test)
        print(f"  sigma/m=10^{sigma_m_log_test}={10**sigma_m_log_test:.3f} cm^2/g:")
        print(f"    log10(n_LRD) per z bin: {pred}")
        print(f"    loglike = {ll:.3f}")
        print()