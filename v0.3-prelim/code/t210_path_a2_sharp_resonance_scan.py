"""
T210 Path A2 — Sharp resonance scan at v_HL = 28 km/s.

Per Cloud-9alternate.docx memo, Path A2 is the only model-level route to
satisfy Cloud-9 and dSph simultaneously: a resonance narrower than the
velocity separation.

The current model has v_HL = 98.2 km/s (where the heavy-light sigma_HL
Lorentzian peak is centered). The cloud-9 / Crater II / Antlia II
requirements are at v ~ 5-28 km/s, while dSph is at v = 15 km/s.

Question: can we move v_HL down to v=28 (Cloud-9 scale) and shrink
the width_HL to < 15 km/s such that:
- Cloud-9 at v=28: sigma_eff high (on-peak, sigma_peak_HL * f_H^2 ~ large)
- dSph at v=15: sigma_eff low (off-peak, well below ceiling)
- SPARC at v=100: sigma_eff ~ 0.19 (back to heavy-channel-only)

This is a parameter scan. Test v_HL in [25, 30, 35] km/s and width_HL
in [5, 10, 15, 20] km/s. For each combination, evaluate sigma_eff at
v = 5, 10, 15, 28, 100, 500 km/s and check the per-channel verdict.

Caveat: if Crater II and Antlia II probe v ~ 5-10 km/s (satellite
dwarf regime), then a v_HL = 28 resonance still leaves them
unsatisfied.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from T207_three_term_fit import sigma_eff_three_term

# Borrowed mode parameters (Path F1 standing)
SIGMA_0 = 0.005
SIGMA_PEAK_HH_1 = 84.4
SIGMA_0_HL = 0.0001
SIGMA_PEAK_HL_DEFAULT = 0.318
V_HL_DEFAULT = 98.2
SIGMA_0_LL = 0.0006
A_SLOPE = 1.0

F_H_CF = 0.85
F_H_CC = 0.5
F_H_INT = 0.5 * (F_H_CF + F_H_CC)

# Per-channel f_H assignment
HALO_CLASSES = {
    "UFD v=3": "core_collapsed",
    "UFD v=5": "core_collapsed",
    "UFD v=7": "core_collapsed",
    "UFD v=10": "core_collapsed",
    "dSph v=15": "core_collapsed",
    "Cloud-9 v=28": "core_forming",
    "Crater II": "core_collapsed",  # satellite dwarf
    "Antlia II": "core_collapsed",   # satellite dwarf
    "SPARC v=100": "intermediate",
    "Cluster v=500": "core_collapsed",
}

# Per-channel observation requirements
CHANNELS = {
    # name: (v, sigma_unc, obs, kind)
    "UFD v=3": (3.0, 0.05, 0.155, "ceiling"),
    "UFD v=5": (5.0, 0.05, 0.093, "ceiling"),
    "UFD v=7": (7.0, 0.05, 0.067, "ceiling"),
    "UFD v=10": (10.0, 0.05, 0.047, "ceiling"),
    "dSph v=15": (15.0, 0.04, 0.8, "ceiling"),
    "Cloud-9 v=28": (28.0, 30.0, 128.0, "floor"),
    "Crater II": (28.0, 10.0, 30.0, "floor"),   # using V_max=28 for memo Scenario D
    "Antlia II": (28.0, 10.0, 30.0, "floor"),    # using V_max=28
    "SPARC v=100": (100.0, 0.05, 0.193, "gaussian"),
    "Cluster v=500": (500.0, 5e-4, 2.5e-4, "ceiling"),
}

# Scenarios to scan
V_HL_SCENARIOS = [25.0, 28.0, 30.0, 35.0, 50.0, 75.0, 100.0]
WIDTH_HL_SCENARIOS = [5.0, 10.0, 15.0, 20.0, 30.0, 50.0]


def f_H_for(halo_class: str) -> float:
    if halo_class == "core_forming":
        return F_H_CF
    elif halo_class == "core_collapsed":
        return F_H_CC
    elif halo_class == "intermediate":
        return F_H_INT


def evaluate_all_channels(v_HL: float, width_HL: float) -> dict:
    """Compute sigma_eff and per-channel z-score for given v_HL, width_HL."""
    results = {}
    for name, (v, sigma_unc, obs, kind) in CHANNELS.items():
        halo_class = HALO_CLASSES[name]
        f_H = f_H_for(halo_class)
        sigma_eff = sigma_eff_three_term(
            v,
            f_H=f_H,
            sigma_0=SIGMA_0,
            a_slope=A_SLOPE,
            sigma_peak_HH_1=SIGMA_PEAK_HH_1,
            sigma_0_HL=SIGMA_0_HL,
            sigma_peak_HL=SIGMA_PEAK_HL_DEFAULT,
            v_HL=v_HL,
            width_HL=width_HL,
            sigma_0_LL=SIGMA_0_LL,
        )
        if kind == "ceiling":
            z = (sigma_eff - obs) / sigma_unc
            verdict = "PASS" if z < 1.0 else ("MARGINAL" if z < 2.0 else "FAIL")
        elif kind == "floor":
            z = (obs - sigma_eff) / sigma_unc
            verdict = "PASS" if z < 1.0 else ("MARGINAL" if z < 2.0 else "FAIL")
        elif kind == "gaussian":
            z = (sigma_eff - obs) / sigma_unc
            verdict = "PASS" if abs(z) < 1.0 else ("MARGINAL" if abs(z) < 2.0 else "FAIL")
        results[name] = {
            "v": v, "sigma_eff": sigma_eff, "obs": obs,
            "kind": kind, "z": z, "verdict": verdict,
        }
    return results


def main():
    all_results = {}
    print("=" * 80)
    print("T210 Path A2 — Sharp resonance scan at v_HL in [25, 28, 30, 35, 50, 75, 100]")
    print("=" * 80)

    # Iterate through all combinations
    for v_HL in V_HL_SCENARIOS:
        for width_HL in WIDTH_HL_SCENARIOS:
            key = f"v_HL={v_HL:.0f}, width_HL={width_HL:.0f}"
            all_results[key] = evaluate_all_channels(v_HL, width_HL)

    # Find configurations that pass:
    # - Cloud-9 PASS (sigma_eff >= 128 at v=28)
    # - dSph PASS (sigma_eff <= 0.8 at v=15)
    # - SPARC PASS or MARGINAL (|z| < 2)
    # - Crater II / Antlia II: assume V_max = 28 for memo scenario D
    passing_configs = []
    for key, results in all_results.items():
        c9 = results["Cloud-9 v=28"]
        dsph = results["dSph v=15"]
        sparc = results["SPARC v=100"]
        crater = results["Crater II"]
        antlia = results["Antlia II"]
        if c9["verdict"] == "PASS" and dsph["verdict"] == "PASS":
            passing_configs.append((key, results))

    print(f"\n{len(passing_configs)} configurations pass both Cloud-9 AND dSph:")
    for key, results in passing_configs[:20]:  # first 20
        print(f"\n  {key}:")
        for ch in ["Cloud-9 v=28", "dSph v=15", "SPARC v=100", "Crater II", "Antlia II"]:
            r = results[ch]
            print(f"    {ch}: sigma_eff = {r['sigma_eff']:.3f}, verdict = {r['verdict']} (z={r['z']:.2f})")

    # Save all results
    out_path = Path(__file__).resolve().parent.parent / "data" / "results" / "t210_path_a2_sharp_resonance_scan.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nFull scan saved to {out_path}")

    # Also save summary
    summary_path = Path(__file__).resolve().parent.parent / "data" / "results" / "t210_path_a2_summary.json"
    summary = {
        "n_passing": len(passing_configs),
        "n_total": len(all_results),
        "passing_configs": [(k, all_results[k]) for k, _ in passing_configs],
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()