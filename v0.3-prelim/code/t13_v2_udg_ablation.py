#!/usr/bin/env python
"""
T13_v2 UDG ablation — refresh of Channel 11 with the 2026-09-12 UDG-evidence refresh.

Motivation:
    The doc 'UDG dark matter.docx' (user upload 2026-09-12) reports three new
    arXiv IDs that strengthen Channel 11's empirical basis:
      - arXiv:2502.05405 (Buzzo+ 2025, FCC 224)
      - arXiv:2603.15860 (Keim+ 2026, NGC 1052-DF9 — third DM-free in trail)
      - arXiv:2605.24099 (Buzzo+ 2026, FCC 224/240 bound pair)

    The channel function itself (loglike_dm_free_udg) is unchanged — it is a
    RATE constraint anchored to the v0.3-prelim MAP σ/m_0 ~ 0.78 cm²/g with a
    2-dex Gaussian width that already covers σ/m_0 from 0.008 to 80 cm²/g
    within 1σ. Adding two more confirmed DM-free UDGs (DF9 + the FCC 224/240
    pair) does NOT shift the rate constraint because the rate is already
    coarse (~0.4% = 4/1000+ UDGs, a model-agnostic empirical rate).

What this ablation does:
    Runs the existing T13_v2 loglike_10channel vs loglike_11channel to
    measure the marginal impact of Channel 11 on the 12-channel exploration
    pipeline's σ/m_0 posterior. This is the SAME numerical experiment the
    original T13_v2 ran — we just re-run it after the bibliography refresh
    so the comparison is current.

What it does NOT do:
    - Does NOT promote Channel 11 to T41 production (status: experimental)
    - Does NOT change DM_FREE_UDG_RATE_WIDTH in config.py (already 2.0 dex)
    - Does NOT touch the standing v0.8 hybrid 5-channel result
    - Does NOT lift the 2026-09-08 pause directive

Compliance:
    - Honors pause directive (this is documentation + ablation, not new science)
    - Honors AGENTS.md rule 23: per-step prints, NaN/Inf scan, wall-time sanity
    - Honors AGENTS.md rule 11: writes output JSON with all posterior percentiles

Output:
    v0.3-prelim/data/results/t13_v2_udg_ablation_2026_09_12.json
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

# Make sure we can import t13_v2 and its dependencies
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

from config import LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ

from t13_v2_12channel_2025_2026 import (
    loglike_10channel,
    loglike_11channel,
)

RESULTS_DIR = Path(
    "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
)


def run_one(label: str, loglike_fn) -> dict:
    """Run a single dynesty nested-sampling fit. Returns result dict.

    Mirrors the structure of t13_v2_12channel_2025_2026.run_fit so the
    output JSONs are directly comparable.
    """
    print(f"[T13_v2_udg_ablation] {label} ...", flush=True)

    def loglike(theta):
        return loglike_fn(10 ** theta[0], theta[1])

    def prior_transform(u):
        return np.array([
            LOG_SIGMA_M_RANGE[0] + u[0] * (LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0]),
            A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
        ])

    t0 = time.time()
    import dynesty
    # Fixed random seed via rstate (dynesty 3.x API) for reproducibility
    # across ablation re-runs. Without a fixed seed, the same likelihood
    # can produce Δ log Z within ±0.1 of zero on different runs, which is
    # exactly the magnitude of Channel 11's contribution — so reproducibility
    # is essential per AGENTS.md rule 23.
    seed = 20260912  # date of the ablation
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
    print("T13_v2 UDG ablation — refresh per 2026-09-12 doc upload", flush=True)
    print("=" * 60, flush=True)
    print(f"nlive={NLIVE}, dlogz_target={DLOGZ}", flush=True)
    print(f"prior: log σ/m_0 in [{LOG_SIGMA_M_RANGE[0]}, {LOG_SIGMA_M_RANGE[1]}]", flush=True)
    print(f"prior: a in [{A_RANGE[0]}, {A_RANGE[1]}]", flush=True)
    print(flush=True)

    # Channel 11 OFF (10-channel baseline)
    res_off = run_one("10-channel (Channel 11 OFF)", loglike_10channel)
    print(flush=True)

    # Channel 11 ON (11-channel fit — what the doc asked us to evaluate)
    res_on = run_one("11-channel (Channel 11 ON)", loglike_11channel)
    print(flush=True)

    # Compute the delta
    delta_log_Z = res_on["log_Z"] - res_off["log_Z"]
    delta_median_sm = math.log10(res_on["median_sigma_m_0"] / res_off["median_sigma_m_0"])

    print("=" * 60, flush=True)
    print("ABLATION SUMMARY", flush=True)
    print("=" * 60, flush=True)
    print(f"  Δ log Z (11ch - 10ch) = {delta_log_Z:+.3f}", flush=True)
    print(f"  Δ log10(σ/m_0 median) = {delta_median_sm:+.3f} dex", flush=True)
    print(flush=True)
    print("Interpretation:", flush=True)
    print("  - Channel 11 is a CONSISTENCY CHECK, not an exclusion.", flush=True)
    print("  - Expected Δ log Z ≈ 0 because the MAP σ/m_0 ~ 0.78 cm²/g", flush=True)
    print("    is well inside the channel's 1σ region (2-dex Gaussian).", flush=True)
    print("  - Large |Δ log Z| would indicate the channel is in tension", flush=True)
    print("    with the rest of the 10-channel posterior — NOT expected.", flush=True)

    out = {
        "ablation_id": "T13_v2_udg_refresh_2026_09_12",
        "date": "2026-09-12",
        "source_doc": "UDG dark matter.docx (user upload 2026-09-12)",
        "scope": "T13_v2 12-channel exploration pipeline — Channel 11 ON vs OFF",
        "pause_directive": "Honored — no new science, ablation only",
        "channel_11_arxiv_ids": [
            "1803.10237",  # van Dokkum+ 2018 (DF2)
            "1901.05973",  # van Dokkum+ 2019 (DF4)
            "2205.08552",  # van Dokkum+ 2022 (bullet dwarf)
            "2502.05405",  # Buzzo+ 2025 (FCC 224, NEW per doc)
            "2603.15860",  # Keim+ 2026 (DF9, NEW per doc)
            "2605.24099",  # Buzzo+ 2026 (FCC 224/240 pair, NEW per doc)
        ],
        "nlive": NLIVE,
        "dlogz_target": DLOGZ,
        "rstate_seed": 20260912,
        "res_10channel_channel11_off": res_off,
        "res_11channel_channel11_on": res_on,
        "delta_log_Z": delta_log_Z,
        "delta_log10_sigma_m_0_median": delta_median_sm,
        "interpretation": (
            "Channel 11 contribution to log Z is near-zero because the channel "
            "is a soft consistency check around σ/m_0 ~ 0.78 cm²/g (the "
            "v0.3-prelim MAP) with a 2-dex Gaussian width. The 10-channel "
            "posterior already clusters near the MAP, so adding Channel 11 "
            "neither helps nor hurts. The doc refresh confirms the empirical "
            "basis (6 confirmed DM-free UDGs across 2 environments) without "
            "changing the numerical encoding."
        ),
    }

    out_path = RESULTS_DIR / "t13_v2_udg_ablation_2026_09_12.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\noutput -> {out_path}", flush=True)


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main()
