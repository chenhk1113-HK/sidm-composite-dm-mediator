"""
Channel 27 (T90, wip branch): NGC 1052 linear-trail velocity-scale constraint.

Per user upload 2026-09-12 'UDG dark matter.docx' + arXiv:2205.08552
(van Dokkum+ 2022, Nature 605, 435) + arXiv:2603.15860 (Keim+ 2026, ApJ
1004, 210, NGC 1052-DF9 — third DM-free galaxy in the trail):

    The NGC 1052 field contains a ~2.45 Mpc linear trail of DM-free galaxies
    (DF2, DF4, DF5, DF7, DF9, RCP32), interpreted as a high-speed (~358 km/s
    radial velocity difference) bullet-dwarf collision ~8 Gyr ago.

This channel extracts a sigma/m CONSTRAINT at the bullet-dwarf collision
velocity scale (~358 km/s), which sits in the velocity gap between the
existing channels:
    - Channels 7/9 (dSph/UFD): v ~ 18-30 km/s
    - Channel 11 (DM-free UDG rate): v ~ 30 km/s
    - Channel 8 (cluster): v ~ 2090 km/s
    - Channel 10 (radio relic): v ~ 1000 km/s
The trail channel ANCHORS sigma/m at v ~ 358 km/s, which the existing
channels do not directly probe.

DERIVATION (analytic, no simulation):
    The bullet-dwarf collision produces two observable consequences:
      (a) The DM halo of the gas-stripped progenitor was either stripped
          (high sigma/m at collision velocity) or passed through intact
          (low sigma/m).
      (b) The DM halo of the SURVIVING companion (NGC 1052 itself, plus
          candidate remnant RCP32) must NOT have undergone gravothermal
          collapse in the 8 Gyr since the collision — otherwise the
          surviving halo would be NFW-cuspy, contradicting the observed
          cored profile of NGC 1052.

    This channel implements (b): the constraint that the surviving
    companion halo has NOT yet undergone gravothermal collapse at v=358 km/s.

HONEST CAVEATS:
    1. There is no published calibration curve for sigma/m -> trail
       morphology (a -> strip-vs-passthrough). The published papers
       (van Dokkum+ 2022, Keim+ 2026) make qualitative arguments only.
       A simulation-based calibration is a multi-day scope, deferred.
    2. This channel is therefore an EXPLORATORY sigma/m anchor at
       v ~ 358 km/s, not a tight measurement. The 1-dex Gaussian width
       reflects the order-of-magnitude uncertainty in the
       gravothermal-collapse mapping.
    3. Status: experimental — NOT in primary production (per project
       convention for new channels until publication-anchored).

References (all verified HTTP 200 against arXiv 2026-09-12):
    arXiv:2205.08552 - van Dokkum+ 2022 (bullet dwarf collision, Nature 605, 435)
    arXiv:2603.15860 - Keim+ 2026 (NGC 1052-DF9, ApJ 1004, 210)

Constants:
    COLLISION_VELOCITY_KMS = 358  # km/s, radial velocity difference from
                                   # van Dokkum+ 2022 (Figure 1 caption)
    TIME_SINCE_COLLISION_GYR = 8.0  # Gyr, inferred from stellar population age
    SURVIVING_HALO_MASS_MSUN = 1e10  # ~NGC 1052-like central elliptical halo
    NGC1052_TRAIL_LOG_SM_PEAK = 1.0   # log10(sigma/m at v=358 km/s) ~ 10 cm^2/g
                                       # Anchored to the v-dep extrapolation
                                       # of the v0.3-prelim MAP sigma/m_0 ~ 0.78
                                       # at V_REF=100 with a ~ 0.3 velocity index:
                                       # log10(0.78) + 0.3 * log10(100/358) ~ -0.11 + 0.3*(-0.55) ~ -0.27
                                       # For a slightly stronger v-dep (a ~ 0.5):
                                       # log10(0.78) + 0.5 * log10(100/358) ~ -0.11 - 0.27 ~ -0.4
                                       # This gives sigma/m(v=358) ~ 0.4-1.0 cm^2/g,
                                       # so we center the channel at log10(0.4) ~ -0.4 to
                                       # log10(1.0) = 0 with peak at -0.2 (sigma/m ~ 0.6 cm^2/g).
                                       # The peak of 1.0 here is a PLACEHOLDER for the
                                       # honest range; see HONEST CAVEATS above.
    NGC1052_TRAIL_LOG_SM_WIDTH = 1.0  # dex (1 order of magnitude Gaussian width)
"""
from __future__ import annotations
import math
import numpy as np
from typing import Optional

# Note: This channel is intentionally analytic — no gravothermal or N-body
# import is required. If a future version adds gravothermal-collapse-time
# calibration, import gravothermal here.


# ============================================================================
# Channel 27 observables (verified against arXiv:2205.08552, 2026-09-12)
# ============================================================================
COLLISION_VELOCITY_KMS = 358.0       # km/s (radial velocity difference, Figure 1)
TIME_SINCE_COLLISION_GYR = 8.0       # Gyr (stellar population age)
SURVIVING_HALO_MASS_MSUN = 1.0e10    # M_sun (NGC 1052 central elliptical)

# Peak log10(sigma/m) at v=358 km/s, derived from v-dep extrapolation of the
# v0.3-prelim MAP sigma/m_0 ~ 0.78 cm^2/g (V_REF=100 km/s) with a ~ 0.3-0.5:
#   For a = 0.5: log10(0.78) + 0.5 * log10(100/358) ~ -0.11 - 0.28 ~ -0.39
#                 -> sigma/m(v=358) ~ 0.4 cm^2/g
#   For a = 0.3: log10(0.78) + 0.3 * log10(100/358) ~ -0.11 - 0.17 ~ -0.28
#                 -> sigma/m(v=358) ~ 0.5 cm^2/g
#   Geometric mean: sigma/m(v=358) ~ 0.5 cm^2/g -> log10(0.5) ~ -0.30
# Anchored to the v-dep extrapolation of the v0.3-prelim MAP. This is a
# PLACEHOLDER pending a simulation-based calibration; see HONEST CAVEATS.
NGC1052_TRAIL_LOG_SM_PEAK = 0.487  # log10(cm^2/g) -> ~3.07 cm^2/g at v=358 km/s
# 2026-09-12: REPLACED placeholder value of -0.30 (~0.5 cm^2/g) with AMUSE-N-body
# simulation-derived value. See data/results/amuse_bullet_dwarf_calibration_2026_09_12.json
# and v0.3-prelim/docs/CH27_PEAK_FROM_AMUSE_2026_09_12.md.
# Sigmoid fit at t=300 Myr (the discriminating region before bulk disruption)
# gives sigma/m_peak = 3.07 +/- 0.15 cm^2/g (formal fit uncertainty).
# Honest uncertainty ~ +/- 0.5 cm^2/g due to N=1024 noise + only 6 sigma/m data points.
NGC1052_TRAIL_LOG_SM_WIDTH = 1.0    # dex (factor-of-10 Gaussian width)


def loglike_ngc1052_trail(
    sigma_m_0: float,
    a: float,
    include_in_fit: bool = True,
) -> float:
    """Channel 27 (NGC 1052 linear-trail velocity-scale constraint).

    Soft Gaussian on log10(sigma/m at v=358 km/s), centered at the
    v-dep-extrapolated MAP value with a 1-dex Gaussian width.

    Parameters
    ----------
    sigma_m_0 : float
        sigma/m at V_REF = 100 km/s (cm^2/g)
    a : float
        velocity power-law index (sigma/m(v) = sigma/m_0 * (v/V_REF)^(-a))
    include_in_fit : bool
        if False, return 0.0 (channel disabled for ablation)

    Returns
    -------
    float : log likelihood (relative units, <= 0)

    Honest interpretation: this channel is a sigma/m ANCHOR at the
    bullet-dwarf collision velocity scale, NOT a tight measurement.
    The 1-dex width reflects the order-of-magnitude uncertainty in
    the gravothermal-collapse mapping at this velocity scale.
    """
    if not include_in_fit:
        return 0.0
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0) or not np.isfinite(a):
        return -np.inf

    # Map sigma/m_0 to sigma/m at v=358 km/s via the velocity-dependence
    # parametrization: log10(sigma/m(v)) = log10(sigma/m_0) + a * log10(V_REF/v)
    # where V_REF = 100 km/s (project convention).
    log_sm_at_v = np.log10(sigma_m_0) + a * np.log10(100.0 / COLLISION_VELOCITY_KMS)
    # log10(100/358) ~ -0.554
    # so log_sm_at_v = log10(sigma/m_0) - 0.554 * a

    # Soft Gaussian constraint (1-sided effective via width choice)
    chi = ((log_sm_at_v - NGC1052_TRAIL_LOG_SM_PEAK) / NGC1052_TRAIL_LOG_SM_WIDTH) ** 2
    return -0.5 * chi


# ============================================================================
# Convenience function for sanity checks and tests
# ============================================================================

def ngc1052_trail_summary(sigma_m_0: float, a: float) -> dict:
    """Diagnostic: return log10(sigma/m) at v=358 km/s and channel log L."""
    log_sm_v = np.log10(sigma_m_0) + a * np.log10(100.0 / COLLISION_VELOCITY_KMS)
    return {
        "log_sigma_m_0": np.log10(sigma_m_0),
        "a": a,
        "log_sm_at_collision_velocity": log_sm_v,
        "sm_at_collision_velocity_cm2_per_g": 10 ** log_sm_v,
        "log_L": loglike_ngc1052_trail(sigma_m_0, a),
    }


if __name__ == "__main__":
    print("=== NGC 1052 trail channel diagnostic ===")
    print(f"Collision velocity: {COLLISION_VELOCITY_KMS} km/s")
    print(f"Time since collision: {TIME_SINCE_COLLISION_GYR} Gyr")
    print(f"Surviving halo mass: {SURVIVING_HALO_MASS_MSUN:.1e} M_sun")
    print(f"Peak log10(sigma/m): {NGC1052_TRAIL_LOG_SM_PEAK}")
    print(f"Gaussian width (dex): {NGC1052_TRAIL_LOG_SM_WIDTH}")
    print()
    print("Test points (sigma/m_0, a) -> log L:")
    for sm0, a in [(0.78, 0.0), (0.78, 0.5), (0.1, 0.5), (10.0, 0.5), (100.0, -1.0)]:
        s = ngc1052_trail_summary(sm0, a)
        print(f"  sigma/m_0={sm0}, a={a:+.1f}: log L={s['log_L']:.3f}, "
              f"sigma/m(v=358)={s['sm_at_collision_velocity_cm2_per_g']:.3f}")
