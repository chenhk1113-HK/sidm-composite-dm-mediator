#!/usr/bin/env python
"""
T9 — Systematic prior-variation test (per peer review item 2.1.6).

The reviewer's complaint: "Weak systematic uncertainty scanning. No dedicated
test suite varying critical priors (halo density ranges, Υ_d bounds, sampler
hyperparameters) to measure how posterior σ/m shifts with prior choices."

This script runs T8's joint 5-channel fit MULTIPLE TIMES with different prior
ranges, then reports how much the posterior median σ/m shifts.

Three prior variations are tested:
    1. TIGHT_LOG_SM = (-2.0, 1.5)   — narrower than default (-3.0, 2.5)
    2. WIDE_LOG_SM   = (-4.0, 3.5)   — wider
    3. TIGHT_A       = (-1.0, 1.0)    — narrower velocity power-law

For each variant we report: posterior median σ/m, MAP σ/m, 68% CI, log Z.
Then we tabulate how much the median shifts between variants.

Wall: ~10-15 s per variant × 4 variants = ~60 s.
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
import numpy as np
import dynesty

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ

sys.path.insert(0, str(Path(__file__).resolve().parent))
from channels_v03 import (
    loglike_dsph_v03, loglike_ufd_v03, loglike_bullet_v03,
    sigma_m_at_v, V_REF, V_GALAXY,
)


RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def loglike_5channel(sigma_m_0: float, a: float) -> float:
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf
    if not (-2 <= a <= 2):
        return -np.inf
    ll = 0.0
    ll += loglike_dsph_v03(sigma_m_0, a)
    ll += loglike_ufd_v03(sigma_m_0, a)
    ll += loglike_bullet_v03(sigma_m_0, a)
    # SPARC saturation (same as t8_v03)
    from t8_v03_joint_fit import delta_log_sparc
    ll += delta_log_sparc(sigma_m_0, a) / 1000
    return ll


def run_fit(label: str, log_sm_range: tuple, a_range: tuple):
    """Run dynesty with given priors; return posterior summary."""
    print(f"[T9 {label}] log_sm_range={log_sm_range}, a_range={a_range}")

    def loglike(theta):
        return loglike_5channel(10**theta[0], theta[1])

    def prior_transform(u):
        return np.array([
            log_sm_range[0] + u[0] * (log_sm_range[1] - log_sm_range[0]),
            a_range[0] + u[1] * (a_range[1] - a_range[0]),
        ])

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=2, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    log_sm_samples = samples[:, 0]
    a_samples = samples[:, 1]

    imap = int(np.argmax(weights))
    log_sm_MAP = float(log_sm_samples[imap])
    a_MAP = float(a_samples[imap])
    p16_sm, p50_sm, p84_sm = np.percentile(log_sm_samples, [16, 50, 84])
    p16_a, p50_a, p84_a = np.percentile(a_samples, [16, 50, 84])

    print(f"  log Z={log_Z:.3f}  MAP σ/m={10**log_sm_MAP:.2f}  median σ/m={10**p50_sm:.2f}  "
          f"68% CI=[{10**p16_sm:.2f}, {10**p84_sm:.2f}]  a={p50_a:.2f}  wall={wall:.1f}s")

    return {
        "label": label,
        "log_Z": log_Z,
        "MAP_log_sigma_m": log_sm_MAP,
        "MAP_sigma_m": 10**log_sm_MAP,
        "MAP_a": a_MAP,
        "median_log_sigma_m": p50_sm,
        "median_sigma_m": 10**p50_sm,
        "p16_sigma_m": 10**p16_sm,
        "p84_sigma_m": 10**p84_sm,
        "p16_a": p16_a,
        "p50_a": p50_a,
        "p84_a": p84_a,
        "wall_seconds": wall,
        "priors": {"log_sigma_m_range": list(log_sm_range), "a_range": list(a_range)},
    }


def main():
    variants = [
        ("default", LOG_SIGMA_M_RANGE, A_RANGE),
        ("tight_log_sm", (-2.0, 1.5), A_RANGE),
        ("wide_log_sm", (-4.0, 3.5), A_RANGE),
        ("tight_a", LOG_SIGMA_M_RANGE, (-1.0, 1.0)),
    ]
    results = [run_fit(*v) for v in variants]

    # Compute drift vs default
    default = results[0]
    print("\n=== DRIFT vs DEFAULT ===")
    print(f"{'variant':<16} {'MAP σ/m':<10} {'median σ/m':<12} {'68% CI':<22} {'Δmedian log':<10}")
    for r in results:
        delta_log = r["median_log_sigma_m"] - default["median_log_sigma_m"]
        ci = f"[{r['p16_sigma_m']:.2f}, {r['p84_sigma_m']:.2f}]"
        print(f"{r['label']:<16} {r['MAP_sigma_m']:<10.3f} {r['median_sigma_m']:<12.3f} {ci:<22} {delta_log:+.3f}")

    # Robustness summary
    medians = [r["median_log_sigma_m"] for r in results]
    drift_max = max(medians) - min(medians)
    print(f"\nMax drift in log10(σ/m) across variants: {drift_max:.3f} dex")
    print(f"  (small drift = result is prior-robust; large drift = prior-sensitive)")

    out_path = RESULTS_DIR / "t9_prior_variation.json"
    out_path.write_text(json.dumps({
        "test": "T9_prior_variation",
        "results": results,
        "drift_max_log_sigma_m": drift_max,
        "robustness": "robust" if drift_max < 0.3 else ("moderate" if drift_max < 0.6 else "sensitive"),
        "notes": "Per peer review item 2.1.6 / Medium-Term #4: tests prior robustness.",
    }, indent=2))
    print(f"\noutput -> {out_path}")


if __name__ == "__main__":
    main()