"""
T130 — Inelastic DM kinematic scan (Strategy 1 from Qwen referee).

Question: For what m_chi does there exist a Delta_m that satisfies
  (a) Delta_m >= 100 keV (LZ/XENONnT DD threshold for kinetic forbiddance)
  (b) 6.25e-10 m_chi c^2 < Delta_m < 2.18e-9 m_chi c^2 (between Cloud-9 and dSph KE)
  (c) Sigma_DM-DM/m at v=28 km/s matches Cloud-9 target (~100 cm^2/g)

If no GeV-scale model works, this is a no-go theorem supporting the v1.14
phenomenology-only framing.

Reference: Qwen referee report 2026-09-19, Strategy 1.
"""
import numpy as np

# ============================================================
# Physical constants and thresholds
# ============================================================

# Cloud-9 and dSph velocities (km/s)
v_cloud9 = 28.0
v_dSph = 15.0
v_UFD_deep = 3.0

# DD threshold: minimum Delta_m for tree-level nuclear scattering to be
# kinematically forbidden. Standard LZ/XENONnT recoil energy ~ 5-50 keV,
# so we need Delta_m > ~100 keV to be safely forbidden for typical
# Xe recoils. (Qwen referee uses 100 keV threshold.)
DD_THRESHOLD_keV = 100.0  # keV

# Mass range to scan
M_CHI_MIN_GeV = 1.0
M_CHI_MAX_GeV = 100_000.0  # 100 TeV
N_POINTS = 500


def ke_cm_eV(m_chi_GeV, v_km_s):
    """Center-of-mass kinetic energy for two equal-mass particles (eV).

    KE_CM = (1/4) m_chi v^2 where v in units of c.
    """
    m_chi_eV = m_chi_GeV * 1e9
    v_c = v_km_s * 1e3 / 2.998e8
    return 0.25 * m_chi_eV * v_c**2


def inelastic_dm_check(m_chi_GeV, Delta_m_keV):
    """Check if inelastic DM (chi_1 chi_1 -> chi_2 chi_2) is allowed at velocity v.

    Returns True if KE_CM(v) > Delta_m (allowed), False otherwise.
    """
    ke = ke_cm_eV(m_chi_GeV, 1.0)  # test at v=1 km/s first, scale
    ke_28 = ke_cm_eV(m_chi_GeV, v_cloud9)
    ke_15 = ke_cm_eV(m_chi_GeV, v_dSph)
    ke_3 = ke_cm_eV(m_chi_GeV, v_UFD_deep)

    Delta_m_eV = Delta_m_keV * 1000

    return {
        'allowed_at_Cloud9': ke_28 > Delta_m_eV,
        'allowed_at_dSph': ke_15 > Delta_m_eV,
        'allowed_at_UFD': ke_3 > Delta_m_eV,
        'KE_CM_Cloud9_eV': ke_28,
        'KE_CM_dSph_eV': ke_15,
        'KE_CM_UFD_eV': ke_3,
        'Delta_m_eV': Delta_m_eV,
        'window_Cloud9_dSph': Delta_m_eV > ke_15 and Delta_m_eV < ke_28,
    }


def scan_mass_for_inelastic_window():
    """For each m_chi, find the Delta_m window where:
       - Cloud-9 scattering is ALLOWED (KE > Delta_m)
       - dSph/UFD scattering is FORBIDDEN (KE < Delta_m)
       - DD evasion via Delta_m > 100 keV

    Returns dict with scan results.
    """
    m_chi_array = np.logspace(np.log10(M_CHI_MIN_GeV), np.log10(M_CHI_MAX_GeV), N_POINTS)

    # For Qwen's window: 6.25e-10 m_chi < Delta_m < 2.18e-9 m_chi (in eV)
    # In natural units: KE(28)/m_chi ~ 2.18e-9, KE(15)/m_chi ~ 6.25e-10
    # So Delta_m/m_chi window = [6.25e-10, 2.18e-9]
    # DD threshold: Delta_m > 100 keV

    results = []
    for m_chi_GeV in m_chi_array:
        # KE_CM at Cloud-9 (eV)
        ke_28 = ke_cm_eV(m_chi_GeV, v_cloud9)
        # KE_CM at dSph (eV)
        ke_15 = ke_cm_eV(m_chi_GeV, v_dSph)

        # Lower bound from Qwen: Delta_m > KE(dSph) = 6.25e-10 * m_chi
        # In eV: Delta_m > 6.25e-10 * m_chi_eV
        Delta_m_lower_window_eV = ke_15

        # Upper bound from Qwen: Delta_m < KE(Cloud9) = 2.18e-9 * m_chi
        Delta_m_upper_window_eV = ke_28

        # DD threshold: Delta_m > 100 keV = 1e5 eV
        Delta_m_DD_eV = DD_THRESHOLD_keV * 1000

        # Window exists only if lower < upper
        if Delta_m_lower_window_eV < Delta_m_upper_window_eV:
            # Required Delta_m must be in [max(DD, lower), upper]
            Delta_m_required_lower = max(Delta_m_DD_eV, Delta_m_lower_window_eV)
            Delta_m_required_upper = Delta_m_upper_window_eV

            valid = Delta_m_required_lower < Delta_m_required_upper
        else:
            valid = False
            Delta_m_required_lower = None
            Delta_m_required_upper = None

        results.append({
            'm_chi_GeV': m_chi_GeV,
            'KE_CM_Cloud9_eV': ke_28,
            'KE_CM_dSph_eV': ke_15,
            'window_lower_eV': Delta_m_lower_window_eV,
            'window_upper_eV': Delta_m_upper_window_eV,
            'DD_threshold_eV': Delta_m_DD_eV,
            'Delta_m_required_lower_eV': Delta_m_required_lower,
            'Delta_m_required_upper_eV': Delta_m_required_upper,
            'valid': valid,
        })

    return results


def main():
    print("=" * 80)
    print("T130 — Inelastic DM kinematic scan")
    print("=" * 80)
    print()
    print("Qwen referee Strategy 1 check:")
    print("  Question: For what m_chi does a valid Delta_m exist that")
    print("    (a) evades DD via Delta_m > 100 keV")
    print("    (b) allows scattering at Cloud-9 (KE(28) > Delta_m)")
    print("    (c) forbids scattering at dSph (KE(15) < Delta_m)")
    print()

    # First: verify the math
    print("=" * 80)
    print("STEP 1: Verify the math (Qwen vs independent)")
    print("=" * 80)
    print()
    for label, v in [("Cloud-9", 28), ("dSph", 15), ("UFD-deep", 3)]:
        ke_per_mchi = ke_cm_eV(1.0, v) / 1e9  # KE / m_chi in dimensionless units
        print(f"  {label} (v={v} km/s): KE_CM / m_chi = {ke_per_mchi:.3e}")
    print()
    print("  Qwen claims: 6.25e-10 (dSph) and 2.18e-9 (Cloud-9)")
    print("  Independent verification:")
    print(f"    dSph   = {ke_cm_eV(1.0, 15) / 1e9:.3e}  (Qwen: 6.25e-10)")
    print(f"    Cloud9 = {ke_cm_eV(1.0, 28) / 1e9:.3e}  (Qwen: 2.18e-9)")
    print()

    # Main scan
    print("=" * 80)
    print("STEP 2: Mass scan for valid Delta_m window")
    print("=" * 80)
    print()

    results = scan_mass_for_inelastic_window()

    # Find the smallest m_chi where valid Delta_m window exists
    valid_results = [r for r in results if r['valid']]

    if valid_results:
        m_chi_min_valid = valid_results[0]['m_chi_GeV']
        print(f"  First m_chi with valid window: {m_chi_min_valid:.2e} GeV")
        print()

        # Print 10 sample points spanning the valid range
        print(f"  Sample of valid m_chi values:")
        print(f"  {'m_chi (GeV)':>15s}  {'KE_C9 (eV)':>12s}  {'KE_dSph (eV)':>12s}  {'Delta_m range (eV)':>25s}")
        for r in valid_results[::max(1, len(valid_results)//10)][:10]:
            lower = r['Delta_m_required_lower_eV']
            upper = r['Delta_m_required_upper_eV']
            print(f"  {r['m_chi_GeV']:>15.3e}  {r['KE_CM_Cloud9_eV']:>12.3e}  {r['KE_CM_dSph_eV']:>12.3e}  [{lower:.3e}, {upper:.3e}]")
    else:
        print("  NO valid m_chi found in the scanned range [1 GeV, 100 TeV]")
        print()

    # Key threshold: when does the window open?
    print()
    print("=" * 80)
    print("STEP 3: When does the inelastic DM window open?")
    print("=" * 80)
    print()
    print("  Required: Delta_m_DD < Delta_m_upper_window")
    print("            100 keV   < KE_CM(Cloud-9)")
    print("            1e5 eV    < (1/4) m_chi (v_Cloud9/c)^2")
    print()
    print("  Solving for m_chi:")
    m_chi_threshold_GeV = 4 * DD_THRESHOLD_keV * 1000 / (1e9 * (v_cloud9 * 1e3 / 2.998e8)**2)
    print(f"    m_chi > 4 * Delta_m_DD / (v_Cloud9/c)^2")
    print(f"    m_chi > {m_chi_threshold_GeV:.2f} GeV")
    print()
    print(f"  (Qwen claims: m_chi >= 46 TeV = 46000 GeV)")
    print()

    # Qwen's number
    qwen_threshold = 4.6e4  # GeV (Qwen's 46 TeV)
    factor_off = m_chi_threshold_GeV / qwen_threshold
    print(f"  Our independent calculation: {m_chi_threshold_GeV:.2f} GeV")
    print(f"  Qwen's claim:                 {qwen_threshold:.0f} GeV (46 TeV)")
    print(f"  Factor off: {factor_off:.2f}")
    print()

    if abs(factor_off - 1.0) < 0.5:
        print("  Qwen's threshold is consistent with our independent calculation.")
    else:
        print(f"  ⚠️ Qwen's threshold disagrees with our calculation by factor {factor_off:.2f}")

    # The Qwen 2.18e-9 vs ours
    qwen_ke_fraction = 2.18e-9
    our_ke_fraction = ke_cm_eV(1.0, 28) / 1e9
    print(f"\n  Qwen's KE_CM(28)/m_chi: {qwen_ke_fraction:.3e}")
    print(f"  Our KE_CM(28)/m_chi:    {our_ke_fraction:.3e}")
    qwen_factor = qwen_ke_fraction / our_ke_fraction
    print(f"  Ratio Qwen/ours: {qwen_factor:.3f}")
    if abs(qwen_factor - 1.0) < 0.05:
        print("  Qwen's number is correct.")
    else:
        print(f"  ⚠️ Qwen's number is off by factor {qwen_factor:.3f}")


if __name__ == '__main__':
    main()
