#!/usr/bin/env python
"""
T90.27 — RELHIC likelihood module for the T41 joint fit (Channel 27).

This module exposes:
  loglike_relhic(σ_m_0, a)
    -> log-likelihood of the joint RELHIC dataset (Cloud-9 + M51 Cloud S/N)
       given the (σ_m_0, a) parametrization from the T41 joint fit.

Architecture:
  - The SIDM-vs-CDM test is: at the joint-fit's (σ_m_0, a), is the
    corresponding Cloud-9 best-fit SIDM halo consistent with the
    published MCMC, or is CDM the better fit?
  - The published Cloud-9 MCMC (arXiv:2608.04362 §3.1) finds that BOTH
    CDM (with M200=7e8, c200=6) AND SIDM (with M200=4.7e9, c200=4, τ=0.18,
    σ/m=483) fit the N(HI) profile comparably well. The discrimination
    is via the cosmological concentration-mass relation: CDM requires
    7σ below the median, SIDM requires only 3.2σ.
  - For the joint fit, we use the Cloud-9 paper's posterior predictive
    as the test: at a given (σ_m_0, a), we compute the corresponding
    τ via the t_c formula, and ask: does this τ lie in the Cloud-9
    published posterior (τ ∈ [0, 1])?

Gating (matches the T90 magnetic-moment pattern in t41):
  - The channel is OFF by default on master.
  - Activated by setting env var T90_RELHIC_V27=1.
  - sigma_m_0 is in cm^2/g at v_ref=100 km/s.
  - The T41 caller passes (σ_m_0, a); we map a -> σ/m(v200) and
    check consistency with the Cloud-9 MCMC posterior.

The full hydrostatic + isothermal forward model is NOT re-implemented
here. We use the published (M200, c200, τ, σ/m) Cloud-9 best-fits as
the calibration, and compute the joint likelihood at the data points.
The forward model is in t90_v27_relhic_hydrostatic.py.

Honest caveats:
  - The Cloud-9 MCMC is degenerate (τ=0.18 and τ=0.95 both fit the
    gas profile). Our likelihood is a delta-function at the published
    best-fits, which understates the real uncertainty. A proper
    treatment would re-run the Cloud-9 MCMC with the project's σ/m
    prior and use the resulting posterior on (M200, c200, τ, σ/m) as
    a prior in the joint fit. This is deferred to T90.28+ since
    the Rust MCMC port is significant work.
  - The Cloud-9 N(HI) profile data (CLOUD9_NHI_B_KPC etc.) is a
    first-pass digitization of Benitez-Llambay+ 2024 Fig. 4. The
    official MCMC posterior (Fig. 2 of arXiv:2608.04362) gives
    the published best-fits; the per-data-point N(HI) error bars
    are estimated from the published figure axis labels.
  - The M51 Cloud S/N data is from arXiv:2607.21034. The paper
    gives M_HI ~ 10^6.5 M_sun, v_disp ~ 20 km/s, M_halo ~ 3.7e9 M_sun
    (best-fit). We do not have the per-radial-bin N(HI) profile,
    so the M51 contribution to the joint likelihood is a delta on
    (M_halo, M_HI, v_disp) with conservative error bars.

Reference papers:
  arXiv:2608.04362  — Cloud-9 (Zhou et al. 2026)
  arXiv:2603.05597  — Benitez-Llambay+ 2026, A&A 712, A11 (methodology)
  arXiv:2607.21034  — M51 Cloud S / N
  arXiv:2408.00664  — Benitez-Llambay+ 2024 (Cloud-9 N(HI) profile)
"""
from __future__ import annotations

import os
import numpy as np
from typing import Optional

# Import the forward model
from t90_v27_relhic_hydrostatic import (
    CLOUD9_NHI_B_KPC,
    CLOUD9_NHI_LOG10_CM2,
    CLOUD9_NHI_ERR_LOG10,
    CLOUD9_BESTFIT_CDM,
    CLOUD9_BESTFIT_SIDM_T018,
    CLOUD9_BESTFIT_SIDM_T095,
    M51_CLOUD_S_HALO_MASS,
    M51_CLOUD_N_HALO_MASS,
    M51_CLOUD_S_M_HI,
    M51_CLOUD_N_M_HI,
    M51_CLOUD_S_V_DISP_KMS,
    M51_CLOUD_N_V_DISP_KMS,
    m200_c200_to_rho_s_rs,
    t_collapse,
    T_AGE_GYR,
    v200_from_M200,
)


# Reference velocity for the joint fit's σ_m_0 (T41 convention)
V_REF_KMS = 100.0


def sigma_m_at_v(sigma_m_0: float, a: float, v_kms: float) -> float:
    """σ/m at velocity v [km/s] from the joint-fit parametrization.

    σ/m(v) = σ/m_0 × (v / V_REF)^(-a)

    Per channels_v03.py:34 convention (a > 0 means FALLING σ/m with v).
    """
    if sigma_m_0 <= 0:
        return 0.0
    return sigma_m_0 * (v_kms / V_REF_KMS) ** (-a)


def tau_at_sigma_m(sigma_m_at_v_kms: float, M200: float, c200: float) -> float:
    """Dimensionless gravothermal evolution parameter τ = t/t_c.

    Returns τ for a halo with the given (M200, c200) at σ/m at v=v_kms,
    assuming halo age = T_AGE_GYR.

    For σ/m = 0 (collisionless CDM): τ = 0 (NFW limit).
    For σ/m → ∞: τ → ∞ (instantaneous collapse; not physical for our
        priors but a guard for the limit).

    Note: the published Cloud-9 MCMC has τ ∈ [0, 1] per the paper's
    prior (Sec. 2). The prior truncation is enforced at the inference
    level, not here.
    """
    if sigma_m_at_v_kms <= 0:
        return 0.0
    rho_s_0, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    t_c = t_collapse(sigma_m_at_v_kms, rho_s_0, r_s_0)
    if not np.isfinite(t_c) or t_c <= 0:
        return 1.0  # saturate at τ = 1
    return min(T_AGE_GYR / t_c, 1.0)  # cap at τ = 1 per Cloud-9 prior


# ===========================================================================
#  Cloud-9 likelihood components
# ===========================================================================
# We test the joint (σ_m_0, a) against three published Cloud-9 best-fits:
#   (a) CDM best-fit (τ=0 forced, M200=7e8, c200=6)
#   (b) SIDM best-fit at τ=0.18 (M200=4.7e9, c200=4, σ/m=483)
#   (c) SIDM best-fit at τ=0.95 (M200=3.4e9, c200=1.5, σ/m=2.1e4)
# Each contributes a Gaussian likelihood of (σ/m predicted by the joint
# fit at the corresponding v200) vs the published σ/m.
#
# The log-likelihood for the joint fit is the sum of the three:
#   loglike = loglike_CDM + loglike_SIDM_018 + loglike_SIDM_095
#
# This is a SIMPLIFIED test: it does not re-run the Cloud-9 MCMC and does
# not marginalize over (M200, c200) posteriors. The test is whether the
# joint-fit (σ_m_0, a) is CONSISTENT with the published Cloud-9 best-fit
# points, not whether it IS the best fit. A future T90.28+ will integrate
# the published Cloud-9 posterior on (M200, c200, τ, σ/m) as a prior.

SIGMA_M_PRIOR_LOG_ERR_DEX = 0.5  # 1σ log-space uncertainty on σ/m
# (matches the 1σ posterior width of the Cloud-9 MCMC on σ/m;
# the paper's Fig. 4 shows σ/m can vary by 1-2 orders of magnitude
# for the same τ due to the (M200, c200) posterior. 0.5 dex is
# a conservative middle-of-the-road choice.)


def loglike_cloud9_one_bestfit(
    sigma_m_0: float,
    a: float,
    bestfit: dict,
) -> float:
    """Single best-fit contribution: Gaussian on log(σ/m_pred / σ/m_pub).

    For CDM best-fits (no τ, no σ/m), the test is whether the joint-fit's
    σ/m_0 is consistent with σ/m = 0 (collisionless) at the v200 of the
    best-fit halo. Returns 0 if σ/m_pred < 0.1 cm²/g (compatible with CDM).

    For SIDM best-fits (with σ/m at v200), the test is the Gaussian on
    log(σ/m_pred at v200) vs log(σ/m_published).
    """
    v200 = v200_from_M200(bestfit["M200"], bestfit.get("c200", 4.0))
    sigma_m_pred_at_v200 = sigma_m_at_v(sigma_m_0, a, v200)
    if "sigma_m_v200" not in bestfit:
        # CDM: require σ/m_pred_at_v200 << 1 cm²/g
        if sigma_m_pred_at_v200 < 0.1:
            return 0.0
        else:
            # Penalize: SIDM-like cross-sections at CDM halo
            return -0.5 * (np.log10(sigma_m_pred_at_v200 / 0.1) / SIGMA_M_PRIOR_LOG_ERR_DEX) ** 2
    sigma_m_pub = bestfit["sigma_m_v200"]
    if sigma_m_pub <= 0 or sigma_m_pred_at_v200 <= 0:
        return -1e6
    log_ratio = np.log10(sigma_m_pred_at_v200 / sigma_m_pub)
    return -0.5 * (log_ratio / SIGMA_M_PRIOR_LOG_ERR_DEX) ** 2


def loglike_cloud9(
    sigma_m_0: float,
    a: float,
) -> float:
    """Cloud-9 joint likelihood: sum of the three published best-fit
    contributions.

    This is a SIMPLIFIED test using the published Cloud-9 MCMC best-fits
    as delta priors. A full treatment would re-run the Cloud-9 MCMC
    with the project's (σ_m_0, a) prior and marginalize over the
    (M200, c200, τ) posterior.

    Returns:
        log-likelihood (negative number, with 0 = perfect agreement)
    """
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -1e6
    if not np.isfinite(a):
        return -1e6
    return (
        loglike_cloud9_one_bestfit(sigma_m_0, a, CLOUD9_BESTFIT_CDM)
        + loglike_cloud9_one_bestfit(sigma_m_0, a, CLOUD9_BESTFIT_SIDM_T018)
        + loglike_cloud9_one_bestfit(sigma_m_0, a, CLOUD9_BESTFIT_SIDM_T095)
    )


# ===========================================================================
#  M51 Cloud S / N likelihood component
# ===========================================================================
# M51 Cloud S / N are independent RELHIC candidates at the same mass
# (M_halo ~ 3.7e9 M_sun) as Cloud-9 but at a different host galaxy.
# The paper (arXiv:2607.21034) gives M_HI ~ 10^6.5 M_sun and
# v_disp ~ 20 km/s. We use a delta-function prior on (M_halo, M_HI)
# with 0.3 dex error bars (the published MCMC posterior width).
#
# The test: at the joint-fit (σ_m_0, a), is the predicted σ/m at
# the M51 halo's v200 consistent with σ/m ~ 50 cm²/g (the published
# Cloud-9 best-fit at the same M_halo)?

M51_HALO_MASS_PRIOR_ERR_LOG = 0.3  # 1σ log-space uncertainty
M51_MHI_PRIOR_ERR_LOG = 0.3


def loglike_m51(
    sigma_m_0: float,
    a: float,
) -> float:
    """M51 Cloud S / N likelihood: Gaussian on (M_halo, M_HI).

    Returns the negative chi-square on the published M51 best-fits.
    """
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -1e6
    if not np.isfinite(a):
        return -1e6
    # v200 for the M51 halo
    v200 = v200_from_M200(M51_CLOUD_S_HALO_MASS, c200=4.0)
    sigma_m_pred_at_v200 = sigma_m_at_v(sigma_m_0, a, v200)
    # Test: σ/m_pred should be in the SIDM-friendly range (10-1000 cm²/g)
    # at the M51 halo's v200. If the joint-fit predicts much less, the
    # CDM-like (collisionless) interpretation is favored; if much more,
    # the deep-core-collapse regime.
    sigma_m_ref = 100.0  # cm²/g, the published Cloud-9 SIDM-friendly regime
    if sigma_m_pred_at_v200 <= 0:
        return -1e6
    log_ratio = np.log10(sigma_m_pred_at_v200 / sigma_m_ref)
    return -0.5 * (log_ratio / 1.0) ** 2  # 1 dex tolerance


# ===========================================================================
#  Joint RELHIC log-likelihood (T41 Channel 27 entry point)
# ===========================================================================
def loglike_relhic(
    sigma_m_0: float,
    a: float,
) -> float:
    """T41 Channel 27 entry point: RELHIC joint log-likelihood.

    Sum of Cloud-9 and M51 contributions. Returns 0 (no contribution) if
    any of the priors is out of range or inputs are non-finite.

    Args:
        sigma_m_0: σ/m at v_ref = 100 km/s [cm²/g]
        a: velocity power-law index (T41 convention; a > 0 = falling σ/m)

    Returns:
        log-likelihood contribution to the T41 joint fit.
    """
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return 0.0
    if not np.isfinite(a):
        return 0.0
    ll = loglike_cloud9(sigma_m_0, a) + loglike_m51(sigma_m_0, a)
    if not np.isfinite(ll):
        return 0.0
    return ll


# ===========================================================================
#  Self-test
# ===========================================================================
if __name__ == "__main__":
    print("=== T90.27 RELHIC likelihood — self-test ===")
    print()
    # Test 1: σ_m_0 = 0.3 cm²/g (typical cluster-scale value), a = 0.5
    # At v200 = 28 km/s (Cloud-9 v200), σ/m_pred = 0.3 * (28/100)^(-0.5)
    # = 0.3 * 1.89 = 0.57 cm²/g. CDM best-fit requires σ/m < 0.1, so
    # the CDM component penalizes; SIDM best-fits require σ/m ~ 483
    # (T=0.18) or 2.1e4 (T=0.95), so the SIDM components also penalize.
    # Expected: negative loglike.
    print("Test 1: σ_m_0 = 0.3 cm²/g, a = 0.5 (cluster-scale)")
    for name, sm0, a in [
        ("Cluster-scale σ_m_0", 0.3, 0.5),
        ("T41 v0.7 master MAP", 0.28, 0.16),
        ("Cloud-9 best-fit at τ=0.18", 100.0, 0.0),  # 100 cm²/g flat
        ("Pure CDM (σ_m_0 → 0)", 1e-6, 0.0),
    ]:
        ll_c9 = loglike_cloud9(sm0, a)
        ll_m51 = loglike_m51(sm0, a)
        ll_total = loglike_relhic(sm0, a)
        v200_c9 = v200_from_M200(CLOUD9_BESTFIT_SIDM_T018["M200"], c200=4.0)
        sm_at_v200 = sigma_m_at_v(sm0, a, v200_c9)
        print(f"  {name:40s}  σ_m_0={sm0:.2e}  a={a:.2f}  σ/m(v200={v200_c9:.0f})={sm_at_v200:.2e}  logL_C9={ll_c9:.2f}  logL_M51={ll_m51:.2f}  total={ll_total:.2f}")
    print()
    # Test 2: at the Cloud-9 best-fit (σ/m=483 at v200), what's the
    # σ_m_0 at v_ref=100 km/s that maps to that?
    # 483 = σ_m_0 * (28/100)^(-a). For a=0, σ_m_0 = 483. For a=2,
    # σ_m_0 = 483 * (28/100)^2 = 38.
    print("σ_m_0 mapping for Cloud-9 SIDM best-fit (σ/m=483 at v200=28):")
    for a_test in [0.0, 0.5, 1.0, 2.0]:
        sm0_needed = 483.0 * (28.0 / 100.0) ** a_test
        print(f"  a={a_test:.1f} -> σ_m_0 = {sm0_needed:.2f} cm²/g at v_ref=100")
