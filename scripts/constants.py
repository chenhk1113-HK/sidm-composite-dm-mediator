"""
constants.py: Framework constants - SINGLE SOURCE OF TRUTH

Per R66 reviewer: "The fix isn't more dimensional analysis; it's a
constants file that every script imports. m_chi = 1.0 GeV or 10.44 GeV,
declared once, used everywhere."

This file centralizes all framework constants so:
1. Every script that computes sigma_SI uses the same m_chi
2. Dimensional analysis scripts can verify consistency
3. Changes propagate to all scripts automatically

Used by: T226, T231, T232, T233, and future cross-section code.
"""

# ====== FRAMEWORK CONSTANTS ======

# DM particle mass: 1.0 GeV (standard WIMP assumption)
# This is the value used in Phase 44 framework derivation
M_CHI_GEV = 1.0

# Mediator mass: 200 eV = 2e-7 GeV (Yukawa with sub-eV mediator)
M_PHI_GEV = 200e-9

# Target velocity at Cloud-9 resonance: 29.4 km/s
# Per Phase 44 free fit (phase44_joint_fit.json best_params[3] = 29.36)
# Constants.py uses 29.4 (rounded); paper §2.6 line 152 used 28 (baseline, FIXED R74)
V_TARGET_KMS = 29.4

# R76: RESOLVED σ vs FWHM. The Gaussian σ width used in all formulas is 4.4 km/s.
# (Previously labelled FWHM_KMS = 4.4 but used as Gaussian σ in exp(-Δ²/(2*4.4²))).
# The numerical value is unchanged; only the variable name is corrected.
# Equivalent FWHM = 4.4 × 2.355 = 10.36 km/s.
SIGMA_KMS = 4.4  # Gaussian σ (NOT FWHM) — historical rename in R76 from FWHM_KMS; see C.2 in R88(45) audit  # Gaussian σ width (R76 renamed from FWHM_KMS)

# Resonance amplitude A_res ~ 100 (Breit-Wigner peak height enhancement)
A_RES = 100.0

# Target sigma_peak at Cloud-9 resonance: 174 cm^2/g
# R76 RESOLUTION: 174 is the CAUSALITY CAP (paper §9.12), NOT a rounded fit value.
# Phase 44 free fit gave σ_peak_R0 = 178.5 unconstrained (best_params[4]).
# Causality cap truncates to 174. See §2.6 sensitivity sweep.
SIGMA_PEAK_CM2_PER_G = 174.0

# Nucleon mass (for reduced mass calc): 0.939 GeV
M_NUCLEON_GEV = 0.939

# ====== PHASE 44 POWER-LAW BACKGROUND CONSTANTS (R88, R88(23)) ======
# Background sigma/m(v) = sigma_0 * (v_ref/v)^a_slope

# Background amplitude at v_ref = 100 km/s
SIGMA_0_CM2_PER_G = 0.052  # cm^2/g (Phase 44 free-fit background)

# Background velocity exponent (Phase 44 free fit, NOT v1.13 Option A flattening)
A_SLOPE = 1.93

# Reference velocity for background normalization
V_REF_KMS = 100.0

# Legacy v1.13 Option A flattening (kept for comparison, NOT canonical)
A_SLOPE_OPTION_A = 1.0

# f_H(Cloud-9 core) -- Phase G7 phenomenological placeholder (R88(88) caveat)
# ============================================================================
# IMPORTANT: This value is a DOCUMENTED PLACEHOLDER, NOT a first-principles
# Yang+ 2025 SIDM2c derivation. The original v1.13 hand-picked f_H values
# were RETRACTED in v18.29 (per CHANGELOG and paper section 3.6):
#
#   "v1.13 with hand-picked placeholder f_H, retracted v18.29 --
#    shown for reference only"
#
# The actual Yang+ 2025 Fig. 2 f_H range is f_L in [0.3, 0.6] (i.e. f_H in
# [0.4, 0.7]), but for sigma_0/m = 147 cm^2/g, NOT Phase 44's 0.052 cm^2/g.
# At Phase 44 sigma/m, T202 N-body (T202 path B validation, see V18.40
# review bundle) found f_H(r) ~= 0.92 (NO segregation; gravothermal cascade
# timescale >> Hubble at weak sigma/m).
#
# v40.41 sensitivity sweep (scripts/v19_2_f_fH_sensitivity.py): ALL
# physically motivated f_H in [0.3, 1.0] give tau > 1 (deep core collapse)
# for v19.2-F canonical parameters. The c-M tension is STRUCTURAL, not
# driven by this placeholder value. Section 2.6b of the paper documents
# this finding.
#
# Per Nemotron 120B review (2026-10-19, v40.41): "Adding the v40.41
# sensitivity analysis as a formal robustness check in the paper is
# warranted." The c-M tension is a real structural constraint, and the
# placeholder f_H value is not the limiting factor.
#
# Use F_H_PLACEHOLDER_G7 (= 0.297) for backward compatibility with v1.13
# code that imported F_H_CANONICAL. New code should use F_H_PHYSICAL_RANGES
# to acknowledge the f_H is a placeholder, not a first-principles value.
F_H_CANONICAL = 0.297  # DEPRECATED: use F_H_PLACEHOLDER_G7 instead
F_H_PLACEHOLDER_G7 = 0.297  # v1.13 / Phase G7 placeholder (retracted v18.29)
F_H = F_H_PLACEHOLDER_G7  # backward-compat alias

# Yang+ 2025 Fig. 2 segregation range (for sigma_0/m = 147 cm^2/g, NOT Phase 44)
F_H_YANG_PLUS_LOW = 0.40  # f_L = 0.6 (heavy fraction at low end)
F_H_YANG_PLUS_MID = 0.50  # f_L = 0.5 (mid segregation)
F_H_YANG_PLUS_HIGH = 0.70  # f_L = 0.3 (heavy fraction at high end)

# T202 N-body at Phase 44 sigma/m (gravothermal cascade timescale >> Hubble,
# NO segregation develops)
F_H_T202_NBODY = 0.92

# Single-component SIDM (no f_H suppression)
F_H_SINGLE_COMPONENT = 1.00

# Documented physically motivated ranges (per v40.41 sensitivity sweep)
F_H_PHYSICAL_RANGES = {
    "placeholder_g7_retracted": F_H_PLACEHOLDER_G7,
    "yang_plus_low": F_H_YANG_PLUS_LOW,
    "yang_plus_mid": F_H_YANG_PLUS_MID,
    "yang_plus_high": F_H_YANG_PLUS_HIGH,
    "t202_nbody": F_H_T202_NBODY,
    "single_component": F_H_SINGLE_COMPONENT,
}

# Speed of light
C_KMS = 2.998e5

# Planck constant * c
HBAR_C_GEV_CM = 1.973e-14
HBAR_C_SQ_GEV2_CM2 = HBAR_C_GEV_CM ** 2

# ====== DERIVED QUANTITIES ======

def reduced_mass_gev(m_chi_gev=M_CHI_GEV, m_n_gev=M_NUCLEON_GEV):
    """DM-nucleon reduced mass (GeV)."""
    return m_chi_gev * m_n_gev / (m_chi_gev + m_n_gev)


def q_mev(v_kms, m_chi_gev=M_CHI_GEV):
    """Momentum transfer at velocity v (MeV)."""
    mu = reduced_mass_gev(m_chi_gev)
    return 2 * mu * (v_kms / C_KMS) * 1000


def g_chi_from_sigma_peak(sigma_peak=SIGMA_PEAK_CM2_PER_G, v_target=V_TARGET_KMS):
    """Compute g_chi from sigma_peak = sigma_0 * A_res * (g^4 / m_chi^2 * c/v^4) (v_form).

    From T226: coeff = 1.0 / (32 pi v^4) * hbar_c^2 / m_chi  (in GeV cm^2 units)
    sigma_peak = A_res * coeff * g^4
    => g = (sigma_peak / (A_res * coeff))^(1/4)
    """
    v = v_target
    coeff = 1.0 / (32 * 3.14159 * (v / C_KMS)**4) * HBAR_C_SQ_GEV2_CM2 / (M_CHI_GEV * 1.783e-24)
    return (sigma_peak / (A_RES * coeff)) ** 0.25


# ====== EXPERIMENTAL BOUNDS ======

LZ_BOUND_CM2 = 9.4e-48  # LZ 2024 90% CL for m_chi ~ 1 GeV (R88(46): updated from 9e-48)  # LZ 2024 direct-detection bound


if __name__ == '__main__':
    print("=" * 60)
    print("FRAMEWORK CONSTANTS")
    print("=" * 60)
    print(f"M_CHI_GEV = {M_CHI_GEV}")
    print(f"M_PHI_GEV = {M_PHI_GEV}")
    print(f"V_TARGET_KMS = {V_TARGET_KMS}")
    print(f"SIGMA_KMS = {SIGMA_KMS} (Gaussian sigma; equivalent FWHM = {SIGMA_KMS * 2.355:.2f} km/s)")
    print(f"SIGMA_PEAK_CM2_PER_G = {SIGMA_PEAK_CM2_PER_G} (causality cap from §9.12)")
    print(f"M_NUCLEON_GEV = {M_NUCLEON_GEV}")
    print()
    print("Derived:")
    print(f"  reduced_mass = {reduced_mass_gev():.4f} GeV")
    print(f"  g_chi (from sigma_peak) = {g_chi_from_sigma_peak():.4e}")
    print()
    print("=" * 60)
    print("CROSS-SCRIPT CONSISTENCY (per R66 reviewer)")
    print("=" * 60)
    print(f"All scripts that use M_CHI_GEV = {M_CHI_GEV} now agree.")
    print(f"Previous inconsistencies: T226 used 1.0, T231 used 10.44, T232 used 0.469 implicit")
    print(f"  (T232's reduced_mass 0.469 GeV corresponds to m_chi = {0.469 * 0.939 / (0.939 - 0.469):.3f} GeV)")
    print(f"  which is between 1.0 (T226) and 10.44 (T231). NEITHER was correct.")
    print()
    print(f"With m_chi = {M_CHI_GEV} GeV:")
    print(f"  reduced_mass = {reduced_mass_gev():.4f} GeV")
    print(f"  q(v=200) = {q_mev(200):.4f} MeV")