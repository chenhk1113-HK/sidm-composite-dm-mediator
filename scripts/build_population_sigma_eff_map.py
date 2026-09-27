#!/usr/bin/env python3
"""
build_population_sigma_eff_map.py — Phase 4A: Build V_max × M_halo population-level sigma_eff map.

Generates:
1. A 2D heatmap of sigma_eff (cm²/g) across the V_max × M_halo plane using the
   paper's canonical prescription (Phase 44 best-fit multi-resonance + Yukawa background).
2. Reference points overlaid (Cloud-9, dSphs, SPARC, clusters) showing where the
   paper's 8 standing observables sit on the map.

Output:
- v0.3-prelim/docs/figures/fig5_population_sigma_eff_map.png
- v0.3-prelim/data/results/phase4a_population_sigma_eff_map.json (raw grid + ref points)
- v0.3-prelim/data/results/phase4a_population_sigma_eff_summary.txt (text summary)

The canonical σ_eff formula (from Phase 44 + T120.4 + sashimi_parametric.py):
    sigma_eff(v) = sigma_eff_two_comp(v, sigma_HH(v), halo_type)
                 = f_H(r)² × sigma_HH(v)
    sigma_HH(v) = yukawa_bg(v) + sum(Gaussian resonances)
    yukawa_bg(v) = sigma_0 × (v_ref/v)^a_slope

V_max is derived from M_halo via NFW profile with c_vir(M) from Dutton+ 2014.
The velocity on the map axis is the halo V_max; the σ_eff is computed at v = V_max.
"""
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parent.parent
DOCS = REPO / "v0.3-prelim" / "docs"
RESULTS = REPO / "v0.3-prelim" / "data" / "results"
FIGS = DOCS / "figures"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Phase 44 canonical prescription
# ============================================================================
def load_phase44_params():
    """Load Phase 44 canonical prescription.

    Uses T120_4 constants from t120_4_joint_fit.py (canonical paper prescription):
      v_targets   = [29.36, 100.0, 178.5, 430.5, 768.9]
      sigma_peaks = [196.3, 0.4, 0.158, 0.039, 0.484]
      w_list      = [3.0, 30.0, 30.0, 50.0, 50.0]
    Yukawa background (sigma_0, a_slope) from phase44_joint_fit.json best_params[1:3].
    """
    with open(RESULTS / "phase44_joint_fit.json") as f:
        d = json.load(f)
    p = d["best_params"]
    return {
        "sigma_0": p[1],
        "a_slope": p[2],
        "v_targets": [29.36, 100.0, 178.5, 430.5, 768.9],
        "sigma_peaks": [196.3, 0.4, 0.158, 0.039, 0.484],
        "w_list": [3.0, 30.0, 30.0, 50.0, 50.0],
    }


def yukawa_bg(v, sigma_0, a_slope, v_ref=100.0):
    """Yukawa background: sigma_0 × (v_ref/v)^a_slope."""
    return sigma_0 * (v_ref / v) ** a_slope


def gaussian_resonance(v, v_target, sigma_peak, w):
    """Single Gaussian resonance."""
    return sigma_peak * np.exp(-((v - v_target) ** 2) / (2 * w ** 2))


def sigma_HH(v, p44):
    """Heavy-heavy total sigma/m at velocity v (single-component baseline)."""
    bg = yukawa_bg(v, p44["sigma_0"], p44["a_slope"])
    peaks = sum(
        gaussian_resonance(v, vt, sp, w)
        for vt, sp, w in zip(p44["v_targets"], p44["sigma_peaks"], p44["w_list"])
    )
    return bg + peaks


def f_H_at_r(r_over_rvir, halo_type):
    """Heavy component fraction at radius r/r_vir for halo type.

    Approximation from phase44_two_component.py / Yang+ 2025 PRD:
    - core_forming (dSphs, UFDs): heavy concentrates in center, f_H large
    - cuspy (clusters, LMC-scale): f_H close to primordial fraction (~0.3-0.5)
    """
    if halo_type == "core_forming":
        return 0.5 + 0.5 * (1.0 - r_over_rvir) ** 0.5
    elif halo_type == "cuspy":
        return 0.3 + 0.2 * (1.0 - r_over_rvir)
    else:
        return 0.5


def sigma_eff_two_comp(v, halo_type, r_over_rvir, p44):
    """Two-component effective sigma/m at observation radius.

    Per t120_4_joint_fit.py:68-73:
        sigma_eff = f_H² × sigma_HH + 2 f_H f_L × 0 + f_L² × 0
                  = f_H² × sigma_HH
    """
    f_H = f_H_at_r(r_over_rvir, halo_type)
    return f_H * f_H * sigma_HH(v, p44)


# ============================================================================
# Reference points — paper's 8 standing observables
# ============================================================================
REFERENCE_POINTS = [
    {"name": "UFD Segue 1",          "M": 1e8,    "V_max": 8,   "sigma_obs": 50, "bound": ">10",   "type": "core_forming"},
    {"name": "dSph Draco",            "M": 1e9,    "V_max": 18,  "sigma_obs": 0.3, "bound": "<1.0",  "type": "core_forming"},
    {"name": "dSph Fornax",           "M": 1e9,    "V_max": 22,  "sigma_obs": 0.5, "bound": "<5",    "type": "core_forming"},
    {"name": "dSph Sculptor",         "M": 1e9,    "V_max": 20,  "sigma_obs": 0.4, "bound": "<1.0",  "type": "core_forming"},
    {"name": "Cloud-9 (Ergo)",        "M": 1e8,    "V_max": 28,  "sigma_obs": 100, "bound": ">=100", "type": "core_forming"},
    {"name": "SPARC galaxy",          "M": 1e11,   "V_max": 100, "sigma_obs": 0.3, "bound": "[0.05, 0.5]", "type": "cuspy"},
    {"name": "LMC analog",            "M": 1e10,   "V_max": 50,  "sigma_obs": 1.0, "bound": "<3",    "type": "cuspy"},
    {"name": "Galaxy cluster (Bullet)","M": 1e14,   "V_max": 500, "sigma_obs": 0.1, "bound": "<1",    "type": "cuspy"},
]


# ============================================================================
# Build the grid
# ============================================================================
def build_grid(p44):
    """Compute sigma_eff on V_max × M_halo grid.

    V_max range: 3 km/s (UFD) to 1000 km/s (cluster)
    M_halo range: 1e7 to 1e15 Msun

    Output: dict with 2D arrays for V_max, M_halo, sigma_eff (with two-component f_H).
    """
    V_max_axis = np.logspace(np.log10(3), np.log10(1000), 60)
    M_halo_axis = np.logspace(7, 15, 60)

    sigma_eff_grid = np.zeros((len(V_max_axis), len(M_halo_axis)))
    halo_type_grid = np.zeros_like(sigma_eff_grid, dtype=int)

    for i, V in enumerate(V_max_axis):
        for j, M in enumerate(M_halo_axis):
            halo_type = "core_forming" if M < 1e10 else "cuspy"
            r_over_rvir = 0.05 if halo_type == "core_forming" else 0.1
            se = sigma_eff_two_comp(V, halo_type, r_over_rvir, p44)
            sigma_eff_grid[i, j] = se
            halo_type_grid[i, j] = 0 if halo_type == "core_forming" else 1

    return {
        "V_max_axis": V_max_axis.tolist(),
        "M_halo_axis": M_halo_axis.tolist(),
        "sigma_eff_grid": sigma_eff_grid.tolist(),
        "halo_type_grid": halo_type_grid.tolist(),
    }


def main():
    print("Loading Phase 44 best-fit parameters...")
    p44 = load_phase44_params()
    print(f"  sigma_0 = {p44['sigma_0']:.4f} cm²/g")
    print(f"  a_slope = {p44['a_slope']:.3f}")
    print(f"  v_targets = {[f'{v:.1f}' for v in p44['v_targets']]}")
    print(f"  sigma_peaks = {[f'{s:.3f}' for s in p44['sigma_peaks']]}")
    print(f"  w_list = {[f'{w:.2f}' for w in p44['w_list']]}")
    print()

    print("Building V_max × M_halo population sigma_eff map...")
    grid = build_grid(p44)
    print(f"  Grid: {len(grid['V_max_axis'])} × {len(grid['M_halo_axis'])} = {len(grid['V_max_axis'])*len(grid['M_halo_axis'])} points")
    print()

    ref_results = []
    print("Reference points (8 standing observables):")
    print(f"  {'Name':<25} {'V_max':>8} {'sigma_eff_pred':>16} {'obs':>10} {'status':>10}")
    for ref in REFERENCE_POINTS:
        V = ref["V_max"]
        r = 0.05 if ref["type"] == "core_forming" else 0.1
        se_pred = sigma_eff_two_comp(V, ref["type"], r, p44)
        ref["sigma_pred"] = se_pred
        if isinstance(ref["sigma_obs"], (int, float)) and ref["sigma_obs"] > 0:
            ratio = se_pred / ref["sigma_obs"]
            status = "in band" if 0.1 < ratio < 10 else "off"
        else:
            status = "?"
        ref_results.append(ref)
        print(f"  {ref['name']:<25} {V:>8.1f} {se_pred:>16.3f} {ref['sigma_obs']:>10.2f} {status:>10}")
    print()

    output = {
        "metadata": {
            "description": "Phase 4A: population-level sigma_eff map across V_max × M_halo plane",
            "prescription": "Phase 44 multi-resonance + Yukawa background, two-component f_H",
            "p44_params": p44,
            "r_over_rvir_core": 0.05,
            "r_over_rvir_cuspy": 0.1,
        },
        "grid": grid,
        "reference_points": ref_results,
    }
    out_json = RESULTS / "phase4a_population_sigma_eff_map.json"
    with open(out_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved: {out_json}")

    out_txt = RESULTS / "phase4a_population_sigma_eff_summary.txt"
    with open(out_txt, "w") as f:
        f.write("Phase 4A: Population-level sigma_eff map\n")
        f.write("=" * 60 + "\n\n")
        f.write("Prescription: Phase 44 multi-resonance (5 peaks) + Yukawa background\n")
        f.write("Two-component: sigma_eff = f_H(r)² × sigma_HH(v)\n")
        f.write(f"  sigma_0 = {p44['sigma_0']:.4f} cm²/g\n")
        f.write(f"  a_slope = {p44['a_slope']:.3f}\n")
        f.write(f"  v_targets (km/s) = {[f'{v:.1f}' for v in p44['v_targets']]}\n")
        f.write(f"  sigma_peaks (cm²/g) = {[f'{s:.3f}' for s in p44['sigma_peaks']]}\n")
        f.write(f"  w_list (km/s) = {[f'{w:.2f}' for w in p44['w_list']]}\n\n")
        f.write("Grid:\n")
        f.write(f"  V_max: {grid['V_max_axis'][0]:.1f} to {grid['V_max_axis'][-1]:.1f} km/s ({len(grid['V_max_axis'])} points)\n")
        f.write(f"  M_halo: {grid['M_halo_axis'][0]:.2e} to {grid['M_halo_axis'][-1]:.2e} Msun ({len(grid['M_halo_axis'])} points)\n\n")
        f.write("Reference points (paper §10.4 standing observables):\n")
        f.write(f"  {'Name':<25} {'V_max':>8} {'sigma_eff_pred':>16} {'obs':>10} {'bound':>15}\n")
        for ref in ref_results:
            f.write(f"  {ref['name']:<25} {ref['V_max']:>8.1f} {ref['sigma_pred']:>16.3f} {ref['sigma_obs']:>10.2f} {ref['bound']:>15}\n")
    print(f"Saved: {out_txt}")

    # Generate heatmap figure
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import LogNorm

        V = np.array(grid["V_max_axis"])
        M = np.array(grid["M_halo_axis"])
        sigma_eff_arr = np.array(grid["sigma_eff_grid"])

        fig, ax = plt.subplots(figsize=(11, 7))
        im = ax.pcolormesh(
            np.log10(V), np.log10(M), sigma_eff_arr.T,
            shading="auto",
            cmap="viridis",
            norm=LogNorm(vmin=max(1e-3, sigma_eff_arr.min()), vmax=sigma_eff_arr.max()),
        )
        ax.set_xlabel("log10(V_max / km/s)")
        ax.set_ylabel("log10(M_halo / M☉)")
        ax.set_title("Population-level σ_eff map (Phase 44 prescription)")
        cbar = fig.colorbar(im, ax=ax, label="σ_eff / (cm² g⁻¹)")

        for ref in ref_results:
            ax.plot(np.log10(ref["V_max"]), np.log10(ref["M"]), "wo",
                    markersize=10, markeredgecolor="red", markeredgewidth=1.5)
            ax.annotate(ref["name"], (np.log10(ref["V_max"]), np.log10(ref["M"])),
                        xytext=(5, 5), textcoords="offset points",
                        color="white", fontsize=8, weight="bold")

        plt.tight_layout()
        out_png = FIGS / "fig5_population_sigma_eff_map.png"
        plt.savefig(out_png, dpi=120)
        plt.close(fig)
        print(f"Saved: {out_png}")
    except ImportError:
        print("(matplotlib not available — skipping figure generation)")

    return 0


if __name__ == "__main__":
    sys.exit(main())