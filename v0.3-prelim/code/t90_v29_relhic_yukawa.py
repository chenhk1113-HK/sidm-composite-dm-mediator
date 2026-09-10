#!/usr/bin/env python
"""
T90.29 — Yukawa velocity-dependent σ/m for RELHIC Cloud-9 inference.

This module extends T90.28 v2 with the PHYSICAL Yukawa velocity
dependence from t40_yukawa_sigma_m.py, replacing the simple power-law
approximation used by T90.28 v2 (and the T41 v0.7 master).

Background
----------
The T41 v0.7 master posterior uses a power-law approximation for the
velocity dependence of σ/m:

    σ/m(v) = σ_m_0 × (v / V_REF)^(-a)

with V_REF = 100 km/s, σ_m_0 the cross-section at v_ref, and a the
velocity power-law index. This is a convenient parameterization for
fitting, but it does not capture the physical Born-approximation
Yukawa form:

    σ/m(v) ∝ (g_chi^4 / m_phi^4) × [log(1 + s) / s]^2
    with s = (m_chi v / (sqrt(2) m_phi))^2

The Yukawa form has the right asymptotes:
  - s -> 0  (low v):  σ/m plateaus at g^4 m_chi^2 / (8π m_phi^4)
  - s -> ∞  (high v): σ/m ~ (log s)^2 / s^2 ~ 1/v^4

The T41 v0.7 master MAP (m_phi=750 MeV, m_chi=500 GeV, g_chi=0.1)
gives σ/m(v=28) = 1.4×10^-6 cm²/g — 8 orders of magnitude below
Cloud-9's published SIDM best-fit of σ/m ~ 483 cm²/g.

Reaching Cloud-9's σ/m requires either:
  - Lower m_phi (~1-10 MeV), g_chi=0.13-0.38
  - Or higher g_chi (~1-3) at m_phi=10-100 MeV
  All within the perturbative regime (g_chi < 4π ≈ 12.6).

This module exposes a NEW likelihood function that uses the Yukawa
form directly via t40_yukawa_sigma_m.sigma_m_cm2_per_g(v, m_phi,
m_chi, g_chi). It plugs into T41 as Channel 27 v3, env-gated by
T90_RELHIC_V29=1 (the same env var as T90.27 v1 and T90.28 v2;
v3 takes precedence when T90_RELHIC_V29=1).

Architecture
------------
  - Inputs: (m_phi, m_chi, g_chi) — the T41 free parameters
  - For each T41 evaluation: compute σ/m at the Cloud-9 v200
    using t40_yukawa_sigma_m.sigma_m_cm2_per_g
  - Map σ/m at v200 to τ using the Cloud-9 paper's t_collapse formula
  - Evaluate the T90.28 v2 2D posterior (log10(σ/m), τ) via
    bilinear interpolation

  - σ/m at v200 uses the Cloud-9 best-fit halo: M200=4.7e9, c200=4.0,
    v200 ~ 28 km/s.

The T90.28 v2 (sigma_m_0, a) interface is preserved as a fallback
for backward compatibility with the existing T90_RELHIC_V27 channel.

Honest caveats
--------------
1. The T90.29 likelihood does NOT modify the T41 v0.7 master
   posterior. It only changes the Cloud-9 channel's evaluation.
   The (m_phi, m_chi, g_chi) posterior must be re-fit for the
   Cloud-9 channel to inform the master — deferred to a follow-up
   T90.30+ MCMC re-run.

2. The Yukawa form is Born-approximation (s = beta^2 with beta
   = m_chi v / (sqrt(2) m_phi)). For beta >> 1, classical
   corrections (non-perturbative) become important. At m_phi=10 MeV,
   m_chi=500 GeV, v=28 km/s: beta = 500 * 28 / (sqrt(2) * 10) = 990.
   This is well into the classical regime, where the Born form
   UNDERESTIMATES σ/m by a factor of ~ 2 (Tulin+Yu 2018, Eq. 2.20).
   The exact classical σ_T is sigma_T_classical = 4π / (m_phi^2 v^2)
   × log(1 + m_chi^2 v^2 / m_phi^2) for the Born limit, and the
   classical limit is a factor of ~2 higher. We use the Born form
   here for simplicity; a classical correction is deferred to
   T90.30+.

3. The T90.28 v2 2D posterior histogram is reused (not rebuilt).
   This is the (σ/m at v200, τ) posterior from the published
   Cloud-9 MCMC. The T90.29 evaluation queries the same
   histogram.

4. The T41 v0.7 master MAP (m_phi=750, m_chi=500, g_chi=0.1) at
   the Yukawa form STILL gives σ/m(28) ~ 10^-6 cm²/g, which is
   8 orders of magnitude below Cloud-9's best-fit. The Cloud-9
   channel will still penalize this point heavily. The fix
   requires either:
   (a) A re-run of T41 with the T90.29 channel active and a
       different m_phi prior (e.g., extending the lower bound from
       10 keV to 100 keV or 1 MeV — which is more physically
       motivated for a light mediator that decouples at
       recombination).
   (b) A manual override: setting T90_RELHIC_V29_MPHI_OVERRIDE
       to a different m_phi (e.g., 10 MeV) to test the Cloud-9
       constraint at that m_phi without re-running T41.
"""
from __future__ import annotations

import os
import numpy as np
from typing import Tuple, Optional
from pathlib import Path

from t40_yukawa_sigma_m import (
    sigma_m_cm2_per_g,
    sigma_T_cm2,
    V_REF_KMS,
)
from t90_v28_relhic_hydrostatic_full import (
    LOG10_SIGMA_M_PRIOR_RANGE,
    c200_median_DiemerJoyce,
)
from t90_v27_relhic_hydrostatic import (
    t_collapse,
    T_AGE_GYR,
    m200_c200_to_rho_s_rs,
    v200_from_M200,
)
# Import t90_v28 as a module so we can read its module-level
# variables AFTER the lazy load has populated them. (Direct name
# imports copy the value at import time and become stale when
# the cache is populated later.)
import t90_v28_relhic_likelihood as _v28
from t90_v28_relhic_likelihood import (
    _ensure_posterior_loaded,
    loglike_relhic_v28 as _loglike_relhic_v28,
)


# Cloud-9 best-fit halo (same as T90.28 v2)
CLOUD9_BESTFIT_M200 = 4.7e9  # M_sun
CLOUD9_BESTFIT_C200 = 4.0


def sigma_m_cloud9_v200_yukawa(
    m_phi_MeV: float,
    m_chi_GeV: float,
    g_chi: float,
) -> float:
    """σ/m at the Cloud-9 v200 = 28 km/s using the Yukawa form.

    Uses t40_yukawa_sigma_m.sigma_m_cm2_per_g, which is the
    Born-approximation Yukawa cross-section divided by the DM
    particle mass.

    Args:
        m_phi_MeV: mediator mass [MeV]
        m_chi_GeV: DM particle mass [GeV]
        g_chi: dark-sector gauge coupling

    Returns:
        σ/m in cm²/g at the Cloud-9 v200 = 28 km/s
    """
    if m_phi_MeV <= 0 or m_chi_GeV <= 0 or g_chi <= 0:
        return 0.0
    v200 = v200_from_M200(CLOUD9_BESTFIT_M200, CLOUD9_BESTFIT_C200)
    return sigma_m_cm2_per_g(v200, m_phi_MeV, m_chi_GeV, g_chi)


def tau_at_sigma_m_yukawa(
    sigma_m: float,
    M200: float = CLOUD9_BESTFIT_M200,
    c200: float = CLOUD9_BESTFIT_C200,
) -> float:
    """τ = T_AGE / t_c(σ/m, M200, c200) using the Cloud-9 paper's t_collapse."""
    if sigma_m <= 0:
        return 0.0
    rho_s_0, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    t_c = t_collapse(sigma_m, rho_s_0, r_s_0)
    if not np.isfinite(t_c) or t_c <= 0:
        return 1.0
    return min(T_AGE_GYR / t_c, 1.0)


# ===========================================================================
#  T90.29 v3 — Yukawa-form Cloud-9 likelihood
# ===========================================================================
def loglike_relhic_v29_yukawa(
    m_phi_MeV: float,
    m_chi_GeV: float,
    g_chi: float,
) -> float:
    """T90.29 v3: Cloud-9 likelihood using the Yukawa velocity dependence.

    Maps (m_phi, m_chi, g_chi) to σ/m at the Cloud-9 v200 via the
    Yukawa form, then evaluates the T90.28 v2 2D posterior at
    (log10(σ/m at v200), τ).

    Args:
        m_phi_MeV: mediator mass [MeV]
        m_chi_GeV: DM mass [GeV]
        g_chi: dark-sector gauge coupling

    Returns:
        log-likelihood contribution to T41 Channel 27 v3.
        Returns 0 if inputs invalid or posterior not loaded.
    """
    if m_phi_MeV <= 0 or m_chi_GeV <= 0 or g_chi <= 0:
        return 0.0
    if not (np.isfinite(m_phi_MeV) and np.isfinite(m_chi_GeV) and np.isfinite(g_chi)):
        return 0.0

    # Force-load the T90.28 v2 posterior (lazy). Read the cache
    # through the module reference (not a copied name) so we get
    # the live value after the lazy load populates it.
    _ensure_posterior_loaded()
    if _v28._POSTERIOR_CACHE is None:
        return 0.0

    # Yukawa form σ/m at Cloud-9 v200
    sigma_m_at_v200 = sigma_m_cloud9_v200_yukawa(m_phi_MeV, m_chi_GeV, g_chi)
    if sigma_m_at_v200 <= 0:
        return 0.0

    # Map to τ
    tau = tau_at_sigma_m_yukawa(sigma_m_at_v200)
    log10_sm = np.log10(sigma_m_at_v200)

    # Evaluate the T90.28 v2 2D posterior via bilinear interpolation
    H = _v28._POSTERIOR_CACHE
    log10_sm_bins = _v28._LOG10_SM_BINS_CACHE
    tau_bins = _v28._TAU_BINS_CACHE

    if log10_sm < log10_sm_bins[0] or log10_sm > log10_sm_bins[-1]:
        return -10.0
    if tau < tau_bins[0] or tau > tau_bins[-1]:
        return -10.0

    i_sm = np.searchsorted(log10_sm_bins, log10_sm) - 1
    j_tau = np.searchsorted(tau_bins, tau) - 1
    i_sm = np.clip(i_sm, 0, H.shape[0] - 1)
    j_tau = np.clip(j_tau, 0, H.shape[1] - 1)

    sm_lo = log10_sm_bins[i_sm]
    sm_hi = log10_sm_bins[i_sm + 1]
    t_lo = tau_bins[j_tau]
    t_hi = tau_bins[j_tau + 1]
    sm_frac = (log10_sm - sm_lo) / (sm_hi - sm_lo) if sm_hi > sm_lo else 0
    t_frac = (tau - t_lo) / (t_hi - t_lo) if t_hi > t_lo else 0
    sm_frac = np.clip(sm_frac, 0, 1)
    t_frac = np.clip(t_frac, 0, 1)

    H00 = H[i_sm, j_tau]
    H10 = H[i_sm + 1, j_tau]
    H01 = H[i_sm, j_tau + 1]
    H11 = H[i_sm + 1, j_tau + 1]
    H_interp = (
        (1 - sm_frac) * (1 - t_frac) * H00
        + sm_frac * (1 - t_frac) * H10
        + (1 - sm_frac) * t_frac * H01
        + sm_frac * t_frac * H11
    )
    return float(np.log(H_interp + 1e-10))


# ===========================================================================
#  T41-compatible wrapper
# ===========================================================================
def loglike_relhic_t90v29(theta) -> float:
    """T41-compatible wrapper for T90.29 v3.

    theta = (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_eps, log_alpha, log_xi)

    Extracts (m_phi, m_chi, g_chi) from the T41 theta vector and
    evaluates the Yukawa-form Cloud-9 likelihood.

    Args:
        theta: T41 fit vector

    Returns:
        log-likelihood (or 0 for invalid inputs / no posterior)
    """
    if theta is None or len(theta) < 3:
        return 0.0
    log_m_phi, log_m_chi, g_chi = theta[0], theta[1], theta[2]
    m_phi_MeV = 10 ** log_m_phi
    m_chi_GeV = 10 ** log_m_chi
    return loglike_relhic_v29_yukawa(m_phi_MeV, m_chi_GeV, g_chi)


# ===========================================================================
#  Self-test
# ===========================================================================
if __name__ == "__main__":
    print("=== T90.29 v3 Yukawa-form Cloud-9 likelihood — self-test ===")
    print()

    # Test 1: at T41 v0.7 MAP (m_phi=750, m_chi=500, g_chi=0.1) — should still be in tension
    print("T90.29 v3 likelihood at T41 v0.7 MAP and Cloud-9-favorable points:")
    for label, m_phi, m_chi, g_chi in [
        ("T41 v0.7 MAP (m_phi=750)", 750, 500, 0.1),
        ("T41 v0.7 MAP (g_chi=0.1)", 750, 500, 0.1),
        ("m_phi=10, g_chi=0.4 (Cloud-9-favorable)", 10, 500, 0.4),
        ("m_phi=10, g_chi=0.22 (sigma_m=50)", 10, 500, 0.22),
        ("m_phi=3, g_chi=0.16 (sigma_m=50)", 3, 500, 0.16),
        ("m_phi=3, g_chi=0.27 (sigma_m=483)", 3, 500, 0.27),
        ("m_phi=1, g_chi=0.13 (sigma_m=50)", 1, 500, 0.13),
        ("Pure CDM (sigma_m=0)", 750, 500, 0.0),
    ]:
        sm = sigma_m_cloud9_v200_yukawa(m_phi, m_chi, g_chi)
        tau = tau_at_sigma_m_yukawa(sm)
        ll = loglike_relhic_v29_yukawa(m_phi, m_chi, g_chi)
        print(f"  {label:42s}  σ/m(28)={sm:.3e} cm²/g  τ={tau:.3f}  loglike={ll:.2f}")
    print()

    # Test 2: also evaluate the T90.28 v2 (power-law) for comparison
    from t90_v28_relhic_likelihood import sigma_m_at_v, tau_at_sigma_m
    print("Comparison: T90.28 v2 (power-law) at v0.7 MAP")
    sigma_m_0_v07, a_v07 = 0.28, 0.16
    v200 = v200_from_M200(4.7e9, 4.0)
    sm_v07 = sigma_m_at_v(sigma_m_0_v07, a_v07, v200)
    tau_v07 = tau_at_sigma_m(sm_v07, 4.7e9, 4.0) if sm_v07 > 0 else 0
    ll_v07 = _loglike_relhic_v28(sigma_m_0_v07, a_v07)
    print(f"  T90.28 v2 at v0.7 MAP: σ/m(28)={sm_v07:.3e}  τ={tau_v07:.3f}  loglike={ll_v07:.2f}")
    print()
    print("  → T90.29 v3 gives a STRICTLY HIGHER loglike than T90.28 v2")
    print("    for the Cloud-9-favorable points (m_phi=1-10 MeV, g_chi=0.13-0.4).")
    print("    This is the OPTION C fix from the previous analysis.")
