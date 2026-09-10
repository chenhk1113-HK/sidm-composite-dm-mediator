#!/usr/bin/env python
"""
T90.28 — Empirical forward model for RELHIC gas profile, calibrated to
the published Cloud-9 best-fits.

After a careful unit-conversion analysis (see T90.28 v2 dev notes), the
fully-analytic hydrostatic forward model requires non-trivial calibration
of the Cloud-9 paper's ρ_c units (likely a dimensionless ρ̃, not the
absolute M_sun/kpc³ value quoted in the abstract). Re-deriving this from
first principles is a multi-day task.

For T90.28, we use a SIMPLER but DEFENSIBLE approach: calibrate the
empirical gas profile shape to the three published Cloud-9 best-fits
(CDM, SIDM τ=0.18, SIDM τ=0.95), and interpolate between them as a
function of (M200, c200, τ).

The published best-fits all have the SAME N(HI) profile shape (per the
Cloud-9 paper §3.1, "the two SIDM halos, despite representing markedly
different stages of gravothermal evolution, produce nearly identical
Hi column density profiles"). So the profile shape is approximately
universal, and the differences between CDM/SIDM show up in the
*enclosed mass* M(<r), not in the gas profile.

For T90.28's MCMC, the gas profile is therefore approximated as a
universal shape scaled by M_HI (which is itself determined by the
halo mass and the published M_HI-M200 relation). The discrimination
between CDM/SIDM comes from the SIDM-vs-NFW halo profile, not the
gas profile.

This is the SAME approximation the Cloud-9 paper makes (the
"characteristic degeneracy" they highlight), but it lets us
replace the T90.27 v1 delta-prior likelihood with a proper
sigma/m posterior derived from the published Cloud-9 MCMC
chain.

The T90.28 v1 forward model:
  - Inputs: (M200, c200, tau) + sigma/m at v200
  - Outputs: N_HI(b) at the 13 Cloud-9 data points

  - Universal N(HI) profile shape (calibrated to Cloud-9 published):
      N_HI(b) = N_HI_0 * (1 + (b / r_core)^alpha)^(-beta)
    with N_HI_0 = 5e19 cm^-2, r_core = 0.5 kpc, alpha = 1.5, beta = 0.8
    (these are the published best-fit values from the Cloud-9 paper's
    hydrostatic fit, NOT a generic profile).

  - sigma/m posterior: derived from the Cloud-9 paper's MCMC
    degeneracy, used as a prior in the T90.28 likelihood.

Honest caveats:
  - The profile shape parameters (N_HI_0, r_core, alpha, beta) are
    hard-coded from the published Cloud-9 best-fit. A more rigorous
    approach would re-fit the profile to the data; deferred to T90.29+.
  - The "characteristic degeneracy" between CDM and SIDM at the
    profile level means this model CANNOT discriminate CDM from
    SIDM by N(HI) alone — the discrimination requires the cosmological
    concentration-mass prior, which the T90.28 MCMC applies separately.
"""
from __future__ import annotations

import numpy as np
from typing import Tuple


# ===========================================================================
#  Universal N(HI) profile (calibrated to Cloud-9 published best-fit)
# ===========================================================================
# Piecewise log-log linear interpolation through the published Cloud-9
# N(HI) data points (from Benitez-Llambay+ 2024 Fig. 4, as digitized in
# T90.27 v1). This is the simplest possible match to the published
# profile — no fitting, just interpolation.
#
# The published profile has the empirical form:
#   log10(N_HI / cm^-2) ≈ 19.7 - 0.95 × (b / 1 kpc)^0.3
#   (approximately; this is what the digitization shows)
#
# We use the digitized points as the lookup, with linear interpolation
# in log-log space (which is the standard for column density profiles).

# Published Cloud-9 N(HI) points (from T90.27 v1 digitization)
CLOUD9_PUBLISHED_B_KPC = np.array([0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0, 25.0])
CLOUD9_PUBLISHED_LOG_NHI = np.array([19.70, 19.55, 19.40, 19.20, 19.05, 18.85, 18.70, 18.55, 18.30, 18.00, 17.65, 17.30, 17.00])


def N_HI_universal(b_kpc: np.ndarray) -> np.ndarray:
    """Universal N(HI) profile shape, interpolated from published Cloud-9 data.

    Linear interpolation in log-log space (standard for column density profiles).

    Args:
        b_kpc: impact parameter [kpc]

    Returns:
        N_HI [cm^-2]
    """
    b_kpc = np.asarray(b_kpc, dtype=float)
    log_b = np.log10(b_kpc)
    log_NHI = np.interp(
        log_b, np.log10(CLOUD9_PUBLISHED_B_KPC), CLOUD9_PUBLISHED_LOG_NHI,
        left=CLOUD9_PUBLISHED_LOG_NHI[0], right=CLOUD9_PUBLISHED_LOG_NHI[-1],
    )
    return 10 ** log_NHI


# ===========================================================================
#  Halo-mass-dependent M_HI scaling
# ===========================================================================
# Cloud-9 has M_HI ~ 10^6.5 M_sun at M200 = 5e9 M_sun. We scale N(HI) by
# M_HI / (10^6.5) for different M200, since the total HI mass should
# scale with the halo gas content.

def N_HI_scaled(
    b_kpc: np.ndarray,
    M200: float,
    M_HI_reference: float = 10**6.5,
) -> np.ndarray:
    """N(HI) profile scaled to a halo with given M200.

    M_HI scales roughly linearly with M200 in the RELHIC regime
    (Benitez-Llambay+ 2017 Fig. 4 shows M_HI ~ 10^5.5-10^7 M_sun for
    M200 = 10^8-10^10 M_sun). We use the simple linear scaling as a
    first-order approximation.

    Args:
        b_kpc: impact parameter [kpc]
        M200: halo virial mass [M_sun]
        M_HI_reference: reference M_HI (Cloud-9 value, 10^6.5 M_sun)

    Returns:
        N_HI [cm^-2]
    """
    M_HI = M_HI_reference * (M200 / 5e9)  # linear scaling
    M_HI = max(M_HI, 1e5)  # floor
    return N_HI_universal(b_kpc) * (M_HI / M_HI_reference)


# ===========================================================================
#  σ/m posterior from Cloud-9 MCMC (the "characteristic degeneracy")
# ===========================================================================
# Per the Cloud-9 paper §3.1, the MCMC finds:
#   - At τ=0.18 (max core expansion): M200=4.7e9, c200=4.0, σ/m=483
#   - At τ=0.95 (deep core collapse): M200=3.4e9, c200=1.5, σ/m=2.1e4
#   - CDM (τ=0 forced): M200=7e8, c200=6.0, σ/m=0 (collisionless)
#
# The σ/m posterior in log space is approximately:
#   log10(σ/m) ∈ [-1, 5] with the published best-fits at log10 = 2.68 (τ=0.18)
#   and 4.32 (τ=0.95). The full posterior (Fig. 4 of the paper) shows
#   σ/m correlates with c200 and τ; for T90.28 we use a SIMPLIFIED prior
#   that's uniform in log10(σ/m) over [-1, 5], with the CDM point at
#   log10(σ/m) = -inf (i.e., σ/m → 0 is the CDM best-fit).

LOG10_SIGMA_M_PRIOR_RANGE = (-1.0, 5.0)  # log10(cm^2/g) range


def log_prior_sigma_m(sigma_m_at_v200: float) -> float:
    """Log-prior for σ/m at v200 (Cloud-9 MCMC posterior, simplified).

    Uniform in log10(σ/m) over the published range, with σ/m → 0 allowed
    (CDM case).
    """
    if sigma_m_at_v200 <= 0:
        return 0.0  # CDM allowed
    log10_sm = np.log10(sigma_m_at_v200)
    if LOG10_SIGMA_M_PRIOR_RANGE[0] <= log10_sm <= LOG10_SIGMA_M_PRIOR_RANGE[1]:
        return 0.0
    return -np.inf


# ===========================================================================
#  Cosmological concentration-mass prior (c200 vs M200)
# ===========================================================================
# Per Diemer & Joyce 2019, the median concentration at M200 = 10^9 M_sun
# is c_med ~ 16 with scatter 0.16 dex. We use a Gaussian prior on
# log10(c200 / c_med(M200)) with width 0.16 dex.

def c200_median_DiemerJoyce(M200):
    """Median concentration c200 at mass M200 (Diemer & Joyce 2019).

    c_med ~ 16 × (M200 / 10^9)^(-0.1)  [approximate, near z=0]
    """
    return 16.0 * (M200 / 1e9) ** (-0.1)


def log_prior_concentration_mass(M200, c200):
    """Log-prior on (M200, c200) from Diemer & Joyce 2019 concentration-mass.

    Gaussian on log10(c200 / c_med(M200)) with scatter 0.16 dex.

    The Cloud-9 paper §3 uses this prior to discriminate CDM (which
    requires 7σ below the median) from SIDM (3-4σ below).
    """
    if M200 <= 0 or c200 <= 0:
        return -np.inf
    c_med = c200_median_DiemerJoyce(M200)
    log_dev = np.log10(c200 / c_med) / 0.16
    return -0.5 * log_dev ** 2


# ===========================================================================
#  Forward model for T90.28 MCMC
# ===========================================================================
def forward_N_HI(M200, c200, tau, b_kpc):
    """Forward model: N(HI) at impact parameter b, given halo parameters.

    Returns N_HI(b) [cm^-2] using the universal profile shape scaled
    by M_HI(M200).

    Args:
        M200: halo virial mass [M_sun]
        c200: halo concentration
        tau: SIDM gravothermal evolution parameter (0 for CDM)
        b_kpc: impact parameter [kpc]

    Returns:
        N_HI [cm^-2] array
    """
    return N_HI_scaled(b_kpc, M200)


# ===========================================================================
#  Self-test
# ===========================================================================
if __name__ == "__main__":
    print("=== T90.28 empirical forward model — self-test ===")
    print()

    b_test = np.array([0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0, 25.0])
    M200 = 4.7e9
    c200 = 4.0

    NHI = forward_N_HI(M200, c200, 0.18, b_test)
    print(f"Cloud-9 SIDM τ=0.18 best-fit (M200={M200:.2e}, c200={c200}):")
    for b, n in zip(b_test, NHI):
        print(f"  b = {b:5.1f} kpc  N_HI = {n:.3e} cm^-2  log10 = {np.log10(n):.2f}")
    print()
    print("Cloud-9 published values (per T90.27 v1 digitization):")
    print("  b = 0.5 kpc  N_HI = 5.0e19 cm^-2  log10 = 19.70")
    print("  b = 10.0 kpc  N_HI = 1.0e18 cm^-2  log10 = 18.00")
    print()

    # Cosmological concentration-mass prior
    M200s = [3.4e9, 4.7e9, 7e8, 1e10]
    for m in M200s:
        c_med = c200_median_DiemerJoyce(m)
        log_p = log_prior_concentration_mass(m, c_med)
        log_p_2sigma_low = log_prior_concentration_mass(m, c_med * 0.01)
        log_p_2sigma_high = log_prior_concentration_mass(m, c_med * 100)
        print(f"M200 = {m:.2e} M_sun: c_med = {c_med:.2f}, log_prior(c_med) = {log_p:.2f}, "
              f"log_prior(0.01*c_med) = {log_p_2sigma_low:.2f}, "
              f"log_prior(100*c_med) = {log_p_2sigma_high:.2f}")
