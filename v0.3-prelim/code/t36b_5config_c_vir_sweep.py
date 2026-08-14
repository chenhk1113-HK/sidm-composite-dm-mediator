"""
T36b — D15 follow-on to T36: 5-config c_vir sweep to see if Hayashi+ 2025
is uniquely good or if a finer grid closes the residual 3.1× further.

T36 (D13) tested 3 c_vir relations:
  A1: Dutton-Macciò 2014 (T15 default; 500× off)
  A2: Hayashi+ 2025 (3.1× off, BEST)
  A3: Ludlow+ 2016 (no crossing)

T36b expands to 5 c_vir relations to map the residual gap:
  A4: Hayashi+ 2025 high-tail (their published MW satellite 1-sigma upper)
  A5: Dutton-Macciò 2014 + 1.4× bump (A2/A1 mix — emulate a robust avg)

Headline to test: does a slightly different c_vir relation close the 3.1× gap
further? Or is the residual purely N-body calibration drift?
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import sashimi_parametric as sp


# T36b: 5 c_vir relations (3 from T36 + 2 new)
def c_vir_dutton_maccio_2014(M_vir_Msun):
    """Dutton-Maccio 2014 (T15 default)."""
    log_c = 0.54 - 0.13 * np.log10(M_vir_Msun / 1e12)
    return 10 ** log_c


def c_vir_hayashi_2025(M_vir_Msun):
    """Hayashi+ 2025 MW satellite (T36 best)."""
    log_c = 1.42 - 0.10 * np.log10(M_vir_Msun / 1e12)
    return 10 ** log_c


def c_vir_ludlow_2016(M_vir_Msun):
    """Ludlow+ 2016."""
    log_c = 0.47 - 0.13 * np.log10(M_vir_Msun / 1e12)
    return 10 ** log_c


def c_vir_hayashi_2025_high(M_vir_Msun):
    """Hayashi+ 2025 high-tail (1-sigma upper of their MW satellite distribution).
    log_c = 1.55 - 0.08 * log(M/1e12) -- even higher concentrations.
    """
    log_c = 1.55 - 0.08 * np.log10(M_vir_Msun / 1e12)
    return 10 ** log_c


def c_vir_dutton_hayashi_mix(M_vir_Msun):
    """Hybrid: Dutton-Maccio + 1.4x bump (a "robust avg" of DM and Hayashi).
    Tests whether ANY 1.4x-bumped Dutton-Maccio-like relation closes the gap.
    """
    base = c_vir_dutton_maccio_2014(M_vir_Msun)
    return 1.4 * base


C_VIR_RELATIONS = {
    "A1_dutton_maccio_2014": c_vir_dutton_maccio_2014,
    "A2_hayashi_2025": c_vir_hayashi_2025,
    "A3_ludlow_2016": c_vir_ludlow_2016,
    "A4_hayashi_2025_high": c_vir_hayashi_2025_high,
    "A5_dutton_hayashi_mix": c_vir_dutton_hayashi_mix,
}


def predict_collapse_fraction(M_vir_arr, c_vir_arr, sigma_0_cm2_per_g: float, w_kms: float = np.inf):
    n = 0
    for M_vir, c_vir in zip(M_vir_arr, c_vir_arr):
        sidm = sp.predict_sparc_satellite(
            M_vir_Msun=M_vir, c_vir=c_vir,
            sigma_0_per_m_chi_cm2_per_g=sigma_0_cm2_per_g, w_kms=w_kms,
        )
        if sidm["core_collapsed"]:
            n += 1
    return n / len(M_vir_arr)


def run_one(c_vir_fn, label, n_halos=100):
    np.random.seed(42)
    M_vir_arr = np.random.lognormal(mean=np.log(3e8), sigma=0.5, size=n_halos)
    c_vir_arr = c_vir_fn(M_vir_arr)
    log_c_arr = np.log10(c_vir_arr) + np.random.normal(0, 0.13, n_halos)
    c_vir_arr = 10 ** log_c_arr

    sigma_0_grid = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0]
    sweep = []
    for sigma_0 in sigma_0_grid:
        frac = predict_collapse_fraction(M_vir_arr, c_vir_arr, sigma_0)
        sweep.append({"sigma_0_cm2_per_g": sigma_0, "collapsed_fraction": frac})
    sigmas = np.array([s["sigma_0_cm2_per_g"] for s in sweep])
    fracs = np.array([s["collapsed_fraction"] for s in sweep])
    cross_idx = np.where(np.diff(np.sign(fracs - 0.5)))[0]
    if len(cross_idx) > 0:
        i = int(cross_idx[0])
        log_s = np.log10(sigmas[i]) + (0.5 - fracs[i]) / (fracs[i+1] - fracs[i]) * (
            np.log10(sigmas[i+1]) - np.log10(sigmas[i])
        )
        crossing = float(10 ** log_s)
    else:
        crossing = None
    return {
        "config_label": label,
        "median_c_vir": float(np.median(c_vir_arr)),
        "median_M_vir_Msun": float(np.median(M_vir_arr)),
        "sigma_0_sweep": sweep,
        "crossing_sigma_0_cm2_per_g": crossing,
    }


def main():
    print("=" * 80)
    print("T36b — SASHIMI 5-config c_vir sweep (D15 follow-on to T36)")
    print("=" * 80)
    configs = []
    for label, fn in C_VIR_RELATIONS.items():
        t0 = time.time()
        cfg = run_one(fn, label)
        cfg["wall_seconds"] = time.time() - t0
        configs.append(cfg)
        crossing = cfg["crossing_sigma_0_cm2_per_g"]
        print(f"  {label}: crossing = {crossing}, wall = {cfg['wall_seconds']:.2f}s")

    HAYASHI_BOUNDARY = 0.2
    for cfg in configs:
        c = cfg["crossing_sigma_0_cm2_per_g"]
        if c is not None:
            cfg["ratio_to_hayashi"] = c / HAYASHI_BOUNDARY
            cfg["gap_in_dex"] = abs(np.log10(c) - np.log10(HAYASHI_BOUNDARY))
        else:
            cfg["ratio_to_hayashi"] = None
            cfg["gap_in_dex"] = None

    with_crossing = [c for c in configs if c["crossing_sigma_0_cm2_per_g"] is not None]
    if with_crossing:
        best = min(with_crossing, key=lambda c: c["gap_in_dex"])
    else:
        best = None

    print()
    print("HEADLINE:")
    for cfg in configs:
        c = cfg["crossing_sigma_0_cm2_per_g"]
        if c is not None:
            print(f"  {cfg['config_label']}: crossing = {c:.3f}, ratio = {cfg['ratio_to_hayashi']:.1f}x, gap = {cfg['gap_in_dex']:.2f} dex")
        else:
            print(f"  {cfg['config_label']}: NO CROSSING")

    if best:
        print(f"\n  BEST: {best['config_label']} (gap {best['gap_in_dex']:.2f} dex)")

    out = {
        "test": "T36b_sashimi_5config_c_vir_sweep",
        "direction": "D15 follow-on to T36: 5 c_vir relations (3 from T36 + 2 new)",
        "configs_run": configs,
        "best_config": best["config_label"] if best else None,
        "best_crossing_sigma_0_cm2_per_g": best["crossing_sigma_0_cm2_per_g"] if best else None,
        "best_gap_in_dex": best.get("gap_in_dex") if best else None,
        "verdict": (
            f"T36b 5-config sweep found best fit at {best['config_label'] if best else 'NONE'}, "
            f"gap {best.get('gap_in_dex', 'N/A')} dex from Hayashi+ 2025 boundary."
        ),
        "interpretation": (
            "T36 (D13) found A2 Hayashi+ 2025 with 0.49 dex gap. T36b tests whether a "
            "finer grid closes the gap further (A4 Hayashi high-tail, A5 1.4x bump). "
            "If A4 or A5 closes to <0.3 dex, the gap is configurable; if A2 remains best, "
            "the residual is N-body calibration drift, not configuration choice."
        ),
    }
    out_path = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results/t36b_5config_c_vir_sweep.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/t36b_5config_c_vir_sweep.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()