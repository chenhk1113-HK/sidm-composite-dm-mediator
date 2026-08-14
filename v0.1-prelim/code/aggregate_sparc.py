#!/usr/bin/env python
"""
T3 aggregator: BIC + BMA over the 175-galaxy SPARC fits.

Outputs:
    - BIC weight per profile
    - BMA weight per profile
    - Model-averaged posterior summary (only meaningful if we add more params)
    - Per-galaxy evidence table
    - Joint log Z (sum across galaxies, both profiles)

For v0.1-prelim we compare only 2 profiles: NFW (CDM) and Burkert (cored SIDM-like).
Both have 2 free params; BIC difference = -2 * (log Z_B - log Z_NFW).

Usage:
    python aggregate_sparc.py
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
import numpy as np

RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.1-prelim/data/results")

# WIMpy uses Bayesian evidence directly for BMA weights; BIC for model selection.
# For 2-profile case with same n_params, BIC reduces to:  BIC = chi^2 - n_pts * log(n_pts)
# but easier to just use the evidence difference:  B = exp(log Z_B - log Z_NFW)

def compute_bma_weights(log_Zs: dict[str, float]) -> dict[str, float]:
    """BMA weights from log Z values via softmax."""
    names = list(log_Zs.keys())
    arr = np.array([log_Zs[n] for n in names])
    arr -= arr.max()  # numerical stability
    w = np.exp(arr)
    return {n: float(w[i] / w.sum()) for i, n in enumerate(names)}


def main():
    summary_path = RESULTS_DIR / "batch_summary.json"
    if not summary_path.exists():
        sys.exit(f"missing {summary_path}")
    summary = json.loads(summary_path.read_text())

    per_fit = summary["per_fit"]
    delta = summary["delta_log_Z"]

    # ------------------------------------------------------------
    # Per-profile aggregate statistics
    # ------------------------------------------------------------
    nfw_log_zs = [v["log_Z"] for v in per_fit["NFW"].values() if "log_Z" in v]
    bur_log_zs = [v["log_Z"] for v in per_fit["Burkert"].values() if "log_Z" in v]

    # ------------------------------------------------------------
    # Joint evidence sum (assumes independence across galaxies)
    # This is an approximation (data points within a galaxy are correlated,
    # and global parameters like Υ_d are shared). For v0.1 we do the
    # simple per-galaxy sum; v0.2 will add Υ_d marginalization.
    # ------------------------------------------------------------
    nfw_joint = float(np.sum(nfw_log_zs))
    bur_joint = float(np.sum(bur_log_zs))

    # ------------------------------------------------------------
    # BMA weights on the JOINT log Z (single Bayes factor for the dataset)
    # ------------------------------------------------------------
    joint_bma = compute_bma_weights({"NFW": nfw_joint, "Burkert": bur_joint})

    # ------------------------------------------------------------
    # Median per-galaxy Bayes factor (treating each galaxy as 1 vote)
    # ------------------------------------------------------------
    delta_arr = np.array(list(delta.values()))
    median_dlogz = float(np.median(delta_arr))
    n_burkert_pref = int(np.sum(delta_arr > 0))
    n_nfw_pref     = int(np.sum(delta_arr < 0))
    n_tied         = int(np.sum(delta_arr == 0))

    # ------------------------------------------------------------
    # BIC approximation (for reference; differs from evidence by O(n_pts))
    # ------------------------------------------------------------
    nfw_chi2 = [v["chi2_red"] * v.get("n_pts", 1) for v in per_fit["NFW"].values() if "chi2_red" in v]
    bur_chi2 = [v["chi2_red"] * v.get("n_pts", 1) for v in per_fit["Burkert"].values() if "chi2_red" in v]
    nfw_bic = float(np.sum(nfw_chi2) - 2 * len(nfw_chi2))  # 2 params each
    bur_bic = float(np.sum(bur_chi2) - 2 * len(bur_chi2))
    bic_bma = compute_bma_weights({"NFW": -0.5 * nfw_bic, "Burkert": -0.5 * bur_bic})

    # ------------------------------------------------------------
    # Per-galaxy Bayes factor categorization
    # Strong / moderate / weak thresholds per Jeffreys' scale
    # ------------------------------------------------------------
    cat = {"strong_NFW": 0, "moderate_NFW": 0, "weak_NFW": 0, "tied": 0,
           "weak_Burkert": 0, "moderate_Burkert": 0, "strong_Burkert": 0}
    for d in delta_arr:
        if d > 5:    cat["strong_Burkert"]   += 1
        elif d > 2:  cat["moderate_Burkert"] += 1
        elif d > 0:  cat["weak_Burkert"]     += 1
        elif d == 0: cat["tied"]             += 1
        elif d > -2: cat["weak_NFW"]         += 1
        elif d > -5: cat["moderate_NFW"]     += 1
        else:        cat["strong_NFW"]       += 1

    out = {
        "n_galaxies": len(delta),
        "joint_log_Z_NFW": nfw_joint,
        "joint_log_Z_Burkert": bur_joint,
        "joint_delta_log_Z_Burkert_minus_NFW": bur_joint - nfw_joint,
        "joint_Bayes_factor_Burkert_over_NFW_log10": float((bur_joint - nfw_joint) / np.log(10)),
        "joint_BMA_weights": joint_bma,
        "median_per_galaxy_delta_log_Z": median_dlogz,
        "n_galaxies_prefer_Burkert": n_burkert_pref,
        "n_galaxies_prefer_NFW": n_nfw_pref,
        "n_galaxies_tied": n_tied,
        "per_galaxy_evidence_categories_Jeffreys": cat,
        "BIC_weights_approximate": bic_bma,
        "BIC_NFW_total": nfw_bic,
        "BIC_Burkert_total": bur_bic,
        "interpretation": {
            "joint_log_Z_diff > 0": f"Burkert preferred joint (by {(bur_joint - nfw_joint):.0f} log Z)",
            "BMA_weight_Burkert > 0.95": "decisive evidence",
            "median_per_galaxy > 2": "majority of galaxies individually prefer Burkert",
            "weak_Burkert + moderate_Burkert": f"{cat['weak_Burkert']+cat['moderate_Burkert']} galaxies with mild-to-moderate preference",
            "strong_Burkert": f"{cat['strong_Burkert']} galaxies with strong preference for cored profile",
            "strong_NFW": f"{cat['strong_NFW']} galaxies with strong preference for cuspy profile",
        },
    }
    out_path = RESULTS_DIR / "t3_aggregate.json"
    out_path.write_text(json.dumps(out, indent=2))

    print("=" * 60)
    print(f"T3 AGGREGATE — v0.1-prelim SPARC ({out['n_galaxies']} galaxies)")
    print("=" * 60)
    print(f"Joint log Z: NFW = {nfw_joint:.1f}, Burkert = {bur_joint:.1f}")
    print(f"Δlog Z (B - N) = {bur_joint - nfw_joint:.1f} = log10 B = {(bur_joint - nfw_joint) / np.log(10):.2f}")
    print(f"Joint BMA: NFW = {joint_bma['NFW']:.4f}, Burkert = {joint_bma['Burkert']:.4f}")
    print()
    print(f"Per-galaxy median Δlog Z = {median_dlogz:.2f}")
    print(f"  Burkert preferred: {n_burkert_pref} galaxies ({100*n_burkert_pref/out['n_galaxies']:.0f}%)")
    print(f"  NFW preferred:     {n_nfw_pref} galaxies ({100*n_nfw_pref/out['n_galaxies']:.0f}%)")
    print(f"  Tied:              {n_tied}")
    print()
    print(f"Jeffreys' scale:")
    for k, v in cat.items():
        print(f"  {k:>20}: {v:3d} galaxies")
    print()
    print(f"Approximate BIC weights: NFW = {bic_bma['NFW']:.4f}, Burkert = {bic_bma['Burkert']:.4f}")
    print(f"Summary -> {out_path}")


if __name__ == "__main__":
    main()