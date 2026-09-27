"""
Phase 19 — Full v0.3-prelim Joint Fit at m_chi = 5 GeV

Refits the complete v0.3-prelim Majorana reframe pipeline at the
natural asymmetric DM mass m_chi = 5 GeV. Compares results to the
m_chi = 45 GeV baseline (Phase 8d) and tests if the natural mass
resolves the asymmetry tuning.

Same framework as Phase 8d.1 (5D, α = g_D²/4π):
  Parameters: log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H
  Channels: LZ elastic + LZ 248 keV + Fermi dwarf + SIDM (dSph, UFD,
            Bullet, SPARC saturation)

Differences from Phase 8d.1:
  - m_chi = 5 GeV (was 45 GeV)
  - All other model parameters same
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v0.1-prelim" / "code"))

import dynesty
import config
import channels_v03 as ch_v03
from t30_lz_real_posterior import loglike_lz_real
from t32_real_likelihood import loglike_fermi_real
from phase8c_majorana_reframe_joint_fit import (
    sigma_SI_majorana_cm2, sigma_inel_majorana_cm2,
    loglike_lz_248keV, M_CHI_GEV_FIXED, M_A_PRIME_MEV_FIXED,
    DELTA_KEV_FIXED, LZ_248_KEV_EXPOSURE_TONNE_YEAR,
    LZ_248_KEV_RATE_TARGET, LZ_248_KEV_RATE_SIGMA, LZ_EVENT_RATE_COEFF,
)
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# m_chi = 5 GeV — natural asymmetric DM mass
M_CHI_GEV_NEW = 5.0
LOG_EPSILON_RANGE = (-12.0, -3.0)
LOG_G_D_RANGE = (-2.0, 0.5)
LOG_F_H_RANGE = (-3.0, 0.0)


def loglike_full_mchi5(theta):
    """5D loglike at m_chi = 5 GeV."""
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

    # 1. LZ elastic (m_chi-dependent)
    sigma_SI_M = sigma_SI_majorana_cm2(epsilon, g_D)
    ll_lz_elastic = loglike_lz_real(M_CHI_GEV_NEW, sigma_SI_M)

    # 2. LZ 248 keV (m_chi-dependent via inelastic kinematics)
    sigma_inel = sigma_inel_majorana_cm2(epsilon, g_D, f_H, m_chi_GeV=M_CHI_GEV_NEW, m_A_prime_MeV=M_A_PRIME_MEV_FIXED)
    n_pred = sigma_inel * LZ_EVENT_RATE_COEFF * LZ_248_KEV_EXPOSURE_TONNE_YEAR
    n_pred = np.clip(n_pred, 1e-6, 1e6)
    delta = (n_pred - LZ_248_KEV_RATE_TARGET) / LZ_248_KEV_RATE_SIGMA
    ll_lz_248 = -0.5 * delta**2

    # 3. Fermi dwarf (m_chi-dependent)
    sigma_v = sigma_v_majorana_cm3_per_s(g_D)
    ll_fermi = loglike_fermi_real(M_CHI_GEV_NEW, sigma_v, channel="bb", use_J_prior=True)

    # 4. SIDM channels (m_chi-independent)
    ll_dsph = ch_v03.loglike_dsph_v03(sigma_m_0, a)
    ll_ufd = ch_v03.loglike_ufd_v03(sigma_m_0, a)
    ll_bullet = ch_v03.loglike_bullet_v03(sigma_m_0, a)

    # 5. SPARC (m_chi-independent, saturation proxy)
    try:
        import t8_v03_joint_fit as t8
        ll_sparc = t8.delta_log_sparc(sigma_m_0, a) / 1000
    except Exception:
        ll_sparc = 0.0

    return ll_lz_elastic + ll_lz_248 + ll_fermi + ll_dsph + ll_ufd + ll_bullet + ll_sparc


def loglike_baseline_mchi5(theta):
    """Baseline: LZ elastic + Fermi + SIDM (no LZ 248 keV channel)."""
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

    sigma_SI_M = sigma_SI_majorana_cm2(epsilon, g_D)
    ll_lz_elastic = loglike_lz_real(M_CHI_GEV_NEW, sigma_SI_M)

    sigma_v = sigma_v_majorana_cm3_per_s(g_D)
    ll_fermi = loglike_fermi_real(M_CHI_GEV_NEW, sigma_v, channel="bb", use_J_prior=True)

    ll_dsph = ch_v03.loglike_dsph_v03(sigma_m_0, a)
    ll_ufd = ch_v03.loglike_ufd_v03(sigma_m_0, a)
    ll_bullet = ch_v03.loglike_bullet_v03(sigma_m_0, a)

    try:
        import t8_v03_joint_fit as t8
        ll_sparc = t8.delta_log_sparc(sigma_m_0, a) / 1000
    except Exception:
        ll_sparc = 0.0

    return ll_lz_elastic + ll_fermi + ll_dsph + ll_ufd + ll_bullet + ll_sparc


def prior_transform_5d(u):
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


def run_fit(loglike_fn, label: str) -> dict:
    """Run 5D fit with given loglike function."""
    print(f"\n--- RUN: {label} ---")
    t0 = time.time()

    sampler = dynesty.NestedSampler(
        loglikelihood=loglike_fn,
        prior_transform=prior_transform_5d,
        ndim=5, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=0.3, print_progress=False, maxiter=15000)

    wall = time.time() - t0
    res = sampler.results
    log_Z = float(res.logz[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()

    sm_q = [10**q for q in weighted_quantiles(samples[:, 0], weights, [0.16, 0.5, 0.84])]
    gd_q = [10**q for q in weighted_quantiles(samples[:, 3], weights, [0.16, 0.5, 0.84])]
    fh_q = [10**q for q in weighted_quantiles(samples[:, 4], weights, [0.16, 0.5, 0.84])]

    print(f"  log_Z = {log_Z:.3f}, wall = {wall:.1f}s")
    print(f"  MAP: σ/m = {10**MAP[0]:.3f}, a = {MAP[1]:.3f}, g_D = {10**MAP[3]:.3f}, f_H = {10**MAP[4]:.3f}")
    print(f"  Posterior 16/50/84%: σ/m = {sm_q[0]:.3f} / {sm_q[1]:.3f} / {sm_q[2]:.3f}")
    print(f"  Posterior 16/50/84%: g_D = {gd_q[0]:.3f} / {gd_q[1]:.3f} / {gd_q[2]:.3f}")
    print(f"  Posterior 16/50/84%: f_H = {fh_q[0]:.3f} / {fh_q[1]:.3f} / {fh_q[2]:.3f}")

    return {
        "log_Z": log_Z,
        "MAP": MAP,
        "MAP_sigma_m": 10**MAP[0],
        "MAP_a": MAP[1],
        "MAP_g_D": 10**MAP[3],
        "MAP_f_H": 10**MAP[4],
        "posterior_sigma_m_16_50_84": sm_q,
        "posterior_g_D_16_50_84": gd_q,
        "posterior_f_H_16_50_84": fh_q,
        "wall_seconds": wall,
    }


def main():
    print("=" * 80)
    print("Phase 19 — Full v0.3-prelim Joint Fit at m_chi = 5 GeV")
    print("=" * 80)
    print(f"Re-running the entire v0.3-prelim Majorana reframe at m_chi = 5 GeV")
    print(f"(natural asymmetric DM mass, per Phase 16 finding)")
    print()

    out = {
        "test": "Phase19_full_fit_mchi_5GeV",
        "m_chi_GeV": M_CHI_GEV_NEW,
        "direction": "Refit the entire v0.3-prelim pipeline at the natural asymmetric DM mass",
    }

    results = {}
    results["baseline_no_LZ248"] = run_fit(loglike_baseline_mchi5, "Baseline (no LZ 248 keV)")
    results["full_with_LZ248"] = run_fit(loglike_full_mchi5, "Full (with LZ 248 keV)")

    delta_log_Z = results["full_with_LZ248"]["log_Z"] - results["baseline_no_LZ248"]["log_Z"]

    print()
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"Baseline log_Z (no LZ 248): {results['baseline_no_LZ248']['log_Z']:.3f}")
    print(f"Full log_Z (with LZ 248):   {results['full_with_LZ248']['log_Z']:.3f}")
    print(f"Δlog Z (full - baseline):   {delta_log_Z:+.3f}")
    print()
    print(f"MAP at m_chi = 5 GeV (full):")
    print(f"  σ/m = {results['full_with_LZ248']['MAP_sigma_m']:.3f} cm²/g")
    print(f"  g_D  = {results['full_with_LZ248']['MAP_g_D']:.3f}")
    print(f"  f_H  = {results['full_with_LZ248']['MAP_f_H']:.3f}")
    print()
    print(f"Compare to Phase 8d at m_chi = 45 GeV:")
    print(f"  σ/m = 0.065, g_D = 0.146, f_H = 0.030, Δlog Z = +0.22")

    if abs(delta_log_Z) < 0.5:
        verdict = "INERT at m_chi = 5 GeV (LZ 248 keV has minimal effect, like 45 GeV)"
    elif delta_log_Z > 0.5:
        verdict = f"FAVORED at m_chi = 5 GeV (Δlog Z = {delta_log_Z:+.2f})"
    else:
        verdict = f"DISFAVORED at m_chi = 5 GeV (Δlog Z = {delta_log_Z:+.2f})"
    print(f"\nVERDICT: {verdict}")

    out["results"] = results
    out["delta_log_Z"] = delta_log_Z
    out["verdict"] = verdict
    out["comparison_to_45GeV"] = {
        "phase_8d_45GeV": {"sigma_m": 0.065, "g_D": 0.146, "f_H": 0.030, "delta_log_Z": 0.22},
        "phase_19_5GeV": {
            "sigma_m": results["full_with_LZ248"]["MAP_sigma_m"],
            "g_D": results["full_with_LZ248"]["MAP_g_D"],
            "f_H": results["full_with_LZ248"]["MAP_f_H"],
            "delta_log_Z": delta_log_Z,
        },
    }

    out_path = RESULTS_DIR / "phase19_full_fit_mchi_5GeV.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
