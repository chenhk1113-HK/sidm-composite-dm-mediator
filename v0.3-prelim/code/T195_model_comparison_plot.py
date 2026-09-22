"""
T195 — Bayesian model comparison plot (2026-09-21)

Per Grok review T2-D: consolidate mixed-method model comparison into
one figure. Compares three competing SIDM / halo-profile models on
SPARC + Cloud-9 joint likelihood.

Models compared:
- Multi-resonance SIDM (Phase 44 / T163 best fit)
- Constant σ/m (1-parameter baseline)
- Burkert profile (SPARC-only winner per Phase 42)

Metrics:
- log L (joint SPARC + Cloud-9)
- log B (Bayes factor from T177)
- # free parameters
- Δ BIC

Output: matplotlib figure + JSON.
"""

import json
import numpy as np
from pathlib import Path


# Phase 54 results (2026-09-16)
PHASE54_3CH_LOG_L = {
    "Constant σ/m": -17.66,
    "Multi-resonance (Phase 44)": -11.58,
}

# Phase 42 results (SPARC-only dynesty)
PHASE42_LOG_Z = {
    "Burkert": -963,
    "PISO": -1409,
    "Einasto": -1595,
    "NFW": -2654,
    "SIDM hybrid": -3300,
}

# T177 Bayes factor
T177_LOG_B = 3.06
T177_B = 21.3

# Parameter counts
N_PARAMS = {
    "Constant σ/m": 1,
    "Multi-resonance (Phase 44)": 15,
    "Burkert profile": 3,
}


def main():
    out_dir = Path("v0.3-prelim/data/results")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON metadata
    result = {
        "script": "T195_model_comparison_plot.py",
        "purpose": "Consolidated Bayesian model comparison: multi-resonance vs constant σ/m vs Burkert",
        "phase42_sparc_only_log_Z": PHASE42_LOG_Z,
        "phase54_3ch_log_L": PHASE54_3CH_LOG_L,
        "t177_log_B_multi_vs_constant": T177_LOG_B,
        "t177_bayes_factor": T177_B,
        "n_free_params": N_PARAMS,
        "verdict": "mixed: multi-resonance wins joint log L (+6.08), loses SPARC-only evidence to Burkert, wins Bayes factor (B=21) on multi-channel",
    }

    out_json = out_dir / "t195_model_comparison.json"
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved metadata: {out_json}")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Left panel: SPARC-only dynesty log Z
        models = list(PHASE42_LOG_Z.keys())
        log_z = list(PHASE42_LOG_Z.values())
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        # Highlight Burkert (winner) and SIDM hybrid (our model)
        colors_highlight = ["gold" if m == "Burkert" else
                            ("steelblue" if m == "SIDM hybrid" else "lightgray")
                            for m in models]

        ax = axes[0]
        bars = ax.barh(range(len(models)), log_z, color=colors_highlight, edgecolor="black")
        ax.set_yticks(range(len(models)))
        ax.set_yticklabels(models)
        ax.set_xlabel("dynesty log Z (Bayesian evidence)\n[higher = better]", fontsize=11)
        ax.set_title("SPARC only (Phase 42, 120 galaxies)\n"
                     "Burkert wins; multi-resonance is WORST of 5 models",
                     fontsize=11)
        ax.axvline(-963, color="gold", linestyle="--", alpha=0.5)
        ax.axvline(-3300, color="steelblue", linestyle="--", alpha=0.5)
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3)

        # Right panel: Joint log L comparison (Phase 54)
        models_joint = list(PHASE54_3CH_LOG_L.keys())
        log_l_joint = list(PHASE54_3CH_LOG_L.values())
        colors_joint = ["lightcoral" if m.startswith("Constant") else "steelblue"
                        for m in models_joint]
        ax = axes[1]
        bars = ax.barh(range(len(models_joint)), log_l_joint, color=colors_joint, edgecolor="black")
        for i, (m, l) in enumerate(zip(models_joint, log_l_joint)):
            ax.text(l + 0.2, i, f"  log L = {l}", va="center", fontsize=9)
        ax.set_yticks(range(len(models_joint)))
        ax.set_yticklabels([f"{m} (k={N_PARAMS[m]})" for m in models_joint])
        ax.set_xlabel("log L (joint SPARC + Cloud-9 likelihood)\n[higher = better]", fontsize=11)
        ax.set_title(f"Joint 3-channel (Phase 54)\n"
                     f"Multi-resonance wins raw log L (+{log_l_joint[1] - log_l_joint[0]:.2f})\n"
                     f"but ΔBIC = +3.22 favors Constant σ/m (15-vs-1 param penalty)\n"
                     f"T177: log B = {T177_LOG_B:.2f} (B = {T177_B:.1f}) favoring multi",
                     fontsize=10)
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3)

        plt.suptitle("Bayesian model comparison — multi-resonance SIDM architecture\n"
                     "(*honest* mixed-verdict framing)",
                     fontsize=12, y=1.02)
        plt.tight_layout()
        out_png = out_dir / "t195_model_comparison.png"
        fig.savefig(out_png, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved figure: {out_png}")
    except ImportError:
        print("matplotlib not available; ASCII fallback only")


if __name__ == "__main__":
    main()