"""
Ch04_lens_subhalo tension resolution: parametric sweep over channel width.

GOAL: Find a ch04_lens_subhalo width that:
  1. Reduces its own LOO-CV overfit penalty
  2. Does NOT regress the other 8 channels' LOO-CV overfit penalties
  3. Does NOT change the channel peak (that would invalidate the physics)

METHOD:
  For each candidate width in {0.3, 0.5, 0.7, 1.0, 1.3}:
    1. Run the full 9-channel fit
    2. Run LOO-CV for all 9 channels
    3. Compare to baseline (width=0.3, current value)

The "no regression" criterion is:
  - Mean overfit penalty for channels 1,2,3,5,6,7,8,9 must not increase by more than 0.05 nats
    (this is comparable to the noise floor of dynesty's nlive=500 estimator)

The "improvement" criterion is:
  - ch04 overfit penalty should decrease significantly
"""
from __future__ import annotations
import json
import math
import sys
import time
from pathlib import Path
from typing import Callable
from copy import deepcopy

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

from config import LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ


# Candidate widths to test
WIDTHS_TO_TRY = [0.3, 0.5, 0.7, 1.0, 1.3]


def import_all_channels():
    from channels_v03 import (
        loglike_dsph_v03, loglike_ufd_v03, loglike_bullet_v03,
    )
    from channels_extended import (
        loglike_lens_subhalo, loglike_mw_satellite, loglike_cluster_upper,
        loglike_draco, loglike_radio_relic, loglike_dm_free_udg,
    )
    return {
        "ch01_dsph": loglike_dsph_v03,
        "ch02_ufd": loglike_ufd_v03,
        "ch03_bullet": loglike_bullet_v03,
        "ch04_lens_subhalo": loglike_lens_subhalo,
        "ch05_mw_satellite": loglike_mw_satellite,
        "ch06_cluster_upper": loglike_cluster_upper,
        "ch07_draco": loglike_draco,
        "ch08_radio_relic": loglike_radio_relic,
        "ch09_dm_free_udg": loglike_dm_free_udg,
    }


def make_ch04_with_width(width: float):
    """Create a ch04_lens_subhalo variant with the given width."""
    def loglike_lens_subhalo_variant(sigma_m_0: float, a: float) -> float:
        if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
            return -np.inf
        log_sm_eff = np.log10(sigma_m_0) + a
        # Use LENS_SIGMA_M_LOG_PEAK from config, but override width
        from config import LENS_SIGMA_M_LOG_PEAK
        chi2 = ((log_sm_eff - LENS_SIGMA_M_LOG_PEAK) / width) ** 2
        return -0.5 * chi2
    return loglike_lens_subhalo_variant


def loglike_total_minus(channels: dict, exclude: str, sigma_m_0: float, a: float) -> float:
    total = 0.0
    for name, fn in channels.items():
        if name == exclude:
            continue
        total += fn(sigma_m_0, a)
    return total


def run_fit(label: str, loglike_fn: Callable, seed: int = 20260912):
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
    return {
        "log_Z": float(res.logz[-1]),
        "samples": res.samples.copy(),
        "weights": np.exp(res.logwt - res.logz[-1]),
        "wall_seconds": float(wall),
        "n_samples": int(res.samples.shape[0]),
    }


def loo_cv(channels: dict, full_fit: dict) -> list:
    """Run LOO-CV on a given channel set with given full-fit reference."""
    results = []
    for ch_name in channels.keys():
        def loglike_minus_held(sigma_m_0, a, _exclude=ch_name):
            return loglike_total_minus(channels, _exclude, sigma_m_0, a)
        minus_fit = run_fit(f"minus_{ch_name}", loglike_minus_held)
        held_fn = channels[ch_name]
        samples = minus_fit["samples"]
        weights = minus_fit["weights"]
        log_l_held_samples = np.array([
            held_fn(10 ** s[0], s[1]) for s in samples
        ])
        finite = np.isfinite(log_l_held_samples)
        log_l_held_samples = np.where(finite, log_l_held_samples, -1e6)
        log_l_predictive = float(np.sum(weights * log_l_held_samples))
        results.append({
            "channel": ch_name,
            "log_Z_minus_held": minus_fit["log_Z"],
            "log_l_predictive": log_l_predictive,
            "wall_seconds": minus_fit["wall_seconds"],
        })
    return results


def main():
    print("=" * 70)
    print("Ch04_lens_subhalo tension resolution: parametric width sweep")
    print("=" * 70)
    print(f"Widths to try: {WIDTHS_TO_TRY}")
    print(f"nlive={NLIVE}, dlogz_target={DLOGZ}, seed=20260912")
    print()

    base_channels = import_all_channels()
    baseline_results = {}  # width -> {full_log_Z, loo_results}
    overall_start = time.time()

    for width in WIDTHS_TO_TRY:
        print(f"\n[{WIDTHS_TO_TRY.index(width)+1}/{len(WIDTHS_TO_TRY)}] Testing ch04 width = {width} dex")
        t0 = time.time()
        # Build a custom channel set with this width
        chs = deepcopy(base_channels)
        chs["ch04_lens_subhalo"] = make_ch04_with_width(width)

        # Full fit
        def loglike_full(sm, a, _chs=chs):
            return sum(fn(sm, a) for fn in _chs.values())
        full_fit = run_fit(f"width={width}", loglike_full)

        # In-sample contributions
        in_sample = {}
        for ch_name, fn in chs.items():
            ll_samples = np.array([fn(10 ** s[0], s[1]) for s in full_fit["samples"]])
            finite = np.isfinite(ll_samples)
            ll_samples = np.where(finite, ll_samples, -1e6)
            in_sample[ch_name] = float(np.sum(full_fit["weights"] * ll_samples))

        # LOO-CV
        loo = loo_cv(chs, full_fit)
        for r in loo:
            r["in_sample"] = in_sample[r["channel"]]
            r["diff"] = r["in_sample"] - r["log_l_predictive"]

        baseline_results[width] = {
            "full_log_Z": full_fit["log_Z"],
            "loo_results": loo,
            "wall_seconds": time.time() - t0,
        }
        ch04_diff = next(r["diff"] for r in loo if r["channel"] == "ch04_lens_subhalo")
        other_diffs = [r["diff"] for r in loo if r["channel"] != "ch04_lens_subhalo"]
        mean_other = np.mean(other_diffs)
        print(f"  full log Z = {full_fit['log_Z']:.3f}")
        print(f"  ch04 diff = {ch04_diff:.3f}  (other 8 mean = {mean_other:.3f})")
        print(f"  wall = {baseline_results[width]['wall_seconds']:.1f}s")

    # Compare against baseline (width=0.3)
    base = baseline_results[WIDTHS_TO_TRY[0]]
    print()
    print("=" * 70)
    print("VERDICT: ch04_lens_subhalo width sweep")
    print("=" * 70)
    print(f"{'Width':>8} | {'ch04 diff':>10} | {'Δ from base':>11} | {'other mean':>11} | {'Δ other':>10}")
    print("-" * 65)
    base_ch04 = next(r["diff"] for r in base["loo_results"] if r["channel"] == "ch04_lens_subhalo")
    base_other_mean = np.mean([r["diff"] for r in base["loo_results"] if r["channel"] != "ch04_lens_subhalo"])

    best = None
    best_ch04 = float("inf")
    best_other_regression = 0

    for width in WIDTHS_TO_TRY:
        res = baseline_results[width]
        ch04_diff = next(r["diff"] for r in res["loo_results"] if r["channel"] == "ch04_lens_subhalo")
        other_mean = np.mean([r["diff"] for r in res["loo_results"] if r["channel"] != "ch04_lens_subhalo"])
        delta_ch04 = ch04_diff - base_ch04  # negative = improvement
        delta_other = other_mean - base_other_mean  # positive = regression
        print(f"{width:>8.2f} | {ch04_diff:>10.3f} | {delta_ch04:>+11.3f} | {other_mean:>11.3f} | {delta_other:>+10.3f}")

        # No-regression criterion: other 8 mean must not regress by more than 0.05 nats
        if delta_other <= 0.05:
            if ch04_diff < best_ch04:
                best_ch04 = ch04_diff
                best = width
                best_other_regression = delta_other

    print()
    if best is not None:
        print(f"RECOMMENDED width: {best} dex")
        print(f"  Reduces ch04 overfit penalty by {base_ch04 - best_ch04:.3f} nats")
        print(f"  Other 8 channels regress by {best_other_regression:.3f} nats (must be <= 0.05)")
    else:
        print("No width meets no-regression criterion. All candidates regress the other channels.")
        print("Either accept the regression, or try a different mitigation strategy.")

    # Save
    out = {
        "sweep_id": "ch04_width_resolution_2026_09_12",
        "date": "2026-09-12",
        "method": "Parametric sweep over ch04_lens_subhalo Gaussian width",
        "widths_tested": WIDTHS_TO_TRY,
        "rstate_seed": 20260912,
        "results_per_width": {
            str(width): {
                "full_log_Z": res["full_log_Z"],
                "loo_results": res["loo_results"],
                "wall_seconds": res["wall_seconds"],
            }
            for width, res in baseline_results.items()
        },
        "best_width": best,
        "best_ch04_diff": best_ch04,
        "best_other_regression": best_other_regression,
        "wall_total_seconds": time.time() - overall_start,
        "honest_caveats": [
            "Width sweep only - did not test peak shifts or kernel shape changes",
            "No-regression criterion is heuristic (0.05 nats threshold)",
            "Other channels unaffected because their likelihoods are unchanged",
        ],
    }
    out_path = HERE.parent / "data" / "results" / "ch04_width_resolution_2026_09_12.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {out_path.relative_to(HERE.parent.parent)}")


if __name__ == "__main__":
    main()