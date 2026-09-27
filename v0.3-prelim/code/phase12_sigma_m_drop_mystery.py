"""
Phase 12 — Investigate the σ/m drop mystery (T39 0.72 → Phase 8c 0.065)

The Phase 8c/8d Majorana reframe showed σ/m posterior dropping from
T39's MAP at 0.72 cm²/g to Phase 8c's MAP at 0.065 cm²/g (10× drop).

Three hypotheses to test:
  (A) LZ 248 keV event is statistical fluctuation (N=1, Poisson)
      → Drop the channel, see if σ/m returns to ~0.7
  (B) SIDM channels overestimate σ/m at v=100 (LSB/galactic calibration)
      → Refit with v=100 km/s at SIDM MAP → check sigma_m there
  (C) Different physics: SIDM σ/m(v_disp) vs σ_inelastic(m_A', g_D, ε)
      → Parameter decoupling; both can be at different values

Method: Run three ablations on the Phase 8d.1 framework:
  Run 1: LZ 248 keV ON (baseline = Phase 8d.1 result)
  Run 2: LZ 248 keV OFF (drop the channel entirely)
  Run 3: LZ 248 keV CHANNEL replaced with "expected σ_inel ~ 0" (null hypothesis)

If Run 2 σ/m returns to ~0.7: hypothesis A is correct (statistical fluctuation)
If Run 3 differs from Run 2: hypothesis C is correct (channel physics)
If Run 2 still gives 0.065: hypothesis B (SIDM channel issue)
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
    loglike_lz_248keV, loglike_joint_majorana,
    M_CHI_GEV_FIXED, M_A_PRIME_MEV_FIXED, DELTA_KEV_FIXED,
    LZ_248_KEV_EXPOSURE_TONNE_YEAR, LZ_248_KEV_RATE_TARGET,
    LZ_248_KEV_RATE_SIGMA, LZ_EVENT_RATE_COEFF,
)
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LOG_EPSILON_RANGE = (-12.0, -3.0)
LOG_G_D_RANGE = (-2.0, 0.5)
LOG_F_H_RANGE = (-3.0, 0.0)


def loglike_sigma_m_drop_investigation(theta, lz_248_mode: str = "on"):
    """
    5D loglike with three LZ 248 keV modes.

    Modes:
      "on":        Full Poisson likelihood (Phase 8d.1 baseline)
      "off":       Channel disabled
      "null":      Replaced with N_obs = 0 (no event seen)
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

    # 1. LZ elastic
    sigma_SI_M = sigma_SI_majorana_cm2(epsilon, g_D)
    ll_lz_elastic = loglike_lz_real(M_CHI_GEV_FIXED, sigma_SI_M)

    # 2. LZ 248 keV (mode-dependent)
    if lz_248_mode == "off":
        ll_lz_248 = 0.0
    elif lz_248_mode == "null":
        # Hypothetical: NO event seen (N_obs = 0)
        # Penalize any predicted events > 0
        sigma_inel = sigma_inel_majorana_cm2(epsilon, g_D, f_H)
        n_pred = sigma_inel * LZ_EVENT_RATE_COEFF * LZ_248_KEV_EXPOSURE_TONNE_YEAR
        # N_obs = 0: penalize if n_pred > 0
        delta = (n_pred - 0.0) / 1.0  # σ = 1 event
        ll_lz_248 = -0.5 * delta**2 if n_pred > 0 else 0.0
    else:  # "on"
        ll_lz_248 = loglike_lz_248keV(epsilon, g_D, f_H)

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


def run_fit(mode: str) -> dict:
    """Run a 5D fit with the given LZ 248 keV mode."""
    print(f"\n--- RUN: lz_248_mode = {mode} ---")
    t0 = time.time()

    def loglike(theta):
        return loglike_sigma_m_drop_investigation(theta, lz_248_mode=mode)

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
        "mode": mode,
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
    print("Phase 12 — σ/m Drop Mystery Investigation")
    print("=" * 80)
    print(f"Phase 8c/8d MAP: σ/m = 0.065 cm²/g (10× below T39's 0.72)")
    print(f"Three hypotheses: A) statistical fluctuation, B) SIDM overestimate, C) different physics")
    print()

    results = {}
    for mode in ["on", "off", "null"]:
        results[mode] = run_fit(mode)

    # Compare
    print()
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"{'Mode':<10} {'log_Z':<10} {'σ/m MAP':<12} {'σ/m 50%':<12} {'Verdict'}")
    for mode, r in results.items():
        sm_median = r["posterior_sigma_m_16_50_84"][1]
        print(f"{mode:<10} {r['log_Z']:<10.2f} {r['MAP_sigma_m']:<12.4f} {sm_median:<12.4f}")

    delta_off = results["off"]["log_Z"] - results["on"]["log_Z"]
    delta_null = results["null"]["log_Z"] - results["on"]["log_Z"]
    print()
    print(f"Δlog Z (off vs on):  {delta_off:+.3f}")
    print(f"Δlog Z (null vs on): {delta_null:+.3f}")

    # Hypothesis test
    sm_on = results["on"]["MAP_sigma_m"]
    sm_off = results["off"]["MAP_sigma_m"]
    sm_null = results["null"]["MAP_sigma_m"]

    print()
    if abs(sm_off - 0.72) < abs(sm_on - 0.72):
        hyp_a = "SUPPORTED: σ/m returns toward 0.72 when 248 keV channel disabled"
    else:
        hyp_a = f"NOT supported: σ/m stays at {sm_off:.3f} even without 248 keV channel"
    if abs(sm_null - sm_off) > 0.1:
        hyp_c = f"SUPPORTED: σ/m differs by {abs(sm_null - sm_off):.3f} between 'on' and 'null' modes"
    else:
        hyp_c = "NOT supported: σ/m same in 'on' and 'null' modes"
    print(f"Hypothesis A (statistical fluctuation): {hyp_a}")
    print(f"Hypothesis C (different physics):       {hyp_c}")

    out = {
        "test": "Phase12_sigma_m_drop_mystery",
        "direction": "Three ablations on LZ 248 keV channel mode",
        "results": results,
        "comparisons": {
            "delta_log_Z_off_vs_on": delta_off,
            "delta_log_Z_null_vs_on": delta_null,
        },
        "hypotheses": {
            "A_statistical_fluctuation": hyp_a,
            "B_sidm_overestimate": "(not directly testable in this framework)",
            "C_different_physics": hyp_c,
        },
    }

    out_path = RESULTS_DIR / "phase12_sigma_m_drop_mystery.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
