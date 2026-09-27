"""
T120.16 — Kinematic threshold check for inelastic DM self-scattering.

This test is the FIRST calculation that should have been done before
claiming the Hidden U(1) + pseudo-Dirac UV completion works.
It was added in response to the referee report (M1) and confirms
that the chosen parameters (Delta_m = 10 MeV) are outside the
allowed regime for self-interaction preservation.

Reference: Zhang 2016 Phys. Dark Univ. 15 (2017) 82-89, Eq. (8) and surrounding text.
"""
import numpy as np


# Zhang 2016's actual potential (Eq. 8):
# V(r) = [[0, alpha_D/r * exp(-m_V r)],
#         [alpha_D/r * exp(-m_V r), 2*Delta_m]]
#
# Key statement (Zhang 2016 text):
# "If we further increase the mass splitting BEYOND alpha_D^2 * m_D,
#  the quantum mechanical effect stops being effective.
#  As a result, the up-scattering is forbidden everywhere
#  and the dark matter self-interaction potential becomes
#  genuinely loop suppressed."
#
# Allowed regime: Delta_m < alpha_D^2 * m_chi


def zhang2016_well_depth(alpha_D, m_chi_MeV):
    """Zhang 2016's actual V_max formula: alpha_D^2 * m_chi (NOT alpha_D * m_phi or alpha_D * m_chi)."""
    return alpha_D**2 * m_chi_MeV


def zhang2016_allowed_splitting(alpha_D, m_chi_MeV):
    """Maximum Delta_m for which self-interaction is preserved (Zhang 2016)."""
    return zhang2016_well_depth(alpha_D, m_chi_MeV)


def ke_cm_eV(m_chi_GeV, v_km_s):
    """Center-of-mass kinetic energy for two equal-mass particles, in eV.

    KE_CM = (1/4) m_chi * v^2  (each particle has KE_lab = 1/2 m v^2; CM = half of lab)
    """
    m_chi_eV = m_chi_GeV * 1e9
    v_c = v_km_s * 1e3 / 2.998e8  # km/s → c
    return 0.25 * m_chi_eV * v_c**2


def kinematic_threshold_check(alpha_D, m_chi_GeV, Delta_m_MeV, v_km_s):
    """Check whether chi_1 chi_1 -> chi_2 chi_2 up-scattering is allowed.

    Returns dict with:
      - KE_CM_eV: available kinetic energy in CM frame
      - Delta_m_eV: mass splitting
      - Delta_m_over_KE: ratio (>>1 means forbidden)
      - zhang_allowed_keV: max Delta_m for self-interaction preservation
      - regime: 'preserved', 'transition', or 'forbidden'
    """
    KE = ke_cm_eV(m_chi_GeV, v_km_s)
    Delta_m_eV = Delta_m_MeV * 1e6
    m_chi_MeV = m_chi_GeV * 1000
    # zhang2016_allowed_splitting returns MeV (since m_chi_MeV is in MeV)
    zhang_allowed_MeV = zhang2016_allowed_splitting(alpha_D, m_chi_MeV)

    # Zhang's regime classification (Zhang 2016 text):
    # - "preserved": Delta_m << alpha_D^2 * m_chi (well below threshold)
    # - "transition": Delta_m ~ alpha_D^2 * m_chi (within order of magnitude)
    # - "forbidden": Delta_m >> alpha_D^2 * m_chi (well above threshold)
    zhang_allowed_eV = zhang_allowed_MeV * 1e6  # convert MeV to eV

    if Delta_m_eV < zhang_allowed_eV * 0.1:
        regime = 'preserved'
    elif Delta_m_eV < zhang_allowed_eV * 10:
        regime = 'transition'
    else:
        regime = 'forbidden'

    return {
        'KE_CM_eV': KE,
        'Delta_m_eV': Delta_m_eV,
        'Delta_m_over_KE': Delta_m_eV / KE,
        'zhang_allowed_MeV': zhang_allowed_MeV,
        'zhang_allowed_keV': zhang_allowed_MeV * 1000,
        'Delta_m_over_zhang_allowed': Delta_m_MeV / zhang_allowed_MeV,
        'regime': regime,
    }


def zhang2016_self_scattering_v(v_km_s, alpha_D, m_chi_GeV, Delta_m_MeV, m_phi_MeV):
    """Zhang 2016 self-scattering cross section per unit mass.

    If Delta_m > zhang_allowed splitting, returns NaN (up-scattering forbidden).
    Otherwise, returns sigma/m based on Born approximation.
    """
    result = kinematic_threshold_check(alpha_D, m_chi_GeV, Delta_m_MeV, v_km_s)
    if result['regime'] == 'forbidden':
        return float('nan')
    # In allowed regime, sigma/m ~ alpha_D^2 / (m_chi * v^4) ~ 1/v^2 (Born)
    # Numerical coefficient from Zhang 2016 Fig 4
    # sigma/m ~ 0.1 cm^2/g at v = 100 km/s for alpha_D = 0.01
    # We use a simple scaling: sigma/m ~ alpha_D^2 / m_chi * (100/v)^2 * 0.1
    m_chi_MeV = m_chi_GeV * 1000
    v_rel = max(v_km_s, 1.0)  # avoid divide by zero
    return 0.1 * (alpha_D / 0.01)**2 / (m_chi_GeV / 10) * (100 / v_rel)**2


# ============================================================
# Self-test: verify the original T120.11 parameters fail
# ============================================================
if __name__ == '__main__':
    alpha_D = 0.0015
    m_chi_GeV = 10.7
    Delta_m_MeV = 10.0
    m_phi_MeV = 30.0

    print("=" * 80)
    print("T120.16 — Kinematic threshold check")
    print("=" * 80)
    print()
    print(f"Parameters (T120.11):")
    print(f"  alpha_D   = {alpha_D}")
    print(f"  m_chi     = {m_chi_GeV} GeV")
    print(f"  Delta_m   = {Delta_m_MeV} MeV")
    print(f"  m_phi     = {m_phi_MeV} MeV")
    print()
    print(f"Zhang 2016 allowed Delta_m: {zhang2016_allowed_splitting(alpha_D, m_chi_GeV*1000):.4f} MeV = {zhang2016_allowed_splitting(alpha_D, m_chi_GeV*1000)*1000:.2f} keV")
    print(f"Our Delta_m / Zhang allowed = {Delta_m_MeV / (zhang2016_allowed_splitting(alpha_D, m_chi_GeV*1000)/1000):.1f}x")
    print()
    print("Per-channel kinematic check:")
    print(f"{'Channel':25s} {'v (km/s)':10s} {'KE_CM (eV)':12s} {'Delta_m/KE':12s} {'Regime':12s}")
    print("-" * 80)
    for label, v in [("Cloud-9", 28), ("dSph", 15), ("UFD-edge", 7), ("UFD-deep", 3), ("SPARC", 100), ("Cluster", 500)]:
        r = kinematic_threshold_check(alpha_D, m_chi_GeV, Delta_m_MeV, v)
        print(f"{label:25s} {v:10d} {r['KE_CM_eV']:12.3f} {r['Delta_m_over_KE']:12.2e} {r['regime']:12s}")
