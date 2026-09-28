#!/usr/bin/env python3
"""
build_species_dependent_sigma.py — Path 3:
Independent HH/HL/LL resonance peaks — tests if the missing parameter
lives in sigma-v shape (not in E).

Currently the model only has sigma_HH(v) with 5 Gaussian peaks at
fixed positions. Path 3 extends this to three species:
  - sigma_HH(v): Yukawa bg + 5 Gaussian peaks at p44 positions
  - sigma_HL(v): Yukawa bg + 5 Gaussian peaks at INDEPENDENT positions
  - sigma_LL(v): Yukawa bg + 5 Gaussian peaks at INDEPENDENT positions

sigma_eff = f_H^2 * sigma_HH + 2 f_H f_L * sigma_HL + f_L^2 * sigma_LL

Tests whether the dSph tension (which Path 2's continuous E could not
resolve predictively) is resolved by allowing sigma_HL/sigma_LL to have
different peak structures than sigma_HH.
"""
import json
import numpy as np
from pathlib import Path
from scipy.optimize import minimize

REPO = Path(__file__).parent.parent
RESULTS = REPO / "v0.3-prelim" / "data" / "results"
FIGS = REPO / "v0.3-prelim" / "docs" / "figures"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

import sys
sys.path.insert(0, str(Path(__file__).parent))
from build_population_sigma_eff_map import (
    load_phase44_params, f_H_at_r,
)
from smoke_test_continuous_E import E_proxy


# ============================================================================
# Species-dependent sigma(v)
# ============================================================================
def gaussian_peak(v, v_target, sigma_peak, w):
    return sigma_peak * np.exp(-((v - v_target) ** 2) / (2 * w ** 2))


def yukawa_bg(v, sigma_0, a_slope, v_ref=100.0):
    return sigma_0 * (v_ref / v) ** a_slope


def sigma_species(v, v_targets, sigma_peaks, w_list, sigma_0, a_slope):
    """Generic sigma(v) for one species: Yukawa bg + Gaussian peaks."""
    bg = yukawa_bg(v, sigma_0, a_slope)
    peaks = sum(gaussian_peak(v, vt, sp, w)
                for vt, sp, w in zip(v_targets, sigma_peaks, w_list))
    return bg + peaks


def sigma_eff_three_comp(v, f_H, sigma_HH, sigma_HL, sigma_LL):
    """Two-component DM: sigma_eff = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL."""
    f_L = 1 - f_H
    return f_H * f_H * sigma_HH + 2 * f_H * f_L * sigma_HL + f_L * f_L * sigma_LL


# ============================================================================
# Standing observables (5 in-sample + 2 held-out)
# ============================================================================
# Format: (name, V_max, sigma_obs, bound, f_b, host_ratio, t_over_t_core, f_H)
# f_H values from Phase 44 prescription
OBSERVABLES_5 = [
    # (name, V_max, sigma_obs, bound, f_b, host_ratio, t_over_t_core, f_H)
    ("Cloud-9 (RELHIC)",     28,   100, "lower", 1e-4, 1.0,    0.05, 0.05),
    ("Draco (field dSph)",   18,   1.0, "upper", 1e-3, 1.0,    0.20, 0.20),
    ("Sculptor (field dSph)",20,   1.0, "upper", 2e-3, 1.0,    0.20, 0.20),
    ("Fornax (satellite)",   22,   5.0, "upper", 5e-4, 1000.0, 0.30, 0.30),
    ("Cluster (Bullet)",     500,  0.1, "upper", 0.1,  1.0,    1.0,  0.50),
]

HELDOUT = [
    ("Leo T (classical dSph)", 15, 0.5, "upper", 3e-3, 1.0, 0.10, 0.20),
    ("Segue 1 (UFD)", 12, 1.0, "upper", 1e-4, 1.0, 0.10, 0.10),
]


# ============================================================================
# Phase 44 baseline (sigma_HH only, current model)
# ============================================================================
p44 = load_phase44_params()


def sigma_eff_baseline(v, f_H):
    """Phase 44 baseline: sigma_eff = f_H^2 * sigma_HH(v)."""
    sHH = sigma_species(v, p44["v_targets"], p44["sigma_peaks"], p44["w_list"],
                         p44["sigma_0"], p44["a_slope"])
    return sigma_eff_three_comp(v, f_H, sHH, 0.0, 0.0)


# ============================================================================
# Three-species model
# ============================================================================
def sigma_eff_3species(v, f_H, v_t_HL, v_t_LL, peak_shift=0.0):
    """
    sigma_HH at fixed Phase 44 positions.
    sigma_HL at shifted positions: v_t_HL = p44["v_targets"] + offset_per_peak.
    sigma_LL at shifted positions: v_t_LL = p44["v_targets"] + offset_per_peak * 2.

    For simplicity, use a single offset per species (5 params total: HL_offset, LL_offset).
    """
    v_targets_HH = p44["v_targets"]
    v_targets_HL = [vt + v_t_HL for vt in v_targets_HH]
    v_targets_LL = [vt + v_t_LL for vt in v_targets_HH]

    sHH = sigma_species(v, v_targets_HH, p44["sigma_peaks"], p44["w_list"],
                         p44["sigma_0"], p44["a_slope"])
    sHL = sigma_species(v, v_targets_HL, p44["sigma_peaks"], p44["w_list"],
                         p44["sigma_0"], p44["a_slope"])
    sLL = sigma_species(v, v_targets_LL, p44["sigma_peaks"], p44["w_list"],
                         p44["sigma_0"], p44["a_slope"])
    return sigma_eff_three_comp(v, f_H, sHH, sHL, sLL)


# ============================================================================
# Fit: 2 free params (v_t_HL, v_t_LL) + categorical E from Path 2
# ============================================================================
def fit_3species(observables, beta_p2=-3.40, deltas_p2=None):
    """
    Fit HL_offset, LL_offset to minimize violations.
    Use Path 2's beta = -3.40 and per-bin offsets as starting point.

    Returns (best_offsets, residuals, in_sample_pass_count).
    """
    if deltas_p2 is None:
        deltas_p2 = {"RELHIC": 0.0, "field_dSph": 0.0, "satellite": 0.0, "cluster": 0.0}

    def loss_fn(params):
        HL_offset, LL_offset = params
        loss = 0
        for name, V, sigma_obs, bound, f_b, host_ratio, t_tc, f_H in observables:
            logE = E_proxy(f_b, host_ratio, t_tc)
            s_eff = sigma_eff_3species(V, f_H, HL_offset, LL_offset)
            if s_eff <= 0:
                s_eff = 1e-10  # numerical floor
            log_pred = np.log10(s_eff) + beta_p2 * logE + deltas_p2.get(
                {"RELHIC": "RELHIC", "field_dSph": "field_dSph",
                 "satellite": "satellite", "cluster": "cluster"}.get(
                    {"RELHIC": "RELHIC", "field_dSph": "field_dSph",
                     "satellite": "satellite", "cluster": "cluster"}.get(name.split(" ")[1].strip("()"), "field_dSph"),
                    "field_dSph"), 0.0)
            # Bin lookup simpler:
            if "Cloud-9" in name:
                delta = deltas_p2["RELHIC"]
            elif "Draco" in name or "Sculptor" in name or "Leo T" in name or "Segue" in name:
                delta = deltas_p2["field_dSph"]
            elif "Fornax" in name:
                delta = deltas_p2["satellite"]
            elif "Cluster" in name:
                delta = deltas_p2["cluster"]
            else:
                delta = 0.0
            log_pred_final = log_pred + delta

            if bound == "lower":
                v = max(0, np.log10(sigma_obs) - log_pred_final)
            else:
                v = max(0, log_pred_final - np.log10(sigma_obs))
            loss += v ** 2
        return loss

    best_result = None
    best_loss = np.inf
    for HL_init in [-100, -50, 0, 50, 100]:
        for LL_init in [-200, -100, -50, 0, 50, 100, 200]:
            x0 = [HL_init, LL_init]
            result = minimize(loss_fn, x0, method='Nelder-Mead',
                              options={'xatol': 1e-2, 'fatol': 1e-6, 'maxiter': 500})
            if result.fun < best_loss:
                best_loss = result.fun
                best_result = result
    return best_result.x, best_loss


# ============================================================================
# Compute sigma_eff for any system
# ============================================================================
def compute_predictions(observables, HL_offset, LL_offset, beta_p2=-3.40, deltas_p2=None):
    if deltas_p2 is None:
        deltas_p2 = {"RELHIC": 0.0, "field_dSph": 0.0, "satellite": 0.0, "cluster": 0.0}
    preds = {}
    for name, V, sigma_obs, bound, f_b, host_ratio, t_tc, f_H in observables:
        logE = E_proxy(f_b, host_ratio, t_tc)
        s_eff = sigma_eff_3species(V, f_H, HL_offset, LL_offset)
        if s_eff <= 0:
            s_eff = 1e-10
        log_pred = np.log10(s_eff) + beta_p2 * logE

        if "Cloud-9" in name:
            delta = deltas_p2["RELHIC"]
        elif "Draco" in name or "Sculptor" in name or "Leo T" in name or "Segue" in name:
            delta = deltas_p2["field_dSph"]
        elif "Fornax" in name:
            delta = deltas_p2["satellite"]
        elif "Cluster" in name:
            delta = deltas_p2["cluster"]
        else:
            delta = 0.0
        log_pred_final = log_pred + delta
        sigma_pred = 10 ** log_pred_final

        if bound == "lower":
            ratio = sigma_pred / sigma_obs
            PASS = ratio >= 1
        else:
            ratio = sigma_pred / sigma_obs
            PASS = ratio <= 1
        preds[name] = {
            "V_max": V, "sigma_pred": float(sigma_pred), "sigma_obs": sigma_obs,
            "bound": bound, "ratio": float(ratio), "PASS": bool(PASS),
            "f_H": f_H, "log_E": float(logE), "delta": float(delta),
        }
    return preds


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("PATH 3: Independent HH/HL/LL resonance peaks")
    print("=" * 70)
    print()

    # Baseline: Phase 44 only (sigma_HH)
    print("Baseline (Phase 44, sigma_HH only):")
    for name, V, sigma_obs, bound, f_b, host_ratio, t_tc, f_H in OBSERVABLES_5:
        s = sigma_eff_baseline(V, f_H)
        print(f"  {name:<28} f_H={f_H:.2f} sigma={s:.3f} bound={bound} obs={sigma_obs}")
    print()

    # Fit 3-species
    print("Fitting 3-species model (HL_offset, LL_offset) + Path 2 E...")
    offsets, loss = fit_3species(OBSERVABLES_5, beta_p2=-3.40,
                                  deltas_p2={"RELHIC": 0.0, "field_dSph": 0.0,
                                             "satellite": 0.0, "cluster": 0.0})
    print(f"  HL_offset = {offsets[0]:.2f} km/s")
    print(f"  LL_offset = {offsets[1]:.2f} km/s")
    print(f"  Loss = {loss:.4f}")
    print()

    # Predictions
    print("In-sample (5 systems):")
    in_sample = compute_predictions(OBSERVABLES_5, offsets[0], offsets[1])
    for name, p in in_sample.items():
        verdict = "PASS" if p["PASS"] else "FAIL"
        print(f"  {name:<28} sigma_pred={p['sigma_pred']:.3f} obs={p['sigma_obs']:.2f} {p['bound']:<8} ratio={p['ratio']:.3f} {verdict}")
    n_in_pass = sum(1 for p in in_sample.values() if p["PASS"])
    print()
    print(f"In-sample: {n_in_pass}/5 PASS")
    print()

    print("Held-out (2 systems):")
    heldout = compute_predictions(HELDOUT, offsets[0], offsets[1])
    for name, p in heldout.items():
        verdict = "PASS" if p["PASS"] else "FAIL"
        print(f"  {name:<28} sigma_pred={p['sigma_pred']:.3f} obs={p['sigma_obs']:.2f} {p['bound']:<8} ratio={p['ratio']:.3f} {verdict}")
    n_out_pass = sum(1 for p in heldout.values() if p["PASS"])
    print()
    print(f"Held-out: {n_out_pass}/2 PASS")
    print()

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    if n_in_pass == 5 and n_out_pass == 2:
        print("Independent HH/HL/LL peaks PREDICT held-out systems.")
        print("Missing parameter lives in sigma-v shape, NOT in E.")
    elif n_in_pass == 5 and n_out_pass == 1:
        print("In-sample OK; 1/2 held-out PASS.")
        print("Partial predictive power from species-dependent sigma.")
    elif n_in_pass < 5:
        print(f"In-sample: {n_in_pass}/5 only. Species-dependent sigma insufficient.")
        print("Need different approach (e.g. genuinely categorical E).")
    else:
        print("Held-out predictions FAIL.")
        print("Species-dependent sigma does not generalize.")
    print()

    # Save
    out = {
        "metadata": {
            "description": "Path 3: independent HH/HL/LL resonance peaks",
            "model": "sigma_eff = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL",
            "free_params": ["HL_offset (km/s)", "LL_offset (km/s)"],
            "in_sample": [o[0] for o in OBSERVABLES_5],
            "held_out": [h[0] for h in HELDOUT],
        },
        "best_fit": {
            "HL_offset": float(offsets[0]),
            "LL_offset": float(offsets[1]),
            "loss": float(loss),
        },
        "in_sample": in_sample,
        "held_out": heldout,
        "verdict": {
            "in_sample_pass": n_in_pass,
            "in_sample_total": len(in_sample),
            "held_out_pass": n_out_pass,
            "held_out_total": len(heldout),
        },
    }

    def _convert(o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    out_path = RESULTS / "phase4d_species_dependent_sigma.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=_convert)
    print(f"Saved: {out_path}")

    # Plot
    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Left: sigma_eff(v) for HH, HL, LL
        ax = axes[0]
        v_arr = np.logspace(0, 3, 200)
        f_H = 0.5
        sHH = [sigma_species(v, p44["v_targets"], p44["sigma_peaks"], p44["w_list"],
                              p44["sigma_0"], p44["a_slope"]) for v in v_arr]
        v_HL = [vt + offsets[0] for vt in p44["v_targets"]]
        v_LL = [vt + offsets[1] for vt in p44["v_targets"]]
        sHL = [sigma_species(v, v_HL, p44["sigma_peaks"], p44["w_list"],
                              p44["sigma_0"], p44["a_slope"]) for v in v_arr]
        sLL = [sigma_species(v, v_LL, p44["sigma_peaks"], p44["w_list"],
                              p44["sigma_0"], p44["a_slope"]) for v in v_arr]
        ax.plot(v_arr, sHH, 'b-', label='sigma_HH (Phase 44)', linewidth=2)
        ax.plot(v_arr, sHL, 'r--', label=f'sigma_HL (offset {offsets[0]:.0f})', linewidth=2)
        ax.plot(v_arr, sLL, 'g:', label=f'sigma_LL (offset {offsets[1]:.0f})', linewidth=2)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('v (km/s)')
        ax.set_ylabel(r'$\sigma$ (cm$^2$/g)')
        ax.set_title('Path 3: species-dependent sigma(v)')
        ax.legend()
        ax.grid(True, alpha=0.3, which='both')

        # Right: sigma_eff for each system (in-sample + held-out)
        ax2 = axes[1]
        all_obs = OBSERVABLES_5 + HELDOUT
        all_preds = list(in_sample.values()) + list(heldout.values())
        Vs = [o[1] for o in all_obs]
        sigmas = [p["sigma_pred"] for p in all_preds]
        colors = ["green" if p["PASS"] else "red" for p in all_preds]
        markers = ["o"] * 5 + ["s"] * 2  # circles=fit, squares=held-out
        for i, (V, s, c, m) in enumerate(zip(Vs, sigmas, colors, markers)):
            ax2.scatter(V, s, c=c, s=150, edgecolors='black', marker=m, zorder=3)
            ax2.annotate(p["bound"][0] if False else all_preds[i]["bound"][0],
                        (V, s), textcoords="offset points", xytext=(8, 8),
                        fontsize=11, fontweight='bold')
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_xlabel('V_max (km/s)')
        ax2.set_ylabel(r'$\sigma_{\rm eff}$ (cm$^2$/g)')
        ax2.set_title(f'In-sample {n_in_pass}/5, Held-out {n_out_pass}/2')
        ax2.grid(True, alpha=0.3, which='both')

        plt.tight_layout()
        out_png = FIGS / "fig8_species_dependent_sigma.png"
        plt.savefig(out_png, dpi=120)
        print(f"Saved: {out_png}")
    except ImportError:
        print("matplotlib not available")


if __name__ == "__main__":
    main()