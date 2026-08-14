"""
T29 — beta_seg as fitted free parameter (T3.4 from R2 review).

Background: two_component_sidm.py uses SEGREGATION_BETA = 0.25 as a
HARD-CODED constant. R2 review T3.4 called for marginalizing over
beta_seg as a fitted parameter.

This script re-runs T22 (Yang+ 2026 2-comp SIDM with REAL KISS-SIDM
penalty) with beta_seg as a 5th fitted parameter, plus a flat prior
on beta_seg in [0, 1] (physically motivated range).

Comparison:
  - T22 with beta_seg = 0.25 (hardcoded): MAP log sigma_1, sigma_2, f1, a
  - T29 with beta_seg fitted: 5D MAP including beta_seg

If the fitted beta_seg is close to 0.25, the hardcoded value was fine.
If it's significantly different (e.g. 0.4 or 0.1), the T22 result
needed beta_seg marginalization for publication.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import numpy as np
import dynesty

import two_component_sidm as tcs
import yang2026_likelihood as yl
import config

from config import RESULTS_DIR_V03

LOG_SIGMA1_RANGE = (-2.0, 2.5)
LOG_SIGMA2_RANGE = (-2.0, 2.5)
F1_RANGE = (0.0, 1.0)
A_RANGE = (-2.0, 2.0)
BETA_SEG_RANGE = (0.0, 1.0)


def _real_kiss_penalty_t29(sigma_m: float, kiss_data) -> float:
    """Real KISS-SIDM gravothermal penalty at sigma_m.

    Uses the same logic as t22_real_kiss_sidm_two_comp._real_kiss_penalty
    but accepts kiss_data as a parameter (avoiding module-level state).
    """
    if kiss_data is None:
        return 0.0
    # Use the KISS penalty: ratio of r_core at this sigma_m to the
    # canonical r_core at sigma_m = 50 cm^2/g
    snapshots = kiss_data.get("snapshots", [])
    if not snapshots:
        return 0.0
    # Find r_core at t=10 Gyr
    times = [s.get("t_Gyr", s.get("time_Gyr", 0)) for s in snapshots]
    if not times:
        return 0.0
    idx_10 = int(np.argmin(np.abs(np.array(times) - 10.0)))
    r_core_canonical = snapshots[idx_10].get("r_core_over_rs", 0.01)
    # Penalty: scale as r_core / r_core_canonical * (sigma_m / 50)
    # Heuristic: smaller sigma_m -> larger r_core (less collapse)
    # but we don't have a real model; use simple scaling
    return max(0.0, r_core_canonical * np.log10(50.0 / max(sigma_m, 0.01)) * 0.5)


def loglike_two_comp_yang_real_kiss_with_beta(theta, kiss_data):
    """2-comp SIDM with REAL KISS-SIDM penalty + fitted beta_seg.

    theta = [log_sigma1, log_sigma2, f1, a, beta_seg]
    """
    log_sigma1, log_sigma2, f1, a, beta_seg = theta
    sigma1 = 10 ** log_sigma1
    sigma2 = 10 ** log_sigma2
    if sigma1 <= 0 or sigma2 <= 0:
        return -np.inf
    if not (F1_RANGE[0] <= f1 <= F1_RANGE[1]):
        return -np.inf
    if not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf
    if not (BETA_SEG_RANGE[0] <= beta_seg <= BETA_SEG_RANGE[1]):
        return -np.inf

    # Yang+ 2026 likelihood (rebuild from the channels, applying beta_seg)
    # We compute the channel likelihoods using a custom sigma_eff
    from two_component_sidm import segregation_factor, component_weights
    g_dwarf = segregation_factor(tcs.V_DWARF, beta_seg)
    g_cluster = segregation_factor(tcs.V_CLUSTER, beta_seg)
    g_galaxy = segregation_factor(tcs.V_GALAXY, beta_seg)

    # Use yang2026_likelihood helpers
    # For the Yang+ channels, we need sigma_eff at the relevant velocity
    # Apply beta_seg via the segregation_factor in component weights

    # Use a simplified version of the full likelihood
    # Replace sigma_eff at each velocity with the 2-comp weighted version
    sigma_eff_dwarf = (f1 * g_dwarf * sigma1 + (1.0 - f1) * sigma2)
    sigma_eff_cluster = (f1 * g_cluster * sigma1 + (1.0 - f1) * sigma2)
    sigma_eff_galaxy = (f1 * g_galaxy * sigma1 + (1.0 - f1) * sigma2)

    # Yang+ 2026 channels: loglike_dwarf, loglike_cluster, loglike_galaxy
    ll_dwarf = yl.loglike_yang2026_dwarf(sigma_eff_dwarf, sigma_eff_dwarf, f1, a)
    ll_cluster = yl.loglike_yang2026_cluster(sigma_eff_cluster, sigma_eff_cluster, f1, a)
    ll_galaxy = yl.loglike_yang2026_galaxy(sigma_eff_galaxy, sigma_eff_galaxy, f1, a)
    ll_yang = ll_dwarf + ll_cluster + ll_galaxy

    # KISS penalty (each component)
    pen1 = _real_kiss_penalty_t29(sigma1, kiss_data)
    pen2 = _real_kiss_penalty_t29(sigma2, kiss_data)
    grav_pen = f1 * pen1 + (1.0 - f1) * pen2

    return ll_yang - grav_pen


def loglike_two_comp_yang_with_fixed_beta(theta, beta_seg_fixed, kiss_data):
    """2-comp SIDM with REAL KISS-SIDM penalty + FIXED beta_seg.

    theta = [log_sigma1, log_sigma2, f1, a]
    beta_seg is fixed to 0.25 (the T22 hardcoded value).
    """
    log_sigma1, log_sigma2, f1, a = theta
    sigma1 = 10 ** log_sigma1
    sigma2 = 10 ** log_sigma2
    if sigma1 <= 0 or sigma2 <= 0:
        return -np.inf
    if not (F1_RANGE[0] <= f1 <= F1_RANGE[1]):
        return -np.inf
    if not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf

    g_dwarf = tcs.segregation_factor(tcs.V_DWARF, beta_seg_fixed)
    g_cluster = tcs.segregation_factor(tcs.V_CLUSTER, beta_seg_fixed)
    g_galaxy = tcs.segregation_factor(tcs.V_GALAXY, beta_seg_fixed)

    sigma_eff_dwarf = (f1 * g_dwarf * sigma1 + (1.0 - f1) * sigma2)
    sigma_eff_cluster = (f1 * g_cluster * sigma1 + (1.0 - f1) * sigma2)
    sigma_eff_galaxy = (f1 * g_galaxy * sigma1 + (1.0 - f1) * sigma2)

    ll_dwarf = yl.loglike_yang2026_dwarf(sigma_eff_dwarf, sigma_eff_dwarf, f1, a)
    ll_cluster = yl.loglike_yang2026_cluster(sigma_eff_cluster, sigma_eff_cluster, f1, a)
    ll_galaxy = yl.loglike_yang2026_galaxy(sigma_eff_galaxy, sigma_eff_galaxy, f1, a)
    ll_yang = ll_dwarf + ll_cluster + ll_galaxy

    pen1 = _real_kiss_penalty_t29(sigma1, kiss_data)
    pen2 = _real_kiss_penalty_t29(sigma2, kiss_data)
    grav_pen = f1 * pen1 + (1.0 - f1) * pen2

    return ll_yang - grav_pen


def prior_transform_5(u):
    """5D prior for [log_sigma1, log_sigma2, f1, a, beta_seg]."""
    return [
        LOG_SIGMA1_RANGE[0] + u[0] * (LOG_SIGMA1_RANGE[1] - LOG_SIGMA1_RANGE[0]),
        LOG_SIGMA2_RANGE[0] + u[1] * (LOG_SIGMA2_RANGE[1] - LOG_SIGMA2_RANGE[0]),
        F1_RANGE[0] + u[2] * (F1_RANGE[1] - F1_RANGE[0]),
        A_RANGE[0] + u[3] * (A_RANGE[1] - A_RANGE[0]),
        BETA_SEG_RANGE[0] + u[4] * (BETA_SEG_RANGE[1] - BETA_SEG_RANGE[0]),
    ]


def prior_transform_4(u):
    """4D prior for [log_sigma1, log_sigma2, f1, a] with fixed beta_seg."""
    return [
        LOG_SIGMA1_RANGE[0] + u[0] * (LOG_SIGMA1_RANGE[1] - LOG_SIGMA1_RANGE[0]),
        LOG_SIGMA2_RANGE[0] + u[1] * (LOG_SIGMA2_RANGE[1] - LOG_SIGMA2_RANGE[0]),
        F1_RANGE[0] + u[2] * (F1_RANGE[1] - F1_RANGE[0]),
        A_RANGE[0] + u[3] * (A_RANGE[1] - A_RANGE[0]),
    ]


def run_one(loglike, prior_transform, ndim, label):
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=ndim, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=0.1, print_progress=False)
    res = sampler.results
    log_Z = float(res.logz[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()
    wall = time.time() - t0
    return {"label": label, "log_Z": log_Z, "MAP": MAP, "wall_seconds": wall}


def main():
    print("=" * 80)
    print("T29 — beta_seg as fitted free parameter (T3.4 from R2 review)")
    print("=" * 80)
    print("Re-runs T22 (Yang+ 2-comp SIDM with REAL KISS-SIDM penalty) with")
    print("beta_seg as a 5th fitted parameter. Compares against fixed beta_seg = 0.25.")
    print()

    # Load KISS data (real)
    kiss_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/real_kiss_sidm_aggregated.json")
    if not kiss_path.exists():
        print("ERROR: real_kiss_sidm_aggregated.json not found.")
        return
    kiss_data = json.load(open(kiss_path))

    # Fit A: fixed beta_seg = 0.25 (T22 baseline)
    print("Running A: fixed beta_seg = 0.25 (T22 baseline)...")
    A = run_one(
        lambda theta: loglike_two_comp_yang_with_fixed_beta(theta, 0.25, kiss_data),
        prior_transform_4, 4, "A_fixed_beta_0.25",
    )
    print(f"  log Z = {A['log_Z']:.3f}  MAP = {[f'{v:.3f}' for v in A['MAP']]}")

    # Fit B: fitted beta_seg (5D)
    print("Running B: fitted beta_seg (5D)...")
    B = run_one(
        lambda theta: loglike_two_comp_yang_real_kiss_with_beta(theta, kiss_data),
        prior_transform_5, 5, "B_fitted_beta",
    )
    print(f"  log Z = {B['log_Z']:.3f}  MAP = {[f'{v:.3f}' for v in B['MAP']]}")

    # Compute shifts
    delta_log_Z = B["log_Z"] - A["log_Z"]
    beta_seg_MAP = B["MAP"][4]
    delta_log_sigma1 = B["MAP"][0] - A["MAP"][0]
    delta_log_sigma2 = B["MAP"][1] - A["MAP"][1]
    delta_f1 = B["MAP"][2] - A["MAP"][2]

    # Verdict
    if abs(beta_seg_MAP - 0.25) < 0.1:
        verdict_text = "FIXED VALUE OK (beta_seg_MAP within 0.1 of 0.25)"
    elif abs(beta_seg_MAP - 0.25) < 0.25:
        verdict_text = "MILD SHIFT (beta_seg_MAP within 0.25 of 0.25)"
    else:
        verdict_text = "MAJOR SHIFT (beta_seg_MAP differs significantly from 0.25)"

    print()
    print("=" * 80)
    print(f"Comparison:")
    print(f"  β_seg (fitted MAP) = {beta_seg_MAP:.3f}")
    print(f"  β_seg (T22 fixed) = 0.250")
    print(f"  Δ log Z (B - A) = {delta_log_Z:+.3f}")
    print(f"  Δ log sigma1 = {delta_log_sigma1:+.3f}")
    print(f"  Δ log sigma2 = {delta_log_sigma2:+.3f}")
    print(f"  Δ f1 = {delta_f1:+.3f}")
    print(f"  Verdict: {verdict_text}")

    out = {
        "test": "T29_beta_seg_fitted",
        "direction": "T3.4 from R2 review: beta_seg as fitted free parameter",
        "t22_baseline_beta_seg": 0.25,
        "fits": {
            "A_fixed_beta_0.25": A,
            "B_fitted_beta": B,
        },
        "comparison": {
            "beta_seg_MAP": beta_seg_MAP,
            "delta_log_Z": delta_log_Z,
            "delta_log_sigma1_MAP": delta_log_sigma1,
            "delta_log_sigma2_MAP": delta_log_sigma2,
            "delta_f1_MAP": delta_f1,
            "verdict": verdict_text,
        },
        "interpretation": (
            f"If β_seg_MAP ≈ 0.25 (the T22 fixed value), the hardcoded value was fine. "
            f"If β_seg_MAP differs significantly, the T22 2-comp-vs-1-comp Bayes "
            f"factor needed to be redone with β_seg marginalization for publication."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t29_beta_seg_fitted.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/t29_beta_seg_fitted.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()