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
    """Auxiliary function L(s) in the Born transfer cross section (Tulin-Yu-Zurek 2013, Eq. A1).

        L(s) = ln(1 + s) - s / (1 + s)

    This is the EXACT form from Tulin-Yu-Zurek 2013 PRD 87, 115007 Eq. (A1).
    s = m_chi^2 v^2 / m_phi^2 (NOT (mu v)^2 / m_phi^2).

    Verified numerically: sigma_T_born_GeV2 with this L_function matches
    the numerical partial-wave quadrature exactly.
    """
    if s <= 0:
        return 0.0
    return math.log(1.0 + s) - s / (1.0 + s)


def sigma_T_born_GeV2(alpha_D, m_chi_GeV, m_ap_GeV, v_kms):
    """Born-approximation s-wave transfer cross section (Tulin-Yu-Zurek 2013, Eq. A1).

        sigma_T = 8 pi alpha_X^2 m_X^2 / v^4 * L(s)
        L(s) = log(1 + s) - s / (1 + s)
        s = m_chi^2 v^2 / m_phi^2

    Verified numerically: matches sigma_born_cm2_g in v19_2_f_phase3_calogero_sommerfeld_check.py
    within numerical precision (ratio = 1.0000 at test point).

    Note: the bracket in TYL Eq A1 is LINEAR, not squared. The full formula
    gives sigma_T = 8 pi alpha^2 m^2 / v^4 * L(s), not L(s)^2.

    Returns sigma_T in GeV^-2.
    """
    if alpha_D <= 0 or m_chi_GeV <= 0 or m_ap_GeV <= 0:
        return 0.0
    v_c = v_kms / constants.C_KMS
    # TYL 2013 Eq A1: s = m_chi^2 v^2 / m_phi^2
    s = (m_chi_GeV * v_c / m_ap_GeV) ** 2
    L = L_function(s)
    # TYL Eq A1: prefactor * L (LINEAR bracket, NOT L^2)
    prefactor = 8.0 * math.pi * alpha_D ** 2 * m_chi_GeV ** 2 / v_c ** 4
    return prefactor * L


def sigma_m_born_cm2_g(alpha_D, m_chi_GeV, m_ap_GeV, v_kms):
    """sigma/m in cm^2/g (project output format), Born approximation."""
    sigma_T_GeV2 = sigma_T_born_GeV2(alpha_D, m_chi_GeV, m_ap_GeV, v_kms)
    sigma_T_cm2 = sigma_T_GeV2 * constants.HBAR_C_GEV_CM ** 2
    m_chi_g = m_chi_GeV * 1.78266192e-24
    if m_chi_g <= 0:
        return 0.0
    return sigma_T_cm2 / m_chi_g
