"""
T43 — Inelastic Dark Matter (iDM) cross-section module.

Motivation
----------
T41's headline finding: simple Yukawa SIDM gives a < 0 (sigma/m
INCREASES with v), but the data wants a > 0 (sigma/m DECREASES with v).
Delta_a = 2.75 sigma.

Inelastic DM (Tucker-Smith & Weiner 2001, PRD 64, 043502) provides a
natural resolution. The two-state system (chi_1 lighter, chi_2 heavier
with mass splitting delta) has:

    chi_1 + chi_1 -> chi_2 + chi_2   [endothermic, requires KE > delta]

At low velocity (v_thermal < sqrt(2 delta / m_chi)), the reaction is
kinematically SUPPRESSED. So sigma/m(v) *decreases* with v at low v,
then rises at high v (where delta is negligible). This is exactly the
a > 0 signature the data wants.

Cross-section (Born approx, inelastic generalization of Finkbeiner+09):

  sigma_T(v, delta) = sigma_T_yukawa(v) * F_inel(v)
  F_inel(v) = exp(-delta / (m_chi v^2 / 4))      [kinematic suppression]
                                                  = exp(-2 delta / (m_chi v^2 / 2))

The exponential cut-off in velocity gives the inverted-Yukawa signature.
"""
from __future__ import annotations
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t40_yukawa_sigma_m as yukawa


# Conversion: 1 GeV = 1000 MeV; v in km/s requires careful unit handling
# delta in MeV, m_chi in GeV, v in km/s
# Energy scale: delta vs (1/2) m_chi v^2
# (1/2) m_chi v_thermal^c2 = delta (threshold)
# v_threshold = sqrt(2 delta / m_chi) (in natural units)
# In km/s: convert via c = 3e5 km/s
# 1 GeV = 1e9 eV; thermal KE = (1/2) m_chi v^2
# v^2 (km/s)^2 = 2 delta / (m_chi_GeV * 1e9 * eV) * (c^2) / (eV per GeV)
# Easier: v_threshold in km/s = sqrt(2 * delta_MeV / m_chi_GeV) * (c * 1e-3 * 1e-3)
# Even easier: use dimensionless beta = (m_chi v / (sqrt(2) m_phi)) as in T40,
# and threshold condition: m_chi v_threshold^2 / 4 = delta
# v_threshold^2 = 4 delta / m_chi
# v_threshold (km/s) = sqrt(4 delta_MeV / (m_chi_GeV * 1000)) * (c_km_s_to_natural)
# (1/2) m_chi v^2 = delta, with v in km/s, m_chi in GeV, delta in MeV
# m_chi_GeV * 1000 = m_chi_MeV
# (1/2) m_chi_MeV * (v/c)^2 = delta_MeV
# v = c * sqrt(2 delta_MeV / m_chi_MeV)
# v_threshold = 299792 km/s * sqrt(2 * delta_MeV / (m_chi_GeV * 1000))


C_KMS = 299792.458


def v_threshold_km_s(delta_MeV: float, m_chi_GeV: float) -> float:
    """Threshold velocity for endothermic scattering chi_1 chi_1 -> chi_2 chi_2.

    At v < v_threshold, the reaction is exponentially suppressed.
    """
    m_chi_MeV = m_chi_GeV * 1000.0
    return C_KMS * np.sqrt(2.0 * delta_MeV / m_chi_MeV)


def inelastic_suppression(v_kms: float, delta_MeV: float, m_chi_GeV: float) -> float:
    """Kinematic suppression factor F_inel(v).

    F_inel(v) = exp(-2 delta / (m_chi v^2 / 2))
              = exp(-delta / (m_chi v^2 / 4))

    Threshold: when (1/2) m_chi v^2 = delta, F_inel = e^-2 ~ 0.135.
    """
    m_chi_MeV = m_chi_GeV * 1000.0
    if v_kms <= 0:
        return 0.0
    if delta_MeV <= 0:
        # Elastic limit: no suppression
        return 1.0
    # Natural-units v: v/c, then (1/2) m_chi_MeV (v/c)^2 = KE / delta
    v_over_c = v_kms / C_KMS
    ke_over_delta = 0.5 * m_chi_MeV * v_over_c ** 2 / delta_MeV
    if ke_over_delta <= 0:
        return 0.0
    return float(np.exp(-1.0 / ke_over_delta))  # exp(-delta / KE)


def sigma_m_inelastic(v_kms: float, m_phi_MeV: float, m_chi_GeV: float,
                       g_chi: float, delta_MeV: float) -> float:
    """Inelastic DM cross-section sigma/m at velocity v.

    sigma/m_inel(v) = sigma/m_yukawa(v) * F_inel(v)

    For delta > 0, sigma/m is suppressed at v < v_threshold and
    approaches the elastic Yukawa at v >> v_threshold.
    """
    sm_yukawa = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)
    F = inelastic_suppression(v_kms, delta_MeV, m_chi_GeV)
    return sm_yukawa * F


def derived_a_inelastic(m_phi_MeV: float, m_chi_GeV: float, g_chi: float,
                          delta_MeV: float,
                          v_lo_kms: float = 50.0, v_hi_kms: float = 200.0) -> float:
    """Velocity power-law index for inelastic DM.

    Returns a > 0 if delta is large enough to suppress low-v scattering.
    """
    s1 = sigma_m_inelastic(v_lo_kms, m_phi_MeV, m_chi_GeV, g_chi, delta_MeV)
    s2 = sigma_m_inelastic(v_hi_kms, m_phi_MeV, m_chi_GeV, g_chi, delta_MeV)
    if s1 <= 0 or s2 <= 0:
        return -2.0
    a = (np.log10(s1) - np.log10(s2)) / (np.log10(v_lo_kms) - np.log10(v_hi_kms))
    return float(a)


def g_chi_to_match_sigma_m_0_inelastic(target_sigma_m_0: float, m_phi_MeV: float,
                                        m_chi_GeV: float, delta_MeV: float,
                                        v_ref_kms: float = 100.0) -> float:
    """Solve g_chi such that sigma/m_inel(v_ref) = target.

    Note: g_chi^4 scaling still holds because the inelastic factor
    is independent of g_chi (it's a kinematic suppression).
    """
    # First get g_chi=1 elastic result
    sm_unit = sigma_m_inelastic(v_ref_kms, m_phi_MeV, m_chi_GeV, 1.0, delta_MeV)
    if sm_unit <= 0:
        return None
    if target_sigma_m_0 < sm_unit:
        # Suppression: need g_chi > 1
        g_chi = (target_sigma_m_0 / sm_unit) ** 0.25
    else:
        g_chi = (target_sigma_m_0 / sm_unit) ** 0.25
    return float(g_chi)


if __name__ == "__main__":
    print("=" * 80)
    print("T43 — Inelastic DM cross-section module (smoke test)")
    print("=" * 80)

    # Test 1: elastic case (delta = 0) should reduce to T40
    print("\nElastic case (delta = 0):")
    sm_elastic = sigma_m_inelastic(100.0, 100.0, 40.0, 0.5, 0.0)
    sm_yukawa = yukawa.sigma_m_cm2_per_g(100.0, 100.0, 40.0, 0.5)
    print(f"  inelastic (=T40 elastic): {sm_elastic:.3e} cm^2/g")
    print(f"  Yukawa direct:             {sm_yukawa:.3e} cm^2/g")
    assert abs(sm_elastic - sm_yukawa) / sm_yukawa < 1e-6, "Mismatch at delta=0!"

    # Test 2: delta > 0 should suppress low-v
    print("\nInelastic case (delta = 1 MeV, m_chi = 40 GeV):")
    v_thr = v_threshold_km_s(1.0, 40.0)
    print(f"  v_threshold = {v_thr:.1f} km/s")
    for v in [10.0, v_thr * 0.5, v_thr, v_thr * 2.0, 1000.0]:
        F = inelastic_suppression(v, 1.0, 40.0)
        sm = sigma_m_inelastic(v, 100.0, 40.0, 0.5, 1.0)
        sm_y = yukawa.sigma_m_cm2_per_g(v, 100.0, 40.0, 0.5)
        print(f"  v = {v:>7.1f} km/s: F_inel = {F:.3e}, sigma/m = {sm:.3e} cm^2/g")

    # Test 3: the smoking gun — derive a for various delta
    print("\nScanning delta to find a > 0 (the data wants this):")
    print(f"  {'delta [MeV]':>12} {'v_thr [km/s]':>14} {'a (50-200 km/s)':>18}")
    for delta in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0]:
        v_thr = v_threshold_km_s(delta, 40.0)
        a = derived_a_inelastic(100.0, 40.0, 0.5, delta)
        print(f"  {delta:>12.2f} {v_thr:>14.1f} {a:>18.3f}")

    # Test 4: can we match T39 sigma/m_0 = 1.57 with a > 0?
    print("\nMatching T39 sigma/m_0 = 1.57 cm^2/g WITH a > 0:")
    for delta in [0.5, 1.0, 2.0, 5.0]:
        g = g_chi_to_match_sigma_m_0_inelastic(1.57, 100.0, 40.0, delta)
        if g is None:
            continue
        a = derived_a_inelastic(100.0, 40.0, g, delta)
        sm_at_v = sigma_m_inelastic(100.0, 100.0, 40.0, g, delta)
        sm_at_10 = sigma_m_inelastic(10.0, 100.0, 40.0, g, delta)
        sm_at_1000 = sigma_m_inelastic(1000.0, 100.0, 40.0, g, delta)
        print(f"  delta = {delta:>4.1f} MeV: g_chi = {g:.4f}, "
              f"a = {a:>6.3f}, sigma/m @v=10: {sm_at_10:.3e}, "
              f"@v=100: {sm_at_v:.3e}, @v=1000: {sm_at_1000:.3e}")
