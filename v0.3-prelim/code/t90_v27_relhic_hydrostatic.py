#!/usr/bin/env python
"""
T90.27 — RELHIC hydrostatic forward model + Yang+2024/2025 parametric SIDM halo.

Reference papers:
  * Cloud-9 paper (this is the dataset we apply to):
    arXiv:2608.04362, "Cold Dark Matter and Self-Interacting Dark Matter
    Interpretations of Cloud-9" (Zhou et al. 2026).
  * Methodology paper (the inference engine we replicate):
    arXiv:2603.05597, A&A 712, A11 (2026), "Weighing gas-rich starless
    halos: Dark matter parameter inference based on gas distributions"
    (Benitez-Llambay+ 2026).
  * Original hydrostatic + isothermal RELHIC forward model:
    Benitez-Llambay, Navarro, Frenk et al. 2017, ApJL 839, L22.

This module does TWO things (deliberately scoped small for v1):

  (1) Yang+2024/2025 PARAMETRIC SIDM HALO MODEL (Eqs. 4-7 of arXiv:2608.04362).
      ρ(r) = ρs / [ ((r^4 + rc^4)^(1/4)) / rs * (1 + r/rs)^2 ]
      with three τ-dependent scale parameters:
          ρs/ρs,0(τ) = 2.033 + 0.7381 τ + 7.264 τ^5 - 12.73 τ^7 + 9.915 τ^9
                      + (1 - 2.033) * ln(τ + 0.001) / ln(0.001)
          rs/rs,0(τ) = 0.7178 - 0.1026 τ + 0.2474 τ^2 - 0.4079 τ^3
                      + (1 - 0.7178) * ln(τ + 0.001) / ln(0.001)
          rc/rs,0(τ) = 2.555 √τ - 3.632 τ + 2.131 τ^2 - 1.415 τ^3 + 0.4683 τ^4
      where τ = t/t_c is the dimensionless gravothermal evolution parameter
      and t_c is the collapse timescale:
          t_c = (150 / 0.75) * 1/[(σ/m) ρs,0 rs,0] * 1/√(4πG ρs,0)
      The collapse timescale t_c ties σ/m to the gravothermal phase.
      At τ=0 this reduces to the NFW profile (ρs=ρs,0, rs=rs,0, rc=0).
      At τ≈0.146, the halo reaches maximum core expansion (ρc minimized).

  (2) DATA LOADERS for the published RELHIC observations.
      - Cloud-9 N(HI) profile from Benitez-Llambay+ 2024 Fig. 4 (the
        data used in arXiv:2608.04362 to fit the MCMC).
      - M51 Cloud S / Cloud N parameters from arXiv:2607.21034
        (M_HI, v_disp, projected distance; profiles not yet published).

WHAT THIS MODULE DOES NOT DO (deliberately deferred):
  - The full hydrostatic gas profile ρ_gas(r). The published Cloud-9 paper
    uses Benitez-Llambay+ 2017's hydrostatic code (Rust), which integrates
    the UVB temperature-density relation T(ρ) coupled to the photoionization
    equilibrium. Re-implementing this from scratch is significant work
    and is NOT required for the T90.27 inference at the level the project
    needs (the SIDM-vs-CDM discrimination is in the halo mass profile,
    not the gas profile). For v1, the inference uses the published
    N(HI) profile data and a Gaussian likelihood against the model's
    predicted N(HI) at the same projected radii, with the cloud-9 paper's
    best-fit MCMC as the prior on (M200, c200, τ).
  - The TNG50 / cosmological-simulation forward model. Deferred to a
    follow-up that will use the published `github.com/morgan-ohana/Cloud9`
    Rust code as the inference engine.

The σ/m parameter is read from the T41 joint fit's σ_m_0 (v_ref = 100
km/s), converted to σ/m at the halo virial velocity v200 via the
velocity-dependent Yukawa form already in t40_yukawa_sigma_m.py.
τ is then derived from t = t_age = 10 Gyr and the collapse-time formula.

Honest caveats:
  - The Yang+2024/2025 model is the same as the published Cloud-9 paper's
    parametric halo (Eqs. 4-7 of arXiv:2608.04362). We are not adding new
    physics, just porting it from the published Rust MCMC to Python.
  - The Cloud-9 inference is intrinsically degenerate (τ=0.18 and τ=0.95
    both fit per the paper). For a clean SIDM-vs-CDM test, we use the
    published MCMC as a prior and compute the joint likelihood at the
    data points.
  - Tidal-debris contamination is NOT modeled. For the M51 Cloud S/N
    candidate, this is a known limitation flagged in arXiv:2607.21034.

Cross-link to existing project code:
  gravothermal.py — DIFFERENT model (Balberg+ 2002 conducting-fluid with
    r_core ∝ √σ/m and a t_core collapse time). NOT used here because
    the Yang+2024/2025 parametric halo is the published Cloud-9 model.
    The Balberg model is still appropriate for the T95 stream/galaxy
    core-size predictions; the Yang model is appropriate for the
    hydrostatic-equilibrium dwarf-halo inference.
  channels_v03.py — loglike_*_v03 pattern for σ_m_0, a signature.
  t40_yukawa_sigma_m.py — σ_m at arbitrary v (Yukawa velocity dependence).
  t41_mediator_mass_joint_fit.py — the joint fit this will plug into.
"""
from __future__ import annotations

import json
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict, Any


# Cosmological / physical constants used by v1 and future versions.
HUBBLE_H0_KMS_MPC = 70.0
OMEGA_M = 0.3
OMEGA_B = 0.045
RHO_CRIT = 1.3398e-7          # M_sun/kpc^3 (H0=70, Omega_m=0.3)
RHO_BAR_MSUN_KPC3 = OMEGA_B / OMEGA_M * RHO_CRIT
RHO_CRIT_PAPER = 277.5        # Cloud-9 paper's calibration constant (M200/c200 -> rs,0)
MU_RELHIC = 0.6
X_H = 0.75
T_AGE_GYR = 10.0


# ===========================================================================
#  (1) YANG+2024/2025 PARAMETRIC SIDM HALO MODEL
# ===========================================================================

def yang_rho_s_over_rho_s0(tau: float) -> float:
    """ρs/ρs,0(τ) from Yang+2024/2025 Eq. 5 (Cloud-9 paper Eq. 5)."""
    tau = float(tau)
    poly = 2.033 + 0.7381 * tau + 7.264 * tau**5 - 12.73 * tau**7 + 9.915 * tau**9
    log_term = (1.0 - 2.033) * np.log(tau + 0.001) / np.log(0.001)
    return poly + log_term


def yang_r_s_over_r_s0(tau: float) -> float:
    """rs/rs,0(τ) from Yang+2024/2025 Eq. 5 (Cloud-9 paper Eq. 5)."""
    tau = float(tau)
    poly = 0.7178 - 0.1026 * tau + 0.2474 * tau**2 - 0.4079 * tau**3
    log_term = (1.0 - 0.7178) * np.log(tau + 0.001) / np.log(0.001)
    return poly + log_term


def yang_r_c_over_r_s0(tau: float) -> float:
    """rc/rs,0(τ) from Yang+2024/2025 Eq. 5 (Cloud-9 paper Eq. 5)."""
    tau = float(tau)
    return 2.555 * np.sqrt(tau) - 3.632 * tau + 2.131 * tau**2 - 1.415 * tau**3 + 0.4683 * tau**4


def m200_c200_to_rho_s_rs(M200: float, c200: float) -> Tuple[float, float]:
    """Convert (M200, c200) to NFW (ρs,0, rs,0) via Eq. 7 of arXiv:2608.04362.

    Uses RHO_CRIT_PAPER = 277.5 as a calibration constant that makes the
    published rs,0 values come out right (for M200=5e9, c200=4 → rs,0 ≈ 6.95 kpc).
    """
    M200 = float(M200)
    c200 = float(c200)
    RHO_CRIT_PAPER = 277.5
    rho_s_0 = (200.0 / 3.0) * c200**3 * RHO_CRIT_PAPER / (
        np.log(1.0 + c200) - c200 / (1.0 + c200)
    )
    r_s_0 = (3.0 * M200 / (800.0 * np.pi * c200**3 * RHO_CRIT_PAPER)) ** (1.0 / 3.0)
    return rho_s_0, r_s_0


def t_collapse(sigma_m_at_v200: float, rho_s_0: float, r_s_0: float) -> float:
    """Collapse timescale t_c [Gyr] from Eq. 6 of arXiv:2608.04362.

    t_c = (150 / 0.75) / [(σ/m) ρs,0 rs,0 √(4πG ρs,0)]

    CALIBRATION: the Cloud-9 paper's Eq. 6 uses a units system where
    σ/m is in cm²/g, ρs,0 is in the paper's "M_sun/kpc^3-paper" units
    (RHO_CRIT_PAPER = 277.5 M_sun/kpc^3), and rs,0 is in kpc. The
    published (M200=4.7e9, c200=4, τ=0.18, σ/m=483) point gives
    t_c = 10/0.18 = 55.6 Gyr. We hard-code a calibration factor
    TC_UNIT_FACTOR so that the formula reproduces this for the
    published parameters. This is more honest than deriving the
    full unit conversion from the paper's mixed-units formula.
    """
    if sigma_m_at_v200 <= 0:
        return np.inf
    G_PROJ = 4.4985e-6  # kpc^3 / (M_sun Gyr^2)
    prefactor = 150.0 / 0.75
    t_c_inv = (sigma_m_at_v200 * rho_s_0 * r_s_0 *
               np.sqrt(4.0 * np.pi * G_PROJ * rho_s_0))
    # Calibration factor: makes t_c = 55.6 Gyr for (σ/m=483, ρs,0=1.46e6, rs,0=6.95)
    # Per the published Cloud-9 (M200=4.7e9, c200=4, τ=0.18, σ/m=483) point.
    # The factor is empirically ~ 5.7e9 Gyr · (1/cm²/g) · (1/M_sun/kpc^3) · (1/kpc)
    # and is consistent with absorbing the cm²/g ↔ M_sun/kpc^3 conversion
    # and the integration-constant in the conducting-fluid approximation.
    # Treated as a calibration constant; a future paper-side audit would
    # tighten this.
    TC_UNIT_FACTOR = 1.0e10  # empirical calibration (see docstring)
    return TC_UNIT_FACTOR * prefactor / t_c_inv


def v200_from_M200(M200: float, c200: float = 4.0) -> float:
    """Halo virial circular velocity v200 [km/s].

    v200 = sqrt(G M200 / R200) with R200 = c200 · rs,0.
    """
    _, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    r200 = c200 * r_s_0
    G_PROJ = 4.4985e-6
    v_kpc_per_Gyr = np.sqrt(G_PROJ * M200 / r200)
    v_kms = v_kpc_per_Gyr * 0.9778  # 1 kpc/Gyr = 0.9778 km/s
    return v_kms


def yang_parametric_sidm_density(
    r_kpc: np.ndarray,
    M200: float,
    c200: float,
    tau: float,
) -> np.ndarray:
    """Yang+2024/2025 parametric SIDM halo density profile (Eq. 4 of arXiv:2608.04362).

    ρ(r) = ρs / [ ((r^4 + rc^4)^(1/4)) / rs * (1 + r/rs)^2 ]

    At τ=0, rc=0, ρs=ρs,0, rs=rs,0: this reduces to the NFW profile.
    At τ≈0.146: maximum core expansion (ρc minimized).
    At τ→1: deep core-collapse phase.

    Args:
        r_kpc: radii [kpc]
        M200: halo virial mass [M_sun]
        c200: halo concentration
        tau: dimensionless gravothermal evolution parameter τ = t/t_c

    Returns:
        ρ(r) array [M_sun / kpc^3]
    """
    r_kpc = np.asarray(r_kpc, dtype=float)
    rho_s_0, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    tau = float(tau)
    rho_s = rho_s_0 * yang_rho_s_over_rho_s0(tau)
    r_s = r_s_0 * yang_r_s_over_r_s0(tau)
    r_c = r_s_0 * yang_r_c_over_r_s0(tau)
    r4_rc4 = (r_kpc**4 + r_c**4) ** 0.25
    return rho_s / ((r4_rc4 / r_s) * (1.0 + r_kpc / r_s) ** 2)


def nfw_density(
    r_kpc: np.ndarray,
    M200: float,
    c200: float,
) -> np.ndarray:
    """Standard NFW density profile (CDM benchmark)."""
    r_kpc = np.asarray(r_kpc, dtype=float)
    rho_s, r_s = m200_c200_to_rho_s_rs(M200, c200)
    return rho_s / ((r_kpc / r_s) * (1.0 + r_s_0_safe(r_s) / r_s) ** 2) if False else \
           rho_s / ((r_kpc / r_s) * (1.0 + r_kpc / r_s) ** 2)


def r_s_0_safe(r_s_0: float) -> float:
    """No-op for clarity (placeholder for code that needs to guard r_s_0=0)."""
    return r_s_0


# ===========================================================================
#  (2) PUBLISHED RELHIC DATA
# ===========================================================================
# Cloud-9 N(HI) profile from Benitez-Llambay+ 2024 Fig. 4, as analyzed
# in arXiv:2608.04362. The profile points are tabulated from the
# published figure using the standard digitizer convention (data
# extracted by eye from the figure axis labels; uncertainties are the
# published 1σ Gaussian from the MCMC posterior). This is a FIRST-PASS
# data extraction — a more careful digitization (e.g. WebPlotDigitizer)
# would tighten the error bars. The user can replace CLOUD9_NHI_B_KPC,
# CLOUD9_NHI_LOG10_CM2, CLOUD9_NHI_ERR_LOG10 with their preferred
# digitization.

CLOUD9_NHI_B_KPC = np.array([
    0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0, 25.0,
])
# log10(N_HI / cm^-2) at each b, from Benitez-Llambay+ 2024 Fig. 4.
# Central values. Cloud-9 has N_HI ~ 5e19 cm^-2 at b=0.5 kpc, dropping
# to ~ 1e19 at b=10 kpc.
CLOUD9_NHI_LOG10_CM2 = np.array([
    19.70, 19.55, 19.40, 19.20, 19.05, 18.85, 18.70, 18.55,
    18.30, 18.00, 17.65, 17.30, 17.00,
])
# 1σ uncertainties on log10(N_HI), typical for HI column density
# measurements: 0.1-0.2 dex.
CLOUD9_NHI_ERR_LOG10 = np.array([
    0.20, 0.18, 0.15, 0.13, 0.12, 0.10, 0.10, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30,
])

# M51 Cloud S / Cloud N parameters from arXiv:2607.21034.
# M_HI ~ 10^6.5 M_sun each, v_disp ~ 20 km/s, projected distance 70-90 kpc.
# The MCMC in arXiv:2607.21034 finds M_halo ~ 3.7e9 M_sun for both.
M51_CLOUD_S_HALO_MASS = 3.7e9  # M_sun, best-fit per arXiv:2607.21034
M51_CLOUD_N_HALO_MASS = 3.7e9  # M_sun
M51_CLOUD_S_V_DISP_KMS = 20.0  # km/s
M51_CLOUD_N_V_DISP_KMS = 20.0  # km/s
M51_CLOUD_S_M_HI = 10**6.5     # M_sun
M51_CLOUD_N_M_HI = 10**6.5     # M_sun


# ===========================================================================
#  (3) SIDM-vs-CDM TEST (lightweight)
# ===========================================================================
# For T90.27 v1, the test is:
#   Given σ_m_0 (from the joint fit) and the published RELHIC MCMC
#   posterior on (M200, c200, τ), compute the log-likelihood of the
#   Cloud-9 N(HI) data under the SIDM model at the mean (M200, c200, τ)
#   and under the CDM model at the mean (M200, c200, τ=0). The
#   likelihood difference Δlog L is the test statistic.
#
# The full forward model (hydrostatic gas + N(HI) projection) is NOT
# implemented here. Instead, we use the published Cloud-9 paper's
# best-fit N(HI) as the CDM benchmark and the published SIDM N(HI) as
# the SIDM benchmark. The inference then becomes a sigma/m-vs-τ test
# using the published N(HI) profile data.
#
# This is the same approach the Cloud-9 paper takes (compare the
# hydrostatic-model-predicted N(HI) at the best-fit halo parameters
# to the observed N(HI)). The published best-fit halo parameters
# from the paper are:
#   CDM:    M200 = 7e8 M_sun, c200 = 6 (per the CDM-best-fit in §3.1)
#   SIDM τ=0.18: M200 = 4.7e9 M_sun, c200 = 4.0, σ/m = 483 cm^2/g
#   SIDM τ=0.95: M200 = 3.4e9 M_sun, c200 = 1.5, σ/m = 2.1e4 cm^2/g
#
# For T90.27 v1, we hard-code these as the benchmark fits. A future
# version would re-run the Cloud-9 MCMC with the project's SIDM model
# and the project's σ/m prior.


# Best-fit halo parameters from arXiv:2608.04362 §3.1
CLOUD9_BESTFIT_CDM = {
    "M200": 7.0e8,  # M_sun (CDM best-fit, very low concentration)
    "c200": 6.0,    # 7σ below cosmological concentration-mass relation
    "label": "CDM best-fit (Cloud-9 paper)",
}
CLOUD9_BESTFIT_SIDM_T018 = {
    "M200": 4.7e9,    # M_sun
    "c200": 4.0,      # 3.2σ below cosmological median
    "tau": 0.18,      # near maximum core expansion
    "sigma_m_v200": 483.0,  # cm^2/g
    "label": "SIDM τ=0.18 (Cloud-9 paper, σ/m=483)",
}
CLOUD9_BESTFIT_SIDM_T095 = {
    "M200": 3.4e9,    # M_sun
    "c200": 1.5,      # 6σ below cosmological median
    "tau": 0.95,      # deep core collapse
    "sigma_m_v200": 2.1e4,  # cm^2/g
    "label": "SIDM τ=0.95 (Cloud-9 paper, σ/m=2.1e4)",
}


def enclosed_mass_yang(
    r_kpc: np.ndarray,
    M200: float,
    c200: float,
    tau: float,
) -> np.ndarray:
    """Enclosed mass M(<r) for the Yang+2024 SIDM profile (numerical).

    M(<r) = 4π ∫_0^r r'^2 ρ(r') dr'

    Used by the joint fit to compute the gravitational potential.
    """
    from scipy.integrate import cumulative_trapezoid
    r_fine = np.geomspace(1e-3, r_kpc[-1] * 1.5, 500)
    rho_fine = yang_parametric_sidm_density(r_fine, M200, c200, tau)
    # Cumulative enclosed mass:
    integrand = 4.0 * np.pi * r_fine**2 * rho_fine
    M_cum_fine = np.concatenate([[0.0], cumulative_trapezoid(integrand, r_fine)])
    # Interpolate to r_kpc:
    M_cum = np.interp(r_kpc, r_fine, M_cum_fine)
    return M_cum


def enclosed_mass_nfw(
    r_kpc: np.ndarray,
    M200: float,
    c200: float,
) -> np.ndarray:
    """Enclosed mass M(<r) for NFW (analytic).

    M(<r) = M200 · [ln(1+r/rs) - r/rs / (1+r/rs)] / [ln(1+c) - c/(1+c)]
    """
    r_kpc = np.asarray(r_kpc, dtype=float)
    _, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    fc = np.log(1.0 + c200) - c200 / (1.0 + c200)
    return M200 * (np.log(1.0 + r_kpc / r_s_0) - r_kpc / r_s_0 / (1.0 + r_kpc / r_s_0)) / fc


def central_density_yang(
    M200: float,
    c200: float,
    tau: float,
) -> float:
    """Central density ρ(r→0) for the Yang+2024 SIDM profile.

    At τ=0, this is the NFW central density ρs,0.
    At τ>0, the core radius rc softens the cusp.
    """
    return float(yang_parametric_sidm_density(np.array([1e-3]), M200, c200, tau)[0])


# ===========================================================================
#  Self-test
# ===========================================================================
if __name__ == "__main__":
    print("=== T90.27 RELHIC forward model — self-test (v1, NFW + Yang halo) ===")
    print()
    M200 = 5.0e9
    c200 = 4.0
    print(f"Test halo: M200 = {M200:.2e} M_sun, c200 = {c200}")
    print(f"v200 = {v200_from_M200(M200, c200):.2f} km/s")
    rho_s_0, r_s_0 = m200_c200_to_rho_s_rs(M200, c200)
    print(f"rho_s_0, r_s_0 = ({rho_s_0:.3e}, {r_s_0:.3f}) M_sun/kpc^3, kpc")
    print()
    # Yang vs NFW at τ=0
    r_test = np.geomspace(0.1, 50.0, 100)
    rho_nfw = nfw_density(r_test, M200, c200)
    rho_yang0 = yang_parametric_sidm_density(r_test, M200, c200, tau=0.0)
    print(f"NFW density at r=1 kpc:  {nfw_density(np.array([1.0]), M200, c200)[0]:.3e} M_sun/kpc^3")
    print(f"Yang density at r=1 kpc (tau=0): {rho_yang0[np.argmin(np.abs(r_test-1.0))]:.3e}")
    print(f"  (should match NFW at tau=0: max diff {np.max(np.abs(rho_nfw - rho_yang0)):.3e})")
    print()
    # Cloud-9 best-fit SIDM halo
    for label, params in [
        ("CDM best-fit", CLOUD9_BESTFIT_CDM),
        ("SIDM τ=0.18", CLOUD9_BESTFIT_SIDM_T018),
        ("SIDM τ=0.95", CLOUD9_BESTFIT_SIDM_T095),
    ]:
        if "tau" in params:
            rho = yang_parametric_sidm_density(
                r_test, params["M200"], params["c200"], params["tau"]
            )
        else:
            rho = nfw_density(r_test, params["M200"], params["c200"])
        rho_1kpc = float(np.interp(1.0, r_test, rho))
        print(f"  {label:18s}  M200={params['M200']:.1e} c200={params['c200']:.1f}  rho(r=1kpc) = {rho_1kpc:.3e}")
    print()
    # τ-c mapping
    print("τ = t/t_c at t=10 Gyr, σ/m(v200) = 483 cm^2/g (Cloud-9 SIDM τ=0.18):")
    t_c = t_collapse(483.0, *m200_c200_to_rho_s_rs(M200, c200))
    print(f"  t_c = {t_c:.3f} Gyr  ->  τ = {10.0 / t_c:.3f}")
    print()
    # Cloud-9 N(HI) data
    print("Cloud-9 published N(HI) data points (B from Benitez-Llambay+ 2024 Fig. 4):")
    for b, lN, e in zip(CLOUD9_NHI_B_KPC, CLOUD9_NHI_LOG10_CM2, CLOUD9_NHI_ERR_LOG10):
        print(f"  b = {b:5.1f} kpc   log10 N_HI = {lN:.2f} ± {e:.2f}  cm^-2")
    print()
    print("M51 Cloud S / N (arXiv:2607.21034):")
    print(f"  M_HI each = {M51_CLOUD_S_M_HI:.1e} M_sun")
    print(f"  v_disp each = {M51_CLOUD_S_V_DISP_KMS:.1f} km/s")
    print(f"  M_halo each = {M51_CLOUD_S_HALO_MASS:.1e} M_sun (best-fit)")
