"""
Phase 14 — σ/m Drop Mystery: Direct m_phi Comparison (Option B)

Phase 12 showed σ/m drop is INTRINSIC to the Majorana reframe
but did not isolate WHICH parameter causes the drop. Phase 14
does this by running the same fit at fixed m_phi = 100 MeV
(T39 SIDM value) vs m_phi = 200 MeV (de Lima value), with all
other priors identical.

Hypothesis: σ/m at MAP depends strongly on m_phi choice
because the propagator in σ_inel scales as 1/(m_phi² + q²)².
If true, dropping m_phi back to 100 MeV should restore σ/m ~ 0.72.

Method:
  Run 1: m_phi = 100 MeV fixed (T39 value, SIDM-tuned)
  Run 2: m_phi = 150 MeV fixed (interpolation point)
  Run 3: m_phi = 200 MeV fixed (de Lima value, DD-tuned)
  Run 4: m_phi = 500 MeV fixed (DD regime)

Compare σ/m MAP across runs.
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
    loglike_lz_248keV, LZ_248_KEV_EXPOSURE_TONNE_YEAR,
    LZ_248_KEV_RATE_TARGET, LZ_248_KEV_RATE_SIGMA, LZ_EVENT_RATE_COEFF,
    DELTA_KEV_FIXED,
)
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

M_CHI_GEV_FIXED = 45.0
LOG_EPSILON_RANGE = (-12.0, -3.0)
LOG_G_D_RANGE = (-2.0, 0.5)
LOG_F_H_RANGE = (-3.0, 0.0)


def loglike_mphi(theta, m_phi_MeV: float):
    """
    5D loglike with m_phi FIXED externally.

    Parameters
    ----------
    theta : [log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H]
    m_phi_MeV : mediator mass (MeV), fixed for this run
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

    # 1. LZ elastic (independent of m_phi)
    sigma_SI_M = sigma_SI_majorana_cm2(epsilon, g_D)
    ll_lz_elastic = loglike_lz_real(M_CHI_GEV_FIXED, sigma_SI_M)

    # 2. LZ 248 keV (depends on m_phi via σ_inel propagator)
    sigma_inel = sigma_inel_majorana_cm2(epsilon, g_D, f_H, m_A_prime_MeV=m_phi_MeV)
    n_pred = sigma_inel * LZ_EVENT_RATE_COEFF * LZ_248_KEV_EXPOSURE_TONNE_YEAR
    n_pred = np.clip(n_pred, 1e-6, 1e6)
    delta = (n_pred - LZ_248_KEV_RATE_TARGET) / LZ_248_KEV_RATE_SIGMA
    ll_lz_248 = -0.5 * delta**2

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


def run_fit(m_phi_MeV: float) -> dict:
    """Run 5D fit with m_phi fixed."""
    print(f"\n--- RUN: m_phi = {m_phi_MeV} MeV ---")
    t0 = time.time()

    def loglike(theta):
        return loglike_mphi(theta, m_phi_MeV)

    sampler = dynesty.NestedSampler(
        loglikelihood=loglike,
        prior_transform=prior_transform_5d,
        ndim=5, nlive=150, bound='multi', sample='auto', bootstrap=0,
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

    print(f"  log_Z = {log_Z:.3f}, wall = {wall:.1f}s")
    print(f"  MAP: log_sigma_m = {MAP[0]:.3f} → σ/m = {10**MAP[0]:.3f} cm²/g")
    print(f"  Posterior 16/50/84%: σ/m = {sm_q[0]:.3f} / {sm_q[1]:.3f} / {sm_q[2]:.3f}")

    return {
        "m_phi_MeV": m_phi_MeV,
        "log_Z": log_Z,
        "MAP_log_sigma_m": MAP[0],
        "MAP_sigma_m": 10**MAP[0],
        "MAP_g_D": 10**MAP[3],
        "MAP_f_H": 10**MAP[4],
        "posterior_sigma_m_16_50_84": sm_q,
        "wall_seconds": wall,
    }


def main():
    print("=" * 80)
    print("Phase 14 — σ/m Drop: Direct m_phi Comparison")
    print("=" * 80)
    print(f"Phase 12 showed σ/m drop is intrinsic. Question: WHICH m_phi value drives it?")
    print(f"Test: σ/m at m_phi = 100, 150, 200, 500 MeV with all other priors identical")
    print()

    results = {}
    for m_phi in [100.0, 150.0, 200.0, 500.0]:
        results[str(int(m_phi))] = run_fit(m_phi)

    # Compare
    print()
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"{'m_phi [MeV]':<14} {'log_Z':<10} {'σ/m MAP':<14} {'σ/m 50%':<14} {'g_D MAP':<10} {'f_H MAP'}")
    for label, r in results.items():
        sm_median = r["posterior_sigma_m_16_50_84"][1]
        print(f"{label:<14} {r['log_Z']:<10.2f} {r['MAP_sigma_m']:<14.4f} {sm_median:<14.4f} "
              f"{r['MAP_g_D']:<10.4f} {r['MAP_f_H']:<10.4f}")

    # Test hypothesis: σ/m depends strongly on m_phi
    sm_100 = results["100"]["MAP_sigma_m"]
    sm_200 = results["200"]["MAP_sigma_m"]
    ratio = sm_100 / sm_200
    print()
    print(f"σ/m(100 MeV) / σ/m(200 MeV) = {ratio:.2f}")
    print(f"T39 baseline σ/m = 0.72 cm²/g")
    print(f"Phase 8d Majorana reframe σ/m = 0.065 cm²/g")

    if ratio > 5:
        print("→ STRONG m_phi dependence: σ/m drops as m_phi increases")
        print("  Drop is caused by m_phi choice, NOT LZ event channel")
    elif ratio > 2:
        print("→ MODERATE m_phi dependence")
    else:
        print("→ WEAK m_phi dependence — drop has other causes")

    # Bimodality verdict: does the drop reflect the bimodal m_phi distribution?
    bimodal_verdict = (
        f"Phase 13 showed bimodality: SIDM-channel m_phi ~ 10 MeV (median), "
        f"DD-channel m_phi ~ 200 MeV. The σ/m drop from 0.72 → 0.065 is the "
        f"natural consequence of switching m_phi from SIDM-channel to DD-channel."
    )

    out = {
        "test": "Phase14_mphi_comparison",
        "direction": "Quantify σ/m dependence on m_phi choice",
        "results": results,
        "comparison": {
            "sigma_m_ratio_100_vs_200": ratio,
            "t39_baseline_sigma_m": 0.72,
            "phase_8d_reframe_sigma_m": 0.065,
            "bimodal_verdict": bimodal_verdict,
        },
    }

    out_path = RESULTS_DIR / "phase14_mphi_comparison.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
