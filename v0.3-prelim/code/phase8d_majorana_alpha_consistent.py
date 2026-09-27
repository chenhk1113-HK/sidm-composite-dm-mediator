"""
Phase 8d — Majorana Dark Photon Reframe with α = g_D²/(4π) consistency.

Addresses the honest caveat from Phase 8c: α (annihilation coupling) and
g_D (dark gauge coupling) were independently varied, but they're physically
linked via α_D = g_D²/(4π). Phase 8d enforces this consistency by:

1. Dropping log_alpha as a free parameter
2. Deriving σ_v directly from g_D via Berlin+ 2018
3. Keeping the same Majorana reframe structure (σ_SI² ∝ (g_D ε)²)

This reduces the parameter count from 6D to 5D but enforces physical
consistency. Δlog Z vs Phase 8c baseline tests whether the consistency
constraint helps or hurts.

Priors (5D):
  log_sigma_m_0 ∈ [-3.0, 2.5]
  a             ∈ [-2.0, 2.0]
  log_epsilon   ∈ [-12, -3]    (REFRAME: was [-60, -1] in T39)
  log_g_D       ∈ [-2.0, 0.5]  (g_D ∈ [0.01, 3.16])
  log_f_H       ∈ [-3.0, 0.0]  (f_H ∈ [0.001, 1.0])

Wall target: ~20s (nlive=200, 5D)
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
from t30_lz_real_posterior import loglike_lz_real, LZ_REAL
from t32_real_likelihood import loglike_fermi_real
from t39_tier3_epsilon_alpha_joint_fit import sigma_v_from_dark_photon
from phase8c_majorana_reframe_joint_fit import (
    sigma_SI_majorana_cm2, sigma_inel_majorana_cm2,
    lz_248keV_event_rate, loglike_lz_248keV,
    M_CHI_GEV_FIXED, M_A_PRIME_MEV_FIXED, DELTA_KEV_FIXED,
    LZ_248_KEV_EXPOSURE_TONNE_YEAR,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Priors (5D)
LOG_EPSILON_RANGE = (-12.0, -3.0)
LOG_G_D_RANGE = (-2.0, 0.5)
LOG_F_H_RANGE = (-3.0, 0.0)


def sigma_v_majorana_cm3_per_s(g_D: float, m_chi_GeV: float = M_CHI_GEV_FIXED,
                                 m_A_prime_MeV: float = M_A_PRIME_MEV_FIXED) -> float:
    """
    Majorana DM annihilation σ_v via dark photon.

    σ_v = (π α_D²/m_χ²) × v_rel × phase_space

    This is the Berlin+ 2018 formula with α_D = g_D²/(4π) derived
    consistently from g_D. No free α parameter.
    """
    return sigma_v_from_dark_photon(
        m_chi_GeV=m_chi_GeV,
        m_A_prime_MeV=m_A_prime_MeV,
        alpha_D=g_D**2 / (4 * np.pi),
    )


def loglike_joint_majorana_5d(theta, lz_248_enabled: bool = True):
    """
    5D joint likelihood under the Majorana reframe with α = g_D²/(4π).

    theta = (log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H)

    Channels:
      - LZ elastic: σ_SI^Majorana = σ_SI^Dirac × (g_D ε)²
      - LZ 248 keV: Poisson event-rate (toggle)
      - Fermi dwarf: σ_v from g_D (no free α)
      - SIDM: σ/m(v) at dSph/UFD/Bullet
      - SPARC: sigma_m_0, a
    """
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
    if not (LOG_F_H_RANGE[0] <= log_f_H <= LOG_F_H_RANGE[1]):
        return -np.inf

    # 1. LZ elastic (Majorana second-order)
    sigma_SI_M = sigma_SI_majorana_cm2(epsilon, g_D)
    ll_lz_elastic = loglike_lz_real(M_CHI_GEV_FIXED, sigma_SI_M)

    # 2. LZ 248 keV (Majorana inelastic)
    ll_lz_248 = loglike_lz_248keV(epsilon, g_D, f_H) if lz_248_enabled else 0.0

    # 3. Fermi dwarf (σ_v from g_D — consistency enforced)
    sigma_v = sigma_v_majorana_cm3_per_s(g_D)
    ll_fermi = loglike_fermi_real(M_CHI_GEV_FIXED, sigma_v, channel="bb", use_J_prior=True)

    # 4. dSph + UFD + Bullet
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


def prior_transform_5(u):
    return [
        config.LOG_SIGMA_M_RANGE[0] + u[0] * (config.LOG_SIGMA_M_RANGE[1] - config.LOG_SIGMA_M_RANGE[0]),
        config.A_RANGE[0] + u[1] * (config.A_RANGE[1] - config.A_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[2] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_G_D_RANGE[0] + u[3] * (LOG_G_D_RANGE[1] - LOG_G_D_RANGE[0]),
        LOG_F_H_RANGE[0] + u[4] * (LOG_F_H_RANGE[1] - LOG_F_H_RANGE[0]),
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
    print("Phase 8d — Majorana Reframe with α = g_D²/(4π) consistency (5D)")
    print("=" * 80)
    print(f"Parameters: log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H (5D)")
    print(f"epsilon range: 10^{LOG_EPSILON_RANGE[0]:.0f} to 10^{LOG_EPSILON_RANGE[1]:.0f}")
    print(f"g_D range:     10^{LOG_G_D_RANGE[0]:.1f} to 10^{LOG_G_D_RANGE[1]:.1f}")
    print(f"f_H range:     10^{LOG_F_H_RANGE[0]:.1f} to 10^{LOG_F_H_RANGE[1]:.1f}")
    print()

    # ===== RUN 1: Full =====
    print("--- RUN 1: LZ 248 keV ENABLED ---")
    t0 = time.time()

    def loglike_full(theta):
        return loglike_joint_majorana_5d(theta, lz_248_enabled=True)

    sampler_full = dynesty.NestedSampler(
        loglikelihood=loglike_full,
        prior_transform=prior_transform_5,
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

    # ===== RUN 2: Baseline (no 248 keV) =====
    print("--- RUN 2: LZ 248 keV DISABLED ---")
    t0 = time.time()

    def loglike_baseline(theta):
        return loglike_joint_majorana_5d(theta, lz_248_enabled=False)

    sampler_base = dynesty.NestedSampler(
        loglikelihood=loglike_baseline,
        prior_transform=prior_transform_5,
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
    print(f"  Δlog Z (Phase 8d full - baseline): {delta_log_Z:+.3f}")

    # Posterior summaries
    sm_q = [10**q for q in weighted_quantiles(samples_full[:, 0], weights_full, [0.16, 0.5, 0.84])]
    eps_q = [10**q for q in weighted_quantiles(samples_full[:, 2], weights_full, [0.16, 0.5, 0.84])]
    gD_q = [10**q for q in weighted_quantiles(samples_full[:, 3], weights_full, [0.16, 0.5, 0.84])]
    fH_q = [10**q for q in weighted_quantiles(samples_full[:, 4], weights_full, [0.16, 0.5, 0.84])]

    print()
    print(f"  Full fit posteriors (16/50/84%):")
    print(f"    σ/m (cm²/g): {sm_q[0]:.3f} / {sm_q[1]:.3f} / {sm_q[2]:.3f}")
    print(f"    ε:           {eps_q[0]:.2e} / {eps_q[1]:.2e} / {eps_q[2]:.2e}")
    print(f"    g_D:         {gD_q[0]:.3f} / {gD_q[1]:.3f} / {gD_q[2]:.3f}")
    print(f"    f_H:         {fH_q[0]:.3f} / {fH_q[1]:.3f} / {fH_q[2]:.3f}")

    # Compare to Phase 8c
    print()
    print("  Comparison to Phase 8c (α decoupled, 6D):")
    print(f"    Phase 8c baseline log_Z = -206.76")
    print(f"    Phase 8d baseline log_Z = {log_Z_base:.3f}")
    print(f"    Improvement from consistency: Δlog Z = {log_Z_base - (-206.76):+.3f}")
    print()
    print(f"    Phase 8c full Δlog Z (vs baseline) = -0.17")
    print(f"    Phase 8d full Δlog Z (vs baseline) = {delta_log_Z:+.3f}")
    print(f"    Δlog Z improvement: {(delta_log_Z - (-0.17)):+.3f}")

    if delta_log_Z > 0.5:
        verdict = "PROCEED: consistency constraint helps the 248 keV channel"
    elif delta_log_Z > -0.5:
        verdict = "MIXED: consistency constraint is neutral"
    else:
        verdict = f"REGRESSION: consistency constraint hurts by Δlog Z = {delta_log_Z:.1f}"

    print()
    print(f"VERDICT: {verdict}")

    out = {
        "test": "Phase8d_majorana_alpha_consistent",
        "direction": "Majorana + dark photon, 5D with α = g_D²/(4π) enforced",
        "ndim": 5,
        "parameters": ["log_sigma_m_0", "a", "log_epsilon", "log_g_D", "log_f_H"],
        "priors": {
            "log_sigma_m_0": list(config.LOG_SIGMA_M_RANGE),
            "a": list(config.A_RANGE),
            "log_epsilon": list(LOG_EPSILON_RANGE),
            "log_g_D": list(LOG_G_D_RANGE),
            "log_f_H": list(LOG_F_H_RANGE),
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
            "alpha_D_implied": (10**MAP_full[3])**2 / (4 * np.pi),
        },
        "MAP_baseline": {
            "log_sigma_m_0": MAP_base[0],
            "a": MAP_base[1],
            "log_epsilon": MAP_base[2],
            "log_g_D": MAP_base[3],
            "log_f_H": MAP_base[4],
        },
        "posteriors_full_16_50_84": {
            "sigma_m_cm2_per_g": sm_q,
            "epsilon": eps_q,
            "g_D": gD_q,
            "f_H": fH_q,
        },
        "verdict": verdict,
        "comparison_to_phase8c": {
            "phase8c_baseline_log_Z": -206.76,
            "phase8c_delta_log_Z_248kev": -0.17,
            "improvement_from_consistency": log_Z_base - (-206.76),
            "improvement_in_248kev_channel": delta_log_Z - (-0.17),
        },
        "wall_seconds": wall_full + wall_base,
    }

    out_path = RESULTS_DIR / "phase8d_majorana_alpha_consistent.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
