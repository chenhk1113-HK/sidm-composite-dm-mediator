"""
Phase 33d — External probe with REAL SPARC data.

Uses the actual SPARC database (Lelli, McGaugh, Schombert 2016):
  - 127 high-quality galaxies (Q=1 or Q=2)
  - Vflat range: 33.6 - 332 km/s
  - Median: 116.6 km/s

For each galaxy, evaluate the multi-resonance model's sigma/m(Vflat)
prediction and compare to observational constraints.

If model predicts sigma/m consistent with SIDM range [0.1, 10] cm^2/g
for most galaxies -> external probe passes.

Uses Phase 32b posterior median as model parameters.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v70_multi_resonant_darkqcd import (
    sigma_m_multi_resonant,
    velocity_dependent_background,
)
from t90_v50_resonant_sidm import kinetic_energy_eV

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
SPARC_DIR = Path(__file__).resolve().parent.parent / "data" / "external" / "sparc"


def parse_sparc_table1():
    """Parse Table1.mrt to get galaxy names and Vflat."""
    galaxies = []
    seen_names = set()
    table_path = SPARC_DIR / "Table1.mrt"
    if not table_path.exists():
        print(f"ERROR: SPARC Table1.mrt not found at {table_path}")
        return []

    with open(table_path) as f:
        for line in f:
            if len(line) < 120:
                continue
            name = line[:11].strip()
            if not name or name in seen_names or " " in name:
                continue
            try:
                vflat = float(line[101:106])
                q_str = line[115:118].strip()
                q = int(q_str) if q_str and q_str.lstrip("-").isdigit() else 3
                if vflat > 0 and q in [1, 2]:
                    galaxies.append({"name": name, "Vflat_kms": vflat, "Q": q})
                    seen_names.add(name)
            except (ValueError, IndexError):
                pass

    return galaxies


def get_best_posterior():
    """Load best sample from Phase 32b joint fit."""
    with open(RESULTS_DIR / "phase32b_multi_resonant_joint_fit.json") as f:
        data = json.load(f)
    return data["best_sample"]


def build_resonances(best):
    """Build resonance list from best sample."""
    resonances = []
    names = ["R1_Cloud9", "R2_SPARC", "R3_Stream", "R4_Cluster"]
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]
    widths = best.get("width_fractions", [0.05, 0.05, 0.05, 0.10])
    for i in range(4):
        v_t = best["v_targets_kms"][i]
        E_R = kinetic_energy_eV(v_t, best["m_chi_GeV"])
        Gamma = widths[i] * E_R
        resonances.append({
            "name": names[i],
            "E_R_eV": E_R,
            "Gamma_eV": Gamma,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
            "v_target_kms": v_t,
        })
    return resonances


def main():
    print("=" * 70)
    print("Phase 33d — External probe with REAL SPARC data")
    print("=" * 70)
    print()

    # Load SPARC
    galaxies = parse_sparc_table1()
    print(f"Loaded {len(galaxies)} SPARC galaxies (Q=1,2)")
    vflat_values = [g["Vflat_kms"] for g in galaxies]
    print(f"Vflat range: {min(vflat_values):.1f} - {max(vflat_values):.1f} km/s")
    print(f"Vflat median: {np.median(vflat_values):.1f} km/s")
    print()

    # Load model
    best = get_best_posterior()
    resonances = build_resonances(best)
    print(f"Model parameters (Phase 32b posterior median):")
    print(f"  m_chi = {best['m_chi_GeV']:.2f} GeV")
    print(f"  sigma_0_dwarf = {best['sigma_0_dwarf']:.3f} cm^2/g")
    print(f"  a_slope = {best['a_slope']:.3f}")
    print(f"  v_targets = {[f'{v:.1f}' for v in best['v_targets_kms']]}")
    print()

    # Test target: SIDM-consistent range
    sidm_range = (0.1, 10.0)

    # Compute predictions for each galaxy
    predictions = []
    n_consistent = 0
    n_too_low = 0
    n_too_high = 0

    print(f"{'Galaxy':15s} {'Vflat':>8} {'sigma/m':>10} {'in SIDM?':>10}")
    print("-" * 50)
    for i, gal in enumerate(galaxies):
        v_max = gal["Vflat_kms"]
        sigma_0_v = velocity_dependent_background(
            v_max, best["sigma_0_dwarf"], best["a_slope"]
        )
        result = sigma_m_multi_resonant(
            v_max, best["m_chi_GeV"], resonances, sigma_0_v, 0.0
        )
        sm = result["sigma_m_total"]

        if sidm_range[0] <= sm <= sidm_range[1]:
            n_consistent += 1
            in_range = "YES"
        elif sm < sidm_range[0]:
            n_too_low += 1
            in_range = "TOO_LOW"
        else:
            n_too_high += 1
            in_range = "TOO_HIGH"

        predictions.append({
            "name": gal["name"],
            "Vflat_kms": v_max,
            "Q": gal["Q"],
            "sigma_m": float(sm),
            "in_sidm_range": in_range == "YES",
        })

        # Print first 15, last 5, plus a sample from middle
        if i < 15 or i >= len(galaxies) - 5 or i % 20 == 0:
            print(f"{gal['name']:15s} {v_max:8.1f} {sm:10.4f} {in_range:>10}")

    print()
    print("=" * 70)
    print("External probe results (REAL SPARC data)")
    print("=" * 70)
    print()
    total = len(galaxies)
    pct = 100.0 * n_consistent / total
    print(f"Total galaxies tested: {total}")
    print(f"  In SIDM range [0.1, 10] cm^2/g: {n_consistent} ({pct:.1f}%)")
    print(f"  Too low  (< 0.1): {n_too_low} ({100*n_too_low/total:.1f}%)")
    print(f"  Too high (> 10):  {n_too_high} ({100*n_too_high/total:.1f}%)")
    print()

    sigma_m_values = [p["sigma_m"] for p in predictions]
    print(f"Predicted sigma/m statistics:")
    print(f"  min:    {min(sigma_m_values):.4f}")
    print(f"  p25:    {np.percentile(sigma_m_values, 25):.4f}")
    print(f"  median: {np.median(sigma_m_values):.4f}")
    print(f"  p75:    {np.percentile(sigma_m_values, 75):.4f}")
    print(f"  max:    {max(sigma_m_values):.4f}")
    print()

    # Velocity-band breakdown
    print("Velocity-band breakdown:")
    bands = [
        ("Dwarfs (Vflat 30-80)",   30,  80),
        ("Intermediate (80-150)",  80, 150),
        ("Spirals (150-250)",     150, 250),
        ("Giants (250-350)",      250, 350),
    ]
    band_results = {}
    for name, v_lo, v_hi in bands:
        in_band = [p for p in predictions if v_lo <= p["Vflat_kms"] < v_hi]
        if in_band:
            sm_band = [p["sigma_m"] for p in in_band]
            n_ok = sum(1 for p in in_band if p["in_sidm_range"])
            band_results[name] = {
                "n_galaxies": len(in_band),
                "n_in_sidm_range": n_ok,
                "sigma_m_min": float(min(sm_band)),
                "sigma_m_max": float(max(sm_band)),
            }
            print(f"  {name:25s}: {len(in_band):3d} galaxies, "
                  f"sigma/m range [{min(sm_band):.3f}, {max(sm_band):.3f}], "
                  f"in SIDM range: {n_ok}/{len(in_band)}")
    print()

    # Verdict
    if pct > 80:
        verdict = "EXTERNAL_PROBE_PASS"
    elif pct > 50:
        verdict = "EXTERNAL_PROBE_MIXED"
    else:
        verdict = "EXTERNAL_PROBE_FAIL"

    print(f"Verdict: {verdict} ({pct:.1f}% of real SPARC galaxies consistent)")

    # Save results
    out = {
        "test": "Phase33d_external_probe_real_sparc",
        "n_galaxies": total,
        "vflat_range_kms": [float(min(vflat_values)), float(max(vflat_values))],
        "vflat_median_kms": float(np.median(vflat_values)),
        "model_parameters": best,
        "n_consistent": n_consistent,
        "n_too_low": n_too_low,
        "n_too_high": n_too_high,
        "pct_consistent": pct,
        "verdict": verdict,
        "velocity_band_breakdown": band_results,
        "sigma_m_statistics": {
            "min": float(min(sigma_m_values)),
            "p25": float(np.percentile(sigma_m_values, 25)),
            "median": float(np.median(sigma_m_values)),
            "p75": float(np.percentile(sigma_m_values, 75)),
            "max": float(max(sigma_m_values)),
        },
        "data_source": "SPARC database (Lelli, McGaugh, Schombert 2016), downloaded from https://astroweb.cwru.edu/SPARC/",
    }

    out_path = RESULTS_DIR / "phase33d_external_probe_real.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())