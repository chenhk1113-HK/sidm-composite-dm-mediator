"""
Sensitivity sweep over Channel 27 peak value.

GOAL: Map out how the posterior responds to the choice of sigma/m peak.
With the AMUSE-derived peak at 3.07 cm^2/g, the ablation shows delta_log_Z
is -0.898 (channel penalizes fit). Is this a fundamental tension, or does it
depend on where exactly we put the peak?

METHOD:
Run 4 ablations with peaks {1.0, 2.0, 3.0, 5.0} cm^2/g and compare:
- median sigma/m_0 (does posterior shift toward peak?)
- delta log Z (does the channel improve or penalize?)
- implied sigma/m(v=358) (does the model converge on a velocity-scale value?)

This addresses: "is the AMUSE peak (3.07) the right value, or is it the
particular choice of 3.07 that creates the tension?"
"""
from __future__ import annotations
import json
import math
import os
import sys
import time
import warnings
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
PEAKS_TO_TRY = [1.0, 2.0, 3.0, 5.0]  # cm^2/g at v=358 km/s
ORIGINAL_PEAK = ch27.NGC1052_TRAIL_LOG_SM_PEAK  # save to restore


def loglike_with_peak(sigma_m_0, a, log_sm_peak):
    """Like loglike_ngc1052_trail but with caller-specified peak."""
    return ch27.loglike_ngc1052_trail.__wrapped__(sigma_m_0, a, include_in_fit=True) if False else None


def run_one(label, loglike_fn, seed=20260912):
    """Run a single dynesty fit."""
    print(f"[sensitivity] {label} ...", flush=True)

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
    weights = np.exp(res.logwt - res.logz[-1])
    log_sm = samples[:, 0]
    a = samples[:, 1]

    p16_sm, p50_sm, p84_sm = np.percentile(log_sm, [16, 50, 84])
    p16_a, p50_a, p84_a = np.percentile(a, [16, 50, 84])

    # Compute weighted implied sigma/m(v=358)
    # log_sm_at_v = log10(sigma/m_0) + a * log10(100/358)
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
    print("Channel 27 peak sensitivity sweep — sigma/m at v=358")
    print("=" * 70)
    print(f"nlive={NLIVE}, dlogz_target={DLOGZ}")
    print(f"Peaks to test (cm^2/g): {PEAKS_TO_TRY}")
    print(f"Original (AMUSE-derived) peak: 10^{ch27.NGC1052_TRAIL_LOG_SM_PEAK:.3f} = {10**ch27.NGC1052_TRAIL_LOG_SM_PEAK:.3f} cm^2/g")
    print()

    # Baseline: 11-channel (Channel 27 OFF)
    res_baseline = run_one("11-channel (baseline, Channel 27 OFF)", loglike_11channel)
    print(f"  baseline log Z = {res_baseline['log_Z']:.3f}")
    print()

    # Sensitivity sweep over peak values
    results = []
    for peak_cm2 in PEAKS_TO_TRY:
        log_sm_peak = math.log10(peak_cm2)
        # Monkey-patch the channel's peak for this run
        ch27.NGC1052_TRAIL_LOG_SM_PEAK = log_sm_peak

        def loglike_12(sigma_m_0, a):
            return loglike_11channel(sigma_m_0, a) + ch27.loglike_ngc1052_trail(sigma_m_0, a)

        label = f"12-channel (peak={peak_cm2:.1f} cm^2/g)"
        res = run_one(label, loglike_12)
        res["peak_cm2_per_g"] = peak_cm2
        res["peak_log10"] = log_sm_peak
        res["delta_log_Z_vs_baseline"] = res["log_Z"] - res_baseline["log_Z"]
        results.append(res)
        print(f"  peak={peak_cm2:.1f} cm^2/g  log Z={res['log_Z']:.3f}  "
              f"dlogZ={res['delta_log_Z_vs_baseline']:+.3f}  "
              f"median sigma/m_0={res['median_sigma_m_0']:.3f}  "
              f"implied sigma/m(v=358)={res['median_sm_at_v358']:.3f}")
        print(flush=True)

    # Restore original peak
    ch27.NGC1052_TRAIL_LOG_SM_PEAK = ORIGINAL_PEAK

    # Summary table
    print()
    print("=" * 70)
    print("SENSITIVITY SUMMARY")
    print("=" * 70)
    print(f"{'Peak (cm²/g)':>15} | {'ΔlogZ':>8} | {'σ/m_0 median':>14} | {'σ/m(v=358)':>13}")
    print("-" * 70)
    print(f"{'(none)':>15} | {'---':>8} | {res_baseline['median_sigma_m_0']:>14.3f} | {res_baseline['median_sm_at_v358']:>13.3f}  (baseline 11ch)")
    for r in results:
        print(f"{r['peak_cm2_per_g']:>15.1f} | {r['delta_log_Z_vs_baseline']:>+8.3f} | {r['median_sigma_m_0']:>14.3f} | {r['median_sm_at_v358']:>13.3f}")

    # Save
    out = {
        "sweep_id": "Channel27_peak_sensitivity_2026_09_12",
        "date": "2026-09-12",
        "source": "AMUSE-ph4 bullet-dwarf simulation peak (3.07 cm^2/g) + sensitivity sweep",
        "nlive": NLIVE,
        "dlogz_target": DLOGZ,
        "rstate_seed": 20260912,
        "peaks_tested_cm2_per_g": PEAKS_TO_TRY,
        "baseline_11channel": res_baseline,
        "sensitivity_results": results,
        "honest_caveats": [
            "AMUSE simulation is N=1024 per halo, ~100x below publication-grade",
            "SIDM kernel is uniform Gaussian perturbation, not Rutherford-like pairwise scattering",
            "Channel 27 width is 1.0 dex; finer peaks would need width reduction",
            "Sensitivity sweep at 4 peak values; not exhaustive",
        ],
    }
    out_path = RESULTS_DIR / "ch27_peak_sensitivity_2026_09_12.json"
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {out_path.relative_to(RESULTS_DIR.parent.parent)}")


if __name__ == "__main__":
    main()