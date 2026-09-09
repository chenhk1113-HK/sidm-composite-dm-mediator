"""
T90.23 PATH 2 (LIVE) — PandaX-4T 1.54 t-y DM candidate events: high-E_R count.

PURPOSE
=======
The PandaX-4T 1.54 t·y paper (PRL 134, 011805) releases 2490 DM candidate
events with (qS1, qS2, x, y, z, t) — Run 0 + Run 1 combined. Unlike LZ's
HEPData 155182, PandaX does NOT apply a strict S1c > 3 phd cut, so events
in the [5, 50] keVnr magnetic-m signal region are preserved.

This script:
  1. Loads Run0 + Run1 candidate CSVs
  2. Maps (qS1, qS2b) -> E_R via PandaX NEST parametrization (g1, g2b
     per-run, E-field per-run)
  3. Counts events in [5, 50], [50, 200], [200, 300] keVnr windows
  4. Compares to magnetic-m prediction (mu_x = 6.10e-8 mu_N, m_chi = 1 TeV)
  5. Verdict: magnetic-m CONSISTENT / UNDER-PREDICTS / OVER-PREDICTS

KEY RESULT (2026-09-10)
=======================
PandaX preserves events below LZ's 3 phd S1c cut:
  - Run 0: 1117 events, qS1 range [2.02, 134.32] PE, 20 events with qS1 < 3 PE
  - Run 1: 1373 events, qS1 range [2.09, 134.96] PE, 16 events with qS1 < 3 PE
  - Combined: 2490 events, 36 events with qS1 < 3 PE (these are below LZ's cut)

This is CRITICAL: the PandaX data CAN directly test the [5, 50] keVnr
magnetic-m signal region that LZ structurally blocks.

OUTPUT
======
  - outputs/t90/t90_v23_pandax_highE_count.json
      Per-window counts + ratio-to-prediction + verdict

MAGNETIC-M PREDICTION (at LZ-tuned coupling, scaled to PandaX exposure)
========================================================================
LZ predicts:
  - 1 event at [200, 300] keVnr in 2.84 t-y
  - 778 events at [5, 50] keVnr in 2.84 t-y

PandaX exposure = 1.54 t-y = 0.542x LZ exposure.
Scaling: N_pred_PandaX = N_pred_LZ * 0.542

So at the same coupling:
  - 0.54 events at [200, 300] keVnr in 1.54 t-y at PandaX
  - 422 events at [5, 50] keVnr in 1.54 t-y at PandaX
  - 815 events at [5, 270] keVnr in 1.54 t-y at PandaX
  - 390 events at [50, 200] keVnr in 1.54 t-y at PandaX

PandaX has NOT reported a 248 keV candidate. With 2490 events published,
the expected ~0.5 events at [200, 300] keVnr from magnetic-m is BELOW
the natural background fluctuation of ~few events in this window.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Where the user places the extracted opendata bundle.
PANDAX_EXPECT_DIR = _PROJECT_ROOT / "data" / "external_data" / "pandax_4t"
EXPECTED_FILE_PATTERNS = [
    "Run0_DM_candidates.csv",
    "Run1_DM_candidates.csv",
]
GLOB_PATTERN = "*_DM_candidates.csv"  # fallback glob

# PandaX detector parameters (from plot.py in the opendata bundle)
PANDAX_PARAMS = {
    "run0": {
        "g1": 0.0997,    # PE/keV
        "g2b": 4.12,     # PE/electron (bottom array only)
        "elec_field": 92.8,  # V/cm
    },
    "run1": {
        "g1": 0.0907,
        "g2b": 5.029,
        "elec_field": 84.4,
    },
}

# Analysis windows (keV nuclear-recoil energy)
WINDOW_248KEV = (200.0, 300.0)
WINDOW_LOW_E = (5.0, 50.0)
WINDOW_FULL = (5.0, 270.0)
WINDOW_SIDEBAND = (50.0, 200.0)

# Magnetic-moment prediction at LZ-tuned coupling, scaled to PandaX exposure.
# LZ predictions at 2.84 t-y from v12 dry-run:
#   N_pred(200-300 keVnr) = 1.0
#   N_pred(5-50 keVnr) = 778.0
#   N_pred(5-270 keVnr) = 1500.0
#   N_pred(50-200 keVnr) = 720.0
# PandaX exposure = 1.54 t-y = 0.542x LZ exposure.
MAG_MOMENT_PREDICTION_PANDAX = {
    "mu_x_mu_N": 6.10e-8,
    "m_chi_GeV": 1000.0,
    "exposure_tonne_years": 1.54,
    "exposure_ratio_to_LZ": 0.542,    # 1.54 / 2.84
    "N_pred_window_200_300_keVnr": 0.54,   # 1.0 * 0.542
    "N_pred_window_5_50_keVnr": 422.0,     # 778 * 0.542
    "N_pred_window_5_270_keVnr": 815.0,    # 1500 * 0.542
    "N_pred_window_50_200_keVnr": 390.0,    # 720 * 0.542
    "source": "t90_v12 dry-run, scaled by 1.54/2.84 = 0.542 from LZ 2.84 t-y",
}


# ---------------------------------------------------------------------------
# NEST mapping for PandaX
# ---------------------------------------------------------------------------

def nest_map_pandax_s1_to_er(qS1_pe: "np.ndarray", qS2B_pe: "np.ndarray",
                              run: str = "run0") -> "np.ndarray":
    """Reverse-map (qS1, qS2B) to nuclear-recoil energy E_R for PandaX.

    Uses PandaX NEST parametrization from the plot.py script:
      E_ee = 0.0137 * (1/g1 + S2b/S1/g2b) * S1

    Then Lindhard quenching to convert E_ee -> E_R for NR events.

    Note: This is a simplified mapping. PandaX's actual NEST uses a more
    complex E_ee(E_R, field) inversion. For an order-of-magnitude
    count this is sufficient.
    """
    g1 = PANDAX_PARAMS[run]["g1"]
    g2b = PANDAX_PARAMS[run]["g2b"]

    # First convert to electronic-equivalent energy
    # E_ee [keVee] = 0.0137 * (1/g1 + S2b/S1/g2b) * S1
    e_ee = 0.0137 * (1.0 / g1 + qS2B_pe / qS1_pe / g2b) * qS1_pe

    # Lindhard quenching for NR: E_R = E_ee / L_eff(E_R)
    # Iteratively solve E_R = E_ee / L_eff(E_R)
    # L_eff(E_R) ~ 0.05 * (E_R / 10) ** 0.18 for low-E NR (PandaX tuned)
    # For now, use simple approximation: E_R = E_ee / 0.10 (rough Lindhard at moderate E_R)
    # Better: solve iteratively

    def l_eff_nr(E_R):
        """NEST Lindhard-based NR light yield, PandaX-tuned."""
        return 0.05 * np.power(np.maximum(E_R, 0.5) / 10.0, 0.18)

    # Iterative solution: start with E_R = E_ee, refine
    e_r = e_ee.copy()
    for _ in range(20):
        e_r_new = e_ee / np.maximum(l_eff_nr(e_r), 0.01)
        if np.max(np.abs(e_r_new - e_r)) < 0.01:
            break
        e_r = e_r_new
    return e_r


def count_in_window(er_keV: "np.ndarray", window_keV: tuple) -> dict:
    """Count events in a recoil-energy window."""
    lo, hi = window_keV
    mask = (er_keV >= lo) & (er_keV <= hi)
    n = int(mask.sum())
    return {
        "window_keV": list(window_keV),
        "n_events": n,
        "fraction_of_total": float(n / max(len(er_keV), 1)),
    }


def compare_to_prediction(counts: dict, prediction: dict) -> dict:
    """Compare observed counts to magnetic-moment prediction."""
    result = {"windows": {}}
    for label, window in [
        ("low_E_5_50", WINDOW_LOW_E),
        ("248_keV_200_300", WINDOW_248KEV),
        ("sideband_50_200", WINDOW_SIDEBAND),
        ("full_5_270", WINDOW_FULL),
    ]:
        c = counts[label]
        # Try a few key format variants
        for key_format in [
            f"N_pred_window_{window[0]:.0f}_{window[1]:.0f}_keVnr",
            f"N_pred_window_{window[0]:.0f}_{window[1]:.0f}keVnr",
            f"N_pred_window_{window[0]:.0f}_{window[1]:.0f}_keV",
            f"N_pred_window_{window[0]:.0f}_{window[1]:.0f}",
        ]:
            if key_format in prediction:
                n_pred = prediction[key_format]
                break
        else:
            raise KeyError(
                f"No matching prediction key for window {window}; "
                f"available keys: {list(prediction.keys())}"
            )
        ratio = c["n_events"] / max(n_pred, 1e-9)
        if ratio < 0.3:
            verdict = "below_prediction (magnetic-m contradicted)"
        elif ratio < 3.0:
            verdict = "consistent_with_magnetic_m"
        else:
            verdict = "above_prediction (magnetic-m under-predicts)"
        result["windows"][label] = {
            **c,
            "n_predicted": n_pred,
            "ratio_obs_to_pred": ratio,
            "verdict": verdict,
        }
    return result


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_run_csv(csv_path: Path, run: str) -> dict:
    """Load a single PandaX run CSV."""
    rows = []
    with csv_path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    qS1 = np.array([float(r["qS1"]) for r in rows])
    qS2B = np.array([float(r["qS2B"]) for r in rows])
    qS2 = np.array([float(r["qS2"]) for r in rows])
    x = np.array([float(r["x"]) for r in rows])
    y = np.array([float(r["y"]) for r in rows])
    z = np.array([float(r["z"]) for r in rows])
    print(f"[load] {run}: {len(rows)} events from {csv_path.name}")
    print(f"[load]   qS1 range: [{qS1.min():.2f}, {qS1.max():.2f}] PE")
    print(f"[load]   qS2B range: [{qS2B.min():.1f}, {qS2B.max():.1f}] PE")
    print(f"[load]   log10(qS2B/qS1) range: "
          f"[{np.log10(qS2B/qS1).min():.3f}, {np.log10(qS2B/qS1).max():.3f}]")
    print(f"[load]   events with qS1 < 3 PE: {int(np.sum(qS1 < 3))}")
    er_keV = nest_map_pandax_s1_to_er(qS1, qS2B, run=run)
    print(f"[load]   NEST-mapped E_R range: [{er_keV.min():.2f}, {er_keV.max():.2f}] keVnr")
    return {
        "run": run,
        "n_events": len(rows),
        "qS1": qS1, "qS2B": qS2B, "qS2": qS2,
        "x": x, "y": y, "z": z,
        "er_keV": er_keV,
    }


def find_candidate_files(search_dir: Path) -> list:
    """Find PandaX Run0 and Run1 CSVs in search_dir."""
    found = []
    if not search_dir.exists():
        return found
    # Walk subdirectories too, since the bundle puts them in open_csv/
    for path in search_dir.rglob("*_DM_candidates.csv"):
        found.append(path)
    return sorted(found)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("T90.23 Path 2 (LIVE) -- PandaX-4T 1.54 t-y high-E_R count")
    print("=" * 70)

    candidates = find_candidate_files(PANDAX_EXPECT_DIR)
    if not candidates:
        # Try the immediate parent too
        candidates = find_candidate_files(PANDAX_EXPECT_DIR.parent)

    if not candidates:
        print(f"[dry-run] No PandaX Run*_DM_candidates.csv found at:")
        print(f"  {PANDAX_EXPECT_DIR}")
        print(f"  {PANDAX_EXPECT_DIR.parent}")
        print("")
        print("  To run live: download opendata.tar.gz from")
        print("  https://pandax.sjtu.edu.cn/public/data_release")
        print("  (the 'Dark Matter Search Results from 1.54 Tonne-Year Exposure'")
        print("  section), extract, and place the two CSVs in:")
        print(f"  {PANDAX_EXPECT_DIR}/Run0_DM_candidates.csv")
        print(f"  {PANDAX_EXPECT_DIR}/Run1_DM_candidates.csv")
        print("")
        print("[dry-run] EMITTING SHELL-ONLY OUTPUT (no data, no counts).")

        output = {
            "mode": "dry_run",
            "status": "awaiting_data",
            "expected_data_dir": str(PANDAX_EXPECT_DIR),
            "expected_filenames": EXPECTED_FILE_PATTERNS,
            "magnetic_moment_prediction_pandax": MAG_MOMENT_PREDICTION_PANDAX,
            "important_caveat_pandax_no_s1c_cut": (
                "Unlike LZ's HEPData 155182 (which cuts all S1c < 3 phd events "
                "before publication), PandaX's opendata.tar.gz publishes events "
                "with qS1 down to 2 PE. This means PandaX's data CAN directly "
                "test the [5, 50] keVnr magnetic-m signal region that LZ "
                "structurally blocks. Per the README, the opendata CSV has columns "
                "qS1, qS2B, qS2, x, y, z, t, set_label -- full per-event data."
            ),
            "schema_note": (
                "PandaX detector parameters (from README): "
                "Run 0 g1=0.0997 PE/keV, g2b=4.12 PE/electron, E=92.8 V/cm; "
                "Run 1 g1=0.0907, g2b=5.029, E=84.4 V/cm. "
                "iso-energy contours drawn at E_R = [5, 10, 20, 40, 80] keVnr."
            ),
            "verdict_rule": (
                "If N_obs in [5, 50] keVnr at PandaX is ~422 (predicted), "
                "magnetic-m is consistent. If ~0, magnetic-m is contradicted. "
                "If ~0 in [200, 300] keVnr, this is also consistent (predicts 0.54 "
                "events; PandaX has not reported a 248 keV candidate in this dataset)."
            ),
        }
    else:
        # LIVE mode: data is present, run the analysis
        print(f"[live] Found {len(candidates)} candidate CSV(s):")
        for c in candidates:
            print(f"  {c}")

        # Determine which run each CSV is
        runs = []
        for csv_path in candidates:
            name = csv_path.name
            if "Run0" in name:
                run = "run0"
            elif "Run1" in name:
                run = "run1"
            else:
                run = "run0"  # default
            runs.append((run, csv_path))

        # Load and process
        all_er = []
        all_qs1 = []
        per_run_results = []
        for run, csv_path in sorted(runs):
            result = load_run_csv(csv_path, run)
            per_run_results.append(result)
            all_er.append(result["er_keV"])
            all_qs1.append(result["qS1"])

        er_keV = np.concatenate(all_er)
        qS1_combined = np.concatenate(all_qs1)
        print()
        print(f"[live] Combined: {len(er_keV)} events, mapped E_R range "
              f"[{er_keV.min():.2f}, {er_keV.max():.2f}] keVnr")

        counts = {
            "low_E_5_50": count_in_window(er_keV, WINDOW_LOW_E),
            "248_keV_200_300": count_in_window(er_keV, WINDOW_248KEV),
            "sideband_50_200": count_in_window(er_keV, WINDOW_SIDEBAND),
            "full_5_270": count_in_window(er_keV, WINDOW_FULL),
        }
        for label, c in counts.items():
            print(f"  {label}: {c['n_events']} events in "
                  f"[{c['window_keV'][0]}, {c['window_keV'][1]}] keVnr")

        comparison = compare_to_prediction(counts, MAG_MOMENT_PREDICTION_PANDAX)

        # Determine verdict
        low_E_ratio = comparison["windows"]["low_E_5_50"]["ratio_obs_to_pred"]
        if low_E_ratio < 0.01:
            verdict = ("magnetic-m CONTRADICTED: [5, 50] keVnr is empty at PandaX")
        elif low_E_ratio < 0.3:
            verdict = "magnetic-m below prediction: weak constraint"
        elif low_E_ratio < 3.0:
            verdict = "magnetic-m CONSISTENT with low-E_R observation"
        else:
            verdict = "magnetic-m UNDER-PREDICTS: too many low-E_R events"

        output = {
            "mode": "live",
            "n_events_total": int(len(er_keV)),
            "data_source": [str(c) for _, c in sorted(runs)],
            "magnetic_moment_prediction_pandax": MAG_MOMENT_PREDICTION_PANDAX,
            "counts": comparison["windows"],
            "headline_verdict": verdict,
            "important_caveat": (
                "PandaX preserves events below the LZ 3 phd S1c cut (down to "
                "qS1 = 2 PE), so this test directly probes the [5, 50] keVnr "
                "magnetic-m signal region that LZ structurally blocks."
            ),
            "low_s1c_event_count": int(np.sum(qS1_combined < 3.0)),
            "low_s1c_fraction": float(np.sum(qS1_combined < 3.0) / max(len(qS1_combined), 1)),
        }

    out_path = _PROJECT_ROOT / "outputs" / "t90" / "t90_v23_pandax_highE_count.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[output] {out_path}")

    return output


if __name__ == "__main__":
    main()
