"""
XRISM Resolve phi -> gamma gamma decay null-channel (Channel 22 documented null, T88.D).

This module implements a "documented null" channel for the XRISM Resolve
spectroscopy line search for secluded-mediator phi -> gamma gamma decay at the
Perseus cluster core.

The result is a DOUBLY-NULL channel: (1) predicted photon energy E_gamma = m_phi/2
is in the 100-500 MeV range, ABOVE XRISM Resolve's 0.3-12 keV band by 4-5
orders of magnitude; (2) the lifetime tau_phi ~ 4e32 yr at v0.7 epsilon is
3e22 times the Hubble time, so the line is undetectable even in principle.

This is NOT a real constraining channel. It is an AUDIT TRAIL: code that
documents the R15B reassessment verdict ("asymptotically null at v0.7 epsilon")
with hand-computed numbers, so future review rounds don't re-litigate the
analysis.

Source: R15B reassessment
    v0.3-prelim/docs/consider5_review/R15B_DATASET_AVAILABILITY_REASSESSMENT.md
    lines 168-174 (P6b entry).
Background: consider5_source_extracted.md lines 27-28 (XRISM phi -> gamma gamma
    in Perseus cluster cores for portal coupling constraints).

Inputs:
    theta = (log_eps, log_alpha, m_phi_MeV, m_chi_GeV, g_chi, log_xi)
        from T41 v0.7 posterior.

Returns:
    loglike_phi_to_gamgam_xrism(theta) = 0.0 (silent cross-check; channel is
    documented null in physically-relevant regions of posterior).

Edge cases handled:
    - epsilon >= XRISM_PHI_DECAY_HARD_CAP_EPS (1e-30): returns 0 (no constraint,
      cap only flags numerical breakdown in test_epsilon_far_above_cap)
    - m_phi = 0 or NaN: returns 0 (degenerate input)
    - theta with negative entries: returns 0 (out of valid posterior)
"""

from __future__ import annotations

import math

from config import (
    XRISM_RESOLVE_BAND_HIGH_KEV,
    XRISM_RESOLVE_BAND_LOW_KEV,
    XRISM_PHI_DECAY_HARD_CAP_EPS,
    XRISM_PHI_DECAY_PERSIAN_FOV_KPC3,
    XRISM_PHI_DECAY_PREFACTOR_GEV2,
)

# Citation provenance (no-network contract; per joint-fit skill P9)
XRISM_PHI_DECAY_ARXIV_ID = "2402.08452"  # Bulbul+ 2024 eRASS1 catalog (cross-cites XRISM)
R15B_AUDIT_PATH = "v0.3-prelim/docs/consider5_review/R15B_DATASET_AVAILABILITY_REASSESSMENT.md"

# Convert MeV to keV for the XRISM band comparison
MEV_TO_KEV = 1.0e3

# Photon energy ratio required for the decay to be detectable
# (E_gamma / XRISM_RESOLVE_BAND_HIGH_KEV) must be <= 1 for the line to be in-band.
# For m_phi in 100-1000 MeV, E_gamma is 50-500 MeV, which is 4000-50000x above
# XRISM's 12 keV ceiling.

# Lifetime calculation constants
# tau_phi = hbar / Gamma_phi_to_gamgam
# Gamma_phi_to_gamgam = (alpha eps^2 m_phi^3) / (64 pi^3 v_phi^2)  [scalar Higgs-like, v_phi = v_EW]
# v_EW = 246 GeV (SM Higgs vev)
VEV_GEV = 246.0
ALPHA_EM = 1.0 / 137.036  # fine-structure constant at low energy

# Unit conversions
HBAR_EV_S = 6.582119569e-16  # Planck constant in eV * s
SECONDS_PER_YEAR = 3.15576e7
HUBBLE_TIME_YR = 1.38e10  # Planck 2018 H0 = 67.4 km/s/Mpc -> t_H = 1/H0 ~ 1.38e10 yr


def phi_decay_lifetime_yr(eps: float, m_phi_MeV: float) -> float:
    """Compute the φ→γγ decay lifetime in years for portal coupling ε and mediator mass m_φ.

    Uses the kinetic-mixing portal approximation for a Higgs-like scalar:
        Γ(φ→γγ) = (α ε² m_φ³) / (64 π³ v_EW²)
        τ = ℏ / Γ

    Parameters:
        eps: portal coupling (dimensionless, typically 1e-40 to 1e-30)
        m_phi_MeV: mediator mass in MeV

    Returns:
        Lifetime in years (a very large number, often > 1e30 yr).
    """
    m_phi_eV = m_phi_MeV * 1.0e6  # MeV -> eV
    # Gamma in eV
    # Pre-factor: alpha / (64 pi^3) ~ 1.20e-5
    prefactor = ALPHA_EM / (64.0 * math.pi ** 3)
    gamma_eV = prefactor * (eps ** 2) * (m_phi_eV ** 3) / (VEV_GEV ** 2 * 1.0e18)  # convert GeV^2 -> eV^2
    # gamma_eV = (alpha * eps^2 * m_phi_eV^3) / (64 pi^3 * v_eV^2)
    # where v_eV = 246 GeV = 2.46e11 eV, so v_eV^2 = 6.05e22 eV^2
    gamma_eV = prefactor * (eps ** 2) * (m_phi_eV ** 3) / (VEV_GEV * 1.0e9) ** 2
    if gamma_eV <= 0:
        return float("inf")
    tau_s = HBAR_EV_S / gamma_eV
    tau_yr = tau_s / SECONDS_PER_YEAR
    return tau_yr


def photon_energy_keV(m_phi_MeV: float) -> float:
    """Decay photon energy E_γ = m_φ/2 in keV (for the φ→γγ line).

    For m_φ in 100-1000 MeV, E_γ = 50-500 MeV = 5e4-5e5 keV.
    XRISM Resolve band is 0.3-12 keV, so E_γ is 4-5 orders of magnitude above.
    """
    return 0.5 * m_phi_MeV * MEV_TO_KEV


def is_photon_in_xrism_band(m_phi_MeV: float) -> bool:
    """Check if the predicted photon energy falls within XRISM Resolve's band.

    For ANY m_φ in the project's posterior range (10-1000 MeV), E_γ = m_φ/2 is
    5000-500000 keV, all 3-5 orders of magnitude above XRISM's 12 keV ceiling.

    Returns:
        False for all physically-relevant m_φ.
    """
    e_gamma_keV = photon_energy_keV(m_phi_MeV)
    return XRISM_RESOLVE_BAND_LOW_KEV <= e_gamma_keV <= XRISM_RESOLVE_BAND_HIGH_KEV


def predicted_photons_in_fov(eps: float, m_phi_MeV: float,
                              rho_DM_g_per_cm3: float = 1.0e-26,
                              exposure_s: float = 745.0e3) -> float:
    """Estimate the expected photon count in XRISM Resolve FOV during exposure.

    Number of φ in FOV × decay probability in exposure time × 2 (γγ final state).
        N_phi = rho_DM * V_FOV / m_phi
        P_decay = exposure / tau_phi_s
        N_photons = 2 * N_phi * P_decay

    Parameters:
        eps: portal coupling
        m_phi_MeV: mediator mass in MeV
        rho_DM_g_per_cm3: local DM density (default: 1e-26 g/cm^3, cluster core value)
        exposure_s: exposure time in seconds (default: 745 ks = XRISM Perseus)

    Returns:
        Expected photon count (a very large number, but at wrong energy band).
    """
    if m_phi_MeV <= 0:
        return 0.0
    m_phi_g = m_phi_MeV * 1.0e6 * 1.783e-33  # MeV -> g (1 eV/c^2 = 1.783e-33 g)
    # FOV volume: convert kpc^3 to cm^3
    V_FOV_cm3 = XRISM_PHI_DECAY_PERSIAN_FOV_KPC3 * (3.086e21) ** 3  # 1 kpc = 3.086e21 cm
    # Mass in FOV
    M_FOV_g = rho_DM_g_per_cm3 * V_FOV_cm3
    # Number of phi particles
    N_phi = M_FOV_g / m_phi_g
    # Lifetime in seconds
    tau_yr = phi_decay_lifetime_yr(eps, m_phi_MeV)
    tau_s = tau_yr * SECONDS_PER_YEAR
    # Probability of decay during exposure
    if tau_s <= 0 or math.isinf(tau_s):
        return 0.0
    P_decay = exposure_s / tau_s
    # Photon count (factor 2 for gamma-gamma final state)
    N_photons = 2.0 * N_phi * P_decay
    return N_photons


def loglike_phi_to_gamgam_xrism(theta) -> float:
    """T41-compatible log-likelihood for the XRISM φ→γγ decay null-channel.

    Channel signature: returns 0 (silent) for ALL physically-relevant input
    because the predicted photon energy is 4-5 orders of magnitude above
    XRISM's band, and the lifetime is ~3e22 x Hubble time.

    Parameters:
        theta: tuple (log_eps, log_alpha, m_phi_MeV, m_chi_GeV, g_chi, log_xi)

    Returns:
        0.0 (silent cross-check).
    """
    # Unpack (log_eps at index 0, m_phi at index 2)
    try:
        log_eps = float(theta[0])
        m_phi_MeV = float(theta[2])
    except (TypeError, IndexError, ValueError):
        return 0.0

    # Convert log_eps -> eps
    try:
        eps = 10.0 ** log_eps
    except (OverflowError, ValueError):
        return 0.0

    # Hard cap: eps above 1e-30 is outside the v0.7 posterior; flag and return 0
    # (the constraint is only meaningful in the posterior region, not at
    # unphysically large couplings)
    if eps >= XRISM_PHI_DECAY_HARD_CAP_EPS:
        return 0.0

    # Documented null: regardless of (eps, m_phi) in the posterior region,
    # the predicted photon energy is above XRISM's band by 4-5 orders of
    # magnitude, AND the lifetime exceeds Hubble time by 3e22. Silent.
    return 0.0


# Channel registration metadata for the T41 wire-in
__all__ = [
    "loglike_phi_to_gamgam_xrism",
    "phi_decay_lifetime_yr",
    "photon_energy_keV",
    "is_photon_in_xrism_band",
    "predicted_photons_in_fov",
    "XRISM_PHI_DECAY_ARXIV_ID",
    "R15B_AUDIT_PATH",
    "XRISM_PHI_DECAY_HARD_CAP_EPS",
    "HUBBLE_TIME_YR",
]