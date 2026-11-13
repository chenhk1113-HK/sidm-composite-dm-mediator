#!/usr/bin/env python
"""
T13_v2 LSB ablation — impact of the new LSB core channel (Channel 14 candidate).

Motivation
----------
The uploaded document 'LSB science.docx' (2026-11-13) proposed using low-
surface-brightness (LSB) galaxy cores as a constraint on sigma/m.  The check was
implemented in v0.3-prelim/code/channels_lsb_core.py and split into two halves
after verification against the primary sources:

  (A) USABLE — NGC 5963 core-collapsibility, Sanchez-Salcedo, Melnick & Vega 2005
      (astro-ph/0506345, read end-to-end from the primary PDF, now in
      docs/papers/verified/).  sigma_0 at v0 = 100 km/s must stay below
      ~0.2 cm^2 g^-1 (95% CL; the authors' tighter core-size fit gives ~0.1,
      and their core-collapse / halo-lifetime test gives ~0.08) or the halo
      would have gravothermally collapsed.  The paper's velocity convention
      (v0 = 100 km/s) is identical to this project's V_REF.

  (B) DIAGNOSTIC ONLY — Kitazawa 2026 (arXiv:2605.05588) five field LSBGs.
      Recomputing the paper's own equations from its own Table 1 parameters
      gives t_core values ~1.0e3 LARGER than the printed Tables 2-7 (ratio
      999-1062 on 5/5 objects at both sigma/m = 1 and 0.1 cm^2 g^-1), while the
      printed rho_s / r_s pairs reproduce the printed M_dyn to a few percent
      under an NFW mass integral.  The factor 10^3 therefore sits in the
      timescale arithmetic, not in the catalogue.  The channel is exposed as a
      diagnostic and is NOT wired into the likelihood.

What this ablation does
-----------------------
Runs dynesty nested sampling for:
    baseline      = loglike_12channel            (current T13_v2 pipeline)
    + LSB (loose) = baseline + NGC 5963 limit at 0.2 cm^2 g^-1 (95% CL)
    + LSB (tight) = baseline + NGC 5963 limit at 0.1 cm^2 g^-1 (Upsilon*=1.2 fit)
and reports dlog Z, the sigma/m_0 and a posteriors, and the Bayes factor.

What it does NOT do
-------------------
- Does NOT promote the LSB channel to production.  Status is "ablation only"
  until the project decides; see docs/papers/to_verify/arXiv:2605.05588.
- Does NOT use Kitazawa's printed timescales as a constraint.
- Does NOT touch config.py, the standing hybrid 5-channel result, or any
  existing channel.

Compliance
----------
- AGENTS.md rule 23: per-step flush prints, finite/NaN assertions, wall-time
  reported, seed pinned (dynesty rstate) so dlog Z is reproducible.
- AGENTS.md rule 32: seed pinned in the artifact, posteriors reported as
  16/50/84 percentiles rather than points.
- Run with the SIDM project venv (.venv-sidm-bench), NOT the agent venv.

Output
------
v0.3-prelim/data/results/t13_v2_lsb_ablation_2026-11-13.json
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
sys.path.insert(0, str(HERE.parent.parent / "v0.1-prelim" / "code"))  # halo_profiles

from config import LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ  # noqa: E402

from t13_v2_12channel_2025_2026 import loglike_12channel  # noqa: E402
from channels_lsb_core import (  # noqa: E402
    loglike_lsb_ngc5963_core,
    reproduce_kitazawa_table,
    NGC5963_SIGMA_LIMIT_CM2G,
    NGC5963_SIGMA_LIMIT_TIGHT,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"   # CG-16: repo-relative
SEED = int(os.environ.get("LSB_ABLATION_SEED", 20261113))
NLIVE_RUN = int(os.environ.get("LSB_ABLATION_NLIVE", NLIVE))
DLOGZ_RUN = float(os.environ.get("LSB_ABLATION_DLOGZ", DLOGZ))
# Replica runs (different seed) are written to a separate file so a
# reproducibility check never overwrites the primary result.
OUT_SUFFIX = "" if SEED == 20261113 else f"_replica_seed{SEED}"


def make_loglike(limit_cm2_g: float | None):
    """Baseline (limit=None) or baseline + NGC 5963 LSB core bound."""
    if limit_cm2_g is None:
        return lambda s0, a: loglike_12channel(s0, a)

    def loglike(s0, a):
        out = loglike_lsb_ngc5963_core(
            s0, a, sigma_limit_cm2_g=limit_cm2_g)
        return loglike_12channel(s0, a) + out["loglike"]

    return loglike


def run_one(label: str, loglike_fn) -> dict:
    """One dynesty nested-sampling run; mirrors t13_v2_udg_ablation.run_one."""
    print(f"[T13_v2_lsb_ablation] {label} ...", flush=True)

    def loglike(theta):
        return loglike_fn(10 ** theta[0], theta[1])

    def prior_transform(u):
        return np.array([
            LOG_SIGMA_M_RANGE[0] + u[0] * (LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0]),
            A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
        ])

    t0 = time.time()
    import dynesty  # noqa: PLC0415

    rstate = np.random.default_rng(SEED)
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike,
        prior_transform=prior_transform,
        ndim=2, nlive=NLIVE_RUN, bound='multi', sample='auto', bootstrap=0,
        rstate=rstate,
    )
    sampler.run_nested(dlogz=DLOGZ_RUN, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    samples = res.samples
    log_sm = samples[:, 0]
    a_samp = samples[:, 1]

    p16_sm, p50_sm, p84_sm = np.percentile(log_sm, [16, 50, 84])
    p16_a, p50_a, p84_a = np.percentile(a_samp, [16, 50, 84])

    # AGENTS.md rule 23 sanity checks
    assert math.isfinite(log_Z), f"log Z not finite for {label}: {log_Z}"
    vals = [p16_sm, p50_sm, p84_sm, p16_a, p50_a, p84_a]
    assert all(not math.isnan(v) for v in vals), f"NaN percentile for {label}"

    # fraction of the posterior that the LSB channel actually penalises
    penalised = 0.0
    for s0, a_val in zip(log_sm, a_samp):
        out = loglike_lsb_ngc5963_core(10 ** s0, a_val)
        if out["metadata"]["penalised"]:
            penalised += 1.0
    penalised_frac = penalised / max(1, samples.shape[0])

    print(
        f"  log Z={log_Z:.3f}  median sigma/m_0={10**p50_sm:.4f}  "
        f"68% CI=[{10**p16_sm:.4f}, {10**p84_sm:.4f}]  a={p50_a:.2f} "
        f"[{p16_a:.2f}, {p84_a:.2f}]  penalised_fraction={penalised_frac:.3f}  "
        f"wall={wall:.1f}s  N={samples.shape[0]}",
        flush=True,
    )

    return {
        "label": label,
        "log_Z": log_Z,
        "median_log_sigma_m_0": float(p50_sm),
        "median_sigma_m_0": float(10 ** p50_sm),
        "p16_sigma_m_0": float(10 ** p16_sm),
        "p84_sigma_m_0": float(10 ** p84_sm),
        "credible_68pct_sigma_m_0": [float(10 ** p16_sm), float(10 ** p84_sm)],
        "median_a": float(p50_a),
        "p16_a": float(p16_a),
        "p84_a": float(p84_a),
        "credible_68pct_a": [float(p16_a), float(p84_a)],
        "lsb_penalised_posterior_fraction": float(penalised_frac),
        "wall_seconds": float(wall),
        "n_posterior_samples": int(samples.shape[0]),
        "seed": SEED,
        "nlive": NLIVE_RUN,
        "dlogz": DLOGZ_RUN,
    }


def main():
    print("=" * 72, flush=True)
    print("T13_v2 LSB ablation — NGC 5963 core-collapsibility channel", flush=True)
    print("=" * 72, flush=True)
    print(f"nlive={NLIVE_RUN}, dlogz={DLOGZ_RUN}, seed={SEED}", flush=True)
    print(f"prior: log10 sigma/m_0 in {LOG_SIGMA_M_RANGE}, a in {A_RANGE}", flush=True)
    print(flush=True)

    # Print the Kitazawa audit up front so the JSON records why half the
    # LSB evidence is excluded.
    audit = reproduce_kitazawa_table()
    ratios = [r["sigma_1"]["ratio_calc_over_printed"] for r in audit]
    print("Kitazawa+2026 t_core audit (recomputed / printed):", flush=True)
    for r in audit:
        print(f"  {r['name']:>9} nu_s={r['nu_s_kms']:6.1f} km/s "
              f"sigma=1: printed {r['sigma_1']['printed_Gyr']:6.2f} Gyr vs "
              f"recomputed {r['sigma_1']['recomputed_Gyr']:10.1f} Gyr "
              f"(x{r['sigma_1']['ratio_calc_over_printed']:.0f})", flush=True)
    print(f"  ratio range: {min(ratios):.0f} - {max(ratios):.0f}  "
          f"-> printed times NOT reproducible; channel excluded\n", flush=True)

    res_base = run_one("baseline 12-channel (LSB OFF)", make_loglike(None))
    print(flush=True)
    res_loose = run_one("12ch + NGC 5963 limit 0.2 cm2/g (95% CL)",
                        make_loglike(NGC5963_SIGMA_LIMIT_CM2G))
    print(flush=True)
    res_tight = run_one("12ch + NGC 5963 limit 0.1 cm2/g (Upsilon*=1.2 fit)",
                        make_loglike(NGC5963_SIGMA_LIMIT_TIGHT))
    print(flush=True)

    out = {
        "test": "T13_v2_lsb_ablation_ngc5963_core",
        "date": "2026-11-13",
        "seed": SEED,
        "nlive": NLIVE_RUN,
        "dlogz": DLOGZ_RUN,
        "channel_citation": ("astro-ph/0506345 (Sanchez-Salcedo, Melnick & Vega 2005) "
                            "NGC 5963: sigma_0 <~ 0.2 cm2/g at 95% CL, ~0.1 tighter; "
                            "quoted at v0 = 100 km/s, same V_REF convention"),
        "channel_status": "ablation only — not promoted to production",
        "kitazawa_audit": {
            "citation": "arXiv:2605.05588 (Kitazawa 2026)",
            "rows": audit,
            "recomputed_over_printed_ratio_range": [min(ratios), max(ratios)],
            "verdict": ("printed t_core values are ~1e3 smaller than the paper's own "
                        "equations produce from its own Table 1 parameters; catalogue "
                        "parameters themselves pass an independent NFW mass check. "
                        "LSB core-formation times therefore NOT used as a constraint."),
        },
        "res_baseline": res_base,
        "res_lsb_loose": res_loose,
        "res_lsb_tight": res_tight,
        "delta_log_Z_loose": res_loose["log_Z"] - res_base["log_Z"],
        "delta_log_Z_tight": res_tight["log_Z"] - res_base["log_Z"],
        "delta_median_sigma_m_0_loose_dex": math.log10(
            res_loose["median_sigma_m_0"] / res_base["median_sigma_m_0"]),
        "delta_median_sigma_m_0_tight_dex": math.log10(
            res_tight["median_sigma_m_0"] / res_base["median_sigma_m_0"]),
    }

    print("=" * 72, flush=True)
    print("ABLATION SUMMARY", flush=True)
    print("=" * 72, flush=True)
    for key, lbl in (("res_lsb_loose", "loose 0.2"), ("res_lsb_tight", "tight 0.1")):
        dlogz = out[f"delta_log_Z_{key.split('_')[2]}"]
        dsm = out[f"delta_median_sigma_m_0_{key.split('_')[2]}_dex"]
        print(f"  {lbl:<12} dlog Z = {dlogz:+.3f}   "
              f"dlog10(median sigma/m_0) = {dsm:+.3f} dex   "
              f"Bayes factor = {math.exp(dlogz):.3f}", flush=True)

    out_path = RESULTS_DIR / f"t13_v2_lsb_ablation_2026-11-13{OUT_SUFFIX}.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\noutput -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
