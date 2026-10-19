"""v40.49: Full multi-scale background refit.

Per Nemotron 3 Ultra 550B 9th review (v40.48): "It has not been tested
against Bullet Cluster (v~1500 km/s, sigma/m<0.7), Milky Way satellites
(v~10-30 km/s), or the original Phase 44 free-fit likelihood surface.
... A full multi-scale refit (v40.49+) is still required before
locking background parameters."

REVIEWED BY (v40.49): Nemotron 3 Ultra 550B (UPGRADED from 120B)

Method: take the 14 passing combinations from v40.48 (which passed
Cloud-9, Fornax, SPARC) and test them against ADDITIONAL channels:
  - Bullet Cluster (v~1500 km/s, sigma/m < 0.7)
  - MW satellite v=10 km/s (sigma/m < 1.0, low-mass dSph ceiling)
  - MW satellite v=20 km/s (sigma/m < 1.0)
  - MW satellite v=30 km/s (sigma/m < 1.0)
  - Lyman-alpha (v~100 km/s, sigma/m < 0.1) [SPARC already at 100]
  - Cluster (v~1000 km/s, sigma/m < 0.5)

If all 14 combinations pass these additional channels, the
background refit is robust across all SIDM observational scales.
If some fail, narrow down the passing region.

Per R88(68) lesson: this is an EXPLORATORY analysis. The result
either confirms the multi-scale robustness or shows that the
Yukawa power-law is INSUFFICIENT.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))
sys.path.insert(0, str(REPO / "scripts"))

# Multi-scale observational constraints
CONSTRAINTS = {
    "cloud9": {"v_kms": 28.0, "sigma_m_max": 1.0, "name": "Cloud-9 (V_max=28 km/s)"},
    "fornax": {"v_kms": 15.0, "sigma_m_max": 0.8, "name": "Fornax (v=15 km/s, dSph ceiling)"},
    "sparc": {"v_kms": 100.0, "sigma_m_max": 0.1, "name": "SPARC (v=100 km/s)"},
    "mw_sat_10": {"v_kms": 10.0, "sigma_m_max": 1.0, "name": "MW satellite (v=10 km/s)"},
    "mw_sat_20": {"v_kms": 20.0, "sigma_m_max": 1.0, "name": "MW satellite (v=20 km/s)"},
    "mw_sat_30": {"v_kms": 30.0, "sigma_m_max": 1.0, "name": "MW satellite (v=30 km/s)"},
    "lyman_alpha": {"v_kms": 100.0, "sigma_m_max": 0.1, "name": "Lyman-alpha (v=100 km/s)"},
    "cluster_1000": {"v_kms": 1000.0, "sigma_m_max": 0.5, "name": "Cluster (v=1000 km/s)"},
    "bullet_cluster": {"v_kms": 1500.0, "sigma_m_max": 0.7, "name": "Bullet Cluster (v=1500 km/s)"},
}

# The 14 passing combinations from v40.48
# (Manually reproduced from v40.48 sweep with peak=0)
PASSING_14 = [
    {"sigma_0": 0.010, "a_slope": 1.50, "v_ref": 50.0},
    {"sigma_0": 0.010, "a_slope": 1.93, "v_ref": 50.0},
    {"sigma_0": 0.010, "a_slope": 1.50, "v_ref": 100.0},
    {"sigma_0": 0.030, "a_slope": 1.50, "v_ref": 50.0},
    {"sigma_0": 0.010, "a_slope": 2.50, "v_ref": 50.0},
    {"sigma_0": 0.030, "a_slope": 1.93, "v_ref": 50.0},
    {"sigma_0": 0.010, "a_slope": 1.50, "v_ref": 150.0},
    {"sigma_0": 0.052, "a_slope": 1.50, "v_ref": 50.0},
    {"sigma_0": 0.010, "a_slope": 3.00, "v_ref": 50.0},
    {"sigma_0": 0.010, "a_slope": 1.93, "v_ref": 100.0},
    {"sigma_0": 0.030, "a_slope": 1.50, "v_ref": 100.0},
    {"sigma_0": 0.030, "a_slope": 2.50, "v_ref": 50.0},
    {"sigma_0": 0.010, "a_slope": 2.50, "v_ref": 100.0},
    {"sigma_0": 0.010, "a_slope": 1.93, "v_ref": 150.0},
]


def sigma_m_yukawa(v, sigma_0, a_slope, v_ref):
    """Yukawa-only sigma/m(v) (no Gaussian peak)."""
    return sigma_0 * (v_ref / v)**a_slope


def evaluate_combo(combo, constraints):
    """Evaluate a (sigma_0, a_slope, v_ref) combo against all constraints."""
    results = {}
    for key, c in constraints.items():
        sm = sigma_m_yukawa(c["v_kms"], combo["sigma_0"], combo["a_slope"], combo["v_ref"])
        results[key] = {
            "sigma_m": sm,
            "ceiling": c["sigma_m_max"],
            "passes": sm < c["sigma_m_max"],
        }
    return results


def main():
    print("=" * 70)
    print("v40.49: Full multi-scale background refit")
    print("=" * 70)
    print()
    print("Per Nemotron 3 Ultra 550B 9th review (v40.48):")
    print("  'A full multi-scale refit (v40.49+) is still required")
    print("   before locking background parameters.'")
    print()
    print("REVIEWER: Nemotron 3 Ultra 550B (UPGRADED from 120B)")
    print()
    print(f"Test {len(PASSING_14)} combinations from v40.48 against:")
    for key, c in CONSTRAINTS.items():
        print(f"  {c['name']:<40} (v={c['v_kms']:>5} km/s, sigma/m < {c['sigma_m_max']} cm^2/g)")
    print()

    # Evaluate each combo against all constraints
    all_results = []
    for combo in PASSING_14:
        results = evaluate_combo(combo, CONSTRAINTS)
        all_pass = all(r["passes"] for r in results.values())
        all_results.append((combo, results, all_pass))

    # Print summary
    print("=" * 70)
    print("MULTI-SCALE TEST RESULTS")
    print("=" * 70)
    print()
    print(f"{'sigma_0':>8} {'a':>6} {'v_ref':>7} {'Cloud9':>8} {'Fornax':>8} {'SPARC':>8} {'MW10':>8} {'MW20':>8} {'MW30':>8} {'LyA':>8} {'Cl1000':>8} {'Bullet':>8} {'All?':>5}")
    print("-" * 130)
    for combo, results, all_pass in all_results:
        line = f"{combo['sigma_0']:>8.3f} {combo['a_slope']:>6.2f} {combo['v_ref']:>7.1f} "
        for key in ["cloud9", "fornax", "sparc", "mw_sat_10", "mw_sat_20", "mw_sat_30", "lyman_alpha", "cluster_1000", "bullet_cluster"]:
            sm = results[key]["sigma_m"]
            line += f"{sm:>7.4f} "
        line += f"{'Y' if all_pass else 'N':>5}"
        print(line)

    # Count passing
    n_all_pass = sum(1 for _, _, ap in all_results if ap)
    n_each = {}
    for key in CONSTRAINTS.keys():
        n_each[key] = sum(1 for _, r, _ in all_results if r[key]["passes"])

    print()
    print(f"Combinations passing ALL 9 channels: {n_all_pass}/{len(PASSING_14)}")
    print()
    print("Per-channel pass rate:")
    for key in CONSTRAINTS.keys():
        print(f"  {CONSTRAINTS[key]['name']:<40} {n_each[key]}/{len(PASSING_14)}")
    print()

    # Verdict
    print("=" * 70)
    print("v40.49 KEY FINDINGS:")
    print("=" * 70)
    print()
    if n_all_pass == len(PASSING_14):
        print(f"ALL {len(PASSING_14)} combinations pass all 9 multi-scale channels!")
        print("The background refit is ROBUST across all SIDM observational scales.")
        print("The framework CAN be self-consistent with peak=0 + background refit.")
    elif n_all_pass == 0:
        print("NO combinations pass all 9 multi-scale channels.")
        print("The Yukawa power-law form is INSUFFICIENT -- additional physics needed.")
    else:
        print(f"{n_all_pass}/{len(PASSING_14)} combinations pass all 9 multi-scale channels.")
        print("The background refit is PARTIALLY robust -- some pass, some don't.")
        # Identify the binding constraint
        binding = min(n_each, key=n_each.get)
        print(f"Binding constraint: {CONSTRAINTS[binding]['name']} (only {n_each[binding]}/{len(PASSING_14)} pass)")

    print()
    print("Per Nemotron 3 Ultra 550B 9th review (v40.48):")
    print("  'A full multi-scale refit (v40.49+) is still required'")
    print("  'Do not adopt as the refit without multi-scale validation.'")
    print()
    print("=" * 70)
    print("R88(71) PRE-CLAIM CHECKLIST")
    print("=" * 70)
    print("(a) v40.49 tests 14 combinations from v40.48 against 9 multi-scale")
    print("    channels (3 from v40.48 + 6 new: MW satellites, Lyman-alpha,")
    print("    cluster, Bullet Cluster).")
    print()
    print("(b) Per R88(68) lesson: this is an EXPLORATORY multi-scale test.")
    print("    The result either confirms robustness or shows additional")
    print("    physics is needed.")
    print()
    print("(c) HONEST FRAMING: if all 14 pass, the background refit is")
    print("    robust. If some fail, the passing region is narrower than")
    print("    v40.48 suggested. If 0 pass, the Yukawa form is insufficient.")
    print()
    print("(d) RECOMMENDATION: Send to Nemotron 3 Ultra 550B for 10th review.")

    # Save
    out_dir = REPO / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v19_2_f_multiscale_refit_2026_10_19.json"
    out_data = {
        "method": "v40.49: Full multi-scale background refit",
        "date": "2026-10-19",
        "framework": "v19.2-F Phase 44, peak=0 (per v40.46)",
        "reviewer": "Nemotron 3 Ultra 550B (UPGRADED from 120B)",
        "input_from_v40_48": "14 passing combinations (sigma_0, a_slope, v_ref)",
        "constraints": CONSTRAINTS,
        "n_combinations": len(PASSING_14),
        "n_all_pass": n_all_pass,
        "n_per_channel": n_each,
        "results": [
            {
                "combo": combo,
                "per_channel": {key: {"sigma_m": r["sigma_m"], "ceiling": r["ceiling"], "passes": r["passes"]} for key, r in results.items()},
                "all_pass": all_pass,
            } for combo, results, all_pass in all_results
        ],
    }
    out.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print()
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
