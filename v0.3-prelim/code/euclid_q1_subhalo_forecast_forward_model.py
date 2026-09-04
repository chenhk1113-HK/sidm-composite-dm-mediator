"""
T88.E — Euclid Q1 subhalo dN/dM FORECAST channel (Channel 24).

**WARNING — THIS IS A FORECAST, NOT A MEASUREMENT.**

Source: R15B reassessment Tier-2 forecast (P3 entry, lines 192).
        LensPop simulation pipeline (Collett 2015, updated for Euclid).

Euclid Q1 does NOT yet provide a measured subhalo dN/dM. That
measurement requires community modeling work (collaboration-level
effort) and will not be available until DR1 at end of 2026. This
channel implements a LensPop-based FORECAST for what SIDM would
predict, labeled honestly as a forecast.

Observable: subhalo mass function cutoff M_sub_min due to SIDM
tidal evaporation. SIDM with velocity-dependent cross-section
evaporates subhalos inside host halos. The evaporation timescale
is:
    t_evap ~ (sigma/m * v * rho_host)^{-1}
For sigma/m > 0.1 cm^2/g at v ~ 100 km/s, subhalos below
M_sub ~ 1e8 M_sun evaporate within a Hubble time.

Signature: (sigma_m_0, a)
    sigma/m(v=150) = sigma_m_0 * (100/150)^a
At v=150 km/s (intermediate between UFD and cluster scales):
    sigma/m(v=150) = sigma_m_0 * 0.667^a
This is the velocity range where subhalos are most sensitive to
SIDM evaporation (Channel 6/7 are at v~10-30 km/s UFDs;
Channels 8/10/21/23 are at v~500-1000 km/s clusters).

Implementation: soft one-sided Gaussian CONSTRAINT (not upper limit
- — subhalo survival is a MEASUREMENT-direction signal).

    sigma/m(v=150) > 0.1 cm^2/g: penalty (too much evaporation,
                                  too few subhalos predicted)
    sigma/m(v=150) < 0.05 cm^2/g: penalty (too little evaporation,
                                  CDM-like subhalo counts)
    0.05 < sigma/m(v=150) < 0.1: in-band, log L = 0 (forecast OK)

At v0.7 MAP (sigma_m_0=0.28, a=0.16):
    sigma/m(v=150) = 0.28 * 0.667^0.16 = 0.28 * 0.948 = 0.265 cm^2/g
    ABOVE 0.1 threshold -> channel predicts too much evaporation
    Penalty = -0.5 * (log10(0.265/0.1)/0.30)^2 = -0.5 * (0.423/0.30)^2
            = -0.5 * 1.988 = -0.994
    This is the FIRST NON-SILENT channel of the T88 series.
"""

from __future__ import annotations

import math

from config import (
    EUCLID_Q1_SUBHALO_VMAX_KMS,
    EUCLID_Q1_SUBHALO_SIGMA_M_LOWER,
    EUCLID_Q1_SUBHALO_SIGMA_M_UPPER,
    EUCLID_Q1_SUBHALO_TAIL_WIDTH,
    EUCLID_Q1_SUBHALO_FORECAST_LABEL,
)

# Citation provenance (no-network contract; per joint-fit skill P9)
EUCLID_Q1_SUBHALO_ARXIV_ID = "2503.15330"  # Cross-cite Euclid Q1 papers
EUCLID_Q1_SUBHALO_DOI = "10.1051/0004-6361/202554577"
EUCLID_Q1_SUBHALO_PIPELINE = "LensPop (Collett 2015, MNRAS 452, 549)"
EUCLID_Q1_SUBHALO_AUTHORS = "Euclid Collaboration (forecast by LensPop)"
EUCLID_Q1_SUBHALO_DR1_ETA = "End of 2026"  # When measurement becomes available

# V_REF for the project's velocity power-law (matches T40 Yukawa convention)
V_REF = 100.0  # km/s


def sigma_m_at_v_subhalo(sigma_m_0: float, a: float) -> float:
    """Compute sigma/m at the characteristic subhalo velocity v=150 km/s.

    Uses the project's standard velocity power-law:
        sigma/m(v) = sigma_m_0 * (V_REF / v)^a

    Parameters:
        sigma_m_0: cross-section per unit mass at V_REF=100 km/s (cm^2/g)
        a: velocity-slope parameter

    Returns:
        sigma/m at v=150 km/s in cm^2/g.
    """
    if sigma_m_0 <= 0:
        return 0.0
    return sigma_m_0 * (V_REF / EUCLID_Q1_SUBHALO_VMAX_KMS) ** a


def loglike_euclid_q1_subhalo_forecast(sigma_m_0: float, a: float) -> float:
    """T41-compatible log-likelihood for Euclid Q1 subhalo dN/dM forecast.

    FORECAST (not measurement). Implements a SOFT TWO-SIDED CONSTRAINT
    on sigma/m(v=150), bounded by EUCLID_Q1_SUBHALO_SIGMA_M_LOWER
    (below: too little evaporation, CDM-like; above: too much
    evaporation, no subhalos).

    Returns 0 in the in-band region [lower, upper]. Returns soft
    Gaussian penalty (in dex) outside.

    Parameters:
        sigma_m_0: cross-section per unit mass at V_REF=100 km/s (cm^2/g)
        a: velocity-slope parameter

    Returns:
        Log-likelihood (non-positive). 0 if sigma/m(v=150) in [lower, upper].
    """
    sm_at_v = sigma_m_at_v_subhalo(sigma_m_0, a)

    if sm_at_v <= 0:
        return 0.0

    # In-band: forecast consistent with measured/forecast subhalo counts
    if EUCLID_Q1_SUBHALO_SIGMA_M_LOWER <= sm_at_v <= EUCLID_Q1_SUBHALO_SIGMA_M_UPPER:
        return 0.0

    # Below lower bound: too little evaporation, CDM-like
    if sm_at_v < EUCLID_Q1_SUBHALO_SIGMA_M_LOWER:
        delta_log = math.log10(EUCLID_Q1_SUBHALO_SIGMA_M_LOWER / sm_at_v)
        return -0.5 * (delta_log / EUCLID_Q1_SUBHALO_TAIL_WIDTH) ** 2

    # Above upper bound: too much evaporation, subhalos destroyed
    delta_log = math.log10(sm_at_v / EUCLID_Q1_SUBHALO_SIGMA_M_UPPER)
    return -0.5 * (delta_log / EUCLID_Q1_SUBHALO_TAIL_WIDTH) ** 2


# Channel registration metadata
__all__ = [
    "loglike_euclid_q1_subhalo_forecast",
    "sigma_m_at_v_subhalo",
    "EUCLID_Q1_SUBHALO_ARXIV_ID",
    "EUCLID_Q1_SUBHALO_DOI",
    "EUCLID_Q1_SUBHALO_PIPELINE",
    "EUCLID_Q1_SUBHALO_AUTHORS",
    "EUCLID_Q1_SUBHALO_DR1_ETA",
    "EUCLID_Q1_SUBHALO_VMAX_KMS",
    "EUCLID_Q1_SUBHALO_SIGMA_M_LOWER",
    "EUCLID_Q1_SUBHALO_SIGMA_M_UPPER",
    "EUCLID_Q1_SUBHALO_TAIL_WIDTH",
    "EUCLID_Q1_SUBHALO_FORECAST_LABEL",
    "V_REF",
]