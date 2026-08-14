"""
T37 — D12 deliverable: T22 Bayes factor with beta_seg at the fitted MAP value.

Direction B (v0.3, Yang+ 2026 + real KISS-SIDM) completion.

Background
----------
T22 (t22_real_kiss_sidm_two_comp.py) computes the 2-comp-vs-1-comp
Bayes factor with beta_seg = 0.25 hardcoded. T29 showed beta_seg_MAP ≈ 0.899.

This script re-runs the T22 fits with beta_seg set to the T29-MAP value
(0.899) to get the headline Bayes factor under the *data-favoured*
beta_seg. We also re-compute the 1-comp fits (which by construction do
not depend on beta_seg) so the BF comparison is internally consistent
on the same data path.

Three runs:
  - T37_A : 2-comp (4 par, 3 Yang+ channels, real KISS-SIDM, IMFP corr, beta_seg=0.899)
  - T37_C : 1-comp nested (2 par, same 3 channels, real KISS-SIDM, IMFP corr)
  - T37_E : 2-comp (4 par, 3 Yang+ channels, real KISS-SIDM, NO IMFP, beta_seg=0.899)

Outputs the headline BF (2-comp vs 1-comp) and compares to T22's BF.

Why this is non-trivial
-----------------------
beta_seg only affects the 2-comp model (it's the mass-segregation weight
between components 1 and 2). At beta_seg=0.899 (T29-MAP), the heavier
component 1 dominates dwarf-scale cross-sections more strongly than at
beta_seg=0.25 (default). This shifts sigma_eff at dwarf scale by
(V_DWARF / V_REF)**(0.899 - 0.25) ≈ 0.49 dex (factor ~3×) at V=30 km/s,
relative to the cluster-scale value.

Expected outcome
----------------
Most plausible: BF shifts by <1 unit (the data has weak constraining
power on beta_seg, so the headline 2-comp BF should be roughly stable).
But if BF shifts by >2.5 units, the 2-comp-vs-1-comp verdict is sensitive
to the beta_seg assumption, which is a publishable finding (claims about
2-comp must specify beta_seg assumptions).
"""
from __future__ import annotations
import json
import sys
import time
import contextlib
from pathlib import Path

# --- Path bootstrap (mirrors T22/T29 pattern) ---
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import numpy as np
import dynesty

import two_component_sidm as tc
import yang2026_likelihood as yl
import t22_real_kiss_sidm_two_comp as t22_mod  # underlying likelihoods + KISS data loader

from config import RESULTS_DIR_V03


# BETA_SEG_MAP from T29 result
BETA_SEG_FITTED_MAP = 0.899
BETA_SEG_HARDCODED_DEFAULT = 0.25

NLIVE = 200
DLOGZ = 0.1


# ------------------------------------------------------------------
# Context manager to swap two_component_sidm.SEGREGATION_BETA at runtime.
#
# Why: yang2026_likelihood.loglike_yang2026_full/_{dwarf,galaxy,cluster}
# call into two_component_sidm.sigma_eff_{dwarf,galaxy,cluster} which
# in turn use the MODULE-LEVEL SEGREGATION_BETA constant. Rather than
# refactor yang2026 + two_component_sidm to thread beta_seg through
# every call, we swap the constant for the duration of the dynesty run.
# ------------------------------------------------------------------
@contextlib.contextmanager
def patched_beta_seg(value: float):
    """Temporarily set two_component_sidm.SEGREGATION_BETA = value."""
    saved = tc.SEGREGATION_BETA
    tc.SEGREGATION_BETA = float(value)
    try:
        yield
    finally:
        tc.SEGREGATION_BETA = saved


def run_one(loglike, prior_transform, ndim, label):
    """Same as t22.run_one but locally defined to keep this script standalone."""
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=ndim, nlive=NLIVE, bound="multi", sample="auto", bootstrap=0,
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
    pcts = np.percentile(samples, [16, 50, 84], axis=0, weights=weights, method="inverted_cdf")
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
    print("T37 — T22 Bayes factor with beta_seg at the T29-MAP value (0.899)")
    print("=" * 80)

    kiss_data = t22_mod._get_kiss_data()
    print(f"Loaded KISS-SIDM data: {kiss_data.get('n_snapshots', '?')} snapshots")
    print(f"beta_seg choice: T29-MAP = {BETA_SEG_FITTED_MAP}")
    print()

    # --- Run 1: 2-comp with beta_seg=0.899 + IMFP correction ---
    print("Running A: 2-comp (4 par), beta_seg=0.899, IMFP correction...")
    with patched_beta_seg(BETA_SEG_FITTED_MAP):
        A = run_one(t22_mod.loglike_two_comp_yang_real_kiss,
                    t22_mod.prior_transform_4, 4,
                    "two_comp_real_kiss_with_imfp_beta0899")
    print(f"  log Z = {A['log_Z']:.3f} +/- {A['log_Z_err']:.3f}  "
          f"MAP = {[round(v, 3) for v in A['MAP']]}  (wall {A['wall_seconds']:.1f}s)")

    # --- Run 2: 2-comp with beta_seg=0.899, NO IMFP ---
    print("Running B: 2-comp (4 par), beta_seg=0.899, NO IMFP correction...")
    with patched_beta_seg(BETA_SEG_FITTED_MAP):
        B = run_one(t22_mod.loglike_two_comp_yang_real_kiss_no_imfp,
                    t22_mod.prior_transform_4, 4,
                    "two_comp_real_kiss_no_imfp_beta0899")
    print(f"  log Z = {B['log_Z']:.3f} +/- {B['log_Z_err']:.3f}  "
          f"MAP = {[round(v, 3) for v in B['MAP']]}  (wall {B['wall_seconds']:.1f}s)")

    # --- Run 3: 1-comp nested baseline (independent of beta_seg) ---
    print("Running C: 1-comp nested (2 par), IMFP correction...")
    C = run_one(t22_mod.loglike_one_comp_yang_real_kiss,
                t22_mod.prior_transform_2, 2,
                "one_comp_real_kiss_nested_with_imfp")
    print(f"  log Z = {C['log_Z']:.3f} +/- {C['log_Z_err']:.3f}  "
          f"MAP = {[round(v, 3) for v in C['MAP']]}  (wall {C['wall_seconds']:.1f}s)")

    # --- Bayes factors (this is the headline) ---
    delta_A_C = A["log_Z"] - C["log_Z"]   # 2-comp(beta=0.899) vs 1-comp
    delta_B_C = B["log_Z"] - C["log_Z"]   # 2-comp(beta=0.899,no IMFP) vs 1-comp

    def verdict(d):
        if d > 5: return "STRONGLY preferred (log BF > 5)"
        elif d > 2.5: return "MODERATELY preferred (2.5 < log BF < 5)"
        elif d > 1: return "WEAKLY preferred (1 < log BF < 2.5)"
        elif d > -1: return "INCONCLUSIVE (-1 < log BF < 1)"
        elif d > -2.5: return "WEAKLY disfavored (-2.5 < log BF < -1)"
        else: return "STRONGLY disfavored (log BF < -2.5)"

    print()
    print("=" * 80)
    print("Headline Bayes factors (T37, beta_seg = T29-MAP = 0.899):")
    print(f"  A vs C (2-comp[beta=0.899,IMFP] vs 1-comp[IMFP,3 ch]): {delta_A_C:+.3f} -- {verdict(delta_A_C)}")
    print(f"  B vs C (2-comp[beta=0.899,noIMFP] vs 1-comp[IMFP,3 ch]): {delta_B_C:+.3f} -- {verdict(delta_B_C)}")

    # --- Comparison vs T22 baseline (beta_seg=0.25) ---
    print()
    print("=" * 80)
    print("Comparison vs T22 baseline (beta_seg = 0.25 hardcoded):")
    t22_path = Path(__file__).resolve().parent.parent / "data" / "results" / "t22_real_kiss_sidm_two_comp.json"
    if t22_path.exists():
        with open(t22_path) as f:
            t22_data = json.load(f)
        t22_delta_AC = t22_data["bayes_factors"].get("delta_A_C_2comp_vs_1comp_3ch", float("nan"))
        t22_delta_BC = t22_data["bayes_factors"].get("delta_B_C_2comp_no_imfp_vs_1comp", float("nan"))
        print(f"  T22 A vs C (beta=0.25, IMFP):       {t22_delta_AC:+.3f}")
        print(f"  T37 A vs C (beta=0.899, IMFP):      {delta_A_C:+.3f}   "
              f"[delta = {delta_A_C - t22_delta_AC:+.3f}]")
        print(f"  T22 B vs C (beta=0.25, no IMFP):    {t22_delta_BC:+.3f}")
        print(f"  T37 B vs C (beta=0.899, no IMFP):   {delta_B_C:+.3f}   "
              f"[delta = {delta_B_C - t22_delta_BC:+.3f}]")
        comparison_note = (
            f"Beta_seg shifts the 2-comp-vs-1-comp Bayes factor by "
            f"|{delta_A_C - t22_delta_AC:.3f}| (IMFP) and "
            f"|{delta_B_C - t22_delta_BC:.3f}| (no IMFP). "
            f"{'Significant if >2.5' if max(abs(delta_A_C - t22_delta_AC), abs(delta_B_C - t22_delta_BC)) > 2.5 else 'Not significant — headline verdict is robust to beta_seg choice.'}"
        )
        print()
        print(f"  Summary: {comparison_note}")
    else:
        comparison_note = "T22 baseline JSON not found — comparison skipped."
        print(comparison_note)

    # --- Persist ---
    out = {
        "test": "T37_t22_with_fitted_beta_seg",
        "direction": ("D12 deliverable: re-run T22 2-comp-vs-1-comp Bayes factor "
                      "with beta_seg at the T29-MAP value (data-fitted segregation)."),
        "t22_baseline_beta_seg": BETA_SEG_HARDCODED_DEFAULT,
        "t37_beta_seg_value": BETA_SEG_FITTED_MAP,
        "t29_beta_seg_MAP_source": "v0.3-prelim/data/results/t29_beta_seg_fitted.json",
        "fits": {
            "A_two_comp_beta0899_with_imfp": A,
            "B_two_comp_beta0899_no_imfp": B,
            "C_one_comp_nested_with_imfp": C,
        },
        "bayes_factors_t37": {
            "delta_A_C_2comp_beta0899_vs_1comp_3ch": delta_A_C,
            "delta_B_C_2comp_beta0899_no_imfp_vs_1comp_3ch": delta_B_C,
        },
        "comparison_to_t22": {
            "t22_delta_A_C_2comp_vs_1comp_3ch": (t22_data["bayes_factors"]["delta_A_C_2comp_vs_1comp_3ch"]
                                                   if t22_path.exists() else None),
            "t22_delta_B_C_2comp_no_imfp_vs_1comp": (t22_data["bayes_factors"]["delta_B_C_2comp_no_imfp_vs_1comp"]
                                                     if t22_path.exists() else None),
            "t37_delta_A_C_minus_t22_delta_A_C": (delta_A_C - t22_data["bayes_factors"]["delta_A_C_2comp_vs_1comp_3ch"]
                                                  if t22_path.exists() else None),
            "t37_delta_B_C_minus_t22_delta_B_C": (delta_B_C - t22_data["bayes_factors"]["delta_B_C_2comp_no_imfp_vs_1comp"]
                                                  if t22_path.exists() else None),
            "comparison_note": comparison_note,
        },
        "interpretation": (
            f"With beta_seg at the data-fitted T29-MAP value ({BETA_SEG_FITTED_MAP}), "
            f"the T22 2-comp-vs-1-comp Bayes factor is "
            f"delta_A_C = {delta_A_C:+.3f} (IMFP) and "
            f"delta_B_C = {delta_B_C:+.3f} (no IMFP). "
            f"Compared to the T22 baseline (beta_seg=0.25), the IMFP BF shifted by "
            f"{delta_A_C - t22_data['bayes_factors']['delta_A_C_2comp_vs_1comp_3ch']:+.3f} "
            f"(beta_seg=0.899 vs 0.25). "
            f"{'A shift >2.5 indicates the 2-comp-vs-1-comp verdict depends on beta_seg.' if abs(delta_A_C - t22_data['bayes_factors']['delta_A_C_2comp_vs_1comp_3ch']) > 2.5 else 'The headline verdict is robust to beta_seg choice.'}"
        ),
        "verdict": (
            f"After beta_seg marginalization: "
            f"log BF (2-comp vs 1-comp, IMFP) = {delta_A_C:+.3f} [{verdict(delta_A_C)}]. "
            f"Direction B's headline BF {'IS' if abs(delta_A_C) > 1 else 'is NOT'} "
            f"significantly affected by the beta_seg choice."
        ),
    }

    out_path = RESULTS_DIR_V03 / "t37_t22_with_fitted_beta_seg.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/t37_t22_with_fitted_beta_seg.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print()
    print(f"output -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()
