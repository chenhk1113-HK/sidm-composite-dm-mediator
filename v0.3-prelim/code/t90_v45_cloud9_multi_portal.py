"""
Multi-portal Cloud-9 likelihood wrapper.

The standard T90.29 v3 wrapper (loglike_relhic_t90v29) only evaluates
Portal A's contribution to sigma/m. For the T90.45 multi-portal model,
the total sigma/m at Cloud-9 v200 is the SUM of Portal A and Portal B
contributions, since both portals contribute to the elastic scattering
cross-section.

This wrapper correctly evaluates the total sigma/m for multi-portal
models. Use this instead of loglike_relhic_t90v29 in any T90.45+
context.
"""
from __future__ import annotations
import numpy as np
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import t40_yukawa_sigma_m as yukawa
from t90_v29_relhic_yukawa import loglike_relhic_v29_yukawa


def sigma_m_two_portal(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                        m_phi_B_MeV, m_chi_B_GeV, g_chi_B) -> float:
    """Total sigma/m from two portals (additive)."""
    sm_A = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A)
    sm_B = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    return sm_A + sm_B


def find_effective_single_portal_params(m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                                         m_phi_B_MeV, m_chi_B_GeV, g_chi_B,
                                         v_kms=28.0):
    """Find effective single-portal (m_phi, m_chi, g_chi) that reproduces
    the two-portal sigma/m at v_kms.

    Strategy: use Portal B params (light, gives high sigma/m at low v),
    but adjusted g_chi to match total sigma/m.
    """
    sigma_m_total = sigma_m_two_portal(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                                          m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    sigma_m_B = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_B_MeV, m_chi_B_GeV, g_chi_B)

    # If Portal B dominates, adjust g_chi_B
    if sigma_m_B > 0:
        # Scale g_chi to give sigma_m_total
        # sigma/m ~ g^4, so g_eff = g_B * (sm_total / sm_B)^(1/4)
        g_chi_eff = g_chi_B * (sigma_m_total / sigma_m_B) ** 0.25
    else:
        g_chi_eff = g_chi_A

    return m_phi_B_MeV, m_chi_B_GeV, g_chi_eff


def loglike_relhic_multi_portal(
    m_phi_A_MeV: float,
    m_chi_A_GeV: float,
    g_chi_A: float,
    m_phi_B_MeV: float,
    m_chi_B_GeV: float,
    g_chi_B: float,
    v_kms: float = 28.0,
) -> float:
    """Multi-portal Cloud-9 likelihood.

    Computes sigma/m at v_kms as the sum of Portal A + Portal B contributions,
    then maps to an effective single-portal representation and evaluates
    the T90.29 v3 Cloud-9 likelihood.

    Args:
        m_phi_A_MeV, m_chi_A_GeV, g_chi_A: Portal A (heavy) params
        m_phi_B_MeV, m_chi_B_GeV, g_chi_B: Portal B (light) params
        v_kms: Velocity scale (default 28 km/s = Cloud-9 v200)

    Returns:
        Cloud-9 log-likelihood (or 0 if posterior not loaded)
    """
    # Compute total sigma/m at v_kms
    sigma_m_total = sigma_m_two_portal(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                                          m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    if sigma_m_total <= 0:
        return 0.0

    # Map to effective single-portal (m_phi, m_chi, g_chi)
    m_phi_eff, m_chi_eff, g_chi_eff = find_effective_single_portal_params(
        m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
        m_phi_B_MeV, m_chi_B_GeV, g_chi_B,
        v_kms=v_kms,
    )

    return loglike_relhic_v29_yukawa(m_phi_eff, m_chi_eff, g_chi_eff)


def loglike_relhic_multi_portal_9d(theta) -> float:
    """9D theta wrapper for joint fits.

    theta = (log_m_phi_A, log_m_chi_A, g_chi_A,
             log_m_phi_B, log_m_chi_B, g_chi_B,
             log_eps, log_alpha, log_xi)
    """
    if theta is None or len(theta) < 6:
        return 0.0
    m_phi_A_MeV = 10 ** theta[0]
    m_chi_A_GeV = 10 ** theta[1]
    g_chi_A = theta[2]
    m_phi_B_MeV = 10 ** theta[3]
    m_chi_B_GeV = 10 ** theta[4]
    g_chi_B = theta[5]
    return loglike_relhic_multi_portal(
        m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
        m_phi_B_MeV, m_chi_B_GeV, g_chi_B,
    )
