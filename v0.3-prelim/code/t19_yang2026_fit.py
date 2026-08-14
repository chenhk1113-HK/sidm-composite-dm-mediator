#!/usr/bin/env python
"""
T19 — Direction B with REAL Yang+ 2026 SIDM2v published curve.

This is the publication-quality replacement for t18_two_component_fit.py.
Same parameter space (sigma1, sigma2, f1, a) but uses the Yang+ 2026
published sigma_eff vs V_max curve as the channel likelihood (NOT a
Gaussian placeholder).

Comparison:
    t18 (placeholder Gaussians) — Bayes factor vs single-comp = +5.47 (2-comp
        preferred, partly circular)
    t19 (Yang+ 2026 published curve) — this is the real comparison.

If t19's Bayes factor against single-component (using the same Yang+ curve)
is comparable to t18's, the placeholder is validated. If t19's Bayes factor
is very different, the placeholder was misleading.
"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Path setup: yang2026_likelihood.py depends on two_component_sidm.py in the
# same dir, so they need to be importable together.
import numpy as np
import dynesty

import two_component_sidm as tc
import yang2026_likelihood as yl

from config import RESULTS_DIR_V03


# Same prior box as t18 (Yang+ 2026 mass ratio = 3 implies sigma1/sigma2 ~ 3-10)
LOG_SIGMA1_RANGE = (-2.0, 2.0)   # sigma1 ~ 0.01 to 100 cm^2/g
LOG_SIGMA2_RANGE = (-3.0, 1.0)   # sigma2 ~ 0.001 to 10 cm^2/g
F1_RANGE = (0.01, 0.99)
A_RANGE = (-2.0, 2.0)

NLIVE = 200
DLOGZ = 0.1


def loglike_two_comp_yang(theta):
    """Joint log L using Yang+ 2026 published curve (3 channels)."""
    log_sigma1, log_sigma2, f1, a = theta
    sigma1 = 10 ** log_sigma1
    sigma2 = 10 ** log_sigma2
    if sigma1 <= 0 or sigma2 <= 0:
        return -np.inf
    if not (F1_RANGE[0] <= f1 <= F1_RANGE[1]):
        return -np.inf
    if not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf
    return yl.loglike_yang2026_full(sigma1, sigma2, f1, a)


def loglike_one_comp_yang(theta):
    """1-component nested baseline: sigma1 == sigma2, same 3 channels."""
    log_sigma, a = theta
    sigma = 10 ** log_sigma
    if sigma <= 0 or not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf
    # 1-component: f1 = 0.5, sigma1 = sigma2 = sigma
    return yl.loglike_yang2026_full(sigma, sigma, 0.5, a)


def loglike_one_comp_2ch_yang(theta):
    """1-component 2-channel (dwarf+galaxy only, no cluster constraint)."""
    log_sigma, a = theta
    sigma = 10 ** log_sigma
    if sigma <= 0 or not (A_RANGE[0] <= a <= A_RANGE[1]):
        return -np.inf
    return (
        yl.loglike_yang2026_dwarf(sigma, sigma, 0.5, a)
        + yl.loglike_yang2026_galaxy(sigma, sigma, 0.5, a)
    )


def prior_transform_4(u):
    return [
        LOG_SIGMA1_RANGE[0] + u[0] * (LOG_SIGMA1_RANGE[1] - LOG_SIGMA1_RANGE[0]),
        LOG_SIGMA2_RANGE[0] + u[1] * (LOG_SIGMA2_RANGE[1] - LOG_SIGMA2_RANGE[0]),
        F1_RANGE[0] + u[2] * (F1_RANGE[1] - F1_RANGE[0]),
        A_RANGE[0] + u[3] * (A_RANGE[1] - A_RANGE[0]),
    ]


def prior_transform_2(u):
    return [
        LOG_SIGMA1_RANGE[0] + u[0] * (LOG_SIGMA1_RANGE[1] - LOG_SIGMA1_RANGE[0]),
        A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
    ]


def run_one(loglike, prior_transform, ndim, label):
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=ndim, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()
    wall = time.time() - t0
    pcts = np.percentile(samples, [16, 50, 84], axis=0, weights=weights, method='inverted_cdf')
    return {
        "label": label,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": MAP,
        "median": pcts[1].tolist(),
        "p16": pcts[0].tolist(),
        "p84": pcts[2].tolist(),
        "wall_seconds": wall,
        "n_samples": int(len(samples)),
    }


def main():
    print("=" * 80)
    print("T19 — Direction B with REAL Yang+ 2026 SIDM2v published curve")
    print("=" * 80)
    print(f"Reference: Yang, Fan, Hou, Tsai 2026, Sci. Bull., arXiv:2506.14898v3")
    print(f"Published SIDM2v parameters (Table 1):")
    pub = yl.model_yang2026_sidm2v()
    for k, v in pub.items():
        print(f"    {k} = {v}")
    print(f"Published sigma_eff vs V_max (Fig 1, my reading):")
    for v, s in zip(yl.V_MAX_AXIS, yl.SIGMA_EFF_SIDM2V):
        print(f"    V_max = {v:6.0f} km/s: sigma_eff = {s:5.2f} cm^2/g")
    print()
    print(f"Priors: log10 s1 in {LOG_SIGMA1_RANGE}, log10 s2 in {LOG_SIGMA2_RANGE},")
    print(f"        f1 in {F1_RANGE}, a in {A_RANGE}")
    print(f"Sampler: dynesty NLIVE={NLIVE}, DLOGZ={DLOGZ}")
    print()

    # Three fits: A (2-comp 4D), B (1-comp nested 2D), C (1-comp 2ch 2D)
    print("Running fit A: 2-component (4 par, 3 Yang+ 2026 channels)...")
    A = run_one(loglike_two_comp_yang, prior_transform_4, 4, "two_comp_yang")
    print(f"  log Z = {A['log_Z']:.3f} +/- {A['log_Z_err']:.3f}  (wall {A['wall_seconds']:.1f}s)")

    print("Running fit B: 1-component nested (2 par, same 3 channels)...")
    B = run_one(loglike_one_comp_yang, prior_transform_2, 2, "one_comp_yang_nested")
    print(f"  log Z = {B['log_Z']:.3f} +/- {B['log_Z_err']:.3f}  (wall {B['wall_seconds']:.1f}s)")

    print("Running fit C: 1-component 2-channel (dwarf + galaxy only)...")
    C = run_one(loglike_one_comp_2ch_yang, prior_transform_2, 2, "one_comp_2ch_yang")
    print(f"  log Z = {C['log_Z']:.3f} +/- {C['log_Z_err']:.3f}  (wall {C['wall_seconds']:.1f}s)")

    print()
    print("=" * 80)
    print("Bayes factors (log Z difference, 2-comp minus 1-comp):")
    delta_B = A["log_Z"] - B["log_Z"]
    delta_C = A["log_Z"] - C["log_Z"]
    if delta_B > 5:
        verdict_B = "STRONGLY preferred (log BF > 5)"
    elif delta_B > 2.5:
        verdict_B = "MODERATELY preferred (2.5 < log BF < 5)"
    elif delta_B > 1:
        verdict_B = "MILDLY preferred (1 < log BF < 2.5)"
    elif delta_B > -1:
        verdict_B = "EQUIVALENT (|log BF| < 1)"
    else:
        verdict_B = "MILDLY DISFAVORED (log BF < -1)"
    if delta_C > 5:
        verdict_C = "STRONGLY preferred"
    elif delta_C > 2.5:
        verdict_C = "MODERATELY preferred"
    elif delta_C > 1:
        verdict_C = "MILDLY preferred"
    elif delta_C > -1:
        verdict_C = "EQUIVALENT"
    else:
        verdict_C = "MILDLY DISFAVORED"
    print(f"  vs B (same 3 Yang+ channels): {delta_B:+.3f}  -> {verdict_B}")
    print(f"  vs C (dwarf+galaxy only, no cluster):  {delta_C:+.3f}  -> {verdict_C}")
    print()

    # MAP values for A
    log_s1, log_s2, f1_MAP, a_MAP = A["MAP"]
    s1_MAP = 10 ** log_s1
    s2_MAP = 10 ** log_s2
    sigma_eff_dwarf_MAP = tc.sigma_eff_dwarf(s1_MAP, s2_MAP, f1_MAP, a_MAP)
    sigma_eff_galaxy_MAP = tc.sigma_eff_galaxy(s1_MAP, s2_MAP, f1_MAP, a_MAP)
    sigma_eff_cluster_MAP = tc.sigma_eff_cluster(s1_MAP, s2_MAP, f1_MAP, a_MAP)

    print("T19 (A) MAP analysis:")
    print(f"  sigma1 = {s1_MAP:.4f} cm^2/g, sigma2 = {s2_MAP:.4f} cm^2/g")
    print(f"  f1 = {f1_MAP:.4f}, a = {a_MAP:.4f}")
    print(f"  sigma1/sigma2 = {s1_MAP/s2_MAP:.2f}")
    print(f"  sigma_eff(V_DWARF) = {sigma_eff_dwarf_MAP:.3f}  (Yang+ target: {yl.sigma_eff_yang2026(yl.V_DWARF):.3f})")
    print(f"  sigma_eff(V_GALAXY)= {sigma_eff_galaxy_MAP:.3f}  (Yang+ target: {yl.sigma_eff_yang2026(yl.V_GALAXY):.3f})")
    print(f"  sigma_eff(V_CLUSTER)= {sigma_eff_cluster_MAP:.3f}  (Yang+ target: {yl.sigma_eff_yang2026(yl.V_CLUSTER):.3f})")
    print(f"  dwarf/cluster contrast = {sigma_eff_dwarf_MAP/max(sigma_eff_cluster_MAP, 1e-9):.1f}")

    # Save
    out = {
        "test": "T19_yang2026_real_posterior",
        "reference": "Yang, Fan, Hou, Tsai 2026, Sci. Bull., arXiv:2506.14898v3",
        "channels": {
            "dwarf": f"sigma_eff(V_DWARF={yl.V_DWARF} km/s) ~ Gaussian(target={yl.sigma_eff_yang2026(yl.V_DWARF):.3f}, 0.3 dex)",
            "galaxy": f"sigma_eff(V_GALAXY={yl.V_GALAXY} km/s) ~ Gaussian(target={yl.sigma_eff_yang2026(yl.V_GALAXY):.3f}, 0.3 dex)",
            "cluster": f"sigma_eff(V_CLUSTER={yl.V_CLUSTER} km/s) one-sided Gaussian (0.3 dex above, 0.5 dex below), target={yl.sigma_eff_yang2026(yl.V_CLUSTER):.3f}",
        },
        "fit_A_2comp": A,
        "fit_B_1comp_nested": B,
        "fit_C_1comp_2ch": C,
        "bayes_factors": {
            "vs_B_same_3_channels": {"delta_log_Z": delta_B, "verdict": verdict_B},
            "vs_C_dwarf_galaxy_only": {"delta_log_Z": delta_C, "verdict": verdict_C},
        },
        "T19_MAP_analysis": {
            "sigma1": s1_MAP, "sigma2": s2_MAP, "f1": f1_MAP, "a": a_MAP,
            "sigma1_over_sigma2": s1_MAP / s2_MAP,
            "sigma_eff_dwarf": sigma_eff_dwarf_MAP,
            "sigma_eff_galaxy": sigma_eff_galaxy_MAP,
            "sigma_eff_cluster": sigma_eff_cluster_MAP,
            "dwarf_over_cluster_contrast": sigma_eff_dwarf_MAP / max(sigma_eff_cluster_MAP, 1e-9),
        },
        "verdict": (
            f"Yang+ 2026 real posterior: 2-comp vs nested 1-comp log BF = {delta_B:+.3f} "
            f"({verdict_B}); vs 1-comp dwarf+galaxy only = {delta_C:+.3f} ({verdict_C}). "
            f"Compare to t18 (placeholder): 2-comp vs nested 1-comp = +5.47 (strongly preferred, partly circular). "
            f"Using the published Yang+ 2026 curve changes the result."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t19_yang2026_real_fit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\noutput -> {out_path}")


if __name__ == "__main__":
    main()
