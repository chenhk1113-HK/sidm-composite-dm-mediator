"""
Three-way Channel 27 peak comparison: placeholder vs compromise vs AMUSE.

GOAL: Find which peak value is most consistent with the 11-channel baseline
by comparing ΔlogZ (penalty vs improvement) at three anchor values:
  - 0.5 cm^2/g  (the original placeholder, hand-tuned)
  - 1.0 cm^2/g  (compromise: 2x above placeholder, 3x below AMUSE)
  - 3.07 cm^2/g (AMUSE-derived)

If ΔlogZ is LEAST negative (or positive) at one of these, that's the
model-consistent anchor.
"""
from __future__ import annotations
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

from config import LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ
from t13_v2_12channel_2025_2026 import loglike_11channel

import ch27_ngc1052_trail_channel as ch27

RESULTS_DIR = Path(
    "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
)
THREE_WAY_PEAKS = [0.5, 1.0, 3.07]  # cm^2/g
ORIGINAL_PEAK = ch27.NGC1052_TRAIL_LOG_SM_PEAK  # save to restore


def run_one(label, loglike_fn, seed=20260912):
    """Run a single dynesty fit."""
    print(f"[three_way] {label} ...", flush=True)

    def loglike(theta):
        return loglike_fn(10 ** theta[0], theta[1])

    def prior_transform(u):
        return np.array([
            LOG_SIGMA_M_RANGE[0] + u[0] * (LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0]),
            A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
        ])

    t0 = time.time()
    import dynesty
    rstate = np.random.default_rng(seed)
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=2, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
        rstate=rstate,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    samples = res.samples
    log_sm = samples[:, 0]
    a = samples[:, 1]

    p16_sm, p50_sm, p84_sm = np.percentile(log_sm, [16, 50, 84])
    p16_a, p50_a, p84_a = np.percentile(a, [16, 50, 84])

    log_sm_at_v_samples = log_sm + a * math.log10(100.0 / 358.0)
    p50_v = float(np.percentile(log_sm_at_v_samples, 50))
    p16_v = float(np.percentile(log_sm_at_v_samples, 16))
    p84_v = float(np.percentile(log_sm_at_v_samples, 84))

    return {
        "label": label, "log_Z": log_Z,
        "median_log_sigma_m_0": float(p50_sm),
        "median_sigma_m_0": float(10 ** p50_sm),
        "p16_sigma_m_0": float(10 ** p16_sm), "p84_sigma_m_0": float(10 ** p84_sm),
        "median_a": float(p50_a), "p16_a": float(p16_a), "p84_a": float(p84_a),
        "median_log_sm_at_v358": p50_v, "p16_log_sm_at_v358": p16_v, "p84_log_sm_at_v358": p84_v,
        "median_sm_at_v358": float(10 ** p50_v),
        "wall_seconds": float(wall),
        "n_samples": int(samples.shape[0]),
    }


def main():
    print("=" * 70)
    print("Three-way Channel 27 peak comparison")
    print("=" * 70)
    print(f"nlive={NLIVE}, dlogz_target={DLOGZ}, seed=20260912")
    print(f"Peaks to test (cm^2/g): {THREE_WAY_PEAKS}")
    print(f"  0.5  = original placeholder (hand-tuned)")
    print(f"  1.0  = compromise (2x above placeholder, 3x below AMUSE)")
    print(f"  3.07 = AMUSE-derived peak")
    print()

    # Baseline: 11-channel (Channel 27 OFF)
    res_baseline = run_one("11-channel (baseline, Channel 27 OFF)", loglike_11channel)
    print(f"  baseline log Z = {res_baseline['log_Z']:.3f}")
    print()

    # Three-way comparison
    results = []
    for peak_cm2 in THREE_WAY_PEAKS:
        log_sm_peak = math.log10(peak_cm2)
        ch27.NGC1052_TRAIL_LOG_SM_PEAK = log_sm_peak

        def loglike_12(sigma_m_0, a):
            return loglike_11channel(sigma_m_0, a) + ch27.loglike_ngc1052_trail(sigma_m_0, a)

        label = f"12-channel (peak={peak_cm2} cm^2/g)"
        res = run_one(label, loglike_12)
        res["peak_cm2_per_g"] = peak_cm2
        res["peak_log10"] = log_sm_peak
        res["delta_log_Z_vs_baseline"] = res["log_Z"] - res_baseline["log_Z"]
        results.append(res)
        print(f"  peak={peak_cm2} cm^2/g  log Z={res['log_Z']:.3f}  "
              f"dlogZ={res['delta_log_Z_vs_baseline']:+.3f}  "
              f"sigma/m_0={res['median_sigma_m_0']:.3f}  "
              f"sigma/m(v=358)={res['median_sm_at_v358']:.3f}")
        print(flush=True)

    # Restore original peak
    ch27.NGC1052_TRAIL_LOG_SM_PEAK = ORIGINAL_PEAK

    # Find best (least negative ΔlogZ)
    best = max(results, key=lambda r: r["delta_log_Z_vs_baseline"])

    # Summary
    print()
    print("=" * 70)
    print("THREE-WAY SUMMARY")
    print("=" * 70)
    print(f"{'Peak (cm²/g)':>15} | {'ΔlogZ':>8} | {'σ/m_0':>10} | {'σ/m(v=358)':>12} | {'verdict':>30}")
    print("-" * 90)
    print(f"{'(none)':>15} | {'---':>8} | {res_baseline['median_sigma_m_0']:>10.3f} | {res_baseline['median_sm_at_v358']:>12.3f} | {'baseline 11ch':>30}")
    for r in results:
        verdict = "BEST (least penalty)" if r is best else "penalty"
        print(f"{r['peak_cm2_per_g']:>15.2f} | {r['delta_log_Z_vs_baseline']:>+8.3f} | {r['median_sigma_m_0']:>10.3f} | {r['median_sm_at_v358']:>12.3f} | {verdict:>30}")

    print()
    print(f"VERDICT: peak = {best['peak_cm2_per_g']} cm^2/g is most model-consistent")
    print(f"  ΔlogZ = {best['delta_log_Z_vs_baseline']:+.3f} (vs AMUSE: {results[2]['delta_log_Z_vs_baseline']:+.3f}, vs placeholder: {results[0]['delta_log_Z_vs_baseline']:+.3f})")

    # Save
    out = {
        "comparison_id": "Channel27_three_way_2026_09_12",
        "date": "2026-09-12",
        "source": "Three-way comparison of placeholder / compromise / AMUSE peak",
        "nlive": NLIVE,
        "dlogz_target": DLOGZ,
        "rstate_seed": 20260912,
        "peaks_tested_cm2_per_g": THREE_WAY_PEAKS,
        "baseline_11channel": res_baseline,
        "three_way_results": results,
        "verdict": {
            "best_peak_cm2_per_g": best["peak_cm2_per_g"],
            "best_delta_log_Z": best["delta_log_Z_vs_baseline"],
            "comparison_to_other_peaks": {
                f"{r['peak_cm2_per_g']}_cm2_per_g": r["delta_log_Z_vs_baseline"]
                for r in results
            },
        },
        "honest_caveats": [
            "AMUSE simulation is N=1024 per halo, ~100x below publication-grade",
            "SIDM kernel is uniform Gaussian perturbation, not Rutherford-like pairwise scattering",
            "Channel 27 width is 1.0 dex (factor-of-10 Gaussian)",
            "Only 3 peaks tested; finer resolution might shift verdict",
        ],
    }
    out_path = RESULTS_DIR / "ch27_three_way_comparison_2026_09_12.json"
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {out_path.relative_to(RESULTS_DIR.parent.parent)}")


if __name__ == "__main__":
    main()