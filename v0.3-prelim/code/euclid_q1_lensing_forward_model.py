"""
T88.C — Euclid Q1 strong-lensing cluster catalog (Channel 23).

Source: Bergamini et al. 2026 (Euclid Q1 - XXXIII), A&A 711 A33,
arXiv:2503.15330, DOI 10.1051/0004-6361/202554577.

Provides 14 grade-A strong-lensing clusters (P_lens=1) from Euclid Q1
observations covering 63.1 deg^2.

Observable: lensing-derived mass profile / Einstein radius theta_E.
SIDM cross-section at v ~ 1000 km/s sets the core radius:
    R_core ~ (sigma/m * rho_core * t_age)^(1/2)
which in turn affects the central mass profile slope.

Signature: (sigma_m_0, a)
    sigma/m(v=1000) = sigma_m_0 * (V_REF / 1000)^a = sigma_m_0 * 10^(-a)

For the lensing observable, the strongest test is the ratio of total
mass inside the Einstein radius to the SIDM-predicted core mass.
Mass enclosed in SIDM core vs CDM-like cusp differs at the ~10-30%
level when sigma/m > 0.5 cm^2/g at v=1000 km/s.

This is a SOFT ONE-SIDED UPPER LIMIT on sigma/m(v=1000):
    - sigma/m(v=1000) < 0.5 cm^2/g: channel silent (CDM-like, no
      distinguishing power)
    - sigma/m(v=1000) > 0.5 cm^2/g: soft Gaussian penalty in dex with
      sigma = 0.30 (matching Channels 8, 10, 21 pattern)

At v0.7 MAP (sigma_m_0=0.28, a=0.16):
    sigma/m(v=1000) = 0.28 * 10^(-0.16) = 0.28 * 0.692 = 0.194 cm^2/g
    Below 0.5 threshold -> channel silent (cross-check OK).
"""

from __future__ import annotations

import math

from config import (
    EUCLID_Q1_VMAX_KMS,
    EUCLID_Q1_N_GRADE_A_CLUSTERS,
    EUCLID_Q1_SIGMA_M_UPPER_LIMIT,
    EUCLID_Q1_TAIL_WIDTH,
)

# Citation provenance (no-network contract; per joint-fit skill P9)
EUCLID_Q1_LENSING_ARXIV_ID = "2503.15330"
EUCLID_Q1_LENSING_DOI = "10.1051/0004-6361/202554577"
EUCLID_Q1_LENSING_JOURNAL = "A&A 711 A33"
EUCLID_Q1_LENSING_AUTHORS = "Euclid Collaboration: Bergamini et al."

# V_REF for the project's velocity power-law (matches T40 Yukawa convention)
V_REF = 100.0  # km/s


def sigma_m_at_v_euclid_q1(sigma_m_0: float, a: float) -> float:
    """Compute sigma/m at the characteristic cluster velocity v=1000 km/s.

    Uses the project's standard velocity power-law:
        sigma/m(v) = sigma_m_0 * (V_REF / v)^a

    Parameters:
        sigma_m_0: cross-section per unit mass at V_REF=100 km/s (cm^2/g)
        a: velocity-slope parameter

    Returns:
        sigma/m at v=1000 km/s in cm^2/g.
    """
    if sigma_m_0 <= 0:
        return 0.0
    return sigma_m_0 * (V_REF / EUCLID_Q1_VMAX_KMS) ** a


def loglike_euclid_q1_lensing(sigma_m_0: float, a: float) -> float:
    """T41-compatible log-likelihood for Euclid Q1 strong-lensing cluster channel.

    Soft one-sided Gaussian UPPER LIMIT at EUCLID_Q1_SIGMA_M_UPPER_LIMIT.
    Returns 0 below threshold (CDM-like, no distinguishing power);
    soft Gaussian penalty above threshold.

    Parameters:
        sigma_m_0: cross-section per unit mass at V_REF=100 km/s (cm^2/g)
        a: velocity-slope parameter

    Returns:
        Log-likelihood (non-positive). 0 if sigma/m(v=1000) below threshold.
    """
    sm_at_v = sigma_m_at_v_euclid_q1(sigma_m_0, a)

    # Below threshold: silent cross-check (SIDM cores not yet visible)
    if sm_at_v <= EUCLID_Q1_SIGMA_M_UPPER_LIMIT:
        return 0.0

    # Above threshold: soft Gaussian penalty in dex
    delta_log = math.log10(sm_at_v / EUCLID_Q1_SIGMA_M_UPPER_LIMIT)
    penalty = -0.5 * (delta_log / EUCLID_Q1_TAIL_WIDTH) ** 2
    return penalty


# Channel registration metadata
__all__ = [
    "loglike_euclid_q1_lensing",
    "sigma_m_at_v_euclid_q1",
    "EUCLID_Q1_LENSING_ARXIV_ID",
    "EUCLID_Q1_LENSING_DOI",
    "EUCLID_Q1_LENSING_JOURNAL",
    "EUCLID_Q1_LENSING_AUTHORS",
    "EUCLID_Q1_VMAX_KMS",
    "EUCLID_Q1_N_GRADE_A_CLUSTERS",
    "EUCLID_Q1_SIGMA_M_UPPER_LIMIT",
    "EUCLID_Q1_TAIL_WIDTH",
    "V_REF",
]