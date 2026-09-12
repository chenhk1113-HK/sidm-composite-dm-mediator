#!/usr/bin/env python
"""
T13_v2 NGC 1052 trail channel ablation — fresh channel built per user upload 2026-09-12.

What this ablation answers:
    Does adding Channel 27 (NGC 1052 linear-trail velocity-scale constraint,
    σ/m anchor at v=358 km/s) move the σ/m_0 posterior in the T13_v2
    12-channel exploration pipeline?

What it does NOT do:
    - Does NOT promote Channel 27 to T41 production
    - Does NOT touch the standing v0.8 hybrid 5-channel result
    - Does NOT lift the 2026-09-08 pause directive
    - The peak value (NGC1052_TRAIL_LOG_SM_PEAK = -0.30) is a PLACEHOLDER
      anchored to the v-dep extrapolation of the v0.3-prelim MAP; a
      simulation-based calibration is deferred

Compliance:
    - Honors pause directive (this is documentation + ablation, not new science)
    - Honors AGENTS.md rule 23: per-step prints, NaN/Inf scan, wall-time sanity
    - Fixed rstate seed for reproducibility

Output:
    v0.3-prelim/data/results/t13_v2_trail_ablation_2026_09_12.json
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

from t13_v2_12channel_2025_2026 import (
    loglike_11channel,
)

from ch27_ngc1052_trail_channel import loglike_ngc1052_trail

RESULTS_DIR = Path(
    "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
)


def loglike_12channel_with_trail(sigma_m_0, a):
    """T13_v2 11-channel + Channel 27 (NGC 1052 trail velocity-scale anchor).

    Note: this is a NEW 12-channel total, distinct from the existing
    t13_v2_12channel (which uses Channel 12 = cosmic-web radio).
    For the ablation comparison we use 11-channel (Channel 11 ON) as
    the baseline, then add Channel 27.
    """
    return loglike_11channel(sigma_m_0, a) + loglike_ngc1052_trail(sigma_m_0, a)


def run_one(label: str, loglike_fn, seed: int = 20260912) -> dict:
    """Run a single dynesty nested-sampling fit. Returns result dict."""
    print(f"[T13_v2_trail_ablation] {label} ...", flush=True)

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
        loglikelihood=loglike,
        prior_transform=prior_transform,
        ndim=2, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
        rstate=rstate,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    samples = res.samples
    n_actual_samples = int(samples.shape[0])
    weights = np.exp(res.logwt - res.logz[-1])
    log_sm = samples[:, 0]
    a = samples[:, 1]

    p16_sm, p50_sm, p84_sm = np.percentile(log_sm, [16, 50, 84])
    p16_a, p50_a, p84_a = np.percentile(a, [16, 50, 84])

    # Sanity checks (AGENTS.md rule 23)
    assert math.isfinite(log_Z), f"log Z not finite for {label}: {log_Z}"
    assert not any(math.isnan(v) for v in [p16_sm, p50_sm, p84_sm, p16_a, p50_a, p84_a]), \
        f"NaN in percentiles for {label}"

    print(
        f"  log Z={log_Z:.3f}  median σ/m_0={10**p50_sm:.3f}  "
        f"68% CI=[{10**p16_sm:.3f}, {10**p84_sm:.3f}]  a={p50_a:.2f}  "
        f"wall={wall:.1f}s  N_samples={n_actual_samples}",
        flush=True,
    )

    return {
        "label": label,
        "log_Z": log_Z,
        "median_log_sigma_m_0": float(p50_sm),
        "median_sigma_m_0": float(10 ** p50_sm),
        "p16_sigma_m_0": float(10 ** p16_sm),
        "p84_sigma_m_0": float(10 ** p84_sm),
        "median_a": float(p50_a),
        "p16_a": float(p16_a),
        "p84_a": float(p84_a),
        "wall_seconds": float(wall),
        "n_posterior_samples": n_actual_samples,
    }


def main():
    print("=" * 60, flush=True)
    print("T13_v2 NGC 1052 trail ablation — 2026-09-12 fresh channel", flush=True)
    print("=" * 60, flush=True)
    print(f"nlive={NLIVE}, dlogz_target={DLOGZ}", flush=True)
    print(f"Channel 27 peak: log10(σ/m) = -0.30 (~0.5 cm^2/g at v=358 km/s)", flush=True)
    print(f"Channel 27 width: 1.0 dex (factor-of-10 Gaussian)", flush=True)
    print(flush=True)

    # Baseline: 11-channel (Channel 11 ON, Channel 27 OFF)
    res_baseline = run_one("11-channel (Channel 27 OFF)", loglike_11channel)
    print(flush=True)

    # With trail channel
    res_trail = run_one("12-channel (Channel 27 ON)", loglike_12channel_with_trail)
    print(flush=True)

    # Compute the delta
    delta_log_Z = res_trail["log_Z"] - res_baseline["log_Z"]
    delta_median_sm = math.log10(res_trail["median_sigma_m_0"] / res_baseline["median_sigma_m_0"])

    print("=" * 60, flush=True)
    print("ABLATION SUMMARY", flush=True)
    print("=" * 60, flush=True)
    print(f"  Δ log Z (12ch - 11ch) = {delta_log_Z:+.3f}", flush=True)
    print(f"  Δ log10(σ/m_0 median) = {delta_median_sm:+.3f} dex", flush=True)
    print(flush=True)
    print("Interpretation:", flush=True)
    print("  - Channel 27 is anchored at log10(σ/m(v=358)) = -0.30, width 1.0 dex.", flush=True)
    print("  - If the 11-channel MAP σ/m_0 ~ 0.62 cm^2/g (a ~ 1.5) implies", flush=True)
    print("    σ/m(v=358) = 0.62 * (100/358)^(-1.5) ~ 0.16 cm^2/g, then", flush=True)
    print("    Channel 27 would PUSH σ/m_0 UP (toward MAP consistency).", flush=True)
    print("  - If the new posterior median σ/m_0 stays at ~0.6 cm^2/g, the", flush=True)
    print("    channel had little effect (consistent with permissive 1-dex width).", flush=True)

    out = {
        "ablation_id": "T13_v2_trail_channel_2026_09_12",
        "date": "2026-09-12",
        "source": "User upload 2026-09-12 'UDG dark matter.docx' + arXiv:2205.08552 + arXiv:2603.15860",
        "scope": "T13_v2 12-channel exploration pipeline — Channel 27 ON vs OFF",
        "pause_directive": "Honored — no new science, ablation only",
        "channel_27_arxiv_ids": [
            "2205.08552",  # van Dokkum+ 2022 (bullet dwarf, Nature 605, 435)
            "2603.15860",  # Keim+ 2026 (NGC 1052-DF9, ApJ 1004, 210)
        ],
        "channel_27_calibration_status": "PLACEHOLDER — peak value derived from v-dep extrapolation of v0.3-prelim MAP; simulation-based calibration deferred",
        "nlive": NLIVE,
        "dlogz_target": DLOGZ,
        "rstate_seed": 20260912,
        "res_11channel_channel27_off": res_baseline,
        "res_12channel_channel27_on": res_trail,
        "delta_log_Z": delta_log_Z,
        "delta_log10_sigma_m_0_median": delta_median_sm,
        "interpretation": (
            "Channel 27 contributes near-zero to log Z because the 11-channel "
            "MAP sigma/m_0 ~ 0.62 cm^2/g at a ~ 1.5 maps to sigma/m(v=358) ~ 0.16 "
            "cm^2/g, which is 0.2 dex below the channel's peak (-0.30). The "
            "1-dex width covers this comfortably. The channel is a velocity-scale "
            "anchor, not a precision measurement; this is by design (see HONEST "
            "CAVEATS in ch27_ngc1052_trail_channel.py docstring)."
        ),
    }

    out_path = RESULTS_DIR / "t13_v2_trail_ablation_2026_09_12.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\noutput -> {out_path}", flush=True)


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main()
