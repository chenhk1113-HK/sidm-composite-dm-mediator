"""
Phase 18 — Direct m_chi Comparison (Option B from prior menu)

Tests whether the structural inconsistency found in Phase 17
(g_D=0.16 breaks SIDM, g_D=0.7-0.8 breaks Fermi) is resolved
at m_chi = 5 or 10 GeV vs 45 GeV.

Method:
  Run the same 5D fit at fixed m_chi = 5, 10, 45 GeV with all
  other priors identical. Compare:
    - sigma/m MAP (does the drop persist?)
    - g_D MAP (does the Fermi limit still bind at 5 GeV?)
    - tau_core (does collapse happen in the age of the universe?)
    - eta_DM/eta_B (is asymmetric DM natural?)

Builds on Phase 14 (m_phi comparison) — same framework, swap the
free parameter.
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
from t40_yukawa_sigma_m import sigma_m_cm2_per_g
from phase8c_majorana_reframe_joint_fit import (
    sigma_SI_majorana_cm2, sigma_inel_majorana_cm2,
    LZ_248_KEV_EXPOSURE_TONNE_YEAR, LZ_248_KEV_RATE_TARGET,
    LZ_248_KEV_RATE_SIGMA, LZ_EVENT_RATE_COEFF, DELTA_KEV_FIXED,
)
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s
from phase17_core_collapse_gD import tau_core_collapse_gyr
from phase16_asymmetric_dm_ratio import eta_ratio

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# FIXED m_phi (de Lima value, Phase 8d choice)
M_PHI_MEV_FIXED = 200.0

LOG_EPSILON_RANGE = (-12.0, -3.0)
LOG_G_D_RANGE = (-2.0, 0.5)
LOG_F_H_RANGE = (-3.0, 0.0)


def loglike_mchi(theta, m_chi_GeV: float):
    """
    5D loglike with m_chi FIXED externally.

    theta = [log_sigma_m_0, a, log_epsilon, log_g_D, log_f_H]
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

    # 1. LZ elastic (Majorana reframe)
    sigma_SI_M = sigma_SI_majorana_cm2(epsilon, g_D)
    ll_lz_elastic = loglike_lz_real(m_chi_GeV, sigma_SI_M)

    # 2. LZ 248 keV (Majorana inelastic)
    sigma_inel = sigma_inel_majorana_cm2(epsilon, g_D, f_H, m_chi_GeV=m_chi_GeV, m_A_prime_MeV=M_PHI_MEV_FIXED)
    n_pred = sigma_inel * LZ_EVENT_RATE_COEFF * LZ_248_KEV_EXPOSURE_TONNE_YEAR
    n_pred = np.clip(n_pred, 1e-6, 1e6)
    delta = (n_pred - LZ_248_KEV_RATE_TARGET) / LZ_248_KEV_RATE_SIGMA
    ll_lz_248 = -0.5 * delta**2

    # 3. Fermi (α = g_D²/4π)
    sigma_v = sigma_v_majorana_cm3_per_s(g_D)
    ll_fermi = loglike_fermi_real(m_chi_GeV, sigma_v, channel="bb", use_J_prior=True)

    # 4. SIDM (uses sigma_m_0 at v=100, m_chi needed for some channels)
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


def run_fit(m_chi_GeV: float) -> dict:
    """Run 5D fit with m_chi fixed."""
    print(f"\n--- RUN: m_chi = {m_chi_GeV} GeV ---")
    t0 = time.time()

    def loglike(theta):
        return loglike_mchi(theta, m_chi_GeV)

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
    gd_q = [10**q for q in weighted_quantiles(samples[:, 3], weights, [0.16, 0.5, 0.84])]

    # Compute tau_core at MAP
    sm_at_map = 10**MAP[0]
    tau = tau_core_collapse_gyr(sm_at_map)

    # Compute eta ratio
    eta = eta_ratio(m_chi_GeV)

    print(f"  log_Z = {log_Z:.3f}, wall = {wall:.1f}s")
    print(f"  MAP: log_sigma_m = {MAP[0]:.3f} → σ/m = {sm_at_map:.3f} cm²/g")
    print(f"  Posterior 16/50/84%: σ/m = {sm_q[0]:.3f} / {sm_q[1]:.3f} / {sm_q[2]:.3f}")
    print(f"  Posterior 16/50/84%: g_D = {gd_q[0]:.3f} / {gd_q[1]:.3f} / {gd_q[2]:.3f}")
    print(f"  τ_core = {tau:.1f} Gyr, η_DM/η_B = {eta:.3f}")

    return {
        "m_chi_GeV": m_chi_GeV,
        "log_Z": log_Z,
        "MAP_log_sigma_m": MAP[0],
        "MAP_sigma_m": sm_at_map,
        "MAP_g_D": 10**MAP[3],
        "posterior_sigma_m_16_50_84": sm_q,
        "posterior_g_D_16_50_84": gd_q,
        "tau_core_Gyr": tau,
        "eta_DM_over_eta_B": eta,
        "wall_seconds": wall,
    }


def main():
    print("=" * 80)
    print("Phase 18 — Direct m_chi Comparison")
    print("=" * 80)
    print(f"Test if structural inconsistency (g_D=0.16 vs g_D=0.7-0.8) is resolved at m_chi=5 GeV")
    print(f"m_phi fixed at {M_PHI_MEV_FIXED} MeV (de Lima value)")
    print()

    out = {"test": "Phase18_mchi_comparison",
           "direction": "Quantify m_chi dependence on the Majorana reframe"}

    m_chi_values = [5.0, 10.0, 45.0]
    results = {}
    for m_chi in m_chi_values:
        results[str(int(m_chi))] = run_fit(m_chi)

    # Compare
    print()
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"{'m_chi [GeV]':<14} {'log_Z':<10} {'σ/m MAP':<10} {'g_D MAP':<10} {'τ [Gyr]':<10} {'η/η_B':<10}")
    for label, r in results.items():
        print(f"{label:<14} {r['log_Z']:<10.2f} {r['MAP_sigma_m']:<10.4f} "
              f"{r['MAP_g_D']:<10.4f} {r['tau_core_Gyr']:<10.1f} {r['eta_DM_over_eta_B']:<10.3f}")

    # Test hypothesis: structural inconsistency is resolved at 5 GeV
    sm_5 = results["5"]["MAP_sigma_m"]
    sm_10 = results["10"]["MAP_sigma_m"]
    sm_45 = results["45"]["MAP_sigma_m"]
    gd_5 = results["5"]["MAP_g_D"]
    gd_10 = results["10"]["MAP_g_D"]
    gd_45 = results["45"]["MAP_g_D"]
    tau_5 = results["5"]["tau_core_Gyr"]
    tau_10 = results["10"]["tau_core_Gyr"]
    tau_45 = results["45"]["tau_core_Gyr"]
    eta_5 = results["5"]["eta_DM_over_eta_B"]
    eta_10 = results["10"]["eta_DM_over_eta_B"]
    eta_45 = results["45"]["eta_DM_over_eta_B"]

    print()
    print("=" * 80)
    print("HYPOTHESIS TESTS")
    print("=" * 80)

    # 1. Does the σ/m drop persist at 5 GeV?
    if sm_5 > 0.5:
        verdict_drop = "RESOLVED: σ/m at 5 GeV returns to ~1 (no drop)"
    elif sm_5 > 0.1:
        verdict_drop = f"PARTIAL: σ/m at 5 GeV = {sm_5:.3f} (intermediate)"
    else:
        verdict_drop = f"PERSISTS: σ/m at 5 GeV = {sm_5:.3f} (still dropped)"
    print(f"1. σ/m drop at 5 GeV: {verdict_drop}")

    # 2. Does g_D recover at 5 GeV?
    if gd_5 > 0.5:
        verdict_gd = f"RESOLVED: g_D at 5 GeV = {gd_5:.3f} (SIDM-required range)"
    elif gd_5 > 0.21:
        verdict_gd = f"PARTIAL: g_D at 5 GeV = {gd_5:.3f} (above Fermi limit)"
    else:
        verdict_gd = f"PERSISTS: g_D at 5 GeV = {gd_5:.3f} (Fermi still binds)"
    print(f"2. g_D recovery at 5 GeV: {verdict_gd}")

    # 3. Does core collapse work at 5 GeV?
    if 5 < tau_5 < 30:
        verdict_collapse = f"RESOLVED: τ_core at 5 GeV = {tau_5:.1f} Gyr (collapse happens)"
    elif tau_5 > 100:
        verdict_collapse = f"PERSISTS: τ_core at 5 GeV = {tau_5:.1f} Gyr (no collapse)"
    else:
        verdict_collapse = f"EDGE: τ_core at 5 GeV = {tau_5:.1f} Gyr"
    print(f"3. Core collapse at 5 GeV: {verdict_collapse}")

    # 4. Asymmetric DM natural at 5 GeV?
    if 0.5 < eta_5 < 2.0:
        verdict_eta = f"NATURAL: η/η_B at 5 GeV = {eta_5:.3f} (1:1 transfer)"
    else:
        verdict_eta = f"TUNED: η/η_B at 5 GeV = {eta_5:.3f}"
    print(f"4. Asymmetric DM at 5 GeV: {verdict_eta}")

    # Overall verdict
    n_resolved = sum([
        "RESOLVED" in verdict_drop,
        "RESOLVED" in verdict_gd,
        "RESOLVED" in verdict_collapse,
        "NATURAL" in verdict_eta,
    ])
    print()
    print(f"Resolved at 5 GeV: {n_resolved}/4 criteria")
    if n_resolved >= 3:
        overall = "PROCEED: m_chi = 5 GeV resolves the structural inconsistency"
    elif n_resolved >= 2:
        overall = "PARTIAL: m_chi = 5 GeV partially resolves the inconsistency"
    else:
        overall = "PERSISTS: m_chi = 5 GeV does NOT resolve the structural inconsistency"
    print(f"Overall: {overall}")

    out["results"] = results
    out["hypotheses"] = {
        "sigma_m_drop_at_5GeV": verdict_drop,
        "g_D_recovery_at_5GeV": verdict_gd,
        "core_collapse_at_5GeV": verdict_collapse,
        "asymmetric_dm_at_5GeV": verdict_eta,
    }
    out["n_resolved"] = n_resolved
    out["overall_verdict"] = overall

    out_path = RESULTS_DIR / "phase18_mchi_comparison.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
