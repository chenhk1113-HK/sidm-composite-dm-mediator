#!/usr/bin/env python
"""
T90.54 -- Hybrid multi-portal + resonance + Sommerfeld sigma/m(v).

The Grand Unified SIDM (Option B) parametric form:

  sigma/m(v) = sigma/m_portal_A(v) + sigma/m_portal_B(v) + sigma/m_resonant(v)

where each piece comes from a previously validated module:
  - sigma_m_portal_A(v) = T40 Yukawa via t90_v44_multi_portal.sigma_m_multi_portal
  - sigma_m_portal_B(v) = same, sum of two portals
  - sigma/m_resonant(v) = Breit-Wigner + Sommerfeld from t90_v50_resonant_sidm

Parameter vector (9D, all in physical units, NOT log):

    theta = (m_chi_GeV,
             m_phi_A_MeV, g_chi_A,
             m_phi_B_MeV, g_chi_B,
             E_R_eV, Gamma_R_eV,
             sigma_0_cm2_per_g,
             alpha_Y)

The two portals share a common m_chi (no multi-component DM at this level).
The resonance adds 3 free parameters (E_R, Gamma_R, sigma_0).
The Sommerfeld adds 1 (alpha_Y).

If we drop the portals (g_A = g_B = 0), the model reduces to T90.50 resonant.
If we drop the resonance (E_R -> infty, sigma_0 -> 0), the model reduces to
T90.45 multi-portal.

This is the simplest model that contains BOTH T90.50 and T90.45 as special
cases, enabling the Option B comparison: "what is the best the data can do
when both mechanisms are allowed?"
"""
from __future__ import annotations

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t90_v44_multi_portal import sigma_m_multi_portal
from t90_v50_resonant_sidm import sigma_m_resonant


def sigma_m_hybrid(v_kms: float, theta: tuple) -> dict:
    """Hybrid sigma/m(v) = multi-portal + resonance + Sommerfeld.

    Parameters
    ----------
    v_kms : float
        Relative velocity (km/s).
    theta : tuple of 9 floats
        (m_chi_GeV,
         m_phi_A_MeV, g_chi_A,
         m_phi_B_MeV, g_chi_B,
         E_R_eV, Gamma_R_eV,
         sigma_0_cm2_per_g,
         alpha_Y)

    Returns
    -------
    dict with keys:
        sigma_m_portal_cm2_per_g : sum of two portals (Sommerfeld not applied)
        sigma_m_resonant_cm2_per_g : Breit-Wigner + Sommerfeld contribution
        sigma_m_total_cm2_per_g : total sigma/m
    """
    (m_chi_GeV,
     m_phi_A_MeV, g_chi_A,
     m_phi_B_MeV, g_chi_B,
     E_R_eV, Gamma_R_eV,
     sigma_0_cm2_per_g,
     alpha_Y) = theta

    # --- Portal contribution (T90.44 multi-portal, T40 Yukawa) ---
    # Both portals share the same m_chi. sigma_m_multi_portal returns cm^2/g.
    if g_chi_A > 0 and g_chi_B > 0:
        sigma_m_portal = sigma_m_multi_portal(
            v_kms,
            m_phi_A_MeV, m_chi_GeV, g_chi_A,
            m_phi_B_MeV, m_chi_GeV, g_chi_B,
        )
    elif g_chi_A > 0:
        # Only portal A
        from t40_yukawa_sigma_m import sigma_m_cm2_per_g
        sigma_m_portal = sigma_m_cm2_per_g(v_kms, m_phi_A_MeV, m_chi_GeV, g_chi_A)
    elif g_chi_B > 0:
        from t40_yukawa_sigma_m import sigma_m_cm2_per_g
        sigma_m_portal = sigma_m_cm2_per_g(v_kms, m_phi_B_MeV, m_chi_GeV, g_chi_B)
    else:
        sigma_m_portal = 0.0

    # --- Resonance + Sommerfeld contribution (T90.50) ---
    if E_R_eV > 0 and Gamma_R_eV > 0 and sigma_0_cm2_per_g > 0:
        r_res = sigma_m_resonant(v_kms, m_chi_GeV, E_R_eV, Gamma_R_eV,
                                   sigma_0_cm2_per_g, alpha_Y)
        sigma_m_res = r_res["sigma_m_total"]
    else:
        sigma_m_res = 0.0

    sigma_m_total = sigma_m_portal + sigma_m_res

    return {
        "sigma_m_portal_cm2_per_g": float(sigma_m_portal),
        "sigma_m_resonant_cm2_per_g": float(sigma_m_res),
        "sigma_m_total_cm2_per_g": float(sigma_m_total),
    }


def hybrid_at_3_velocities(theta: tuple) -> dict:
    """Compute hybrid sigma/m at the 3 canonical velocities (Cloud-9, Galaxy, Bullet)."""
    sm_c9 = sigma_m_hybrid(28.0, theta)
    sm_gal = sigma_m_hybrid(100.0, theta)
    sm_bul = sigma_m_hybrid(3000.0, theta)
    return {
        "sigma_m_Cloud9": sm_c9["sigma_m_total_cm2_per_g"],
        "sigma_m_Galaxy": sm_gal["sigma_m_total_cm2_per_g"],
        "sigma_m_Bullet": sm_bul["sigma_m_total_cm2_per_g"],
        "portal_Cloud9": sm_c9["sigma_m_portal_cm2_per_g"],
        "portal_Galaxy": sm_gal["sigma_m_portal_cm2_per_g"],
        "portal_Bullet": sm_bul["sigma_m_portal_cm2_per_g"],
        "resonant_Cloud9": sm_c9["sigma_m_resonant_cm2_per_g"],
        "resonant_Galaxy": sm_gal["sigma_m_resonant_cm2_per_g"],
        "resonant_Bullet": sm_bul["sigma_m_resonant_cm2_per_g"],
    }


def evaluate_hybrid_point(theta: tuple) -> dict:
    """Evaluate hybrid at the 3 canonical velocities and report channel satisfaction."""
    r = hybrid_at_3_velocities(theta)
    c9_ok = 30.0 < r["sigma_m_Cloud9"] < 500.0
    gal_ok = r["sigma_m_Galaxy"] < 2.0
    bul_ok = r["sigma_m_Bullet"] < 0.5
    return {
        **r,
        "Cloud9_OK": c9_ok,
        "Galaxy_OK": gal_ok,
        "Bullet_OK": bul_ok,
        "all_three_OK": c9_ok and gal_ok and bul_ok,
        "n_channels_satisfied": int(c9_ok) + int(gal_ok) + int(bul_ok),
    }


# --------------------------------------------------------------------------
# Priors (all log-uniform on physical quantities)
# --------------------------------------------------------------------------
# T90.54 prior ranges (9D)
LOG_M_CHI_GEV_RANGE = (0.5, 3.0)        # 3 GeV to 1 TeV
LOG_M_PHI_A_MEV_RANGE = (1.5, 4.0)     # 30 MeV to 10 TeV (heavy portal)
G_CHI_A_RANGE = (0.0, 2.0)             # 0 (off) to 2 (moderate-strong)
LOG_M_PHI_B_MEV_RANGE = (-0.5, 2.0)    # 0.3 MeV to 100 MeV (light portal)
G_CHI_B_RANGE = (0.0, 0.5)             # 0 (off) to 0.5 (weak)
LOG_E_R_EV_RANGE = (0.5, 5.0)          # 3 eV to 100 keV (includes off-resonance)
LOG_GAMMA_R_EV_RANGE = (-3.0, 3.0)     # 1 meV to 1 keV
LOG_SIGMA_0_RANGE = (-5.0, 0.0)        # 1e-5 to 1 cm^2/g (sigma_0=0 = off)
LOG_ALPHA_Y_RANGE = (-5.0, 0.0)        # 1e-5 to 1

LOG_RANGES = [
    LOG_M_CHI_GEV_RANGE,
    LOG_M_PHI_A_MEV_RANGE,
    G_CHI_A_RANGE,             # linear
    LOG_M_PHI_B_MEV_RANGE,
    G_CHI_B_RANGE,             # linear
    LOG_E_R_EV_RANGE,
    LOG_GAMMA_R_EV_RANGE,
    LOG_SIGMA_0_RANGE,
    LOG_ALPHA_Y_RANGE,
]
PARAM_NAMES = [
    "log_m_chi_GeV",
    "log_m_phi_A_MeV",
    "g_chi_A",
    "log_m_phi_B_MeV",
    "g_chi_B",
    "log_E_R_eV",
    "log_Gamma_R_eV",
    "log_sigma_0",
    "log_alpha_Y",
]
IS_LOG = [True, True, False, True, False, True, True, True, True]


def prior_transform_9(u):
    """9D unit cube -> mixed log/linear parameter vector.

    Convention: theta output is in the same units as the LOG_RANGES bounds.
    For IS_LOG=True params, theta[i] is log10(x). For IS_LOG=False params,
    theta[i] is x directly.

    Layout (matches T90.54):
      [log_m_chi, log_m_phi_A, g_A (linear),
       log_m_phi_B, g_B (linear),
       log_E_R, log_Gamma, log_sigma_0, log_alpha_Y]
    """
    theta = np.zeros(9)
    for i in range(9):
        lo, hi = LOG_RANGES[i]
        theta[i] = lo + u[i] * (hi - lo)  # direct mapping, units match LOG_RANGES
    return theta


def unpack_theta(theta_log):
    """Convert log-mixed theta vector to the 9-tuple physical form expected
    by sigma_m_hybrid."""
    m_chi = 10.0 ** theta_log[0]
    m_phi_A = 10.0 ** theta_log[1]
    g_A = theta_log[2]                            # linear
    m_phi_B = 10.0 ** theta_log[3]
    g_B = theta_log[4]                            # linear
    E_R = 10.0 ** theta_log[5]
    Gamma = 10.0 ** theta_log[6]
    sigma_0 = 10.0 ** theta_log[7]
    alpha_Y = 10.0 ** theta_log[8]
    return (m_chi, m_phi_A, g_A, m_phi_B, g_B,
            E_R, Gamma, sigma_0, alpha_Y)


if __name__ == "__main__":
    # Smoke print
    theta = (30.0, 700.0, 0.5, 5.0, 0.10, 65.0, 0.1, 0.01, 0.01)
    out = evaluate_hybrid_point(theta)
    print(f"[T90.54] At hybrid point:")
    print(f"  sigma/m(Cloud-9)  = {out['sigma_m_Cloud9']:.3f}  "
          f"(portal {out['portal_Cloud9']:.3f} + resonant {out['resonant_Cloud9']:.3f})")
    print(f"  sigma/m(Galaxy)   = {out['sigma_m_Galaxy']:.3f}")
    print(f"  sigma/m(Bullet)   = {out['sigma_m_Bullet']:.4f}")
    print(f"  Channel satisfaction: C9={out['Cloud9_OK']} Gal={out['Galaxy_OK']} "
          f"Bul={out['Bullet_OK']}  ({out['n_channels_satisfied']}/3)")
