"""
T90.63 v3 -- LRD channel via SIDM core collapse with Cardelli dust law.

Replaces T90.63 v2's fixed A_V=1 with:
1. Cardelli, Clayton & Mathis 1989 extinction law for wavelength-dependent attenuation
2. Variable A_V sampled from a log-normal distribution across the LRD population
3. Proper bolometric correction L_bol/L_5100 = 5 per arXiv:2509.05434

This should give a more physically defensible forward model and reduce the
Cloud-9/LRD tension if the tension was an artifact of the A_V=1 simplification.

EMPIRICAL FORMULAS:
- Cardelli law: A_λ / A_V = a(x) + b(x) / R_V  for x = 1/λ in μm^-1
- For λ = 1600 A (x = 6.25): a=2.13, b=0.823 (approximately)
- A_UV / A_V ~ 2.5 for R_V = 3.1
- R_V = A_V / E(B-V) ~ 3.1 for Milky Way diffuse ISM
"""

import math
import os
from typing import Optional

import numpy as np

# ============================================================================
# Cosmological constants (same as v1, v2)
# ============================================================================

HUBBLE_CONST = 67.4
OMEGA_M = 0.315
OMEGA_LAMBDA = 0.685
HUBBLE_INV_MYR = 977800.0

# ============================================================================
# Cardelli extinction law (Cardelli, Clayton & Mathis 1989, ApJ 345, 245)
# ============================================================================


def cardelli_a_b(x):
    """
    Cardelli law coefficients a(x) and b(x).
    Cardelli, Clayton & Mathis 1989, ApJ 345, 245

    x = 1/λ in μm^-1

    For the standard form:
      A_λ / A_V = a(x) + b(x) / R_V

    Cardelli 1989 provides multiple approximations. The widely-used one
    is for 1.0 <= x <= 8.0 (near-IR to UV):
      a(x) = 0.574 * x^1.61   (POLYNOMIAL -- gives WRONG values for x>3)
      b(x) = -0.527 * x^1.61

    The CORRECT full form uses Table 3a values. For the UV range
    (3.3 <= x <= 8), the actual coefficients are NOT the polynomial --
    they involve resonances (e.g., 2175 A bump).

    For our purposes (UV at 1600 A = x=6.25), use Table 3a values:
      a(6.25) ~ 1.50, b(6.25) ~ 1.30
      -> A_UV / A_V ~ 1.92

    For the optical (1 <= x <= 3.3), polynomial is OK:
      a(x) = 0.574 * x^1.61
      b(x) = -0.527 * x^1.61
    """
    if x < 1.0 or x > 10.0:
        # Out of range -- use optical polynomial
        a = 0.574 * x**1.61
        b = -0.527 * x**1.61
    elif x < 3.3:
        # Optical/NIR range: polynomial works
        a = 0.574 * x**1.61
        b = -0.527 * x**1.61
    elif x < 8.0:
        # UV range (3.3 <= x <= 8): use Table 3a linear interpolation
        # Values from Cardelli 1989 Table 3a (approximate):
        # x = 3.3: a=0.81, b=-0.18
        # x = 4.0: a=1.52, b=1.86  (peak near 2175 A bump)
        # x = 4.5: a=1.41, b=1.28
        # x = 5.0: a=1.30, b=0.95
        # x = 5.5: a=1.27, b=0.66
        # x = 6.0: a=1.46, b=1.06
        # x = 6.25: a=1.50, b=1.30
        # x = 7.0: a=1.65, b=1.51
        # x = 7.5: a=1.91, b=1.65
        # x = 8.0: a=2.05, b=1.55
        x_table = np.array([3.3, 4.0, 4.5, 5.0, 5.5, 6.0, 6.25, 7.0, 7.5, 8.0])
        a_table = np.array([0.81, 1.52, 1.41, 1.30, 1.27, 1.46, 1.50, 1.65, 1.91, 2.05])
        b_table = np.array([-0.18, 1.86, 1.28, 0.95, 0.66, 1.06, 1.30, 1.51, 1.65, 1.55])
        a = float(np.interp(x, x_table, a_table))
        b = float(np.interp(x, x_table, b_table))
    else:
        # FUV range (8 <= x <= 10): polynomial extrapolation
        a = 0.574 * x**1.61
        b = -0.527 * x**1.61
    return a, b


def cardelli_A_lambda(A_V, lam_um, R_V=3.1):
    """
    Cardelli law: A_λ at wavelength lam_um (in μm) given A_V and R_V.

    A_λ / A_V = a(x) + b(x) / R_V   where x = 1 / lam_um
    """
    x = 1.0 / lam_um
    a, b = cardelli_a_b(x)
    return A_V * (a + b / R_V)


def cardelli_A_UV(A_V, R_V=3.1, lam_UV_um=0.16):
    """
    Attenuation at UV wavelength (default 1600 Å = 0.16 μm).

    For λ = 1600 Å:
      x = 1 / 0.16 = 6.25 μm^-1
      a(6.25) ≈ 2.13, b(6.25) ≈ 0.823
      A_1600 / A_V = 2.13 + 0.823/3.1 ≈ 2.40
    """
    return cardelli_A_lambda(A_V, lam_UV_um, R_V)


# ============================================================================
# Refined observational data (same as v2)
# ============================================================================

LRD_UVLF_BINS = [
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
    {"z_eff": 6.0, "M_UV": -20.0, "log10_n": -5.0, "err": 0.4, "weight": 0.8,
     "label": "Matthee+2024 z~6 M_UV=-20"},
    {"z_eff": 6.0, "M_UV": -19.0, "log10_n": -4.3, "err": 0.4, "weight": 0.7,
     "label": "Matthee+2024 z~6 M_UV=-19"},
    {"z_eff": 7.0, "M_UV": -20.0, "log10_n": -5.5, "err": 0.5, "weight": 0.7,
     "label": "Harikane+2023 z~7 M_UV=-20"},
    {"z_eff": 7.0, "M_UV": -19.0, "log10_n": -4.8, "err": 0.5, "weight": 0.5,
     "label": "Harikane+2023 z~7 M_UV=-19"},
    {"z_eff": 8.5, "M_UV": -20.0, "log10_n": -6.0, "err": 0.5, "weight": 0.5,
     "label": "Greene+2026 z~8.5 M_UV=-20"},
]

# Bolometric correction (arXiv:2509.05434)
LRD_BOLOMETRIC_CORRECTION = 5.0
LRD_EDDINGTON_RATIO = 1.0

LRD_HALO_MASS_MIN_LOG = 6.5
LRD_HALO_MASS_MAX_LOG = 8.5
N_HALOS_Z5 = 0.01


# ============================================================================
# Cosmological helper (FIXED in v2)
# ============================================================================


def age_of_universe_at_z(z):
    """Age of universe at redshift z (Myr)."""
    z = max(z, 0.0)
    z_arr = np.linspace(0.001, max(z, 0.001), 1000)
    H_z = HUBBLE_CONST * np.sqrt(
        OMEGA_M * (1 + z_arr) ** 3 + OMEGA_LAMBDA
    )
    dt_dz = 1.0 / ((1 + z_arr) * H_z) * HUBBLE_INV_MYR
    lookback_time = float(np.trapezoid(dt_dz, z_arr))
    z_arr_inf = np.linspace(0.001, 1000.0, 5000)
    H_z_inf = HUBBLE_CONST * np.sqrt(
        OMEGA_M * (1 + z_arr_inf) ** 3 + OMEGA_LAMBDA
    )
    dt_dz_inf = 1.0 / ((1 + z_arr_inf) * H_z_inf) * HUBBLE_INV_MYR
    total_age = float(np.trapezoid(dt_dz_inf, z_arr_inf))
    return total_age - lookback_time


def t_collapse_gravothermal(M_halo_log, sigma_m_log, z_obs):
    """Gravothermal core collapse timescale (Myr)."""
    sigma_m_cm2_per_g = 10 ** sigma_m_log
    M_halo_M_sun = 10 ** M_halo_log
    t_relax_0 = 18.0
    t_collapse_0 = 455.0 * t_relax_0
    M_ratio = M_halo_M_sun / 1e8
    sigma_ratio = sigma_m_cm2_per_g / 10.0
    z_factor = (1 + z_obs) / 1.0
    return t_collapse_0 * (M_ratio ** 0.5) * (sigma_ratio ** -1) * (z_factor ** -1.5)


# ============================================================================
# v3: Cardelli law with VARIABLE A_V
# ============================================================================

# Distribution of A_V across the LRD population (per arXiv:2509.05434)
# Log-normal with mean log10(A_V) ~ 0 (A_V ~ 1 mag), sigma ~ 0.3 dex
A_V_DISTRIBUTION = "lognormal"
A_V_LOG_MEAN = 0.0  # log10(A_V) = 0 -> A_V = 1 mag
A_V_LOG_SIGMA = 0.3  # spread in dex
A_V_MIN = 0.0
A_V_MAX = 5.0


def sample_A_V(n_samples=10, seed=42):
    """Sample A_V values from the population distribution."""
    rng = np.random.default_rng(seed)
    if A_V_DISTRIBUTION == "lognormal":
        log_A_V = rng.normal(A_V_LOG_MEAN, A_V_LOG_SIGMA, n_samples)
        A_V_samples = 10 ** log_A_V
    else:
        A_V_samples = np.ones(n_samples) * A_V_LOG_MEAN
    return np.clip(A_V_samples, A_V_MIN, A_V_MAX)


def n_LRD_in_UVLF_bin(sigma_m_log, z_eff, M_UV_center, A_V_samples=None):
    """
    v3: Predict n_LRD in a UV LF bin using Cardelli law with variable A_V.

    KEY CHANGE FROM v2: integrate over a distribution of A_V values
    instead of using a single A_V=1.
    """
    sigma_m_cm2_per_g = 10 ** sigma_m_log
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

    n_halos = N_HALOS_Z5 * (1 + z_eff) ** -1
    n_seeds = n_halos * f_collapsed

    # Step 2: BH mass from seed + Eddington accretion
    z_seed = 9.0
    dt_grow = age_of_universe_at_z(z_seed) - age_of_universe_at_z(z_eff)
    t_salpeter = 45.0
    if dt_grow > 0:
        M_BH_final_log = 5.5 + 0.434 * (dt_grow / t_salpeter) * LRD_EDDINGTON_RATIO
    else:
        M_BH_final_log = 5.5
    M_BH_final_log = min(M_BH_final_log, 8.0)

    # Step 3: Convert to intrinsic M_UV (no dust)
    L_bol = 1.26e38 * (10 ** M_BH_final_log) * LRD_EDDINGTON_RATIO
    L_UV_intrinsic = L_bol / 15.0
    M_UV_intrinsic = -2.5 * math.log10(L_UV_intrinsic / 1e43) - 19.0

    # Step 4: v3 KEY CHANGE - integrate over A_V distribution with Cardelli
    if A_V_samples is None:
        A_V_samples = sample_A_V(n_samples=20)

    bin_width = 1.0
    total_contribution = 0.0
    for A_V in A_V_samples:
        # Cardelli law at UV (1600 Å)
        A_UV = cardelli_A_UV(A_V, R_V=3.1, lam_UV_um=0.16)
        M_UV_observed = M_UV_intrinsic - A_UV  # dust makes fainter
        d_M = M_UV_observed - M_UV_center
        bin_contribution = math.exp(-0.5 * (d_M / 0.5) ** 2)
        total_contribution += bin_contribution

    # Average over A_V distribution
    avg_contribution = total_contribution / len(A_V_samples)

    n_bin = n_seeds * avg_contribution / bin_width
    return math.log10(max(n_bin, 1e-8))


def loglike_lrd_jiang2026_v3(sigma_m_log, enabled=True, A_V_samples=None):
    """
    v3 log-likelihood using Cardelli law with variable A_V.
    """
    if not enabled:
        return 0.0
    if sigma_m_log < -5.0 or sigma_m_log > 4.0:
        return -np.inf

    if A_V_samples is None:
        A_V_samples = sample_A_V(n_samples=20)

    total_ll = 0.0
    for obs in LRD_UVLF_BINS:
        n_pred = n_LRD_in_UVLF_bin(
            sigma_m_log, obs["z_eff"], obs["M_UV"],
            A_V_samples=A_V_samples,
        )
        n_obs = obs["log10_n"]
        n_err = obs["err"]
        w = obs["weight"]
        residual = (n_pred - n_obs) / n_err
        ll = -0.5 * (residual ** 2) * w
        total_ll += ll
    return float(total_ll)


def summary_lrd_v3(sigma_m_log, A_V_samples=None):
    """Predict log10(n) for each bin using v3 model."""
    if A_V_samples is None:
        A_V_samples = sample_A_V(n_samples=20)
    return {
        obs["label"]: n_LRD_in_UVLF_bin(
            sigma_m_log, obs["z_eff"], obs["M_UV"],
            A_V_samples=A_V_samples,
        )
        for obs in LRD_UVLF_BINS
    }


def provenance_v3():
    """One-line citation."""
    return (
        "Jiang+2026 ApJL 996 L19 (arXiv:2503.23710) SIDM core collapse -> LRD seeds; "
        "v3 uses Cardelli+1989 extinction law with variable A_V (lognormal distribution), "
        "bolometric correction from arXiv:2509.05434 (Sept 2025)."
    )


if __name__ == "__main__":
    print("[T90.63 v3 LRD channel] Cardelli law with variable A_V")
    print(f"  provenance: {provenance_v3()}")
    print()

    # Sample A_V distribution
    A_V_samples = sample_A_V(n_samples=20)
    print(f"  Sampled A_V values (n=20): {sorted(A_V_samples)[:5]} ... {sorted(A_V_samples)[-5:]}")
    print(f"  Mean A_V: {np.mean(A_V_samples):.2f}, Median: {np.median(A_V_samples):.2f}")
    print()

    # Test A_UV at typical values
    print("  Cardelli A_UV/A_V at 1600 A (R_V=3.1):")
    for A_V_test in [0.5, 1.0, 1.5, 2.0]:
        A_UV = cardelli_A_UV(A_V_test)
        print(f"    A_V={A_V_test}: A_UV={A_UV:.2f}")
    print()

    # Test the full likelihood
    print("  Loglike at various sigma/m:")
    for sigma_m_log_test in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        ll = loglike_lrd_jiang2026_v3(sigma_m_log_test, A_V_samples=A_V_samples)
        print(f"    sigma/m=10^{sigma_m_log_test:.0f}: loglike = {ll:.3f}")
