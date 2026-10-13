"""
v19_2_f_priority1_resonance_helpers.py
SIDM composite-DM project - Resonance form factor helpers (extracted from resonance_form_factor).

Extracted from v19_2_f_priority1_resonance_form_factor.py to reduce file size
(REVIEWER-15 item 11: file split).

Contains:
  - F_resonance_sq(q, m_rho, Gamma_rho): Breit-Wigner |F(q)|^2
  - sigma_m_resonance(v, alpha_D, m_rho, Gamma_rho, m_chi): sigma/m with resonance
  - velocity_at_resonance(m_rho, m_chi): v at which resonance peak occurs

Reference: Chu, Hambye, Tytgat (2018) M2 model, arXiv:1712.02521
"""
from __future__ import annotations
import math
from pathlib import Path
import sys

_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from constants import M_CHI_GEV, MU_RED_GEV, C_KMS, HBAR_C_GEV_CM


def F_resonance_sq(q_GeV: float, m_rho_GeV: float, Gamma_rho_GeV: float) -> float:
    """Breit-Wigner |F(q)|^2 = 1 / [ (q^2 - m_rho^2)^2 + (m_rho Gamma_rho)^2 ]."""
    inv = (q_GeV**2 - m_rho_GeV**2) ** 2 + (m_rho_GeV * Gamma_rho_GeV) ** 2
    if inv <= 0.0 or not math.isfinite(inv):
        return 0.0
    return 1.0 / inv


def sigma_m_resonance(v_kms: float, alpha_D: float, m_rho_GeV: float,
                      Gamma_rho_GeV: float, m_chi_GeV: float = M_CHI_GEV) -> float:
    """sigma/m(v) for Yukawa-like scattering with a dark-rho resonance propagator.

    Returns:
        sigma/m in cm^2/g. May return NaN if v is too small for the Born approximation.
    """
    from scipy.integrate import quad as _quad

    mu_GeV = m_chi_GeV / 2.0
    v = v_kms / C_KMS
    q = mu_GeV * v

    GEVSQ_TO_CM2 = HBAR_C_GEV_CM ** 2
    G_TO_GEV = 1.0 / 1.66053900266e-24

    # Born baseline: numerical quadrature
    def _integrand(cos_theta):
        q_squared = 4.0 * mu_GeV**2 * v**2 * (1.0 - cos_theta) / 2.0
        return (1.0 - cos_theta) / (q_squared + m_rho_GeV**2) ** 2

    integral_val, _ = _quad(_integrand, -1.0, 1.0, limit=100)
    sigma_T0_GeV2 = 2.0 * math.pi * alpha_D**2 * integral_val
    sigma_T0_cm2 = sigma_T0_GeV2 * HBAR_C_GEV_CM**2
    m_chi_g = m_chi_GeV / G_TO_GEV
    sigma_m0 = sigma_T0_cm2 / m_chi_g

    # Resonance factor
    F2_factor = (q**2 + m_rho_GeV**2) ** 2 / (
        (q**2 - m_rho_GeV**2) ** 2 + (m_rho_GeV * Gamma_rho_GeV) ** 2
    )

    sigma_m = sigma_m0 * F2_factor

    if not math.isfinite(sigma_m) or sigma_m < 0.0:
        return float("nan")
    return sigma_m


def velocity_at_resonance(m_rho_GeV: float, m_chi_GeV: float = M_CHI_GEV) -> float:
    """Solve q^2 = m_rho^2 for v_rel: (mu*v)^2 = m_rho^2 -> v_kms = C_KMS * m_rho / mu."""
    mu_GeV = m_chi_GeV / 2.0
    return C_KMS * m_rho_GeV / mu_GeV
