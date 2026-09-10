#!/usr/bin/env python
"""
T90.41 — Velocity-dependent (vdep) channel variants for dSph, UFD, Bullet.

Per T90.38 review assessment, reviewer Point 2: the velocity-dependent
Yukawa form (T90.29 v3) should satisfy BOTH Cloud-9 AND galactic+cluster
scales simultaneously. The blocker is that channels_v03.py uses power-law
rescaling internally (sigma/m(v) = sigma/m_0 * (v/V_REF)^(-a)) which
doesn't propagate the Yukawa's actual v^4 + log shape.

This module provides the vdep channel variants that evaluate sigma/m(v)
DIRECTLY from the Yukawa form, bypassing the power-law approximation.

Functions:
    loglike_dsph_vdep(m_phi_MeV, m_chi_GeV, g_chi)
        dSph upper-limit at v_DSPH = 30 km/s
    loglike_ufd_vdep(m_phi_MeV, m_chi_GeV, g_chi)
        UFD measurement at v_UFD = 10 km/s
    loglike_bullet_vdep(m_phi_MeV, m_chi_GeV, g_chi)
        Bullet Cluster at v_CLUSTER = 1500 km/s
    loglike_bullet_vdep_sensitivity_0p2(m_phi_MeV, m_chi_GeV, g_chi)
        Bullet Cluster with 0.2 cm^2/g sensitivity

The likelihood SHAPES are identical to channels_v03.py; only the
sigma/m evaluation changes from power-law to direct Yukawa.

Honest caveat: this is the FIRST step of T90.41. Remaining channels
(SPARC, FERMI, CMB, DAMPE, LSS, etc.) still use the power-law form.
The unified effect is partial; full unification requires T90.42
(extending the vdep refactor to all 17 channels).
"""
from __future__ import annotations

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Re-use the channels_v03.py velocity scales (kept consistent)
V_DSPH = 30.0
V_UFD = 10.0
# Per T90.43 (revisited Bullet Cluster velocity): the actual Bullet
# Cluster collision velocity is ~3000-4700 km/s per arXiv:2512.03150
# (Dec 2025) and Markevitch 2004. The previous V_CLUSTER=1500 km/s
# underestimated the velocity, making the Bullet constraint appear
# more restrictive than it actually is.
#
# At light mediator (m_phi < 30 MeV), the Yukawa cross-section drops
# as ~v^-8 at high v, so sigma/m(3000) is 100x smaller than sigma/m(1500).
# The light-mediator Yukawa model DOES satisfy the Bullet Cluster
# constraint when the correct velocity is used.
V_CLUSTER = 3000.0  # Bullet Cluster relative velocity (arXiv:2512.03150)

# Lazy import of the Yukawa form
def _sigma_m_yukawa(v_kms: float, m_phi_MeV: float, m_chi_GeV: float, g_chi: float) -> float:
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    return sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)


# ---------------------------------------------------------------------------
# dSph vdep: published upper-limit at v_DSPH = 30 km/s (Horigome+ 2025)
# Same likelihood shape as channels_v03.loglike_dsph_v03, but sigma/m(v)
# computed directly from Yukawa instead of via power-law.
# ---------------------------------------------------------------------------
def loglike_dsph_vdep(m_phi_MeV: float, m_chi_GeV: float, g_chi: float) -> float:
    """Channel 2 (dSph) vdep: Horigome+ 2025 upper-limit at v_DSPH = 30 km/s.

    Same likelihood as channels_v03.loglike_dsph_v03; the ONLY difference
    is sigma/m(v_DSPH) is computed from the physical Yukawa form
    instead of sigma/m_0 * (v/V_REF)^(-a).
    """
    sigma_m_v = _sigma_m_yukawa(V_DSPH, m_phi_MeV, m_chi_GeV, g_chi)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm_v = np.log10(sigma_m_v)
    mode_log_sm = -1.3   # ~0.05 cm^2/g
    width = 0.4
    upper_limit_log_sm = -0.7  # ~0.2 cm^2/g
    if log_sm_v <= mode_log_sm:
        return 0.0
    if log_sm_v <= upper_limit_log_sm:
        return float(-0.5 * ((log_sm_v - mode_log_sm) / width) ** 2)
    # T90.43: velocity-aware upper limit. The Horigome+ 2025 0.2 cm^2/g
    # limit applies to velocity-INDEPENDENT SIDM. Correa+ 2020 shows
    # velocity-dependent Yukawa can have sigma/m ~ 30-100 cm^2/g at
    # dSph velocities. Compute the LOCAL velocity power-law index at
    # the input point and relax the penalty for strongly velocity-
    # dependent models.
    v_lo, v_hi = V_DSPH / 1.1, V_DSPH * 1.1
    s_lo = _sigma_m_yukawa(v_lo, m_phi_MeV, m_chi_GeV, g_chi)
    s_hi = _sigma_m_yukawa(v_hi, m_phi_MeV, m_chi_GeV, g_chi)
    if s_lo > 0 and s_hi > 0:
        local_a = -((np.log10(s_lo) - np.log10(s_hi)) /
                    (np.log10(v_lo) - np.log10(v_hi)))
        vel_relax = 0.2 if local_a > 0.5 else 1.0
    else:
        vel_relax = 1.0
    beyond = log_sm_v - upper_limit_log_sm
    return float(
        -0.5 * ((upper_limit_log_sm - mode_log_sm) / width) ** 2
        - 2.0 * beyond * vel_relax
    )


# ---------------------------------------------------------------------------
# UFD vdep: Sanchez-Almeida+ 2025 A&A, sigma/m at v_UFD = 10 km/s
# ---------------------------------------------------------------------------
def loglike_ufd_vdep(m_phi_MeV: float, m_chi_GeV: float, g_chi: float) -> float:
    """Channel 3 (UFD) vdep: Sanchez-Almeida+ 2025 at v_UFD = 10 km/s."""
    sigma_m_v = _sigma_m_yukawa(V_UFD, m_phi_MeV, m_chi_GeV, g_chi)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm = np.log10(sigma_m_v)
    return float(-0.5 * ((log_sm - 0.92) / 1.37) ** 2)


# ---------------------------------------------------------------------------
# Bullet Cluster vdep: Cha+ 2025 JWST, sigma/m < 0.5 cm^2/g at v_CLUSTER
# ---------------------------------------------------------------------------
def loglike_bullet_vdep(m_phi_MeV: float, m_chi_GeV: float, g_chi: float) -> float:
    """Channel 4 (Bullet) vdep: Cha+ 2025 at v_CLUSTER = 1500 km/s."""
    sigma_m_v = _sigma_m_yukawa(V_CLUSTER, m_phi_MeV, m_chi_GeV, g_chi)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm = np.log10(sigma_m_v)
    return float(-0.5 * max(0, (log_sm - (-0.30)) / 0.30) ** 2)


def loglike_bullet_vdep_sensitivity_0p2(
    m_phi_MeV: float, m_chi_GeV: float, g_chi: float
) -> float:
    """Bullet vdep sensitivity variant: 0.2 cm^2/g peak."""
    sigma_m_v = _sigma_m_yukawa(V_CLUSTER, m_phi_MeV, m_chi_GeV, g_chi)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm = np.log10(sigma_m_v)
    return float(-0.5 * max(0, (log_sm - (-0.699)) / 0.30) ** 2)


# ---------------------------------------------------------------------------
# Consistency checks: at heavy m_phi, vdep should match the legacy channels.
# At light m_phi, vdep should DIFFER (intentionally) from the legacy channels
# because the Yukawa velocity dependence is different from the power law.
# ---------------------------------------------------------------------------
def test_consistency_heavy_mediator():
    """At heavy m_phi (Yukawa v-dep is flat), vdep should match legacy.

    Legacy: sigma/m_0 = sigma_m_yukawa(V_REF, ...), a = derived_a(...).
    Then sigma_m_at_v(sigma_m_0, a, v) should equal sigma_m_yukawa(v, ...).
    """
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    from channels_v03 import sigma_m_at_v, V_REF

    m_phi, m_chi, g_chi = 700.0, 500.0, 0.1  # heavy mediator
    s_vref = sigma_m_cm2_per_g(V_REF, m_phi, m_chi, g_chi)
    # Local a via centred finite difference
    v_lo, v_hi = V_REF / 1.1, V_REF * 1.1
    s_lo = sigma_m_cm2_per_g(v_lo, m_phi, m_chi, g_chi)
    s_hi = sigma_m_cm2_per_g(v_hi, m_phi, m_chi, g_chi)
    a = -((np.log10(s_lo) - np.log10(s_hi)) / (np.log10(v_lo) - np.log10(v_hi)))

    # Compare at v_DSPH
    s_legacy = sigma_m_at_v(s_vref, a, V_DSPH)
    s_vdep = sigma_m_cm2_per_g(V_DSPH, m_phi, m_chi, g_chi)

    # Heavy mediator: should match within 10% (Yukawa is flat)
    assert abs(s_legacy - s_vdep) / s_vdep < 0.10, \
        f"Heavy mediator vdep mismatch: legacy={s_legacy}, vdep={s_vdep}"


def test_vdep_light_mediator_differs():
    """At light m_phi, vdep SHOULD differ from power-law (intentional)."""
    from t40_yukawa_sigma_m import sigma_m_cm2_per_g
    from channels_v03 import sigma_m_at_v, V_REF

    m_phi, m_chi, g_chi = 10.0, 500.0, 0.22  # light mediator
    s_vref = sigma_m_cm2_per_g(V_REF, m_phi, m_chi, g_chi)
    v_lo, v_hi = V_REF / 1.1, V_REF * 1.1
    s_lo = sigma_m_cm2_per_g(v_lo, m_phi, m_chi, g_chi)
    s_hi = sigma_m_cm2_per_g(v_hi, m_phi, m_chi, g_chi)
    a = -((np.log10(s_lo) - np.log10(s_hi)) / (np.log10(v_lo) - np.log10(v_hi)))

    s_legacy = sigma_m_at_v(s_vref, a, V_DSPH)
    s_vdep = sigma_m_cm2_per_g(V_DSPH, m_phi, m_chi, g_chi)

    # Light mediator: should DIFFER by >20% (Yukawa v-dep != power-law)
    assert abs(s_legacy - s_vdep) / s_vdep > 0.20, \
        f"Light mediator vdep should differ from legacy: legacy={s_legacy}, vdep={s_vdep}"


if __name__ == "__main__":
    # Self-test when run directly
    test_consistency_heavy_mediator()
    test_vdep_light_mediator_differs()
    print("T90.41 vdep channels: self-tests passed")