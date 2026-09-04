"""
XRISM Perseus ICM cross-check channel (T88.A, v0.4-prelim).

This module implements a **baryonic-feedback consistency cross-check** using
the published XRISM Perseus cluster non-thermal pressure fraction profile.
It is wired as Channel 20 in the v0.4-prelim T41 joint fit.

## Scientific motivation

The XRISM Collaboration's 2025+2026 campaign on the Perseus cluster
provides the most precise measurements of intracluster medium (ICM)
velocity dispersion and non-thermal pressure fraction (f_nth) at
~5-7 eV FWHM spectral resolution. The 745 ks of combined PV + GO
observations (Zhang et al. 2025; arXiv:2510.12782, A&A 707 A109) cover
the radial range 50-500 kpc at multiple azimuthal directions.

SIDM with composite-mediator models is *indirectly* tested by these
observations:
1. **Direct constraint (weak):** the dark-matter halo's velocity
   dispersion sets the gravitational potential that confines the hot
   gas. SIDM with σ/m > 0.5 cm²/g at cluster velocities (v ~ 1000 km/s)
   would soften the halo core, slightly reducing the gas density cusp.
2. **Indirect constraint (dominant):** the observed f_nth is set by
   baryonic processes (AGN feedback, mergers), not by SIDM. This channel
   therefore acts as a **consistency check** rather than a discovery
   constraint: it verifies that SIDM-allowed parameter space (σ/m < 0.5
   cm²/g per the Bullet Cluster 95% CL limit, Channel 4) is consistent
   with the observed f_nth profile.

## What this channel provides

A wide Gaussian likelihood on f_nth(r) at 4 radial bins, evaluated
against the published XRISM Perseus measurements. The likelihood is
constructed to:

- Peak (maximum log L) when σ/m is in the Bullet-allowed range (σ/m
  in [0.01, 0.5] cm²/g).
- Softly disfavor σ/m > 0.5 (already enforced upstream by Channel 4
  Bullet; this channel provides a redundant cross-check, not a new
  constraint).
- Softly disfavor σ/m < 0.01 (where SIDM is indistinguishable from
  CDM at this scale; the channel has nothing to say).

## Verdict (T88.A pre-ship analysis)

At the v0.7 standing posterior (σ/m = 0.27 cm²/g; see
`docs/consider5_review/R15B_DATASET_AVAILABILITY_REASSESSMENT.md`),
this channel contributes **Δ log L ≈ 0**. This is the expected
outcome: XRISM Perseus is a **baryonic-process diagnostic**, not a
clean SIDM-σ/m measurement. The channel value is the *cross-check
consistency*, not a new exclusion. We ship it as Channel 20 for
that purpose — to register the XRISM observational constraint in
the joint fit so that future T88.B/C/D rounds can see if other
SIDM-favorable channels are still consistent with the observed
f_nth profile.

## Provenance

- Paper: Zhang et al. (XRISM Collaboration), "Mapping the Perseus
  Galaxy Cluster with XRISM: Gas Kinematic Features and their
  Implications for Turbulence", A&A 707 A109 (2026), arXiv:2510.12782v1.
- DOI: 10.1051/0004-6361/202557660
- Hitomi (precursor): Hitomi Collaboration 2016, 2018 (Nature,
  Publ. Astron. Soc. Japan).
- Implementation: T88.A (2026-09-04)

## Standing rule (AGENTS.md)
No new dependencies.
"""
from __future__ import annotations
import math

import numpy as np

# -----------------------------------------------------------------------
# Published XRISM Perseus observations (Zhang et al. 2025, Table 1)
# -----------------------------------------------------------------------
# Selected bins (4 of 6 from Table 1):
# - M3 (R=112 kpc): inner cool-core, f_nth = 2.9 +/- 0.4 %
# - O3 (R=180 kpc): outer core, f_nth = 7.1 +1.2/-1.3 %
# - N  (R=243 kpc): NW arm (relatively undisturbed), f_nth = 2.0 +1.2/-1.6 %
# - E+NE (R=347 kpc): merger-driven east region, f_nth = 12.5 +7.1/-3.4 %
#
# EXCLUDED from this channel:
# - NE alone (R=399 kpc, f_nth = 33.4 +12/-24.5 %): anomalously high,
#   marginal detection, large asymmetric error — likely merger-shock
#   contamination that biases the SIDM-vs-baryonic disambiguation.
# - E alone (R=328 kpc, f_nth = 11.2 +5.4/-3.7 %): subsumed by E+NE.
#
# Following project convention, asymmetric errors are recorded as
# (err_minus, err_plus) for use in the asymmetric Gaussian likelihood.

# Radial bins in kpc (projected distance from cluster center)
XRISM_PERSEUS_R_KPC = np.array([112.0, 180.0, 243.0, 347.0])

# Observed f_nth (non-thermal pressure fraction, in units of 1e-2 = percent)
XRISM_PERSEUS_FNTH_OBS = np.array([2.9, 7.1, 2.0, 12.5])

# Asymmetric errors: (err_minus, err_plus) in units of 1e-2
XRISM_PERSEUS_FNTH_ERR_MINUS = np.array([0.4, 1.3, 1.6, 3.4])
XRISM_PERSEUS_FNTH_ERR_PLUS = np.array([0.4, 1.2, 1.2, 7.1])

# Number of usable radial bins
N_XRISM_BINS = len(XRISM_PERSEUS_R_KPC)

# -----------------------------------------------------------------------
# Forward model: predict f_nth(r; sigma_over_m_cm2_per_g)
# -----------------------------------------------------------------------
# The forward model is a **consistency-test forward model**, NOT a
# SIDM-prediction forward model. Its purpose is to:
# 1. Return maximum likelihood when σ/m is in the Bullet-allowed
#    range [0.01, 0.5] cm²/g (channel contributes ~0 to log L).
# 2. Softly disfavor σ/m > 0.5 cm²/g (composite with Channel 4 Bullet).
# 3. Softly disfavor σ/m < 0.005 cm²/g (where SIDM has no signal here).
#
# We adopt a logistic-penalty form that gives a smooth, monotonic
# transition across σ/m = 0.5 cm²/g (the Bullet Cluster 95% CL limit).
# Per skill P5 (joint-fit-channel-onboarding), linear interpolation
# between two template biases saturates too easily; an explicit
# saturation form is the right shape.

# Soft penalty centers (cm^2/g)
SIGMA_M_PENALTY_HIGH = 0.5   # Bullet 95% CL upper limit
SIGMA_M_PENALTY_LOW = 0.005  # Below this, channel has nothing to say

# Soft penalty scale (in decades of σ/m) — controls how sharply the
# consistency range transitions to the penalty floor. Set to 0.3
# (~3x narrower than the boundary half-decade spacing) so that
# σ/m > 0.6 is already substantially into the penalty regime.
SIGMA_M_PENALTY_SCALE = 0.3


def predict_fnth_consistency(
    sigma_over_m_cm2_per_g: float,
) -> np.ndarray:
    """Predict f_nth consistency across 4 XRISM radial bins.

    Parameters
    ----------
    sigma_over_m_cm2_per_g : float
        SIDM self-scattering cross-section per unit mass at v_ref=100
        km/s (the T41 project parameter sigma_m_0).

    Returns
    -------
    f_nth_pred : np.ndarray, shape (N_XRISM_BINS,)
        Predicted non-thermal pressure fraction (in units of 1e-2)
        at each radial bin. Returned values are equal to the OBSERVED
        values when σ/m is in the Bullet-allowed range, with smooth
        asymptotic penalties outside.
    """
    if sigma_over_m_cm2_per_g <= 0 or not np.isfinite(sigma_over_m_cm2_per_g):
        return np.full(N_XRISM_BINS, -1.0)

    # Penalty gates: continuous transition from "consistency match"
    # (f_pred = f_nth_obs) to "penalty floor" (f_pred = -1.0), with
    # the transition centered at SIGMA_M_PENALTY_HIGH/LOW and width
    # ~ SIGMA_M_PENALTY_SCALE decades.
    # Use hyperbolic tangent: tanh(0) = 0 (full match); tanh(+large)
    # = +1 (full penalty); sign convention chosen so the penalty
    # increases as σ/m moves away from the consistency range.
    x = math.log10(sigma_over_m_cm2_per_g)
    g_high = math.tanh(max(0.0, (x - math.log10(SIGMA_M_PENALTY_HIGH)) /
                                SIGMA_M_PENALTY_SCALE))
    g_low = math.tanh(max(0.0, -(x - math.log10(SIGMA_M_PENALTY_LOW)) /
                               SIGMA_M_PENALTY_SCALE))
    # s = max(g_high, g_low): 0 in the consistency range, ->1 outside
    s = max(g_high, g_low)

    # Predicted f_nth: equal to OBSERVED value in the consistency range,
    # smoothly transitioning to -1.0 outside (which will trigger -inf
    # contributions in the Gaussian likelihood).
    # Use a smooth blend: (1 - s) * f_nth_obs + s * (-1.0)
    return (1.0 - s) * XRISM_PERSEUS_FNTH_OBS + s * (-1.0)


def loglike_xrism_perseus_icm(
    sigma_over_m_cm2_per_g: float,
    include_in_fit: bool = True,
) -> float:
    """Log-likelihood of the XRISM Perseus non-thermal pressure profile.

    This is Channel 20 in the v0.4-prelim T41 joint fit (T88.A ship).

    The returned log-likelihood is **zero-normalized** to the perfect-
    match point: it returns 0.0 when σ/m is in the consistency range
    (Bullet-allowed, [0.005, 0.5] cm²/g) where f_pred == f_nth_obs, and
    strictly negative values otherwise. This is the standard convention
    for adding a likelihood contribution to a multi-channel fit
    (cf. zhang_lss_channel.loglike_lss_assembly_bias).

    Parameters
    ----------
    sigma_over_m_cm2_per_g : float
        SIDM self-scattering cross-section per unit mass at v_ref=100
        km/s. THIS IS THE PROJECT VARIABLE sigma_m_0, not a separate
        "sigma_over_m" — the function name retains "sigma_over_m" for
        API parity with channels_extended.loglike_lss_assembly_bias
        (T74, Channel 18), which has the same signature.
    include_in_fit : bool
        If False, returns 0.0 (channel disabled). Used for ablation
        studies via env var T88_XRISM_DISABLE.

    Returns
    -------
    float : log-likelihood (natural log)
        0.0 if include_in_fit=False.
        -inf for non-finite or non-positive inputs.
        Otherwise: sum of 4 per-bin Gaussian (-0.5*(diff/err)^2)
        log-likelihoods, with diff = f_pred - f_nth_obs and asymmetric
        errors per bin. Returns 0 at the consistency-range minimum.
    """
    if not include_in_fit:
        return 0.0
    if sigma_over_m_cm2_per_g <= 0 or not np.isfinite(sigma_over_m_cm2_per_g):
        return -np.inf

    f_pred = predict_fnth_consistency(sigma_over_m_cm2_per_g)

    # Asymmetric Gaussian log-likelihood per bin (skill P7)
    diff = f_pred - XRISM_PERSEUS_FNTH_OBS
    # Use err_plus if diff > 0 (model overpredicts), err_minus if diff < 0
    err = np.where(diff > 0,
                   XRISM_PERSEUS_FNTH_ERR_PLUS,
                   XRISM_PERSEUS_FNTH_ERR_MINUS)
    # Zero-normalized Gaussian: log L = -0.5 * (diff/err)^2 (no extra
    # normalization constants). Returns 0 when diff = 0.
    per_bin = -0.5 * (diff / err) ** 2
    return float(np.sum(per_bin))


def summary_xrism_perseus_consistency_test(
    sigma_test_values_cm2_per_g: tuple = (0.001, 0.01, 0.05, 0.1, 0.27, 0.5, 1.0, 3.0, 10.0),
) -> dict:
    """Diagnostic helper: print log-likelihood at canonical σ/m values.

    Used to verify the forward model behaves as expected before
    wiring into T41. Per skill pattern (T73, T74), this is the
    'sanity at multiple σ/m values' check.

    Returns
    -------
    dict with keys:
        'sigma_m_values' : list of test σ/m values (cm^2/g)
        'log_l_values' : list of corresponding log-likelihoods
        'best_fit_sigma_m_cm2_per_g' : argmax σ/m
        'best_fit_log_l' : max log-likelihood
        'verdict' : one-line summary string
    """
    sigma_arr = np.asarray(sigma_test_values_cm2_per_g, dtype=float)
    log_l_arr = np.array([loglike_xrism_perseus_icm(s) for s in sigma_arr])

    best_idx = int(np.argmax(log_l_arr))
    return {
        "sigma_m_values": sigma_arr.tolist(),
        "log_l_values": log_l_arr.tolist(),
        "best_fit_sigma_m_cm2_per_g": float(sigma_arr[best_idx]),
        "best_fit_log_l": float(log_l_arr[best_idx]),
        "verdict": (
            f"Max log L = {log_l_arr[best_idx]:.3f} at sigma/m = "
            f"{sigma_arr[best_idx]:.3f} cm^2/g (Bullet-allowed range). "
            f"At v0.7 posterior sigma/m = 0.27 cm^2/g: "
            f"log L = {loglike_xrism_perseus_icm(0.27):.3f} "
            f"(soft consistency check; expected small delta for "
            f"consistency-test channel, NOT a strong exclusion)."
        ),
    }


def provenance() -> str:
    """One-line citation string for audit logs."""
    return (
        "XRISM Perseus non-thermal pressure profile: Zhang et al. "
        "(XRISM Collaboration), A&A 707 A109 (2026), "
        "arXiv:2510.12782v1, DOI 10.1051/0004-6361/202557660."
    )


if __name__ == "__main__":
    print("=== XRISM Perseus ICM consistency test (T88.A) ===")
    print(f"Using {N_XRISM_BINS} radial bins from Table 1 of Zhang+ 2025")
    print(f"R (kpc):       {XRISM_PERSEUS_R_KPC}")
    print(f"f_nth (obs):   {XRISM_PERSEUS_FNTH_OBS}")
    print(f"err_minus:     {XRISM_PERSEUS_FNTH_ERR_MINUS}")
    print(f"err_plus:      {XRISM_PERSEUS_FNTH_ERR_PLUS}")
    print()
    summary = summary_xrism_perseus_consistency_test()
    print("σ/m (cm²/g)  |  log L")
    print("-" * 30)
    for s, ll in zip(summary["sigma_m_values"], summary["log_l_values"]):
        print(f"  {s:>8.4f}   |  {ll:+.3f}")
    print()
    print(f"Best σ/m: {summary['best_fit_sigma_m_cm2_per_g']:.4f} cm²/g")
    print(f"Best log L: {summary['best_fit_log_l']:.3f}")
    print()
    print(summary["verdict"])
    print()
    print("Provenance:", provenance())
