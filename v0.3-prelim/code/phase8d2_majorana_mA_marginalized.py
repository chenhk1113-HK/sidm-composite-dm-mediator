"""
Phase 8d.2 — Majorana Reframe with m_A' marginalization (6D).

Builds on Phase 8d.1 (α = g_D²/(4π) consistency) by adding m_A' as a
fitted parameter. Previous phases fixed m_A' = 200 MeV (de Lima value).

m_A' range: [10, 1000] MeV — safely below m_χ = 45 GeV (so 2 m_A' < m_χ
for annihilation to be kinematically allowed).

Parameter vector (6D):
  theta = (log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H, log_m_A_prime_MeV)

Priors:
  log_sigma_m_0      ∈ [-3.0, 2.5]
  a                  ∈ [-2.0, 2.0]
  log_epsilon        ∈ [-12, -3]
  log_g_D            ∈ [-2.0, 0.5]
  log_f_H            ∈ [-3.0, 0.0]
  log_m_A_prime_MeV  ∈ [1.0, 3.0]   (m_A' ∈ [10, 1000] MeV)

Wall target: ~30s (nlive=200, 6D)
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
from t30_lz_real_posterior import loglike_lz_real
from t32_real_likelihood import loglike_fermi_real
from t39_tier3_epsilon_alpha_joint_fit import sigma_v_from_dark_photon
from phase8c_majorana_reframe_joint_fit import (
    sigma_SI_majorana_cm2, sigma_inel_majorana_cm2,
    lz_248keV_event_rate, loglike_lz_248keV,
    M_CHI_GEV_FIXED, DELTA_KEV_FIXED,
)
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Priors (6D)
LOG_EPSILON_RANGE = (-12.0, -3.0)
LOG_G_D_RANGE = (-2.0, 0.5)
LOG_F_H_RANGE = (-3.0, 0.0)
LOG_M_A_PRIME_MEV_RANGE = (1.0, 3.0)   # m_A' ∈ [10, 1000] MeV


def sigma_SI_with_mA(epsilon, g_D, m_A_prime_MeV):
    """Majorana SI σ with explicit m_A' (no fixed benchmark)."""
    from phase8c_majorana_reframe_joint_fit import sigma_SI_majorana_cm2
    return sigma_SI_majorana_cm2(epsilon=epsilon, g_D=g_D,
                                  m_A_prime_MeV=m_A_prime_MeV)


def sigma_inel_with_mA(epsilon, g_D, f_H, m_A_prime_MeV, m_chi_GeV=M_CHI_GEV_FIXED):
    """Majorana inelastic σ with explicit m_A'.

    The sigma_inel_majorana_cm2 function in phase8c uses a de Lima
    calibration that fixes m_A'=200 MeV. For the m_A'-marginalized case,
    we recompute the bare cross-section with the actual m_A' and apply
    the same calibration factor.
    """
    # Bare formula at the actual m_A'
    alpha_D = g_D**2 / (4 * np.pi)
    mu_chiN = (m_chi_GeV * 0.938) / (m_chi_GeV + 0.938)
    m_A_prime_GeV = m_A_prime_MeV * 1.0e-3
    q_MeV = np.sqrt(2 * 0.938 * 1e3 * 0.248)
    q_GeV = q_MeV * 1e-3
    sigma_bare_cm2 = (
        epsilon**2 * alpha_D * mu_chiN**2
        / (np.pi * (m_A_prime_GeV**2 + q_GeV**2)**2)
        * (1.97e-14)**2
    )
    # Calibration factor (from phase8c, evaluated at de Lima benchmark)
    sigma_bare_deLima = (
        (1.3e-6)**2 * 4.1e-5 * ((45.0 * 0.938) / (45.0 + 0.938))**2
        / (np.pi * (0.2**2 + q_GeV**2)**2)
        * (1.97e-14)**2
    )
    M_off_sq_calibrated = 7e-47 / sigma_bare_deLima
    return sigma_bare_cm2 * M_off_sq_calibrated * f_H


def loglike_joint_6d(theta, lz_248_enabled: bool = True):
    """6D joint fit with m_A' marginalized."""
    log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H, log_m_A = theta
    sigma_m_0 = 10 ** log_sigma_m_0
    epsilon = 10 ** log_epsilon
    g_D = 10 ** log_g_D
    f_H = 10 ** log_f_H
    m_A_prime_MeV = 10 ** log_m_A

    if sigma_m_0 <= 0 or epsilon <= 0 or g_D <= 0 or f_H <= 0:
        return -np.inf
    if not (config.LOG_SIGMA_M_RANGE[0] <= log_sigma_m_0 <= config.LOG_SIGMA_M_RANGE[1]):
        return -np.inf
    if not (config.A_RANGE[0] <= a <= config.A_RANGE[1]):
        return -np.inf
    if not (LOG_EPSILON_RANGE[0] <= log_epsilon <= LOG_EPSILON_RANGE[1]):
        return -np.inf
    if not (LOG_G_D_RANGE[0] <= log_g_D <= LOG_G_D_RANGE[1]):
        return -np.inf
    if not (LOG_F_H_RANGE[0] <= log_f_H <= LOG_F_H_RANGE[1]):
        return -np.inf
    if not (LOG_M_A_PRIME_MEV_RANGE[0] <= log_m_A <= LOG_M_A_PRIME_MEV_RANGE[1]):
        return -np.inf

    # 1. LZ elastic
    sigma_SI_M = sigma_SI_with_mA(epsilon, g_D, m_A_prime_MeV)
    ll_lz_elastic = loglike_lz_real(M_CHI_GEV_FIXED, sigma_SI_M)

    # 2. LZ 248 keV (compute event rate from scratch with m_A')
    sigma_inel = sigma_inel_with_mA(epsilon, g_D, f_H, m_A_prime_MeV)
    # Event rate: σ_inel × LZ_EVENT_RATE_COEFF × exposure (NO rate_relative!)
    # LZ_EVENT_RATE_COEFF is events/tonne-year/cm², exposure is tonne-year
    from phase8c_majorana_reframe_joint_fit import (
        LZ_EVENT_RATE_COEFF, LZ_248_KEV_EXPOSURE_TONNE_YEAR, LZ_248_KEV_RATE_TARGET,
        LZ_248_KEV_RATE_SIGMA,
    )
    n_pred = sigma_inel * LZ_EVENT_RATE_COEFF * LZ_248_KEV_EXPOSURE_TONNE_YEAR
    # Clamp to avoid catastrophic penalties at extreme m_A' / g_D
    # If n_pred > 1e6 events, the model is ruled out — cap delta at 1e3
    delta_raw = (n_pred - LZ_248_KEV_RATE_TARGET) / LZ_248_KEV_RATE_SIGMA
    delta = np.clip(delta_raw, -1e3, 1e3)
    ll_lz_248 = -0.5 * delta**2 if lz_248_enabled else 0.0

    # 3. Fermi dwarf (σ_v from g_D, with actual m_A')
    sigma_v = sigma_v_from_dark_photon(
        m_chi_GeV=M_CHI_GEV_FIXED,
        m_A_prime_MeV=m_A_prime_MeV,
        alpha_D=g_D**2 / (4 * np.pi),
    )
    ll_fermi = loglike_fermi_real(M_CHI_GEV_FIXED, sigma_v, channel="bb", use_J_prior=True)

    # 4. dSph + UFD + Bullet
    ll_dsph = ch_v03.loglike_dsph_v03(sigma_m_0, a)
    ll_ufd = ch_v03.loglike_ufd_v03(sigma_m_0, a)
    ll_bullet = ch_v03.loglike_bullet_v03(sigma_m_0, a)

    # 5. SPARC
    try:
        import t8_v03_joint_fit as t8
        ll_sparc = t8.delta_log_sparc(sigma_m_0, a) / 1000
    except Exception:
        ll_sparc = 0.0

    return ll_lz_elastic + ll_lz_248 + ll_fermi + ll_dsph + ll_ufd + ll_bullet + ll_sparc


def prior_transform_6d(u):
    return [
        config.LOG_SIGMA_M_RANGE[0] + u[0] * (config.LOG_SIGMA_M_RANGE[1] - config.LOG_SIGMA_M_RANGE[0]),
        config.A_RANGE[0] + u[1] * (config.A_RANGE[1] - config.A_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[2] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_G_D_RANGE[0] + u[3] * (LOG_G_D_RANGE[1] - LOG_G_D_RANGE[0]),
        LOG_F_H_RANGE[0] + u[4] * (LOG_F_H_RANGE[1] - LOG_F_H_RANGE[0]),
        LOG_M_A_PRIME_MEV_RANGE[0] + u[5] * (LOG_M_A_PRIME_MEV_RANGE[1] - LOG_M_A_PRIME_MEV_RANGE[0]),
    ]


def weighted_quantiles(values, weights, q):
    idx = np.argsort(values)
    values = values[idx]
    weights = weights[idx]
    cumw = np.cumsum(weights)
    cumw = cumw / cumw[-1]
    return np.interp(q, cumw, values)


def main():
    print("=" * 80)
    print("Phase 8d.2 — Majorana + m_A' marginalization (6D)")
    print("=" * 80)
    print(f"Parameters: log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H, log_m_A_prime_MeV")
    print(f"m_A' range: {10**LOG_M_A_PRIME_MEV_RANGE[0]:.0f} to {10**LOG_M_A_PRIME_MEV_RANGE[1]:.0f} MeV")
    print()

    # Run 1: Full
    print("--- RUN 1: LZ 248 keV ENABLED ---")
    t0 = time.time()
    def loglike_full(theta):
        return loglike_joint_6d(theta, lz_248_enabled=True)
    sampler_full = dynesty.NestedSampler(
        loglikelihood=loglike_full,
        prior_transform=prior_transform_6d,
        ndim=6, nlive=150, bound='multi', sample='auto', bootstrap=0,
    )
    sampler_full.run_nested(dlogz=0.3, print_progress=False, maxiter=20000)
    wall_full = time.time() - t0
    res_full = sampler_full.results
    log_Z_full = float(res_full.logz[-1])
    samples_full = res_full.samples
    weights_full = np.exp(res_full.logwt - res_full.logz[-1])
    imap_full = int(np.argmax(weights_full))
    MAP_full = samples_full[imap_full].tolist()

    # Run 2: Baseline
    print("--- RUN 2: LZ 248 keV DISABLED ---")
    t0 = time.time()
    def loglike_base(theta):
        return loglike_joint_6d(theta, lz_248_enabled=False)
    sampler_base = dynesty.NestedSampler(
        loglikelihood=loglike_base,
        prior_transform=prior_transform_6d,
        ndim=6, nlive=150, bound='multi', sample='auto', bootstrap=0,
    )
    sampler_base.run_nested(dlogz=0.3, print_progress=False, maxiter=20000)
    wall_base = time.time() - t0
    res_base = sampler_base.results
    log_Z_base = float(res_base.logz[-1])
    samples_base = res_base.samples
    weights_base = np.exp(res_base.logwt - res_base.logz[-1])
    imap_base = int(np.argmax(weights_base))
    MAP_base = samples_base[imap_base].tolist()

    delta_log_Z = log_Z_full - log_Z_base

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"  Baseline (no 248 keV): log_Z = {log_Z_base:.3f}, wall = {wall_base:.1f}s")
    print(f"    MAP: log_sm={MAP_base[0]:.3f}, a={MAP_base[1]:.3f}, "
          f"log_eps={MAP_base[2]:.3f}, log_gD={MAP_base[3]:.3f}, log_fH={MAP_base[4]:.3f}, "
          f"log_mA={MAP_base[5]:.3f}")
    print()
    print(f"  Full (with 248 keV): log_Z = {log_Z_full:.3f}, wall = {wall_full:.1f}s")
    print(f"    MAP: log_sm={MAP_full[0]:.3f}, a={MAP_full[1]:.3f}, "
          f"log_eps={MAP_full[2]:.3f}, log_gD={MAP_full[3]:.3f}, log_fH={MAP_full[4]:.3f}, "
          f"log_mA={MAP_full[5]:.3f}")
    print()
    print(f"  Δlog Z (full - baseline): {delta_log_Z:+.3f}")

    # Posteriors
    sm_q = [10**q for q in weighted_quantiles(samples_full[:, 0], weights_full, [0.16, 0.5, 0.84])]
    eps_q = [10**q for q in weighted_quantiles(samples_full[:, 2], weights_full, [0.16, 0.5, 0.84])]
    gD_q = [10**q for q in weighted_quantiles(samples_full[:, 3], weights_full, [0.16, 0.5, 0.84])]
    fH_q = [10**q for q in weighted_quantiles(samples_full[:, 4], weights_full, [0.16, 0.5, 0.84])]
    mA_q = [10**q for q in weighted_quantiles(samples_full[:, 5], weights_full, [0.16, 0.5, 0.84])]

    print()
    print(f"  Full fit posteriors (16/50/84%):")
    print(f"    σ/m (cm²/g): {sm_q[0]:.3f} / {sm_q[1]:.3f} / {sm_q[2]:.3f}")
    print(f"    ε:           {eps_q[0]:.2e} / {eps_q[1]:.2e} / {eps_q[2]:.2e}")
    print(f"    g_D:         {gD_q[0]:.3f} / {gD_q[1]:.3f} / {gD_q[2]:.3f}")
    print(f"    f_H:         {fH_q[0]:.3f} / {fH_q[1]:.3f} / {fH_q[2]:.3f}")
    print(f"    m_A' (MeV):  {mA_q[0]:.1f} / {mA_q[1]:.1f} / {mA_q[2]:.1f}")

    print()
    print("  Comparison to Phase 8d (m_A' fixed at 200 MeV):")
    print(f"    Phase 8d full Δlog Z = +0.218")
    print(f"    Phase 8d.2 full Δlog Z = {delta_log_Z:+.3f}")
    print(f"    Δlog Z change from marginalizing m_A': {delta_log_Z - 0.218:+.3f}")

    if delta_log_Z > 0.5:
        verdict = "PROCEED: m_A' marginalization helps the 248 keV channel"
    elif delta_log_Z > -0.5:
        verdict = "MIXED: m_A' marginalization is neutral"
    else:
        verdict = f"REGRESSION: m_A' marginalization hurts by Δlog Z = {delta_log_Z:.1f}"

    print()
    print(f"VERDICT: {verdict}")

    out = {
        "test": "Phase8d2_majorana_mA_marginalized",
        "direction": "Majorana + dark photon, 6D with m_A' marginalized",
        "ndim": 6,
        "parameters": ["log_sigma_m_0", "a", "log_epsilon", "log_g_D", "log_f_H", "log_m_A_prime_MeV"],
        "priors": {
            "log_sigma_m_0": list(config.LOG_SIGMA_M_RANGE),
            "a": list(config.A_RANGE),
            "log_epsilon": list(LOG_EPSILON_RANGE),
            "log_g_D": list(LOG_G_D_RANGE),
            "log_f_H": list(LOG_F_H_RANGE),
            "log_m_A_prime_MeV": list(LOG_M_A_PRIME_MEV_RANGE),
        },
        "log_Z_baseline_no_248kev": log_Z_base,
        "log_Z_full_with_248kev": log_Z_full,
        "delta_log_Z_248keV_contribution": delta_log_Z,
        "MAP_full": {
            "log_sigma_m_0": MAP_full[0],
            "a": MAP_full[1],
            "log_epsilon": MAP_full[2],
            "log_g_D": MAP_full[3],
            "log_f_H": MAP_full[4],
            "log_m_A_prime_MeV": MAP_full[5],
            "sigma_m_cm2_per_g": 10**MAP_full[0],
            "epsilon": 10**MAP_full[2],
            "g_D": 10**MAP_full[3],
            "f_H": 10**MAP_full[4],
            "m_A_prime_MeV": 10**MAP_full[5],
        },
        "posteriors_full_16_50_84": {
            "sigma_m_cm2_per_g": sm_q,
            "epsilon": eps_q,
            "g_D": gD_q,
            "f_H": fH_q,
            "m_A_prime_MeV": mA_q,
        },
        "verdict": verdict,
        "comparison_to_phase8d": {
            "phase8d_delta_log_Z_248kev": 0.218,
            "improvement_from_mA_marginalization": delta_log_Z - 0.218,
        },
        "wall_seconds": wall_full + wall_base,
    }

    out_path = RESULTS_DIR / "phase8d2_majorana_mA_marginalized.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
