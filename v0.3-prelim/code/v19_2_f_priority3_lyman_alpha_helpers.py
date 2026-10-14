"""
v19_2_f_priority3_lyman_alpha_helpers.py
SIDM composite-DM project - Lyman-alpha exclusion curve helpers.

Extracted from v19_2_f_priority3_constraint_plot.py (REVIEWER-16 item 8:
further file split). The main constraint plot module now imports from here.

Contains:
  - lyman_alpha_alpha_D_curve(m_ap_GeV_arr, v_kms, sigma_m_target, m_chi_GeV):
      Compute alpha_D(m_A') such that sigma/m = sigma_m_target
      (Lyman-alpha exclusion curve)

Reference: Tulin, Yu, Zurek (2013), arXiv:1306.5010
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
import numpy as np

_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

import constants


def lyman_alpha_alpha_D_curve(m_ap_GeV_arr, v_kms=30.0, sigma_m_target=100.0,
                                m_chi_GeV=1.0):
    """Compute alpha_D(m_A') such that sigma/m(v_kms, m_A', alpha_D) = sigma_m_target.

    Inverts the Born formula (Tulin-Yu 2013 Eq. 2.14) to find the
    alpha_D(m_A') curve that gives a target sigma/m value.

    Assumptions (REVIEWER-17):
    - Born approximation (no Sommerfeld enhancement).
    - s = (mu v)^2 / m_phi^2 is INDEPENDENT of alpha_D (since s depends on
      kinematics and mediator mass only, not on the coupling).
    - Therefore, L(s) is independent of alpha_D, and the inversion is direct:
        sigma/m = (g^4 / 16pi^2) * (m_chi^2 / m_A^4) * L^2 * (hbarc)^2 / m_chi_g
        Solve for g^2 = (4 pi alpha_D), so alpha_D^2 = sigma/m * m_chi_g * m_A^4 /
          [(hbarc)^2 * 2pi m_chi^2 * L^2]
    - Conversion: m_chi_g = m_chi_GeV * 1.78266192e-24 (1 GeV/c^2 = 1.78266e-24 g).

    Returns:
        numpy.ndarray: alpha_D values. NaN where undefined
        (e.g., L(s) -> 0 at very large m_A' or very small v).
        Callers should filter NaN: valid = curve[~np.isnan(curve)].
    """
    m_chi_g = m_chi_GeV * 1.78266192e-24
    # sigma/m = sigma_T_GeV2 * (hbarc)^2 / m_chi_g
    # sigma_T_GeV2 = (16 pi^2 alpha_D^2 m_chi^2) / (8 pi m_A^4) * L(s)^2
    #             = 2 pi alpha_D^2 m_chi^2 / m_A^4 * L(s)^2
    #
    # Setting sigma/m = sigma_m_target:
    #   alpha_D^2 = sigma_m_target * m_chi_g * m_A^4 / [(hbarc)^2 * 2 pi m_chi^2 * L(s)^2]
    v_c = v_kms / constants.C_KMS
    # TYL 2013 standard: s = (mu v)^2 / m_phi^2 = m_chi^2 v^2 / (4 m_phi^2)
    mu_GeV = m_chi_GeV / 2.0
    s_arr = (mu_GeV * v_c / m_ap_GeV_arr) ** 2
    L_arr = np.where(s_arr > 0,
                     np.log(1.0 + 1.0 / s_arr) - 1.0 / (1.0 + s_arr),
                     0.0)
    L_abs = np.abs(L_arr)
    # Avoid division by zero where L=0 (very large m_A' / very small v)
    safe = L_abs > 1e-12
    alpha_D_sq = np.full_like(L_arr, np.nan)
    alpha_D_sq[safe] = (
        sigma_m_target * m_chi_g * m_ap_GeV_arr[safe] ** 4
        / (constants.HBAR_C_GEV_CM ** 2 * 2.0 * np.pi * m_chi_GeV ** 2 * L_abs[safe] ** 2)
    )
    # np.sqrt propagates NaN correctly
    return np.sqrt(alpha_D_sq)
