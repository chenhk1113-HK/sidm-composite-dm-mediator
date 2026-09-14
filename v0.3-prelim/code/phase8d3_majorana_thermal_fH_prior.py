"""
Phase 8d.3 — Majorana Reframe with thermal f_H prior.

Builds on Phase 8d.1 (α = g_D²/(4π) consistency) with a PHYSICALLY
MOTIVATED prior on f_H.

Background: For exothermic DM with mass splitting δ ~ 0.5-1 MeV, the
excited-state abundance f_H is set by Boltzmann factor at freeze-out:
  f_H ~ 1 / (1 + exp(δ/T_freeze))
  T_freeze ~ δ/10 to δ/30 (kinetic decoupling)
  → f_H ~ exp(-10) to exp(-30) ~ 5e-5 to 1e-13 (very small)

de Lima's f_H = 0.5 is NOT the thermal value — it requires a non-thermal
mechanism (up-scattering, freeze-in, asymmetric). Phase 8c/8d used
log-uniform [0.001, 1.0], which is generous to non-thermal scenarios.

Phase 8d.3 uses a bimodal prior:
  - 50% log-uniform [0.001, 1.0]  (non-thermal)
  - 50% log-normal centered at 1e-5, σ=0.5 dex  (thermal)

This tests whether the data prefers one population or the other.

Parameters (5D, same as 8d):
  log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H

Wall target: ~40s (nlive=200, 5D)
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
    M_CHI_GEV_FIXED, M_A_PRIME_MEV_FIXED, DELTA_KEV_FIXED,
)
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LOG_EPSILON_RANGE = (-12.0, -3.0)
LOG_G_D_RANGE = (-2.0, 0.5)
LOG_F_H_NONTHERMAL_RANGE = (-3.0, 0.0)
LOG_F_H_THERMAL_MEAN = -5.0   # log10(1e-5)
LOG_F_H_THERMAL_SIGMA = 0.5   # 0.5 dex = factor ~3


def f_H_prior_sample(u_f_H: float) -> float:
    """
    Bimodal prior on f_H: 50% non-thermal (log-uniform [1e-3, 1]),
    50% thermal (log-normal centered at 1e-5).

    u_f_H ∈ [0, 1]:
      u_f_H < 0.5: thermal (log-normal)
      u_f_H >= 0.5: non-thermal (log-uniform)
    """
    if u_f_H < 0.5:
        # Thermal: log-normal
        # Map u_f_H in [0, 0.5] to standard normal via inverse CDF
        # Use Box-Muller-like: log-normal from uniform
        # Simple approximation: u in [0, 0.5] → z in [-3, +3] (linear)
        z = (u_f_H / 0.5) * 6.0 - 3.0
        log_f_H = LOG_F_H_THERMAL_MEAN + z * LOG_F_H_THERMAL_SIGMA
        return log_f_H
    else:
        # Non-thermal: log-uniform in [1e-3, 1]
        u_norm = (u_f_H - 0.5) / 0.5  # [0, 1]
        return LOG_F_H_NONTHERMAL_RANGE[0] + u_norm * (
            LOG_F_H_NONTHERMAL_RANGE[1] - LOG_F_H_NONTHERMAL_RANGE[0]
        )


def loglike_joint_5d_fH_prior(theta, lz_248_enabled: bool = True):
    """5D joint fit with bimodal f_H prior."""
    log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H = theta
    sigma_m_0 = 10 ** log_sigma_m_0
    epsilon = 10 ** log_epsilon
    g_D = 10 ** log_g_D
    f_H = 10 ** log_f_H

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
    # For bimodal: thermal range is wide (allow log_f_H from -10 to 0)
    if not (-10.0 <= log_f_H <= 0.0):
        return -np.inf

    # 1. LZ elastic
    sigma_SI_M = sigma_SI_majorana_cm2(epsilon, g_D)
    ll_lz_elastic = loglike_lz_real(M_CHI_GEV_FIXED, sigma_SI_M)

    # 2. LZ 248 keV
    ll_lz_248 = loglike_lz_248keV(epsilon, g_D, f_H) if lz_248_enabled else 0.0

    # 3. Fermi (α = g_D²/4π)
    sigma_v = sigma_v_majorana_cm3_per_s(g_D)
    ll_fermi = loglike_fermi_real(M_CHI_GEV_FIXED, sigma_v, channel="bb", use_J_prior=True)

    # 4. SIDM
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


def prior_transform_5d_fH(u):
    return [
        config.LOG_SIGMA_M_RANGE[0] + u[0] * (config.LOG_SIGMA_M_RANGE[1] - config.LOG_SIGMA_M_RANGE[0]),
        config.A_RANGE[0] + u[1] * (config.A_RANGE[1] - config.A_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[2] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_G_D_RANGE[0] + u[3] * (LOG_G_D_RANGE[1] - LOG_G_D_RANGE[0]),
        f_H_prior_sample(u[4]),
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
    print("Phase 8d.3 — Majorana + bimodal f_H prior (thermal vs non-thermal)")
    print("=" * 80)
    print(f"f_H prior: 50% log-normal(μ=1e-5, σ=0.5 dex) thermal,")
    print(f"           50% log-uniform[1e-3, 1] non-thermal")
    print()

    # Run 1: Full
    print("--- RUN 1: LZ 248 keV ENABLED ---")
    t0 = time.time()
    def loglike_full(theta):
        return loglike_joint_5d_fH_prior(theta, lz_248_enabled=True)
    sampler_full = dynesty.NestedSampler(
        loglikelihood=loglike_full,
        prior_transform=prior_transform_5d_fH,
        ndim=5, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler_full.run_nested(dlogz=0.1, print_progress=False)
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
        return loglike_joint_5d_fH_prior(theta, lz_248_enabled=False)
    sampler_base = dynesty.NestedSampler(
        loglikelihood=loglike_base,
        prior_transform=prior_transform_5d_fH,
        ndim=5, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler_base.run_nested(dlogz=0.1, print_progress=False)
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
          f"log_eps={MAP_base[2]:.3f}, log_gD={MAP_base[3]:.3f}, log_fH={MAP_base[4]:.3f}")
    print()
    print(f"  Full (with 248 keV): log_Z = {log_Z_full:.3f}, wall = {wall_full:.1f}s")
    print(f"    MAP: log_sm={MAP_full[0]:.3f}, a={MAP_full[1]:.3f}, "
          f"log_eps={MAP_full[2]:.3f}, log_gD={MAP_full[3]:.3f}, log_fH={MAP_full[4]:.3f}")
    print()
    print(f"  Δlog Z (full - baseline): {delta_log_Z:+.3f}")

    # Posteriors
    sm_q = [10**q for q in weighted_quantiles(samples_full[:, 0], weights_full, [0.16, 0.5, 0.84])]
    eps_q = [10**q for q in weighted_quantiles(samples_full[:, 2], weights_full, [0.16, 0.5, 0.84])]
    gD_q = [10**q for q in weighted_quantiles(samples_full[:, 3], weights_full, [0.16, 0.5, 0.84])]
    fH_q = [10**q for q in weighted_quantiles(samples_full[:, 4], weights_full, [0.16, 0.5, 0.84])]

    # f_H mode decomposition: how much weight on thermal vs non-thermal
    log_f_H_samples = samples_full[:, 4]
    thermal_mask = log_f_H_samples < (LOG_F_H_NONTHERMAL_RANGE[0])
    f_H_thermal_weight = weights_full[thermal_mask].sum() / weights_full.sum()
    f_H_nonthermal_weight = 1.0 - f_H_thermal_weight

    print()
    print(f"  Full fit posteriors (16/50/84%):")
    print(f"    σ/m (cm²/g): {sm_q[0]:.3f} / {sm_q[1]:.3f} / {sm_q[2]:.3f}")
    print(f"    ε:           {eps_q[0]:.2e} / {eps_q[1]:.2e} / {eps_q[2]:.2e}")
    print(f"    g_D:         {gD_q[0]:.3f} / {gD_q[1]:.3f} / {gD_q[2]:.3f}")
    print(f"    f_H:         {fH_q[0]:.3e} / {fH_q[1]:.3e} / {fH_q[2]:.3e}")
    print()
    print(f"  f_H mode weights:")
    print(f"    Thermal (f_H < 1e-3):     {f_H_thermal_weight*100:.1f}%")
    print(f"    Non-thermal (f_H > 1e-3): {f_H_nonthermal_weight*100:.1f}%")

    print()
    print("  Comparison to Phase 8d (uniform f_H prior):")
    print(f"    Phase 8d full Δlog Z = +0.218")
    print(f"    Phase 8d.3 full Δlog Z = {delta_log_Z:+.3f}")
    print(f"    Δlog Z change from physical f_H prior: {delta_log_Z - 0.218:+.3f}")

    if delta_log_Z > 0.5:
        verdict = "PROCEED: physical f_H prior helps the 248 keV channel"
    elif delta_log_Z > -0.5:
        verdict = "MIXED: physical f_H prior is neutral"
    else:
        verdict = f"REGRESSION: physical f_H prior hurts by Δlog Z = {delta_log_Z:.1f}"

    print()
    print(f"VERDICT: {verdict}")

    out = {
        "test": "Phase8d3_majorana_thermal_fH_prior",
        "direction": "Majorana + dark photon, 5D with bimodal f_H prior (thermal/non-thermal)",
        "ndim": 5,
        "f_H_prior": {
            "thermal_weight": 0.5,
            "thermal_mean_log": LOG_F_H_THERMAL_MEAN,
            "thermal_sigma_log": LOG_F_H_THERMAL_SIGMA,
            "nonthermal_weight": 0.5,
            "nonthermal_range_log": list(LOG_F_H_NONTHERMAL_RANGE),
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
            "sigma_m_cm2_per_g": 10**MAP_full[0],
            "epsilon": 10**MAP_full[2],
            "g_D": 10**MAP_full[3],
            "f_H": 10**MAP_full[4],
        },
        "posteriors_full_16_50_84": {
            "sigma_m_cm2_per_g": sm_q,
            "epsilon": eps_q,
            "g_D": gD_q,
            "f_H": fH_q,
        },
        "f_H_mode_weights": {
            "thermal": float(f_H_thermal_weight),
            "nonthermal": float(f_H_nonthermal_weight),
        },
        "verdict": verdict,
        "comparison_to_phase8d": {
            "phase8d_delta_log_Z_248kev": 0.218,
            "improvement_from_physical_fH_prior": delta_log_Z - 0.218,
        },
        "wall_seconds": wall_full + wall_base,
    }

    out_path = RESULTS_DIR / "phase8d3_majorana_thermal_fH_prior.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
