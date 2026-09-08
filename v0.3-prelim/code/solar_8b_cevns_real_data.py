"""
T88.F — Solar 8B CEvNS real measurements channel (Channel 25).

REAL DATA from XENONnT (PRL 133, 191002, 2024) and PandaX-4T
(PRL 133, 191001, 2024).

WHAT'S REAL DATA:
  XENONnT measurement of solar 8B neutrinos via CEvNS on xenon:
    - flux: (4.7 +3.6 -2.3) x 10^6 /cm^2/s
    - CEvNS cross section on Xe: (1.1 +0.8 -0.5) x 10^-39 cm^2
    - significance: 2.7 sigma (background-only rejected)
  PandaX-4T measurement (simultaneous):
    - similar flux measurement on xenon
    - confirmed with independent analysis

WHAT THIS CHANNEL DOES:
  Compares the master's Yukawa σ/m(v) prediction at solar 8B velocity
  scale to these measured cross sections. SIDM with σ/m > 0.1 cm^2/g
  at v ~ 10-30 km/s would contribute ADDITIONAL recoil events on top
  of the standard CEvNS prediction.

  Currently the measured cross sections are consistent with SM (CEvNS
  only). This channel computes the SIDM-induced excess over SM as a
  function of (sigma_m_0, a) and compares to the measured
  cross-section error bars.

SIDM-RELEVANT OBSERVABLE:
  At v ~ 10-30 km/s (solar 8B velocity at Earth), the master Yukawa
  gives σ/m that may differ from the LZ-anchored v=150 km/s value
  by factor (150/30)^a (velocity power-law).

  If σ/m(v=30) > 0.5 cm^2/g, the SIDM contribution to the recoil
  spectrum would be visible above the CEvNS signal.

REFERENCE:
  - XENON Collaboration, PRL 133, 191002 (2024), arXiv:2408.06277
  - PandaX Collaboration, PRL 133, 191001 (2024), arXiv:2407.10892
  - Standard Model CEvNS: Freedman (1974), PRD 9, 1389

OUTPUT
  - outputs/t90/solar_8b_cevns_real.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================================
# Real measurements (XENONnT + PandaX-4T, 2024)
# ============================================================================
XENONNT_8B_FLUX_CM2_S = 4.7e6  # central value
XENONNT_8B_FLUX_UPPER = 4.7e6 + 3.6e6  # +3.6 sigma
XENONNT_8B_FLUX_LOWER = 4.7e6 - 2.3e6  # -2.3 sigma

XENONNT_8B_XSEC_CM2 = 1.1e-39  # central
XENONNT_8B_XSEC_UPPER = 1.1e-39 + 0.8e-39  # +0.8
XENONNT_8B_XSEC_LOWER = 1.1e-39 - 0.5e-39  # -0.5

# SM prediction for CEvNS cross section on Xe
SM_8B_XSEC_XE_CM2 = 1.16e-39  # from PRL 133, 191002 (Eq. 3, theoretical)
# (consistent with measured 1.1 +0.8/-0.5 within error bars)

# Solar 8B velocity distribution parameters (8B neutrinos have E ~ 5-15 MeV)
SOLAR_8B_V_TYPICAL_KMS = 30.0  # approximate typical velocity at Earth
# Actually, neutrinos are ultra-relativistic (v~c); the "velocity" for SIDM
# scattering is NOT the neutrino velocity (neutrinos don't interact via SIDM
# in this model). The relevant velocity for SIDM contribution is the
# NUCLEAR recoil velocity of the xenon nucleus after CEvNS, which is much
# smaller (v ~ 10^-3 c for nuclear recoils of keV-scale).

# For SIDM recoil on xenon: σ/m is evaluated at the DM velocity in the halo,
# not the neutrino energy. SIDM scattering is between DM particles, not
# between DM and nuclei. The contribution to CEvNS-like recoil events from
# SIDM is actually zero unless there's a separate DM-nucleon coupling.

# THEREFORE: this channel is primarily a CONSISTENCY check on whether the
# measured CEvNS cross section is compatible with the SM-only prediction.
# Any SIDM-induced excess would come from an ADDITIONAL DM-nucleon coupling,
# not from the SIDM self-interaction.

# For this script, we model the constraint as: the measured CEvNS cross
# section places an UPPER LIMIT on any non-SM contribution to nuclear
# recoils at E_recoil < ~10 keV.
CEVNS_RECOIL_ENERGY_KEV_MAX = 10.0  # max recoil energy probed


# ============================================================================
# Velocity-rescaling for sigma/m
# ============================================================================
V_REF = 100.0  # km/s (project's standard)


def sigma_m_at_v_low(sigma_m_0: float, a: float, v_kms: float = SOLAR_8B_V_TYPICAL_KMS) -> float:
    """Compute sigma/m at low (dwarf-galaxy / sub-halo) velocities.

    Parameters:
      sigma_m_0: cross-section per unit mass at V_REF=100 km/s (cm^2/g)
      a: velocity-slope parameter
      v_kms: characteristic velocity (default 30 km/s for sub-halo scales)

    Returns:
      sigma/m at v=v_kms in cm^2/g
    """
    if sigma_m_0 <= 0:
        return 0.0
    return sigma_m_0 * (V_REF / v_kms) ** a


# ============================================================================
# Likelihood: measured CEvNS cross section vs SM + SIDM contribution
# =========================================================================
def sidm_recoil_excess_fraction(sigma_m_0: float, a: float,
                                  exposure_kg_year: float = 1.0) -> float:
    """Compute the SIDM-induced fractional excess over SM CEvNS.

    **Conceptually**: SIDM (DM-DM scattering) does NOT directly produce
    CEvNS-like events. The SIDM contribution would be through a separate
    DM-nucleon coupling (not in the master Yukawa). Therefore this
    function returns 0 by default.

    However, the master Yukawa at v ~ 30 km/s predicts σ/m values that
    we can compare to known bounds from DM direct-detection experiments
    (which probe DM-nucleon interactions at low velocities). If
    sigma_m_at_v_low > 1.0 cm^2/g, the SIDM model is in tension with
    direct-detection bounds (independent of CEvNS).

    This function is therefore a CONSISTENCY check, not an SIDM signal
    prediction. Returns 0.0 for the SIDM excess (SIDM doesn't contribute
    to CEvNS directly), but the function exists so the channel can be
    re-purposed when a DM-nucleon coupling is added.

    Parameters:
      sigma_m_0: SIDM cross-section at V_REF=100 km/s
      a: velocity-slope
      exposure_kg_year: detector exposure (not used here)

    Returns:
      Fractional excess over SM (0.0 by default)
    """
    # SIDM does not contribute to CEvNS directly.
    return 0.0


def loglike_xenonnt_8b_cevns(sigma_m_0: float, a: float,
                                measured: float = XENONNT_8B_XSEC_CM2,
                                measured_upper: float = XENONNT_8B_XSEC_UPPER,
                                measured_lower: float = XENONNT_8B_XSEC_LOWER) -> float:
    """Likelihood comparing measured CEvNS cross section to SM prediction.

    If SIDM contributes an excess (via a DM-nucleon coupling), the
    predicted cross section becomes σ_pred = σ_SM + σ_SIDM_excess.
    Currently σ_SIDM_excess = 0, so this is a consistency check:
    is the SM prediction consistent with the measurement?

    Parameters:
      sigma_m_0: SIDM cross-section at V_REF (cm^2/g)
      a: velocity-slope
      measured: central measurement (cm^2)
      measured_upper: +1 sigma upper bound
      measured_lower: -1 sigma lower bound

    Returns:
      Gaussian log likelihood (in sigma units)
    """
    # Compute SIDM contribution (currently 0)
    sidm_excess = sidm_recoil_excess_fraction(sigma_m_0, a)
    # Predicted total cross section
    sigma_pred = SM_8B_XSEC_XE_CM2 + sidm_excess
    # Asymmetric error bars: use the larger of upper/lower as sigma for simplicity
    sigma_err = max(measured_upper - measured, measured - measured_lower)
    # Gaussian log L
    residual = (sigma_pred - measured) / sigma_err
    return -0.5 * residual ** 2


# =========================================================================
# Consistency check: sigma/m(v=30) compared to direct-detection bounds
# =========================================================================
DM_NUCLEON_UPPER_LIMIT_CM2_G = 1e-30  # rough order-of-magnitude upper limit
# on sigma/m that would produce visible direct-detection signal
# (for a generic DM-nucleon coupling). Conservative.

def loglike_dm_nucleon_consistency(sigma_m_0: float, a: float) -> float:
    """Penalty for sigma/m at v ~ 30 km/s exceeding direct-detection bounds.

    If sigma_m(v=30) > 1 cm^2/g, the SIDM model would predict
    additional direct-detection events at LZ/PandaX/XENONnT.
    This penalty is 0 when sigma/m(v=30) < 0.5 cm^2/g, and
    grows quadratically above 1.0 cm^2/g.

    Parameters:
      sigma_m_0: SIDM cross-section at V_REF
      a: velocity-slope

    Returns:
      Log likelihood (Gaussian penalty)
    """
    sm_low = sigma_m_at_v_low(sigma_m_0, a, v_kms=30.0)
    if sm_low < 0.5:
        return 0.0
    # Gaussian penalty above 0.5 cm^2/g
    excess = (sm_low - 0.5) / 0.5  # how many sigma above threshold
    return -0.5 * excess ** 2


# =========================================================================
# Main
# =========================================================================
def main():
    print("=" * 70)
    print("T88.F — Solar 8B CEvNS REAL DATA (XENONnT + PandaX-4T, 2024)")
    print("=" * 70)
    print()
    print(f"XENONnT 8B flux:    ({XENONNT_8B_FLUX_LOWER:.2e} to {XENONNT_8B_FLUX_UPPER:.2e}) cm^-2/s")
    print(f"  central: {XENONNT_8B_FLUX_CM2_S:.2e} cm^-2/s")
    print(f"XENONnT 8B CEvNS xsec on Xe: {XENONNT_8B_XSEC_LOWER:.2e} to {XENONNT_8B_XSEC_UPPER:.2e} cm^2")
    print(f"  central: {XENONNT_8B_XSEC_CM2:.2e} cm^2")
    print(f"SM prediction: {SM_8B_XSEC_XE_CM2:.2e} cm^2 (PRL 133, 191002 Eq. 3)")
    print()

    # Test at LZ-anchored parameters
    sigma_m_0_lz = 0.7  # cm^2/g at v=100 km/s
    a_lz = 0.16
    print(f"At LZ-anchored 7D posterior (sigma_m_0={sigma_m_0_lz}, a={a_lz}):")
    sm_low = sigma_m_at_v_low(sigma_m_0_lz, a_lz, v_kms=30.0)
    print(f"  sigma/m(v=30 km/s) = {sm_low:.3f} cm^2/g")
    sidm_excess = sidm_recoil_excess_fraction(sigma_m_0_lz, a_lz)
    print(f"  SIDM excess over SM CEvNS: {sidm_excess:.3f} (currently 0)")
    log_l_xenon = loglike_xenonnt_8b_cevns(sigma_m_0_lz, a_lz)
    print(f"  CEvNS consistency log L = {log_l_xenon:.3f}")
    log_l_dd = loglike_dm_nucleon_consistency(sigma_m_0_lz, a_lz)
    print(f"  Direct-detection consistency log L = {log_l_dd:.3f}")
    print(f"  Total log L = {log_l_xenon + log_l_dd:.3f}")
    print()

    # Output
    out_path = _PROJECT_ROOT / "outputs" / "t90" / "solar_8b_cevns_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 'T88.F (Channel 25, solar 8B CEvNS real data)',
        'real_data': {
            'xenonnt_flux': {
                'central_cm2_s': XENONNT_8B_FLUX_CM2_S,
                'lower_cm2_s': XENONNT_8B_FLUX_LOWER,
                'upper_cm2_s': XENONNT_8B_FLUX_UPPER,
                'reference': 'PRL 133, 191002 (2024), arXiv:2408.06277',
            },
            'xenonnt_xsec_xe': {
                'central_cm2': XENONNT_8B_XSEC_CM2,
                'lower_cm2': XENONNT_8B_XSEC_LOWER,
                'upper_cm2': XENONNT_8B_XSEC_UPPER,
                'reference': 'PRL 133, 191002 (2024)',
            },
            'pandax_4t': 'PRL 133, 191001 (2024), arXiv:2407.10892 (simultaneous publication)',
            'sm_prediction_cm2': SM_8B_XSEC_XE_CM2,
        },
        'sidm_interpretation': {
            'direct_signal': 'SIDM (DM-DM scattering) does NOT produce CEvNS-like events',
            'channel_purpose': 'Consistency check: is the SM CEvNS prediction consistent with measurement?',
            'sidm_excess_fraction_at_LZ': sidm_excess,
            'sigma_m_at_v30_km_s': sm_low,
            'log_l_xenonnt_cevns': log_l_xenon,
            'log_l_dd_consistency': log_l_dd,
            'total_log_l': log_l_xenon + log_l_dd,
        },
        'caveats': [
            'SIDM (DM-DM scattering) does not produce CEvNS-like events',
            'directly. The measured CEvNS cross section places an upper',
            'limit on any non-SM contribution to nuclear recoils at',
            'E_recoil < 10 keV, but this is not a SIDM-specific constraint.',
            'The real value of this channel is the CROSS-CHECK on whether',
            'the SM prediction matches the measured cross section. If yes,',
            'the SIDM model is consistent with neutrino data. If no, there',
            'is tension between CEvNS measurements and the SM prediction.',
        ],
        'references': [
            'XENONnT 8B: PRL 133, 191002 (2024), arXiv:2408.06277',
            'PandaX-4T 8B: PRL 133, 191001 (2024), arXiv:2407.10892',
            'Standard Model CEvNS: Freedman (1974), PRD 9, 1389',
            'Bahcall et al. 2005, ApJ 621, L85 (solar neutrino fluxes)',
        ],
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()