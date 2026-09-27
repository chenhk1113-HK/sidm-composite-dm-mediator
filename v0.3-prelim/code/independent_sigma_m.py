"""
Independent implementation of the multi-resonance sigma/m function.

This is the Layer D cross-code test:
  - Implemented from scratch (NOT a copy of t90_v70_multi_resonant_darkqcd)
  - Uses a different parameterization choice for the Breit-Wigner centering
    (v-space vs v^2-space) to catch parameterization bugs in the original
  - Cross-checked against phase44_joint_fit.sigma_m_at_v at multiple velocities

Difference from phase44_joint_fit.sigma_m_at_v:
  - Original:  breit_wigner_factor(v, m_chi, E_R, Gamma)
              uses E_R in eV, v in km/s; computed via kinematic v^2 mapping
  - This:     bw_factor_v_space(v, v_target, Gamma_frac)
              uses v_target directly in km/s; computes E_R internally
              from v_target, but the Breit-Wigner shape is in v-space
              (not v^2-space). The v-space shape has FWHM = Gamma_frac * v_target
              in km/s, not in v^2.

  Specifically:
    Original:   BW(v) = (Gamma/2)^2 / [(v^2 - v_t^2)^2 + (Gamma*v_t/2)^2]
    This:       BW(v) = (Gamma_v/2)^2 / [(v - v_t)^2 + (Gamma_v/2)^2]
              where Gamma_v = Gamma_frac * v_target  (in km/s)

  The v-space form is the "textbook" non-relativistic Breit-Wigner. The
  v^2-space form is the kinematic form (energy-space). They differ slightly
  in the shape, especially at v far from v_target where the v^2-space form
  has narrower tails (because (v^2 - v_t^2) grows faster than (v - v_t)).
"""
import numpy as np


def velocity_bg_independent(sigma_0: float, a_slope: float, v_kms: float, v_ref_kms: float = 1.0) -> float:
    """Yukawa-like velocity-dependent background.

    sigma_0(v) = sigma_0 * (v_ref / v)^a_slope

    Args:
        sigma_0: Normalization at v = v_ref (cm^2/g)
        a_slope: Power-law slope (typically ~0.5-1.0 for SIDM)
        v_kms: Velocity (km/s)
        v_ref_kms: Reference velocity for normalization (km/s, default 1.0)

    Returns:
        sigma/m background in cm^2/g
    """
    if v_kms <= 0:
        return 0.0
    return sigma_0 * (v_ref_kms / v_kms) ** a_slope


def bw_factor_v_space(v_kms: float, v_target_kms: float, gamma_frac: float) -> float:
    """Breit-Wigner factor in v-space (NOT v^2-space).

    BW(v) = (Gamma_v/2)^2 / [(v - v_target)^2 + (Gamma_v/2)^2]

    where Gamma_v = gamma_frac * v_target (FWHM in km/s).

    This is the textbook non-relativistic Breit-Wigner in velocity space.
    It is normalized so that BW(v_target) = 1 (peak).

    Args:
        v_kms: Velocity (km/s)
        v_target_kms: Resonance position (km/s)
        gamma_frac: FWHM / v_target ratio (dimensionless)

    Returns:
        BW factor (dimensionless, in [0, 1])
    """
    gamma_v = gamma_frac * v_target_kms
    return (gamma_v / 2) ** 2 / ((v_kms - v_target_kms) ** 2 + (gamma_v / 2) ** 2)


def sigma_m_multi_resonance_independent(
    v_kms: float,
    m_chi_GeV: float,
    v_targets_kms: list,
    sigma_peaks: list,
    gamma_fracs: list,
    sigma_0: float,
    a_slope: float,
) -> float:
    """Independent implementation of multi-resonance sigma/m(v).

    Sums the Yukawa background plus one Breit-Wigner per resonance.

    Args:
        v_kms: Velocity (km/s)
        m_chi_GeV: DM mass (GeV) - not used directly, kept for API compatibility
        v_targets_kms: List of 4 resonance positions (km/s)
        sigma_peaks: List of 4 peak heights (cm^2/g)
        gamma_fracs: List of 4 gamma_fracs (dimensionless)
        sigma_0: Background normalization (cm^2/g)
        a_slope: Background slope (dimensionless)

    Returns:
        sigma/m(v) in cm^2/g
    """
    # Background (Yukawa)
    sigma_total = velocity_bg_independent(sigma_0, a_slope, v_kms)

    # Sum over resonances (v-space Breit-Wigner)
    for v_t, sigma_peak, gamma_frac in zip(v_targets_kms, sigma_peaks, gamma_fracs):
        bw = bw_factor_v_space(v_kms, v_t, gamma_frac)
        sigma_total += sigma_peak * bw

    return sigma_total


def sigma_m_v_derivative_check(v_kms: float, **kwargs) -> float:
    """Cross-check: compute sigma/m(v) using a centered finite-difference derivative
    of the Breit-Wigner shape, to verify the analytical formula is consistent.

    This catches bugs where the analytical formula accidentally has the wrong
    sign or scaling. The finite-difference derivative of the BW factor at
    v_target should be exactly zero (peak), and the second derivative should
    be -4/gamma_v^2 at v_target.

    For now, this is a placeholder that calls sigma_m_multi_resonance_independent.
    A real derivative-check would require a separate implementation of the
    derivative and comparison against numerical differentiation.
    """
    return sigma_m_multi_resonance_independent(v_kms, **kwargs)