"""
v19_2_f_priority3_born_helpers.py
SIDM composite-DM project - Born cross-section helpers (extracted from constraint_plot).

Extracted from v19_2_f_priority3_constraint_plot.py to reduce file size
(REVIEWER-15 item 11: file split).

Contains:
  - L_function(s): auxiliary function in Born transfer cross section
  - sigma_T_born_GeV2(alpha_D, m_chi_GeV, m_ap_GeV, v_kms): Born sigma_T in GeV^-2
  - sigma_m_born_cm2_g(alpha_D, m_chi_GeV, m_ap_GeV, v_kms): Born sigma/m in cm^2/g

Reference: Tulin, Yu, Zurek (2013), arXiv:1306.5010, Eq. (3)
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
import constants


def L_function(s):
    """Auxiliary function L(s) in the Born transfer cross section.

        L(s) = ln(1 + 1/s) - 1/(1 + s)

    This is the standard form from Tulin-Yu-Zurek (2013) Eq. (3).
    """
    if s <= 0:
        return 0.0
    return math.log(1.0 + 1.0 / s) - 1.0 / (1.0 + s)


def sigma_T_born_GeV2(alpha_D, m_chi_GeV, m_ap_GeV, v_kms):
    """Born-approximation s-wave transfer cross section (Tulin-Yu-Zurek 2013, Eq. 3).

        sigma_T = (g^4 m_chi^2) / (8 pi m_A^4) * L(s)^2
        s = (m_chi v / (sqrt(2) m_A))^2

    With alpha_D = g^2 / (4 pi):
        g^4 = (4 pi)^2 alpha_D^2 = 16 pi^2 alpha_D^2

    Returns sigma_T in GeV^-2.

    Born is valid for alpha_D << 1 (weak coupling), independent of kappa.
    For kappa > kappa_c, actual sigma/m can be enhanced by Sommerfeld S(v) > 1.
    """
    if alpha_D <= 0 or m_chi_GeV <= 0 or m_ap_GeV <= 0:
        return 0.0
    v_c = v_kms / constants.C_KMS
    s = (m_chi_GeV * v_c / (math.sqrt(2.0) * m_ap_GeV)) ** 2
    L = L_function(s)
    g4 = (4.0 * math.pi * alpha_D) ** 2
    prefactor = g4 * m_chi_GeV ** 2 / (8.0 * math.pi * m_ap_GeV ** 4)
    return prefactor * L ** 2


def sigma_m_born_cm2_g(alpha_D, m_chi_GeV, m_ap_GeV, v_kms):
    """sigma/m in cm^2/g (project output format), Born approximation."""
    sigma_T_GeV2 = sigma_T_born_GeV2(alpha_D, m_chi_GeV, m_ap_GeV, v_kms)
    sigma_T_cm2 = sigma_T_GeV2 * constants.HBAR_C_GEV_CM ** 2
    m_chi_g = m_chi_GeV * 1.78266192e-24
    if m_chi_g <= 0:
        return 0.0
    return sigma_T_cm2 / m_chi_g
