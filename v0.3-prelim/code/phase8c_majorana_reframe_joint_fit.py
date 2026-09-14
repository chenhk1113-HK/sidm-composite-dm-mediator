"""
Phase 8c — Majorana Dark Photon Reframe Joint Fit (Pathway 7B)

Builds on T39 Tier-3 marginalization (T39_tier3_epsilon_alpha_joint_fit.py)
but with the three structural changes from the Majorana reframe:

1. LZ elastic: σ_SI^Majorana = σ_SI^Dirac × (g_D ε)²
   (Majorana vector current vanishes at tree level — chirality flip
   requires two insertions of kinetic mixing)
2. g_D (dark coupling) opened as FITTED parameter (was fixed at α_D=0.01)
3. f_H (excited-state halo fraction) opened as NEW parameter

Parameter vector (6D):
  theta = (log_sigma_m_0, a, log_epsilon, log_alpha, log_g_D, log_f_H)

Priors:
  log_sigma_m_0 ∈ [-3.0, 2.5]      (cm²/g, v_ref=100)
  a           ∈ [-2.0, 2.0]        (velocity index)
  log_epsilon ∈ [-12, -3]          (REFRAME: was [-60, -1] in T39)
  log_alpha   ∈ [-12, -1]          (annihilation coupling)
  log_g_D     ∈ [-2.0, 0.5]        (g_D ∈ [0.01, 3.16])
  log_f_H     ∈ [-3.0, 0.0]        (f_H ∈ [0.001, 1])

Wall-time target: <2 min (nlive=200, 6D).

Verdict (predicted from Phase 8b analytic):
  - LZ elastic relaxes: ε can now reach 10^-6 (was forced to 10^-50)
  - g_D posterior should concentrate at SIDM-required ~0.5-1.0
  - f_H posterior should concentrate at ~0.1-1 (depending on χ mass)
  - LZ inelastic event-rate channel OPENS for the first time at v0.3-prelim
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import dynesty
import config
import channels_v03 as ch_v03
from sidm_velocity_dependent import sigma_m_effective
from t30_lz_real_posterior import loglike_lz_real, LZ_REAL
from t32_real_likelihood import loglike_fermi_real
from t39_tier3_epsilon_alpha_joint_fit import sigma_v_from_dark_photon
from t87_composite_inelastic_nucleon import sigma_inel_nuc
from phase8b_majorana_reframe import sigma_SI_dirac, DE_LIMA

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Constants (from T39)
HBAR_C_GEV_CM = 1.97e-14
ALPHA_EM = 1.0 / 137.0
M_NUCLEON_GEV = 0.938

# LZ 248 keV event observables
LZ_248_KEV_ENERGY = 248.0   # keV recoil energy
# LZ observed 1 event in WS2024 (2024) + post-run searches (2025-2026).
# Poisson: P(N=1|λ) peaks at λ=1. The likelihood is fairly broad:
# P(N=1|λ=0.5) ≈ 0.30, P(N=1|λ=2) ≈ 0.27, P(N=1|λ=5) ≈ 0.033.
# Gaussian σ of 1.5 events underweights λ=2 vs λ=1 by exp(-0.5) vs exp(0).
# Use σ=2.5 to be more permissive (consistent with 0-4 events).
LZ_248_KEV_RATE_TARGET = 1.0  # 1 event observed
LZ_248_KEV_RATE_SIGMA = 2.5   # events (Gaussian approx to Poisson for 0-4 events)
# LZ exposure for the 248 keV bin analysis (JHEP 2024 + later updates)
# Reference: LZ WS2024 5.5 tonne-year exposure (arXiv:2410.17036, 2024)
LZ_EXPOSURE_TONNE_YEAR = 5.5  # tonne-year for SI analysis
# Effective 248 keV bin exposure (after analysis cuts): ~4 tonne-year
LZ_248_KEV_EXPOSURE_TONNE_YEAR = 4.0
# Approximate rate coefficient: events/tonne-year per cm² of cross-section
# From LZ projection: 1 event at sigma_inel ~ 1e-46 cm² in 4 tonne-year exposure
# (validated against de Lima's 7e-47 cm² → ~1 event)
LZ_EVENT_RATE_COEFF = 1.0 / 1e-46 / LZ_248_KEV_EXPOSURE_TONNE_YEAR  # events/tonne-year/cm²

# Reframe priors (6D)
LOG_EPSILON_RANGE = (-12.0, -3.0)   # REFRAME: was (-60, -1) in T39
LOG_ALPHA_RANGE = (-12.0, -1.0)
LOG_G_D_RANGE = (-2.0, 0.5)         # g_D ∈ [0.01, 3.16]
LOG_F_H_RANGE = (-3.0, 0.0)         # f_H ∈ [0.001, 1.0]

# Fixed model parameters (Benchmark A from T39, kept for v0.3-compat)
M_CHI_GEV_FIXED = 45.0
M_A_PRIME_MEV_FIXED = 200.0
DELTA_KEV_FIXED = 297.0   # Di Mauro best-fit mass splitting


def sigma_SI_majorana_cm2(epsilon: float, g_D: float,
                          m_chi_GeV: float = M_CHI_GEV_FIXED,
                          m_A_prime_MeV: float = M_A_PRIME_MEV_FIXED) -> float:
    """
    Majorana DM spin-independent cross-section via dark photon (second-order).

    σ_SI^Majorana = σ_SI^Dirac × (g_D ε)²

    Where σ_SI^Dirac is the standard dark-photon-portal formula
    (Kaplinghat-Tulin-Yu 2014, Berlin+ 2018). The (g_D ε)² factor is the
    chirality-flip suppression: Majorana vector current J^μ = -J^μ
    vanishes, so the leading contribution is a two-A'-exchange loop.
    """
    alpha_D = g_D**2 / (4 * np.pi)
    sigma_dirac = sigma_SI_dirac(m_chi_GeV, m_A_prime_MeV, g_D, epsilon)
    # Recompute with the proper alpha_D for clarity (sigma_SI_dirac uses g_D^2)
    sigma_dirac_proper = (
        16.0 * np.pi * alpha_D * ALPHA_EM * epsilon**2
        * ((m_chi_GeV * M_NUCLEON_GEV) / (m_chi_GeV + M_NUCLEON_GEV))**2
        / (m_A_prime_MeV * 1e-3)**4
        * (HBAR_C_GEV_CM**2)
    )
    # The (g_D ε)² chirality flip factor
    suppression = (g_D * epsilon)**2
    return sigma_dirac_proper * suppression


def sigma_inel_majorana_cm2(epsilon: float, g_D: float, f_H: float,
                             m_chi_GeV: float = M_CHI_GEV_FIXED,
                             m_A_prime_MeV: float = M_A_PRIME_MEV_FIXED,
                             delta_keV: float = DELTA_KEV_FIXED) -> float:
    """
    Majorana DM inelastic cross-section via dark photon at LZ 248 keV.

    For the Majorana reframe, the inelastic channel is FIRST-ORDER in ε
    (chirality flip absorbed by the χ_H → χ_L mass splitting). The
    cross-section at the recoil energy E_R uses the dark-photon-portal
    formula (Kaplinghat-Tulin-Yu 2014), modified for the inelastic channel:

    σ_inel(E_R) = (ε² α_D μ_chiN² / π) × (1/(m_A'² + q²)²)
                  × |M_off|² × f_H

    where |M_off|² is the off-diagonal nuclear matrix element squared.
    The exact value is model-dependent (depends on χ_H-χ_L mixing angle,
    nuclear shell-model details). We CALIBRATE |M_off|² so that de Lima's
    benchmark (ε=1.3e-6, α_D=4.1e-5, f_H=0.5) reproduces σ_inel = 7e-47 cm²
    (their event-rate-matched value).

    This is an honest normalization: we acknowledge that the absolute
    σ_inel depends on nuclear physics we don't fully control, and use
    de Lima's published event rate as the calibration anchor.

    Returns σ_inel in cm².
    """
    alpha_D = g_D**2 / (4 * np.pi)
    mu_chiN = (m_chi_GeV * M_NUCLEON_GEV) / (m_chi_GeV + M_NUCLEON_GEV)
    m_A_prime_GeV = m_A_prime_MeV * 1.0e-3
    # Momentum transfer at E_R = 248 keV (from T87): q ≈ 21.6 MeV
    q_MeV = np.sqrt(2 * M_NUCLEON_GEV * 1e3 * 0.248)  # MeV
    q_GeV = q_MeV * 1e-3
    # Bare formula (without |M_off|²)
    sigma_bare_cm2 = (
        epsilon**2 * alpha_D * mu_chiN**2
        / (np.pi * (m_A_prime_GeV**2 + q_GeV**2)**2)
        * (HBAR_C_GEV_CM**2)
    )
    # Calibrate |M_off|² to de Lima's benchmark
    sigma_bare_deLima = (
        (1.3e-6)**2 * (4.1e-5) * ((45.0 * 0.938) / (45.0 + 0.938))**2
        / (np.pi * (0.2**2 + q_GeV**2)**2)
        * (HBAR_C_GEV_CM**2)
    )
    M_off_sq_calibrated = 7e-47 / sigma_bare_deLima  # makes benchmark match
    # Apply
    sigma_cm2 = sigma_bare_cm2 * M_off_sq_calibrated
    # Halo fraction (linear in f_H for χ_H component)
    return sigma_cm2 * f_H


def lz_248keV_event_rate(epsilon: float, g_D: float, f_H: float,
                         m_chi_GeV: float = M_CHI_GEV_FIXED,
                         m_A_prime_MeV: float = M_A_PRIME_MEV_FIXED,
                         delta_keV: float = DELTA_KEV_FIXED) -> float:
    """
    Expected number of LZ 248 keV events from Majorana inelastic DM.

    Uses the dark-photon-portal Majorana formula directly (not T87's
    composite empirical one). Calibrated so that de Lima's benchmark
    (ε=1.3e-6, α_D=4.1e-5, f_H=0.5) gives ~1 event in LZ WS2024.

    Args:
        epsilon: kinetic mixing
        g_D: dark gauge coupling
        f_H: excited-state halo fraction
        exposure_tonne_year: LZ effective exposure for 248 keV bin

    Returns:
        Expected number of 248 keV events
    """
    sigma_inel = sigma_inel_majorana_cm2(
        epsilon=epsilon, g_D=g_D, f_H=f_H,
        m_chi_GeV=m_chi_GeV, m_A_prime_MeV=m_A_prime_MeV,
        delta_keV=delta_keV,
    )
    # Event rate: σ × coefficient × exposure
    rate = sigma_inel * LZ_EVENT_RATE_COEFF * LZ_248_KEV_EXPOSURE_TONNE_YEAR
    return max(rate, 0.0)


def loglike_lz_248keV(epsilon: float, g_D: float, f_H: float) -> float:
    """
    Poisson log-likelihood for the LZ 248 keV event.

    N_observed = 1 (one event in WS2024)
    N_predicted = lz_248keV_event_rate(epsilon, g_D, f_H)

    Uses Gaussian approximation to Poisson for numerical stability:
      log L = -0.5 × ((N_pred - N_obs) / σ)²
    where σ = 1.5 events (allows 0-3 events to be within 1σ)
    """
    n_pred = lz_248keV_event_rate(epsilon, g_D, f_H)
    delta = (n_pred - LZ_248_KEV_RATE_TARGET) / LZ_248_KEV_RATE_SIGMA
    return -0.5 * delta**2


def loglike_joint_majorana(theta, lz_248_enabled: bool = True):
    """
    6D joint likelihood under the Majorana reframe.

    theta = (log_sigma_m_0, a, log_epsilon, log_alpha, log_g_D, log_f_H)

    Channels:
      - LZ elastic: σ_SI^Majorana (second-order, factor (g_D ε)²)
      - LZ 248 keV: Poisson event-rate likelihood (can be disabled for
                    baseline comparison vs T39)
      - Fermi dwarf: <σv> via dark photon (uses α as multiplier, T39 convention)
      - SIDM: σ/m(v) at dSph/UFD/Bullet velocities
      - SPARC: sigma_m_0, a (unchanged)
    """
    log_sigma_m_0, a, log_epsilon, log_alpha, log_g_D, log_f_H = theta
    sigma_m_0 = 10 ** log_sigma_m_0
    epsilon = 10 ** log_epsilon
    alpha = 10 ** log_alpha
    g_D = 10 ** log_g_D
    f_H = 10 ** log_f_H

    if sigma_m_0 <= 0 or epsilon <= 0 or alpha <= 0 or g_D <= 0 or f_H <= 0:
        return -np.inf
    if not (config.LOG_SIGMA_M_RANGE[0] <= log_sigma_m_0 <= config.LOG_SIGMA_M_RANGE[1]):
        return -np.inf
    if not (config.A_RANGE[0] <= a <= config.A_RANGE[1]):
        return -np.inf
    if not (LOG_EPSILON_RANGE[0] <= log_epsilon <= LOG_EPSILON_RANGE[1]):
        return -np.inf
    if not (LOG_ALPHA_RANGE[0] <= log_alpha <= LOG_ALPHA_RANGE[1]):
        return -np.inf
    if not (LOG_G_D_RANGE[0] <= log_g_D <= LOG_G_D_RANGE[1]):
        return -np.inf
    if not (LOG_F_H_RANGE[0] <= log_f_H <= LOG_F_H_RANGE[1]):
        return -np.inf

    alpha_D = g_D**2 / (4 * np.pi)

    # 1. LZ elastic (Majorana second-order)
    sigma_SI_M = sigma_SI_majorana_cm2(epsilon, g_D)
    ll_lz_elastic = loglike_lz_real(M_CHI_GEV_FIXED, sigma_SI_M)

    # 2. LZ 248 keV (Majorana inelastic, event-rate) — can be disabled
    ll_lz_248 = loglike_lz_248keV(epsilon, g_D, f_H) if lz_248_enabled else 0.0

    # 3. Fermi dwarf (sigma_v via dark photon; uses alpha = alpha_D multiplier)
    # T39 convention: sigma_v = alpha * sigma_v_from_dark_photon(alpha_D=0.01)
    # At alpha=1e-28 (T39 MAP), sigma_v ~ 1e-52 cm³/s → below Fermi limit (likelihood ~0)
    sigma_v_benchmark = sigma_v_from_dark_photon(
        m_chi_GeV=M_CHI_GEV_FIXED,
        m_A_prime_MeV=M_A_PRIME_MEV_FIXED,
        alpha_D=0.01,
    )
    sigma_v = alpha * sigma_v_benchmark
    ll_fermi = loglike_fermi_real(M_CHI_GEV_FIXED, sigma_v, channel="bb", use_J_prior=True)

    # 4. dSph + UFD + Bullet (sigma/m)
    ll_dsph = ch_v03.loglike_dsph_v03(sigma_m_0, a)
    ll_ufd = ch_v03.loglike_ufd_v03(sigma_m_0, a)
    ll_bullet = ch_v03.loglike_bullet_v03(sigma_m_0, a)

    # 5. SPARC (optional)
    try:
        import t8_v03_joint_fit as t8
        ll_sparc = t8.delta_log_sparc(sigma_m_0, a) / 1000
    except Exception:
        ll_sparc = 0.0

    return ll_lz_elastic + ll_lz_248 + ll_fermi + ll_dsph + ll_ufd + ll_bullet + ll_sparc


def prior_transform_6(u):
    """Prior transform for the 6D Majorana reframe fit."""
    return [
        config.LOG_SIGMA_M_RANGE[0] + u[0] * (config.LOG_SIGMA_M_RANGE[1] - config.LOG_SIGMA_M_RANGE[0]),
        config.A_RANGE[0] + u[1] * (config.A_RANGE[1] - config.A_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[2] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_ALPHA_RANGE[0] + u[3] * (LOG_ALPHA_RANGE[1] - LOG_ALPHA_RANGE[0]),
        LOG_G_D_RANGE[0] + u[4] * (LOG_G_D_RANGE[1] - LOG_G_D_RANGE[0]),
        LOG_F_H_RANGE[0] + u[5] * (LOG_F_H_RANGE[1] - LOG_F_H_RANGE[0]),
    ]


def weighted_quantiles(values, weights, q):
    """Weighted quantiles via inverse CDF."""
    idx = np.argsort(values)
    values = values[idx]
    weights = weights[idx]
    cumw = np.cumsum(weights)
    cumw = cumw / cumw[-1]
    return np.interp(q, cumw, values)


def weighted_median(values, weights):
    return float(weighted_quantiles(values, weights, 0.5))


def main():
    print("=" * 80)
    print("Phase 8c — Majorana Dark Photon Reframe Joint Fit (Pathway 7B)")
    print("=" * 80)
    print(f"Parameters: log_sigma_m_0, a, log_epsilon, log_alpha, log_g_D, log_f_H")
    print(f"epsilon range: 10^{LOG_EPSILON_RANGE[0]:.0f} to 10^{LOG_EPSILON_RANGE[1]:.0f} (REFRAME)")
    print(f"g_D range:     10^{LOG_G_D_RANGE[0]:.1f} to 10^{LOG_G_D_RANGE[1]:.1f}")
    print(f"f_H range:     10^{LOG_F_H_RANGE[0]:.1f} to 10^{LOG_F_H_RANGE[1]:.1f}")
    print()

    # ===== RUN 1: LZ 248 keV ENABLED (full Phase 8c) =====
    print("--- RUN 1: LZ 248 keV ENABLED (full reframe) ---")
    t0 = time.time()

    def loglike_full(theta):
        return loglike_joint_majorana(theta, lz_248_enabled=True)

    sampler_full = dynesty.NestedSampler(
        loglikelihood=loglike_full,
        prior_transform=prior_transform_6,
        ndim=6, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler_full.run_nested(dlogz=0.1, print_progress=False)
    wall_full = time.time() - t0

    res_full = sampler_full.results
    log_Z_full = float(res_full.logz[-1])
    log_Z_err_full = float(res_full.logzerr[-1])
    samples_full = res_full.samples
    weights_full = np.exp(res_full.logwt - res_full.logz[-1])
    imap_full = int(np.argmax(weights_full))
    MAP_full = samples_full[imap_full].tolist()

    # ===== RUN 2: LZ 248 keV DISABLED (baseline for T39 comparison) =====
    print("--- RUN 2: LZ 248 keV DISABLED (baseline) ---")
    t0 = time.time()

    def loglike_baseline(theta):
        return loglike_joint_majorana(theta, lz_248_enabled=False)

    sampler_base = dynesty.NestedSampler(
        loglikelihood=loglike_baseline,
        prior_transform=prior_transform_6,
        ndim=6, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler_base.run_nested(dlogz=0.1, print_progress=False)
    wall_base = time.time() - t0

    res_base = sampler_base.results
    log_Z_base = float(res_base.logz[-1])
    log_Z_err_base = float(res_base.logzerr[-1])
    samples_base = res_base.samples
    weights_base = np.exp(res_base.logwt - res_base.logz[-1])
    imap_base = int(np.argmax(weights_base))
    MAP_base = samples_base[imap_base].tolist()

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"  Baseline (no 248 keV): log_Z = {log_Z_base:.3f} ± {log_Z_err_base:.3f}, wall = {wall_base:.1f}s")
    print(f"    MAP: log_sigma_m = {MAP_base[0]:.3f}, a = {MAP_base[1]:.3f}, "
          f"log_eps = {MAP_base[2]:.3f}, log_alpha = {MAP_base[3]:.3f}")
    print(f"         log_g_D = {MAP_base[4]:.3f}, log_f_H = {MAP_base[5]:.3f}")
    print()
    print(f"  Full (with 248 keV):    log_Z = {log_Z_full:.3f} ± {log_Z_err_full:.3f}, wall = {wall_full:.1f}s")
    print(f"    MAP: log_sigma_m = {MAP_full[0]:.3f}, a = {MAP_full[1]:.3f}, "
          f"log_eps = {MAP_full[2]:.3f}, log_alpha = {MAP_full[3]:.3f}")
    print(f"         log_g_D = {MAP_full[4]:.3f}, log_f_H = {MAP_full[5]:.3f}")

    delta_log_Z = log_Z_full - log_Z_base
    print()
    print(f"  Δlog Z (full - baseline): {delta_log_Z:+.3f}")
    print(f"    Positive = 248 keV channel HELPS")
    print(f"    Negative = 248 keV channel HURTS (occam factor or prior mismatch)")

    # Posterior summaries for the full fit
    log_sigma_m_0_samples = samples_full[:, 0]
    a_samples = samples_full[:, 1]
    log_eps_samples = samples_full[:, 2]
    log_alpha_samples = samples_full[:, 3]
    log_gD_samples = samples_full[:, 4]
    log_fH_samples = samples_full[:, 5]

    sm_q = [10**q for q in weighted_quantiles(log_sigma_m_0_samples, weights_full, [0.16, 0.5, 0.84])]
    eps_q = [10**q for q in weighted_quantiles(log_eps_samples, weights_full, [0.16, 0.5, 0.84])]
    gD_q = [10**q for q in weighted_quantiles(log_gD_samples, weights_full, [0.16, 0.5, 0.84])]
    fH_q = [10**q for q in weighted_quantiles(log_fH_samples, weights_full, [0.16, 0.5, 0.84])]

    print()
    print(f"  Full fit posteriors (16/50/84%):")
    print(f"    σ/m (cm²/g): {sm_q[0]:.3f} / {sm_q[1]:.3f} / {sm_q[2]:.3f}")
    print(f"    ε:           {eps_q[0]:.2e} / {eps_q[1]:.2e} / {eps_q[2]:.2e}")
    print(f"    g_D:         {gD_q[0]:.3f} / {gD_q[1]:.3f} / {gD_q[2]:.3f}")
    print(f"    f_H:         {fH_q[0]:.3f} / {fH_q[1]:.3f} / {fH_q[2]:.3f}")

    # Verdict
    eps_opened = MAP_full[2] > LOG_EPSILON_RANGE[0] + 1
    gD_sidm = 0.3 < 10**MAP_full[4] < 2.0
    fH_opened = 0.01 < 10**MAP_full[5] < 1.0

    if delta_log_Z > 0.5:
        verdict = "PROCEED: 248 keV channel IMPROVES the reframe fit"
    elif delta_log_Z > -0.5:
        verdict = "MIXED: 248 keV channel is consistent (no penalty)"
    else:
        verdict = f"REGRESSION: 248 keV channel HURTS by Δlog Z = {delta_log_Z:.1f}"

    print()
    print(f"  ε MAP opened: {eps_opened} (MAP = 10^{MAP_full[2]:.1f})")
    print(f"  g_D in SIDM range: {gD_sidm} (MAP = {10**MAP_full[4]:.3f})")
    print(f"  f_H opened: {fH_opened} (MAP = {10**MAP_full[5]:.3f})")
    print()
    print(f"VERDICT: {verdict}")

    out = {
        "test": "Phase8c_majorana_reframe_joint_fit",
        "direction": "Pathway 7B: Majorana + dark photon, 6D with LZ 248 keV toggle",
        "ndim": 6,
        "parameters": ["log_sigma_m_0", "a", "log_epsilon", "log_alpha",
                       "log_g_D", "log_f_H"],
        "priors": {
            "log_sigma_m_0": list(config.LOG_SIGMA_M_RANGE),
            "a": list(config.A_RANGE),
            "log_epsilon": list(LOG_EPSILON_RANGE),
            "log_alpha": list(LOG_ALPHA_RANGE),
            "log_g_D": list(LOG_G_D_RANGE),
            "log_f_H": list(LOG_F_H_RANGE),
        },
        "log_Z_baseline_no_248kev": log_Z_base,
        "log_Z_baseline_err": log_Z_err_base,
        "log_Z_full_with_248kev": log_Z_full,
        "log_Z_full_err": log_Z_err_full,
        "delta_log_Z_248keV_contribution": delta_log_Z,
        "MAP_full": {
            "log_sigma_m_0": MAP_full[0],
            "a": MAP_full[1],
            "log_epsilon": MAP_full[2],
            "log_alpha": MAP_full[3],
            "log_g_D": MAP_full[4],
            "log_f_H": MAP_full[5],
            "sigma_m_cm2_per_g": 10**MAP_full[0],
            "epsilon": 10**MAP_full[2],
            "alpha": 10**MAP_full[3],
            "g_D": 10**MAP_full[4],
            "f_H": 10**MAP_full[5],
        },
        "MAP_baseline": {
            "log_sigma_m_0": MAP_base[0],
            "a": MAP_base[1],
            "log_epsilon": MAP_base[2],
            "log_alpha": MAP_base[3],
            "log_g_D": MAP_base[4],
            "log_f_H": MAP_base[5],
        },
        "posteriors_full_16_50_84": {
            "sigma_m_cm2_per_g": sm_q,
            "epsilon": eps_q,
            "g_D": gD_q,
            "f_H": fH_q,
        },
        "verdict": verdict,
        "checks": {
            "epsilon_MAP_opened": bool(eps_opened),
            "g_D_in_SIDM_range": bool(gD_sidm),
            "f_H_MAP_opened": bool(fH_opened),
        },
        "wall_seconds": wall_full + wall_base,
        "wall_seconds_full": wall_full,
        "wall_seconds_baseline": wall_base,
        "n_samples": int(len(samples_full)),
        "T39_baseline_log_Z_reference": -2.9412912122660257,
    }

    out_path = RESULTS_DIR / "phase8c_majorana_reframe_joint_fit.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
