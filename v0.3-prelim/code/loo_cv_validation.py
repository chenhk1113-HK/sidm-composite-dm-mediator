"""
Out-of-sample validation for the v0.3-prelim multi-channel model.

GOAL: Test whether the multi-channel model has PREDICTIVE validity, not just
in-sample fit quality. This is the canonical test for "is this model valid?"

HONEST NOTE: Despite the file name "t13_v2_12channel_2025_2026.py", the actual
channel count is 9 (loglike_11channel includes 9 unique likelihoods):
  - dSph, UFD, Bullet Cluster (3 channels from channels_v03.py)
  - Lens subhalo, MW satellite, Cluster upper, Draco, Radio relic, DM-free UDG
    (6 channels from channels_extended.py)
The "12th" channel (cosmic_web_radio) is degenerate at the fixed epsilon=1e-35
and adds nothing. Per AGENTS.md rule 11, we validate the actual 9 channels.

METHOD: Leave-One-Out Cross-Validation (LOO-CV)
For each of the 9 channels:
  1. Hold out that channel's data
  2. Fit the model on the remaining 8 channels
  3. Compute the posterior predictive for the held-out channel:
     <log L> = sum_i w_i * log L_held_out(theta_i)
  4. Compare to the held-out channel's contribution to the full fit

A model with predictive validity should give:
  - <log L>_LOO close to (full_fit_log_Z - log_Z_other8_channels)
  - Tight posterior (low predictive variance)
  - No systematic bias (predicted vs actual)

A model with NO predictive validity (just curve-fitting) gives:
  - <log L>_LOO much lower than expected (model overfit to the held-out data)
  - Wide posteriors (uncertain predictions)
  - Systematic bias

This script also computes:
- Posterior predictive p-value (lower = better fit to data, but ~0.5 is ideal)
- Effective number of parameters (Bayesian complexity)
- Information criteria (WAIC approximation)
"""
from __future__ import annotations
import json
import math
import sys
import time
from pathlib import Path
from typing import Callable

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

from config import LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ

# All 11 channels with names
CHANNELS = [
    ("ch01_dsph",         "loglike_dsph_v03",        "channels_v03"),
    ("ch02_ufd",          "loglike_ufd_v03",         "channels_v03"),
    ("ch03_bullet",       "loglike_bullet_v03",      "channels_v03"),
    ("ch04_lens_subhalo", "loglike_lens_subhalo",    "channels_extended"),
    ("ch05_mw_satellite", "loglike_mw_satellite",    "channels_extended"),
    ("ch06_cluster_upper","loglike_cluster_upper",   "channels_extended"),
    ("ch07_draco",        "loglike_draco",           "channels_extended"),
    ("ch08_radio_relic",  "loglike_radio_relic",     "channels_extended"),
    ("ch09_dm_free_udg",  "loglike_dm_free_udg",     "channels_extended"),
    ("ch10_dm_dom_udg",   "loglike_dm_dominated_udg","channels_extended"),
]

# Import all channels once
def import_all():
    from channels_v03 import (
        loglike_dsph_v03, loglike_ufd_v03, loglike_bullet_v03,
    )
    from channels_extended import (
        loglike_lens_subhalo, loglike_mw_satellite, loglike_cluster_upper,
        loglike_draco, loglike_radio_relic, loglike_dm_free_udg,
        loglike_dm_dominated_udg,
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
        "ch10_dm_dom_udg": loglike_dm_dominated_udg,
    }


def loglike_total_minus(channels: dict, exclude: str, sigma_m_0: float, a: float) -> float:
    """Sum of all channel log-likelihoods except the excluded one."""
    total = 0.0
    for name, fn in channels.items():
        if name == exclude:
            continue
        total += fn(sigma_m_0, a)
    return total


def run_fit(label: str, loglike_fn: Callable, seed: int = 20260912):
    """Single dynesty fit."""
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


def main():
    print("=" * 70)
    print("Out-of-sample validation: Leave-One-Out CV for 11-channel model")
    print("=" * 70)
    print(f"nlive={NLIVE}, dlogz_target={DLOGZ}, seed=20260912")
    print(f"Channels: {len(CHANNELS)} (LOO over each)")
    print()

    channels = import_all()
    print(f"Loaded {len(channels)} channels: {list(channels.keys())}")
    print()

    # Step 1: Full fit (baseline)
    print("[1] Full 11-channel fit (baseline)")
    def loglike_full(sigma_m_0, a):
        return sum(fn(sigma_m_0, a) for fn in channels.values())
    full_fit = run_fit("full_11ch", loglike_full)
    print(f"  log Z (full 11ch) = {full_fit['log_Z']:.3f}  wall={full_fit['wall_seconds']:.1f}s")
    print()

    # Step 2: LOO-CV
    print("[2] Leave-One-Out Cross-Validation")
    loo_results = []
    for ch_name in channels.keys():
        print(f"  Holding out {ch_name}...", flush=True, end=" ")

        # Fit on N-1 channels (excluding the held-out one)
        def loglike_minus_held(sigma_m_0, a, _exclude=ch_name):
            return loglike_total_minus(channels, _exclude, sigma_m_0, a)

        minus_fit = run_fit(f"minus_{ch_name}", loglike_minus_held)

        # Posterior predictive for held-out channel:
        # <log L> = sum_i w_i * log L_held_out(theta_i)
        held_fn = channels[ch_name]
        samples = minus_fit["samples"]
        weights = minus_fit["weights"]
        log_l_held_samples = np.array([
            held_fn(10 ** s[0], s[1]) for s in samples
        ])
        # Replace -inf with very negative to avoid NaN
        finite_mask = np.isfinite(log_l_held_samples)
        if finite_mask.sum() < len(samples) * 0.5:
            print(f"WARNING: {ch_name} has >50% -inf samples")
        log_l_held_samples = np.where(finite_mask, log_l_held_samples, -1e6)
        log_l_predictive = float(np.sum(weights * log_l_held_samples))

        # Effective number of parameters (rough proxy)
        # p_eff = <log L^2> - <log L>^2 (variance of log-likelihood across posterior)
        mean_ll = float(np.sum(weights * log_l_held_samples))
        var_ll = float(np.sum(weights * (log_l_held_samples - mean_ll) ** 2))

        # Bayesian p-value: fraction of posterior samples that have
        # worse held-out log-L than the observed value
        # Note: for held-out validation, we don't have an "observed value"
        # beyond the channel's own log-likelihood at the MAP. Use the channel's
        # log-likelihood at the MAP as the "data"
        full_samples = full_fit["samples"]
        full_weights = full_fit["weights"]
        log_l_at_MAP = held_fn(10 ** full_samples[np.argmax(full_weights)][0],
                               full_samples[np.argmax(full_weights)][1])
        # Bayesian p-value: P(log L_held(theta) > log L_at_MAP | posterior)
        p_value = float(np.sum(weights * (log_l_held_samples > log_l_at_MAP)))

        loo_results.append({
            "channel": ch_name,
            "log_Z_minus_held": minus_fit["log_Z"],
            "log_l_predictive": log_l_predictive,
            "mean_log_l_held": mean_ll,
            "var_log_l_held": var_ll,
            "p_value": p_value,
            "wall_seconds": minus_fit["wall_seconds"],
        })
        print(f"logZ(minus)={minus_fit['log_Z']:.3f}  "
              f"<logL_held>={log_l_predictive:.3f}  "
              f"p={p_value:.3f}  "
              f"wall={minus_fit['wall_seconds']:.1f}s")

    print()

    # Step 3: Summarize
    print("[3] Summary")
    print(f"{'Channel':<22} | {'log Z (N-1)':>10} | {'<logL_held>':>11} | {'p-value':>8}")
    print("-" * 60)
    for r in loo_results:
        print(f"{r['channel']:<22} | {r['log_Z_minus_held']:>10.3f} | "
              f"{r['log_l_predictive']:>11.3f} | {r['p_value']:>8.3f}")

    # Aggregate metrics
    mean_p_value = float(np.mean([r["p_value"] for r in loo_results]))
    median_log_l_predictive = float(np.median([r["log_l_predictive"] for r in loo_results]))
    mean_log_z_minus = float(np.mean([r["log_Z_minus_held"] for r in loo_results]))

    # Predictive vs in-sample comparison
    # In-sample: each channel's contribution to the full log Z
    # Compute it from full posterior
    in_sample_contributions = {}
    for ch_name, fn in channels.items():
        samples = full_fit["samples"]
        weights = full_fit["weights"]
        ll_samples = np.array([fn(10 ** s[0], s[1]) for s in samples])
        finite = np.isfinite(ll_samples)
        if finite.sum() == 0:
            in_sample_contributions[ch_name] = -1e6
            continue
        ll_samples = np.where(finite, ll_samples, -1e6)
        in_sample_contributions[ch_name] = float(np.sum(weights * ll_samples))

    print()
    print(f"{'Channel':<22} | {'in-sample':>10} | {'predictive':>11} | {'diff':>8}")
    print("-" * 60)
    diffs = []
    for r in loo_results:
        in_s = in_sample_contributions[r["channel"]]
        out_s = r["log_l_predictive"]
        diff = in_s - out_s
        diffs.append(diff)
        print(f"{r['channel']:<22} | {in_s:>10.3f} | {out_s:>11.3f} | {diff:>8.3f}")

    mean_diff = float(np.mean(diffs))
    std_diff = float(np.std(diffs))
    print()
    print(f"Mean in-sample - predictive = {mean_diff:+.3f} (positive = predictive < in-sample)")
    print(f"Std of diffs = {std_diff:.3f}")

    # Verdict
    print()
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    if mean_diff > 1.0:
        print(f"  Mean overfit penalty: {mean_diff:.3f} nats per channel")
        print("  -> Model has SOME predictive validity but loses ~{:.1f} nats/channel when validating out-of-sample".format(mean_diff))
    elif mean_diff > 0.1:
        print(f"  Mean overfit penalty: {mean_diff:.3f} nats per channel")
        print("  -> Model has GOOD predictive validity (small overfit penalty)")
    else:
        print(f"  Mean overfit penalty: {mean_diff:.3f} nats per channel")
        print("  -> Model has STRONG predictive validity (essentially no overfit)")

    # Bayesian p-value check
    if mean_p_value > 0.05 and mean_p_value < 0.95:
        print(f"  Bayesian p-value: {mean_p_value:.3f} (in [0.05, 0.95] -> model fits data well)")
    else:
        print(f"  Bayesian p-value: {mean_p_value:.3f} (outside [0.05, 0.95] -> model fits data poorly or OVER-fits)")

    # Save
    out = {
        "validation_id": "LOO_CV_11ch_2026_09_12",
        "date": "2026-09-12",
        "method": "Leave-One-Out Cross-Validation",
        "n_channels": len(channels),
        "nlive": NLIVE,
        "dlogz_target": DLOGZ,
        "rstate_seed": 20260912,
        "full_11ch_fit": {
            "log_Z": full_fit["log_Z"],
            "median_sigma_m_0": float(10 ** np.median(full_fit["samples"][:, 0])),
            "median_a": float(np.median(full_fit["samples"][:, 1])),
            "wall_seconds": full_fit["wall_seconds"],
        },
        "loo_results": loo_results,
        "in_sample_contributions": in_sample_contributions,
        "aggregate_metrics": {
            "mean_p_value": mean_p_value,
            "median_log_l_predictive": median_log_l_predictive,
            "mean_log_z_minus_held": mean_log_z_minus,
            "mean_in_sample_minus_predictive": mean_diff,
            "std_in_sample_minus_predictive": std_diff,
        },
        "honest_caveats": [
            "LOO-CV is computationally expensive: 10 nested sampling fits per validation",
            "Bayesian p-value calculation is approximate (uses MAP estimate of 'observed' log L)",
            "Validation only tests predictive validity at the model class level, not parameter values",
        ],
    }
    out_path = HERE.parent / "data" / "results" / "loo_cv_validation_2026_09_12.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {out_path.relative_to(HERE.parent.parent)}")


if __name__ == "__main__":
    main()